# Systematic Innovation Skill and Benchmark Design

**Date:** 2026-08-31  
**Status:** Approved design, pending implementation plan  
**Project:** `systematic-innovation`

## 1. Summary

`systematic-innovation` is a portable Agent Skill for producing meaningfully different innovation possibilities from business, technology, product, service, operational, educational, government, nonprofit, and personal challenges.

The skill addresses a recurring weakness in ordinary LLM brainstorming: plausible but generic ideas, repeated causal mechanisms disguised with different wording, premature selection, insufficient system awareness, and novelty pursued without regard for what already works.

The skill combines:

1. Verified systemic innovation principles associated with Tudor Rickards and later innovation literature.
2. Established creative problem-solving methods such as reframing, assumption reversal, analogy, morphological recombination, and constraint transformation.
3. Original AI-native mechanisms including adaptive mode routing, Reasoning Cells, a mechanism ledger, saturation detection, and progressive portfolio disclosure.

The project also includes a provider-neutral evaluation laboratory. The laboratory measures whether the skill improves systematic ideation relative to fair controls across models and agent hosts. It does not claim to measure real-world innovation directly.

## 2. Goals

The project must:

1. Help an LLM escape conventional or repetitive responses.
2. Frame innovation as a systemic, purpose-connected activity rather than raw novelty generation.
3. Generate diverse possibilities distinguished by causal mechanism.
4. Preserve valuable elements of the current system.
5. Offer Quick and Deep interaction modes with automatic routing and user override.
6. Provide light decision support without choosing a winner.
7. Remain useful without web access, subagents, or proprietary tools.
8. Install in coding agents that support the open Agent Skills specification.
9. Remain usable through direct Markdown loading in agents without native skill discovery.
10. Produce evidence about its behavioral effect through repeatable, versioned benchmarks.

## 3. Non-goals

The initial skill does not:

1. Implement ideas, produce roadmaps, assign owners, estimate budgets, or design experiments unless the user explicitly requests a later phase.
2. Claim that generated ideas are completed innovations.
3. Select a universal winner from the portfolio.
4. Simulate stakeholder evidence or claim that fictional perspectives represent real people.
5. Claim global or historical novelty.
6. Reproduce copyrighted source text.
7. Present reconstructed framework names or chapter structures as verified Rickards terminology.
8. Depend on a particular model provider, coding agent, operating system, or subagent interface.
9. Treat a single composite benchmark number as proof of innovation.

## 4. Evidence and Provenance

The skill uses three provenance classes.

### 4.1 Verified principles

These are principles supported by reliable sources:

1. Innovation is systemic rather than exclusively individual.
2. Mental stuckness and habitual framing obstruct creative progress.
3. Problem reframing should precede solution generation.
4. Creative thinking interacts with organizational context and climate.
5. Divergent exploration and convergent evaluation serve different purposes.
6. Meaningful innovation connects to a clear purpose, need, or performance objective.
7. Existing strengths and legitimate constraints should not be discarded merely to appear novel.

### 4.2 Adapted methods

The skill may use established methods with accurate attribution when detailed provenance is requested:

1. Objective laddering and reframing.
2. Assumption reversal.
3. Morphological recombination.
4. Synectics and analogy.
5. Constraint transformation.
6. Feedback and leverage analysis.
7. Stakeholder and incentive analysis.
8. Sustaining and disruptive innovation distinctions.

### 4.3 Original AI mechanisms

The following are project-original behavioral mechanisms:

1. Quick and Deep routing.
2. The Perspective Council presentation layer.
3. Reasoning Cells as explicit cognitive operators.
4. The mechanism ledger.
5. Mechanism-level duplicate detection.
6. Saturation-based stopping.
7. Progressive output disclosure.
8. Cross-agent capability fallback.

Normal user output shows concise method labels. Detailed sources are provided on request. The internal evidence reference must separate verified claims, adapted methods, and original mechanisms.

## 5. Core Behavioral Architecture

The workflow is:

