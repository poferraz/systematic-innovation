# Systematic Innovation: Provider-Neutral Agent Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Standard: Agent Skills](https://img.shields.io/badge/Standard-Agent%20Skills-brightgreen.svg)](skills/systematic-innovation/SKILL.md)
[![Verification: Pilot RED/GREEN Passed](https://img.shields.io/badge/Evaluation-Pilot%20GREEN%20Passed-success.svg)](evals/pilot/treatment-analysis.md)

`systematic-innovation` is a provider-neutral Agent Skill and evaluation laboratory designed to help LLMs break through mode collapse, avoid repackaging obvious tropes, and generate causally distinct, system-aware possibility portfolios while preserving what already works.

Rooted in the socio-technical systems theory of Tudor Rickards (*Stimulating Innovation: A Systems Approach*, 1985) and modern empirical LLM ideation science (2024–2026), this skill replaces generic AI brainstorm dumps with disciplined mechanism tracking, boundary mapping, and low-cost empirical learning probes.

---

## Value Proposition: Beyond Brainstorming Cliches

Ordinary LLM brainstorming suffers from well-documented systemic failure modes:
1. **Mode Collapse / Memory Dumps:** Independent runs repeatedly output identical surface internet cliches (e.g., *"The 2-2-2 meal plan"*, *"NFC tags"*, *"loss aversion deposits"*).
2. **Duplicate Mechanism Clustering:** Numbered "options" vary surface terminology while relying on the exact same underlying causal lever (e.g., 5 different ways to split commissions).
3. **Premature Implementation Drift:** Jumping immediately into 30/60/90-day Gantt charts and forced "winners" before understanding constraints.
4. **Preservation Blindness:** Recommending destructive interventions that violate statutory reviews, customer trust, or legal guardrails.

`systematic-innovation` enforces:
- **Initial Fluency Depletion:** Identifying and quarantining the top-of-mind memory-dump tropes before populating candidates.
- **Mechanism Ledger:** Tracking every candidate across 5 structural dimensions (`What changes`, `Principal actor`, `Timing/Trigger`, `Incentive/Feedback loop`, `Failure mode addressed`) to guarantee causal distinctness.
- **Preservation Inventory:** Explicitly mapping non-negotiables that must not be disrupted.
- **Problem-Owner Receptivity:** Applying Rickards's 3 Problem-Owner Questions, Mission-Orientated / Negotiative / Participative boundary routing, and *Yes-But* hearing inoculation.
- **Decision Restraint:** Ending with tension-revealing Spotlight Signals and 1–2 week low-cost learning probes rather than rigid implementation roadmaps.

---

## Empirical Benchmark Results (Pilot RED Baseline vs. GREEN Treatment)

The skill was evaluated on a 12-case cross-domain pilot corpus (`evals/pilot/cases.json`) using 22 fresh-context runs per condition (`10 positive cases × 2 replicates + 2 negative controls × 1 replicate`). All runs were scored using deterministic NLP extraction and judge-free Vendi Scores ($\text{VS}_k$).

| Evaluation Metric | RED Baseline (`vanilla`) | GREEN Treatment (`skill`) | Delta / Empirical Lift |
| :--- | :---: | :---: | :---: |
| **Primary Efficiency (Mechanisms / 1k Tokens)** | **0.897** | **2.352** | **+162% causal information density** |
| Deep Multi-Turn Efficiency (`permit-wait`) | 0.109 | 1.374 | **12.6x increase** |
| Deep Multi-Turn Efficiency (`retail-retention`) | 0.165 | 1.359 | **8.2x increase** |
| Mean Total Output Tokens in Deep Multi-Turn | 6,422 tokens | 4,170 tokens | **-35% conversational churn** |
| Deep Turn-1 Restraint ($\le 450$ tokens, 4 questions) | 0 / 10 runs (0%) | 10 / 10 runs (100%) | **Zero premature solution dumps** |
| Negative Trigger Precision (`should_trigger: false`) | 100% (0 false triggers) | 100% (0 false triggers) | **Zero unwanted ceremony on lookups/code** |
| Implementation Drift (Forbidden 30/60/90 roadmaps) | 18 / 20 positive runs (90% fail) | 0 / 20 positive runs (0% fail) | **100% decision restraint preserved** |
| System & Preservation Scan Included | 0 / 20 runs (0%) | 20 / 20 runs (100%) | **100% core strength preservation** |

*Full quantitative details, verbatim excerpts, and scoring formulas are documented in [`evals/pilot/treatment-analysis.md`](evals/pilot/treatment-analysis.md).*

---

## Interaction Modes

### Quick Mode (Single-Turn Execution)
Triggered when the user explicitly asks for immediate ideas, rapid alternatives, or provides complete constraints upfront:
- Compact System & Preservation Scan ($<250$ words).
- 4–6 distinct candidates spanning at least 3 distinct causal lever types.
- Mechanism Ledger, Spotlight Signals, and 1–2 Week Learning Probes.

### Deep Mode (Multi-Turn Iterative Discovery)
Default for complex, systemic, or organizational challenges:
- **Turn 1 Restraint:** Strictly limits output to a System & Preservation Scan, exactly 4 targeted discovery questions uncovering hidden assets and decision rights, and 3 provisional seeds ($<450$ total tokens).
- **Turn 2+:** Synthesizes user clarifications into the complete Six-Layer Innovation Portfolio.

---

## Methodology & Architectural Structure

The canonical skill operates through two core architectural frameworks:

### 1. Seven Reasoning Cells & Ten Innovation Lenses
1. **Boundary Relaxation:** Expanding the system perimeter.
2. **Inversion:** Flipping sequence, timing, or figure-ground relationships.
3. **Analogy (Synectics):** Mapping mechanisms from biological, physical, or cross-domain systems.
4. **Unbundling:** Separating tightly coupled functions, incentives, or roles.
5. **Subtraction:** Removing steps, policies, or artifacts rather than adding process.
6. **Perspective Shift:** Reframing from the vantage of neglected actors.
7. **Constraint Imposition:** Turning acute limitations into generative catalysts.

### 2. Six Disclosure Layers
- **Layer 1: Innovation Brief & Preservation Scan** — Core structural tension + non-negotiable preservation inventory + quarantined tropes.
- **Layer 2: Mechanism Ledger** — Tabular tracking of candidate dimensions ensuring zero duplicate mechanisms.
- **Layer 3: Possibility Portfolio** — 4–7 causally distinct candidates.
- **Layer 4: System Receptivity & Action Path** — Rickards (1985) Ch. 8 Problem-Owner Questions, boundary routing (Mission-Orientated / Negotiative / Participative), and *Yes-But* hearing inoculation.
- **Layer 5: Spotlight Signals** — Highlighting tension axes without collapsing user agency.
- **Layer 6: Low-Cost Learning Probes** — Reversible 1–2 week micro-experiments.

---

## Supported Standard & Installation

`systematic-innovation` adheres strictly to the **Agent Skills Specification**:
- 100% Portable Markdown.
- Zero binary or executable dependencies.
- Zero runtime network access.

### Local Installation

You can install `systematic-innovation` directly into any Agent Skills compatible environment:

```bash
# Clone the repository
git clone https://github.com/systematic-innovation/systematic-innovation.git
cd systematic-innovation

# Validate the skill package structure and link integrity
python tools/validate_skill.py skills/systematic-innovation
```

To install into your local agent skills directory:
```bash
# Antigravity / Gemini CLI
cp -r skills/systematic-innovation ~/.gemini/antigravity/skills/

# Claude Desktop / Code
cp -r skills/systematic-innovation ~/.claude/skills/

# Codex / OpenAI CLI
cp -r skills/systematic-innovation ~/.codex/skills/
```

### Direct Markdown Loading (Fallback)
If your environment does not support automated skill discovery, pass [`skills/systematic-innovation/SKILL.md`](skills/systematic-innovation/SKILL.md) directly into your agent's system prompt or context window.

---

## Evidence Limits & Bibliographic Record

This repository enforces strict bibliographic provenance boundaries:
- **Verified Primary Source:** Tudor Rickards (1985), *Stimulating Innovation: A Systems Approach*, Frances Pinter (Publishers), London, `pp. xi + 221`, ISBN `0-86187-512-5`.
- **Verified Historical Chapters:** Ch. 1 (Introduction), Ch. 2 (Structures and Systems), Ch. 3 (Diagnostic Framework), Ch. 4 (Team and Individual Characteristics), Ch. 5 (Techniques of Creative Problem Solving), Ch. 6 (Information Transfer), Ch. 7 (Internal/External Collaboration), Ch. 8 (Evaluation, Acceptance and Action Plans), Ch. 9 (Conclusions).
- **Provenance Separation:** Modern AI adaptations (e.g. LLM initial fluency depletion, judge-free Vendi Scores, Mechanism Ledgers) are documented in [`skills/systematic-innovation/references/evidence.md`](skills/systematic-innovation/references/evidence.md) as original AI mechanisms and are never falsely attributed to 1985 texts.

---

## License & Security

- **License:** [MIT License](LICENSE)
- **Security & Responsible Use:** See [SECURITY.md](SECURITY.md) for vulnerability reporting guidelines and safe prompt isolation instructions.
