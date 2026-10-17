import unittest

from tools.pilot_metrics import (
    assess_falsifiability,
    cluster_mechanisms,
    compute_vendi_score,
    count_discovery_questions,
    count_word_budget_compliance,
    detect_preservation_violations,
    extract_candidate_mechanisms,
)


COMPACT_PORTFOLIO = """L1: Tension: missed visits; Preserve: continuity, no new staff; Assume transport barriers.
P1: Confirm by exception | Intervention point: booking | Causal chain: barrier is named, slot is adjusted, attendance rises | Causal lever: temporal inversion | Preserve check: all L1 invariants
P2: Travel relay | Intervention point: pre-visit | Causal chain: partner relays logistics, patient keeps clinician, missed visit falls | Causal lever: role separation | Preserve check: all L1 invariants
P3: Recovery queue | Intervention point: post-no-show | Causal chain: cancellation releases slot, waitlist fills it, capacity recovers | Causal lever: pull-based capacity | Preserve check: all L1 invariants
P4: Barrier codes | Intervention point: scheduling | Causal chain: code triggers accommodation, travel falls, attendance rises | Causal lever: information schema | Preserve check: all L1 invariants
L4: P1 is mission-oriented; P2 is negotiative.
L5: Fastest P1; deepest P2.
L6: Probe 1: test 20 bookings for 2 weeks; revise if fewer than 10 confirm; revert to current workflow.
"""


class StructuredMechanismTests(unittest.TestCase):
    def test_renaming_a_lever_does_not_create_a_new_mechanism(self) -> None:
        shared = {"intervention_point": "intake", "causal_chain": "route unusual requests to specialist review"}
        self.assertEqual(len(cluster_mechanisms([
            {**shared, "causal_lever": "exception routing"},
            {**shared, "causal_lever": "special-case triage"},
        ])), 1)

    def test_shared_lever_does_not_override_different_structural_operations(self) -> None:
        self.assertEqual(len(cluster_mechanisms([
            {"causal_lever": "temporal inversion", "intervention_point": "supplier procurement",
             "causal_chain": "preorder raw materials to aggregate demand before production"},
            {"causal_lever": "temporal inversion", "intervention_point": "customer settlement",
             "causal_chain": "defer payment until independent verification of delivery"},
        ])), 2)

    def test_vendi_duplicate_blocks_have_known_effective_count(self) -> None:
        # Two orthogonal equal-size blocks have exactly two nonzero eigenvalues of 1/2.
        texts = ["alpha"] * 6 + ["omega"] * 6
        for order in (0.5, 1.0, 2.0):
            self.assertAlmostEqual(compute_vendi_score(texts, k=order), 2.0, places=3)

    def test_cross_run_duplicate_pool_stays_one_effective_mechanism(self) -> None:
        for order in (0.5, 1.0, 2.0):
            self.assertAlmostEqual(compute_vendi_score(["alpha"] * 60, k=order), 1.0, places=3)

    def test_extracts_compact_candidates_and_structured_fields(self) -> None:
        candidates = extract_candidate_mechanisms(COMPACT_PORTFOLIO)
        self.assertEqual(len(candidates), 4)
        self.assertEqual(candidates[0]["intervention_point"], "booking")
        self.assertIn("barrier is named", candidates[0]["causal_chain"])
        self.assertEqual(candidates[0]["causal_lever"], "temporal inversion")
        self.assertEqual(candidates[0]["preserve_check"], "all L1 invariants")

    def test_contrasting_lever_mentions_do_not_collapse(self) -> None:
        one = (
            "P1: Exception triage | Intervention point: intake | "
            "Causal chain: unusual cases are routed earlier | "
            "Causal lever: queue priority | Preserve check: all invariants. "
            "Unlike an incentive split, this does not change commissions."
        )
        two = (
            "P2: Team credit | Intervention point: settlement | "
            "Causal chain: shared credit rewards handoffs | "
            "Causal lever: incentive split | Preserve check: all invariants. "
            "Unlike queue priority, this changes settlement."
        )
        self.assertEqual(len(cluster_mechanisms([one, two])), 2)

    def test_explicit_causal_levers_keep_technical_tradeoff_mechanisms_distinct(self) -> None:
        levers = [
            "passive heat-path relocation",
            "fouling-tolerant geometry",
            "pressure-drop subtraction",
            "phase-change buffering",
            "bounded fan control",
            "workload shaping",
        ]
        operations = [
            ("enclosure wall", "conduct heat outward through a sealed thermal bridge"),
            ("cooling surface", "wide fin spacing prevents dust buildup"),
            ("air duct", "remove obstructions to reduce aerodynamic resistance"),
            ("thermal reservoir", "absorb transient heat through latent storage"),
            ("fan controller", "adjust speed within an acoustic ceiling"),
            ("work scheduler", "shift compute peaks away from hot ambient periods"),
        ]
        candidates = [
            f"P{i + 1}: Mechanism {i + 1} | Intervention point: {point} | "
            f"Causal chain: {chain} | Causal lever: {lever} | Preserve check: all invariants"
            for i, (lever, (point, chain)) in enumerate(zip(levers, operations))
        ]
        self.assertEqual(len(cluster_mechanisms(candidates)), 6)

    def test_vendi_score_supports_requested_kernel_orders(self) -> None:
        texts = [
            "intake nurses route unusual cases to specialist review",
            "intake nurses route unusual cases to specialist review",
            "warehouse staff bundle deliveries into weekly shipment windows",
            "community partners relay appointment logistics with consent",
        ]
        scores = {k: compute_vendi_score(texts, k=k) for k in (0.5, 1.0, 2.0)}
        self.assertGreater(scores[1.0], 1.0)
        self.assertLess(scores[1.0], 4.0)
        self.assertGreaterEqual(scores[0.5], scores[1.0])
        self.assertLess(scores[2.0], scores[1.0])


