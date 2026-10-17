# Pilot RED Baseline Analysis (`vanilla` No-Skill Condition)

## 1. Execution Summary

- **Corpus:** `evals/pilot/cases.json` (12 cross-domain cases: 5 Deep controlled 3-turn cases, 5 Quick single-turn cases, 2 negative trigger controls).
- **Total Fresh-Context Runs:** 22 (`10 positive cases × 2 replicates + 2 negative cases × 1 replicate`), preserved verbatim in `evals/pilot/results/baseline.jsonl`.
- **Host / Isolation:** Clean-context subagent invocations (`antigravity-subagent-clean-context`) with zero access to the skill, rubric, or repository files.

---

## 2. Quantitative RED Baseline Metrics (20 Positive Runs)

| Case ID | Mode | Mean Total Assistant Tokens | Mean Raw Candidates | Mean Distinct Mechanism Families | Mean Duplicate Collapse Ratio | Mean Vendi Score ($\text{VS}_k$) | Mean Qualified Distinct Mechanisms / 1k Tokens |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `retail-retention` | Deep (3-turn) | 6,060 | 6.0 | 1.0 | 0.83 | 5.28 | 0.165 |
| `permit-wait` | Deep (3-turn) | 9,280 | 5.0 | 1.0 | 0.80 | 4.01 | 0.109 |
| `release-bottleneck` | Deep (3-turn) | 6,465 | 4.5 | 1.5 | 0.65 | 3.92 | 0.234 |
| `teacher-fatigue` | Deep (3-turn) | 4,214 | 4.0 | 2.5 | 0.38 | 3.75 | 0.621 |
| `library-access` | Deep (3-turn) | 6,090 | 9.5 | 3.0 | 0.69 | 8.48 | 0.493 |
| `ignored-reminders` | Quick (1-turn) | 1,858 | 7.0 | 1.5 | 0.79 | 6.10 | 0.793 |
| `food-bank-mismatch` | Quick (1-turn) | 1,452 | 4.0 | 2.5 | 0.38 | 3.80 | 1.733 |
| `meal-planning` | Quick (1-turn) | 1,699 | 2.5 | 2.0 | 0.13 | 2.42 | 1.565 |
| `warehouse-returns` | Quick (1-turn) | 3,135 | 8.0 | 3.5 | 0.55 | 7.14 | 1.134 |
| `provocation` | Quick (1-turn) | 2,118 | 6.5 | 4.5 | 0.30 | 6.12 | 2.122 |
| **Aggregate Positive Mean** | **All 20 Runs** | **4,237** | **5.7** | **2.3** | **0.55** | **5.10** | **0.897** |

---

## 3. Observed Failure Modes & Verbatim Evidence

### Failure 1: `duplicate_mechanisms` & Cross-Replicate Homogenization (Observed in 18/20 positive runs)
- **Within-Run Mechanism Collapse (Mean Duplicate Collapse Ratio = `0.55`):**
  - In `retail-retention` (reps 1 & 2), 6 numbered portfolio items repeatedly vary a single underlying lever (`incentive_split_or_bounty` / `queue_or_lead_priority`—e.g., 90/10 vs. 85/15 split, 50/50 cold split, 10% micro-assist split, inbound lead priority).
  - In `food-bank-mismatch` (reps 1 & 2), separate numbered bullets ("Static QR Code + Free Google Doc", "Checkout Grab & Give Cards", "Shelf-Level Buy One Extra Tags", "Pre-Bagged $10 Need Bundles") are surface-channel variations of one causal mechanism: **point-of-purchase donor demand signaling**.
- **Cross-Replicate Mode Collapse (Initial Fluency Memory Dumping):**
  - In `meal-planning` rep 1 (`70679cd6`) and rep 2 (`d89abc5c`), two independent fresh contexts produced virtually identical top-of-mind internet tropes:
    1. *"The 2–2–2 Shopping Architecture"* (rep 1) vs. *"The 2-2-2-1 Energy-Matched Meal Plan"* (rep 2).
    2. *"Put Condiments in the Drawers + Eye-Level Eat Me First Zone"* (rep 1) vs. *"Put condiments, sauces, and drinks inside the bottom drawers + Red Zone Triage Bin at exact eye level"* (rep 2).
    3. *"The Two-Vehicle Buying Filter"* (rep 1) vs. *"The Rule of 2 Jobs (Ban Orphan Ingredients)"* (rep 2).
    4. *"Thursday Clean-Out Vehicle (Fried rice, Frittata, Sheet-pan roast)"* (rep 1) vs. *"Thursday 10-Minute State Change (The Frittata / Omelet, The Sheet-Pan Roast, Friday Fried Rice)"* (rep 2).
  - In `ignored-reminders` rep 1 (`2906ea6c`) and rep 2 (`42330813`), both runs independently generated the same 7 ideas: NFC sticker on pill cap, iOS `FamilyControls`/`ManagedSettings` Screen Time app shielding, OS charger/geofence state triggers, silent partner lock-screen widget, pharmacokinetic coverage curve, pill-in-hand camera photo, and $15–$30 loss-aversion deposit contracts.
