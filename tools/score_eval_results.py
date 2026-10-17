from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Sequence

from tools.pilot_metrics import (
    assess_falsifiability,
    cluster_mechanisms,
    compute_vendi_score,
    count_discovery_questions,
    count_word_budget_compliance,
    detect_preservation_violations,
    extract_candidate_mechanisms,
)


def score_record(record: dict, case: dict | None = None) -> dict:
    case = case or {}
    response = record.get("final_response", "")
    candidates = extract_candidate_mechanisms(response)
    clusters = cluster_mechanisms(candidates)
    levers = [
        candidate.get("causal_lever", "unknown")
        for candidate in candidates
        if candidate.get("causal_lever", "unknown") != "unknown"
    ]
    lever_coverage = round(len(set(levers)) / len(candidates), 3) if candidates else 0.0
    invariants = case.get("preserve") or record.get("preserve") or []
    preservation_violations = detect_preservation_violations(candidates, invariants)
    falsifiability = assess_falsifiability(response)
    word_limit = case.get("word_limit")
    return {
        "case_id": record.get("case_id", case.get("id", "unknown")),
        "condition": record.get("condition", "unspecified"),
        "replicate": record.get("replicate", 0),
        "interaction_mode": record.get("interaction_mode", case.get("interaction_mode", "unknown")),
        "candidate_count": len(candidates),
        "distinct_mechanism_clusters": len(clusters),
        "lever_coverage": lever_coverage,
        "vendi_scores": {
            str(k): compute_vendi_score(candidates, k=k)
            for k in (0.5, 1.0, 2.0)
        },
        "preservation_violation_count": sum(issue["reason"] == "breaks_preserved_asset" for issue in preservation_violations) if invariants else None,
        "missing_preserve_check_count": sum(issue["reason"] == "missing_preserve_check" for issue in preservation_violations),
        "preservation_audit_flags": preservation_violations,
        "preservation_assessment": "lexical_screen_only_not_R5_or_semantic_certification" if invariants else "not_assessed_no_manifest_invariants",
        "token_accounting": record.get("token_accounting", "legacy_estimate_unverified"),
        "falsifiability_rate": falsifiability["rate"],
        "falsifiable_probe_count": falsifiability["falsifiable_count"],
        "learning_probe_count": falsifiability["probe_count"],
        "word_budget_compliant": (
            count_word_budget_compliance(response, int(word_limit))
            if word_limit is not None
            else None
        ),
        "word_count": len(response.split()),
        "discovery_question_count": sum(
            count_discovery_questions(turn.get("assistant", ""))
            for turn in record.get("turns", [{"assistant": response}])
        ),
        "total_assistant_output_tokens": record.get(
            "total_assistant_output_tokens", 0
        ),
    }


def _mean(values: Sequence[float | int | None]) -> float | None:
    present = [float(value) for value in values if value is not None]
    return round(sum(present) / len(present), 3) if present else None


def summarize_results(records: Sequence[dict], cases: Sequence[dict]) -> dict:
    cases_by_id = {case["id"]: case for case in cases}
    scored = [
        score_record(record, cases_by_id.get(record.get("case_id"), {}))
        for record in records
    ]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in scored:
        grouped[record["case_id"]].append(record)

    per_case = {}
    cross_run_mechanisms: dict[str, list] = defaultdict(list)
    for record in records:
        case = cases_by_id.get(record.get("case_id"), {})
        cross_run_mechanisms[record.get("case_id", "unknown")].extend(
            extract_candidate_mechanisms(record.get("final_response", ""))
        )

    for case_id, rows in grouped.items():
        per_case[case_id] = {
            "runs": len(rows),
            "mean_candidates": _mean([row["candidate_count"] for row in rows]),
            "mean_distinct_clusters": _mean(
                [row["distinct_mechanism_clusters"] for row in rows]
            ),
            "mean_lever_coverage": _mean([row["lever_coverage"] for row in rows]),
            "mean_vendi_k_0_5": _mean(
                [row["vendi_scores"]["0.5"] for row in rows]
            ),
            "mean_vendi_k_1": _mean([row["vendi_scores"]["1.0"] for row in rows]),
            "mean_vendi_k_2": _mean([row["vendi_scores"]["2.0"] for row in rows]),
            "mean_preservation_violations": _mean(
                [row["preservation_violation_count"] for row in rows]
            ),
            "mean_falsifiability_rate": _mean(
                [row["falsifiability_rate"] for row in rows]
            ),
            "mean_discovery_questions": _mean(
                [row["discovery_question_count"] for row in rows]
            ),
            "word_budget_compliance": _mean(
                [row["word_budget_compliant"] for row in rows]
            ),
            "cross_run_vendi": {
                str(k): compute_vendi_score(cross_run_mechanisms[case_id], k=k)
                for k in (0.5, 1.0, 2.0)
            },
        }

    return {
        "measurement_scope": "Exploratory structural/lexical diagnostics; no quality-gated primary endpoint or calibrated semantic judgment",
        "record_count": len(scored),
        "aggregate": {
            key: _mean([row[key] for row in scored])
            for key in (
                "candidate_count",
                "distinct_mechanism_clusters",
                "lever_coverage",
                "preservation_violation_count",
                "missing_preserve_check_count",
                "falsifiability_rate",
                "discovery_question_count",
            )
        },
        "aggregate_vendi": {
            "k_0_5": _mean([row["vendi_scores"]["0.5"] for row in scored]),
            "k_1": _mean([row["vendi_scores"]["1.0"] for row in scored]),
            "k_2": _mean([row["vendi_scores"]["2.0"] for row in scored]),
        },
        "per_case": per_case,
        "records": scored,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score JSONL evaluation results")
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    records = [
        json.loads(line)
        for line in args.results.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    cases = json.loads(args.cases.read_text(encoding="utf-8"))["cases"]
    summary = summarize_results(records, cases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Scored {summary['record_count']} records -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
