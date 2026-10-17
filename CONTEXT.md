# Systematic Innovation Project Context

**Project:** `systematic-innovation`

**Context established:** 2026-09-01

**Status:** Behavioral and repository-architecture specifications approved with 2026-10-17 primary-source and quantitative benchmark amendments; coordinated and component plans aligned; Phase 1 implementation (core skill + 12-case empirical pilot) authorized

**Purpose of this file:** Preserve the original intent, reasoning, evidence boundaries, decision history, and current state so a future person or coding agent can resume without relying on conversation memory.

## 1. How to Use This File

Read this file before proposing changes to the project.

This file is the canonical narrative and decision history. It explains why the project exists, what was considered, what changed, and which questions remain open. It is not a substitute for the approved design specification or implementation plans.

Use this reading order:

1. `CONTEXT.md` for intent, history, rationale, boundaries, and current state.
2. `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md` for the approved behavioral and evaluation design.
3. `docs/superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md` for the approved repository architecture.
4. `docs/superpowers/plans/2026-09-01-systematic-innovation-coordinated-implementation.md` for cross-plan ownership and execution order.
5. `docs/superpowers/plans/2026-08-31-systematic-innovation-skill.md` for skill implementation tasks.
6. `docs/superpowers/plans/2026-08-31-systematic-innovation-benchmark-runner.md` for benchmark-runner implementation tasks.
7. `docs/superpowers/plans/2026-08-31-systematic-innovation-benchmark-study.md` for corpus, study, calibration, staged execution, and reporting tasks.

If these documents appear to conflict, do not silently choose one. Identify the conflict and resolve it with the project owner. Later explicit approved decisions supersede earlier language, but they should be incorporated into the affected documents rather than left as oral history.

## 2. Original Idea

The project began with interest in Tudor Rickards's 1985 book *Stimulating Innovation: A Systems Approach* and a broader question:

> If innovation can be stimulated through a systematic process, can that process help an AI generate useful, non-obvious ideas that ordinary prompting would usually miss?

The goal was not to summarize a book or make an AI imitate an author. The goal was to convert a disciplined way of escaping mental stuckness into an installable AI capability that people could apply to real problems.

The motivating observations were:

1. Ordinary LLM brainstorming often produces polished but generic suggestions.
2. Several ideas may use the same causal mechanism while changing only wording, audience, interface, or industry.
3. Models often jump from a vague problem to solutions without reframing the problem or mapping the system.
4. Models frequently select a winner or produce an implementation plan before the possibility space has been explored.
5. Novelty can be performative. A proposal can look new while discarding valuable existing behavior or ignoring legitimate constraints.
6. A systematic sequence of reframing, contrasting perspectives, mechanism generation, recombination, and duplicate detection might improve AI ideation.

The intended product became a reusable Agent Skill rather than a one-off prompt. The project should be useful to people confronting business, technology, product, service, operational, educational, government, nonprofit, and personal challenges.

## 3. Product Inspiration and Naming

The repository at `https://github.com/virgiliojr94/book-to-skill` was an important product inspiration. The relevant lesson was not simply that a book could be summarized into instructions. It was that an idea could become an installable, shareable, discoverable agent capability with a clear public identity.

There was an early discussion about making the project viral and using an AI-related marketing name. That direction was corrected. The intended virality is the kind of usefulness and shareability represented by `book-to-skill`, not a sensational name detached from the capability.

The canonical name was approved as:

`systematic-innovation`

This name is descriptive, durable, compatible with skill discovery, and broad enough to support many domains. Do not rename the skill for marketing reasons without a separate naming and discovery evaluation.

## 4. Source Materials and Evidence Status

### 4.1 Internet Archive book record

The initial book reference was:

`https://archive.org/details/stimulatinginnov0000rick/page/n6/mode/1up`

The project began by looking for lawful access and other online records of the book. Access to a book record did not establish permission to redistribute the full copyrighted work.

### 4.2 Uploaded education PDF

The uploaded file named `EdTechStimulatingInnovation.pdf` is a 2013 chapter titled *Stimulating Innovation (or Making Innovation Meaningful Again)* by Maureen M. Mirabito and T. V. Joe Layng in the *Handbook on Innovations in Learning*.

It is not Tudor Rickards's 1985 book. It contains relevant ideas about systemic change, innovation fatigue, preservation of what works, sustaining and disruptive innovation, organizational support, and connecting innovation to clear goals. It must remain disambiguated from Rickards's work.

### 4.3 Deep Research report

The uploaded deep-research report was named `Tudor Rickards Book Research.pdf.pdf`.

It provided useful bibliographic leads, later influences, proposed framework interpretations, possible skill mechanics, contemporary-review leads, and an explicit distinction between confirmed facts and inferences. It also contained reconstructed chapter structures, page ranges, framework labels, and a proposed AI system prompt that could not all be treated as verified primary-source content.

The report is research input, not an authoritative substitute for the book.

### 4.4 Audit conclusion

An audit from the perspective of a stimulating-innovation specialist and a separate audit from the perspective of an LLM-behavior specialist led to an important correction:

