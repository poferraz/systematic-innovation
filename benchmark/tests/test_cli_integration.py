from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "systematic_innovation_bench.cli", *map(str, args)],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        check=False,
    )


def setup_inputs(tmp_path, *, dry_run=False, host="inbox", **changes):
    cases = tmp_path / "cases.yaml"
    cases.write_text(
        yaml.safe_dump(
            {
                "cases": [
                    {
                        "id": "a",
                        "family": "synthetic-mechanism",
                        "domain": "operations",
                        "split": "development",
                        "prompt": "Give 2 ideas",
                        "strata": {"mode": "quick"},
                    },
                    {
                        "id": "b",
                        "family": "open-ended-systemic",
                        "domain": "education",
                        "split": "development",
                        "prompt": "Improve choices",
                        "strata": {"mode": "deep"},
                        "interaction_mode": "controlled-multi-turn",
                        "conversation_script": {
                            "user_turns": [
                                "Preserve access",
                                "Only local resources. Final portfolio",
                            ]
                        },
                    },
                ]
            }
        )
    )
    config = tmp_path / "config.yaml"
    data = {
        "run_id": "test-run",
        "models": ["fake"],
        "model_allowlist": ["fake"],
        "hosts": [host],
        "conditions": ["vanilla", "full-skill", "format-matched"],
        "retry_limit": 0,
        "max_calls": 30,
        "max_cost": 1,
        "max_concurrency": 6,
        "cost_per_turn": {"fake": 0.01},
        "dry_run": dry_run,
        "failure_threshold": 1,
        "skill_path": str(REPO / "skills/systematic-innovation"),
    } | changes
    config.write_text(yaml.safe_dump(data))
    return cases, config, tmp_path / "run"


def test_complete_inbox_workflow_resume_score_report_and_digest_verification(tmp_path):
    cases, config, run = setup_inputs(tmp_path)
    result = cli("plan", "--cases", cases, "--config", config, "--run-dir", run, "--dry-run")
    assert result.returncode == 0, result.stderr
    assert not run.exists()
    result = cli("plan", "--cases", cases, "--config", config, "--run-dir", run)
    assert result.returncode == 0, result.stderr
    disclosures = {}
    for n in range(3):
        outgoing, incoming = run / f"outgoing-{n}.jsonl", run / f"incoming-{n}.jsonl"
        result = cli("export", "--run-dir", run, "--output", outgoing)
        assert result.returncode == 0, result.stderr
        packets = [json.loads(line) for line in outgoing.read_text().splitlines()]
        for packet in packets:
            assert "full-skill" not in packet["job_id"]
            disclosures.setdefault(packet["job_id"], []).append(
                [t["content"] for t in packet["transcript"] if t["role"] == "user"]
            )
        incoming.write_text(
            "".join(
                json.dumps(
                    {
                        "job_id": p["job_id"],
                        "turn_index": p["assistant_turn_index"],
                        "content": "P1: First | Intervention: queue | Lever: pool demand | Chain: tasks -> pooled slots -> less delay",
                        "output_tokens": 100,
                        "input_tokens": 10,
                        "cost": 0.01,
                        "latency_seconds": 0.1,
                        "attempt": p["attempt"],
                    }
                )
                + "\n"
                for p in packets
            )
        )
        result = cli("ingest", "--run-dir", run, "--input", incoming)
        assert result.returncode == 0, result.stderr
    result = cli("resume", "--run-dir", run)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["pending_turns"] == 0
    responses = [
        json.loads(line) for line in (run / "records/responses.jsonl").read_text().splitlines()
    ]
    assert len(responses) == 6
    deep = [
        r["conversation"]
        for r in responses
        if r["conversation"] and len(r["conversation"]["turns"]) == 6
    ]
    assert len(deep) == 3
    assert all(c["total_assistant_output_tokens"] == 300 for c in deep)
    assert len({tuple(t["content"] for t in c["turns"] if t["role"] == "user") for c in deep}) == 1
    for command in [("score",), ("report",), ("verify-run",)]:
        result = cli(*command, "--run-dir", run)
        assert result.returncode == 0, result.stderr
    report = json.loads((run / "reports/report.json").read_text())
    assert report["counts"]["total_assistant_output_tokens"] == 1200
    assert report["counts"]["qualified_distinct_families"] == 0  # fake output has no judgments
    assert report["headline_automated_claim_allowed"] is False
    result = cli("compare", "--baseline", run, "--candidate", run)
    assert result.returncode == 0, result.stderr
    with (run / "records/responses.jsonl").open("a") as stream:
        stream.write("{}\n")
    assert cli("verify-run", "--run-dir", run).returncode != 0


