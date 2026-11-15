"""Provider-neutral benchmark command interface."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml

from .models import ScoreRecord
from .planner import estimate_run
from .redaction import redact_model
from .reporting import build_report_data, write_json_report, write_markdown_report
from .runtime import RunDirectory, load_config, prepare, public_cases
from .scoring.deterministic import score_deterministic
from .scoring.mechanisms import (
    distinct_mechanism_count,
    extract_mechanisms,
    gate_failures,
    qualified_distinct_mechanism_count,
    validate_semantic_equivalences,
    vendi_score,
)
from .store import append_record, read_records


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="sib", description="Controlled systematic ideation benchmark"
    )
    commands = root.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--config", type=Path, required=True)
    pack = commands.add_parser("validate-pack")
    pack.add_argument("--restricted-pack", type=Path, required=True)
    pack.add_argument("--split", choices=("validation", "test"))
    for name in ("plan", "run"):
        item = commands.add_parser(name)
        item.add_argument("--config", type=Path, required=True)
        item.add_argument("--cases", type=Path, required=True)
        item.add_argument("--case-ids")
        item.add_argument("--run-dir", type=Path, required=True)
        item.add_argument("--preregistration", type=Path)
        item.add_argument("--dry-run", action="store_true")
    for name in ("export", "ingest", "resume", "score", "report", "verify-run"):
        item = commands.add_parser(name)
        item.add_argument("--run-dir", type=Path, required=True)
        if name != "verify-run":
            item.add_argument("--dry-run", action="store_true")
        if name == "export":
            item.add_argument("--output", type=Path, required=True)
        if name == "ingest":
            item.add_argument("--input", type=Path, required=True)
        if name == "score":
            item.add_argument("--judgments", type=Path)
    compare = commands.add_parser("compare")
    compare.add_argument("--baseline", type=Path, required=True)
    compare.add_argument("--candidate", type=Path, required=True)
    preflight = commands.add_parser("restricted-preflight")
    preflight.add_argument("--declaration", type=Path, required=True)
    preflight.add_argument("--output", type=Path, required=True)
    preflight.add_argument("--dry-run", action="store_true")
    return root


def _score(run: RunDirectory, judgments: Path | None = None) -> dict[str, int]:
    import os

    run.require_current_source()
    config = run.manifest.config
    secrets = [os.environ[key] for key in config.secret_environment_keys if os.environ.get(key)]
    existing = {s.job_id: s for s in read_records(run.inside("records/scores.jsonl"), ScoreRecord)}
    external = (
        {s.job_id: redact_model(s, secrets) for s in read_records(judgments, ScoreRecord)}
        if judgments
        else {}
    )
    jobs = {j.job_id: j for j in run.jobs}
    if not set(external) <= set(jobs):
        raise ValueError("unknown judged job")
    count = 0
    for response in run.responses:
        if response.job_id in existing:
            if (
                response.job_id in external
                and external[response.job_id] != existing[response.job_id]
            ):
                raise ValueError("scores are immutable; use a versioned scoring run")
            continue
        job = jobs[response.job_id]
        final = response.conversation.final_response if response.conversation else response.content
        candidates = tuple(extract_mechanisms(final)) if response.status == "succeeded" else ()
        if response.job_id in external:
            supplied = external[response.job_id]
            # A separate measurement role supplies extraction + criterion evidence.
            # It cannot silently turn a failed generation into a useful mechanism.
            if response.status != "succeeded" and supplied.mechanisms:
                raise ValueError("failed generation cannot contain qualified mechanisms")
            for m in supplied.mechanisms:
                if m.quality and (
                    not all(
                        m.quality.evidence.get(key, "").strip()
                        for key in (
                            "relevance",
                            "constraint_alignment",
                            "causal_clarity",
                            "plausibility",
                            "critical_safety_violation",
                        )
                    )
                ):
                    raise ValueError("criterion-specific evidence required")
            candidates = supplied.mechanisms
        semantic_evidence = (
            external[job.job_id].metrics.get("semantic_equivalences", [])
            if job.job_id in external
            else []
        )
        pairs = validate_semantic_equivalences(candidates, semantic_evidence)
        family = next(c.family for c in run.manifest.cases if c.id == job.case_id)
        score = ScoreRecord(
            job_id=job.job_id,
            mechanisms=candidates,
            criterion_scores=score_deterministic(job, response),
            evidence=external[job.job_id].evidence if job.job_id in external else {},
            judge_id=external[job.job_id].judge_id if job.job_id in external else None,
            metrics={
                "family": family,
                "raw_distinct": distinct_mechanism_count(candidates, pairs),
                "qualified_distinct": qualified_distinct_mechanism_count(candidates, pairs),
                "semantic_equivalences": semantic_evidence,
                "vendi_score": vendi_score(candidates),
                "gate_failures": {m.id: gate_failures(m.quality) for m in candidates},
            },
        )
        append_record(run.inside("records/scores.jsonl"), score, secret_values=secrets)
        count += 1
    run.snapshot()
    return {"scored_jobs": count}


def dispatch(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "validate":
        config = load_config(args.config)
        return {"valid": True, "run_id": config.run_id, "dry_run": config.dry_run}
    if args.command == "validate-pack":
        from .restricted import validate_restricted_pack

        summary = validate_restricted_pack(args.restricted_pack)
        return summary.model_dump(mode="json")
    if args.command == "restricted-preflight":
        from .restricted_preflight import authorize_restricted_run, load_declaration

        record = authorize_restricted_run(load_declaration(args.declaration))
        if not args.dry_run:
            # Authorization records cannot replace historical approval evidence.
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(record.model_dump_json(indent=2) + "\n")
        return {"authorized": True, "dry_run": args.dry_run}
    if args.command in ("plan", "run"):
        config = load_config(args.config)
        cases = public_cases(
            args.cases, args.case_ids.split(",") if args.case_ids is not None else None
        )
        if args.preregistration:
            import yaml

            from .study_contracts import validate_preregistration

            issues = validate_preregistration(yaml.safe_load(args.preregistration.read_text()))
            if issues:
                raise ValueError("preregistration contract failed")
        jobs, manifest = prepare(config, cases)
        estimate = estimate_run(jobs, config)
        if args.dry_run or config.dry_run:
            return dict(run_id=config.run_id, dry_run=True, **estimate.model_dump())
        run = RunDirectory(args.run_dir)
        with run.lock():
            run.create(jobs, manifest)
            calls = run.execute() if args.command == "run" else 0
        return dict(
            run_id=config.run_id, dry_run=False, executed_calls=calls, **estimate.model_dump()
        )
    if args.command == "compare":
        baseline, candidate = RunDirectory(args.baseline), RunDirectory(args.candidate)
        baseline.verify()
        candidate.verify()
        b, c = baseline.manifest, candidate.manifest
        return {
            "baseline": b.run_id,
            "candidate": c.run_id,
            "same_corpus": b.artifact_digests["public_corpus"]
            == c.artifact_digests["public_corpus"],
            "same_skill": b.skill_revision == c.skill_revision,
            "same_runner": b.git_revision == c.git_revision
            and b.runner_source_sha256 == c.runner_source_sha256,
            "parameters_equal": b.config.model_parameters == c.config.model_parameters,
            "limitations": "Manifest comparison only; effects require paired case analysis.",
        }
    run = RunDirectory(args.run_dir)
    if args.command == "verify-run":
        return run.verify()
    if args.dry_run:
        run.verify()
        return {"dry_run": True, "pending_turns": len(run.pending())}
    with run.lock():
        run.verify()
        run.require_current_source()
        if args.command == "export":
            return {"pending_turns": run.export(args.output)}
        if args.command == "ingest":
            return {"ingested_turns": run.ingest(args.input)}
        if args.command == "resume":
            if set(run.manifest.config.hosts) == {"subprocess"}:
                run.execute()
            pending = run.pending(finalize=True)
            run.snapshot()
            return {"pending_turns": len(pending)}
        if args.command == "score":
            return _score(run, args.judgments)
        if args.command == "report":
            manifest = run.manifest
            scores = read_records(run.inside("records/scores.jsonl"), ScoreRecord)
            data = build_report_data(
                run.jobs,
                run.responses,
                scores,
                skill_revision=manifest.skill_revision,
                runner_revision=manifest.git_revision,
                benchmark_version=manifest.benchmark_version,
            )
            data["revisions"]["runner_source_sha256"] = manifest.runner_source_sha256
            data["revisions"]["runner_worktree_dirty"] = manifest.runner_worktree_dirty
            if manifest.runner_worktree_dirty:
                data["limitations"].append(
                    "The public runner worktree was dirty at planning; source digest identifies the executed checkout."
                )
            write_json_report(data, run.inside("reports/report.json"))
            write_markdown_report(data, run.inside("reports/report.md"))
            run.snapshot()
            return {"reports": 2, "headline_automated_claim_allowed": False}
    raise ValueError("unknown command")


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = dispatch(args)
    except (ValueError, OSError, KeyError, TypeError, yaml.YAMLError):
        # Pydantic, YAML, adapters and pack contents are untrusted. Never print
        # exception reprs, input values, local paths or provider error payloads.
        print(json.dumps({"error": "VALIDATION_OR_EXECUTION_REFUSED"}))
        return 1
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
