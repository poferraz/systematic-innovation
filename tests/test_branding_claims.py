from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_ASSET_STRINGS = (
    "+162%",
    "8.2x",
    "Pilot Lift",
    "Learning Probes",
    "≤ 4 Questions",
    "&le; 4 Questions",
    "4 surgical questions",
    "5 structural dimensions",
    "0.90 MECH / 1K TOK",
    "2.35 MECH / 1K TOK",
    "1–2 Wk Probes",
    "6 DISTINCT LEVERS",
    "1.36 vs 0.17",
)
FORBIDDEN_README_ACTIVE_STRINGS = (
    "still need reconciliation",
    "still require reconciliation",
    "Transforms ordinary AI ideation",
)


class BrandingClaimsRegressionTests(unittest.TestCase):
    def test_build_branding_contains_no_withdrawn_claims_or_superseded_rules(self) -> None:
        source = (ROOT / "tools/build_branding.py").read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_ASSET_STRINGS:
            self.assertNotIn(forbidden, source)

    def test_readme_embeds_no_withdrawn_claims_or_stale_reconciliation_text(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_ASSET_STRINGS + FORBIDDEN_README_ACTIVE_STRINGS:
            self.assertNotIn(forbidden, readme)
        self.assertIn("evals/restored-2026-10-18/report.md", readme)
        self.assertIn("references/innovation-lenses.md", readme)


if __name__ == "__main__":
    unittest.main()
