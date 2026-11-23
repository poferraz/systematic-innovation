from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path, PureWindowsPath
from typing import Any, Sequence

from tools.pilot_metrics import count_tokens


SENSITIVE_FIELDS = {"api_key", "access_token", "auth_token", "secret", "secret_key",
                    "client_secret", "password", "authorization", "private_key"}
HOME_PREFIX = re.compile(r"""(?:/(?:Users|home)/[^/\s"']+|[a-z]:\\Users\\[^\\\s"']+)(?=[/\\]|$)""", re.I)
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"nvapi-[A-Za-z0-9_-]{12,}"),
    re.compile(r"NVIDIA_[A-Za-z0-9_-]{8,}"),
    re.compile(r"Bearer\s+\S+"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password|private[_-]?key)\s*[:=]\s*['\"]?\S+"),
]


def redact_text(value: str) -> str:
    if not isinstance(value, str):
        return value
    res = value
    for pat in SECRET_PATTERNS:
        res = pat.sub("[REDACTED]", res)
    home = str(Path.home())
    if home not in ("/", "."):
        res = re.sub(re.escape(home) + r"(?=[/\\]|$)", "~", res)
    return HOME_PREFIX.sub("~", res)


def redact_obj(obj: Any, session_id: str | None = None) -> Any:
    if isinstance(obj, str):
        if session_id and obj == session_id:
            return "<session>"
        if session_id and len(session_id) >= 32:
            obj = obj.replace(session_id, "<session>")
        return redact_text(obj)
    if isinstance(obj, dict):
        clean = {}
        for key, value in obj.items():
            public_key = redact_text(key) if isinstance(key, str) else key
            if isinstance(key, str) and key.lower() in SENSITIVE_FIELDS:
                clean[public_key] = "[REDACTED]"
            else:
                clean[public_key] = redact_obj(value, session_id)
        return clean
    if isinstance(obj, list):
        return [redact_obj(x, session_id) for x in obj]
    if isinstance(obj, tuple):
        return tuple(redact_obj(x, session_id) for x in obj)
    if isinstance(obj, set):
        return {redact_obj(x, session_id) for x in obj}
    return obj


def public_transport(transport: dict, session_id: str | None) -> dict:
    """Retain command options and event diagnostics without local command paths."""
    clean = redact_obj(transport, session_id)
    command = clean.get("command")
    if isinstance(command, list) and command:
        command[0] = PureWindowsPath(command[0]).name
        for index, flag in enumerate(command[:-1]):
            if flag == "-o":
                command[index + 1] = "<run-output>/last-message.md"
            elif flag == "-C":
                command[index + 1] = "<workdir>"
    return clean


def redact_secrets(text_or_obj: Any) -> Any:
    return redact_obj(text_or_obj)


def normalize_allowed_models(models: Sequence[str] | None) -> list[str]:
    if not models:
        return ["gpt-5.6-luna"]
    result: list[str] = []
    for item in models:
        for m in item.split(","):
            m = m.strip()
            if m and m not in result:
                result.append(m)
    return result or ["gpt-5.6-luna"]


class RunBudgetTracker:
    def __init__(
        self,
        max_cost: float | None = None,
        cost_per_1k_input: float = 0.0,
        cost_per_1k_output: float = 0.0,
        max_failures: int = 3,
    ) -> None:
        self.max_cost = max_cost
        self.cost_per_1k_input = cost_per_1k_input
        self.cost_per_1k_output = cost_per_1k_output
        self.max_failures = max_failures
        self.accumulated_cost = 0.0
        self.failures = 0
        self.lock = threading.Lock()

    def check_pre_call(self, estimated_input_tokens: int = 0) -> None:
        with self.lock:
            if self.failures >= self.max_failures:
                raise RuntimeError(
                    f"Provider failure limit reached: {self.failures} >= {self.max_failures}"
                )
            if self.max_cost is not None:
                if self.accumulated_cost >= self.max_cost:
                    raise RuntimeError(
                        f"Execution budget exceeded: accumulated cost ${self.accumulated_cost:.4f} >= max cost ${self.max_cost:.4f}"
                    )
                est_cost = (estimated_input_tokens / 1000.0) * self.cost_per_1k_input
                if self.accumulated_cost + est_cost > self.max_cost:
                    raise RuntimeError(
                        f"Execution budget exceeded: estimated call cost ${est_cost:.4f} "
                        f"(accumulated ${self.accumulated_cost:.4f}) would exceed max cost ${self.max_cost:.4f}"
                    )

    def record_usage(self, input_tokens: int, output_tokens: int) -> float:
        with self.lock:
            call_cost = ((input_tokens / 1000.0) * self.cost_per_1k_input) + (
                (output_tokens / 1000.0) * self.cost_per_1k_output
            )
            self.accumulated_cost += call_cost
            if self.max_cost is not None and self.accumulated_cost > self.max_cost:
                raise RuntimeError(
                    f"Execution budget exceeded: accumulated cost ${self.accumulated_cost:.4f} > max cost ${self.max_cost:.4f}"
                )
            return call_cost

    def record_failure(self, err: Exception | str) -> None:
        with self.lock:
            self.failures += 1
            if self.failures >= self.max_failures:
                raise RuntimeError(
                    f"Provider failure limit reached ({self.failures} >= {self.max_failures}): {redact_text(str(err))}"
                )