1. Interpret the request and select Quick or Deep mode.
2. Establish an Innovation Brief.
3. Map the system, stuckness, existing strengths, and preservation requirements.
4. Select relevant Reasoning Cells.
5. Generate candidate mechanisms in differentiated passes.
6. Record and compare mechanisms in the ledger.
7. Cross-pollinate distinct mechanisms.
8. Stop when mechanism saturation is reached.
9. Add light receptivity and system-fit analysis.
10. Present the possibility portfolio progressively.

The skill calls its outputs **innovation possibilities** until implementation and realized value have occurred.

## 6. Mode Routing

### 6.1 Quick mode

Quick mode applies when the challenge is reasonably clear, consequences are contained, sufficient context exists, or the user requests immediate ideation.

Quick mode:

1. Restates the challenge as an innovation question.
2. Infers the Innovation Brief and labels material assumptions.
3. Asks one question only when a critical unknown would make generation meaningless.
4. Uses System Dynamics plus two selected Reasoning Cells.
5. Targets 10 to 15 distinct possibilities.
6. Provides a compact portfolio and selected spotlights.

### 6.2 Deep mode

Deep mode applies when the challenge is ambiguous, systemic, contested, high consequence, involves several interacting problems, or the user requests rigorous exploration.

Deep mode:

1. Begins with a provisional interpretation.
2. May ask up to seven focused questions, one at a time. Three to seven is the normal range for a genuinely ambiguous challenge, but the mode stops earlier when sufficient.
3. Asks a question only when the answer can change the objective, system boundary, preservation needs, cell selection, constraints, or evaluation criteria.
4. Introduces several contrasting provisional seeds during questioning to provide value without anchoring on a single idea.
5. Uses five or six selected Reasoning Cells.
6. Targets 15 to 24 distinct possibilities.
7. Provides a fuller system map and portfolio.

### 6.3 User control

The user can override routing with requests including:

1. Quick mode.
2. Deep mode.
3. Provocation mode.
4. Skip the questions.
5. Go deeper.
6. Compare selected possibilities.
7. Expand a particular possibility.

## 7. Innovation Brief

Every session establishes:

1. **Desired change:** What should become meaningfully different?
2. **Beneficiary:** Who should experience that difference?
3. **Current insufficiency:** Why is the present approach inadequate?
4. **Existing strengths:** What already works?
5. **Preservation requirements:** What must not be lost?
6. **Nonnegotiable constraints:** Which boundaries are real?
7. **Success signals:** What would indicate that the change matters?
8. **Dominant frame:** How is the problem currently understood?

Quick mode infers missing fields and marks uncertainty. Deep mode asks only decision-relevant questions.

## 8. System and Stuckness Map

The system snapshot considers:

1. Actors and beneficiaries.
2. Incentives and disincentives.
3. Resource, information, authority, and value flows.
4. Dependencies, delays, and feedback.
5. Existing strengths and capabilities.
6. Previous attempts and repeated failure patterns.
7. Real, assumed, negotiable, and self-imposed constraints.
8. Beneficial constraints that serve safety, ethics, trust, quality, or stability.
9. People who would carry the burden of change.
10. Leverage points and neglected boundaries.

The skill does not present simulated stakeholder reactions as research evidence.

## 9. Perspective Council and Reasoning Cells

“Perspective Council” is the user-facing presentation. Its internal behavior uses explicit Reasoning Cells rather than fictional personalities.

| Reasoning Cell | Required transformation |
| --- | --- |
| System Dynamics | Change or exploit feedback, dependencies, delays, and leverage points |
| Human Value | Reconfigure needs, behavior, accessibility, trust, or participation |
| Operational Reality | Remove friction, bottlenecks, workarounds, and hidden labor |
| Boundary Reframing | Change the objective, scope, ownership, or assumed limits |
| Mechanism Transfer | Import a causal mechanism from a structurally relevant outside domain |
| Contrarian | Reverse one named assumption and trace the consequences |
| Futures | Change time, scale, scarcity, technology, or institutional conditions |

