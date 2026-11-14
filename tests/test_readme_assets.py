"""Regression checks for Phase D README assets, custom SVGs, and claim discipline."""
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

from tests.test_branding_claims import FORBIDDEN_ASSET_STRINGS


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
EXPECTED_PNGS = (
    "banner.png",
    "comparison.png",
    "system-architecture.png",
    "quick-demo.png",
)
EXPECTED_SVGS = (
    "v2-anti-collapse-loop.svg",
    "v2-piped-budget-lock.svg",
)


class ReadmeVisualAssetsTests(unittest.TestCase):
    def test_expected_png_and_svg_assets_exist(self) -> None:
        for name in EXPECTED_PNGS + EXPECTED_SVGS:
            path = ASSETS_DIR / name
            self.assertTrue(path.is_file(), f"Missing visual asset: {path}")
            self.assertGreater(path.stat().st_size, 1024, f"Asset too small: {path}")

    def test_svg_files_are_self_contained_theme_safe_and_claim_clean(self) -> None:
        for name in EXPECTED_SVGS:
            path = ASSETS_DIR / name
            raw = path.read_text(encoding="utf-8")
            root = ET.fromstring(raw)
            self.assertTrue(root.tag.endswith("svg"), f"{name} root element must be <svg>")
            self.assertIn("viewBox", root.attrib, f"{name} must declare a viewBox")

            lowered = raw.lower()
            stripped = lowered.replace("http://www.w3.org/2000/svg", "")
            self.assertNotIn("<foreignobject", lowered, f"{name} must avoid <foreignObject>")
            self.assertNotIn("<script", lowered, f"{name} must not embed <script>")
            self.assertNotIn("http://", stripped, f"{name} must not fetch remote assets")
            self.assertNotIn("https://", stripped, f"{name} must not fetch remote assets")

            rects = [elem for elem in root.iter() if elem.tag.endswith("rect")]
            self.assertTrue(
                any(elem.attrib.get("fill") not in (None, "", "none", "transparent") for elem in rects),
                f"{name} must include an opaque background <rect> for light/dark GitHub legibility",
            )
            for forbidden in FORBIDDEN_ASSET_STRINGS:
                self.assertNotIn(forbidden, raw, f"{name} contains forbidden string: {forbidden}")

    def test_readme_embeds_verified_v2_assets_and_reports(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        md_images = re.findall(r"!\[[^\]]*\]\((assets/[^)#?]+)\)", readme)
        html_images = re.findall(r'<img[^>]+src="(assets/[^"?#]+)"', readme)
        referenced = md_images + html_images
        self.assertTrue(referenced, "README.md must reference assets/")
        for rel in referenced:
            self.assertTrue((ROOT / rel).is_file(), f"README references missing asset: {rel}")

        for svg in EXPECTED_SVGS:
            self.assertIn(f"assets/{svg}", readme, f"README.md must showcase {svg}")
        for required in (
            "evals/v2-loop/report.md",
            "evals/restored-2026-10-18/report.md",
            "2.0.0",
            "SkillEvaluator",
            "Negative-Space Trope Quarantine",
            "Piped Compact",
        ):
            self.assertIn(required, readme, f"README.md missing v2 reference: {required}")


if __name__ == "__main__":
    unittest.main()
