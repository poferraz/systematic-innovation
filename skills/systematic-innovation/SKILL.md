---
name: systematic-innovation
description: Use when a user wants non-obvious ideas, systemic alternatives, assumption challenges, or ways out of a persistent tradeoff without breaking what already works. Do not use for factual lookup, debugging a known bug, or implementing an already-chosen solution.
---

# Systematic Innovation

## Core Principle

Genuine innovation requires **causally distinct mechanisms** connected to **systemic realities and human receptivity**—not surface-noun variations of the same default trope. Every possibility must change *how* the system produces outcomes while protecting what already works.

## When Not to Trigger

Do **not** run this workflow when the user asks for:
- Factual definitions, historical explanations, or textbook comparisons (answer directly).
- Debugging, root-cause diagnosis of a specific technical defect, or performance micro-benchmarks.
- Implementation artifacts for an already-selected solution (such as database schemas, sprint tickets, or code).

## Mode Routing (Quick vs. Deep)

Route automatically using observable signals in the user's request unless the user explicitly overrides the mode:

| Route | Observable Prompt Signals | Behavior |
| :--- | :--- | :--- |
| **Quick Mode** | Single-actor personal system, bounded feature or operational bottleneck, explicit request for immediate options or a single lens (e.g., `"Use Provocation mode"`), or user says `"skip questions"` / `"give me ideas now"`. | Build a compact Innovation Brief and System & Preservation Scan from the prompt, run 3–4 Reasoning Cells after initial fluency depletion, and deliver **4–6 causally distinct possibilities** in one turn. |
| **Deep Mode** | Multi-stakeholder organizational, civic, educational, or cross-departmental system where hidden incentives, unstated preservation boundaries, or competing goals govern whether any idea can survive. | Run the System & Preservation Scan, ask **up to 7 high-leverage discovery questions** paired with **2–3 contrasting provisional seeds** (unless the user instructs to produce the final portfolio now), and synthesize **6–9 causally distinct possibilities** once context is disclosed. |

### User Overrides
- `"Use Quick mode"`, `"skip questions"`, or `"Produce your final portfolio now"` $\rightarrow$ skip further questions and output the complete portfolio immediately.
- `"Use Deep mode"` $\rightarrow$ run progressive discovery before locking the portfolio.
- `"Use Provocation mode"` $\rightarrow$ include Cell F (Provocation & Movement) as a primary generator with explicit safety and feasibility extraction.

## The Innovation Brief & Preservation Scan

Before generating possibilities, establish five brief fields (explicitly in Deep Mode; concisely in Quick Mode):

1. **Perceived Mess vs. Operational Tension:** What symptom is being reported versus what structural conflict keeps recreating it?
2. **System Actors & Boundary Overflows:** Who owns the problem, who bears the friction, and which adjacent teams or external actors are affected?
3. **Preservation Inventory (What Works & Must Remain):** Which existing incentives, statutory reviews, safety/privacy floors, or cultural strengths must **not** be broken?
4. **Unlocked Levers vs. Hard Constraints:** What can be re-sequenced, re-bundled, or inverted within current budget, staffing, and legal guardrails?
5. **Initial Fluency Depletion (Memory-Dump Quarantine):** List the 2–3 most obvious default tropes for this domain and set them aside so the portfolio explores non-obvious causal mechanisms.

## Reasoning Cell Selection & Mechanism Ledger

Select **3–5 Reasoning Cells** matched to the tension (see [innovation-lenses.md](references/innovation-lenses.md)):
- **Cell A:** Reframing & Boundary Shift (Multiple Redefinition Modes)
- **Cell B:** Preservation & Inversion
- **Cell C:** Contradiction & Resource Reuse
- **Cell D:** Morphological Combination
- **Cell E:** Far-Domain Analogy & Synectic Excursions
- **Cell F:** Provocation & Movement (`Po`)
- **Cell G:** Failure, Misuse & Adoption Critics

### Distinctiveness & Saturation Rules
1. Track every candidate in an explicit **Mechanism Ledger** across four structural dimensions:
   - **Changed Variable / Object**
   - **Causal Lever Type** (e.g., temporal inversion, boundary re-partition, incentive unbundling, physical poka-yoke, subtraction/sunset, information schema unification, peer/ecosystem co-production)
   - **Timing / Stage of Action** (upstream pre-condition, point-of-action, in-transit, post-event audit)
   - **Feedback Loop Altered**
2. **Duplicate Test:** If two ideas use the same causal lever at the same stage with different nouns or channels (e.g., a QR code flyer, a shelf tag, and a checkout card all signaling donor need at a store), **merge them into one mechanism family**.
3. **Saturation Stop:** Stop adding options as soon as additional candidates repeat an existing ledger mechanism. Four genuinely distinct mechanisms beat eight padded variations.

## Ideation-Only & High-Stakes Guardrails

- **No Premature Winner or Implementation Drift:** Keep the portfolio open. Do **not** append unrequested 30-60-90 day rollout roadmaps, Gantt schedules, sprint backlogs, or database schemas. End with small **1–2 week learning probes** instead.
- **No Fabricated Statistics:** Never invent quantitative percentages or effect sizes inside examples. Label causal predictions as testable hypotheses.
- **High-Stakes Safety Floor:** Never propose bypassing statutory life-safety reviews, child/student safeguarding, medical dosing safety, or patron/user privacy.

## Reference Navigation

Read the following reference files conditionally based on the active phase of work:
- Read [innovation-lenses.md](references/innovation-lenses.md) when selecting Reasoning Cells, applying initial fluency depletion, running multiple redefinition or synectic excursions, or deduplicating the Mechanism Ledger.
- Read [deep-mode.md](references/deep-mode.md) when an organizational or multi-stakeholder challenge triggers Deep Mode progressive questioning or when handling mid-stream context disclosures.
- Read [output-contract.md](references/output-contract.md) when formatting the six-layer response, evaluating Rickards's Three Problem-Owner Questions, routing across Mission-Orientated / Negotiative / Participative boundary modes, or inoculating against *Yes-but* rejection.
- Read [evidence.md](references/evidence.md) when explaining the methodological provenance, citing Tudor Rickards (1985), or distinguishing verified principles from adapted AI structures.
