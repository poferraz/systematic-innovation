"""Reproduce descriptive summaries and blind assignments; no semantic ratings."""
import hashlib
import itertools
import json
from pathlib import Path
from statistics import mean

from tools.restored_review import VERSION, blind_answers, measure_record
from tools.pilot_metrics import compute_vendi_score, extract_candidate_mechanisms


ROOT = Path(__file__).resolve().parent
ARMS = ("baseline_clean", "control_creative", "control_format", "skill_treatment")
SOURCES = {
    "before": [ROOT / directory / f"{arm}.jsonl" for directory in ("before-six", "before-boundaries") for arm in ARMS],
    "discovery_only": [ROOT / "discovery-only/skill_treatment.jsonl"],
    "revised": [ROOT / "after/skill_treatment.jsonl"],
    "budget_allocation": [ROOT / "budget-repair/skill_treatment.jsonl"],
    "budget_final": [ROOT / "budget-final/skill_treatment.jsonl"],
    "finite_start": [ROOT / "finite-saturation/starting.jsonl"],
    "finite_revised": [ROOT / "finite-saturation/final.jsonl"],
    "holdout": [ROOT / "holdout" / f"{arm}.jsonl" for arm in ARMS],
}


def main():
    cases = {c["id"]: c for name in ("cases.json", "saturation-reproducer.json", "public-holdout.json")
             for c in json.loads((ROOT / name).read_text())["cases"]}
    all_rows, measurements, integrity, summary = [], [], [], {}
    for epoch, paths in SOURCES.items():
        rows = [{**json.loads(line), "source": str(path.relative_to(ROOT)), "epoch": epoch}
                for path in paths for line in path.read_text().splitlines() if line.strip()]
        all_rows.extend(rows)
        groups = {}
        for row in rows:
            case = cases[row["case_id"]]
            user_turns = [t["user"] for t in row["turns"]]
            assert user_turns[0].endswith(case["prompt"])
            assert user_turns[1:] == case.get("user_turns", [])
            assert row["final_response"] == row["turns"][-1]["assistant"]
            if row["condition"] == "skill_treatment":
                pack = user_turns[0].split("Do not read or infer another methodology.\n\n", 1)[1].rsplit("\n\n=== USER REQUEST ===\n", 1)[0]
                assert hashlib.sha256(pack.encode()).hexdigest() == row["skill_pack_sha256"]
            measurement = measure_record(row, case)
            assert measurement["usage_integrity"] == "consistent cumulative counters"
            measurements.append({**measurement, "epoch": epoch, "source": row["source"]})
            groups.setdefault((row["condition"], row["case_id"]), []).append(measurement)
        summary[epoch] = [{"condition": arm, "case_id": case_id, "runs": len(group),
                           "mean_raw_blocks": mean(r["raw_candidate_blocks"] for r in group),
                           "output_tokens": [r["total_output_tokens"] for r in group],
                           "mean_output_tokens": mean(r["total_output_tokens"] for r in group),
                           "final_words": [r["final_word_count"] for r in group],
                           "word_budget_passes": sum(r["word_budget_compliant"] is True for r in group),
                           "qualified_distinct": None, "primary_effect": None}
                          for (arm, case_id), group in groups.items()]
        integrity.append({"epoch": epoch, "conversations": len(rows),
                          "assistant_turns": sum(len(r["turns"]) for r in rows),
                          "all_exact_disclosures_and_hashes": True})
    packet, key = blind_answers(all_rows, cases)
    for answer_id, mapping in key.items():
        mapping["epoch"] = all_rows[mapping["source_index"]]["epoch"]
    pairs = []
    for (a, ka), (b, kb) in itertools.combinations(key.items(), 2):
        if (ka["case_id"] != kb["case_id"] or ka["replicate"] != kb["replicate"]
                or (ka["condition"], ka["epoch"]) == (kb["condition"], kb["epoch"])):
            continue
        pair_id = f"P{len(pairs)//2+1:04d}"
        pairs.extend([{"pair_id": pair_id, "order": 1, "A": a, "B": b, "preference": None},
                      {"pair_id": pair_id, "order": 2, "A": b, "B": a, "preference": None}])
    repeated = {}
    for epoch in ("before", "revised"):
        rows = [r for r in all_rows if r["epoch"] == epoch and r["case_id"] == "broad-quick" and r["condition"] == "skill_treatment"]
        blocks = [c for r in rows for c in extract_candidate_mechanisms(r["final_response"])]
        repeated[epoch] = {"runs": len(rows), "raw_blocks": len(blocks),
                           "pooled_lexical_vendi": compute_vendi_score(blocks),
                           "causal_homogenization": None}
    target = ROOT / f"final-analysis-{VERSION}"
    target.mkdir(exist_ok=True)
    artifacts = {
        "summary.json": {"by_epoch_and_case": summary, "repeated_prompt_diagnostic": repeated,
                         "primary_effect": None, "human_calibration": "not performed"},
        "integrity.json": {"runs": integrity, "conversations": len(all_rows),
                           "assistant_turns": sum(len(r["turns"]) for r in all_rows),
                           "evaluation_calls_including_three_usage_probes": 3+sum(len(r["turns"]) for r in all_rows),
                           "sources_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                              for paths in SOURCES.values() for p in paths}},
        "measurements.json": measurements, "human-answers.json": packet,
        "human-pairs.json": pairs, "assignment-key.json": key,
    }
    for name, data in artifacts.items():
        (target / name).write_text(json.dumps(data, indent=2) + "\n")
    print("Verified", len(all_rows), "conversations;", artifacts["integrity.json"]["assistant_turns"], "assistant turns")


if __name__ == "__main__":
    main()
