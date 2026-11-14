---
name: systematic-innovation
description: Use when a user wants non-obvious ideas, systemic alternatives, assumption challenges, or ways out of a persistent tradeoff without breaking what already works. Do not use for factual lookup, debugging a known bug, or implementing an already-chosen solution.
---

# Systematic Innovation

## Core Principle

Genuine innovation requires **causally distinct mechanisms** connected to **systemic realities and human receptivity**—not surface-noun variations of the same default trope. Every possibility must change *how* the system produces outcomes while protecting what already works. When the host provides web or workspace research tools and current precedent would materially improve ideation, use them; remain fully functional offline by labeling material assumptions.

## When Not to Trigger

Do **not** run this workflow when the user asks for:
- Factual definitions, historical explanations, or textbook comparisons (answer directly).
- Debugging, root-cause diagnosis of a specific technical defect, or performance micro-benchmarks.
- Implementation artifacts for an already-selected solution (such as database schemas, sprint tickets, or code).
- Evading audits, hiding safety/regulatory findings, avoiding detection, or breaking statutory, privacy, life-safety, or medical-safety obligations. Refuse the bypass intent; offer compliant alternatives only if the user explicitly changes the target.

## Mode Routing (Quick vs. Deep)

Route automatically using observable signals in the user's request unless the user explicitly overrides the mode:

| Route | Observable Prompt Signals | Behavior |
| :--- | :--- | :--- |
| **Quick Mode** | Single-actor personal system, bounded feature or operational bottleneck, one-turn/single-turn/API execution, explicit request for immediate options or a single lens, or user says `"skip questions"` / `"give me ideas now"`. | Build a compact Innovation Brief and System & Preservation Scan from the prompt, run System Dynamics plus two selected Reasoning Cells after initial fluency depletion, and target **10 to 15 distinct possibilities** in one turn (if an interactive reply is available, ask at most one question only when a critical unknown would make generation meaningless). |
| **Deep Mode** | An actual interactive multi-turn channel is available, and a multi-stakeholder organizational, civic, educational, or cross-departmental system has hidden incentives, unstated preservation boundaries, or competing goals. | Run the System & Preservation Scan, ask **one question at a time** (never more than seven total) paired with **2–3 contrasting provisional seeds**, then synthesize **15 to 24 distinct possibilities** once context is disclosed. |

### Execution-Channel Precedence

1. An explicit user override has the highest precedence.
2. If the request must be answered in one turn—single-turn, one-shot, API response, immediate output, or no user reply is available—deliver a complete portfolio now even when the substantive problem is complex. Record unresolved assumptions in Layer 1 and do not stall in discovery questions.
3. Deep Turn-1 restraint is valid only when the actual channel permits a user reply or the user explicitly requests progressive discovery. Never infer it from organizational, civic, or cross-domain complexity alone.
4. If the user requests Deep Mode but only one response is available, produce the complete portfolio with an explicit assumption and preservation ledger.

### Hard Output Budget Precedence

A requested maximum word or token budget overrides normal candidate counts and formatting. Target **80% of the requested ceiling**, and for a word ceiling of 500 or fewer use the `Compact Portfolio Template` in [output-contract.md](references/output-contract.md). Do not add introductions, explanations, or formatting that consume the budget.

Choose the number of entries from that word allowance before drafting. If normal breadth plus essential fields cannot fit, explicitly label the portfolio **budget-limited** and give fewer complete possibilities. The count target never authorizes a word-limit overrun; fewer under an explicit user budget is different from mechanism saturation.

### User Overrides
- `"Use Quick mode"`, `"skip questions"`, or `"Produce your final portfolio now"` $\rightarrow$ skip further questions and output the complete portfolio immediately.
- `"Use Deep mode"` $\rightarrow$ run progressive discovery before locking the portfolio.
- `"Use Provocation mode"` $\rightarrow$ **Provocation mode requires Contrarian and Boundary Reframing** as primary generators with explicit safety and feasibility extraction.

## The Innovation Brief & Preservation Scan

Establish all eight Innovation Brief fields, inferring and labelling material unknowns in Quick Mode and asking only decision-relevant questions in Deep Mode. Combine fields in concise prose rather than repeating them in multiple inventories:

1. **Desired change:** What should become meaningfully different?
2. **Beneficiary:** Who should experience that difference?
3. **Current insufficiency:** What symptom and structural tension keep recurring?
4. **Existing strengths:** What already works?
5. **Preservation requirements:** What must not be lost?
6. **Nonnegotiable constraints:** Which resource, authority, safety, privacy, or physical limits bind?
7. **Success signals:** What observable change would matter? Label inferred signals.
8. **Dominant frame:** How is the problem currently understood?

Map actors, incentives, flows, boundary overflows, dependencies, delays, failed approaches, burdens of change, and leverage points. Quarantine the 2–3 most obvious default tropes before structural generation. Stakeholder reactions are hypotheses, never invented research.

### Preservation Across Turns

Carry forward a cumulative `Preserve:` ledger of every explicit invariant, including earlier user turns. Later examples, seeds, convenience, or silence never revoke it. When a new disclosure conflicts with a seed, withdraw or revise that seed and recheck every final candidate against the cumulative ledger. If a later request would weaken safety, rights, or physical constraints, surface the conflict rather than silently replacing the earlier boundary.

## Reasoning Cell Selection & Mechanism Ledger

Quick Mode uses **System Dynamics plus two selected Reasoning Cells**. Deep Mode uses **five or six selected Reasoning Cells** matched to the tension (see [innovation-lenses.md](references/innovation-lenses.md)):

- **System Dynamics:** Change feedback, dependencies, delays, or leverage points.
- **Human Value:** Reconfigure needs, behavior, accessibility, trust, dignity, or participation.
- **Operational Reality:** Remove friction, bottlenecks, workarounds, or hidden labor.
- **Boundary Reframing:** Change the objective, scope, ownership, or assumed limits.
- **Mechanism Transfer:** Import a causal mechanism from a structurally relevant outside domain.
- **Contrarian:** Reverse one named assumption and trace the consequences.
- **Futures:** Change time, scale, scarcity, technology, or institutional conditions.

### Distinctiveness & Saturation Rules
1. Maintain a **Mechanism Ledger** recording mechanism family, intervention point, principal actor, changed flow, intended effect, variants, and origin (cell and lens). Compare causal operation and structural coordinates, including timing, decision rights, incentives, scale, and feedback. Portfolio fields can carry these coordinates without a second printed ledger.
2. **Duplicate Test:** A possibility is distinct if its causal mechanism is genuinely different, or if at least two structural dimensions differ meaningfully. Shared lever labels or stages alone do not establish equivalence. Merge actual wording/channel variants (such as QR flyers and shelf tags conveying the same donor-need signal), preserving genuinely different operations even when their labels match.
3. **Saturation Stop:** These are targets, not quotas. Stop adding options after a targeted transformation pass yields zero or one new mechanism; if a narrow problem saturates below the target, say so rather than padding variants.

## Ideation-Only & High-Stakes Guardrails

- **No Premature Winner or Implementation Drift:** Keep the portfolio open. Do **not** append unrequested 30-60-90 day rollout roadmaps, Gantt schedules, sprint backlogs, database schemas, pilots, or experiments. Only when the user explicitly requests experiments, provide bounded, falsifiable probes.
- **No Fabricated Statistics:** Never invent quantitative percentages or effect sizes inside examples. Label causal predictions as testable hypotheses.
- **High-Stakes Safety Floor:** Never propose bypassing statutory life-safety reviews, child/student safeguarding, medical dosing safety, or patron/user privacy. For medical, legal, financial, security, and other high-stakes topics, label outputs exploratory and state verification needs explicitly.
- **Physical/Logical Constraint Floor:** If stated constraints are jointly impossible, identify the contradiction and re-anchor the boundary. Never manufacture fake compliance by inventing inventory, authority, energy paths, legal exceptions, or hidden mechanisms.

## Reference Navigation

Read the following reference files conditionally based on the active phase of work:
- Read [innovation-lenses.md](references/innovation-lenses.md) when selecting Reasoning Cells, applying initial fluency depletion, running multiple redefinition or synectic excursions, or deduplicating the Mechanism Ledger.
- Read [deep-mode.md](references/deep-mode.md) when an organizational or multi-stakeholder challenge triggers Deep Mode progressive questioning or when handling mid-stream context disclosures.
- Read [output-contract.md](references/output-contract.md) when formatting the six-layer response, evaluating Rickards's Three Problem-Owner Questions, routing across Mission-Orientated / Negotiative / Participative boundary modes, or inoculating against *Yes-but* rejection.
- Read [evidence.md](references/evidence.md) when explaining the methodological provenance, citing Tudor Rickards (1985), or distinguishing verified principles from adapted AI structures.
