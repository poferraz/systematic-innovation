# Deep Audit & Project Review — systematic-innovation (2026-10-29)

**Commissioned via:** `evals/audits/2026-10-29-deep-audit-and-project-review-prompt.md`
**Target:** working tree of `stress-test/five-cycle-refinement` (9 ahead / 0 behind `main`; `main` == `origin/main` == `46ce0b6`)
**Method:** five independent domain auditors (A+F, B, C+D, E+H, G) executing the protocol in parallel, with orchestrator consolidation and first-hand re-verification of every Critical and High claim before it entered this report.

---

## 1. Executive Summary

**Verdict:** the repository's *internal* discipline is real and unusual — and its *public surfaces and Git history* have not caught up with it.

The verified strengths are substantial: the restored skill conforms to every owner-restored contract boundary (13 element-level conformances verified against the approved specification, each with regression tests); no competing behavioral authority exists anywhere in the tree; restricted/sealed material has never been tracked or committed in any commit; the evaluation laboratory's raw data reconciles with its reports almost perfectly across all five stress cycles, the Cycle-6 rescore, and the restored-candidate diagnostic; and the 116-test suite is green on the standard library alone.

But the audit found **1 Critical and 4 High findings**, concentrated in one failure pattern: decisions recorded inside the repository did not propagate to public surfaces and history. The complete copyrighted text of Rickards's 1985 book (463,748 bytes, 118 spreads) was committed one day *after* the project recorded its "do not reproduce copyrighted book text" boundary — it is confirmed absent from every remote branch, so a remediation window exists. The withdrawn +162% headline remains live on `origin/main` — badge, results table, and three README-embedded images plus their generator — on a branch that contains no withdrawal text at all. The README's evidence badge points at prior-candidate cycles labeled "Current results" while the restored candidate's study is unlinked from every public document. And 47 third-party PDFs (33 MB) are committed with no license record.

Fourteen Medium findings cover spec-less skill additions, a self-labeled "Approved" v2 synthesis with untraceable numbers, the undocumented arithmetic mechanism behind the withdrawn headline, filename-only authority enforcement, and missing CI/manifest/documented commands. None of the Critical/High items require redesign — they require propagation: history correction before push, asset regeneration, a README correction commit, corpus disposition, and a recorded merge plan.

## 2. Premises

### 2.1 Method

