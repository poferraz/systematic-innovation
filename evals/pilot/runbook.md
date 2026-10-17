# Systematic Innovation Pilot Runbook

## 1. Execution Rules

1. **Fresh Contexts:** Every run must execute in a clean, isolated context with no memory of prior cases, rubric criteria, quality-gate formulas, or other experimental conditions.
2. **Identical Prompts and Disclosure Scripts:**
   - **Single-turn cases (`quick` and `none`):** Supply the exact `prompt` from `evals/pilot/cases.json` and capture the single assistant response.
   - **Controlled multi-turn cases (`deep`):**
     1. Turn 1 (User): Supply the exact initial `prompt`. Capture Assistant Turn 1.
     2. Turn 2 (User): Supply `user_turns[0]` verbatim, regardless of whether Assistant Turn 1 asked questions or already proposed ideas. Capture Assistant Turn 2.
     3. Turn 3 (User): Supply `user_turns[1]` verbatim. Capture Assistant Turn 3 (`final_response`).
3. **Token Accounting Across All Turns:**
   - Record output tokens for every assistant turn.
   - `total_assistant_output_tokens` is the sum of assistant output tokens across all turns in the conversation (`Turn 1 + Turn 2 + Turn 3` for controlled multi-turn cases), never only the final portfolio turn.
4. **Replication:**
   - Run every trigger-positive case (`should_trigger: true`, 10 cases) with **2 replicates** per condition.
   - Run every trigger-negative case (`should_trigger: false`, 2 cases) with **1 observation** per condition to test scope restraint and false-positive activation.
5. **Append-Only Preservation:**
   - Store all baseline runs in `evals/pilot/results/baseline.jsonl` and all skill-enabled runs in `evals/pilot/results/treatment.jsonl`.
   - Each JSONL line must contain: `case_id`, `condition`, `replicate`, `host`, `model`, `interaction_mode`, `turns`, `final_response`, `total_assistant_output_tokens`, `extracted_mechanisms`, `raw_distinct_mechanisms`, `qualified_distinct_mechanisms`, `vendi_score`, `primary_efficiency_per_1k_tokens`, `ratings`, `observed_failures`, and `notes`.

## 2. Scoring Procedure

1. Extract every candidate idea from `final_response` into a structured mechanism tuple (`intervention_point`, `principal_actor`, `changed_flow`, `causal_operation`, `intended_effect`).
2. Score each candidate against the conjunctive minimum quality gates defined in `evals/pilot/rubric.md`.
3. Deduplicate raw candidates and qualifying candidates into causal mechanism families using normalized structural signatures and semantic/token equivalence clustering.
4. Compute the judge-free Vendi Score ($\text{VS}_k$) across the extracted mechanism tuples and compute `primary_efficiency_per_1k_tokens = 1000 * qualified_distinct_mechanisms / total_assistant_output_tokens`.
5. Assign the eight 0–3 portfolio ratings with one-sentence evidence excerpts and record all observed failure tags from `target_failures`.