class PreservationAndFalsifiabilityTests(unittest.TestCase):
    def test_removing_waste_does_not_break_an_asset_preserved_in_next_clause(self):
        self.assertEqual(detect_preservation_violations([
            {"preserve_check": "Remove duplicate paperwork while safety reviews remain intact."}
        ], ["safety reviews"]), [])

    def test_sample_threshold_is_not_an_outcome_disconfirmation_rule(self):
        self.assertEqual(assess_falsifiability(
            "L6: Probe 1: Interview at least 20 participants for 2 weeks; revise questions as needed."
        )["rate"], 0.0)

    def test_multiline_probe_fields_belong_to_one_probe(self) -> None:
        response = """## Layer 6: Learning probes
1. **Confirmation probe**
   - Metric: completed confirmations.
   - Threshold: reject if fewer than 10 confirm.
   - Bound: 20 bookings.
   - Horizon: two weeks.
   - Fallback: revert to current workflow.
"""
        self.assertEqual(assess_falsifiability(response), {
            "probe_count": 1, "falsifiable_count": 1, "rate": 1.0})

    def test_blanket_self_check_cannot_hide_an_explicit_constraint_break(self) -> None:
        candidates = [{"text": "Remove commission and replace it with salary.",
                       "preserve_check": "all L1 invariants"}]
        self.assertIn("breaks_preserved_asset", {
            issue["reason"] for issue in detect_preservation_violations(candidates, ["commission"])
        })

    def test_negated_bypass_is_not_a_preservation_violation(self) -> None:
        self.assertEqual(detect_preservation_violations(
            [{"preserve_check": "Do not bypass safety reviews; commission remains."}],
            ["commission", "safety reviews"]), [])

    def test_falsifiability_needs_both_sample_and_horizon_and_numeric_rule(self) -> None:
        for probe in (
            "Test 20 bookings; revise if fewer than 10 confirm; revert to current workflow.",
            "For 2 weeks, stop if fewer than 10 confirm; revert to current workflow.",
            "Test 20 bookings for 2 weeks; stop if above expectations; revert to current workflow.",
        ):
            with self.subTest(probe=probe):
                self.assertEqual(assess_falsifiability("## Layer 6\n- " + probe)["rate"], 0.0)

    def test_missing_preservation_check_is_a_violation(self) -> None:
        candidates = [
            {"text": "P1: Add a new nurse task | Causal chain: more work", "preserve_check": ""},
            {"text": "P2: Relay logistics | Causal chain: partner support", "preserve_check": "all L1 invariants"},
        ]
        violations = detect_preservation_violations(candidates, ["no new nurse tasks", "continuity"])
        self.assertEqual(violations, [{"candidate": 1, "reason": "missing_preserve_check"}])

    def test_falsifiability_rejects_vague_survey_and_accepts_bounded_disconfirmation(self) -> None:
        vague = "## Layer 6\n- Run a pilot survey to learn whether patients like the new system."
        rigorous = (
            "## Layer 6\n- Test 20 eligible bookings for 2 weeks; revise the mechanism "
            "if fewer than 10 confirm, then revert to the current workflow."
        )
        self.assertEqual(assess_falsifiability(vague), {
            "probe_count": 1,
            "falsifiable_count": 0,
            "rate": 0.0,
        })
        self.assertEqual(assess_falsifiability(rigorous), {
            "probe_count": 1,
            "falsifiable_count": 1,
            "rate": 1.0,
        })


class RoutingAndBudgetTests(unittest.TestCase):
    def test_discovery_questions_are_counted_only_before_portfolio(self) -> None:
        response = (
            "What preservation boundary must remain?\n"
            "Which authority can change scheduling?\n\n"
            "P1: Research mechanism | Causal chain: Does this improve care? yes | Causal lever: triage\n"
        )
        self.assertEqual(count_discovery_questions(response), 2)

    def test_word_budget_compliance_uses_visible_words(self) -> None:
        self.assertTrue(count_word_budget_compliance("one two three", 3))
        self.assertFalse(count_word_budget_compliance("one two three four", 3))