- Five domain auditors executed the protocol's Section 2 domains independently. Each read the protocol and authority chain first, worked numbered evidence traces, and returned a findings ledger, strengths, gaps, and premises.
- The orchestrator (this report's author of record) re-verified **every Critical and High claim first-hand** before consolidation, plus a sample of Medium/Low claims (all verified). Verification commands and outcomes are in §2.3.
- Per the protocol's independence rule, no auditor read the prior audit reports (`evals/audits/2026-10-18-*`, `muse-loop/`); a few lines surfaced incidentally in greps and were not used as evidence.
- **Method error disclosed:** two mid-audit steering messages were mis-addressed (E+H environment facts went to the G auditor; vice versa). Effect was nil — the E+H auditor independently found the stdlib `unittest` invocation in the plans and ran the full suite anyway; the G auditor's launch prompt was self-contained. Both corrections are reflected in the final findings.
- **Protocol adaptation disclosed:** the protocol's "deliver as final response; write nothing" rule is adapted in one respect — the consolidated report is saved as this file, matching the repository's established convention for audit artifacts under `evals/audits/`. No tracked repository file was modified: `git status` shows only untracked `evals/audits/` and gitignored caches (`__pycache__/`).

### 2.2 Environment

CPython 3.14.2 (framework build; Homebrew 3.14.7 and system 3.9.6 also present, none with pytest). pytest not installed on any interpreter; no repo venv; `uv` present but unused (no-install discipline). No network access. macOS. Read-only discipline maintained by all auditors except gitignored interpreter caches.

### 2.3 Orchestrator first-hand verification (commands, exit codes)

- `python3 -m pytest --version` → exit 1 (absent). `python3 -m unittest discover tests` → **116 tests OK, exit 0** (run twice; also 5-module subset → 31 OK).
- `python3 tools/validate_skill.py skills/systematic-innovation` → OK, exit 0 (auditor-run; corroborated).
- `git ls-files | grep -Ei 'restricted|sealed|validation\.yaml|benchmark/private|^dist/'` → **NONE tracked**; `git log --all --oneline -- <restricted pathspecs>` → **0 commits**; `git check-ignore -v systematic-innovation-session.bundle` → `.gitignore:18`.
- `git branch -r --contains 0ebddfe` → **empty** (book-text commit not on any remote branch); `git rev-parse main origin/main` → both `46ce0b6`.
- `git show origin/main:README.md` → +162% badge (line 12), "+162% causal information density" table row (line 93), "8.2x increase" (line 95); withdrawal text **absent** on that branch (added later in `4e93a98`).
- Book-text head read: self-described "High-Quality Full Text Extracted from Screen Recording", "Total Extracted Spreads: 118 (covering Preface through Index)", Spread 001 reproduces the © page; 463,748 bytes; `wc -l` = 9,787; tracked.
- `md5` of `docs/research/1703Fads3D.pdf` and `admin,+The+Systems+Approach…pdf` → **identical**.
- `sed` on `tools/build_branding.py:197,375,674` → the three claimed strings verbatim.
- Lorsch greps: 5 hits at book lines 3071–3320 (Ch. 4 range, pp. ~70–77); `evidence.md:21` cites "Ch. 7–8" → mis-citation confirmed.
- `grep -rn 'restored-2026-10-18'` outside `evals/` → only `CONTEXT.md:720` (decision history); none on any public claim surface.
- `restored_review.py:66` → `random.Random(20261018).shuffle` (fixed seed); importer lines 133/138/144 → hardcoded question counts and raw-candidate numerator confirmed.
- Plans grep → all four declare "does not amend or supersede either contract"; guard `test_authority.py:14–18` checks only the literal `"supersede conflicting"`.

### 2.4 Assumptions and corrections

- GitHub repository *visibility* is UNVERIFIED offline; severity framing for F-02 states this explicitly.
- "Distribution surface" = the public Git repository (no dist/ or packaging exists).
- Initial premise "suite not executable here" was **corrected** during the audit: the suite is stdlib-runnable and green; the true finding is the undocumented invocation and absent dependency manifest (F-13).
- Raw eval data (~541 files) was sampled per protocol P-4, not exhaustively read; the G auditor's sampling exceeded the floor (full record-level parsing of both pilot JSONLs, all arm counts for every cycle, full packet verification).

## 3. Invariant Compliance Matrix

| Invariant | Source | Status | Evidence |
|---|---|---|---|
| Single editable skill authority (`skills/systematic-innovation/`) | AGENTS.md:24 | **PASS** | One SKILL.md; validator green; no adapters (T-A1, T-A4, T-A6) |
| No second copy of skill behavior | AGENTS.md:25 | **PARTIAL** | Instruction surfaces clean (T-A1) but branding assets/generator depict superseded behavior (F-02) and enforcement is filename-only (F-12) |
| Plans execute, never amend, specs | AGENTS.md:20 | **PASS** | All four plans declare non-supersession; historical amendment language purged (T-B2; guard narrow → F-12) |
| Generated outputs never authorities | AGENTS.md:30 | **PASS** | `dist/`, `benchmark/` absent; only non-authority references (T-A5) |
| Restricted outside Git/CI/dist/agent context | AGENTS.md:32–34 | **PASS** | 0 tracked, 0 historical commits; ignore patterns verified live; no sweep path; no CI exists (T-E1, T-E2, T-G3a) |
| Provider-neutral portability (7 constraints) | CONTEXT §8 | **PASS** | All seven verified in pack; PROVIDER_RE → no hits; validator enforces (T-F1, T-F2) |
| Provenance classes & source boundaries | CONTEXT §4.4–4.5 | **PARTIAL** | Three-class structure intact and §4.5 attributions corroborated against source (T-C1, T-C3), but Critical book-text breach (F-01) and Lorsch mis-citation (F-17) |
| Public claims match evidence tiers | CONTEXT §8, §19.6 | **FAIL** | Withdrawn claims live on origin/main and in assets (F-02); prior-candidate evidence labeled "Current results" (F-03); untraceable v2 numbers (F-07). Prose discipline otherwise strong (T-D1, T-D2) |
| Three studies not conflated | CONTEXT §15 | **PASS** | All current surfaces separate; only marked-superseded historical docs conflate (T-D3) |
| Raw evidence append-only | CONTEXT §14 | **PASS** | Fail-closed importer (RuntimeError, exit 1); append+fsync runner; integrity tests (T-G2a, T-G2b) |
| Sealed test terminal; gates never misrepresented | CONTEXT §11–12 | **PASS** | No sealed artifact ever; every surface records gates unbuilt/not passed (T-G3a, T-G3b) |

## 4. Findings Ledger

Ordered by severity. Each entry cites its domain auditor finding(s) and the underlying traces.

### Critical

**F-01 [CRITICAL] Full copyrighted book text committed to the repository** — [C+D-F01; B-F02; E+H-F07]
- Evidence: `docs/references/stimulating-innovation-tudor-rickards.md` — 463,748 bytes, 9,787 lines, self-described "High-Quality Full Text Extracted from Screen Recording … 118 spreads (Preface through Index)"; Spread 001 reproduces the copyright page (© Tudor Rickards 1985). Tracked; committed in `0ebddfe` (2026-10-18 13:42) — one day after the §4.4 boundary was recorded (2026-10-17). **Not on any remote branch** (`git branch -r --contains 0ebddfe` → empty): remediation window confirmed.
- Clause: CONTEXT.md:90 (§4.4 rule 3, "Do not reproduce copyrighted book text"), :68 (§4.1), :578 (§18.1:5), :817 (§22.4).
- Impact: merging/publishing the branch would redistribute a complete in-copyright 1985 work from the repository that is itself the distribution surface; the project's own provenance audit exists to prevent exactly this act. The extracted text is also the US edition, while the project's verified bibliographic record is the UK Frances Pinter edition (evidence.md:11) — so it does not even match the recorded source of truth.
- Remediation: **before any push/merge** — remove the file and rewrite/split `0ebddfe` so the full text never enters public history; relocate to an untracked `sources/`-style zone per §18.1; retain only the verified bibliographic facts already in `references/evidence.md`.

### High

**F-02 [HIGH] Withdrawn +162%/8.2x claims live on the remote default branch and in committed assets; assets also depict pre-restoration behaviors** — [C+D-F03; A+F-F01; E+H-F01]
- Evidence: `origin/main` README carries the "+162% Causal Density" badge (line 12), the "+162% causal information density" table row (line 93), and "8.2x increase" (line 95) with **no withdrawal text anywhere on that branch** (withdrawal added in `4e93a98`, stress branch only). Assets `banner/comparison/quick-demo/system-architecture.png` (committed `46ce0b6` = origin/main; embedded at README:2,26,41,59) render `build_branding.py:197` ("Pilot Lift: +162% Causal Density · 0% Roadmap Drift"), `:375` ("2.35 MECH / 1K TOK (+162%)"), `:674` ("8.2x efficiency lift…"), plus pre-restoration behaviors: batched "≤ 4 Questions" (`:532`, `:657`), automatic "Learning Probes" (`:186/:387/:527`), "5 structural dimensions" (`:522`).
- Clause: CONTEXT §19.6 ("withdrawn as substantiated primary-effect claims"); §8 evidence tiers; AGENTS.md:24–25 (assets are a second copy of superseded behavior).
- Impact: the public front door promotes a claim the project formally withdrew; on the working branch the same README withdraws the claim in prose (:74) while the images above it keep asserting it — an image cannot carry a superseded banner. **Border-Critical:** if the GitHub repository is publicly visible (UNVERIFIED offline), this is a false public claim per the rubric's Critical definition.
- Remediation: strip withdrawn numbers and pre-restoration behaviors from `build_branding.py`; regenerate all four assets; add a regression test asserting forbidden claim strings are absent from asset sources; propagate to `main`.

**F-03 [HIGH] Public claim surface presents prior-candidate evidence as current; the restored candidate's evidence is invisible** — [G-F01, G-F05, G-F06; A+F-F02]
- Evidence: README:12 "Evidence: Public Development" badge links `evals/stress/five-cycle-report.md`, whose cycles record `candidate_base_revision: 6f3acb9` — the **prior** candidate (`cycle-5/6-comparison.json:7`; `contract-findings.md:22`: those runs "are not evidence for the restored candidate"). README:72 calls it "Current results". README:47/76/127 still say contract discrepancies "still need reconciliation" although `contract-findings.md:19–22` records the 2026-10-17 restoration decision, executed and regression-tested. The badge-target report itself says "The behavioral-contract decision remains pending" (five-cycle-report.md:5,122,234; last commit `96fe3ec`, pre-restoration). `baseline-analysis.md` lacks the superseded banner its two siblings carry. No public document (README/docs/skills/SECURITY.md) references `evals/restored-2026-10-18/` — the only tree reference is CONTEXT.md:720 in decision history.
- Clause: CONTEXT §19.6 (line 711): prior-candidate runs must not be readable as restored-candidate evidence; §22 propagation.
- Impact: every reader arriving at the front door is directed to superseded evidence and told the current candidate's contract is unresolved — the exact misreading the non-relabeling rule forbids.
- Remediation: one README commit (relabel badge, link the restored report beside the five-cycle link, reword :47/76/127 to the resolved state); dated addendum to five-cycle-report.md; superseded banner on baseline-analysis.md.

**F-04 [HIGH] 47 third-party PDFs (33 MB) committed with no license/provenance record** — [C+D-F02; E+H-F07]
- Evidence: `git ls-files docs/research docs/references | wc -l` = 50; 33 MB under `docs/research/` (12.9 MB `2000-systems-of-innovation-approaches.pdf`, a 38-file Academia.edu bundle, journal papers); `docs/references/` adds two PDFs. Byte-identical duplicate committed twice (`1703Fads3D.pdf` == `admin,+The+Systems+Approach…pdf`, md5 `5949866f…`). No LICENSE/provenance/permission record anywhere in docs/; no docs exclusions in `.gitignore`; no policy statement for the corpus (grep across CONTEXT/AGENTS/docs → none). Added in the same `0ebddfe`.
- Clause: CONTEXT §18.1:5 (protected study material does not enter distributions), §20:4 (separate source research).
- Impact: Academia.edu bundles and journal papers are presumptively copyrighted; per-file lawfulness is UNVERIFIED, but no triage was performed or recorded, and the wholesale duplicate shows uncurated commit.
- Remediation: relocate to an untracked zone or record per-file license status; deduplicate; add `docs/research/README.md` stating research-input status, non-authority, and exclusion from distributions; record the decision in CONTEXT §4/§19.8.

**F-05 [HIGH] 9-commit branch divergence with stale public `main` and no recorded merge/decision plan** — [E+H-F02]
- Evidence: branch is 9 ahead / 0 behind `main`; `main` == `origin/main` == `46ce0b6`; `git diff main..HEAD --stat`: 7 skill files + README + CONTEXT differ (main ships the pre-restoration skill and pre-withdrawal README); assets identical on both branches (stale on both). Grep for a merge plan finds only the loop constraint (CONTEXT:469) and a historical question (:619).
- Clause: CONTEXT §22 (decisions in version control; withdrawals must propagate); architecture spec §11/§15.5.
- Impact: the default branch is a snapshot of the state the project's own records supersede; the divergence has no recorded disposition, so drift compounds.
- Remediation: record an explicit merge/decision plan in CONTEXT §19.8 (merge strategy, claim corrections, main re-baselining) before further divergence; execute after F-01 remediation.

### Medium

**F-06 [MEDIUM] Skill's Execution-Channel and Hard Output Budget precedence have no approved specification basis** — [B-F01]
- Evidence: SKILL.md:29–34 and :36–40 + output-contract.md:5–11 (80% target, Compact Portfolio Template) have no spec counterpart (spec's only budget language is the *no-implementation-budgets* clause, spec:40,324). Both entered in `da237d1` (stress-cycle candidate) and were retained through the owner-directed restoration; §19.6's restored-boundary list does not include them. CONTEXT.md:727–729 claims they were "reconciled … with the approved contract," but the contract contains no such provisions. The budget rule's own efficacy is unresolved (400-word holdout produced 575 words; CONTEXT:731–733).
- Clause: AGENTS.md:20 (requirements live in specifications); the four benchmark corrections show the required incorporation pattern.
- Remediation: draft a spec amendment for both precedence rules and the pending §15/§12/§14 deltas (F-09/F-10/F-21), submit for owner approval, record in CONTEXT §19 — or record them as retained execution refinements pending incorporation.

**F-07 [MEDIUM] v2 synthesis self-labels "Approved," cites a nonexistent spec, and presents untraceable quantitative results** — [B-F03; C+D-F04]
- Evidence: `docs/research/2026-10-18-v2-brainstorming-synthesis.md:4` ("Status: Approved Brainstorming & Architecture Synthesis"); :63–70 ("five independent architectural passes"; "+22% Vendi", "+35% adoption", "+28% Vendi" — found nowhere else in the tree, linked to no runs); :83 names `docs/specifications/2026-10-18-systematic-innovation-v2-design.md` which does not exist. Nothing references or implements the document; the `measure-*-v2` dirs are measurement-version artifacts, not v2 runs.
- Clause: CONTEXT §8 tiers; SKILL.md:86 ("No Fabricated Statistics"); §22.
- Impact: a committed, public-bound document asserts measured gains with no evidence and an authority label no decision record corroborates — downstream agents could treat the numbers as established.
- Remediation: relabel :4 as research input (mirroring CONTEXT:82), qualify or remove the percentages, record that the v2 spec was never authored; or open a proper v2 cycle with a real decision record.

**F-08 [MEDIUM] CONTEXT.md change-control loop not exercised for the head commit `0ebddfe`** — [B-F02]
- Evidence: `0ebddfe` (research corpus + v2 synthesis; ~9,874 insertions) is recorded nowhere in CONTEXT.md (newest entries remain §19.6–19.7); grep for corpus/v2/`0ebddfe` → no hits. `a36903a` and `bb05213` are covered; the head commit is not.
- Clause: CONTEXT §22 triggers 2, 3, 7.
- Remediation: add a §19.8 (or §4.6) entry: what the corpus is, provenance class per §4.4, disposition decision, v2 status, and pointer to this audit.

**F-09 [MEDIUM] Spec §15 capability-aware research branch unimplemented in the skill pack** — [B-F04]
- Evidence: spec:328–340 sanctions research use when hosts provide tools, with a five-row capability table; skill-pack greps find only the subagent fallback and conditional reference loading — no research-use provision. The skill implements only the offline branch of an approved two-branch contract.
- Remediation: add a compact capability-awareness clause, or record an owner decision narrowing §15.

**F-10 [MEDIUM] Spec §12 preservation-first/no-change conclusion not carried into the skill pack** — [B-F05]
- Evidence: spec:265 ("A 'no change' or preservation-first conclusion is valid…"); skill-pack greps for `no change|preservation-first` → 0 hits. When the correct answer is "don't change anything," the six-layer portfolio contract gives the skill no sanctioned way to conclude it.
- Remediation: one authorizing sentence in SKILL.md or output-contract.md §1.

**F-11 [MEDIUM] The "universal fallback" (SKILL.md alone) silently omits the output contract** — [A+F-F03]
- Evidence: README:117–118 instructs passing SKILL.md directly; the six-layer structure lives only in output-contract.md:13–56, Deep stop/filter rules only in deep-mode.md:14–36; SKILL.md:92–96's conditional reading is impossible without file access; `validate_skill.py` enforces existence, not self-sufficiency. Core generation survives inline, but fallback users get portfolios without the contracted structure, and README:85's "100% Portable Markdown" reads as full-function portability.
- Remediation: instruct fallback users to paste all five files, or add a minimal layer skeleton to SKILL.md, or state the degradation explicitly.

**F-12 [MEDIUM] Authority enforcement is filename-level; the blind spot has already been hit** — [A+F-F04; E+H-F08; B-F09]
- Evidence: `authority.py:48–53` rejects only files *named* SKILL.md outside the canonical path; `:58–62` and `test_authority.py:14–18` guard only the literal `"supersede conflicting"`; no CLI; `validate_skill.py:77–80` exempts evidence.md from the provider scan with no documented rationale; nothing scans `build_branding.py`/`assets/` — where drift actually occurred (F-02). The guard would not have caught the historically recorded amendment language (§19.4).
- Clause: AGENTS.md:20, :25.
- Remediation: content-signature sweep (counts, cell names, layer names, seven-question rule) over an explicit allowlist; broaden the supersession phrase list; add a CLI; document or drop the evidence.md exemption.

**F-13 [MEDIUM] No documented test/build/type-check commands at the root orientation layer** — [E+H-F03]
- Evidence: AGENTS.md contains no commands; README:98 documents only the validator; the documented unittest invocations live only in plans (skill plan :420, :470, :514, :535) and the restored runbook:56–57. Suite verified green: `python3 -m unittest discover tests` → 116 OK; pytest absent (exit 1). No build or type-check commands exist anywhere (coordinated plan :356 defers mypy to CI).
- Clause: CONTEXT §18.1:3, §18.2:5; architecture spec §7:4.
- Remediation: add a "Validation commands" block to AGENTS.md; state pytest is not used.

**F-14 [MEDIUM] Runner lacks documented spend/safety controls: cost cap, model allowlist, failure thresholds, redaction** — [E+H-F04]
- Evidence: `stress_runner.py` implements call cap (:260, enforced :278–280), concurrency (:259), 180s timeout (:136), read-only sandbox (:92); `monetary_cost: None` (:242), free-form `--model` (:256), no failure thresholds, no retries, no credential redaction (raw CLI events stored unredacted, :165, :209). CONTEXT:461–465 states the runner "supports" all of these.
- Clause: CONTEXT §14 items 6–11 (design intent; formal package recorded unbuilt).
- Remediation: annotate §14 with implementation status, or add the guards before the next run campaign — this is the one tool that spends provider budget.

**F-15 [MEDIUM] SECURITY.md omits the trust-zone model and the repo-vs-skill executable boundary; non-routable contact** — [E+H-F05]
- Evidence: skill-side claims verified TRUE (validator exit 0; 5-file all-Markdown pack). But SECURITY.md never states the repository contains executable Python (`stress_runner.py` drives a subprocess; `build_branding.py` imports playwright and fetches Google Fonts, :2, :8–12), while architecture spec :266 requires the trust-zone explanation; `:23` gives `security@systematic-innovation.local` — `.local` is not a routable domain.
- Remediation: add a two-paragraph trust-zone section; replace the address or go advisory-only.

**F-16 [MEDIUM] No CI, packaging manifest, or CONTRIBUTING; the plan-sequenced deferral lacks its required trigger record** — [E+H-F06]
- Evidence: `.github/`, `pyproject.toml`, `setup.cfg`, `Makefile`, `package.json`, `CONTRIBUTING.md` all absent while 116 stdlib tests and executable tooling exist. Coordinated plan :36–48 sequences CI to step 6 — a recorded ordering — but no document records "CI deferred until X" with trigger/rationale as spec §15.7/AR-11 require, and spec §12.2 says CI "should" run once executable code exists.
- Remediation: record the trigger in one line; a minimal stdlib Actions workflow is ~5 lines.

**F-17 [MEDIUM] Lawrence/Lorsch chapter mis-citation in the provenance reference** — [C+D-F05]
- Evidence: `evidence.md:21` cites "Rickards (1985, Ch. 7–8)"; all five Lorsch mentions in the committed book text sit at lines 3071–3320 = Chapter 4, pp. ~70–77 (verified first-hand). An unverified chapter locator in the file whose purpose is citation accuracy — the class §4.4 rule 1 excludes.
- Remediation: correct to Ch. 4 or keep only the author attribution.

**F-18 [MEDIUM] Retained pilot evidence has structural, undocumented defects: 2-vs-3-turn asymmetry and a cross-arm numerator mismatch — the arithmetic mechanism behind the withdrawn headline** — [G-F02, G-F03, G-F07]
- Evidence: runbook:9–11 requires the identical 3-turn script for all conditions; baseline Deep records have 3 turns (final scripted disclosure "Produce your final portfolio"), treatment records have **2** — the final disclosure was never delivered (importer comment :97–119). Stored efficiency numerators differ by arm: baseline = 1000×distinct-families/tokens (aggregate 0.897), treatment = 1000×raw-candidates/tokens (importer :138,144; aggregate 2.352 — exactly the withdrawn +162% headline's inputs, matching treatment-analysis.md:28 and candidate-report.md:45). `turn_1_question_count` is hardcoded (:120, :133; meal-planning recorded 0 vs. 3 actual question lines; baseline used a '?'-character heuristic). Raw assistant text is intact; the headline withdrawal is recorded; these specific defects are not documented anywhere.
- Clause: CONTEXT §12.1 (same information, same order, same turn ceiling); §19.6.
- Remediation: one-sentence errata on both pilot analyses' superseded banners recording the turn asymmetry, the numerator mismatch, and the fabricated question-count field; treat all pilot derived fields except `turns`/`final_response` as unverified.

**F-19 [MEDIUM] Pilot rubric/runbook promise semantic clustering and a collapse ratio the tooling does not deliver** — [G-F04]
- Evidence: rubric.md:39 ("free-text paraphrases … merged into one family"), :43 (Duplicate Collapse Ratio); runbook:26–27 ("semantic/token equivalence clustering"). Implementation is lexical-only: `pilot_metrics.py:227–275` union-find over stemmed cosine (thresholds 0.26/0.45/0.65); the repo's own `lexical-boundary-audit.json` proves a paraphrase split (1 expected → 2) and an order-swap merge (2 expected → 1); the collapse ratio exists only in the disabled importer — `score_eval_results.py` has no such field. Mitigation: current reports label the measure lexical (five-cycle-report.md:93; restored report.md:100–101).
- Clause: CONTEXT §19.5 corrections 2–3.
- Remediation: annotate rubric §3/runbook §2 with the implemented-method boundary, or add the two-line collapse-ratio computation to the live scorer.

### Low

**F-20 [LOW] `contract-findings.md:3` header still says the owner decision is pending** — [B-F08] — contradicts its own :19–23 resolution section. Rewrite to past tense.

**F-21 [LOW] High-stakes "exploratory + explicit verification needs" labeling absent from the skill pack** — [B-F06] — spec:326 required; SKILL.md:87 has the refusal floor but no labeling clause. One guardrail sentence.

**F-22 [LOW] Quick-mode one-question allowance and two workflow micro-steps dropped** — [B-F07] — spec:120–133 vs SKILL.md:26–49; defensible for one-turn channels but unapproved. Fold into F-06's reconciliation.

**F-23 [LOW] Two spec-listed lenses (morphological recombination, subtraction) not operational** — [B-F10] — spec §10 palette members appear only as labels/provenance rows. One-line operator cues or record the narrowing.

**F-24 [LOW] stress_runner's format-matched control prompt hard-codes the skill's signature counts** — [A+F-F05] — `stress_runner.py:56–66` embeds "10 to 15"/"15 to 24"; plan-sanctioned instrument, but no drift guard if canonical targets change. Derive from the pack or assert.

**F-25 [LOW] validate_skill provider-scan gaps** — [A+F-F06] — evidence.md exempted without rationale (`:77–80`); regex misses gemini/gpt/openai/anthropic/copilot (`:9`). Not load-bearing today (pack scans clean). Drop the exemption; broaden the regex.

**F-26 [LOW] CONTEXT §6 restates the behavioral contract with no sync enforcement** — [A+F-F07] — currently in sync (verified); a future one-sided edit creates a stale behavioral statement in an agent-loaded root file. Add a sync lint or an "as of 2026-10-17" stamp.

**F-27 [LOW] Untracked `evals/audits/` (14 files, 440 KB) has no recorded commit/ignore/relocate policy** — [E+H-F09] — the only untracked content with no disposition record (contrast: bundle policy recorded at CONTEXT:655 and followed). Record a one-line decision.

**F-28 [LOW] Tool portability/overwrite defects** — [E+H-F10] — hardcoded `<home>/…` paths (`compile_treatment_results.py:15`, `stress_runner.py:257`); `score_eval_results.py:178–179` writes output unconditionally (no exists-refusal, unlike `restored_review.py:90–91`).

**F-29 [LOW] README wording outruns and undersells the evidence** — [C+D-F06, F07, F09] — "Transforms ordinary AI ideation" (:23) vs. inconclusive current results; "Zero … dependencies at runtime" (:86) unqualified for a repo whose dev tooling imports playwright; "format-matched comparisons … remain unverified" (:76) although a format-matched control ran in the small uncalibrated diagnostic. Reword to design-intent language; scope the dependency claim; optionally note the control ran.

**F-30 [LOW] Superseded pilot reports carry a mislabeled trigger metric and a drifted paraphrase** — [C+D-F08] — candidate-report.md:52 ("Negative Trigger Precision 100%") measured with the skill explicitly loaded (model-behavior scope, not the §15 activation study); treatment-analysis.md:61 paraphrases the Three Problem-Owner Questions incorrectly (mixes question (c) with the boundary modes; verified questions at output-contract.md:47). Frozen historical records — optionally append caveat lines.

**F-31 [LOW] Blinding is procedural only: assignment key co-committed beside every packet, shuffle order publicly reconstructable** — [G-F08] — `assignment-key.json` sits beside `human-answers.json` in all 16 measurement dirs by design (`restored_review.py:98`); fixed seed (`Random(20261018)`, :66). No current violation — the packet is genuinely unrated (80 `mechanism_ratings: None`; 286 pairs `preference: None`; forced-None fields; docs claim preparation only). Before the approved 40-pair calibration: regenerate the packet with a key held outside Git or restrict reviewers to exported files; record the operational rule.

**F-32 [LOW] §19.5 Hungarian one-to-one matching is implemented nowhere — no remediation required** — [G-F09] — absent from all tools; correctly so: the hidden-mechanism cases live in the unbuilt restricted package and every surface records the formal package as unbuilt (report.md:21–25; CONTEXT:752). Track as an acceptance criterion when the package is authored.

## 5. Verified Strengths

- **S-1 Restored skill conforms to the approved contract.** All five owner-restored boundaries closed with regression tests; 13 element-level conformances verified against the 735-line specification: portfolio targets, discovery protocol (one-at-a-time, ≤7), Innovation Brief fields, mechanism ledger, distinctness rule, saturation, six disclosure layers, Reasoning Cells, provenance labeling, decision restraint, safety refusal, subagent honesty, fluency-depletion ordering. [B S-1–S-13]
- **S-2 No competing behavioral authority.** Full-tree signature sweep classifies every hit as spec/plan, in-sync CONTEXT §6 narrative, frozen evidence, measurement instrument, enforcement test, or strictly-historical quotation; the old "Quick 4–6 / Deep 6–9" behavior exists nowhere as live instruction; the benchmark injects the canonical pack verbatim. [A+F S-1, S-2]
- **S-3 All seven portability constraints hold**; the pack is five Markdown files; validator green; sequential fallback described honestly. [A+F S-3–S-5, S-9]
- **S-4 No host adapters exist; generated dirs absent and never treated as authorities.** [A+F S-6, S-7]
- **S-5 Restricted/sealed isolation is complete**: zero tracked matches, zero historical commits, all ignore patterns verified live, no agent-context sweep path, no sealed-run artifact, and every surface records the six/twelve-case gates as unbuilt. [E+H S-2; G S-4]
- **S-6 The suite is green on the standard library**: 116 tests, exit 0, no pytest constructs, zero third-party test dependencies — including an AST guard against duplicate-test overwrites (the recorded T2 incident's regression). [E+H S-1; G S-8]
- **S-7 The legacy-import guard demonstrably prevents the recorded overwrite failure mode**: unconditional RuntimeError before any I/O (verified live, exit 1), RED/GREEN logs retained, historical outputs untouched in Git. [G S-1; E+H S-3]
- **S-8 Raw evidence is append-only with layered integrity**: append+fsync, duplicate-completion refusal, manifest immutability, advisory lock, resume guards; dry-run clean. [G S-2; E+H S-5]
- **S-9 Report numbers reconcile with raw data almost perfectly**: pilot per-case means reproduce both analyses exactly; Cycle 1/2/4/5 counts and corrected token totals reproduce from raw; Cycle-6 frozen comparison matches the report table; restored-study counts (80 conv / 104 turns / 107 calls), word counts, and per-epoch pack hashes all reproduce — final-epoch hashes match the *current* skill. The "116 tests" claim reproduces today. [G S-3]
- **S-10 Vendi Score implemented as documented** (kernel eigenvalue entropy, cyclic Jacobi, k∈{0.5,1,2}; identical→1.0 pinned by tests); cumulative-usage correction retains both original and audited totals. [G S-6, S-7; E+H S-4]
- **S-11 Honest measurement labeling throughout the tooling** ("not performed", "legacy_estimate_unverified", "lexical_screen_only…", "no_blocks_detected_not_proof_of_absence"), and the unrated-packet state is enforced in code, not just prose. [E+H S-7; G S-5]
- **S-12 Scoring tests are genuinely behavioral with negative cases** (41 pilot-metrics tests encoding observed failure modes; 16 layout-boundary fixtures; condition-isolation refusal; seeded determinism; fail-closed eigensolver). [E+H S-6, S-8]
- **S-13 Provenance three-class structure intact; §4.5 verified attributions corroborated against the committed source text** (Ch. 8 sections and pp. 158–160 material match); adapted-methods honesty explicit. [C+D S-1–S-3]
- **S-14 Withdrawn-claims hygiene is strong in every prose surface** (withdrawal statements, dated superseded banners, five-cycle-report:188) — the failures are confined to assets and branch state. [C+D S-4]
- **S-15 Three-studies separation respected in all current surfaces**; sampled-language discipline and Cycle 5/6 version distinguishability hold; benchmark-mapping arXiv corrections present with historical raw records intact. [C+D S-5–S-7, S-10]
- **S-16 Plans carry no supersession language**; the historical amendment language recorded at §19.4 is gone from all four plans. [B S-12; verified first-hand]
- **S-17 Boundary hygiene mechanics work**: `.gitignore` patterns verified live against synthetic paths; `.gitattributes` effective (i/lf w/lf, binary macros). [E+H S-2, S-10]

## 6. Domain Evidence Traces (consolidated)

- **Domain A+F (authority, portability):** T-A1 full-tree duplication sweep with per-hit classification → no competing authority; T-A2 README-vs-SKILL conformance (value-prop bullets verified; fallback and findings-status diverge → F-03, F-11); T-A3 authority.py line-by-line + 31-test run → enforcement map (F-12); T-A4 no adapters; T-A5 generated dirs absent; T-F1–F4 portability constraints, provider scan, reference integrity, sequential honesty → all PASS.
- **Domain B (spec conformance):** T-B1 element-by-element skill-vs-spec diff (spec read 735/735; skill pack full) → 13 conformances, 6 divergence classes; provenance of additions via `git log -S` (both precedence sections from `da237d1`). T-B2 plan-authority greps + full coordinated plan read → no supersession; guard narrow. T-B3 per-row contract-findings reconciliation → all five closed; header stale (F-20). T-B4 commit-by-commit CONTEXT currency → 0ebddfe uncovered (F-08); §12/§19.5 corrections incorporated into spec ✓. T-B5 v2 authority status → self-label uncorroborated (F-07).
- **Domain C+D (provenance, claims):** T-C1 evidence.md + heading-map cross-check → three-class boundary intact, Lorsch mis-cited (F-17); T-C2a book-text head, size, commit provenance → F-01; T-C2b corpus inventory, md5 duplicate, absent policy → F-04; T-C3 §4.5 attributions corroborated against source spreads → PASS. T-D1 badge-by-badge tier check (MIT ✓, frontmatter ✓, five-cycle self-label ✓, tests structural ✓, pure-markdown ✓); T-D2 claims sweep (162: 8 hits; density: 163; efficiency: 431 — reviewed) → one resurrection surface (F-02); T-D3/T-D4 separation and sampled-label discipline → PASS; T-D5 benchmark-mapping correction structurally verified.
- **Domain E+H (boundaries, engineering):** T-E1–E5 ignore/history/untracked/attributes verification → boundary PASS, evals/audits policy absent; T-H1 pytest exit 1 → unittest 116 OK → undocumented-invocation finding (F-13); T-H2 all 8 tool modules read → token correction verified, spend-controls absent (F-14), tool defects (F-28); T-H3 all 13 test modules read → behavioral vs. lint-style mapped; T-H4 governance gaps vs. recorded plan sequence (F-16); T-H5 SECURITY.md vs. spec requirements (F-15).
- **Domain G (evaluation laboratory):** T-G1a–h record-level reconciliation across pilot/stress/restored arms (full parsing of pilot JSONLs; all arm counts; in-memory recompute matching frozen comparisons; pack hashes vs. current skill) → S-9, F-18; T-G2a–b importer guard + append-only runner verified live; T-G3a–b sealed/gate sweeps → PASS; T-G4a–c rubric-vs-implementation gap (F-19), Vendi verified, Hungarian correctly absent; T-G5a–d README/badge/report staleness map (F-03); T-G6a–b packet verification + blinding mechanics (F-31).

## 7. Gaps & UNVERIFIED

- **GitHub repository visibility** (public vs. private) — unverifiable offline; governs whether F-02 is formally a *false public claim* (Critical) or an internal-claims violation (High).
- **PNG pixel content** — no image-capable verification in any audit session; F-02 rests on the committed generator text, same-commit asset creation, exact render-signature dimension match, and the clean tree.
- **Per-file copyright status of the 49 committed PDFs** — not opened; presumptively copyrighted; per-file lawfulness unresolved.
- **External validity** — arXiv IDs, URLs, the Vendi paper, Rickards 1975/1978 bibliography: unverified (no network).
- **Historical test-count logs** (61/67/72/84 tests in retained verification logs) — point-in-time records; only the current 116-test suite was dynamically verified.
- **Operator-side restricted/sealed packs** — unverifiable from this repository (none exist locally; isolation verified structurally).
- **Whether the v2 synthesis's "Approved" label reflects an off-tree owner approval** — no record exists either way; stated as a disjunction, not a fact.
- **pytest invocation path** — unverified (absent); the stdlib path was verified instead and reconciles the reports' "116 tests" claims.
- Prior audit reports were not read (independence rule); a few lines surfaced incidentally in greps and were not used.

## 8. Remediation Priorities & Owner Decision Queue

**Risk register (ranked, from the traces):** (1) legal/provenance exposure — F-01, F-04 — blocks any publish/merge; (2) public misrepresentation — F-02, F-03, F-05 — the project's central promise ("current public claims follow the audited evidence") is violated at its front door; (3) measurement validity still unestablished — F-18, F-19, open budget regression, no calibrated judge — the skill's efficacy claim remains unproven; (4) authority-drift recurrence — F-06, F-12 — spec-less additions already happened once and enforcement cannot catch them; (5) reproducibility friction — F-13, F-14, F-16, F-28; (6) decision-record gaps — F-07, F-08.

**Phase-1 trajectory (Domain I1):** delivered — specs/plans aligned and committed; root authority routing implemented and tested; 12-case pilot corpus + validator built; no-skill RED baseline and format-matched control run (with the F-18 defects now documented); canonical skill authored and conformant; GREEN paired numbers produced but inconclusive (efficiency unresolved; budget regression open; no calibrated quality). **Remaining before the six-case gate:** clear the P0/P1 items below, rate the prepared blinded packet (with F-31's operational fix), then author the formal benchmark package.

### P0 — before any push, merge, or publish (publication blockers)

1. **(F-01, F-04)** Remove `docs/references/stimulating-innovation-tudor-rickards.md`; rewrite or split the unpushed `0ebddfe` so the book text and untriaged PDFs never enter public history; relocate both to a gitignored `sources/` zone; deduplicate the identical PDF; record the disposition in CONTEXT §19.8.
2. **(F-02)** Edit `tools/build_branding.py` (withdrawn numbers at :197, :356–375, :674; pre-restoration behaviors at :186, :387, :522, :527, :532, :657); regenerate all four assets; add a regression test asserting forbidden strings ("+162%", "8.2x", "Learning Probes", "≤ 4 Questions") are absent from asset sources.
3. **(F-03)** One README commit: reword :47/:76/:127 to the resolved restoration state (per contract-findings.md:19–22); relabel the evidence badge at :12–13 to name the candidate revision and link `evals/restored-2026-10-18/report.md` beside the five-cycle link at :72; append a dated addendum to five-cycle-report.md; add the superseded banner to baseline-analysis.md.

### P1 — governance this week

4. **(F-05, F-07, F-08, F-20)** Record CONTEXT §19.8: corpus disposition, v2-synthesis status (relabel or open a proper cycle), stress-branch merge/decision plan, pointer to this audit; fix contract-findings.md:3.
5. **(F-06, F-09, F-10, F-21, F-22, F-23) — owner decision:** draft one behavioral-spec amendment covering execution-channel precedence, user-budget precedence, the §15 capability clause, §12 preservation-first conclusion, §14 high-stakes labeling, the Quick one-question allowance, and the two missing lenses; approve and record per the four-corrections pattern — or record the deltas as pending refinements. The skill currently carries two strong precedence rules with no approved requirement behind them.
6. **(F-13, F-16)** Add the AGENTS.md validation-commands block; decide CI adoption (a minimal stdlib workflow is ~5 lines) and record the trigger either way.

### P2 — engineering hardening

7. **(F-12, F-25)** Extend authority.py: content-signature sweep over an allowlist, broadened supersession phrase list, CLI; document or drop the evidence.md provider exemption.
8. **(F-14, F-28)** Add cost cap + model allowlist + redaction to stress_runner before the next campaign; fix hardcoded paths and the unconditional overwrite.
9. **(F-15)** SECURITY.md trust-zone section + routable contact channel.
10. **(F-18, F-19)** Pilot errata (turn asymmetry, numerator mismatch, question counts) on the superseded banners; rubric/runbook implemented-method annotations or the collapse-ratio field.

### P3 — hygiene

11. **(F-17, F-24, F-26, F-27, F-29, F-30)** Lorsch locator; stress_runner drift assertion; CONTEXT §6 sync lint or "as of" stamp; evals/audits disposition; README wording (three items); optional caveats on superseded pilot docs.
12. **(F-31)** When scheduling the 40-pair calibration: regenerate the packet with a fresh key held outside Git or restrict reviewers to exported files; record the rule in human-review.md.

### Owner decision queue (Domain I3)

| # | Decision | Options | What decides it |
|---|---|---|---|
| 1 | Corpus + book-text disposition | History rewrite vs. relocate-and-ignore; per-file license triage | F-01/F-04 evidence; §4.4 boundary; owner's publication intent |
| 2 | Branch strategy | Merge stress branch post-fixes vs. re-baseline main | F-05; recorded in §19.8 either way |
| 3 | Claims-surface policy | Claim-free assets + badge wording; who owns the claim-string regression test | F-02/F-03; §8 tiers |
| 4 | Spec reconciliation | One amendment vs. pending-refinement record | F-06 cluster; the four-corrections precedent |
| 5 | v2 synthesis | Relabel research input vs. open proper v2 cycle | F-07; whether "Approved" reflects an off-tree decision |
| 6 | CI/manifest timing | Minimal workflow now vs. plan step 6 | F-16; AR-11 trigger language |
| 7 | Calibration sequencing | Rate packet (after F-31 fix) → six-case gate | G strengths; F-18/F-19 errata first |
| 8 | `evals/audits/` disposition | Commit / ignore / relocate | F-27 |
| 9 | §19.8 entry scope | Cover 0ebddfe, restoration status, this audit | F-08; §22 triggers |

## 9. Traceability Self-Check

Performed during consolidation, with the following corrections made rather than papered over: (1) Domain G's "no references outside evals/" was narrowed to *public claim surfaces* after the orchestrator's grep found CONTEXT.md:720 in the decision history — the finding stands, its scope is now accurate; (2) the initial premise "test suite not executable" was corrected to "undocumented invocation, absent manifest" after live stdlib runs (116 OK) — three auditors independently converged; (3) F-02's severity is documented as High-border-Critical with the visibility caveat stated, not asserted either way; (4) overlapping domain findings (+162% assets: three auditors; v2 status: two; authority guard: three) were merged with all source citations retained, so no claim in this report lacks a trace-backed finding behind it. Every Executive Summary and Findings Ledger claim above references findings whose evidence cites `path:line` or command+exit-code traces in §2.3 and §6. No orphaned conclusions remain.