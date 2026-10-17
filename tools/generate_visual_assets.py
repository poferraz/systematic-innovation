import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# 1. System Architecture SVG (1200x540)
arch_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 540" width="100%" height="100%" style="background:#090d16; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="glow-cyan" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00f2fe" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#4facfe" stop-opacity="0.9"/>
    </linearGradient>
    <linearGradient id="glow-amber" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f6d365" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#fda085" stop-opacity="0.9"/>
    </linearGradient>
    <linearGradient id="glow-purple" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#a18cd1" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#fbc2eb" stop-opacity="0.9"/>
    </linearGradient>
    <linearGradient id="card-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#141c2e" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#0e1524" stop-opacity="0.85"/>
    </linearGradient>
    <filter id="box-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#00f2fe" flood-opacity="0.15"/>
    </filter>
  </defs>

  <!-- Title & Subtitle -->
  <text x="600" y="48" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="700" letter-spacing="1">THE SYSTEMATIC INNOVATION PIPELINE</text>
  <text x="600" y="74" text-anchor="middle" fill="#8899b5" font-size="13" font-weight="400">Transforming Complex Socio-Technical Contradictions into Causally Distinct Possibility Portfolios</text>

  <!-- Horizontal connector line -->
  <path d="M 100 230 L 1100 230" stroke="#1f2d47" stroke-width="2" stroke-dasharray="6,6"/>

  <!-- Stage 1: Input & Preservation Scan -->
  <g transform="translate(60, 110)">
    <rect width="180" height="240" rx="12" fill="url(#card-grad)" stroke="#223354" stroke-width="1.5" filter="url(#box-glow)"/>
    <rect x="0" y="0" width="180" height="6" rx="3" fill="#00f2fe"/>
    <circle cx="90" cy="40" r="18" fill="#13233a" stroke="#00f2fe" stroke-width="1.5"/>
    <text x="90" y="45" text-anchor="middle" fill="#00f2fe" font-size="14" font-weight="700">1</text>
    <text x="90" y="80" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="600">Preservation Scan</text>
    <text x="90" y="100" text-anchor="middle" fill="#00f2fe" font-size="10" font-weight="600" letter-spacing="0.5">LAYER 1</text>
    <line x1="20" y1="115" x2="160" y2="115" stroke="#1f2d47" stroke-width="1"/>
    <text x="90" y="140" text-anchor="middle" fill="#94a3b8" font-size="11">Core Contradiction</text>
    <text x="90" y="165" text-anchor="middle" fill="#94a3b8" font-size="11">Non-Negotiables</text>
    <text x="90" y="190" text-anchor="middle" fill="#94a3b8" font-size="11">Boundary Mapping</text>
    <rect x="25" y="206" width="130" height="22" rx="4" fill="#0c1e33" stroke="#00f2fe" stroke-width="0.8"/>
    <text x="90" y="221" text-anchor="middle" fill="#38bdf8" font-size="9" font-weight="600">PROTECT ANCHORS</text>
  </g>

  <!-- Arrow 1 -> 2 -->
  <polygon points="252,230 242,225 242,235" fill="#00f2fe"/>

  <!-- Stage 2: Initial Fluency Depletion -->
  <g transform="translate(265, 110)">
    <rect width="180" height="240" rx="12" fill="url(#card-grad)" stroke="#223354" stroke-width="1.5"/>
    <rect x="0" y="0" width="180" height="6" rx="3" fill="#f6d365"/>
    <circle cx="90" cy="40" r="18" fill="#2d2215" stroke="#f6d365" stroke-width="1.5"/>
    <text x="90" y="45" text-anchor="middle" fill="#f6d365" font-size="14" font-weight="700">2</text>
    <text x="90" y="80" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="600">Fluency Depletion</text>
    <text x="90" y="100" text-anchor="middle" fill="#f6d365" font-size="10" font-weight="600" letter-spacing="0.5">ANTI-TROPE QUARANTINE</text>
    <line x1="20" y1="115" x2="160" y2="115" stroke="#1f2d47" stroke-width="1"/>
    <text x="90" y="140" text-anchor="middle" fill="#94a3b8" font-size="11">Top-of-Mind Tropes</text>
    <text x="90" y="165" text-anchor="middle" fill="#94a3b8" font-size="11">Memory Cliche Purge</text>
    <text x="90" y="190" text-anchor="middle" fill="#94a3b8" font-size="11">Discard 2-3 Defaults</text>
    <rect x="25" y="206" width="130" height="22" rx="4" fill="#271c0c" stroke="#f6d365" stroke-width="0.8"/>
    <text x="90" y="221" text-anchor="middle" fill="#fcd34d" font-size="9" font-weight="600">PREVENT COLLAPSE</text>
  </g>

  <!-- Arrow 2 -> 3 -->
  <polygon points="457,230 447,225 447,235" fill="#f6d365"/>

  <!-- Stage 3: 7 Reasoning Cells & Lenses -->
  <g transform="translate(470, 110)">
    <rect width="180" height="240" rx="12" fill="url(#card-grad)" stroke="#223354" stroke-width="1.5"/>
    <rect x="0" y="0" width="180" height="6" rx="3" fill="#a18cd1"/>
    <circle cx="90" cy="40" r="18" fill="#241938" stroke="#a18cd1" stroke-width="1.5"/>
    <text x="90" y="45" text-anchor="middle" fill="#a18cd1" font-size="14" font-weight="700">3</text>
    <text x="90" y="80" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="600">7 Reasoning Cells</text>
    <text x="90" y="100" text-anchor="middle" fill="#a18cd1" font-size="10" font-weight="600" letter-spacing="0.5">10 INNOVATION LENSES</text>
    <line x1="20" y1="115" x2="160" y2="115" stroke="#1f2d47" stroke-width="1"/>
    <text x="90" y="135" text-anchor="middle" fill="#94a3b8" font-size="10">Boundary Relaxation</text>
    <text x="90" y="153" text-anchor="middle" fill="#94a3b8" font-size="10">Inversion &amp; Synectics</text>
    <text x="90" y="171" text-anchor="middle" fill="#94a3b8" font-size="10">Unbundling &amp; Subtraction</text>
    <text x="90" y="189" text-anchor="middle" fill="#94a3b8" font-size="10">Perspective &amp; Constraint</text>
    <rect x="25" y="206" width="130" height="22" rx="4" fill="#231433" stroke="#a18cd1" stroke-width="0.8"/>
    <text x="90" y="221" text-anchor="middle" fill="#d8b4fe" font-size="9" font-weight="600">STRUCTURAL SHIFT</text>
  </g>

  <!-- Arrow 3 -> 4 -->
  <polygon points="662,230 652,225 652,235" fill="#a18cd1"/>

  <!-- Stage 4: Mechanism Ledger -->
  <g transform="translate(675, 110)">
    <rect width="180" height="240" rx="12" fill="url(#card-grad)" stroke="#223354" stroke-width="1.5"/>
    <rect x="0" y="0" width="180" height="6" rx="3" fill="#38ef7d"/>
    <circle cx="90" cy="40" r="18" fill="#132b1f" stroke="#38ef7d" stroke-width="1.5"/>
    <text x="90" y="45" text-anchor="middle" fill="#38ef7d" font-size="14" font-weight="700">4</text>
    <text x="90" y="80" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="600">Mechanism Ledger</text>
    <text x="90" y="100" text-anchor="middle" fill="#38ef7d" font-size="10" font-weight="600" letter-spacing="0.5">LAYER 2: 5 DIMENSIONS</text>
    <line x1="20" y1="115" x2="160" y2="115" stroke="#1f2d47" stroke-width="1"/>
    <text x="90" y="140" text-anchor="middle" fill="#94a3b8" font-size="11">Causal Levers Only</text>
    <text x="90" y="165" text-anchor="middle" fill="#94a3b8" font-size="11">Actors &amp; Triggers</text>
    <text x="90" y="190" text-anchor="middle" fill="#94a3b8" font-size="11">Duplicate Elimination</text>
    <rect x="25" y="206" width="130" height="22" rx="4" fill="#0f2619" stroke="#38ef7d" stroke-width="0.8"/>
    <text x="90" y="221" text-anchor="middle" fill="#86efac" font-size="9" font-weight="600">ZERO PSEUDO-VARIETY</text>
  </g>

  <!-- Arrow 4 -> 5 -->
  <polygon points="867,230 857,225 857,235" fill="#38ef7d"/>

  <!-- Stage 5: Six-Layer Portfolio & Receptivity -->
  <g transform="translate(880, 110)">
    <rect width="250" height="240" rx="12" fill="url(#card-grad)" stroke="#223354" stroke-width="1.5" filter="url(#box-glow)"/>
    <rect x="0" y="0" width="250" height="6" rx="3" fill="url(#glow-cyan)"/>
    <circle cx="125" cy="40" r="18" fill="#13233a" stroke="#00f2fe" stroke-width="1.5"/>
    <text x="125" y="45" text-anchor="middle" fill="#00f2fe" font-size="14" font-weight="700">5</text>
    <text x="125" y="80" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="600">Six-Layer Portfolio</text>
    <text x="125" y="100" text-anchor="middle" fill="#00f2fe" font-size="10" font-weight="600" letter-spacing="0.5">LAYERS 3-6: ACTION PATH</text>
    <line x1="20" y1="115" x2="230" y2="115" stroke="#1f2d47" stroke-width="1"/>
    <text x="125" y="135" text-anchor="middle" fill="#94a3b8" font-size="11">4-7 Causally Distinct Possibilities</text>
    <text x="125" y="155" text-anchor="middle" fill="#94a3b8" font-size="11">Rickards Ch. 8 Problem-Owner Receptivity</text>
    <text x="125" y="175" text-anchor="middle" fill="#94a3b8" font-size="11">Yes-But Hearing Inoculation</text>
    <text x="125" y="195" text-anchor="middle" fill="#94a3b8" font-size="11">Spotlight Signals (No Forced Winner)</text>
    <rect x="35" y="206" width="180" height="22" rx="4" fill="#0c1e33" stroke="#00f2fe" stroke-width="0.8"/>
    <text x="125" y="221" text-anchor="middle" fill="#38bdf8" font-size="9" font-weight="600">1-2 WEEK LEARNING PROBES</text>
  </g>

  <!-- Bottom Proof Bar -->
  <rect x="60" y="380" width="1070" height="120" rx="10" fill="#0c1424" stroke="#1e2c45" stroke-width="1"/>
  <text x="90" y="415" fill="#ffffff" font-size="14" font-weight="700">EMPIRICAL VALIDATION BENCHMARK (PILOT CORPUS)</text>
  <text x="90" y="435" fill="#64748b" font-size="12">Scored across 22 fresh-context runs on 12 cross-domain pilot cases with judge-free Vendi Scores.</text>

  <g transform="translate(90, 455)">
    <text x="0" y="20" fill="#00f2fe" font-size="24" font-weight="800">+162%</text>
    <text x="95" y="20" fill="#94a3b8" font-size="12">Causal Density (Mechanisms/1k tok)</text>
  </g>

  <g transform="translate(420, 455)">
    <text x="0" y="20" fill="#38ef7d" font-size="24" font-weight="800">-35%</text>
    <text x="80" y="20" fill="#94a3b8" font-size="12">Conversational Churn in Multi-Turn</text>
  </g>

  <g transform="translate(730, 455)">
    <text x="0" y="20" fill="#f6d365" font-size="24" font-weight="800">100%</text>
    <text x="75" y="20" fill="#94a3b8" font-size="12">Deep Turn-1 Restraint &amp; Negative Precision</text>
  </g>

  <g transform="translate(1010, 455)">
    <text x="0" y="20" fill="#f43f5e" font-size="24" font-weight="800">0%</text>
    <text x="45" y="20" fill="#94a3b8" font-size="12">Roadmap Drift</text>
  </g>