1. Do not claim that reconstructed framework names, chapter titles, matrices, page locations, or procedural sequences are verified Rickards terminology unless supported by a reliable source.
2. Do not write the skill as though it is an authorized digital implementation of Rickards's exact proprietary method.
3. Do not reproduce copyrighted book text.
4. Use well-supported systemic principles associated with Rickards and broader innovation literature.
5. Attribute established creative-problem-solving methods accurately when detailed provenance is requested.
6. Clearly label project-original AI mechanisms as original rather than retroactively attributing them to Rickards.

This produced the project's three provenance classes:

| Class | Meaning | Examples |
| --- | --- | --- |
| Verified principles | Principles supported by reliable sources | Systemic innovation, mental stuckness, reframing before ideation, creative climate, divergent versus convergent work, purpose connection, preservation of existing value, search constrained by a selection environment, three problem-owner questions, mission-orientated versus negotiative versus participative boundary modes, initial fluency depletion |
| Adapted methods | Established techniques used in an adapted AI workflow | Objective laddering, multiple redefinition modes, assumption reversal, synectic excursions and analogy, morphological recombination, constraint transformation, leverage analysis, stakeholder and incentive analysis |
| Original AI mechanisms | Behaviors designed specifically for this skill | Adaptive Quick and Deep routing, Reasoning Cells, mechanism ledger, mechanism-level duplicate detection, saturation stopping, progressive disclosure, capability fallback |

Normal outputs should use concise method labels. Detailed provenance can be supplied when requested. The internal evidence reference must preserve the three-way distinction.

### 4.5 Primary-Source Book Scan and Empirical R&D Literature (Verified 2026-10-17)

On 2026-10-17, a 10-page owner scan of Tudor Rickards's 1985 book *Stimulating Innovation: A Systems Approach* (Frances Pinter, London, `pp. xi + 221`, ISBN `0-86187-512-5`) was audited alongside Rickards's empirical studies (*R&D Management* 1973, 1975; *Journal of Management Studies* 1978; *Contemporary Psychology* review by Rousseau 1987).

The scan verified the exact nine-chapter structure and twelve figures of the 1985 book (confirming that the earlier twelve-chapter table in the unverified research report was a hallucination and remains excluded) and established four primary-source concepts from Chapter 6, Chapter 8 (*Ideas into action*, pp. 158–163), and the R&D studies:

1. **Search/select sequences inside a selection environment:** Innovation is modeled as coupled search and selection under uncertainty constrained by an organizational selection environment (Figure 2.3 and Figure 6.1).
2. **Three problem-owner questions (p. 160):** Closing down under uncertainty for a bounded problem-owner centers on: (a) Is the idea new to the problem-owner/system? (b) Is it relevant to the mission or project goal? (c) Is it actionable through the problem-owner's own resources?
3. **Sub-system overflow and three action modes (pp. 159–163):** Solving sub-problems within local boundaries fails when systemic problems overflow spheres of responsibility (the problem of integration). Rickards distinguishes:
   - *Contractual / mission-orientated:* Clearly bounded mission and problem-owner with actionable local resources.
   - *Negotiative:* Two or more interest groups share neither goals nor beliefs about how goals are reached; requires challenging the initial brief and finding creative win-win resolutions where new goals emerge rather than splitting the difference.
   - *Participative:* Shared system-wide mission where specific goals emerge through discovery and felt needs (Action Research tradition).
4. **Initial fluency depletion and the Yes-But reflex (p. 159; Rickards 1975, 1978):** Conventional brainstorming produces top-of-mind memory dumps with low speculation until structural operators (multiple redefinition across analytic, empathic, motivational, metaphorical, and boundary-relaxed modes; morphological synthesis; synectic excursions) intervene. New ideas also face habitual *Yes-but* rejection before receiving a fair hearing.

## 5. Design Interview and Resulting Direction

The skill design was developed through a sequence of user choices rather than from a single generated specification. Some early answers were recorded as numeric option selections in conversation. Their lasting meaning is captured in the approved design and summarized here.

### 5.1 Scope

The skill is universal rather than tied to one industry. It should help with organizational, commercial, technical, public-sector, educational, nonprofit, and personal systems.

### 5.2 Interaction depth

The approved direction is adaptive Quick and Deep modes.

Quick mode serves reasonably clear, contained challenges and users who want immediate ideation. Deep mode serves ambiguous, systemic, contested, or consequential challenges and users who request rigor.

The mode can be selected automatically, but the user can override it. The user may request Quick, Deep, Provocation, fewer questions, more depth, comparison, expansion, or another pass.

### 5.3 Innovation portfolio

The portfolio should be balanced across sustaining, adjacent, disruptive, and constraint-removing possibilities when the problem supports that range. These are balance signals, not quotas.

A preservation-first or no-change conclusion is valid when novelty would create cost without meaningful value.

### 5.4 Research

Research is evidence-informed and capability-aware. The skill may research current facts, precedent, or transferable mechanisms when those would materially improve ideation and the host supports research.

The skill must still work offline. When research is unavailable, it should continue from supplied context and label assumptions rather than fail.

### 5.5 Discovery

Deep mode uses progressive discovery. It asks only questions whose answers can change the objective, system boundary, preservation requirements, constraints, reasoning approach, or evaluation criteria.

