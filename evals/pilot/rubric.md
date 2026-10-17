# Systematic Innovation Pilot Rubric

## 1. Purpose

This rubric scores observable behavior in the 12-case RED/GREEN pilot. It applies identically to no-skill (`vanilla`), `format-matched` control, and `full-skill` (`systematic-innovation`) runs.

## 2. Candidate Mechanism Extraction & Minimum Quality Gates

Before any candidate idea is counted as a **qualified useful mechanism**, extract its structural tuple:

- `intervention_point`: Where in the system the change occurs
- `principal_actor`: Who decides or behaves differently
- `changed_flow`: Which resource, information, incentive, authority, value, or timing flow changes
- `causal_operation`: How the intervention produces the change
- `intended_effect`: What value is created or preserved

Score each extracted candidate on four 0–3 anchored criteria and one binary safety gate:

| Gate Criterion | 0 | 1 | 2 (Minimum Pass, except Plausibility $\ge 1$) | 3 |
| :--- | :--- | :--- | :--- | :--- |
| **Relevance** | Off-topic or ignores the stated challenge | Tangentially related to the challenge | Directly addresses the desired change for the beneficiary | Addresses the core systemic bottleneck and desired change with high precision |
| **Constraint Alignment** | Violates an explicit non-negotiable or preservation constraint | Ignores a stated constraint without mitigation | Respects all stated budget, staffing, privacy, and preservation constraints | Exploits or works creatively within hard constraints while protecting existing strengths |
| **Causal Clarity** | Vague buzzword or slogan ("use AI", "improve culture") | Names an action without explaining how it changes system behavior | States a clear cause-and-effect mechanism (intervention $\to$ flow change $\to$ effect) | Articulates a complete causal chain, feedback effect, and boundary condition |
| **Plausibility** | Physically, legally, or logically impossible | Plausible in principle under explicit assumptions (Minimum Pass $\ge 1$) | Plausible with moderate coordination or adjustment | Immediately actionable with existing or stated resources |

**Critical Safety / Rights Violation (Binary):** Any mechanism that weakens statutory safety, clinical safety, patron privacy, safeguarding, or fundamental rights fails (`critical_safety_violation: true`).

**Conjunctive Gate Rule:** A candidate mechanism is **qualified** if and only if:
- `relevance >= 2`
- `constraint_alignment >= 2`
- `causal_clarity >= 2`
- `plausibility >= 1`
- `critical_safety_violation == false`

## 3. Mechanism Deduplication, Equivalence Clustering & Vendi Score

A duplicate is the same underlying causal mechanism presented with changed surface nouns, interfaces, audiences, or industries.

1. **Equivalence Clustering:** Two candidates belong to the same mechanism family unless they have a genuinely different causal operation or differ meaningfully across at least two structural dimensions (`actor`, `intervention_point`, `resource_flow`, `information_flow`, `decision_rights`, `incentive_structure`, `timing`, `scale`, `value_creation`, `value_delivery`). Free-text paraphrases of the same intervention and flow are merged into one family.
2. **Primary Endpoint:**
   $$\text{Primary Efficiency} = 1000 \times \frac{\text{Qualified Distinct Mechanism Families}}{\text{Total Assistant Output Tokens (All Turns)}}$$
3. **Judge-Free Vendi Score ($\text{VS}_k$):**
   Compute the $n \times n$ normalized similarity matrix $K$ over extracted candidate mechanism tuples and report $\text{VS}_k = \exp(-\sum_{i=1}^n \lambda_i \log \lambda_i)$, where $\lambda_i$ are the eigenvalues of $K/n$, alongside the **Duplicate Collapse Ratio** ($1 - \text{Distinct Families} / \text{Raw Candidates}$).

## 4. Portfolio-Level Anchored Ratings (0 to 3)

| Dimension | 0 (Failure) | 1 (Weak) | 2 (Competent) | 3 (Exemplary) |
| :--- | :--- | :--- | :--- | :--- |
| **Mechanism Diversity** | 1–2 repeated mechanisms with surface rewording | 3–5 distinct mechanisms; heavy clustering | 6–9 distinct causal mechanisms across multiple operators | $\ge 10$ genuinely distinct mechanisms spanning system, boundary, operational, and contrarian lenses |
| **Domain Specificity** | Generic advice applicable to any problem | Mentions domain nouns without operational mechanics | Tailored to domain actors, flows, and bottlenecks | Deeply grounded in domain-specific workflows, handoffs, and edge cases |
| **Constraint Relevance** | Violates explicit budget/staff/policy limits | Acknowledges constraints superficially | All possibilities respect hard constraints | Uses constraints as design levers without discarding required safeguards |
| **System Awareness** | Treats symptom in isolation | Notes 1–2 actors or incentives | Maps actors, flows, feedback loops, and boundary overflow | Identifies system stuckness, hidden labor, and mission-orientated vs. negotiative vs. participative boundary modes |
| **Preservation Awareness** | Discards what already works for novelty | Mentions existing features in passing | Explicitly protects stated strengths and considers simplification/no-change | Protects existing value, addresses change fatigue, and includes preservation-first/subtraction options where appropriate |
| **Uncertainty Honesty** | Presents speculations or simulated opinions as proven facts | Vague caveats | Explicitly labels assumptions and main unknowns per possibility | Distinguishes verified constraints, hypotheses, and likely *Yes-but* resistance |
| **Decision Restraint** | Declares a single winner or dumps an unsolicited implementation roadmap/tickets | Ranks ideas into a single winner-take-all list | Illuminates trade-offs without declaring a universal winner or roadmap | Evaluates multi-signal trade-offs and Rickards's three problem-owner questions while keeping ideation boundaries intact |
| **Usability** | Unstructured wall of text or unusable fragments | Repetitive list without synthesis | Clear structure with scannable possibilities and trade-offs | Progressive disclosure (Brief, System Snapshot, Portfolio, Spotlights, Tensions, Continuation) |
