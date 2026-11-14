import json
from pathlib import Path
import re
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

    def test_control_format_targets_match_canonical_skill_targets(self) -> None:
        skill_text = (ROOT / "skills/systematic-innovation/SKILL.md").read_text(encoding="utf-8")
        quick_match = re.search(r"\*\*(\d+\s+to\s+\d+)\s+distinct possibilities\*\* in one turn", skill_text)
        deep_match = re.search(r"synthesize \*\*(\d+\s+to\s+\d+)\s+distinct possibilities\*\*", skill_text)
        self.assertIsNotNone(quick_match, "Quick Mode target range missing in SKILL.md")
        self.assertIsNotNone(deep_match, "Deep Mode target range missing in SKILL.md")
        quick_target = quick_match.group(1)
        deep_target = deep_match.group(1)
        self.assertEqual(quick_target, "10 to 15")
        self.assertEqual(deep_target, "15 to 24")

        case_quick = {"id": "c1", "prompt": "Prompt", "expected_mode": "quick"}
        case_deep = {"id": "c2", "prompt": "Prompt", "expected_mode": "deep"}
        quick_prompt = build_user_prompts(case_quick, "control_format", ROOT / "skills/systematic-innovation")[0]
        deep_prompt = build_user_prompts(case_deep, "control_format", ROOT / "skills/systematic-innovation")[0]
        self.assertIn(quick_target, quick_prompt)
        self.assertIn(deep_target, deep_prompt)


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

class StressPersistenceTests(unittest.TestCase):
    def test_interruption_keeps_completed_turn_and_resume_skips_it(self):
        import tempfile
        from unittest.mock import patch
        from tools.stress_runner import run_case
        case = {"id": "resume", "prompt": "Initial", "user_turns": ["Final"],
                "interaction_mode": "controlled-multi-turn", "expected_mode": "deep",
                "should_trigger": True, "topology": "test", "preserve": [], "primary_source": "test"}
        with tempfile.TemporaryDirectory() as tmp:
            progress = Path(tmp) / "turns.json"
            with patch("tools.stress_runner._execute", side_effect=[("First", "session"), RuntimeError("transport")]):
                with self.assertRaisesRegex(RuntimeError, "transport"):
                    run_case(case, "baseline_clean", 1, ROOT / "skills/systematic-innovation", "model", "codex", progress_path=progress)
            self.assertEqual(json.loads(progress.read_text())["turns"][0]["assistant"], "First")
            with patch("tools.stress_runner._execute", return_value=("Last", "session")) as external:
                record = run_case(case, "baseline_clean", 1, ROOT / "skills/systematic-innovation", "model", "codex", progress_path=progress)
            self.assertEqual(external.call_count, 1)
            self.assertEqual([turn["assistant"] for turn in record["turns"]], ["First", "Last"])

    def test_unmanifested_existing_results_are_not_relabelled(self):
        import tempfile
        from tools.stress_runner import main
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = root / "cases.json"
            cases.write_text(json.dumps({"cases": [{"id": "one", "prompt": "New prompt", "replicates": 1,
                "should_trigger": True, "user_turns": []}]}))
            output = root / "out"
            output.mkdir()
            original = json.dumps({"case_id": "one", "condition": "baseline_clean", "replicate": 1,
                                   "model": "old-model", "final_response": "Old answer"}) + "\n"
            result = output / "baseline_clean.jsonl"
            result.write_text(original)
            with self.assertRaisesRegex(ValueError, "manifest"):
                main(["--cases", str(cases), "--output", str(output), "--conditions", "baseline_clean"])
            self.assertEqual(result.read_text(), original)
            self.assertFalse((output / "manifest.json").exists())

class ProviderAccountingTests(unittest.TestCase):
    def test_resumed_usage_is_differenced_not_summed(self):
        from unittest.mock import patch
        from tools.stress_runner import run_case
        case = {"id": "usage", "prompt": "Initial", "user_turns": ["More", "Final"],
                "interaction_mode": "controlled-multi-turn", "expected_mode": "deep", "should_trigger": True}
        with patch("tools.stress_runner._execute", side_effect=[
            ("alpha", "session", {"output_tokens": 5}),
            ("beta", "session", {"output_tokens": 10}),
            ("gamma", "session", {"output_tokens": 15}),
        ]):
            record = run_case(case, "baseline_clean", 1, ROOT / "skills/systematic-innovation", "model", "codex")
        self.assertEqual(record["total_assistant_output_tokens"], 15)
        self.assertEqual([turn["assistant_tokens"] for turn in record["turns"]], [5, 5, 5])
        self.assertEqual([turn["provider_usage_cumulative"]["output_tokens"] for turn in record["turns"]], [5, 10, 15])

class LegacyProgressAccountingTests(unittest.TestCase):
    def test_legacy_cumulative_progress_requires_explicit_migration(self):
        import hashlib, tempfile
        from unittest.mock import patch
        from tools.stress_runner import run_case
        case = {"id": "legacy", "prompt": "Initial", "user_turns": ["Final"],
                "interaction_mode": "controlled-multi-turn", "expected_mode": "deep", "should_trigger": True}
        with tempfile.TemporaryDirectory() as tmp:
            progress = Path(tmp) / 'progress.json'
            original = json.dumps({'prompt_digest': hashlib.sha256(json.dumps(['Initial', 'Final']).encode()).hexdigest(),
                'model': 'model', 'session_id': 'session', 'turns': [{'turn_index': 1, 'user': 'Initial',
                'assistant': 'First', 'assistant_tokens': 10, 'assistant_tokens_estimate': 2}]})
            progress.write_text(original)
            with patch('tools.stress_runner._execute', side_effect=AssertionError('must fail before model execution')), self.assertRaisesRegex(ValueError, 'accounting'):
                run_case(case, 'baseline_clean', 1, ROOT / 'skills/systematic-innovation', 'model', 'codex', progress_path=progress)
            self.assertEqual(progress.read_text(), original)

class ConcurrentRunSafetyTests(unittest.TestCase):
    def test_two_controllers_cannot_append_the_same_completed_job(self):
        import tempfile, threading, time
        from concurrent.futures import ThreadPoolExecutor
        from unittest.mock import patch
        from tools.stress_runner import main
        ready = threading.Event()
        release = threading.Event()
        def remote(*args, **kwargs):
            ready.set()
            release.wait(3)
            return {'case_id': 'one', 'condition': 'baseline_clean', 'replicate': 1,
                    'total_assistant_output_tokens': 5}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = root / 'cases.json'
            cases.write_text(json.dumps({'cases': [{'id': 'one', 'prompt': 'User prompt',
                'should_trigger': True, 'replicates': 1, 'user_turns': []}]}))
            output = root / 'out'
            args = ['--cases', str(cases), '--output', str(output), '--conditions', 'baseline_clean']
            with patch('tools.stress_runner.run_case', side_effect=remote):
                with ThreadPoolExecutor(max_workers=2) as pool:
                    first = pool.submit(main, args)
                    self.assertTrue(ready.wait(2))
                    second = pool.submit(main, args)
                    time.sleep(0.1)
                    release.set()
                    self.assertEqual(first.result(), 0)
                    self.assertEqual(second.result(), 0)
            self.assertEqual(len((output / 'baseline_clean.jsonl').read_text().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