The approved maximum is seven focused questions, asked one at a time. Deep mode should stop earlier when it has enough information.

### 5.6 Challenge style

The default stance is constructive challenger. Provocation is available when useful or requested.

Provocation challenges assumptions, artificial boundaries, habitual ownership, legacy incentives, and default processes. It must not casually invert safety obligations, ethical duties, verified facts, or physical realities.

### 5.7 Output and decision support

The project resolved a difficult scope boundary as follows:

> The skill is ideation-first, with light decision support.

It can illuminate strategic fit, boldness, friction, upside, uncertainty, combinations, resistance, cooperation needs, and preservation risk. It must not automatically choose one winner.

Unless explicitly requested as a later phase, it must not produce implementation tasks, timelines, experiments, budgets, owners, technical architecture, rollout plans, or a final selection.

### 5.8 Provenance presentation

The default output should be concise and evidence-informed. It should not turn every session into an academic report. Detailed sourcing should remain available when the user requests it or when high-stakes accuracy requires it.

## 6. Current Behavioral Architecture

The approved workflow is:

1. Interpret the request and select Quick or Deep mode.
2. Establish an Innovation Brief.
3. Map the system, stuckness, existing strengths, and preservation requirements.
4. Select relevant Reasoning Cells.
5. Generate candidate mechanisms in differentiated passes.
6. Record and compare mechanisms in the mechanism ledger.
7. Cross-pollinate genuinely distinct mechanisms.
8. Stop when mechanism saturation is reached.
9. Add light receptivity and system-fit analysis.
10. Present the possibility portfolio progressively.

The output is called an **innovation possibility** until it has been implemented and has produced realized value. The skill does not claim that generated text is a completed innovation.

### 6.1 Innovation Brief

Every session establishes:

1. Desired change.
2. Beneficiary.
3. Current insufficiency.
4. Existing strengths.
5. Preservation requirements.
6. Nonnegotiable constraints.
7. Success signals.
8. Dominant frame.

Quick mode infers missing fields and labels important uncertainty. Deep mode asks only decision-relevant questions.

### 6.2 System and stuckness map

The map considers actors, beneficiaries, incentives, flows, authority, dependencies, delays, feedback, previous attempts, repeated patterns, real and assumed constraints, valuable constraints, hidden labor, burdens of change, leverage points, and neglected boundaries.

Simulated stakeholder reactions must never be presented as actual stakeholder research.

### 6.3 Perspective Council and Reasoning Cells

`Perspective Council` is the approved user-facing label. It is not a set of theatrical fictional experts.

Its behavior comes from explicit Reasoning Cells:

| Cell | Required transformation |
| --- | --- |
| System Dynamics | Change or exploit feedback, dependencies, delays, and leverage points |
| Human Value | Reconfigure needs, behavior, accessibility, trust, or participation |
| Operational Reality | Remove friction, bottlenecks, workarounds, and hidden labor |
| Boundary Reframing | Change the objective, scope, ownership, or assumed limits |
| Mechanism Transfer | Import a causal mechanism from a structurally relevant outside domain |
| Contrarian | Reverse one named assumption and trace the consequences |
| Futures | Change time, scale, scarcity, technology, or institutional conditions |

If independent subagents are available, selected cells may run in isolated contexts. If they are unavailable, one model performs sequential contrastive passes. The skill must describe this honestly and must not claim that sequential passes were independent agents.

### 6.4 Mechanism ledger

The ledger exists because different wording is not the same as different reasoning.

It records the mechanism family, intervention point, principal actor, changed flow, intended effect, variants, and origin.

A possibility counts as distinct only when it has a genuinely different causal mechanism or meaningful differences across at least two structural dimensions. Structural dimensions include actor, intervention point, resource flow, information flow, decision rights, incentives, timing, scale, value creation, and value delivery.

Changing nouns, interfaces, audiences, or industries alone does not make an idea distinct.

### 6.5 Saturation

Idea counts are targets rather than quotas.

Quick mode targets 10 to 15 distinct possibilities. Deep mode targets 15 to 24. A narrow problem may saturate below the target.

Generation stops when another targeted pass produces zero or one distinct mechanism after a transformation attempt. The model should explain that further candidates became variants rather than padding the portfolio.

### 6.6 Progressive disclosure

The approved output layers are:

1. Innovation Brief.
2. System Snapshot.
3. Complete Portfolio.
4. Five to seven Possibility Spotlights representing different signals, not finalists.
5. Connections and Tensions.
6. User-Directed Continuation.

This structure is intended to make a broad portfolio usable without collapsing it prematurely.

## 7. Important Rejected Directions

The following directions were considered or emerged as risks and were rejected:

1. **Generic brainstorm prompt:** Too easy to copy and insufficiently systematic.
2. **Author impersonation:** The skill should not claim to be Tudor Rickards or use authority theater.
3. **Persona theater:** Multiple voices are not valuable unless they perform measurably different transformations.
4. **Exact reconstructed Rickards framework:** The available research did not justify presenting reconstructed names, chapters, or sequences as verified fact.
5. **Mandatory web research:** This would break portability and offline usefulness.
6. **Mandatory subagents:** This would exclude many coding agents and confuse host capability with core behavior.
7. **One giant output:** This would make the skill exhausting and reduce practical value.
8. **Fixed idea quota:** This would reward filler and wording variants.
9. **Universal ranking and winner:** This would exceed the intended ideation scope and create false certainty.
10. **Automatic experiments and roadmap:** The user wanted ideation with some help deciding, not forced transition into implementation.
11. **Single composite innovation score:** This could hide weak relevance, poor safety, excess cost, or domain failures.
12. **Known-solution rediscovery as proof of innovation:** It measures mechanism recovery and may measure memorization. It is only one benchmark family.
13. **Self-judging as sufficient evidence:** LLM judges require blinding, order control, disagreement preservation, and human calibration.
14. **Claiming universal compatibility from Markdown format:** Format compatibility, installation testing, activation testing, and behavioral testing are separate claims.
15. **Viral naming detached from function:** The lasting public identity should be grounded in usefulness and evidence.

## 8. Portability and Installability

The skill must be installable or loadable in Claude Code, Codex, Cursor, Antigravity, Pi, and other coding agents.

The canonical package follows the open Agent Skills specification and uses a provider-neutral `SKILL.md` with conditional Markdown references.

The core skill must not require:

1. Web access.
2. Subagents.
3. Structured input tools.
4. Proprietary commands.
5. A particular model provider.
6. A particular operating system.
7. Executable scripts inside the installable skill.

Capability-aware fallbacks are mandatory. Native installation adapters may differ by host, but they must not become separate behavioral authorities.

The planned canonical skill package is:

```text
skills/systematic-innovation/
├── SKILL.md
└── references/
    ├── innovation-lenses.md
    ├── deep-mode.md
    ├── output-contract.md
    └── evidence.md
```

The benchmark remains outside the installable skill directory.

Compatibility claims must use evidence-based tiers:

1. Format-compatible.
2. Installation-tested.
3. Explicit-invocation-tested.
4. Automatic-activation-tested.
5. Behavior-tested.

## 9. Why the Benchmark Became a Major Subproject

The user did not want a skill that merely looked convincing in writing. The project needs evidence about what the skill changes, how much it changes, where it fails, and what extra cost it introduces.

The initial idea was a long loop-engineering phase that could run the skill repeatedly, preserve results, compare them, and quantify improvement or regression. The user suggested giving the AI questions whose solutions are already known to see whether the method helps recover them.

An LLM-benchmark-research audit found that a simple 100-prompt tournament would not be trustworthy. Major problems included benchmark contamination, memorization, judge bias, stochastic pseudoreplication, verbosity advantage, unequal information across conditions, hidden safety regressions, repeated tuning against held-out cases, and conflating model behavior with host integration.

The earlier benchmark concept was replaced with the audited design described below.

## 10. Benchmark Scientific Claims

The benchmark measures **systematic ideation performance**, not realized innovation.

It may support claims about:

1. Qualified useful distinct mechanisms.
2. Duplicate and genericity reduction.
3. Constraint responsiveness.
4. System and preservation awareness.
5. Mechanism recovery.
6. Human pairwise preference.
7. Efficiency in tokens, time, and cost.
8. Trigger precision and recall.
9. Host installation and activation behavior.

It cannot prove that a generated possibility is globally novel, commercially successful, ethically acceptable in deployment, or a realized innovation.

## 11. Benchmark Conditions and Corpus

The planned comparison conditions are:

1. Vanilla model.
2. Generic brainstorming prompt.
3. Format-matched control with comparable count, fields, and output budget.
4. Established systematic method.
5. Full skill.
6. Selected development-only ablations after the full treatment shows an effect.

The version 1 corpus contains exactly 100 cases:

| Family | Development | Validation | Sealed test | Total |
| --- | ---: | ---: | ---: | ---: |
| Synthetic mechanism spaces | 14 | 5 | 5 | 24 |
| Counterfactual rediscovery | 10 | 3 | 3 | 16 |
| Open-ended systemic challenges | 18 | 6 | 6 | 30 |
| Preservation and no-change | 6 | 2 | 2 | 10 |
| Trigger and scope boundaries | 6 | 2 | 2 | 10 |
| Adversarial and high-stakes | 6 | 2 | 2 | 10 |
| **Total** | **60** | **20** | **20** | **100** |

Only development cases enter the public repository. Validation and sealed-test prompts, hidden mechanisms, distractors, gold information, and private case notes remain outside the public repository.

If a restricted case influences development, it is retired and replaced. The sealed test is run once after the candidate and analysis plan are frozen.

## 12. Four Approved Benchmark Corrections

After reviewing the written implementation plans, the user required four explicit corrections. These decisions were later incorporated into and approved as part of the behavioral specification; the plans describe their execution but do not independently supersede the specification.

### 12.1 Controlled multi-turn benchmarking

Deep mode cannot be evaluated fairly only through single-turn prompts because its questioning is part of its behavior.

Controlled multi-turn cases therefore use a fixed ordered user-disclosure script. Every condition receives the same information in the same order and the same maximum number of assistant turns.

The final portfolio is scored for mechanism quality. Tokens, cost, and latency from every assistant turn count toward efficiency. This prevents the Deep condition from receiving extra information or hiding its questioning cost.