Each selected cell produces:

1. Two to four candidate mechanisms.
2. The intervention point being changed.
3. A concise cause-and-effect explanation.
4. A distinction from mechanisms already present.

When separate agents are available, cells may operate in isolated contexts. Otherwise, one model performs sequential contrastive passes and delays synthesis until selected passes are complete. The skill never claims sequential passes were genuinely independent.

Provocation mode requires Contrarian and Boundary Reframing. It challenges assumptions, habits, artificial boundaries, legacy incentives, and default ownership. It does not casually invert safety requirements, ethical obligations, verified facts, or physical realities.

## 10. Innovation Lenses

Cells select from these operators as appropriate:

1. Objective reframing.
2. System and feedback analysis.
3. Constraint removal, inversion, exploitation, or redesign.
4. Assumption reversal.
5. Morphological recombination.
6. Analogy and mechanism transfer.
7. Stakeholder or decision-right inversion.
8. Temporal transformation.
9. Scale transformation.
10. Subtraction.

Lenses are selected for the challenge rather than used as a mandatory checklist.

## 11. Mechanism Ledger

The ledger tracks:

| Field | Meaning |
| --- | --- |
| Mechanism family | Short causal label |
| Intervention point | Where the system changes |
| Principal actor | Who behaves or decides differently |
| Changed flow | Information, resources, incentives, authority, value, or timing |
| Intended effect | How value is created or protected |
| Variants | Ideas sharing the underlying mechanism |
| Origin | Cell and lens that produced it |

A new idea must have either:

1. A genuinely different causal mechanism, or
2. Meaningful differences across at least two structural dimensions.

Structural dimensions include actor, intervention point, resource flow, information flow, decision rights, incentive structure, timing, scale, value creation, and value delivery.

Changing nouns, interfaces, audiences, or industries alone does not create a distinct idea. Duplicates are merged, transformed, or identified as variants.

## 12. Saturation and Portfolio Balance

Idea counts are targets, not quotas.

Generation occurs in batches. After each batch, the ledger checks how many new mechanism families were added. Generation stops when a new pass produces zero or one distinct mechanism after one targeted transformation attempt.

If a narrow challenge saturates below the target, the skill explains that additional candidates became variants and does not pad the portfolio.

Possibilities may be tagged as:

1. Sustaining.
2. Adjacent.
3. Disruptive.
4. Constraint removal.

These tags support balance but are not quotas. A “no change” or preservation-first conclusion is valid when novelty would add cost without meaningful benefit.

## 13. Progressive Output Contract

### 13.1 Layer 1: Innovation Brief

A concise statement of purpose, assumptions, constraints, and preservation requirements.

### 13.2 Layer 2: System Snapshot

Actors, incentives, dependencies, existing strengths, failed approaches, constraints, and leverage points.

### 13.3 Layer 3: Complete Portfolio

Every possibility contains, compactly:

1. A memorable name.
2. Its core mechanism.
3. Intended value.
4. Portfolio category.
5. Originating lens.
6. Main uncertainty.
7. A concise system-fit note.

### 13.4 Layer 4: Possibility Spotlights

Five to seven possibilities receive fuller development. The selection represents different signals rather than finalists:

1. Strongest strategic fit.
2. Boldest departure.
3. Lowest structural friction.
4. Highest potential upside.
5. Most important uncertainty.
6. Best hybrid.
7. Most revealing reframing.

### 13.5 Layer 5: Connections and Tensions

The skill identifies compatible combinations, mutually exclusive approaches, shared dependencies, conflicting assumptions, and possibilities that could form a broader system.

### 13.6 Layer 6: User-Directed Continuation

The user may expand, compare, combine, challenge, or generate another cell pass. No implementation roadmap appears automatically.

## 14. Receptivity and Light Decision Support

Every possibility receives a concise note covering:

1. Required cooperation.
2. Principal resistance.
3. Preservation risk.
4. Major unknown.

Spotlighted possibilities may additionally identify supporting and opposing incentives, structural dependencies, required capabilities, burdens of change, negative externalities, and existing strengths used or protected.

