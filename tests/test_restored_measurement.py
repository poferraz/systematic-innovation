"""Hand-authored extraction boundaries; none of these fixtures rates usefulness."""
import ast
from pathlib import Path
import unittest

from tools.pilot_metrics import assess_falsifiability, extract_candidate_mechanisms
from tools.stress_runner import build_user_prompts, run_case


ROOT = Path(__file__).resolve().parents[1]
A = "Batch collection: Group existing donation pickups by street so volunteers travel less."
B = "Exchange surplus: Let adjacent food banks swap unwanted stock so families receive usable food."


class RestoredMeasurementTests(unittest.TestCase):
    def test_equivalent_explicit_portfolio_layouts_retain_both_proposals(self):
        fixtures = {
            "headings": f"## Possibilities\n### Batch collection\n{A}\n### Exchange surplus\n{B}",
            "table": f"| Possibility | Mechanism |\n| --- | --- |\n| Batch collection | {A} |\n| Exchange surplus | {B} |",
            "list": f"Possible approaches:\n1. {A}\n2. {B}",
            "paragraphs": f"Possibilities:\n\n{A}\n\n{B}",
            "compact": f"P1: Batch collection | Causal chain: {A}\nP2: Exchange surplus | Causal chain: {B}",
        }
        for layout, response in fixtures.items():
            with self.subTest(layout=layout):
                extracted = extract_candidate_mechanisms(response)
                self.assertEqual(len(extracted), 2)
                self.assertIn("volunteers travel less", extracted[0]["text"])
                self.assertIn("usable food", extracted[1]["text"])

    def test_continuation_choices_are_not_learning_probes(self):
        for response in (
            "L6: Expand P1, compare options, or request experiments.",
            "## Layer 6: User-Directed Continuation\n- Expand P1.\n- Compare P1 and P2.",
        ):
            self.assertEqual(assess_falsifiability(response)["probe_count"], 0)

    def test_nonproposal_containers_do_not_become_portfolios(self):
        for section in ("Constraints", "Examples", "Implementation steps", "Refusal", "Rejected ideas"):
            response = f"## {section}\n1. {A}\n2. {B}"
            with self.subTest(section=section):
                self.assertEqual(extract_candidate_mechanisms(response), [])

    def test_later_nonproposal_sections_do_not_leak_into_plain_portfolio(self):
        response = f"Possibilities:\n1. {A}\n2. {B}\n## Implementation steps\n1. Assign owners to each region and schedule a meeting to divide the work."
        extracted = extract_candidate_mechanisms(response)
        self.assertEqual(len(extracted), 2)
        self.assertNotIn("Assign owners", extracted[-1]["text"])

    def test_observed_id_table_retains_the_causal_body_and_stops_before_spotlights(self):
        response = """## Layer 3: Portfolio
| ID / tag | Intervention and causal mechanism | Ledger coordinates |
|---|---|---|
| **P1 — Parts exchange** | Shops list dormant stock so another shop can reuse it without purchasing new inventory. | Information flow at intake |
| **P2 — Capacity routing** | Shops accept voluntary overflow jobs so idle capability reduces regional queues. | Resource allocation at booking |
## Layer 4: Spotlights
| P1 | This is a spotlight and must not create a third candidate. |
"""
        candidates = extract_candidate_mechanisms(response)
        self.assertEqual(len(candidates), 2)
        self.assertIn("dormant stock", candidates[0]["text"])
        self.assertIn("overflow jobs", candidates[1]["text"])
        self.assertNotIn("spotlight", candidates[1]["text"])

    def test_requested_experiment_in_continuation_layer_is_still_detected(self):
        response = "## Layer 6: User-Directed Continuation\n- Experiment 1: observe 20 requests for 2 weeks; if fewer than 10 complete, revert."
        self.assertEqual(assess_falsifiability(response)["probe_count"], 1)

    def test_control_table_is_the_portfolio_instead_of_selected_detail_headings(self):
        response = """## Portfolio: two possibilities
| Possibility | Mechanism | Intended value |
|---|---|---|
| 1. Batch collection | Group existing pickups by street so volunteers travel less. | Less travel |
| 2. Exchange surplus | Swap unwanted stock with adjacent food banks so families receive useful food. | Better access |
## Selected possibilities
### 1. Batch collection
This fuller description repeats the first possibility and is not another candidate.
"""
        candidates = extract_candidate_mechanisms(response)
        self.assertEqual(len(candidates), 2)
        self.assertIn("volunteers travel less", candidates[0]["text"])
        self.assertIn("useful food", candidates[1]["text"])

    def test_numbered_name_column_in_control_table_is_a_portfolio(self):
        response = """## Portfolio of alternatives
| # | Name | Mechanism | Fit note |
|---|---|---|---|
| 1 | Parts exchange | Shops lend spare stock to one another, reducing duplicate purchasing. | Voluntary |
| 2 | Capacity signals | Shops publish available repair capacity so work can reach idle capability. | Optional |
## Selected possibilities
### 1. Parts exchange
This longer description is a repeat, not the complete portfolio.
"""
        self.assertEqual(len(extract_candidate_mechanisms(response)), 2)

    def test_observed_ways_to_improve_container_keeps_short_bold_bullets(self):
        response = """Ways to improve access while preserving privacy:
- **Limit popular seeds** so more people receive scarce varieties.
- **Label substitutes** so borrowers can choose available alternatives.
"""
        self.assertEqual(len(extract_candidate_mechanisms(response)), 2)

    def test_plain_portfolio_does_not_count_selected_details_or_continuation(self):
        response = f"## Possibilities\n### Batch collection\n{A}\n### Exchange surplus\n{B}\n## Spotlights\n### Batch collection\n{A}\n## User-Directed Continuation\n- Expand this option into a longer explanation of the mechanism and its uncertainties."
        self.assertEqual(len(extract_candidate_mechanisms(response)), 2)

    def test_tables_inside_nonproposal_sections_do_not_become_candidates(self):
        for section in ("Examples", "Rejected ideas", "Constraints", "Implementation steps"):
            for header in ("Possibility | Mechanism", "Name | Mechanism"):
                response = f"## {section}\n| {header} |\n|---|---|\n| Batch collection | {A} |\n| Exchange surplus | {B} |"
                with self.subTest(section=section, header=header):
                    self.assertEqual(extract_candidate_mechanisms(response), [])

    def test_selected_details_and_connections_are_not_an_extra_proposal(self):
        response = f"## Portfolio\n1. **Batch collection** — {A}\n2. **Exchange surplus** — {B}\n## Selected details and connections\nCombine both approaches to coordinate transport and improve availability without adding staff.\n## Continuation choices\n- Expand one of these options into a fuller description."
        self.assertEqual(len(extract_candidate_mechanisms(response)), 2)

    def test_candidate_local_receptivity_is_not_a_later_disclosure_layer(self):
        response = f"## L3: Complete Portfolio\n### P1. Batch collection\n{A}\n- **Receptivity:** voluntary cooperation; workload is uncertain.\n### P2. Exchange surplus\n{B}\n- **Receptivity:** partner consent; preserve stock labels.\n## L4: Possibility Spotlights\nP1 and P2 are repeated here for comparison."
        self.assertEqual(len(extract_candidate_mechanisms(response)), 2)
        plain_fields = response.replace('- **Receptivity:**', '**Receptivity:**')
        self.assertEqual(len(extract_candidate_mechanisms(plain_fields)), 2)

    def test_test_method_names_are_not_silently_overwritten(self):
        tree = ast.parse((ROOT / "tests/test_skill_behavior.py").read_text())
        for cls in (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)):
            names = [node.name for node in cls.body if isinstance(node, ast.FunctionDef)]
            self.assertEqual(len(names), len(set(names)), cls.name)

    def test_format_matched_control_preserves_identical_disclosures(self):
        case = {"prompt": "Find alternatives for this process.", "expected_mode": "deep",
                "user_turns": ["Preserve access.", "No new staff.", "Final portfolio now."]}
        prompts = build_user_prompts(case, "control_format", ROOT / "skills/systematic-innovation")
        self.assertEqual(prompts[1:], ["Preserve access.", "No new staff.", "Final portfolio now."])
        self.assertTrue(prompts[0].endswith(case["prompt"]))
        self.assertIn("15 to 24", prompts[0])
        for term in ("Reasoning Cells", "Mechanism Ledger", "saturation", "system map"):
            self.assertNotIn(term, prompts[0])

    def test_raw_transport_metadata_survives_and_unknown_cost_stays_unknown(self):
        from unittest.mock import patch
        case = {"id": "capture", "prompt": "Initial", "user_turns": ["Final"],
                "expected_mode": "deep", "interaction_mode": "controlled-multi-turn", "should_trigger": True}
        with patch("tools.stress_runner._execute", side_effect=[
            ("First", "session", {"output_tokens": 5, "input_tokens": 100},
             {"latency_seconds": 1.25, "events": [{"type": "first"}]}),
            ("Last", "session", {"output_tokens": 11, "input_tokens": 250},
             {"latency_seconds": 2.0, "events": [{"type": "second"}]}),
        ]):
            record = run_case(case, "baseline_clean", 1, ROOT / "skills/systematic-innovation", "model", "codex")
        self.assertEqual(record["turns"][0]["transport"]["events"], [{"type": "first"}])
        self.assertEqual(record["total_latency_seconds"], 3.25)
        self.assertEqual(record["total_input_tokens"], 250)
        self.assertIsNone(record["monetary_cost"])