def test_case_selection_rejects_unknown_repeated_empty_and_dry_run_never_writes(tmp_path):
    cases, config, run = setup_inputs(tmp_path)
    for selection in ["z", "a,a", "a,", ""]:
        result = cli(
            "plan", "--cases", cases, "--config", config, "--run-dir", run, "--case-ids", selection
        )
        assert result.returncode != 0
        assert not run.exists()


def test_subprocess_run_and_resume_do_not_regenerate_successes(tmp_path):
    script = ROOT / "tests/fixtures/fake_agent.py"
    cases, config, run = setup_inputs(
        tmp_path,
        host="subprocess",
        adapter_command=[sys.executable, str(script)],
        allowed_executables=[sys.executable],
    )
    result = cli("run", "--cases", cases, "--config", config, "--run-dir", run)
    assert result.returncode == 0, result.stderr
    before = (run / "records/turns.jsonl").read_bytes()
    result = cli("resume", "--run-dir", run)
    assert result.returncode == 0, result.stderr
    assert (run / "records/turns.jsonl").read_bytes() == before
    assert cli("verify-run", "--run-dir", run).returncode == 0


def test_unknown_cost_prevents_launch_and_errors_never_echo_values(tmp_path):
    cases, config, run = setup_inputs(tmp_path, host="subprocess", cost_per_turn={})
    result = cli("run", "--cases", cases, "--config", config, "--run-dir", run)
    assert result.returncode != 0
    assert not (run / "records/turns.jsonl").exists()
    sentinel = "confidential-payload-123456789"
    config.write_text("model_allowlist: " + sentinel)
    result = cli("validate", "--config", config)
    assert result.returncode != 0
    leaked = sentinel in result.stdout + result.stderr
    assert not leaked


def test_output_path_cannot_escape_run_directory(tmp_path):
    cases, config, run = setup_inputs(tmp_path)
    assert cli("plan", "--cases", cases, "--config", config, "--run-dir", run).returncode == 0
    result = cli("export", "--run-dir", run, "--output", tmp_path / "escape.jsonl")
    assert result.returncode != 0
    assert not (tmp_path / "escape.jsonl").exists()


def test_generator_cannot_supply_its_own_quality_ratings():
    from systematic_innovation_bench.scoring.mechanisms import extract_mechanisms

    payload = {
        "mechanisms": [
            {
                "id": "a",
                "intervention_point": "queue",
                "actor": "staff",
                "changed_flow": "demand",
                "causal_operation": "pool",
                "intended_effect": "delay",
                "quality": {
                    "relevance": 3,
                    "constraint_alignment": 3,
                    "causal_clarity": 3,
                    "plausibility": 3,
                    "critical_safety_violation": False,
                },
            }
        ]
    }
    assert extract_mechanisms(json.dumps(payload))[0].quality is None


def test_malformed_yaml_diagnostics_never_print_input(tmp_path):
    sentinel = "".join(["private", "-yaml", "-sentinel"])  # noqa: FLY002 -- synthetic private input
    config = tmp_path / "bad.yaml"
    config.write_text("run_id: [" + sentinel)
    result = cli("validate", "--config", config)
    assert result.returncode != 0
    leaked = sentinel in result.stdout + result.stderr
    assert not leaked
    assert "Traceback" not in result.stderr


def test_configuration_credentials_are_rejected_before_manifest_write(tmp_path, monkeypatch):
    sentinel = "-".join(["synthetic", "configured", "credential"])  # noqa: FLY002 -- synthetic input
    monkeypatch.setenv("SIB_TEST_CREDENTIAL", sentinel)
    cases, config, run = setup_inputs(
        tmp_path,
        secret_environment_keys=["SIB_TEST_CREDENTIAL"],
        model_parameters={"opaque_parameter": sentinel},
    )
    result = cli("plan", "--cases", cases, "--config", config, "--run-dir", run)
    assert result.returncode != 0
    assert not run.exists()
    leaked = sentinel in result.stdout + result.stderr
    assert not leaked


