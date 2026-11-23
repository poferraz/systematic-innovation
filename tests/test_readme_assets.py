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

            view_parts = root.attrib["viewBox"].replace(",", " ").split()
            self.assertEqual(len(view_parts), 4, f"{name} must have 4-number viewBox")
            vb_w, vb_h = float(view_parts[2]), float(view_parts[3])

            rects = [elem for elem in root.iter() if elem.tag.endswith("rect")]
            self.assertTrue(
                any(
                    elem.attrib.get("fill") not in (None, "", "none", "transparent")
                    and elem.attrib.get("x", "0") in ("0", "0px")
                    and elem.attrib.get("y", "0") in ("0", "0px")
                    and float(elem.attrib.get("width", "0")) >= vb_w
                    and float(elem.attrib.get("height", "0")) >= vb_h
                    for elem in rects
                ),
                f"{name} must include a full-canvas opaque backdrop <rect> for light/dark GitHub legibility",
            )
            for forbidden in FORBIDDEN_ASSET_STRINGS:
                self.assertNotIn(forbidden, raw, f"{name} contains forbidden string: {forbidden}")
            for leak in ("/Users/", "/home/", "C:\\"):
                self.assertNotIn(leak, raw, f"{name} contains local filesystem path leak: {leak}")

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
            "evals/audits/2026-11-14-skillevaluator-final.md",
            "2.0.0",
            "SkillEvaluator",
            "Negative-Space Trope Quarantine",
            "Piped Compact",
        ):
            self.assertIn(required, readme, f"README.md missing v2 reference: {required}")

        for guarded in ("README.md", "tools/build_branding.py"):
            text = (ROOT / guarded).read_text(encoding="utf-8")
            for leak in ("/Users/", "/home/", "C:\\"):
                self.assertNotIn(leak, text, f"{guarded} contains local path leak: {leak}")

    def test_active_docs_links_and_audit_closure_consistency(self) -> None:
        fence_re = re.compile(r"```.*?```", re.DOTALL)
        link_re = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
        active_globs = (
            "README.md",
            "AGENTS.md",
            "CONTEXT.md",
            "SECURITY.md",
            "docs/specifications/*.md",
            "benchmark/study/six-case-protocol.md",
            "docs/research/*.md",
            "evals/audits/2026-11-14-*.md",
        )
        checked_files = []
        for pattern in active_globs:
            checked_files.extend(sorted(ROOT.glob(pattern)))
        self.assertTrue(checked_files)

        for md_path in checked_files:
            stripped = fence_re.sub("", md_path.read_text(encoding="utf-8"))
            for match in link_re.finditer(stripped):
                target = match.group(1).strip().split()[0]
                if target.startswith(("http://", "https://", "mailto:", "#", "conversation://", "file://")):
                    continue
                clean_target = target.split("#")[0].split("?")[0]
                if not clean_target:
                    continue
                resolved = (md_path.parent / clean_target).resolve()
                self.assertTrue(
                    resolved.exists(),
                    f"Broken relative link in {md_path.relative_to(ROOT)}: {target}",
                )

        baseline_md = (ROOT / "evals/audits/2026-11-14-skillevaluator-baseline.md").read_text(encoding="utf-8")
        self.assertIn("Gitleaks `8.30.1`", baseline_md)
        self.assertNotIn("/opt/homebrew/bin/gitleaks", baseline_md)


if __name__ == "__main__":
    unittest.main()