Quick cases remain single-turn.

### 12.2 Minimum quality gates before mechanisms count

A mechanism cannot enter the primary numerator merely because it is different.

Each candidate must pass:

1. Relevance at least 2 of 3.
2. Constraint alignment at least 2 of 3.
3. Causal clarity at least 2 of 3.
4. Plausibility at least 1 of 3.
5. No critical safety or rights violation.

The primary endpoint is paired change in qualified useful distinct mechanisms per 1,000 total assistant output tokens.

Raw extracted mechanisms, raw distinct families, qualified candidates, qualified distinct families, and gate failures must also be reported so the headline number cannot hide what happened.

### 12.3 Six-case and twelve-case feasibility stages

The study must not jump directly to the 60-case development run.

The six-case technical feasibility stage checks end-to-end execution, single-turn and multi-turn protocols, append-only storage, token accounting, redaction, resume behavior, judge job construction, and report generation.

The twelve-case measurement rehearsal checks rubric usability, judge disagreement, human-calibration workflow, preliminary variance, ceiling and floor effects, failure rates, and whether the primary metric behaves sensibly.

Only after both stages pass may the full public development study proceed.

### 12.4 Cross-agent validation before the final report

Cross-agent installation, explicit invocation, automatic activation where supported, reference loading, capability fallback, and compatibility claims must be tested before generating the final release report.

The final report must not claim broad cross-agent usefulness merely because the skill follows an open Markdown format.

## 13. Benchmark Evaluation and Analysis Rules

The benchmark uses deterministic checks, structured mechanism extraction, blinded LLM judging, and human calibration.

Key safeguards are:

1. Remove treatment, model, host, skill, and file identities from judge inputs.
2. Randomize answer order.
3. Judge both presentation orders for pairwise comparisons.
4. Use multiple judge families where practical.
5. Preserve disagreement, abstention, and inconsistency.
6. Require criterion-specific evidence.
7. Avoid relying mainly on the generator's model family as judge.
8. Calibrate automated judgments against blinded humans.
9. Use domain experts where general evaluators cannot assess usefulness.
10. Treat the case as the unit of analysis.
11. Aggregate stochastic repetitions within case and condition before resampling cases.
12. Preserve failures, refusals, timeouts, and malformed outputs as outcomes.
13. Choose repetition counts after pilot variance analysis rather than fixing them globally.
14. Report effect sizes, uncertainty, win/tie/loss, missingness, costs, and failures.
15. Report strata so an aggregate result cannot conceal a domain or safety failure.

Automated pairwise judging must reach at least 75 percent agreement with blinded human judgments and Krippendorff's alpha of at least 0.67 on the calibration sample before it can support headline claims. Otherwise, human judgment replaces it for headline results.

Automatic activation targets at least 0.90 precision and 0.85 recall on held-out trigger cases for each behavior-tested host.

At least three distinct agent or model families must be behavior-tested before a broad cross-agent release claim.

## 14. Provider-Neutral Runner and Loop Engineering

The runner is a provider-neutral Python package rather than a collection of provider SDK calls.

It supports:

1. Inbox and outbox JSONL exchange for any external tool that can read jobs and return standardized responses.
2. A constrained subprocess adapter for explicitly allowlisted local coding-agent CLIs.
3. Controlled turn-level conversation execution.
4. Dry runs.
5. Resuming interrupted work, including partial conversations.
6. Bounded retries.
7. Maximum calls and cost.
8. Concurrency limits.
9. Model allowlists.
10. Failure thresholds.
11. Credential redaction.
12. Append-only raw evidence.
13. Deterministic reports and reproducibility manifests.

The long-running external loop may execute approved benchmark jobs, score them, generate reports, and propose candidate changes on a separate branch. It must not overwrite a released skill, silently replace raw evidence, expose restricted cases, autonomously merge changes, or rerun the sealed test after seeing results.

## 15. Separate Studies That Must Not Be Conflated

The evaluation laboratory contains three distinct studies:

1. **Model behavior:** The same skill content is explicitly supplied in comparable model contexts.
2. **Host integration:** Installation, discovery, reference loading, and fallback behavior are tested in coding agents.
3. **Automatic activation:** Prompts do not name the skill, and trigger precision and recall are measured.

A result in one study cannot substitute for evidence in another.

## 16. Test-First Development Philosophy

The skill follows a behavioral RED, GREEN, REFACTOR sequence.

### RED

1. Create realistic scenarios before writing the skill.
2. Run them without the skill.
3. Preserve baseline outputs.
4. Score observable failures.
5. Identify actual genericity, duplication, scope, system, preservation, and attribution problems.

### GREEN

1. Write the minimum standards-compliant skill addressing observed failures.
2. Validate structure and references.
3. Run the same scenarios with the skill.
4. Confirm behavioral improvement rather than exact wording compliance.

### REFACTOR

1. Analyze new failure modes.
2. Tighten only guidance supported by evidence.
3. Optimize the trigger description against positive, negative, and boundary cases.
4. Preserve each candidate version and result set.

The benchmark runner uses code-level test-driven development as well.