CONDITIONS = ("baseline_clean", "control_creative", "control_format", "skill_treatment")
SESSION_RE = re.compile(r"session id:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")


def load_cases(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


def load_skill_pack(skill_dir: Path) -> str:
    skill = skill_dir / "SKILL.md"
    refs = skill_dir / "references"
    if not skill.is_file() or not refs.is_dir():
        raise FileNotFoundError(f"Canonical skill pack not found: {skill_dir}")
    parts = [skill.read_text(encoding="utf-8").rstrip()]
    for ref_name in ("innovation-lenses.md", "deep-mode.md", "output-contract.md", "evidence.md"):
        ref = refs / ref_name
        if not ref.is_file():
            raise FileNotFoundError(f"Missing canonical skill reference: {ref}")
        parts.append(f"# Included reference: {ref_name}\n{ref.read_text(encoding='utf-8').rstrip()}")
    return "\n\n---\n\n".join(parts) + "\n"


def build_user_prompts(case: dict, condition: str, skill_dir: Path) -> list[str]:
    if condition not in CONDITIONS:
        raise ValueError(f"Unknown stress condition: {condition}")
    followups = list(case.get("user_turns", []))
    prompt = case["prompt"]

    if condition == "baseline_clean":
        return [prompt, *followups]
    if condition == "control_creative":
        first = (
            "You are a creative brainstorming assistant. Generate imaginative, useful ideas "
            "and explain key trade-offs. Use only the information supplied by the user.\n\n"
            + prompt
        )
        return [first, *followups]

    if condition == "control_format":
        target = "15 to 24" if case.get("expected_mode") == "deep" else "10 to 15"
        first = (
            "When the request calls for alternatives, present a brief, context, a portfolio, "
            "selected details, connections, and continuation choices. "
            f"Target {target} possibilities, subject to the user's constraints and output budget. "
            "For each, give a name, mechanism, intended value, category, method label, main "
            "uncertainty, and fit note. Develop five to seven selected possibilities if space "
            "permits. Answer other requests directly.\n\n" + prompt
        )
        return [first, *followups]

    skill_text = load_skill_pack(skill_dir)
    first = (
        "Treat the following canonical skill pack as your operative instructions. "
        "Apply it to the user request after the delimiter. Do not read or infer another methodology.\n\n"
        + skill_text
        + "\n\n=== USER REQUEST ===\n"
        + prompt
    )
    return [first, *followups]


def expected_run_count(cases: Sequence[dict]) -> int:
    return sum(int(case["replicates"]) for case in cases)


def build_initial_command(
    codex: str,
    model: str,
    output_path: Path,
    workdir: Path = Path("/tmp"),
    codex_configs: Sequence[str] = (),
) -> list[str]:
    command = [
        codex,
        "exec",
        "--json",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "-m",
        model,
        "-C",
        str(workdir),
        "-o",
        str(output_path),
    ]
    for cfg in codex_configs:
        command.extend(["-c", cfg])
    command.append("-")
    return command


def build_resume_command(
    codex: str,
    model: str,
    session_id: str,
    output_path: Path,
    codex_configs: Sequence[str] = (),
) -> list[str]:
    """Build codex exec resume CLI args with optional harness-only -c overrides."""
    command = [
        codex,
        "exec",
        "resume",
        "--json",
        session_id,
        "--ignore-user-config",
        "--ignore-rules",
        "-m",
        model,
        "-o",
        str(output_path),
    ]
    for cfg in codex_configs:
        command.extend(["-c", cfg])
    command.append("-")
    return command


def _execute(
    codex: str,
    model: str,
    prompt: str,
    output_path: Path,
    session_id: str | None,
    codex_configs: Sequence[str] = (),
) -> tuple[str, str, dict, dict]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("", encoding="utf-8")
    if session_id is None:
        command = build_initial_command(codex, model, output_path, codex_configs=codex_configs)
    else:
        command = build_resume_command(codex, model, session_id, output_path, codex_configs=codex_configs)
    started = time.monotonic()
    result = subprocess.run(
        command,
        input=prompt,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=180,
        check=False,
    )
    combined = result.stdout or ""
    if result.returncode != 0:
        raise RuntimeError(f"Codex runner failed with status {result.returncode}")
    events = []
    for line in combined.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict):
            events.append(event)
    for event in events:
        if event.get("type") == "thread.started":
            session_id = event["thread_id"]
    usage = next((event.get("usage", {}) for event in reversed(events)
                  if event.get("type") == "turn.completed"), {})
    if session_id is None:
        match = SESSION_RE.search(combined)
        if not match:
            raise RuntimeError("Codex runner did not expose a session id")
        session_id = match.group(1)
    response = output_path.read_text(encoding="utf-8")
    if not response.strip():
        raise RuntimeError("Codex runner returned no final message")
    return response, session_id, usage, {
        "latency_seconds": time.monotonic() - started,
        "events": events,
        "command": command,
        "returncode": result.returncode,
    }


