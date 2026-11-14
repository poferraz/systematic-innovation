# Systematic Innovation — Audit Remediation & Upgrade Plan

**Date:** 2026-10-29
**Status:** Draft — awaiting owner approval. No repository file will be modified until the owner explicitly confirms this plan.
**Source of record:** [`evals/audits/2026-10-29-deep-audit-report.md`](../../evals/audits/2026-10-29-deep-audit-report.md) — 32 findings: 1 Critical, 4 High, 14 Medium, 12 Low (one explicitly no-action).
**Contract Alignment:** This plan executes the approved specifications and remediates the audit findings. It does not amend or supersede any specification. The single specification change it proposes (task 1.5) is structured as an owner-approved amendment, to be executed only after explicit approval and recorded per the four-corrections precedent (CONTEXT §12 → spec incorporation pattern).

---

## 1. Requirements Restatement

The owner asked for an implementation plan covering the audit findings, their fixes, and the upgrades. Concretely:

1. **Remediate all 32 findings** from the 2026-10-29 deep audit, ordered so publication blockers are cleared before anything reaches a remote.
2. **Preserve what already works** — the verified strengths (restored skill conformance, append-only evidence, restricted-boundary integrity, green 116-test suite) must not regress; every change is RED/GREEN verified where testable.
3. **Respect the project's own governance** — owner decision gates for spec changes, corpus disposition, branch strategy, and status labels; CONTEXT.md §22 change control exercised for every decision; plans never amend specs without approval.
4. **Upgrade the engineering foundation** — CI, packaging manifest, documented validation commands, stronger authority enforcement, runner spend-controls, and security documentation.

## 2. Constraints & Operating Rules

- **Execution branch:** `stress-test/five-cycle-refinement` (current work; `main` == `origin/main` == `46ce0b6`; branch is 9 ahead / 0 behind → merge can be a fast-forward).
- **No push of any kind until Phase 0 completes.** The Critical finding (F-01) is currently contained *only* by the fact that `0ebddfe` sits on no remote branch — verified by `git branch -r --contains 0ebddfe` → empty. That window closes the moment anything is pushed.
- **Test-first (CONTEXT §16):** every fix with a testable contract gets its failing test written first (RED), then the fix (GREEN). Suite + validator must be green before each commit: `python3 -m unittest discover tests -v` and `python3 tools/validate_skill.py skills/systematic-innovation`.
- **Commit hygiene:** small, single-purpose commits matching the repo's message style (`fix:`, `test:`, `docs:`, `feat:`, `chore:`). Each phase lands as a reviewable sequence.
- **Skill-pack edits** touch the single behavioral authority and therefore require: regression assertions in `tests/test_skill_behavior.py` added first, spec grounding for every added clause, and validator green.
- **Historical evidence is never rewritten:** errata are appended to superseded banners; raw JSONL and frozen comparisons are untouched.

## 3. Owner Decision Gates

Nine decisions gate execution. Recommended options are marked; the owner may override any.

| # | Decision | Options (recommended first) | Gates |
|---|---|---|---|
| D1 | Corpus + book-text disposition | Relocate all 49 PDFs + book text to gitignored untracked `sources/` zone; keep only the v2 synthesis tracked | Per-file license triage and retain an open-access subset in-tree |
| D2 | v2 synthesis status | Relabel `:4` to research input; record in §19.8 that the v2 spec was never authored | Open a proper v2 spec/plan cycle now |
| D3 | Channel/budget precedence | Approve a behavioral-spec amendment grounding SKILL.md:29–40 (task 1.5) | Record both as pending refinements in §19.8, ungrounded |
| D4 | CI + packaging | Adopt minimal stdlib workflow + `pyproject.toml` now (tasks 2.2) | Record deferral with explicit trigger only |
| D5 | Branch strategy | Fast-forward merge to `main` after Phases 0–1, then push; retire the stress branch | Re-baseline `main` differently |
| D6 | `evals/audits/` disposition | Commit the audit prompt + report as historical evidence | Keep untracked / add to `.gitignore` |
| D7 | SKILL.md-only fallback | Instruct fallback users to paste all five files (README edit, least invasive) | Add a minimal layer skeleton to SKILL.md / add explicit degradation note |
| D8 | Security contact | GitHub private advisories only | Provide a routable email |
| D9 | Duplicate-collapse ratio | Annotate rubric/runbook with the implemented-method boundary | Add the computation to `score_eval_results.py` |