if __name__ == "__main__":
    unittest.main()


class EvaluationRecordScoringTests(unittest.TestCase):
    def test_score_record_exposes_required_cycle_metrics(self) -> None:
        from tools.score_eval_results import score_record

        record = {
            "case_id": "token-ceiling-portfolio",
            "final_response": COMPACT_PORTFOLIO,
            "total_assistant_output_tokens": 418,
            "interaction_mode": "single-turn",
        }
        case = {
            "id": "token-ceiling-portfolio",
            "preserve": ["continuity", "no new staff"],
            "word_limit": 350,
        }
        result = score_record(record, case)
        self.assertEqual(result["candidate_count"], 4)
        self.assertEqual(result["distinct_mechanism_clusters"], 4)
        self.assertEqual(result["lever_coverage"], 1.0)
        self.assertEqual(result["preservation_violation_count"], 0)
        self.assertEqual(result["falsifiability_rate"], 1.0)
        self.assertTrue(result["word_budget_compliant"])
        self.assertEqual(result["discovery_question_count"], 0)
        self.assertEqual(sorted(result["vendi_scores"]), ["0.5", "1.0", "2.0"])


class LegacyMechanismFormatTests(unittest.TestCase):
    def test_parses_pilot_ledger_and_legacy_candidate_labels(self) -> None:
        legacy = """### Layer 2: Mechanism Ledger
| ID | Causal Lever Type | Stage |
|---|---|---|
| **P1** | **Incentive Unbundling** | Close |

### Layer 3: Possibility Portfolio
#### Possibility 1: Assist Pool
* **Causal Mechanism Chain:** store-funded spiff rewards assistance without docking commission.
* **Preservation & Constraint Check:** primary commission and customer ownership remain intact.
* **Key Assumption & Failure Mode:** assistance must convert stalled sales.
"""
        candidates = extract_candidate_mechanisms(legacy)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["causal_lever"], "incentive unbundling")
        self.assertIn("store-funded spiff", candidates[0]["causal_chain"])
        self.assertIn("customer ownership remain intact", candidates[0]["preserve_check"])

class ConversationBurdenTests(unittest.TestCase):
    def test_all_assistant_discovery_turns_count(self):
        from tools.score_eval_results import score_record
        record = {"turns": [{"assistant": "What constraints must remain?"},
                            {"assistant": "P1: Complete portfolio"}],
                  "final_response": "P1: Complete portfolio"}
        self.assertEqual(score_record(record)["discovery_question_count"], 1)

class LexicalScreenBoundaryTests(unittest.TestCase):
    def test_protection_clause_is_not_the_target_of_waste_reduction(self):
        for text in ("Reduce waiting time without bypassing safety reviews.",
                     "Remove duplicate paperwork and retain safety reviews."):
            self.assertEqual(detect_preservation_violations([{"preserve_check": text}], ["safety reviews"]), [])

    def test_participant_availability_is_not_an_outcome_threshold(self):
        self.assertEqual(assess_falsifiability(
            "L6: Probe 1: Interview 20 participants for 2 weeks; revise questions if at least 20 participants are available."
        )["rate"], 0.0)

class CumulativeUsageRescoringTests(unittest.TestCase):
    def test_explicit_cumulative_mode_retains_and_corrects_original_total(self):
        from tools.score_eval_results import score_record
        record = {"token_accounting": "provider", "total_assistant_output_tokens": 30,
                  "turns": [{"assistant_tokens": 5}, {"assistant_tokens": 10}, {"assistant_tokens": 15}]}
        scored = score_record(record, provider_usage_cumulative=True)
        self.assertEqual(scored["total_assistant_output_tokens"], 15)
        self.assertEqual(scored["original_reported_total_assistant_output_tokens"], 30)

class ObservedCompactFormatTests(unittest.TestCase):
    def test_em_dash_and_inline_fields_are_extracted(self):
        response = '''L1: Preserve continuity.
P1 — Timing | Intervention: booking | Causal chain: adapt arrival windows | Causal lever: temporal inversion | Preserve check: continuity remains.
P2 Recovery | Intervention: follow-up. Causal chain: rebook missed visits. Causal lever: feedback. Preserve check: no new staff.
L4: P1 is locally actionable.
'''
        rows = extract_candidate_mechanisms(response)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['causal_chain'], 'adapt arrival windows')
        self.assertEqual(rows[1]['intervention_point'], 'follow-up')
        self.assertEqual(rows[1]['causal_lever'], 'feedback')

class ModalNegationTests(unittest.TestCase):
    def test_cannot_remove_is_a_prohibition_not_a_proposal(self):
        self.assertEqual(detect_preservation_violations([
            {"preserve_check": "Relay rules cannot remove rural coverage."}
        ], ["rural coverage"]), [])
