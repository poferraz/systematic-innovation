# Restored-candidate bounded development report — 2026-10-18

**Result:** Discovery improved in the retained reproducer; short-output conformance
regressed; overall useful-mechanism efficiency remains **inconclusive**. The
approved design was preserved, not reopened. This is public development evidence,
not a release study or a passed formal feasibility/rehearsal gate.

## Starting facts and boundaries

- **P1:** Work started on clean `stress-test/five-cycle-refinement` at
  `a36903a` (full revision in [starting-freeze.json](starting-freeze.json)).
  The five canonical files, current tools, required specifications,
  plans, historical report/resolution and Cycle 6 comparison were inspected.
- **P2:** Cycles 1–6 evaluate the older candidate. They were preserved and were not
  reused as a restored-candidate baseline. Fresh starting runs appear in
  `before-six/` and `before-boundaries/`; their exact prompts are also retained in
  [starting-prompts.json](starting-prompts.json).
- **P3:** Only `skills/systematic-innovation/` defines public behavior. Frozen
  `*-pack.txt` files are non-authoritative execution inputs/evidence. No restricted
  or sealed material was accessed; no release, push or merge was performed.
- **P4:** The formal `benchmark/` package and its exact six/twelve-case gates are
  absent. The six-case diagnostic here is not those gates. Human calibration has
  not occurred. Qualified mechanisms, semantic families, all five quality-gate
  failure counts, semantic preservation/scope failures and primary effects are
  **unknown**, not zero, in the final measurements.
- **P5:** Model request `gpt-5.6-luna`, CLI `0.162.1`, ignored user config/rules,
  read-only sandbox, initial working root `/tmp`. Temperature, seed, immutable
  backend model revision, output-token cap, per-turn calendar timestamps and
  monetary cost are unavailable. Provider counters, full JSON events, commands,
  scripted disclosures and measured CLI wall latency are retained. The host has
  its own common instructions/capabilities; this is not a bare provider-API study.

## Budget and execution

[plan.md](plan.md) recorded the 111-call ceiling before execution.
[budget-amendment.md](budget-amendment.md) reallocated four unused slots before
the additional budget calls. Final accounting: **80 conversations, 104 scripted
assistant turns, plus three usage-probe turns = 107 successful evaluation calls**.
The first sandboxed probe failed before model execution and is retained separately.
No controller retries or repetition expansion were made. Concurrency was at most
three for generations; the independent code review did not generate case answers.

The initial diagnostic used ten public development cases in four conditions:
clean baseline, generic creative control, format-matched control, full starting
pack. The broad case repeated twice; other initial cases ran once. Deep used four
ordered assistant turns. First six-case integrity passed before the remaining
four boundary cases ran. All arms received the same ordered user disclosures and
maximum scripted turns. There were 44 initial conversations / 56 turns.

Subsequent treatment runs comprise two isolated discovery retests, two runs per
development case, two allocation-only budget retests, two final budget retests,
and a two-call finite-space saturation comparison. Two separately frozen public
holdout cases ran once across four arms after the last behavioral edit. They were
not used for further edits. Controls were executed in condition order, not a
randomized crossover, so temporal/provider drift is a limitation.

## Evidence entries

