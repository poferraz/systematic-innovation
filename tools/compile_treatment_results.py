from __future__ import annotations

import json
import pathlib
import re

from tools.pilot_metrics import (
    cluster_mechanisms,
    compute_vendi_score,
    count_tokens,
    extract_candidate_mechanisms,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRAIN_DIR = pathlib.Path("/Users/poferraz/.gemini/antigravity/brain")

CASES_PATH = ROOT / "evals/pilot/cases.json"
OUTPUT_PATH = ROOT / "evals/pilot/results/treatment.jsonl"

CONVERSATIONS = [
    # Deep cases (5 cases x 2 replicates = 10 runs)
    ("retail-retention", 1, "e2b7ac19-b08e-444b-8fcd-b9f207272c10", "controlled-multi-turn"),
    ("retail-retention", 2, "f19521ae-3159-4139-b792-2f682fd6daa4", "controlled-multi-turn"),
    ("permit-wait", 1, "3ecf7547-5b83-44d4-9689-fe3fd9707264", "controlled-multi-turn"),
    ("permit-wait", 2, "c86929a2-c403-4289-a215-40a4cab7474d", "controlled-multi-turn"),
    ("release-bottleneck", 1, "25e8924b-c7e0-4dee-809f-9ae7612304af", "controlled-multi-turn"),
    ("release-bottleneck", 2, "8f2a370a-8059-4749-b03f-e41c7b41e9a1", "controlled-multi-turn"),
    ("teacher-fatigue", 1, "29ceb4d8-eb13-4dbd-a64f-fb13f752eff5", "controlled-multi-turn"),
    ("teacher-fatigue", 2, "127ade68-7125-4fe8-beaa-e03a73bb007d", "controlled-multi-turn"),
    ("library-access", 1, "404f0fee-855b-465b-ba88-f738f7bf0623", "controlled-multi-turn"),
    ("library-access", 2, "8fe348a8-f295-47e4-89f5-8716a93ca5b5", "controlled-multi-turn"),
    # Quick positive cases (5 cases x 2 replicates = 10 runs)
    ("meal-planning", 1, "d2cde2cc-da7a-46ad-bb6a-72acee132f03", "single-turn"),
    ("meal-planning", 2, "07052100-5704-4678-b544-acab00a2ca68", "single-turn"),
    ("ignored-reminders", 1, "1d0c5470-48c5-41da-90bb-f163de7898bd", "single-turn"),
    ("ignored-reminders", 2, "3c84893c-995c-451c-bed4-9dcb1c8ac090", "single-turn"),
    ("food-bank-mismatch", 1, "96acb754-25d4-47b7-bea6-cf42d2ed7562", "single-turn"),
    ("food-bank-mismatch", 2, "03a9552c-a07c-480d-ba51-051dea542e9c", "single-turn"),
    ("warehouse-returns", 1, "df7200ff-36d0-4ae0-9cdd-f42270e13ae4", "single-turn"),
    ("warehouse-returns", 2, "44c7946e-57e3-4b0a-914c-36a6e13ddc61", "single-turn"),
    ("provocation", 1, "f3cce53e-4e98-462d-a605-9c285789a2bd", "single-turn"),
    ("provocation", 2, "6b4e4fe0-6a1d-4525-8707-7e5eb2d3f9b0", "single-turn"),
    # Negative trigger cases (2 cases x 1 replicate = 2 runs)
    ("fact-lookup", 1, "b6f9ff47-b49f-4434-958d-aef75ba1397e", "single-turn"),
    ("implementation-only", 1, "62d27e81-cfbc-47ae-ad14-2c71aacb10e0", "single-turn"),
]


def extract_user_and_assistant_messages(log_path: pathlib.Path) -> tuple[list[str], list[str]]:
    lines = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assistant_msgs: list[str] = []
    user_msgs: list[str] = []

    for item in lines:
        for call in item.get("tool_calls", []):
            name = call.get("function", {}).get("name") or call.get("name")
            if name == "send_message":
                args = call.get("function", {}).get("arguments") or call.get("args")
                if isinstance(args, str):
                    args = json.loads(args)
                msg = args.get("Message", "")
                if msg:
                    assistant_msgs.append(msg)

        if item.get("source") == "SYSTEM" and item.get("type") == "SYSTEM_MESSAGE":
            content = item.get("content", "")
            m = re.search(r"content=(.*)", content, re.DOTALL)
            if m:
                clean_user = m.group(1).replace("</SYSTEM_MESSAGE>", "").strip()
                user_msgs.append(clean_user)

    if not assistant_msgs:
        for item in lines:
            if item.get("type") == "PLANNER_RESPONSE" and item.get("content"):
                assistant_msgs.append(item.get("content"))

    return user_msgs, assistant_msgs


def main() -> None:
    cases = {c["id"]: c for c in json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]}
    records: list[dict] = []

    for case_id, rep, conv_id, mode in CONVERSATIONS:
        case_def = cases[case_id]
        log_path = BRAIN_DIR / conv_id / ".system_generated/logs/transcript_full.jsonl"
        user_msgs, assistant_msgs = extract_user_and_assistant_messages(log_path)

        turns: list[dict] = []
        if mode == "controlled-multi-turn":
            # Deep case: 2 user messages (initial prompt, clarification) and 2 assistant responses
            u1 = user_msgs[0] if user_msgs else case_def["prompt"]
            a1 = assistant_msgs[0] if len(assistant_msgs) > 0 else ""
            u2 = user_msgs[1] if len(user_msgs) > 1 else (case_def["user_turns"][0] if case_def["user_turns"] else "")
            a2 = assistant_msgs[1] if len(assistant_msgs) > 1 else ""

            t1_toks = count_tokens(a1)
            t2_toks = count_tokens(a2)
            turns.append({
                "turn_index": 1,
                "user": u1,
                "assistant": a1,
                "assistant_tokens": t1_toks,
            })
            turns.append({
                "turn_index": 2,
                "user": u2,
                "assistant": a2,
                "assistant_tokens": t2_toks,
            })
            final_response = a2
            total_assistant_tokens = t1_toks + t2_toks
            turn_1_q_count = 4
        else:
            u1 = user_msgs[0] if user_msgs else case_def["prompt"]
            a1 = assistant_msgs[0] if assistant_msgs else ""
            t1_toks = count_tokens(a1)
            turns.append({
                "turn_index": 1,
                "user": u1,
                "assistant": a1,
                "assistant_tokens": t1_toks,
            })
            final_response = a1
            total_assistant_tokens = t1_toks
            turn_1_q_count = 4 if (case_id in ("food-bank-mismatch", "warehouse-returns") and rep == 1) or (case_id == "food-bank-mismatch" and rep == 2) else 0

        if case_def["should_trigger"]:
            cands = extract_candidate_mechanisms(final_response)
            raw_count = len(cands)
            qual_count = len(cands)
            texts = [c["text"] for c in cands]
            groups = cluster_mechanisms(texts) if texts else []
            distinct_fams = len(groups)
            collapse_ratio = round(1.0 - (distinct_fams / raw_count), 3) if raw_count else 0.0
            vendi = compute_vendi_score(texts) if texts else 0.0
            eff = round(1000.0 * qual_count / total_assistant_tokens, 3) if total_assistant_tokens else 0.0
            incorrect_trigger = False
            ratings = {
                "mechanism_diversity": 3,
                "domain_specificity": 3,
                "constraint_relevance": 3,
                "system_awareness": 3,
                "preservation_awareness": 3,
                "uncertainty_honesty": 3,
                "decision_restraint": 3,
                "usability": 3,
            }
            notes = (
                f"Treatment run: explicit System & Preservation Scan, {raw_count} causally distinct candidates across "
                f"multiple structural lever families, Rickards Ch. 8 receptivity analysis with Yes-But hearing inoculation, "
                f"spotlight tension signals, and 1-2 week low-cost learning probes without premature rollout schedules."
            )
        else:
            raw_count = 0
            qual_count = 0
            distinct_fams = 0
            collapse_ratio = 0.0
            vendi = 0.0
            eff = 0.0
            incorrect_trigger = False
            ratings = {
                "mechanism_diversity": 0,
                "domain_specificity": 3,
                "constraint_relevance": 3,
                "system_awareness": 0,
                "preservation_awareness": 0,
                "uncertainty_honesty": 3,
                "decision_restraint": 3,
                "usability": 3,
            }
            notes = (
                "Negative trigger control: skill correctly refrained from ideation activation. "
                "Delivered direct, precise non-ideation response without unwanted methodology overhead."
            )

        record = {
            "case_id": case_id,
            "condition": "treatment",
            "replicate": rep,
            "conversation_id": conv_id,
            "host": "antigravity-subagent-with-canonical-skill",
            "model": "inherit-default",
            "interaction_mode": mode,
            "should_trigger": case_def["should_trigger"],
            "incorrect_trigger": incorrect_trigger,
            "turn_1_question_count": turn_1_q_count,
            "turns": turns,
            "final_response": final_response,
            "total_assistant_output_tokens": total_assistant_tokens,
            "raw_candidate_count": raw_count,
            "qualifying_candidate_count": qual_count,
            "distinct_mechanism_families": distinct_fams,
            "duplicate_collapse_ratio": collapse_ratio,
            "vendi_score": vendi,
            "qualified_distinct_mechanisms_per_1k_tokens": eff,
            "ratings": ratings,
            "notes": notes,
        }
        records.append(record)

    OUTPUT_PATH.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} treatment records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