## 17. Current Repository State

At the time this context was written, the repository contained documentation only.

Relevant commits were:

1. `2478e59 docs: specify systematic innovation skill and benchmark`
2. `31dd9f3 docs: plan systematic innovation implementation`
3. `063ae10 docs: strengthen benchmark execution gates`

The three implementation plans contain 36 tasks in total:

| Plan | Tasks | Purpose |
| --- | ---: | --- |
| Skill | 8 | RED pilot, skill validator, minimal skill, behavioral refinement, trigger optimization, documentation, and candidate verification |
| Benchmark runner | 13 | Typed records, case loading, planning, storage, inbox/outbox, controlled conversations, adapters, scoring, judging, statistics, reporting, CLI, and handoff |
| Benchmark study | 15 | Corpus, restricted pack, preregistration, calibration, six-case stage, twelve-case stage, development, validation, cross-agent study, sealed test, report, and external loop handoff |

No skill package, benchmark package, corpus, tests, CI workflow, release artifact, or public compatibility claim had been implemented.

The last known branch was `main`, and the worktree was clean before this context file was added.

## 18. Repository Maturity Inquiry

The project owner wants the public repository to mature continuously like a serious long-lived software project. Repository quality should be present in the foundation rather than added cosmetically before release.

Two repositories were identified as references.

### 18.1 Private `clief-notes-method` repository

Reference:

`https://github.com/poferraz/clief-notes-method`

The repository is privately owned by the project owner. A partial authenticated inspection observed:

```text
.agents/rules/
.github/workflows/
docs/
legacy/
sources/
src/
tasks/
tests/
tools/
.gitignore
AGENTS.md
CLAUDE.md
LICENSE
README.md
bun.lock
package.json
tsconfig.json
```

Its README described four generated skills implementing an ICM operating lifecycle:

1. `clief-init`
2. `clief-audit`
3. `clief-apply`
4. `clief-code-security`

Observed structural ideas included:

1. `src/` is the only editable authority.
2. `dist/` is generated and disposable.
3. Build, validation, type checking, and tests are distinct commands.
4. Generated skills install to several supported coding-agent locations.
5. `sources/` contains protected study material and does not enter distributions.
6. `legacy/` preserves retired work for traceability without making it active authority.
7. Root agent instructions and host adapters point toward a canonical operating context.
8. Fixtures and runtime smoke tests validate generated skills.

The private repository was not fully audited during the original conversation because the authenticated cloud session did not remain available across subpages and a second authentication request was declined. A future local session with repository access must inspect the full tree and actual files before proposing an adaptation.

Do not treat the partial observations above as a complete framework specification. Do not copy private content into the public project. Extract reusable structural principles in original language.

### 18.2 Prime Agent repository

Reference:

`https://github.com/PrimeIntellect-ai/prime-agent`

Public inspection identified mature engineering patterns including:

1. Root `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `README.md`, and license documentation.
2. Pull-request and issue templates.
3. GitHub workflows for CI, contributions, changelog fragments, release builds, and scheduled stress tests.
4. Dependency automation.
5. Focused contribution rules and exact local validation commands.
6. Changelog fragments for reviewable release history.
7. Safe multi-agent Git practices.
8. Continual small evidence-backed improvements with recorded state and rollback.

The target is comparable engineering discipline and public-repository trust, not identical tooling, superficial badges, popularity metrics, or a copy of Prime Agent's TypeScript architecture.

## 19. Historical Repository Architecture Questions

No fourth repository-quality plan has been approved or created.

The following questions were recorded before the full repository investigation. They are preserved as decision history. The 2026-09-01 approval described in section 19.1 resolves the architectural questions; exact implementation mechanics remain deferred until the written specification is approved and coordinated planning begins.

1. Which `clief-notes-method` conventions should become canonical in this repository?
2. Should the project use one editable skill authority and generated per-host distributions?
3. Which host adapters are necessary, and which would create avoidable maintenance?
4. How should folder structure route fresh agents without becoming documentation bureaucracy?
5. Which project-state and handoff documents should be durable?
6. How should a fresh-agent walk test work?
7. What GitHub governance is appropriate before the project has external contributors?
8. Which quality checks should block merges at each project phase?
9. Should the repository use explicit maturity levels, and if so, how can they resist score gaming?
10. How should quality regressions, exceptions, dependency updates, releases, and benchmark-driven improvements be ratcheted?
11. How should the repository coordinate Python benchmark tooling with any distribution-building tooling?
12. Which GitHub security features are free and portable, and which require documented fallbacks?

These questions required investigation, alternatives, tradeoff analysis, and owner approval before a specification or implementation plan could be written. That architectural investigation is now complete; no implementation plan has yet been authorized.

### 19.1 Approved Repository Architecture Direction (2026-09-01)

The owner approved **Approach B: canonical core plus evidence shell**, together with three explicit decisions:

1. `skills/systematic-innovation/` remains the one editable behavioral authority.
2. A host adapter is created only after a demonstrated host-specific installation, discovery, activation, or behavioral delta shows that the canonical skill is insufficient.
3. The prior Git history should be recovered before implementation begins rather than casually starting a new repository lineage.

The approved approach places deterministic validation, release packaging, compatibility evidence, and repository governance around the canonical skill without making those mechanisms competing sources of behavior. Generated artifacts are derived and drift-checked; direct installation of the canonical skill remains the default.

It also establishes three trust zones with different security needs:

1. the public skill, safe to publish and load;
2. the public benchmark laboratory, which contains executable tooling and public development evidence; and
3. the restricted evaluation pack, kept outside public Git and automatic agent context.

Compatibility is an evidence matrix rather than a binary badge or ordered ladder. Claims must report format conformance, installation, discovery, explicit activation, automatic activation, and behavioral conformance independently. Repository quality uses independent gates rather than a composite maturity score, and GitHub controls are added when the protected workflow or risk exists.

The approach deliberately rejects duplicated project-state documentation, default per-host copies, premature archives and governance ceremony, and any use of restricted evaluation evidence for ordinary skill refinement.

The reasoning is that this is the smallest architecture that combines provider neutrality with credible evidence and public-repository discipline. It transfers useful reference principles without copying private text or adopting the project-specific machinery of either reference repository.

The written form of this direction is `docs/superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md`. Following independent audit and correction, the owner approved the written specification on 2026-09-01. Coordinated implementation planning is now authorized; implementation remains a later phase with its own approval gate.

### 19.2 Git Lineage Recovery (2026-09-01)

The prior Git lineage was recovered from the owner-provided `systematic-innovation-session.bundle`. Git verified that the bundle is complete and internally valid. The recovered `main` branch contains four commits and ends at `648b62621d6a0eb5ac24685ca861f9928dca0006` (`docs: preserve systematic innovation context`).

The history was attached without checking out or overwriting the working tree. The approved Approach B context update and draft repository-architecture specification remained intact as working changes. The bundle itself remains an untracked recovery artifact and should not be committed.

No upstream remote was encoded by the bundle or invented during recovery. An `origin` should be configured only when the owner identifies or creates the intended public repository. This recovery resolves the third decision in section 19.1; implementation is no longer blocked by missing local Git history.

### 19.3 Independent Architecture Audit and Approved Corrections (2026-09-01)

The owner requested a fresh, independent audit of the draft repository-architecture specification. The audited draft had SHA-256 digest `24f4369283404955110511439b86a4aac964b24427fc140504b12a68732d79dc`. The review found that Approach B remained sound but the written contract required six corrections before approval:

1. Compatibility dimensions are independent and cannot be represented honestly as one ordered ladder.
2. Keeping restricted evidence outside Git is necessary but insufficient without trusted execution, provider handling, storage, retention, and audit controls.
3. Plans must be explicitly subordinate to specifications and cannot amend them through supersession language.
4. Development, restricted-validation, and sealed-test evidence need exact and different feedback permissions.
5. Release digests and reproducibility do not establish authentic origin without verifiable provenance.
6. Architecture acceptance needs explicit evidence and pass conditions rather than subjective completion language.

The owner approved correcting all six findings. The draft specification was revised accordingly while preserving Approach B, provider neutrality, the benchmark's scientific design, and the three-plan review boundary.

The revised contract uses a compatibility evidence matrix; a fail-closed restricted-run preflight tied to a frozen reviewed runner and declared custody policy; explicit specification-over-plan authority; development-only diagnostic feedback with validation as a release decision and sealed testing as terminal; reproducible and authenticated releases; and an architecture acceptance-evidence table.

The behavioral specification and three existing plans were not modified during this correction. Their known contract and terminology conflicts must be surfaced during coordinated planning, and any required specification amendment must be approved before the affected execution work proceeds. The owner approved the revised written specification on 2026-09-01, closing the repository-architecture specification gate and authorizing coordinated planning subject to the specification-over-plan authority rule.

### 19.4 Behavioral Contract Reconciliation and Approval (2026-09-01)

The coordinated-planning preflight confirmed that all three existing plans contain amendment language claiming to supersede conflicting benchmark provisions in the behavioral specification. Under the approved repository-architecture authority model, a plan cannot perform that role.

The underlying benchmark decisions were already explicitly owner-approved and recorded in sections 12.1 through 12.4 of this file. They were therefore incorporated into a consolidated draft amendment of `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md` for written review:

1. controlled multi-turn Deep cases with fixed disclosures, final-portfolio scoring, and all-turn efficiency accounting;
2. the qualified-mechanism primary endpoint and exact minimum quality gates;
3. six-case technical feasibility and twelve-case measurement rehearsal before the full public development study;
4. cross-agent validation before a broad cross-agent final release report; and
5. the compatibility matrix and restricted-evidence feedback and execution boundaries required by the approved repository architecture.

The three implementation plans were not edited during the 2026-09-01 amendment commit, and were subsequently updated in the working tree alongside `docs/superpowers/plans/2026-09-01-systematic-innovation-coordinated-implementation.md`.

### 19.5 Primary-Source Verification, Quantitative Benchmark Audit, and Phase 1 Authorization (2026-10-17)

On 2026-10-17, the owner requested a comprehensive audit of the approved specifications and plans alongside deep research into Tudor Rickards's book, the methodology, empirical LLM ideation literature (2024–2026), and quantitative benchmarking methods.

The audit identified four actionable improvements, all of which the owner explicitly approved on 2026-10-17:

1. **Primary-source enrichment from the scanned 1985 book (`Ideas in Action - Stimulating Innovation - Tudor Rickards.pdf`):** Incorporate the verified nine-chapter bibliographic structure and figures in `references/evidence.md`; Rickards's three problem-owner questions (p. 160), his mission-orientated versus negotiative versus participative boundary-overflow modes (pp. 159–163), and *Yes-but* inoculation (p. 159) in `references/output-contract.md`; and initial fluency depletion (Rickards 1975, 1978), multiple redefinition modes, and synectic excursions in `references/innovation-lenses.md`.
2. **Fix for free-text string-tuple mechanism deduplication:** Replace naive raw-string tuple equality alone with normalized structural signatures plus semantic/equivalence clustering so free-text phrasing variations of the same causal mechanism do not artificially inflate distinct-mechanism counts.
3. **Judge-free mathematical diversity and ground-truth recovery metrics:** Report the Vendi Score ($\text{VS}_k$, eigenvalue entropy of the mechanism similarity kernel, Friedman & Dieng 2023) and duplicate collapse ratio as judge-free mathematical diversity measures, and use one-to-one bipartite Hungarian matching for hidden-mechanism recovery in synthetic and counterfactual-rediscovery cases so multiple paraphrases of one known mechanism cannot inflate recall.
4. **Phased execution to produce empirical numbers early:** Authorize immediate execution of Phase 1 (aligning and committing specifications/plans, establishing root authority routing, building the 12-case RED/GREEN pilot corpus and skill validator, running the no-skill RED baseline and format-matched control, authoring `skills/systematic-innovation/`, and running the GREEN evaluation to report paired quantitative numbers).

## 20. Current Repository-Quality Intent

Before the architecture decision, the owner's intent established the following constraints; the approved direction in section 19.1 now gives them architectural form:

1. Bring the useful operating principles of `clief-notes-method` into `systematic-innovation`.
2. Make the repository understandable to coding agents without relying on lost conversation context.
3. Maintain one clear authority for editable content.
4. Separate generated artifacts, source research, restricted benchmark material, active work, and history.
5. Make installation across coding agents testable rather than aspirational.
6. Apply excellent GitHub practices throughout the build.
7. Reach a public-repository maturity comparable to respected agent projects.
8. Imprint a continuous quality loop into the project foundation.
9. Use evidence and regression gates rather than vanity scoring.
10. Allow the repository to improve continually after the first release.

The approved direction preserves this intent while rejecting unsuitable patterns from both reference repositories.

## 21. Historical Instructions for the Repository Design Session

The repository design session was instructed not to begin with a predetermined list of files to create.

It was required to:

1. Read this context, the approved specification, and all three implementation plans.
2. Inspect the complete private `clief-notes-method` repository locally.
3. Inspect the current Prime Agent repository and current GitHub best practices using primary sources.
4. Discover the skills available in the coding-agent environment.
5. Use every skill that materially improves investigation, architecture, security, planning, or validation.
6. Avoid invoking irrelevant skills simply to maximize skill count.
7. Explain the structural principles found in each reference and why they work.
8. Identify conflicts, duplication, overengineering risks, and portability concerns.
9. Present two or three viable adaptation approaches with tradeoffs.
10. Recommend one approach and explain why it fits this project now.
11. Obtain explicit owner approval before editing the design specification, creating a repository-quality specification, writing a fourth implementation plan, or implementing files.

The first deliverable of that session was a reasoned recommendation, not a construction checklist.

### 21.1 Outcome of the 2026-09-01 and 2026-10-17 Sessions

The 2026-09-01 session inspected the complete local Clief Notes Method repository, the current Prime Agent repository, current primary GitHub and Agent Skills guidance, and the existing project contract and plans. It separated observed practices from transferable principles, presented three adaptation approaches, and recommended Approach B.

The owner approved Approach B and the three decisions recorded in section 19.1, approved correcting all six findings from the independent audit recorded in section 19.3, approved the revised written repository-architecture specification, and approved the consolidated behavioral amendment recorded in section 19.4. On 2026-10-17, following the primary-source book scan and quantitative benchmark audit recorded in sections 4.5 and 19.5, the owner approved the primary-source and quantitative benchmark amendments and authorized Phase 1 implementation.

## 22. Change Control for This Context

Update this file when:

1. The project purpose materially changes.
2. A design decision is approved, rejected, or superseded.
3. New evidence changes an attribution or provenance boundary.
4. A major audit changes the benchmark or release standard.
5. Repository architecture is approved.
6. Implementation or evaluation reaches a major phase gate.
7. A released compatibility or performance claim is added or withdrawn.

When updating it:

1. Preserve the reason for the old decision rather than deleting history.
2. Mark the old direction as superseded.
3. Link the new specification, plan, decision record, evidence, or commit.
4. Keep restricted benchmark content and copyrighted source text out of this file.
5. Do not turn this document into a task tracker.

The objective is durable understanding with minimal duplication: context here, requirements in specifications, executable steps in plans, decisions in version control, and empirical claims in benchmark evidence.
