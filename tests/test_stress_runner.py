import json
from pathlib import Path
import unittest

from tools.stress_runner import (
    build_user_prompts,
    build_initial_command,
    expected_run_count,
    load_cases,
    load_skill_pack,
)


ROOT = Path(__file__).resolve().parents[1]


class StressRunnerTests(unittest.TestCase):
    def test_treatment_prompt_loads_the_complete_canonical_skill_pack(self) -> None:
        case = {
            "id": "case",
            "prompt": "User prompt.",
            "user_turns": [],
        }
        prompts = build_user_prompts(case, "skill_treatment", ROOT / "skills/systematic-innovation")
        skill_text = load_skill_pack(ROOT / "skills/systematic-innovation")
        self.assertEqual(prompts[0].count(skill_text), 1)
        self.assertIn("User prompt.", prompts[0])
        self.assertEqual(prompts, [prompts[0]])

    def test_controls_do_not_embed_skill_behavior(self) -> None:
        case = {"id": "case", "prompt": "User prompt.", "user_turns": []}
        baseline = build_user_prompts(case, "baseline_clean", ROOT / "skills/systematic-innovation")
        control = build_user_prompts(case, "control_creative", ROOT / "skills/systematic-innovation")
        skill_text = load_skill_pack(ROOT / "skills/systematic-innovation")
        self.assertNotIn(skill_text, baseline[0])
        self.assertNotIn(skill_text, control[0])
        self.assertIn("creative", control[0].lower())
        self.assertEqual(baseline, ["User prompt."])

    def test_multi_turn_prompts_preserve_turn_boundaries(self) -> None:
        case = {
            "id": "case",
            "prompt": "Initial prompt.",
            "user_turns": ["Turn 2.", "Turn 3.", "Turn 4."],
        }
        prompts = build_user_prompts(case, "skill_treatment", ROOT / "skills/systematic-innovation")
        self.assertEqual(len(prompts), 4)
        self.assertIn("Initial prompt.", prompts[0])
        self.assertEqual(prompts[1:], ["Turn 2.", "Turn 3.", "Turn 4."])

    def test_expected_run_count_matches_manifest_replicates(self) -> None:
        cases = load_cases(ROOT / "evals/stress/cases.json")
        self.assertEqual(expected_run_count(cases), 42)
        self.assertEqual(sum(case["replicates"] for case in cases), 42)


if __name__ == "__main__":
    unittest.main()


class StressRunnerCommandTests(unittest.TestCase):
    def test_initial_command_supports_isolated_non_repo_root(self) -> None:
        command = build_initial_command(
            codex="/codex",
            model="model",
            output_path=Path("/tmp/output.md"),
            workdir=Path("/tmp"),
        )
        self.assertIn("--skip-git-repo-check", command)
        self.assertIn("-C", command)
        self.assertIn("/tmp", command)