The skill may identify several different signals, including strongest fit, boldest departure, lowest friction, highest upside, highest uncertainty, and best combination candidate. It does not aggregate these into a universal ranking or declare a winner.

Evaluation labels are provisional and accompanied by reasons. Stakeholder responses and feasibility remain hypotheses until externally validated.

Unless requested, the skill does not provide implementation tasks, timelines, experiments, budgets, assigned owners, technical architecture, rollout plans, or final selection.

For medical, legal, financial, security, and other high-stakes topics, outputs remain exploratory and verification needs are explicit.

## 15. Research and Capability Awareness

The skill may use research when current facts, domain mechanisms, or precedent would materially improve ideation and the host provides appropriate tools. It remains fully functional offline and labels assumptions.

| Capability | Available behavior | Fallback behavior |
| --- | --- | --- |
| Subagents | Run selected cells in isolated contexts | Use sequential contrastive passes |
| Web research | Verify facts and collect external mechanisms | Continue from supplied context and label assumptions |
| Structured user-input tool | Present choices | Ask one plain-language question |
| File creation | Save a requested portfolio | Return the portfolio in chat |
| Long context | Load conditional references | Use the compact core workflow |

The skill contains no required proprietary commands or tool names.

## 16. Discovery and Portability

The canonical package follows the open Agent Skills specification. The final description must be optimized through trigger evaluation rather than finalized before baseline testing.

It should activate for requests involving:

1. Escaping conventional or repetitive ideas.
2. Generating meaningfully different approaches.
3. Reframing persistent problems.
4. Discovering opportunities across systems.
5. Challenging assumptions.
6. Producing diverse possibility portfolios.
7. Exploring sustaining and transformative change.

It should not activate for ordinary implementation, routine debugging, fact retrieval, cosmetic writing variations, simple option comparison, or roadmap execution without ideation.

The public repository uses this layout:

```text
systematic-innovation/
├── skills/
│   └── systematic-innovation/
│       ├── SKILL.md
│       └── references/
│           ├── innovation-lenses.md
│           ├── deep-mode.md
│           ├── output-contract.md
│           └── evidence.md
├── benchmark/
├── docs/
├── README.md
├── LICENSE
└── SECURITY.md
```

The benchmark remains outside the installable skill directory. Installation commands are documented only after being verified against current installers.

## 17. Benchmark Purpose and Claims

The benchmark measures **systematic ideation performance**, not realized innovation.

It has three separate studies:

1. **Model behavior study:** Explicitly provide the same skill content in comparable model contexts.
2. **Host integration study:** Test installation, discovery, reference loading, and capability fallback in coding agents.
3. **Automatic activation study:** Present prompts without naming the skill and measure activation precision and recall.

Results from these studies are not combined as though model and host effects were interchangeable.

## 18. Benchmark Experimental Conditions

The benchmark supports:

1. **Vanilla model:** No creativity method.
2. **Generic brainstorming:** A conventional creativity request.
3. **Format-matched control:** The same count, fields, and approximate output budget without the skill's distinctive mechanisms.
4. **Established-method baseline:** At least one recognized systematic method such as SCAMPER, conventional Creative Problem Solving, or morphological analysis.
5. **Full skill:** The complete treatment.
6. **Selected ablations:** Development-only experiments removing the ledger, Reasoning Cells, system map, preservation check, saturation detection, or cross-pollination.

Ablations are run only after the full treatment demonstrates an effect. They use the development set unless a later confirmatory ablation study is preregistered.

All comparisons use comparable prompts, model versions, output budgets, and model parameters where controllable.

## 19. Benchmark Cases and Splits

The initial benchmark contains 100 cases:

