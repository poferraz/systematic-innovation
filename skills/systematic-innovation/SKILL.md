---
name: systematic-innovation
version: "2.0.0"
description: Use when users need non-obvious, causally distinct ideas or systemic reframing without breaking what works. Not for bugs, facts, or coding.
license: MIT
metadata:
  author: systematic-innovation maintainers
  tags:
    - ideation
    - systems-thinking
    - creativity
    - problem-solving
---

# Systematic Innovation

## Purpose

Generate **causally distinct innovation possibilities** grounded in system dynamics and human receptivity—never surface-noun variations of the same modal trope. Every candidate must alter *how* the system produces outcomes while separating protected **invariants** (*what* must remain intact) from replaceable **legacy delivery vehicles** (*which* habit, role, or artifact carries it today).

**Do not trigger** when the user asks for:
- Factual definitions, textbook explanations, or neutral comparisons (answer directly).
- Debugging, root-cause fault localization, or code-level optimization.
- Implementation artifacts for an already-selected design (schemas, sprint backlogs, production code).
- Evading audits, concealing safety or regulatory findings, or weakening statutory, privacy, or medical safeguards. Refuse evasion intent; offer compliant exploration only if the user explicitly pivots to compliant goals.

## Prerequisites

- **Zero runtime dependencies:** Works completely **offline** in a single text session by explicitly labeling material assumptions.
- **Host capability awareness:** When the **host provides** web search, workspace read, or isolated subagent tools and current facts or external mechanisms would materially strengthen ideation, use them without fabricating sources or claiming sequential passes were independent agents.

## Instructions

### 1. Mode Routing, Channel Precedence & Budget Lock

Select Quick or Deep Mode from observable signals unless explicitly overridden:

| Route | Observable Signals | Behavior |
| :--- | :--- | :--- |
| **Quick Mode** | Bounded bottleneck, single-actor system, single-turn/API channel, explicit request for immediate options, or `"skip questions"` / `"give me ideas now"`. | Build a compact Innovation Brief and System & Preservation Scan from supplied context, run System Dynamics plus two selected Reasoning Cells after trope quarantine, and deliver **10 to 15 distinct possibilities** in one turn (ask at most one clarifying question if an interactive reply is available and a critical unknown blocks meaningful generation). |
| **Deep Mode** | An interactive multi-turn channel is open **and** multiple stakeholders hold conflicting incentives, ambiguous ownership, or fragile preservation boundaries. | Map the system, ask **one question at a time** (maximum 7 total) paired with **2–3 contrasting provisional seeds**, then synthesize **15 to 24 distinct possibilities** once constraints stabilize. |

**Execution-Channel Precedence:**
1. Explicit user overrides have highest precedence (`"Use Quick mode"`, `"Use Deep mode"`, `"Use Provocation mode"`, `"skip questions"`, `"Produce your final portfolio now"`).
2. On any single-turn, one-shot, or API channel with no user reply available, emit the complete portfolio immediately with labeled assumptions in Layer 1—even for complex multi-stakeholder requests or `"Use Deep mode"` prompts.
3. Deep Turn-1 discovery restraint is valid only when an interactive reply path actually exists.

**Hard Output Budget Precedence:**
- An explicit word or token ceiling overrides default target counts and formatting. Aim for **80% of the requested ceiling**, count every whitespace-delimited token (including labels, pipes `|`, and arrows `->`), and cut prose before dropping distinct mechanisms.
- For ceilings of **500 words or fewer**, use colon-keyed Piped Compact Syntax (`L1:`, `L2:`, `P1:`..`Pn:`, `L4:`, `L5:`, `L6:`) from [output-contract.md](references/output-contract.md) with hard token caps: keep `L1:` + `L2:` combined in `<= 45` whitespace words (never expand all eight brief labels separately), keep each `P1..Pn` line at **<= 38 whitespace tokens** using `A→B→C` and `Preserve: all L1` (always retaining `Lever:`, `Intervention:`, `Chain:`, `Preserve:`, `Failure:`, `Fit:`), keep `L4:` + `L5:` + `L6:` combined `<= 45` words, and cap candidate breadth at **3 to 4** entries (`<= 350` words) or **4 to 5** entries (`351–500` words)—never attempt 10–15 inside `<= 500` words.
- Count total whitespace tokens before sending; if above 85% of ceiling, shorten prose or drop trailing entries and mark **budget-limited** rather than exceeding the limit.