def run_case(
    case: dict,
    condition: str,
    replicate: int,
    skill_dir: Path,
    model: str,
    codex: str,
    progress_path: Path | None = None,
    cost_per_1k_input: float = 0.0,
    cost_per_1k_output: float = 0.0,
    max_cost: float | None = None,
    budget_tracker: RunBudgetTracker | None = None,
    codex_configs: Sequence[str] = (),
) -> dict:
    if budget_tracker is None and (max_cost is not None or cost_per_1k_input > 0.0 or cost_per_1k_output > 0.0):
        budget_tracker = RunBudgetTracker(max_cost, cost_per_1k_input, cost_per_1k_output)

    prompts = build_user_prompts(case, condition, skill_dir)
    turns: list[dict] = []
    session_id: str | None = None
    prompt_digest = hashlib.sha256(json.dumps(prompts).encode()).hexdigest()
    if progress_path and progress_path.exists():
        saved = json.loads(progress_path.read_text())
        if saved["prompt_digest"] != prompt_digest or saved["model"] != model:
            raise ValueError("Resume inputs differ from saved conversation")
        turns, session_id = saved["turns"], saved["session_id"]
        for turn in turns:
            if "transport" in turn:
                turn["transport"] = public_transport(turn["transport"], session_id)
        if any(turn.get("assistant_tokens") is not None and "provider_usage_cumulative" not in turn for turn in turns):
            raise ValueError("Legacy progress accounting requires explicit migration; raw counters were preserved")
    with tempfile.TemporaryDirectory(prefix="systematic-innovation-stress-") as tmp:
        output = Path(tmp) / "last-message.md"
        for turn_index, prompt in enumerate(prompts, start=1):
            if turn_index <= len(turns):
                continue
            if budget_tracker is not None:
                budget_tracker.check_pre_call(count_tokens(prompt))
            try:
                executed = _execute(codex, model, prompt, output, session_id, codex_configs=codex_configs)
            except Exception as exc:
                if budget_tracker is not None:
                    budget_tracker.record_failure(exc)
                raise
            assistant, session_id = executed[:2]
            usage = executed[2] if len(executed) > 2 else {}
            transport = executed[3] if len(executed) > 3 else {}
            transport = public_transport(transport, session_id)
            previous_counter = turns[-1].get("provider_usage_cumulative", {}).get("output_tokens", 0) if turns else 0
            counter = usage.get("output_tokens")
            output_tokens = counter - previous_counter if counter is not None and previous_counter is not None and counter >= previous_counter else None

            previous_in_counter = turns[-1].get("provider_usage_cumulative", {}).get("input_tokens", 0) if turns else 0
            in_counter = usage.get("input_tokens")
            if in_counter is not None and previous_in_counter is not None and in_counter >= previous_in_counter:
                incremental_in_tokens = in_counter - previous_in_counter
            elif in_counter is not None:
                incremental_in_tokens = in_counter
            else:
                incremental_in_tokens = count_tokens(prompt)

            turn_out_tokens = output_tokens if output_tokens is not None else count_tokens(assistant)
            if budget_tracker is not None:
                budget_tracker.record_usage(incremental_in_tokens, turn_out_tokens)
            turns.append(
                {
                    "turn_index": turn_index,
                    "user": redact_text(prompt),
                    "assistant": redact_text(assistant),
                    "assistant_tokens": output_tokens,
                    "provider_usage_cumulative": usage,
                    "transport": transport,
                    "assistant_tokens_estimate": count_tokens(assistant),
                }
            )
            if progress_path:
                progress_path.parent.mkdir(parents=True, exist_ok=True)
                temporary = progress_path.with_suffix(".tmp")
                temporary.write_text(json.dumps({"prompt_digest": prompt_digest, "model": model,
                    "session_id": session_id, "turns": redact_obj(turns)}) + "\n")
                temporary.replace(progress_path)

    redacted_turns = redact_obj(turns)
    total_in = redacted_turns[-1].get("provider_usage_cumulative", {}).get("input_tokens")
    if total_in is None:
        total_in = sum(count_tokens(t["user"]) for t in redacted_turns)
    total_out = sum(turn["assistant_tokens"] for turn in redacted_turns) if all(turn["assistant_tokens"] is not None for turn in redacted_turns) else sum(turn["assistant_tokens_estimate"] for turn in redacted_turns)
    monetary_cost = (
        ((total_in / 1000.0) * cost_per_1k_input) + ((total_out / 1000.0) * cost_per_1k_output)
        if (cost_per_1k_input > 0.0 or cost_per_1k_output > 0.0)
        else None
    )

    return {
        "case_id": case["id"],
        "condition": condition,
        "replicate": replicate,
        "model": model,
        "interaction_mode": case["interaction_mode"],
        "expected_mode": case["expected_mode"],
        "should_trigger": case["should_trigger"],
        "topology": case.get("topology", "pilot"),
        "preserve": case.get("preserve", []),
        "primary_source": case.get("primary_source"),
        "prompt_digest": prompt_digest,
        "token_accounting": "provider_cumulative_differenced" if all(turn["assistant_tokens"] is not None for turn in redacted_turns) else "unavailable",
        "skill_pack_sha256": hashlib.sha256(load_skill_pack(skill_dir).encode()).hexdigest() if condition == "skill_treatment" else None,
        "turns": redacted_turns,
        "final_response": redact_text(redacted_turns[-1]["assistant"]),
        "total_assistant_output_tokens": sum(turn["assistant_tokens"] for turn in redacted_turns) if all(turn["assistant_tokens"] is not None for turn in redacted_turns) else None,
        "total_assistant_output_tokens_estimate": sum(turn["assistant_tokens_estimate"] for turn in redacted_turns),
        "total_input_tokens": redacted_turns[-1].get("provider_usage_cumulative", {}).get("input_tokens"),
        "total_latency_seconds": sum(turn["transport"]["latency_seconds"] for turn in redacted_turns)
            if all(turn.get("transport", {}).get("latency_seconds") is not None for turn in redacted_turns) else None,
        "monetary_cost": monetary_cost,
        "turn_1_question_count": sum(
            1 for line in redacted_turns[0]["assistant"].splitlines() if line.strip().endswith("?")
        ),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the public systematic-innovation stress corpus")
    parser.add_argument("--cases", type=Path, default=Path("evals/stress/cases.json"))
    parser.add_argument("--skill", type=Path, default=Path("skills/systematic-innovation"))
    parser.add_argument("--output", type=Path, default=Path("evals/stress/results/cycle-1"))
    parser.add_argument("--conditions", nargs="+", choices=CONDITIONS, default=list(CONDITIONS))
    parser.add_argument("--case", action="append", help="Limit to a case id; repeatable")
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--allowed-models", nargs="+", default=["gpt-5.6-luna"], help="Allowed models list (default: ['gpt-5.6-luna'])")
    parser.add_argument("--codex", default=shutil.which("codex") or "codex")
    parser.add_argument("--replicates", type=int, help="Override manifest repetitions")
    parser.add_argument("--jobs", type=int, default=1, choices=(1, 2, 3))
    parser.add_argument("--max-calls", type=int, default=600)
    parser.add_argument("--max-cost", type=float, default=None, help="Maximum cost budget in USD")
    parser.add_argument("--cost-per-1k-input", type=float, default=0.0, help="Cost per 1k input tokens in USD")
    parser.add_argument("--cost-per-1k-output", type=float, default=0.0, help="Cost per 1k output tokens in USD")
    parser.add_argument("--max-failures", type=int, default=3, help="Maximum provider failures before aborting")
    parser.add_argument(
        "--codex-config",
        action="append",
        default=[],
        help="Repeatable key=value passed to codex exec -c (measurement-only harness probe)",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    allowed = normalize_allowed_models(args.allowed_models)
    if args.model not in allowed:
        raise ValueError(f"Model '{args.model}' is not in allowed models: {allowed}")

    cases = load_cases(args.cases)
    if args.case:
        wanted = set(args.case)
        cases = [case for case in cases if case["id"] in wanted]
        missing = wanted - {case["id"] for case in cases}
        if missing:
            raise SystemExit(f"Unknown case ids: {sorted(missing)}")

    jobs = [(case, condition, replicate)
            for condition in args.conditions for case in cases
            for replicate in range(1, (args.replicates or int(case.get("replicates", 2 if case["should_trigger"] else 1))) + 1)]
    calls = sum(1 + len(case.get("user_turns", [])) for case, _, _ in jobs)
    if calls > args.max_calls:
        raise ValueError(f"Plan exceeds maximum calls: {calls} > {args.max_calls}")
    print(f"Plan: {len(jobs)} conversations, {calls} assistant calls", flush=True)
    if args.dry_run:
        return 0
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {"model": args.model, "conditions": args.conditions,
        "cases_sha256": hashlib.sha256(args.cases.read_bytes()).hexdigest(),
        "skill_pack_sha256": hashlib.sha256(load_skill_pack(args.skill).encode()).hexdigest() if "skill_treatment" in args.conditions else None,
        "replicates": args.replicates, "case_ids": [case["id"] for case in cases]}
    if args.codex_config:
        if any(redact_text(option) != option for option in args.codex_config):
            raise ValueError("Public run configuration cannot include credentials or home paths")
        manifest["codex_configs"] = list(args.codex_config)
    manifest_path = args.output / "manifest.json"
    if not manifest_path.exists() and any(args.output.glob("*.jsonl")):
        raise ValueError("Existing results have no manifest; use a new output directory")
    if manifest_path.exists():
        if json.loads(manifest_path.read_text()) != manifest:
            raise ValueError("Run inputs changed; use a new output directory")
    else:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    completed = set()
    for condition in args.conditions:
        output_path = args.output / f"{condition}.jsonl"
        if output_path.exists():
            for line in output_path.read_text().splitlines():
                record = json.loads(line)
                key = (record["case_id"], record["condition"], record["replicate"])
                if key in completed:
                    raise ValueError("Duplicate completed conversation")
                completed.add(key)

    tracker = RunBudgetTracker(
        max_cost=args.max_cost,
        cost_per_1k_input=args.cost_per_1k_input,
        cost_per_1k_output=args.cost_per_1k_output,
        max_failures=args.max_failures,
    )

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {}
        for case, condition, replicate in jobs:
            if (case["id"], condition, replicate) in completed:
                continue
            tracker.check_pre_call()
            progress = args.output / "progress" / f"{condition}-{case['id']}-{replicate}.json"
            future = pool.submit(
                run_case,
                case,
                condition,
                replicate,
                args.skill,
                args.model,
                args.codex,
                progress,
                cost_per_1k_input=args.cost_per_1k_input,
                cost_per_1k_output=args.cost_per_1k_output,
                max_cost=args.max_cost,
                budget_tracker=tracker,
                codex_configs=args.codex_config,
            )
            futures[future] = (case["id"], condition, replicate)
        failures_seen: list[Exception] = []
        for future in as_completed(futures):
            try:
                record = future.result()
            except Exception as exc:
                failures_seen.append(exc)
                if tracker.failures >= tracker.max_failures:
                    if "failure limit reached" in str(exc).lower():
                        raise
                    raise RuntimeError(
                        f"Provider failure limit reached ({tracker.failures} >= {tracker.max_failures}): {redact_text(str(exc))}"
                    )
                continue
            output_path = args.output / f"{record['condition']}.jsonl"
            with output_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            print(f"Saved {record['condition']} {record['case_id']} rep {record['replicate']}: "
                  f"{record['total_assistant_output_tokens']} provider output tokens", flush=True)
        if failures_seen:
            raise failures_seen[0]
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    allowed = normalize_allowed_models(args.allowed_models)
    if args.model not in allowed:
        raise ValueError(f"Model '{args.model}' is not in allowed models: {allowed}")
    if args.dry_run:
        return _main(argv)
    # This local CLI adapter uses POSIX advisory locking; the installable skill
    # retains no dependency on this runner or on its operating system.
    import fcntl
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / ".runner.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