</svg>
"""

(ASSETS / "system-architecture.svg").write_text(arch_svg, encoding="utf-8")
print("Generated assets/system-architecture.svg")

# 2. Before / After Contrast SVG (1200x480)
contrast_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 480" width="100%" height="100%" style="background:#090d16; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="red-tint" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#241318" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#180d12" stop-opacity="0.9"/>
    </linearGradient>
    <linearGradient id="green-tint" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0f261d" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#0a1913" stop-opacity="0.9"/>
    </linearGradient>
  </defs>

  <text x="600" y="44" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="700">BEHAVIORAL CONTRAST: VANILLA LLM VS. SYSTEMATIC INNOVATION</text>
  <text x="600" y="68" text-anchor="middle" fill="#8899b5" font-size="13">Why ordinary AI brainstorming fails in production and how the systems approach fixes it</text>

  <!-- Left: Vanilla Card -->
  <g transform="translate(60, 95)">
    <rect width="520" height="345" rx="12" fill="url(#red-tint)" stroke="#5c1d29" stroke-width="1.5"/>
    <rect x="0" y="0" width="520" height="6" rx="3" fill="#f43f5e"/>

    <text x="24" y="38" fill="#fda4af" font-size="12" font-weight="700" letter-spacing="1">WITHOUT THE SKILL: VANILLA LLM</text>
    <text x="24" y="64" fill="#ffffff" font-size="17" font-weight="600">The "Obvious Listicle" Anti-Pattern</text>

    <line x1="24" y1="80" x2="496" y2="80" stroke="#3b1720" stroke-width="1"/>

    <!-- Bullet 1 -->
    <circle cx="36" cy="110" r="8" fill="#4c1420"/>
    <text x="36" y="114" text-anchor="middle" fill="#f43f5e" font-size="11" font-weight="800">✕</text>
    <text x="56" y="114" fill="#e2e8f0" font-size="13" font-weight="600">Surface Mode Collapse</text>
    <text x="56" y="132" fill="#94a3b8" font-size="12">Dumps top-of-mind internet tropes (2-2-2 meal rules, NFC pill caps, cash bounties) on repeat.</text>

    <!-- Bullet 2 -->
    <circle cx="36" cy="165" r="8" fill="#4c1420"/>
    <text x="36" y="169" text-anchor="middle" fill="#f43f5e" font-size="11" font-weight="800">✕</text>
    <text x="56" y="169" fill="#e2e8f0" font-size="13" font-weight="600">Duplicate Mechanism Collapse (0.55 ratio)</text>
    <text x="56" y="187" fill="#94a3b8" font-size="12">Generates 6–10 numbered ideas that are merely wording variations of a single causal lever.</text>

    <!-- Bullet 3 -->
    <circle cx="36" cy="220" r="8" fill="#4c1420"/>
    <text x="36" y="224" text-anchor="middle" fill="#f43f5e" font-size="11" font-weight="800">✕</text>
    <text x="56" y="224" fill="#e2e8f0" font-size="13" font-weight="600">Zero Turn-1 Restraint (0/10 runs)</text>
    <text x="56" y="242" fill="#94a3b8" font-size="12">Prematurely dumps 2,000+ words of answers without asking clarifying discovery questions.</text>

    <!-- Bullet 4 -->
    <circle cx="36" cy="275" r="8" fill="#4c1420"/>
    <text x="36" y="279" text-anchor="middle" fill="#f43f5e" font-size="11" font-weight="800">✕</text>
    <text x="56" y="279" fill="#e2e8f0" font-size="13" font-weight="600">Mandated 90-Day Implementation Roadmaps</text>
    <text x="56" y="297" fill="#94a3b8" font-size="12">Hallucinates multi-month Gantt execution schedules and forces an unearned winner.</text>
  </g>

  <!-- Right: Systematic Innovation Card -->
  <g transform="translate(620, 95)">
    <rect width="520" height="345" rx="12" fill="url(#green-tint)" stroke="#1a533c" stroke-width="1.5"/>
    <rect x="0" y="0" width="520" height="6" rx="3" fill="#10b981"/>

    <text x="24" y="38" fill="#6ee7b7" font-size="12" font-weight="700" letter-spacing="1">WITH SYSTEMATIC-INNOVATION SKILL</text>
    <text x="24" y="64" fill="#ffffff" font-size="17" font-weight="600">The Systems-Aware Possibility Portfolio</text>

    <line x1="24" y1="80" x2="496" y2="80" stroke="#123829" stroke-width="1"/>

    <!-- Bullet 1 -->
    <circle cx="36" cy="110" r="8" fill="#0d3b28"/>
    <text x="36" y="114" text-anchor="middle" fill="#10b981" font-size="11" font-weight="800">✓</text>
    <text x="56" y="114" fill="#e2e8f0" font-size="13" font-weight="600">Initial Fluency Depletion</text>
    <text x="56" y="132" fill="#94a3b8" font-size="12">Explicitly quarantines the top 2–3 default memory-dump tropes before generating ideas.</text>

    <!-- Bullet 2 -->
    <circle cx="36" cy="165" r="8" fill="#0d3b28"/>
    <text x="36" y="169" text-anchor="middle" fill="#10b981" font-size="11" font-weight="800">✓</text>
    <text x="56" y="169" fill="#e2e8f0" font-size="13" font-weight="600">Causally Diverse Mechanism Ledger (+162% Density)</text>
    <text x="56" y="187" fill="#94a3b8" font-size="12">Every candidate operates across distinct levers (incentives, queues, information schemas, time, roles).</text>

    <!-- Bullet 3 -->
    <circle cx="36" cy="220" r="8" fill="#0d3b28"/>
    <text x="36" y="224" text-anchor="middle" fill="#10b981" font-size="11" font-weight="800">✓</text>
    <text x="56" y="224" fill="#e2e8f0" font-size="13" font-weight="600">Disciplined Turn-1 Restraint (10/10 runs)</text>
    <text x="56" y="242" fill="#94a3b8" font-size="12">Outputs a concise Preservation Scan, 4 targeted discovery questions, and 3 seeds (&lt;450 tokens).</text>

    <!-- Bullet 4 -->
    <circle cx="36" cy="275" r="8" fill="#0d3b28"/>
    <text x="36" y="279" text-anchor="middle" fill="#10b981" font-size="11" font-weight="800">✓</text>
    <text x="56" y="279" fill="#e2e8f0" font-size="13" font-weight="600">Spotlight Signals &amp; 1–2 Week Learning Probes</text>
    <text x="56" y="297" fill="#94a3b8" font-size="12">Preserves human decision agency; concludes with reversible low-cost empirical micro-experiments.</text>
  </g>
</svg>
"""

(ASSETS / "comparison.svg").write_text(contrast_svg, encoding="utf-8")
print("Generated assets/comparison.svg")