### 2. Innovation Brief, Preservation & Negative-Space Trope Quarantine

Establish all eight Innovation Brief fields concisely (infer and label unknowns in Quick Mode; probe high-value unknowns in Deep Mode):
1. **Desired change:** Outcome that must shift.
2. **Beneficiary:** Who experiences the improvement.
3. **Current insufficiency:** Recurring symptom and underlying tension.
4. **Existing strengths:** Working assets to protect.
5. **Preservation requirements:** Non-negotiable values, service floors, and **legacy delivery vehicle** distinctions.
6. **Nonnegotiable constraints:** Binding budget, staff, authority, safety, legal, and physical limits.
7. **Success signals:** Observable markers (mark inferred metrics explicitly).
8. **Dominant frame:** Default mental model keeping the system stuck.

**Two-Stage Anti-Typicality Protocol:**
1. **Negative-Space Trope Quarantine:** Explicitly name the 2–3 highest-probability modal tropes in Layer 1 and exclude them from the numbered portfolio. Reject any draft candidate that shares a core mechanism or verb-object dynamic with a quarantined trope.
2. **Tail-Distribution Exploration:** Draw possibilities across distinct conditional regions of the solution space rather than rewording one cluster near the mode.

**Cumulative `Preserve:` Ledger:** Track every invariant from Turn 1 onward across multi-turn sessions. When a new turn conflicts with an earlier boundary or provisional seed, surface the conflict and retire or repair affected candidates by inspecting their causal chain and actual resource demands.

### 3. Reasoning Cells, Excursions & Receptivity

Quick Mode runs **System Dynamics plus two selected Reasoning Cells**; Deep Mode runs **five or six selected Reasoning Cells**:
- **System Dynamics:** Reshape feedback, delays, accumulation, or high-impact control points.
- **Human Value:** Rework dignity, trust, effort distribution, accessibility, or participation.
- **Operational Reality:** Cut handoff waste, bottlenecks, hidden labor, or idle byproducts without undisclosed resources.
- **Boundary Reframing:** Shift objective, ownership, decision rights, or assumed scope.
- **Mechanism Transfer:** Map a two-node abstract causal or dependency structure from another domain, stripping source jargon before generating the candidate.
- **Contrarian:** Reverse a named assumption (**Provocation mode requires Contrarian and Boundary Reframing** as primary generators; always convert raw provocations into safe, constraint-compliant operations).
- **Futures:** Stress mechanisms under shifted scale, scarcity, regulation, or coordination regimes.

**Ledger, Duplicate Test, Field Consistency & Saturation:**
- Every candidate in Layer 3 must explicitly include the verbatim field keys **`Intervention point:`** (or compact `Intervention:`), **`Causal lever:`** (or compact `Lever:`), **`Causal chain:`** (or compact `Chain:`), and **`Preserve check:`** (or compact `Preserve:`)—never rename `Causal lever:` to bare `Mechanism:` or omit `Preserve check:`.
- Compare underlying causal operation and structural coordinates (actor, control point, flows, timing, incentives, feedback)—never treat shared lever labels alone as equivalence or different synonyms as distinction.
- **Clustered Variety Floor:** On non-budget-limited runs, explore at least five distinct causal clusters across two or more Reasoning Cells before stopping on saturation (hard word ceilings override this floor). These counts remain **targets, not quotas**; stop after a targeted pass adds zero or one new mechanism (or earlier if genuinely domain-saturated).
- **Dual Selling-In / Selling-Out & Three Questions:** Evaluate each spotlighted possibility on internal **Selling-In** value/risk, external **Selling-Out** value, Rickards's Three Problem-Owner Questions, boundary mode, and a specific causal *Yes-but* safeguard.

