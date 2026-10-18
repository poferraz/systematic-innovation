from __future__ import annotations

import argparse
import json
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence

from tools.pilot_metrics import count_tokens


CONDITIONS = ("baseline_clean", "control_creative", "skill_treatment")
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


def build_initial_command(codex: str, model: str, output_path: Path, workdir: Path = Path("/tmp")) -> list[str]:
    return [
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
        "-",
    ]


def _execute(
    codex: str,
    model: str,
    prompt: str,
    output_path: Path,
    session_id: str | None,
) -> tuple[str, str, dict]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("", encoding="utf-8")
    if session_id is None:
        command = build_initial_command(codex, model, output_path)
    else:
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
            "-",
        ]
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
        raise RuntimeError(f"Codex runner failed ({result.returncode}):\n{combined[-4000:]}")
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
            raise RuntimeError(f"Codex runner did not expose a session id:\n{combined[-4000:]}")
        session_id = match.group(1)
    response = output_path.read_text(encoding="utf-8")
    if not response.strip():
        raise RuntimeError(f"Codex runner returned no final message:\n{combined[-4000:]}")
    return response, session_id, usage


def run_case(
    case: dict,
    condition: str,
    replicate: int,
    skill_dir: Path,
    model: str,
    codex: str,
    progress_path: Path | None = None,
) -> dict:
    prompts = build_user_prompts(case, condition, skill_dir)
    turns: list[dict] = []
    session_id: str | None = None
    prompt_digest = hashlib.sha256(json.dumps(prompts).encode()).hexdigest()
    if progress_path and progress_path.exists():
        saved = json.loads(progress_path.read_text())
        if saved["prompt_digest"] != prompt_digest or saved["model"] != model:
            raise ValueError("Resume inputs differ from saved conversation")
        turns, session_id = saved["turns"], saved["session_id"]
        if any(turn.get("assistant_tokens") is not None and "provider_usage_cumulative" not in turn for turn in turns):
            raise ValueError("Legacy progress accounting requires explicit migration; raw counters were preserved")
    with tempfile.TemporaryDirectory(prefix="systematic-innovation-stress-") as tmp:
        output = Path(tmp) / "last-message.md"
        for turn_index, prompt in enumerate(prompts, start=1):
            if turn_index <= len(turns):
                continue
            executed = _execute(codex, model, prompt, output, session_id)
            assistant, session_id = executed[:2]
            usage = executed[2] if len(executed) > 2 else {}
            previous_counter = turns[-1].get("provider_usage_cumulative", {}).get("output_tokens", 0) if turns else 0
            counter = usage.get("output_tokens")
            output_tokens = counter - previous_counter if counter is not None and previous_counter is not None and counter >= previous_counter else None
            turns.append(
                {
                    "turn_index": turn_index,
                    "user": prompt,
                    "assistant": assistant,
                    "assistant_tokens": output_tokens,
                    "provider_usage_cumulative": usage,
                    "assistant_tokens_estimate": count_tokens(assistant),
                }
            )
            if progress_path:
                progress_path.parent.mkdir(parents=True, exist_ok=True)
                temporary = progress_path.with_suffix(".tmp")
                temporary.write_text(json.dumps({"prompt_digest": prompt_digest, "model": model,
                    "session_id": session_id, "turns": turns}) + "\n")
                temporary.replace(progress_path)

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
        "token_accounting": "provider_cumulative_differenced" if all(turn["assistant_tokens"] is not None for turn in turns) else "unavailable",
        "skill_pack_sha256": hashlib.sha256(load_skill_pack(skill_dir).encode()).hexdigest() if condition == "skill_treatment" else None,
        "turns": turns,
        "final_response": turns[-1]["assistant"],
        "total_assistant_output_tokens": sum(turn["assistant_tokens"] for turn in turns) if all(turn["assistant_tokens"] is not None for turn in turns) else None,
        "total_assistant_output_tokens_estimate": sum(turn["assistant_tokens_estimate"] for turn in turns),
        "turn_1_question_count": sum(
            1 for line in turns[0]["assistant"].splitlines() if line.strip().endswith("?")
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
    parser.add_argument("--codex", default="/Users/poferraz/.local/bin/codex")
    parser.add_argument("--replicates", type=int, help="Override manifest repetitions")
    parser.add_argument("--jobs", type=int, default=1, choices=(1, 2, 3))
    parser.add_argument("--max-calls", type=int, default=600)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
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
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {}
        for case, condition, replicate in jobs:
            if (case["id"], condition, replicate) in completed:
                continue
            progress = args.output / "progress" / f"{condition}-{case['id']}-{replicate}.json"
            future = pool.submit(run_case, case, condition, replicate, args.skill,
                                 args.model, args.codex, progress)
            futures[future] = (case["id"], condition, replicate)
        for future in as_completed(futures):
            record = future.result()
            output_path = args.output / f"{record['condition']}.jsonl"
            with output_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            print(f"Saved {record['condition']} {record['case_id']} rep {record['replicate']}: "
                  f"{record['total_assistant_output_tokens']} provider output tokens", flush=True)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
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
