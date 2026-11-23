from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills/systematic-innovation"


def read(name: str) -> str:
    return (SKILL_DIR / name).read_text(encoding="utf-8")


class SkillBehaviorContractTests(unittest.TestCase):
    def test_single_turn_execution_channel_precedes_substantive_complexity(self) -> None:
        skill = read("SKILL.md")
        deep = read("references/deep-mode.md")
        self.assertIn("Execution-Channel Precedence", skill)
        self.assertIn("single-turn", skill)
        self.assertIn("complete portfolio", skill)
        self.assertIn("Hard Output Budget Precedence", skill)
        self.assertIn("80% of the requested ceiling", skill)
        self.assertIn("Never activate Deep Mode Turn-1 restraint solely because", deep)

    def test_deep_mode_requires_an_actual_interactive_channel(self) -> None:
        deep = read("references/deep-mode.md")
        self.assertIn("Actual interaction availability is mandatory", deep)
        self.assertIn("single-turn request", deep)
        self.assertIn("complete portfolio", deep)

    def test_explicit_output_budgets_override_verbose_contract(self) -> None:
        contract = read("references/output-contract.md")
        self.assertIn("Budget precedence", contract)
        self.assertIn("hard word or token ceiling", contract)
        self.assertIn("compressed six-layer response", contract)
        self.assertIn("Never exceed", contract)
        self.assertIn("80% of the stated word ceiling", contract)
        self.assertIn("ultra-compact format", contract)
        self.assertIn("Compact Portfolio Template", contract)
        self.assertNotIn("four candidate lines", contract)
        self.assertNotIn("250 words", contract)
        self.assertNotIn("state saturation", contract)

    def test_brief_and_portfolio_retain_approved_information(self) -> None:
        # Static completeness lint; fresh model outputs are reviewed separately.
        skill = read("SKILL.md")
        for field in ("Desired change", "Beneficiary", "Current insufficiency", "Existing strengths",
                      "Preservation requirements", "Nonnegotiable constraints", "Success signals", "Dominant frame"):
            self.assertIn(field, skill)
        contract = read("references/output-contract.md")
        for field in ("Intended value", "Portfolio category", "Originating lens",
                      "Required cooperation", "Principal resistance", "Preservation risk", "Major unknown"):
            self.assertIn(field, contract)

    def test_duplicate_labels_do_not_define_causal_equivalence(self) -> None:
        self.assertNotIn("Same lever + same stage = merge", read("references/innovation-lenses.md"))
        self.assertNotIn("same causal lever at the same stage", read("SKILL.md"))

    def test_impossible_constraints_do_not_become_noncompliant_candidates(self) -> None:
        contract = read("references/output-contract.md")
        skill = read("SKILL.md")
        self.assertIn("Contradiction & Boundary Re-Anchor", contract)
        self.assertIn("Do not number boundary relaxations as Possibility Portfolio candidates", contract)
        self.assertIn("fake compliance", skill)

    def test_candidate_fields_expose_causal_structure_and_preservation(self) -> None:
        contract = read("references/output-contract.md")
        for anchor in (
            "Intervention point",
            "Causal chain",
            "Causal lever",
            "Preserve check",
        ):
            self.assertIn(anchor, contract)
        self.assertIn("every Layer 1 preservation invariant", contract)

    def test_requested_experiments_are_falsifiable_with_bounds_and_fallback(self) -> None:
        contract = read("references/output-contract.md")
        self.assertIn("Only when the user explicitly requests experiments", contract)
        for anchor in (
            "quantitative disconfirmation threshold",
            "sample or observation bound",
            "time horizon",
            "fallback next move",
        ):
            self.assertIn(anchor, contract)
        self.assertIn("Reject or revise the mechanism if", contract)


    def test_portfolio_targets_match_approved_specification(self) -> None:
        skill = read("SKILL.md")
        contract = read("references/output-contract.md")
        self.assertIn("**10 to 15 distinct possibilities**", skill)
        self.assertIn("**15 to 24 distinct possibilities**", skill)
        self.assertIn("**Quick Mode:** **10 to 15**", contract)
        self.assertIn("**Deep Mode:** **15 to 24**", contract)
        self.assertIn("targets, not quotas", contract)

    def test_deep_discovery_asks_one_question_at_a_time(self) -> None:
        skill = read("SKILL.md")
        deep = read("references/deep-mode.md")
        self.assertIn("one question at a time", skill)
        self.assertIn("Ask exactly one decision-relevant question", deep)
        self.assertIn("Do not batch discovery questions", deep)
        self.assertIn("Never exceed 7 total questions", deep)

    def test_deep_discovery_has_no_fixed_two_exchange_shortcut(self) -> None:
        # Contract lint only; the four-turn behavioral reproducer supplies evidence.
        deep = read("references/deep-mode.md")
        self.assertNotIn("Two discovery exchanges have occurred", deep)

    def test_experiments_appear_only_after_explicit_request(self) -> None:
        skill = read("SKILL.md")
        contract = read("references/output-contract.md")
        self.assertIn("Only when the user explicitly requests experiments", skill)
        self.assertIn("No experiment, pilot, rollout, or implementation plan appears automatically", contract)
        self.assertIn("If the user explicitly requests experiments", contract)
        self.assertIn("### Layer 6: User-Directed Continuation", contract)
        self.assertNotIn("Low-Cost Learning Probes", contract)

    def test_disclosure_layers_match_approved_contract(self) -> None:
        contract = read("references/output-contract.md")
        for heading in (
            "### Layer 1: Innovation Brief",
            "### Layer 2: System Snapshot",
            "### Layer 3: Complete Portfolio",
            "### Layer 4: Possibility Spotlights",
            "### Layer 5: Connections and Tensions",
            "### Layer 6: User-Directed Continuation",
        ):
            self.assertIn(heading, contract)

    def test_reasoning_cell_taxonomy_has_no_retired_cell_labels(self) -> None:
        skill = read("SKILL.md")
        lenses = read("references/innovation-lenses.md")
        for cell in (
            "System Dynamics",
            "Human Value",
            "Operational Reality",
            "Boundary Reframing",
            "Mechanism Transfer",
            "Contrarian",
            "Futures",
        ):
            self.assertIn(cell, skill)
            self.assertIn(cell, lenses)
        self.assertNotIn("Cell A:", lenses)
        self.assertNotIn("Cell G:", lenses)

    def test_reasoning_cells_are_original_ai_mechanisms(self) -> None:
        evidence = read("references/evidence.md")
        lenses = read("references/innovation-lenses.md")
        self.assertIn("Reasoning Cells as explicit cognitive operators", evidence)
        self.assertIn("Project-original AI-native mechanism", lenses)
        self.assertNotIn("Seven Reasoning Cells (Cells A–G)", evidence)

    def test_provenance_table_lists_all_original_ai_mechanisms(self) -> None:
        evidence = read("references/evidence.md")
        for mechanism in (
            "Quick and Deep routing",
            "Perspective Council presentation layer",
            "Reasoning Cells as explicit cognitive operators",
            "Mechanism ledger",
            "Mechanism-level duplicate detection",
            "Saturation-based stopping",
            "Progressive output disclosure",
            "Cross-agent capability fallback",
        ):
            self.assertIn(mechanism, evidence)

    def test_reasoning_cells_match_approved_specification(self) -> None:
        skill = read("SKILL.md")
        lenses = read("references/innovation-lenses.md")
        for cell in (
            "System Dynamics",
            "Human Value",
            "Operational Reality",
            "Boundary Reframing",
            "Mechanism Transfer",
            "Contrarian",
            "Futures",
        ):
            self.assertIn(cell, skill)
            self.assertIn(cell, lenses)
        self.assertIn("Provocation mode requires Contrarian and Boundary Reframing", skill)
        self.assertIn("System Dynamics plus two selected Reasoning Cells", skill)
        self.assertIn("five or six selected Reasoning Cells", skill)
        self.assertIn("Two to four candidate mechanisms", lenses)
        self.assertIn("System Dynamics plus two selected Reasoning Cells", skill)
        self.assertIn("five or six selected Reasoning Cells", skill)
        self.assertIn("Two to four candidate mechanisms", lenses)

    def test_original_ai_mechanisms_are_not_attributed_to_rickards(self) -> None:
        evidence = read("references/evidence.md")
        for mechanism in (
            "Quick and Deep routing",
            "Perspective Council presentation layer",
            "Reasoning Cells as explicit cognitive operators",
            "Mechanism ledger",
            "Mechanism-level duplicate detection",
            "Saturation-based stopping",
            "Progressive output disclosure",
            "Cross-agent capability fallback",
        ):
            self.assertIn(mechanism, evidence)
        self.assertNotIn("Seven Reasoning Cells (Cells A–G)", evidence)

    def test_behavioral_spec_includes_execution_channel_and_budget_precedence(self) -> None:
        spec = (ROOT / "docs/specifications/skill-and-evaluation.md").read_text(encoding="utf-8")
        self.assertIn("### 6.4 Execution-channel precedence", spec)
        self.assertIn("### 12.1 User-requested output budgets", spec)

    def test_skill_pack_implements_spec_research_nochg_highstakes_quick_q_and_lenses(self) -> None:
        skill = read("SKILL.md")
        lenses = read("references/innovation-lenses.md")
        contract = read("references/output-contract.md")
        evidence = read("references/evidence.md")

        # F-09: Capability-aware research when host provides tools (§15)
        self.assertIn("host provides", skill.lower())
        self.assertIn("offline", skill.lower())

        # F-10: Valid preservation-first / no-change conclusion (§12)
        self.assertIn("no-change", contract.lower())
        self.assertIn("preservation-first", contract.lower())

        # F-21: High-stakes exploratory + verification needs labeling (§14)
        self.assertIn("exploratory", skill.lower())
        self.assertIn("verification needs", skill.lower())

        # F-22: Quick mode one critical question allowance (§6.1)
        self.assertIn("critical unknown", skill.lower())

        # F-23: Morphological recombination and subtraction operational cues (§10)
        self.assertIn("Morphological recombination", lenses)
        self.assertIn("Subtraction", lenses)

        # F-17: Corrected Lawrence/Lorsch chapter locator in Rickards (1985)
        self.assertIn("Ch. 4", evidence)
        self.assertNotIn("Ch. 7–8", evidence)

    def test_skill_v2_probabilistic_and_skillevaluator_sections(self) -> None:
        import re

        skill = read("SKILL.md")
        spec = (ROOT / "docs/specifications/skill-and-evaluation.md").read_text(encoding="utf-8")
        for heading in (
            "## Purpose",
            "## Prerequisites",
            "## Instructions",
            "## Examples",
            "## Limitations",
            "## Troubleshooting",
        ):
            self.assertIn(heading, skill)
        self.assertIn("```text", skill)
        self.assertIsNone(
            re.search(r"\b(?:utilize|facilitate|leverage|paradigm|synergy)\b", skill, re.IGNORECASE),
            "SKILL.md should avoid complex/corporate filler wording flagged by SkillEvaluator",
        )
        self.assertIn("Negative-Space Trope Quarantine", skill)
        self.assertIn("tail", skill.lower())
        self.assertIn("legacy delivery vehicle", skill.lower())
        self.assertIn("Selling-In", skill)
        self.assertIn("Selling-Out", skill)
        for anchor in (
            "### 8.1 Invariant vs. Legacy-Vehicle Separation",
            "### 10.1 Anti-Typicality Two-Stage Protocol",
            "### 16.1 Standard structure, progressive disclosure, and bibliographic accuracy",
        ):
            self.assertIn(anchor, spec)

    def test_output_contract_and_lenses_v2_mechanisms(self) -> None:
        from tools.pilot_metrics import detect_preservation_violations, extract_candidate_mechanisms

        lenses = read("references/innovation-lenses.md")
        contract = read("references/output-contract.md")
        deep = read("references/deep-mode.md")

        self.assertIn("two-node abstract", lenses.lower())
        self.assertIn("2x2", lenses)
        self.assertIn("Liability-to-Asset Reversal", lenses)
        self.assertIn("at least five distinct causal clusters", lenses.lower())
        self.assertIn("legacy delivery vehicle", lenses.lower())
        self.assertIn("legacy delivery vehicle", deep.lower())

        self.assertIn("Selling-In", contract)
        self.assertIn("Selling-Out", contract)
        self.assertIn("Lever:", contract)
        self.assertIn("Intervention:", contract)
        self.assertIn("Chain:", contract)
        self.assertIn("Preserve:", contract)

        sample_compact = (
            "L1: Reduce rural no-shows | Preserve: continuity of care, no new clinical staff | Quarantine: SMS reminders\n"
            "L2: Intake lag causes missed visits; mobile check-in channel is idle\n"
            "L3:\n"
            "P1: Peer Shuttle Bundle | Lever: boundary separation | Intervention: ride dispatch | "
            "Chain: Group intake by ZIP -> volunteer courier pairs rides -> attendance rises | "
            "Preserve: all L1 invariants; continuity of care and no new clinical staff | "
            "Failure: sparse route match | Fit: participative — driver stipend boundary respected\n"
            "L4: Best fit P1 (Selling-In: uses existing dispatch; Selling-Out: cuts rider travel barrier)\n"
            "L5: P1 complements async triage\n"
            "L6: Expand P1 or run another cell?"
        )
        extracted = extract_candidate_mechanisms(sample_compact)
        self.assertGreaterEqual(len(extracted), 1)
        self.assertEqual(extracted[0]["causal_lever"], "boundary separation")
        violations = detect_preservation_violations(extracted, ["continuity of care", "no new clinical staff"])
        self.assertEqual(violations, [])

    def test_evidence_rickards_1985_pagination_and_no_fabricated_appendix(self) -> None:
        evidence = read("references/evidence.md")
        for verified_locator in (
            "(p. 33)",
            "(p. 63)",
            "(p. 87)",
            "(p. 114;",
            "pp. 126–127",
            "(p. 135;",
            "(p. 158;",
            "p. 161)",
            "(p. 184)",
        ):
            self.assertIn(verified_locator, evidence)
        for bad_locator in (
            "Appendix: Techniques for stimulating creativity in innovation",
            "(p. 190)",
            "(p. 28)",
            "(p. 50)",
            "(p. 72)",
            "(p. 92;",
            "p. 97)",
            "(p. 131;",
            "p. 166)",
            "(p. 176)",
        ):
            self.assertNotIn(bad_locator, evidence)
        for paper in ("Zhang et al.", "Deng, Brucks", "Friedman & Dieng", "Nguyen et al.", "Yuan et al.", "Hu et al."):
            self.assertIn(paper, evidence)

    def test_v2_iteration2_compact_candidate_cap_and_mandatory_lever_preserve_labels(self) -> None:
        skill = read("SKILL.md")
        contract = read("references/output-contract.md")
        self.assertIn("3 to 4", skill)
        self.assertIn("4 to 5", skill)
        self.assertIn("3 to 4", contract)
        self.assertIn("4 to 5", contract)
        self.assertIn("Causal lever:", skill)
        self.assertIn("Preserve check:", skill)
        self.assertIn("Causal lever:", contract)

if __name__ == "__main__":
    unittest.main()
