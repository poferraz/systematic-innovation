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
    def test_public_home_url_survives_next_to_a_local_path(self):
        from tools.stress_runner import redact_text

        url = "https://example.org/us-en/home/example/guide.html"
        direct = "https://example.org/home/example/guide.html"
        result = redact_text(f"{url} {direct} path=/home/fixture-operator/docs file:///home/fixture-operator/guide")
        self.assertEqual(result, f"{url} {direct} path=~/docs ~/guide")

    def test_command_paths_are_private_in_public_records_and_progress(self):
        import subprocess
        import tempfile
        from unittest.mock import patch
        from tools.stress_runner import run_case

        executable = "/home/fixture-operator/bin/codex"
        case = {"id": "portable", "prompt": "Example", "interaction_mode": "single-turn",
                "expected_mode": "quick", "should_trigger": True}

        def execute(command, **kwargs):
            self.assertEqual(command[0], executable)
            Path(command[command.index("-o") + 1]).write_text("Example response")
            events = [
                {"type": "thread.started", "thread_id": "fixture-thread", "api_key": "fixture-value"},
                {"type": "turn.completed", "usage": {"output_tokens": 2},
                 "diagnostic": "config in /home/fixture-operator/settings.json"},
            ]
            return subprocess.CompletedProcess(command, 0, "\n".join(map(json.dumps, events)))

        with tempfile.TemporaryDirectory() as temp, patch("tools.stress_runner.subprocess.run", execute):
            progress = Path(temp) / "progress.json"
            record = run_case(case, "baseline_clean", 1, ROOT / "skills/systematic-innovation",
                              "fixture-model", executable, progress_path=progress)
            self.assertEqual(json.loads(progress.read_text())["session_id"], "fixture-thread")
            self.assertNotIn("fixture-thread", json.dumps(record))
            for retained in (record, json.loads(progress.read_text())):
                self.assertNotIn("fixture-operator", json.dumps(retained))
                self.assertNotIn("fixture-value", json.dumps(retained))
                transport = retained["turns"][0]["transport"]
                command = transport["command"]
                self.assertEqual(command[0], "codex")
                self.assertEqual(command[command.index("-o") + 1], "<run-output>/last-message.md")
                self.assertEqual(command[command.index("-C") + 1], "<workdir>")
                self.assertEqual(transport["events"][-1]["usage"]["output_tokens"], 2)

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

    def test_stress_runner_supports_codex_config_passthrough(self) -> None:
        from tools.stress_runner import build_resume_command, parse_args

        args = parse_args(["--codex-config", "model_reasoning_effort=low"])
        self.assertEqual(args.codex_config, ["model_reasoning_effort=low"])
        init_cmd = build_initial_command(
            codex="/codex",
            model="model",
            output_path=Path("/tmp/out.md"),
            workdir=Path("/tmp"),
            codex_configs=["model_reasoning_effort=low"],
        )
        resume_cmd = build_resume_command(
            codex="/codex",
            model="model",
            session_id="00000000-0000-0000-0000-000000000000",
            output_path=Path("/tmp/out.md"),
            codex_configs=["model_reasoning_effort=low"],
        )
        for cmd in (init_cmd, resume_cmd):
            idx = cmd.index("-c")
            self.assertEqual(cmd[idx + 1], "model_reasoning_effort=low")

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