### Reference Navigation

Load detailed reference files only when needed:
- [innovation-lenses.md](references/innovation-lenses.md): Negative-Space Trope Quarantine, 2x2 morphological forcing, Liability-to-Asset Reversal, two-node Mechanism Transfer, and Currie invariant audits.
- [deep-mode.md](references/deep-mode.md): One-question-at-a-time progressive discovery, 7-question cap, contrasting Turn-1/2 seeds, and invariant-vs-vehicle probes.
- [output-contract.md](references/output-contract.md): Full Layers 1–6 templates, `<= 500`-word Piped Compact Syntax, Selling-In/Selling-Out spotlights, boundary re-anchors, and explicit-request experiments.
- [evidence.md](references/evidence.md): Audited Tudor Rickards (1985) bibliography/pagination and verified diversity literature boundaries.

## Examples

Compact `<= 350`-word piped response (counts ~100 words; zero invented stats):

```text
L1: Cut clinic no-shows | Preserve: continuity of care, zero added clinical staff (separate reminder vehicle) | Quarantine: SMS reminders, late fees
L2: Rigid intake queues collide with shared rural transit.
L3:
P1: Pre-Visit Micro-Swap | Lever: temporal batch | Intervention: booking desk | Chain: Open feed→paired neighbor fills slot→idle chairs fall | Preserve: all L1 | Failure: thin rural density | Fit: negotiative—opt-in only
P2: Async Arrival Slip | Lever: boundary separation | Intervention: intake packet | Chain: Pre-transit history→pre-slot review→wait bottleneck drops | Preserve: all L1 | Failure: literacy barrier | Fit: mission—oral phone kept
L4: P1 (Selling-In: uses desk; Selling-Out: predictable rides); P2 (Selling-In: cuts backlog; Selling-Out: shorter wait).
L5: P1+P2 combine; P2 needs oral fallback.
L6: Budget-limited (2 of 10-15). Expand P1/P2 or request probes?
```

Deep Mode Turn-1 discovery structure: emit 2–3 brief contrasting structural seeds first, then ask one non-batched decision-relevant question targeting preservation invariants vs. legacy vehicles.

## Limitations

- **Ideation-Only Boundary:** Keep options open; never declare an automatic winner, invent percentages/effect sizes, or emit unrequested rollout schedules, sprint backlogs, database schemas, or experiments. Only when the user explicitly requests experiments, emit 1–3 reversible probes with quantitative disconfirmation thresholds, sample bounds, horizons, and fallback moves.
- **High-Stakes Floor:** Outputs on medical, legal, financial, or safety-critical domains remain **exploratory** with explicit **verification needs** and never relax life-safety, privacy, or child/patient protections.
- **Methodological Scope:** Designed to widen causally distinct ideation options, not guarantee commercial adoption or substitute for domain engineering validation.

## Troubleshooting

| Error / Edge Case | Cause | Solution |
| :--- | :--- | :--- |
| **Overconstrained impossibility** (`fake compliance` risk) | Requirements conflict physically, logically, or legally without valid slack. | Trigger `Contradiction & Boundary Re-Anchor`: state **no compliant candidate exists**, name the exact conflict, and list minimal decision-owner relaxations outside `P1..Pn`. |
| **Tight word ceiling overrun** (`<= 500` words) | Full Layers 1–6 headers and prose exceed the explicit word cap. | Switch immediately to the `Compact Portfolio Template` piped syntax, allocate `15% / 50% / 15% / 20%` word budgets beforehand, target 80% of ceiling, and mark **budget-limited**. |
| **Channel / mode conflict** | Prompt signals organizational complexity or requests Deep Mode on a single-turn API call. | Apply **Execution-Channel Precedence**: output a complete Quick-structured portfolio now with labeled assumptions rather than stalling on unanswered questions. |
| **Modal trope repetition** | Drafts paraphrase one obvious mechanism across nouns/channels. | Re-run Negative-Space Trope Quarantine, strip nouns into two-node causal graphs, and force a 2x2 Reasoning Cell crossing across at least five causal clusters. |