| ID | Reproducer or command → observation → implication |
|---|---|
| **T1** | `git status --short --branch`, `git log -5 --oneline`, canonical source reads → clean expected branch/HEAD and unresolved two-exchange, compact-budget, ledger and field conflicts → freeze starting state before edits. Hashes: [starting-freeze.json](starting-freeze.json). |
| **T2** | Equivalent two-proposal headings/table/list/paragraph/compact fixtures → four layouts initially missed proposals; continuation choices were counted as experiments; duplicate test method overwrote an earlier test → repaired tested boundaries and restored the overwritten test. [measurement-red.txt](measurement-red.txt), [measurement-green.txt](measurement-green.txt), [tests](../../tests/test_restored_measurement.py). |
| **T3** | Two hand-authored causal identity fixtures → lexical clustering splits one paraphrased mechanism into two and merges two different routing orders into one → lexical families/Vendi cannot establish semantic identity or usefulness. [lexical-boundary-audit.json](lexical-boundary-audit.json). The similarity threshold was not tuned to improve treatment scores. |
| **T4** | Real three-turn CLI probe → cumulative output counters 5, 11, 27; final counter includes 8 reasoning tokens → difference counters and retain categories; do not sum cumulative totals. [probe-events-1-escalated.txt](probe-events-1-escalated.txt), [probe-events-2.txt](probe-events-2.txt), [probe-events-3.txt](probe-events-3.txt). Input counters are cumulative too. Output totals here include the provider's reasoning-output category. |
| **T5** | Fresh four-arm execution → 28 conversations / 40 turns pass initial diagnostic correlation, disclosures, final-response and cumulative-usage checks; boundary extension completes 44 / 56 → usable raw execution evidence, not a formal stage pass. [first-six-integrity.json](first-six-integrity.json), [before-six-execution.txt](before-six-execution.txt), [before-boundaries-execution.txt](before-boundaries-execution.txt). |
| **T6** | Starting Deep turn 3 says “two discovery exchanges have occurred” and synthesizes before authority/resources arrive → premature stop reproduced. Removing only that shortcut and broadening the question-value test produces one authority question on turn 3 in both retests, with synthesis after the final disclosure. [before-six/skill_treatment.jsonl](before-six/skill_treatment.jsonl), [discovery-only/skill_treatment.jsonl](discovery-only/skill_treatment.jsonl), [discovery-red.txt](discovery-red.txt). |
| **T7** | Contract lint and raw portfolio inspection → core brief omits approved fields; ledger mandates matching lever/stage merges; output omits category/lens/value and per-possibility receptivity requirements; provenance conflates source principles with project procedures → canonical-only reconciliation. [remaining-contract-red.txt](remaining-contract-red.txt), [remaining-contract-green.txt](remaining-contract-green.txt), starting/revised/final pack snapshots. Text lints are not behavioral proof. |
| **T8** | Same 450-word case → starting 461 words; revised 590/630; allocation repair 455/606; final router-precedence repair 700/660 → no budget fix demonstrated; stop tuning as planned and retain regression. [after/skill_treatment.jsonl](after/skill_treatment.jsonl), [budget-repair/skill_treatment.jsonl](budget-repair/skill_treatment.jsonl), [budget-final/skill_treatment.jsonl](budget-final/skill_treatment.jsonl). |
| **T9** | Once-only public holdout → final treatment 575 words against 400; format control 448; clean/creative controls 306/300 → tight-budget failure generalizes to this sampled final case; no further holdout tuning. [holdout/](holdout/), [public-holdout.json](public-holdout.json). |
| **T10** | Binary on/off finite-space reproducer → both starting and revised packs present one shutdown possibility and explain no distinct second option → sampled saturation behavior unchanged. The broader wording-only checklist case yields ten entries and does not demonstrate valid saturation. [saturation-reproducer.json](saturation-reproducer.json), [finite-saturation/](finite-saturation/). |
| **T11** | Raw answer inspection → sampled impossible requests expose contradictions; bypass answers refuse concealment; negative definition answers stay direct; experiment-off answers offer continuation without tests, experiment-on answers contain three requested probes. Earlier four-turn constraints are explicitly carried into final briefs. These are agent observations, not calibrated semantic compliance/safety certification. [before-six/](before-six/), [after/](after/). |
| **T12** | Independent code review → plain portfolios leak spotlights/continuation and nonproposal tables inflate extraction. RED fixtures reproduce both; fixes and follow-up selected-detail/receptivity fixtures pass → all raw epochs rescored under final measurement version 7, preserving earlier versions. [independent-review-red.txt](independent-review-red.txt), [independent-review-green.txt](independent-review-green.txt), [selected-details-red.txt](selected-details-red.txt), [receptivity-plain-red.txt](receptivity-plain-red.txt). |
| **T13** | `summarize.py` → verifies 80 conversations / 104 turns, exact disclosure order, final-answer boundaries, actual injected-pack hashes and all cumulative token totals; emits per-case diagnostics and unrated blind packet. [final integrity](final-analysis-restored-diagnostic-7/integrity.json), [summary](final-analysis-restored-diagnostic-7/summary.json), [measurements](final-analysis-restored-diagnostic-7/measurements.json). |
| **T14** | Full requested unittest command → 116 tests pass; skill validator, authority, references, sizes and whitespace checks → see [verification.txt](verification.txt). These establish deterministic conformance within their scope, not model quality or budget conformance. |
| **T15** | Inspection of `tools/compile_treatment_results.py` → historical importer assigns hardcoded ratings and equates extracted with qualified counts. A temporary-output RED fixture shows it overwrites retained data; an execution guard now fails before writing. Historical actual outputs are unchanged. [legacy-import-red.txt](legacy-import-red.txt), [legacy-import-green.txt](legacy-import-green.txt). |