| Family | Public development | Restricted validation | Sealed test | Total |
| --- | ---: | ---: | ---: | ---: |
| Synthetic mechanism spaces | 14 | 5 | 5 | 24 |
| Counterfactual rediscovery | 10 | 3 | 3 | 16 |
| Open-ended systemic challenges | 18 | 6 | 6 | 30 |
| Preservation and no-change cases | 6 | 2 | 2 | 10 |
| Trigger and scope boundaries | 6 | 2 | 2 | 10 |
| Adversarial and high-stakes cases | 6 | 2 | 2 | 10 |
| **Total** | **60** | **20** | **20** | **100** |

Cases are stratified across domain, expected mode, ambiguity, constraint severity, stakeholder complexity, solution-space openness, opportunity type, and domain-knowledge requirements.

The public repository contains only development cases. Validation and sealed test prompts, hidden mechanisms, and human-calibration cases remain in a restricted evaluation pack. Once a restricted case influences development, it is retired and replaced.

The 100-case suite is version 1 evidence, not proof of universal improvement.

## 20. Counterfactual Rediscovery

Known-answer cases measure rediscovery or mechanism recovery, not innovation itself.

They include:

1. Historical cases, explicitly labeled contamination-prone.
2. Isomorphic fictional cases with names and recognizable details removed.
3. Synthetic mechanism spaces with multiple valid hidden mechanisms.

Scoring distinguishes:

1. Full hidden-mechanism recovery.
2. Partial recovery.
3. Valid alternative mechanism.
4. Relevant but weak mechanism.
5. Invalid or irrelevant output.

Valid alternatives receive credit and review. Failure to reproduce the expected wording is not failure.

## 21. Benchmark Outcomes

### 21.1 Primary endpoint

The primary endpoint is:

> Paired change in useful distinct mechanisms per 1,000 output tokens.

A mechanism is useful when it is causally distinct, relevant, sufficiently explained, compatible with stated constraints, and potentially valuable.

### 21.2 Confirmatory secondary endpoints

1. Total distinct mechanism count.
2. Useful mechanism proportion.
3. Duplicate reduction.
4. Genericity reduction.
5. Constraint responsiveness.
6. System awareness.
7. Preservation awareness.
8. Ideation-scope compliance.
9. Hidden-mechanism recovery.
10. Human pairwise preference.

### 21.3 Exploratory endpoints

1. Receptivity analysis.
2. Cross-domain transfer.
3. Provocation quality.
4. Combination quality.
5. Question usefulness.
6. Performance by agent host.

### 21.4 Efficiency endpoints

1. Useful mechanisms per 1,000 tokens.
2. Useful mechanisms per minute.
3. Useful mechanisms per dollar when cost data are available.
4. Human-rated value per 1,000 tokens.
5. Question burden before the first useful output.

An optional composite dashboard may be reported only with preregistered weights and sensitivity analysis. It is never the primary scientific result.

## 22. Judging and Human Calibration

Evaluation uses four layers.

### 22.1 Deterministic checks

Record completion, required fields, idea counts, token use, latency, scope violations, hidden identifiers, errors, and metadata.

### 22.2 Structured mechanism extraction

Normalize each candidate into intervention point, actor, changed flow, causal mechanism, intended effect, and principal constraint. Semantic clustering assists but does not decide mechanism identity alone.

### 22.3 Blind LLM judging

1. Remove treatment and model identities.
2. Normalize presentation where practical.
3. Randomize answer order.
4. Judge both presentation orders for pairwise comparisons.
5. Use multiple judge families.
6. Avoid relying primarily on the generating model family as judge.
7. Require criterion-specific evidence.
8. Preserve disagreement.

### 22.4 Human calibration

A stratified sample receives blind human evaluation. Specialized cases use domain experts where general evaluators cannot assess usefulness. The study measures agreement between automated and human judgments. Automated judgments cannot support the main claim when calibration is inadequate.

Novelty is reported as within-run novelty or reference-relative novelty. The benchmark does not claim global novelty.

## 23. Statistical Analysis

The analysis plan is frozen before the sealed test.