## 4. Implementation Phases

### Phase 0 — Publication blockers (nothing is pushed until this phase completes)

**0.1 Safety snapshot and state verification**
- Create a local backup ref of the current tip (stays local; deleted after Phase 4 verification or kept at owner's discretion).
- Re-verify the two load-bearing facts: `0ebddfe` is the branch **tip** (making history correction a simple commit replacement, not a deep rewrite) and `git branch -r --contains 0ebddfe` → empty.
- Command set recorded in the task commit message for reproducibility.

**0.2 History-safe removal of the copyrighted book text (F-01, Critical)** — *Decision D1*
- `git reset --soft HEAD~1` (tip commit only), then remove `docs/references/stimulating-innovation-tudor-rickards.md` from index and working tree; relocate the file to the new gitignored `sources/` zone locally (out of Git, retained for owner reference).
- Apply D1 to the 49 PDFs: default = remove `docs/research/**.pdf`, `docs/references/*.pdf` from index, relocate to `sources/`.
- Re-commit the retained content (`docs/research/2026-10-18-v2-brainstorming-synthesis.md` and any D1-approved survivors) as a clean curated commit.
- Verify: `git log --all --oneline -- docs/references/stimulating-innovation-tudor-rickards.md` → empty; `git grep -l "Total Extracted Spreads"` → empty; restricted-pattern sweep still empty; suite green. (CONTEXT.md cites no `0ebddfe` hash — verified in audit F-08 — so no hash-reference repairs are needed.)

**0.3 Corpus boundary record (F-04, remainder)**
- Add `sources/` to `.gitignore`.
- Deduplicate the byte-identical PDF pair within `sources/` (local only).
- Add `docs/research/README.md`: research input only; non-authoritative; excluded from distributions; redistribution-review-required (spec §8.2).
- Record the D1 disposition in CONTEXT §19.8 (task 1.1 covers the entry; this task supplies its corpus section).

**0.4 Branding claim regression test (F-02, test-first)**
- New `tests/test_branding_claims.py` (stdlib): assert `tools/build_branding.py` contains none of the forbidden strings — "+162%", "8.2x", "Pilot Lift", "Learning Probes", "≤ 4 Questions", "4 surgical questions", "5 structural dimensions" — and that `README.md` embeds no withdrawn-claim text. **RED** against the current tree.

**0.5 Branding generator fix (F-02, GREEN)**
- Edit `tools/build_branding.py`: strip withdrawn numbers (:197, :356–:375, :674) and pre-restoration behaviors (:186, :387, :522, :527, :532, :657), replacing them with design-descriptor copy mirroring README:64's disclaimer language; align depicted protocols with the restored skill (one question at a time, ≤7; user-requested probes only).
- Suite green including the new test.

**0.6 Asset regeneration (F-02, environment-gated)**
- Prerequisite: one-time dev environment — `uv venv .venv && uv pip install playwright && .venv/bin/python -m playwright install chromium` (`.venv/` already gitignored); then run the generator and commit the four regenerated PNGs.
- Fallback if the owner declines the browser dependency: commit hand-adjusted static claim-free replacements.
- Verify PNG dimensions still match the generator's render signature.

**0.7 Public claim-surface corrections (F-03)**
- `README.md`: reword :47/:76/:127 to the resolved restoration state (pointing to `contract-findings.md:19–22`); relabel the evidence badge (:12–13) to name the candidate revision; add `evals/restored-2026-10-18/report.md` beside the five-cycle link at :72.
- `evals/stress/five-cycle-report.md`: append a dated "Latest status" addendum (cycles evaluate the pre-restoration candidate; see the restored report). No history rewrite.
- `evals/pilot/baseline-analysis.md`: add the same superseded banner its siblings carry.
- Verify: `git show origin/main:README.md` greps are superseded by the new state after merge (Phase 4.3 re-check).

**Phase 0 exit criteria:** F-01/F-02/F-03/F-04 remediated; suite + validator green; book text absent from all history; nothing pushed yet.

### Phase 1 — Governance and decision records

**1.1 CONTEXT §19.8 entry (F-08; also closes the F-32 no-action record)**
- One dated section recording: the corpus disposition (D1), the corrected tip commit, the v2 synthesis status (D2), the audit report pointer, the merge decision (D5), and a note that Hungarian matching (F-32) is tracked as a formal-benchmark acceptance criterion.

**1.2 Merge/decision plan record (F-05)**
- Record the D5 strategy in §19.8; specify merge order (after Phases 0–1), fast-forward expectation, and branch retirement.

**1.3 v2 synthesis relabel (F-07)** — *Decision D2*
- Default: edit `docs/research/2026-10-18-v2-brainstorming-synthesis.md:4` to "Status: Research input — unexecuted synthesis; no v2 specification exists"; qualify or remove the +22%/+28%/+35% figures (mark them unexecuted projections).

**1.4 contract-findings header fix (F-20)**
- Rewrite `contract-findings.md:3` to past tense pointing at its own resolution section.

**1.5 Spec amendment for execution-channel and user-budget precedence (F-06)** — *Decision D3, hard gate*
- Draft the amendment text (mirroring SKILL.md:29–40): a new §6.4 "Execution-channel precedence" and §12.x "User-requested output budgets"; present to the owner.
- Only on approval: incorporate into the behavioral spec, add the decision record to CONTEXT §19, and update the authority-sync tests. On the alternative (pending-refinement record), write that status into §19.8 instead and leave the spec untouched.

**1.6 Skill conformance completions (F-09, F-10, F-21, F-22, F-23)** — test-first
- RED: add regression assertions to `tests/test_skill_behavior.py` for five spec-grounded clauses the skill currently lacks: research-when-available capability note (spec §15), preservation-first/no-change conclusion (spec:265), high-stakes exploratory + verification labeling (spec:326), Quick-mode single critical question allowance (spec:122), and the two missing operator cues (spec §10: morphological recombination, subtraction).
- GREEN: minimal skill-pack edits (SKILL.md / output-contract.md) implementing exactly those clauses; validator green.
- Note: these execute *existing* approved spec text — no amendment needed.

**1.7 AGENTS.md orientation update**
- Reference this plan from the applicable-plan list (and the §19.8 pointer), so a fresh agent discovers the remediation context.

**Phase 1 exit criteria:** all decision records in CONTEXT; spec amendment resolved (either path); skill closes the five omission gaps with green tests.

### Phase 2 — Engineering hardening & upgrades

**2.1 AGENTS.md validation commands (F-13)**
- Add a "Validation commands" block: `python3 -m unittest discover tests -v`; `python3 tools/validate_skill.py skills/systematic-innovation`; state pytest is not used.

**2.2 CI + packaging manifest (F-16)** — *Decision D4*
- `pyproject.toml`: name, version, requires-python; runtime declared stdlib-only; `[dependency-groups] dev = ["playwright"]` (the only third-party dev dep, F-02's regeneration requirement made explicit).
- `.github/workflows/ci.yml`: on push/PR → setup Python → `python3 -m unittest discover -s tests -v` → `python3 tools/validate_skill.py skills/systematic-innovation`. ~10 lines, stdlib-only.
- If deferred: record the trigger in one line in §19.8 per AR-11.

**2.3 Authority enforcement upgrade (F-12, F-25)**
- Extend `tools/repository/authority.py`: content-signature sweep (candidate counts, seven-question rule, Reasoning Cell names, layer names) over an explicit allowlist (specs, plans, CONTEXT §6, tests, measurement tools, frozen evals, branding generator) flagging unlisted files that restate behavioral commitments; broaden the supersession phrase list (`supersede|override|takes precedence|amend` near "specification"); add a CLI (`python3 -m tools.repository.authority`, exit 1 on findings).
- `tools/validate_skill.py`: remove the evidence.md provider-scan exemption; broaden PROVIDER_RE (gemini/gpt/openai/anthropic/copilot).
- Test-first: RED tests for each new enforcement (a fixture file restating counts under a non-canonical name must fail the sweep), then GREEN.

**2.4 Runner spend/safety controls (F-14)**
- `tools/stress_runner.py`: add `--max-cost` cap (abort before exceeding), model allowlist (default deny-unknown), bounded retries with failure threshold, and credential redaction of raw CLI events before storage.
- Test-first: unit tests for cap-abort, allowlist rejection, redaction.

**2.5 Tool defect fixes (F-28)**
- `compile_treatment_results.py:15` and `stress_runner.py:257`: replace hardcoded absolute paths with CLI-required or env-derived values (test-first).
- `score_eval_results.py:178–179`: refuse an existing output path (mirror `restored_review.py:90–91`); test-first.

**2.6 SECURITY.md trust zones (F-15)** — *Decision D8*
- Add the spec-required trust-zone section: skill zone (pure Markdown, zero deps — verified), repo tooling zone (executable Python; playwright dev-only), restricted pack zone (never in Git/CI/dist).
- Replace `security@systematic-innovation.local` with GitHub-advisories-only wording (or a real address if the owner provides one).

**2.7 Pilot evidence errata (F-18)**
- Append one erratum block to the superseded banners of `evals/pilot/baseline-analysis.md`, `treatment-analysis.md`, `candidate-report.md`: (a) treatment Deep records carry 2 of the required 3 turns (final scripted disclosure never delivered); (b) stored efficiency numerators differ by arm (distinct families vs. raw candidates) and are not cross-arm comparable — the arithmetic mechanism behind the withdrawn headline; (c) `turn_1_question_count` fields are hardcoded importer constants, not measurements. No raw-data changes.

**2.8 Rubric/runbook method annotations (F-19)** — *Decision D9*
- Default: annotate `evals/pilot/rubric.md` §3 and `runbook.md` §2 with the implemented-method boundary (lexical cosine clustering; semantic equivalence awaits calibrated review; collapse ratio computed only in historical records).
- Alternative: add the two-line collapse-ratio computation to `score_eval_results.py` with a test.

**2.9 SKILL.md-only fallback fix (F-11)** — *Decision D7*
- Default: `README.md:117–118` instructs fallback users to paste all five files.
- Alternatives: minimal layer skeleton in SKILL.md (skill edit + behavior tests) or an explicit degradation note.

**Phase 2 exit criteria:** CI green locally (or deferral recorded); authority sweep passes on the fixed tree; runner guards tested; docs honest.

### Phase 3 — Hygiene

- **3.1 (F-17)** Correct the Lorsch locator in `evidence.md:21` to Ch. 4, pp. ~70–77 (or drop the chapter citation).
- **3.2 (F-24)** Add a drift assertion to `tests/test_stress_runner.py`: the control-prompt counts must equal the canonical pack's targets (parse `SKILL.md`).
- **3.3 (F-26)** Add a contract-sync lint test (CONTEXT §6 numbers vs. SKILL.md strings) or stamp CONTEXT §6 "describes state as of 2026-10-17; canonical skill is authoritative."
- **3.4 (F-27)** Apply D6 to `evals/audits/` (default: commit the prompt + report as historical evidence).
- **3.5 (F-29)** README wording: "Transforms…" → design-intent verb; scope "zero dependencies" to the skill package; note the format-matched control ran (uncalibrated).
- **3.6 (F-30)** Optional one-line caveats on the superseded pilot docs' banners (trigger-metric scope; problem-owner paraphrase).
- **3.7 (F-31)** Add the calibration operational rule to `human-review.md`: before the 40-pair calibration, regenerate the packet with a key held outside Git or restrict reviewers to exported files.

### Phase 4 — Verification, merge, and closure

- **4.1 Full verification battery:** `python3 -m unittest discover tests -v` (all green, now >116); validator; authority CLI sweep; restricted-pattern and book-title history greps empty; `git log --all` clean of removed paths.
- **4.2 Merge and push (D5):** fast-forward `main` to the branch tip; push `main`; delete the local stress branch and backup ref after verification. This is the first push in the project's remediation — only after 4.1 passes.
- **4.3 Public-surface re-check:** on the pushed `origin/main`, re-run the audit's claim greps (badge, "+162%", "8.2x", "Current results") — expect clean; confirm the restored report is linked.
- **4.4 Closure:** §19.8 gains the completion note; optionally commission a follow-up mini-audit of the invariant matrix (the same protocol, Domains A–D only) to certify the remediation.

## 5. Dependencies

- 0.2 → 0.3 → 1.1 (disposition record follows the actual disposition).
- 0.4 → 0.5 → 0.6 (test-first generator fix, then regeneration).
- 1.5 (D3) → 1.6 ordering: the skill completions are independent of the amendment and may proceed in parallel; the amendment gates nothing else.
- 2.3's allowlist depends on 0.2/0.3 having removed the corpus (so the sweep list is final).
- 4.2 (push) depends on all of Phase 0 + 1.1/1.2 being complete; Phases 2–3 may land before or after the merge at the owner's preference (recommended: complete 2.x's CI + commands first so the merge is verified by CI).
- Asset regeneration (0.6) depends on the one-time playwright environment (network install — the only network step in this plan, owner-approved).

## 6. Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| History correction goes wrong | HIGH | `0ebddfe` is the unpushed tip → simple `reset --soft` + recommit, no filter-repo; local backup ref first; verify no remote branch contains the old hash before and after |
| Asset regeneration environment (playwright/chromium download) | MEDIUM | One-time `uv` venv, already gitignored; fallback to static claim-free replacements |
| Spec amendment governance | MEDIUM | Hard gate D3: draft → owner approval → incorporation, mirroring the four-corrections precedent; plan itself amends nothing |
| Skill edits regress the canonical behavior | MEDIUM | Test-first per clause; validator + full suite green before each skill commit; only spec-grounded text added |
| Fast-forward merge assumption breaks (new commits land on main) | LOW | Re-verify 0-behind before merge; fall back to a regular merge commit |
| Hash references invalidated by the tip replacement | LOW | Verified in audit: CONTEXT cites no `0ebddfe` hash; §19.8 records the new hash |
| Calibration sequencing (F-31 rule applied later) | LOW | Rule recorded now in human-review.md; enforced when calibration is scheduled |

## 7. Complexity Estimate

- Phase 0: 2–4 hours (careful git surgery + generator edits + regeneration)
- Phase 1: 2–3 hours execution + owner decision latency (D1–D3, D5)
- Phase 2: 6–10 hours (tooling + tests — the bulk of the engineering upgrades)
- Phase 3: 1–2 hours
- Phase 4: 1 hour + optional follow-up mini-audit
- **Total: ~12–20 focused hours**, deliverable in 3–5 sessions.

## 8. Finding → Task Coverage Matrix

| Finding | Task(s) | Finding | Task(s) |
|---|---|---|---|
| F-01 Critical | 0.1, 0.2 | F-17 | 3.1 |
| F-02 High | 0.4, 0.5, 0.6 | F-18 | 2.7 |
| F-03 High | 0.7 | F-19 | 2.8 |
| F-04 High | 0.2, 0.3 | F-20 | 1.4 |
| F-05 High | 1.2, 4.2 | F-21 | 1.6 |
| F-06 Medium | 1.5 (D3) | F-22 | 1.6 |
| F-07 | 1.3 (D2) | F-23 | 1.6 |
| F-08 | 1.1 | F-24 | 3.2 |
| F-09 | 1.6 | F-25 | 2.3 |
| F-10 | 1.6 | F-26 | 3.3 |
| F-11 | 2.9 (D7) | F-27 | 3.4 (D6) |
| F-12 | 2.3 | F-28 | 2.5 |
| F-13 | 2.1 | F-29 | 3.5 |
| F-14 | 2.4 | F-30 | 3.6 |
| F-15 | 2.6 (D8) | F-31 | 3.7 |
| F-16 | 2.2 (D4) | F-32 | 1.1 (record only — no action) |

All 32 findings are covered; 9 decision gates structure the owner's authority over every judgment call.

---

**WAITING FOR CONFIRMATION.** Nothing above will be executed until you confirm. To proceed:

- **"proceed"** — execute Phase 0 immediately using the recommended options (D1–D9 defaults), pausing at each decision gate only where you want a different choice;
- **"proceed with: D3=…, D6=…"** — execute with your explicit gate choices;
- **"modify: …"** — change any task, phase order, or default first.