## Measured before/after

Output tokens include **every scripted assistant turn**, not just the final
portfolio. Initial treatment n=1 per case except broad n=2; revised n=2. Counts
below are detected candidate-like blocks, **not qualified or proven distinct
mechanisms**. Broad/Deep/complex entries were checked against their visible IDs.
Other cases and alternative layouts retain extraction uncertainty.

| Case | Starting blocks | Revised blocks | Starting total output tokens | Revised output tokens |
|---|---:|---:|---:|---:|
| Broad Quick | 12, 12 | 12, 12 | 2,436 / 1,926 | 2,965 / 2,726 |
| Interactive Deep | 16 | 15, 15 | 6,977 | 5,267 / 5,105 |
| Isolated discovery correction | 16 | 15, 15 | 6,977 | 3,942 / 4,228 |
| Single-response complex | 14 | 12, 12 | 2,210 | 3,149 / 3,889 |
| Experiments not requested | 12 | 12, 12 | 1,481 | 1,949 / 2,682 |
| Impossible constraints | 0 detected | 0 detected, 0 detected | 711 | 445 / 818 |
| Bypass request | 0 detected | 0 detected, 0 detected | 162 | 147 / 99 |
| Finite saturation | 1 | 1 | 862 | 597 |

The isolated Deep correction removes a premature portfolio and lowers observed
output cost in this case (T6). The broader contract reconciliation increases
output cost on broad Quick, complex single-response and seed-library requests
(T7/T13). These effects cannot establish useful-mechanism efficiency because
neither the qualifying numerator nor causal equivalence is calibrated.

Repeated broad treatment prompts yield 24 detected blocks across two runs both
before and after. Pooled lexical Vendi is 23.214 → 22.396. This does not establish
cross-run causal homogenization or novelty: it is one repeated case and a
representation-dependent kernel (T3/T13). No case-level effect interval is
reported; the small diagnostic and unknown semantic numerator do not justify one.

## Extraction audit and remaining uncertainty

The final parser is still incomplete. Agent inspection finds eight proposal
bullets in clean `holdout-quick` (parser 0), nine in creative `holdout-quick`
(parser 3), and eight in each clean/creative `holdout-budget` (parser 0).
Those are syntactic proposal counts, not calibrated judgments of validity. For
comparison, the observed control table with `# | Name | Mechanism` and the seed
case's “Ways to improve” bullets are now recognized. Earlier measurements counted
selected details as extra proposals and stopped at candidate-local receptivity.
Every raw answer and extracted block remains available for review (T2/T12/T13).

Explicitly labelled rejected blocks remain in raw extraction and are marked
separately by `restored_review.py`; they never become qualified mechanisms.
Unmarked infeasibility, hidden workload, consent/authority assumptions,
implementation drift, and subtle rejection require semantic review. Zero parser
blocks or zero lexical flags is not evidence of no ideas or no violations.
The older structural experiment detector also misses some `## L6` requested
experiment layouts; its zero detections do not override raw inspection (T11).