1. Run a pilot to estimate variance and choose repetition counts.
2. Use paired comparisons within cases.
3. Cluster or bootstrap uncertainty at the case level.
4. Treat model family and domain as crossed factors when the sample supports it.
5. Report effect sizes, confidence intervals, and win/tie/loss rates.
6. Preserve refusals, timeouts, and malformed outputs as outcomes.
7. Avoid response-level pseudoreplication.
8. Report each stratum so aggregate performance cannot conceal domain failures.
9. Preregister primary and confirmatory endpoints, exclusions, judge aggregation, and release criteria.

The number of repetitions is chosen after pilot variance analysis rather than fixed at three.

## 24. Evaluation Engineering Loop

The loop is:

1. Define constructs, controls, rubric, and analysis plan.
2. Freeze benchmark version and public development set.
3. Run and preserve a 10-to-12-case no-skill RED pilot.
4. Build the minimum skill that addresses observed failures.
5. Iterate only on the public development set.
6. Calibrate judges against blinded humans.
7. Run restricted validation when development gates pass.
8. Revise on development data when validation fails.
9. Freeze a release candidate and analysis plan.
10. Run the sealed test once.
11. Publish results, limitations, costs, and failures.
12. Retire any sealed cases that become development inputs.

Candidate revisions never silently replace the released skill. Each candidate has its own version, Git commit, and result set.

## 25. Provider-Neutral Runner and Handoff

The benchmark runner supports:

1. **Adapter mode:** A small adapter invokes an API or coding-agent CLI and returns a standardized result.
2. **Inbox/outbox mode:** The runner creates JSONL jobs that any external tool can process and return as standardized JSONL responses.

The handoff guide explains environment validation, dry runs, controls, resume behavior, raw-output preservation, scoring, report generation, candidate changes, sealed-test protection, and stopping conditions.

The runner records:

1. Benchmark and runner versions.
2. Case ID and split.
3. Experimental condition.
4. Skill version and Git commit.
5. Agent host and model identifier.
6. Model parameters where exposed.
7. Prompt hash and raw prompt.
8. Raw response.
9. Tokens, cost, and latency when available.
10. Judge outputs and deterministic measurements.
11. Aggregate scores and errors.
12. Timestamp.

Raw results are append-only. The runner supports maximum calls, maximum cost, concurrency limits, a model allowlist, bounded retries, failure thresholds, resume behavior, credential redaction, dry runs, and development-only mode.

## 26. Security and Privacy

The skill itself requires no executable scripts or credentials. The benchmark runner must:

1. Never include credentials in prompts, results, logs, or reports.
2. Treat third-party skill content and benchmark inputs as untrusted.
3. Avoid executing instructions embedded in benchmark cases.
4. Constrain filesystem writes to configured result directories.
5. Use explicit allowlists for executable adapters.
6. Preserve raw evidence while redacting secrets.
7. Stop when configured cost, failure, or retry limits are reached.

## 27. Test-First Delivery Sequence

The implementation follows skill-oriented RED, GREEN, REFACTOR:

### RED

1. Create realistic baseline scenarios.
2. Run them without the skill.
3. Preserve outputs and score observed failures.
4. Identify actual genericity, duplication, scope, system, and attribution failures.

### GREEN

1. Create the minimal standards-compliant skill addressing observed failures.
2. Validate its structure and relative references.
3. Re-run the same scenarios with the skill.
4. Confirm behavioral improvement rather than exact wording.

### REFACTOR

1. Analyze new failure modes.
2. Tighten only guidance supported by observed failures.
3. Optimize the trigger description against should-trigger and should-not-trigger cases.
4. Re-run until release gates pass.

The provider-neutral benchmark runner also follows code-level test-driven development.

## 28. Acceptance Criteria

Before restricted validation, the analysis plan freezes the minimum practically important improvement for the primary endpoint and practical-equivalence margins for relevance, usability, factual integrity, and high-stakes restraint. Those values are derived from the pilot scale and variance and cannot be changed after validation results are seen.

Automatic activation must reach at least 0.90 precision and 0.85 recall on held-out trigger cases for each behavior-tested host. Explicit invocation must activate the skill in every valid explicit-invocation case. At least three distinct agent or model families must be behavior-tested before a broad cross-agent release claim.

