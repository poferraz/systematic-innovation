"""Deterministic factorial planning and conservative budget reservation."""

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from .models import BenchmarkCase, Condition, Job, RunConfig, RunEstimate

PREAMBLES = {
    Condition.VANILLA: "",
    Condition.GENERIC_BRAINSTORM: "Brainstorm varied useful possibilities for the user's challenge.",
    Condition.FORMAT_MATCHED: (
        "Give 10 to 15 possibilities for a bounded challenge, or 15 to 24 for a complex challenge. "
        "Use a brief, context summary, complete portfolio table, selected details, connections, "
        "and a continuation question. For each possibility include name, intervention, causal chain, "
        "expected effect, requirement, and limitation. Respect the user's output budget."
    ),
    Condition.ESTABLISHED_METHOD: (
        "Use SCAMPER: Substitute, Combine, Adapt, Modify, Put to another use, Eliminate, Reverse. "
        "Explore possibilities for the user's challenge without choosing a winner."
    ),
}
ABLATIONS = frozenset(
    {"ledger", "reasoning-cells", "system-map", "preservation", "saturation", "cross-pollination"}
)


def select_cases(
    cases: Sequence[BenchmarkCase], case_ids: Sequence[str] | None
) -> list[BenchmarkCase]:
    by_id = {case.id: case for case in cases}
    if len(by_id) != len(cases):
        raise ValueError("duplicate case id")
    if case_ids is None:
        return sorted(cases, key=lambda case: case.id)
    if not case_ids or any(not item.strip() for item in case_ids):
        raise ValueError("empty case id selection")
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("duplicate selected case id")
    if any(item not in by_id for item in case_ids):
        raise ValueError("unknown selected case id")
    return sorted((by_id[item] for item in case_ids), key=lambda case: case.id)


def load_skill_pack(path: Path) -> str:
    root = path.resolve()
    if not (root / "SKILL.md").is_file() or root.is_symlink():
        raise ValueError("canonical skill pack not found")
    paths = [root / "SKILL.md", *sorted((root / "references").glob("*.md"))]
    if any(path.is_symlink() or not path.resolve().is_relative_to(root) for path in paths):
        raise ValueError("skill pack contains an unsafe source path")
    return "\n\n".join(path.read_text(encoding="utf-8") for path in paths)


def render_condition(condition: Condition, config: RunConfig) -> str:
    if condition in PREAMBLES:
        return PREAMBLES[condition]
    skill_path = (
        config.skill_path or Path(__file__).resolve().parents[3] / "skills/systematic-innovation"
    )
    pack = load_skill_pack(skill_path)
    if condition is Condition.FULL_SKILL:
        return pack
    if not config.ablation or config.ablation not in ABLATIONS:
        raise ValueError("ablation requires a recognized named development variant")
    if not config.ablation_skill_path:
        raise ValueError("ablation requires an independently versioned candidate pack")
    candidate = load_skill_pack(config.ablation_skill_path)
    if candidate == pack:
        raise ValueError("ablation candidate must differ from full treatment")
    return candidate


def estimate_run(jobs: Sequence[Job], config: RunConfig) -> RunEstimate:
    maximum_calls = 0
    maximum_cost = 0.0
    known_cost = True
    for job in jobs:
        calls = job.conversation_script.maximum_assistant_turns if job.conversation_script else 1
        calls *= config.retry_limit + 1
        maximum_calls += calls
        if job.model in config.cost_per_turn:
            maximum_cost += calls * config.cost_per_turn[job.model]
        else:
            known_cost = False
    return RunEstimate(
        parent_jobs=len(jobs),
        maximum_calls=maximum_calls,
        maximum_cost=maximum_cost if known_cost else None,
        maximum_output_tokens=maximum_calls * config.max_output_tokens,
    )


def plan_jobs(cases: Sequence[BenchmarkCase], config: RunConfig, now: datetime) -> list[Job]:
    if any(model not in config.model_allowlist for model in config.models):
        raise ValueError("model is outside configured allowlist")
    if any(case.split != config.split for case in cases):
        raise ValueError("case split does not match run configuration")
    if Condition.ABLATION in config.conditions and config.split != "development":
        raise ValueError("ablations are restricted to development")
    jobs = []
    for case in select_cases(cases, None):
        for condition in config.conditions:
            instructions = render_condition(condition, config)
            for model in config.models:
                for host in config.hosts:
                    for replicate in range(config.replicates):
                        jobs.append(
                            Job(
                                run_id=config.run_id,
                                case_id=case.id,
                                condition=condition,
                                replicate=replicate,
                                model=model,
                                host=host,
                                prompt=case.prompt,
                                created_at=now,
                                split=case.split,
                                interaction_mode=case.interaction_mode,
                                conversation_script=case.conversation_script,
                                system_instructions=instructions,
                                model_parameters=config.model_parameters
                                | {"max_output_tokens": config.max_output_tokens},
                            )
                        )
    estimate = estimate_run(jobs, config)
    if estimate.maximum_calls > config.max_calls:
        raise ValueError("plan exceeds maximum calls including retry reserve")
    if estimate.maximum_cost is not None and estimate.maximum_cost > config.max_cost:
        raise ValueError("plan exceeds maximum cost")
    return jobs
