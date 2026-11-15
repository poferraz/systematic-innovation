from datetime import UTC, datetime

import pytest

from systematic_innovation_bench.models import (
    BenchmarkCase,
    Condition,
    ConversationScript,
    InteractionMode,
    RunConfig,
)
from systematic_innovation_bench.planner import estimate_run, plan_jobs, select_cases

NOW = datetime(2026, 8, 31, tzinfo=UTC)


def case(id="a", deep=False, split="development"):
    return BenchmarkCase(
        id=id,
        family="open-ended-systemic",
        domain="operations",
        split=split,
        prompt="Improve this system",
        strata={"mode": "deep" if deep else "quick"},
        interaction_mode=InteractionMode.CONTROLLED_MULTI_TURN
        if deep
        else InteractionMode.SINGLE_TURN,
        conversation_script=ConversationScript(user_turns=("First context", "Final portfolio now"))
        if deep
        else None,
    )


def config(**updates):
    return RunConfig(
        **(
            {
                "run_id": "r",
                "models": ("m",),
                "model_allowlist": ("m",),
                "conditions": (Condition.VANILLA,),
                "max_calls": 100,
            }
            | updates
        )
    )


def test_exact_selection_rejects_duplicate_unknown_and_empty_ids():
    cases = [case("b"), case("a")]
    assert [c.id for c in select_cases(cases, ["b"])] == ["b"]
    for ids in (("a", "a"), ("missing",), ("",)):
        with pytest.raises(ValueError):
            select_cases(cases, ids)


def test_factorial_jobs_and_information_are_stable():
    cfg = config(
        conditions=(Condition.VANILLA, Condition.FORMAT_MATCHED),
        replicates=2,
        hosts=("inbox", "local"),
    )
    jobs = plan_jobs([case("b"), case("a", deep=True)], cfg, NOW)
    assert len(jobs) == 16
    assert [j.case_id for j in jobs[:8]] == ["a"] * 8
    assert all(j.prompt == "Improve this system" for j in jobs)
    assert all(j.conversation_script == jobs[0].conversation_script for j in jobs[:8])
    assert [j.job_id for j in jobs] == [
        j.job_id for j in plan_jobs([case("a", True), case("b")], cfg, NOW)
    ]


def test_estimate_counts_all_turns_and_retry_reserve_and_unknown_cost():
    cfg = config(retry_limit=1)
    jobs = plan_jobs([case("a", True), case("b")], cfg, NOW)
    estimate = estimate_run(jobs, cfg)
    assert estimate.maximum_calls == 8
    assert estimate.maximum_output_tokens == 32768
    assert estimate.maximum_cost is None
    priced = config(cost_per_turn={"m": 0.5})
    assert estimate_run(jobs, priced).maximum_cost == 4.0


@pytest.mark.parametrize(
    "cfg,cases",
    [
        (config(max_calls=2), [case("a", True)]),
        (config(model_allowlist=("other",)), [case()]),
        (
            config(conditions=(Condition.ABLATION,), ablation="ledger", split="validation"),
            [case(split="validation")],
        ),
        (config(cost_per_turn={"m": 10.0}, max_cost=1), [case()]),
    ],
)
def test_plans_fail_closed_on_limits(cfg, cases):
    with pytest.raises(ValueError):
        plan_jobs(cases, cfg, NOW)


def test_full_skill_runtime_authority_and_ablations_require_named_development_variant(tmp_path):
    skill = tmp_path / "skill"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text("Frozen canonical text")
    (skill / "references/deep.md").write_text("Supporting authority")
    job = plan_jobs([case()], config(conditions=(Condition.FULL_SKILL,), skill_path=skill), NOW)[0]
    assert "Frozen canonical text" in job.system_instructions
    assert "Supporting authority" in job.system_instructions
    with pytest.raises(ValueError):
        plan_jobs([case()], config(conditions=(Condition.ABLATION,)), NOW)