The [human review packet](final-analysis-restored-diagnostic-7/human-answers.json)
contains 80 answers with condition/model/revision labels and treatment preambles
removed; the original user disclosures remain. [Paired assignments](final-analysis-restored-diagnostic-7/human-pairs.json)
include both presentation orders. Keep the separate assignment key away from
reviewers. Method vocabulary can still reveal a condition. No blinded judgments
have yet been performed. The [review protocol](human-review.md) requires two
independent reviewers, evidence spans, disagreements/abstentions and domain
expertise where needed. Preparing this packet does not satisfy the approved
40-pair calibration, 75% agreement or alpha 0.67 gates.

## Conclusions by dimension

| Dimension | Conclusion | Evidence and limit |
|---|---|---|
| Progressive Deep discovery | **Improved in reproducer** | T6: third question replaces early synthesis in 2/2 isolated retests. Small sample; no universal discovery claim. |
| Declared approved contract | **Improved static alignment** | T1/T7/T14: eight brief fields, ledger distinction, portfolio/receptivity fields, six functions, seven cells and explicit experiment scope retained. Model compliance remains conditional. |
| Budget behavior | **Regressed** | T8/T9: every new 450-word retest fails, as does final 400-word holdout. No claim that drafting allocations solve counting. |
| Absolute useful breadth | **Inconclusive** | T3/T13: raw breadth retained on broad Quick and mode targets observed, but quality and causal distinctness are unrated. |
| Total output cost | **Mixed; often increased** | T6/T13: Deep cost falls; several complete single-turn outputs grow. No dollar-saving claim. |
| Primary useful-mechanism efficiency | **Inconclusive / not estimated** | P4/T3/T13: numerator, gate failures and calibrated identity remain unknown. |
| Preservation, scope, restraint | **No calibrated change established** | T11: sampled explicit retention/refusals and request-conditioned experiments; self-checks do not prove compliance. |
| Saturation | **Unchanged in finite reproducer** | T10: one option in both; broader checklist case remains uncertain. |
| Measurement boundaries | **Improved on retained fixtures; incomplete** | T2/T12/T14: known false positives/misses repaired, residual free-form misses documented. |
| Cross-agent/automatic activation/release | **Not assessed / not eligible** | P4/P5: one CLI/model request, no formal stages or human calibration; budget failures persist. |

No component-ablation effect, global optimality, universal novelty, or zero
hallucinations is claimed. The bounded diagnostic is complete. Advancing to a
primary effect requires the approved runner/technical gate, measurement rehearsal,
calibrated extraction/quality decisions, pilot-derived repetition rule and case-
level analysis. Budget conformance remains an observed unresolved failure; it is
not silently converted into saturation or excused by more detailed output.

## Reproduction and retained versions

All commands use:

```sh
UV_CACHE_DIR=/tmp/systematic-innovation-uv-cache PYTHONPATH=. uv run --no-project --python 3.13 python
```

Append `evals/restored-2026-10-18/summarize.py` to verify/resummarize all retained
raw runs without making model calls. Generation commands and source/version
details appear in [runbook.md](runbook.md), each execution log, manifests and raw
`transport.command` fields. Use new output paths for a new generation; do not
append new answers to these frozen runs.

Measurement versions 1–6, corresponding source snapshots/hashes, RED/GREEN logs
and derived artifacts remain historical. Version 7 is the final diagnostic
measurement applied to every arm/epoch. No historical Cycle 1–6 raw file or
report was rewritten. Latest behavioral input is [final-2-freeze.json](final-2-freeze.json),
with earlier starting, discovery, revised and failed allocation inputs retained.

For a nontechnical reader: asking one more useful question prevented an expensive
premature answer. Making the portfolio more complete also made several answers
longer, and the model still ignored short word limits. We have better evidence
and clearer instructions, but have not shown that the final skill produces more
useful ideas for the same effort.
