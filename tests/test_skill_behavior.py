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
        self.assertIn("min(80% of the stated word ceiling, 250 words)", contract)
        self.assertIn("Layer 1 at most 40 words", contract)
        self.assertIn("each candidate at most 30 words", contract)
        self.assertIn("Compact Portfolio Template", contract)
        self.assertIn("No Markdown tables, headings, or bold styling", contract)
        self.assertIn("supersedes the normal Six Disclosure Layers formatting", contract)
        self.assertIn("Each candidate line at most 30 visible words including labels", contract)
        self.assertIn("omit optional assumption and failure prose", contract)

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

    def test_learning_probes_are_falsifiable_with_bounds_and_fallback(self) -> None:
        contract = read("references/output-contract.md")
        for anchor in (
            "quantitative disconfirmation threshold",
            "sample or observation bound",
            "time horizon",
            "fallback next move",
        ):
            self.assertIn(anchor, contract)
        self.assertIn("Reject or revise the mechanism if", contract)


if __name__ == "__main__":
    unittest.main()