- **Required Skill Counter:** Enforce **Initial Fluency Depletion** (explicitly identifying and setting aside the top 2–3 default memory-dump tropes in a domain before populating the Mechanism Ledger) and require each portfolio concept to occupy a distinct **Mechanism Ledger** row across structural dimensions (`What changes`, `Timing`, `Incentive/Feedback loop`).

### Failure 2: `missing_preservation` & Zero Turn-1 Discovery in Deep Cases (Observed in 10/10 Deep runs)
- **Zero Turn-1 Questions:** Across all 10 Deep multi-turn runs (`retail-retention`, `permit-wait`, `release-bottleneck`, `teacher-fatigue`, `library-access`), the baseline assistant asked **0 clarifying questions on Turn 1** (except a generic optional footer in `meal-planning` rep 2, which is a Quick case) and immediately output a full solution dump.
- **Premature Constraint Violation Before Disclosure:**
  - In `permit-wait` Turn 1, both replicates proposed waiving pre-opening city reviews (*"Permit-by-Notification + Post-Opening Audits"*, *"Risk-Tiered Self-Certification"*, *"Abolish case-by-case public hearings"*), violating statutory review and public-record preservation until Turn 3 forced a retraction.
  - In `retail-retention` Turn 1, both replicates proposed cash spiffs, $50–$100 rescue bounties, and paid creator overrides before Turn 3 revealed the zero-payroll constraint.
- **Required Skill Counter:** In Deep mode, perform an explicit **Preservation Scan** (*What currently works and must not be broken*) and ask targeted, high-leverage **Brief-Shaping Questions** (capped at $\le 7$, paired with contrasting provisional seeds) before locking the final portfolio.

### Failure 3: `missing_system_map` & Missing Stakeholder Receptivity (Observed in 16/20 positive runs)
- Vanilla outputs jump straight to categorizing interventions without mapping the socio-technical system's actors, incentives, feedback loops, and boundary overflows.
- None of the 20 runs evaluated **Problem-Owner Receptivity** (whether an idea is actionable within the owner's direct resources vs. requiring **Negotiative** win-win goal emergence across independent departments or **Participative** discovery, nor how to inoculate against immediate *"Yes, but..."* rejection).
- **Required Skill Counter:** Require a concise **System & Preservation Map** before portfolio generation, and attach **Receptivity & Action Path Notes** (Rickards's Three Problem-Owner Questions, Mission-Orientated / Negotiative / Participative boundary routing, and *Yes-But* inoculation) to spotlighted possibilities.

### Failure 4: `premature_winner` & `implementation_drift` (Observed in 18/20 positive runs)
- 18 of 20 positive runs concluded with prescriptive **30-Day / 90-Day / 180-Day Implementation Roadmaps** (e.g., *"Phase 1: Weeks 1–4... Phase 2: Weeks 5–8... Phase 3: Weeks 9–12"*) that collapse open exploration into a single mandated execution sequence.
- **Required Skill Counter:** Strictly prohibit multi-phase implementation roadmaps, Gantt/sprint schedules, and unrequested winner selection during ideation; end instead with **1–2 week low-cost learning probes** and open comparative trade-offs.

### Failure 5: Unverified Quantitative Claims (`uncertainty_honesty`, Observed in 8/20 positive runs)
- Vanilla outputs fabricated precise-sounding empirical percentages inside examples (e.g., `warehouse-returns` claiming *"40%–50% of returns resolved at Filter 1"* and *"65–75% of reverse-logistics labor is spent simply cutting tape"*; `ignored-reminders` quoting *"afternoon focus rating is 38% higher"*).
- **Required Skill Counter:** Forbid invented statistics or unverified quantitative effect sizes; require explicit labeling of causal assumptions and what must be tested locally.