class StressRunnerSafetyTests(unittest.TestCase):
    def test_rejects_model_outside_allowlist(self):
        import tempfile
        from tools.stress_runner import main
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = root / "cases.json"
            cases.write_text(json.dumps({"cases": [{"id": "c1", "prompt": "Hi", "replicates": 1, "should_trigger": True, "user_turns": []}]}))
            output = root / "out"
            # Default allowed_models should be ["gpt-5.6-luna"]
            with self.assertRaises(ValueError):
                main(["--cases", str(cases), "--output", str(output), "--model", "unapproved-model", "--dry-run"])
            # When explicitly included in --allowed-models, it should not raise ValueError
            self.assertEqual(main(["--cases", str(cases), "--output", str(output), "--model", "unapproved-model", "--allowed-models", "unapproved-model", "--dry-run"]), 0)

    def test_aborts_when_estimated_or_accumulated_cost_exceeds_max_cost(self):
        import tempfile
        from unittest.mock import patch
        from tools.stress_runner import main
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = root / "cases.json"
            cases.write_text(json.dumps({"cases": [{"id": "c1", "prompt": "Hi", "replicates": 1, "should_trigger": True, "user_turns": []}]}))
            output = root / "out"
            with patch("tools.stress_runner._execute", return_value=(
                "response", "session", {"input_tokens": 1000, "output_tokens": 500},
                {"latency_seconds": 1.0, "events": []}
            )):
                with self.assertRaises((RuntimeError, ValueError)):
                    main([
                        "--cases", str(cases),
                        "--output", str(output),
                        "--max-cost", "0.50",
                        "--cost-per-1k-input", "1.00",
                        "--cost-per-1k-output", "2.00",
                    ])

    def test_redacts_credentials_from_transport_events_and_errors(self):
        from tools.stress_runner import redact_text, redact_obj, redact_secrets, run_case
        from unittest.mock import patch
        import tempfile

        sk_tok = "sk-" + "1234567890abcdef1234567890"
        aiza_tok = "AIza" + "1234567890abcdef1234567890"
        ghp_tok = "ghp_" + "1234567890abcdef1234567890"
        nvapi_tok = "nvapi-" + "1234567890abcdef"
        nvidia_tok = "NVIDIA_" + "1234567890"
        raw_secrets = [
            sk_tok,
            aiza_tok,
            ghp_tok,
            nvapi_tok,
            nvidia_tok,
            "Bearer " + "secret_bearer_token_xyz",
            "api_key: " + "secret_api_key_12345",
            "token = '" + "secret_token_abc'",
            "secret=\"" + "secret_val_xyz\"",
        ]
        sample_text = "Errors: " + " ".join(raw_secrets)
        redacted = redact_text(sample_text)
        self.assertIn("[REDACTED]", redacted)
        for secret in raw_secrets:
            self.assertNotIn(secret, redacted)
        for token in (sk_tok, aiza_tok, ghp_tok, nvapi_tok, nvidia_tok):
            self.assertNotIn(token, redacted)

        nested_obj = {
            "auth": "Bearer " + "token123",
            "list": [{"key": aiza_tok}],
            "tuple": (ghp_tok,),
        }
        redacted_obj = redact_obj(nested_obj)
        self.assertEqual(redacted_obj["auth"], "[REDACTED]")
        self.assertEqual(redacted_obj["list"][0]["key"], "[REDACTED]")
        self.assertEqual(redacted_obj["tuple"][0], "[REDACTED]")

        # Verify transport events and error redaction in run_case
        case = {"id": "c1", "prompt": "Hi", "user_turns": [], "interaction_mode": "single-turn", "expected_mode": "quick", "should_trigger": True}
        with tempfile.TemporaryDirectory() as tmp:
            with patch("tools.stress_runner._execute", return_value=(
                f"Here is key {sk_tok} and Bearer supersecrettoken", "session", {},
                {"latency_seconds": 0.5, "events": [{"auth": "Bearer supersecrettoken"}]}
            )):
                record = run_case(case, "baseline_clean", 1, ROOT / "skills/systematic-innovation", "gpt-5.6-luna", "codex")
                events_str = json.dumps(record["turns"][0]["transport"]["events"])
                self.assertNotIn("supersecrettoken", events_str)
                self.assertIn("[REDACTED]", events_str)

                # Check both final_response and turns assistant text
                self.assertNotIn(sk_tok, record["final_response"])
                self.assertNotIn("supersecrettoken", record["final_response"])
                self.assertIn("[REDACTED]", record["final_response"])

                self.assertNotIn(sk_tok, record["turns"][-1]["assistant"])
                self.assertNotIn("supersecrettoken", record["turns"][-1]["assistant"])
                self.assertIn("[REDACTED]", record["turns"][-1]["assistant"])

    def test_aborts_when_failures_exceed_max_failures(self):
        import tempfile
        from unittest.mock import patch
        from tools.stress_runner import main
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = root / "cases.json"
            cases.write_text(json.dumps({"cases": [
                {"id": "c1", "prompt": "Hi", "replicates": 3, "should_trigger": True, "user_turns": []}
            ]}))
            output = root / "out"
            with patch("tools.stress_runner._execute", side_effect=RuntimeError("Provider 500 error")):
                with self.assertRaises((RuntimeError, ValueError)) as ctx:
                    main([
                        "--cases", str(cases),
                        "--output", str(output),
                        "--max-failures", "2",
                    ])
                self.assertIn("failure limit reached", str(ctx.exception).lower())




if __name__ == "__main__":
    unittest.main()