def test_manifest_identifies_current_executable_source_not_only_git_head(tmp_path):
    cases, config, run = setup_inputs(tmp_path)
    result = cli("plan", "--cases", cases, "--config", config, "--run-dir", run)
    assert result.returncode == 0
    manifest = json.loads((run / "manifest.json").read_text())
    assert len(manifest["runner_source_sha256"]) == 64
    assert isinstance(manifest["runner_worktree_dirty"], bool)


def test_scoring_redacts_configured_secret_in_all_retained_judge_material(tmp_path, monkeypatch):
    from systematic_innovation_bench.models import Mechanism, MechanismQuality, ScoreRecord
    from systematic_innovation_bench.store import read_records

    sentinel = "-".join(["synthetic", "score", "credential"])  # noqa: FLY002 -- constructed synthetic credential
    monkeypatch.setenv("SIB_SCORE_CREDENTIAL", sentinel)
    script = ROOT / "tests/fixtures/fake_agent.py"
    cases, config, run = setup_inputs(
        tmp_path,
        host="subprocess",
        secret_environment_keys=["SIB_SCORE_CREDENTIAL"],
        adapter_command=[sys.executable, str(script)],
        allowed_executables=[sys.executable],
    )
    result = cli("run", "--cases", cases, "--config", config, "--run-dir", run)
    assert result.returncode == 0
    job_id = json.loads((run / "records/jobs.jsonl").read_text().splitlines()[0])["job_id"]
    evidence = {
        key: sentinel
        for key in (
            "relevance",
            "constraint_alignment",
            "causal_clarity",
            "plausibility",
            "critical_safety_violation",
        )
    }
    quality = MechanismQuality(
        relevance=2,
        constraint_alignment=2,
        causal_clarity=2,
        plausibility=1,
        critical_safety_violation=False,
        evidence=evidence,
    )
    mechanisms = tuple(
        Mechanism(
            id=identifier,
            intervention_point="queue",
            actor="staff",
            changed_flow="demand",
            causal_operation="pool requests",
            intended_effect="less delay",
            principal_constraint=sentinel,
            quality=quality,
            evidence={"source": sentinel},
        )
        for identifier in ("m1", "m2")
    )
    score = ScoreRecord(
        job_id=job_id,
        mechanisms=mechanisms,
        evidence={"review": sentinel},
        metrics={"semantic_equivalences": [{"left": "m1", "right": "m2", "evidence": sentinel}]},
    )
    judgments = tmp_path / "judgments.jsonl"
    judgments.write_text(score.model_dump_json() + "\n")
    result = cli("score", "--run-dir", run, "--judgments", judgments)
    assert result.returncode == 0
    canonical = run / "records/scores.jsonl"
    leaked = sentinel in canonical.read_text()
    assert not leaked
    saved = next(s for s in read_records(canonical, ScoreRecord) if s.job_id == job_id)
    assert saved.metrics["qualified_distinct"] == 1
    assert saved.metrics["semantic_equivalences"][0]["evidence"] == "[REDACTED]"
    assert cli("report", "--run-dir", run).returncode == 0
    leaked = any(sentinel in path.read_text() for path in (run / "reports").iterdir())
    assert not leaked


def test_changed_runner_source_blocks_all_mutating_existing_run_commands(
    tmp_path, monkeypatch, capsys
):
    from systematic_innovation_bench import runtime
    from systematic_innovation_bench.cli import main

    cases, config, run = setup_inputs(tmp_path)
    assert cli("plan", "--cases", cases, "--config", config, "--run-dir", run).returncode == 0
    before = (run / "integrity.jsonl").read_bytes()
    monkeypatch.setattr(runtime, "current_source_digest", lambda: "0" * 64)
    for command in ("resume", "score", "report"):
        assert main([command, "--run-dir", str(run)]) == 1
    assert (run / "integrity.jsonl").read_bytes() == before
    assert not (run / "records/dispatches.jsonl").exists()
    assert not (run / "records/scores.jsonl").exists()
    assert not (run / "reports").exists()
    capsys.readouterr()
