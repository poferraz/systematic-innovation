from __future__ import annotations

import argparse
import json
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
) -> tuple[str, str]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("", encoding="utf-8")
    if session_id is None:
        command = build_initial_command(codex, model, output_path)
    else:
        command = [
            codex,
            "exec",
            "resume",
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
    if session_id is None:
        match = SESSION_RE.search(combined)
        if not match:
            raise RuntimeError(f"Codex runner did not expose a session id:\n{combined[-4000:]}")
        session_id = match.group(1)
    response = output_path.read_text(encoding="utf-8")
    if not response.strip():
        raise RuntimeError(f"Codex runner returned no final message:\n{combined[-4000:]}")
    return response, session_id


def run_case(
    case: dict,
    condition: str,
    replicate: int,
    skill_dir: Path,
    model: str,
    codex: str,
) -> dict:
    prompts = build_user_prompts(case, condition, skill_dir)
    turns: list[dict] = []
    session_id: str | None = None
    with tempfile.TemporaryDirectory(prefix="systematic-innovation-stress-") as tmp:
        output = Path(tmp) / "last-message.md"
        for turn_index, prompt in enumerate(prompts, start=1):
            assistant, session_id = _execute(codex, model, prompt, output, session_id)
            turns.append(
                {
                    "turn_index": turn_index,
                    "user": prompt,
                    "assistant": assistant,
                    "assistant_tokens": count_tokens(assistant),
                }
            )

    return {
        "case_id": case["id"],
        "condition": condition,
        "replicate": replicate,
        "model": model,
        "interaction_mode": case["interaction_mode"],
        "expected_mode": case["expected_mode"],
        "should_trigger": case["should_trigger"],
        "topology": case["topology"],
        "preserve": case["preserve"],
        "primary_source": case["primary_source"],
        "turns": turns,
        "final_response": turns[-1]["assistant"],
        "total_assistant_output_tokens": sum(turn["assistant_tokens"] for turn in turns),
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
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    cases = load_cases(args.cases)
    if args.case:
        wanted = set(args.case)
        cases = [case for case in cases if case["id"] in wanted]
        missing = wanted - {case["id"] for case in cases}
        if missing:
            raise SystemExit(f"Unknown case ids: {sorted(missing)}")

    args.output.mkdir(parents=True, exist_ok=True)
    for condition in args.conditions:
        records: list[dict] = []
        output_path = args.output / f"{condition}.jsonl"
        for case in cases:
            for replicate in range(1, int(case["replicates"]) + 1):
                record = run_case(case, condition, replicate, args.skill, args.model, args.codex)
                records.append(record)
                print(
                    f"{condition} {case['id']} replicate {replicate}: "
                    f"{record['total_assistant_output_tokens']} tokens",
                    flush=True,
                )
        output_path.write_text(
            "\n".join(json.dumps(record) for record in records) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {len(records)} records to {output_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