Automated pairwise judging must reach at least 75 percent agreement with blinded human judgments and Krippendorff's alpha of at least 0.67 on the calibration sample. If it does not, human judgments replace automated judgments for headline claims.

The initial release is ready when:

1. The skill conforms to the open Agent Skills specification.
2. Quick, Deep, Provocation, and explicit override behavior pass behavioral tests.
3. The model distinguishes mechanisms rather than wording variants.
4. The skill preserves existing strengths and meaningful constraints.
5. Ideation-only scenarios do not drift into implementation planning or forced selection.
6. Evidence tests contain no false Rickards attribution.
7. Offline and no-subagent fallbacks remain useful.
8. Trigger precision and recall meet the stated release thresholds across tested hosts.
9. The full skill improves the primary endpoint over the format-matched control on the preregistered evaluation.
10. It does not materially regress relevance, usability, factual integrity, or high-stakes restraint.
11. Human calibration supports the automated judging method used for headline claims.
12. Benchmark reports disclose efficiency, uncertainty, limitations, and failed cases.
13. Compatibility claims distinguish behavior-tested, installation-tested, and format-compatible agents.

## 29. Delivery Phases

1. Formal implementation plan.
2. Baseline RED scenario and result capture.
3. Minimal portable skill.
4. Skill validation and behavioral refinement.
5. Public development benchmark.
6. Provider-neutral runner.
7. Judge calibration workflow.
8. Restricted evaluation-pack format.
9. Cross-agent installation and activation checks.
10. External-tool handoff package.
11. Release report based on preregistered evidence.

## 30. Key Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Persona theater without different reasoning | Use explicit Reasoning Cell transformations |
| Semantically repeated ideas | Maintain a mechanism ledger and structural distinctiveness test |
| Output quantity creates filler | Use saturation-based stopping |
| Novelty damages valuable existing behavior | Require preservation and no-change analysis |
| Skill output becomes overwhelming | Use progressive disclosure |
| LLM self-evaluation appears authoritative | Use provisional labels, blind judges, and human calibration |
| Longer outputs win benchmarks | Match budgets and normalize primary outcome by tokens |
| Known-answer cases measure memorization | Prefer fictional isomorphs and synthetic mechanism spaces |
| Public benchmarks become contaminated | Keep validation and sealed tests restricted and refresh them |
| Repeated tuning overfits the benchmark | Separate development, validation, and one-time sealed testing |
| Agent and model effects are conflated | Run separate behavior, integration, and activation studies |
| Autonomous loops overwrite good versions | Version every candidate and require release gates |
| Universal compatibility is overstated | Publish tiered, evidence-based compatibility claims |

## 31. Sources Guiding the Design

1. [Agent Skills specification](https://agentskills.io/specification)
2. [Agent Skills evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills)
3. [Agent Skills trigger optimization](https://agentskills.io/skill-creation/optimizing-descriptions)
4. [Tudor Rickards, *Stimulating Innovation: A Systems Approach/View* bibliographic record](https://catalogue.nla.gov.au/catalog/467386)
5. [William Kingston review in *Prometheus*](https://www.prometheusjournal.co.uk/prometheus/stimulating-innovation-frances-pinter-ltd-london-1985-pp-xi-221-15-00-isbn-0-86187-512-5/)
6. [Generative AI enhances individual creativity but reduces collective diversity](https://www.science.org/doi/10.1126/sciadv.adn5290)
7. [Can LLMs Generate Novel Research Ideas?](https://arxiv.org/abs/2409.04109)
8. [Personas in System Prompts Do Not Improve Performances of LLMs](https://aclanthology.org/2024.findings-emnlp.888/)
9. [Principled Personas](https://aclanthology.org/2025.emnlp-main.1364/)
10. [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685)
11. [LiveBench](https://arxiv.org/abs/2406.19314)
12. [LiveIdeaBench](https://arxiv.org/abs/2412.17596)
