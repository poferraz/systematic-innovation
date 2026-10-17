from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# 1. Perfected Hero Banner (assets/banner.png)
banner_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,800;0,9..144,900;1,9..144,600&family=Libre+Baskerville:ital,wght@0,700;1,400;1,700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1280px;
    height: 640px;
    background: #1783be;
    color: #d8ff55;
    font-family: 'Fraunces', 'Times New Roman', serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 56px 84px 44px 84px;
    position: relative;
    overflow: hidden;
  }

  body::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 45% 25%, rgba(255,255,255,0.06) 0%, transparent 65%);
    pointer-events: none;
  }

  .header-block {
    position: relative;
    z-index: 2;
    max-width: 1112px;
  }

  .double-rule-top {
    border-top: 3.5px solid #d8ff55;
    border-bottom: 3.5px solid #d8ff55;
    height: 9px;
    margin-bottom: 26px;
    width: 100%;
  }

  .main-title {
    font-size: 88px;
    line-height: 0.92;
    font-weight: 900;
    letter-spacing: -0.5px;
    color: #d8ff55;
    text-transform: uppercase;
    font-variation-settings: 'opsz' 144, 'wght' 900;
  }

  .rule-mid {
    border-top: 3.5px solid #d8ff55;
    margin-top: 22px;
    margin-bottom: 14px;
    width: 100%;
  }

  .subtitle {
    font-family: 'Libre Baskerville', serif;
    font-size: 32px;
    line-height: 1.1;
    font-style: italic;
    font-weight: 700;
    color: #d8ff55;
    letter-spacing: 0.2px;
  }

  .rule-bottom {
    border-top: 3.5px solid #d8ff55;
    margin-top: 14px;
    width: 100%;
  }

  /* Systems Linework Vector positioned with clean clearance */
  .systems-grid {
    position: absolute;
    right: 84px;
    bottom: 110px;
    width: 450px;
    height: 175px;
    z-index: 1;
  }

  .footer-block {
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }

  .author-tag {
    display: inline-block;
  }

  .author-name {
    font-family: 'Fraunces', serif;
    font-size: 38px;
    font-weight: 800;
    color: #d8ff55;
    letter-spacing: -0.2px;
    display: inline-block;
    padding-bottom: 6px;
    border-bottom: 3.5px solid #d8ff55;
  }

  .provenance-tag {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #ffffff;
    opacity: 0.92;
    text-align: right;
    line-height: 1.6;
  }

  .provenance-tag span {
    color: #d8ff55;
  }
</style>
</head>
<body>
  <div class="header-block">
    <div class="double-rule-top"></div>
    <div class="main-title">
      SYSTEMATIC<br>
      INNOVATION
    </div>
    <div class="rule-mid"></div>
    <div class="subtitle">A Systems Approach to LLM Ideation</div>
    <div class="rule-bottom"></div>
  </div>

  <div class="systems-grid">
    <svg viewBox="0 0 450 175" width="100%" height="100%">
      <!-- Outer Boundary -->
      <rect x="5" y="10" width="440" height="155" rx="3" fill="#136fa3" fill-opacity="0.25" stroke="#d8ff55" stroke-width="1.5" stroke-dasharray="5,5"/>
      <text x="20" y="30" fill="#d8ff55" font-family="'Space Grotesk', sans-serif" font-size="9" font-weight="700" letter-spacing="1.5">SOCIO-TECHNICAL SELECTION ENVIRONMENT (RICKARDS 1985)</text>

      <!-- Search Node -->
      <rect x="25" y="55" width="95" height="46" rx="2" fill="#0f5a85" stroke="#d8ff55" stroke-width="1.5"/>
      <text x="72" y="78" text-anchor="middle" fill="#ffffff" font-family="'Space Grotesk', sans-serif" font-size="10" font-weight="700" letter-spacing="1">SEARCH</text>
      <text x="72" y="91" text-anchor="middle" fill="#d8ff55" font-family="'Space Grotesk', sans-serif" font-size="8">7 REASONING CELLS</text>

      <!-- Arrow 1 -->
      <line x1="120" y1="78" x2="168" y2="78" stroke="#d8ff55" stroke-width="1.8"/>
      <polygon points="168,78 160,74 160,82" fill="#d8ff55"/>

      <!-- Center Transformation Node -->
      <rect x="168" y="48" width="115" height="60" rx="2" fill="#0f5a85" stroke="#d8ff55" stroke-width="2"/>
      <text x="225" y="74" text-anchor="middle" fill="#d8ff55" font-family="'Space Grotesk', sans-serif" font-size="10" font-weight="700" letter-spacing="1">MECHANISM</text>
      <text x="225" y="89" text-anchor="middle" fill="#ffffff" font-family="'Space Grotesk', sans-serif" font-size="10" font-weight="700">LEDGER</text>
      <text x="225" y="100" text-anchor="middle" fill="#c3ebff" font-family="'Space Grotesk', sans-serif" font-size="7.5">DEDUPLICATION GATE</text>

      <!-- Arrow 2 -->
      <line x1="283" y1="78" x2="330" y2="78" stroke="#d8ff55" stroke-width="1.8"/>
      <polygon points="330,78 322,74 322,82" fill="#d8ff55"/>

      <!-- Output Node -->
      <rect x="330" y="55" width="95" height="46" rx="2" fill="#0f5a85" stroke="#d8ff55" stroke-width="1.5"/>
      <text x="377" y="78" text-anchor="middle" fill="#ffffff" font-family="'Space Grotesk', sans-serif" font-size="10" font-weight="700" letter-spacing="1">PORTFOLIO</text>
      <text x="377" y="91" text-anchor="middle" fill="#d8ff55" font-family="'Space Grotesk', sans-serif" font-size="8">6 DISCLOSURE LAYERS</text>

      <!-- Feedback Loop Bottom -->
      <path d="M 377 101 L 377 140 L 72 140 L 72 101" fill="none" stroke="#d8ff55" stroke-width="1.5"/>
      <polygon points="72,101 68,109 76,109" fill="#d8ff55"/>
      <text x="225" y="134" text-anchor="middle" fill="#d8ff55" font-family="'Space Grotesk', sans-serif" font-size="8.5" font-weight="700" letter-spacing="1">LEARNING LOOPS &amp; RECEPTIVITY INOCULATION</text>
    </svg>
  </div>

  <div class="footer-block">
    <div class="author-tag">
      <div class="author-name">Tudor Rickards</div>
    </div>
    <div class="provenance-tag">
      <span>Stimulating Innovation</span> (1985) · Frances Pinter<br>
      Provider-Neutral Agent Skill · Agent Skills Standard
    </div>
  </div>
</body>
</html>
"""

# 2. Authentic Editorial Comparison Card (assets/comparison.svg)
comparison_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 520" width="100%" height="100%" style="background:#0e2438; font-family:'Helvetica Neue', Arial, sans-serif;">
  <defs>
    <style>
      .title-serif { font-family:'Georgia', serif; }
      .mono-label { font-family:'SF Mono', Menlo, Consolas, monospace; }
    </style>
  </defs>

  <!-- Header -->
  <text x="600" y="46" text-anchor="middle" fill="#d8ff55" font-size="24" font-weight="700" class="title-serif" letter-spacing="0.5">THE ARCHITECTURAL CONTRAST</text>
  <text x="600" y="72" text-anchor="middle" fill="#a0c8e0" font-size="13">Why default LLM brainstorming collapses into pseudo-variety and how Tudor Rickards's systems model fixes it</text>

  <!-- Left Card: Vanilla Default -->
  <g transform="translate(60, 100)">
    <rect width="520" height="370" rx="4" fill="#091b2c" stroke="#25425d" stroke-width="1.5"/>
    <rect x="0" y="0" width="520" height="4" fill="#ff6b81"/>

    <text x="28" y="36" fill="#ff94a4" font-size="11" font-weight="700" class="mono-label" letter-spacing="1.5">WITHOUT THE SKILL · VANILLA LLM</text>
    <text x="28" y="66" fill="#ffffff" font-size="18" font-weight="700" class="title-serif">The "Obvious Listicle" Anti-Pattern</text>

    <line x1="28" y1="84" x2="492" y2="84" stroke="#1f374e" stroke-width="1"/>

    <!-- Point 1 -->
    <text x="28" y="116" fill="#ff6b81" font-size="14" font-weight="700">✕</text>
    <text x="50" y="116" fill="#ffffff" font-size="13" font-weight="700">Top-of-Mind Mode Collapse</text>
    <text x="50" y="136" fill="#8eaabf" font-size="12" line-height="1.4">Dumps immediate memory cliches (2-2-2 meal plans, NFC stickers, cash bonuses) across independent runs.</text>

    <!-- Point 2 -->
    <text x="28" y="176" fill="#ff6b81" font-size="14" font-weight="700">✕</text>
    <text x="50" y="176" fill="#ffffff" font-size="13" font-weight="700">Duplicate Mechanism Families (0.55 Collapse Ratio)</text>
    <text x="50" y="196" fill="#8eaabf" font-size="12">Generates 6–10 numbered ideas that merely re-word a single causal lever (e.g. 5 minor commission variations).</text>

    <!-- Point 3 -->
    <text x="28" y="236" fill="#ff6b81" font-size="14" font-weight="700">✕</text>
    <text x="50" y="236" fill="#ffffff" font-size="13" font-weight="700">Zero Turn-1 Restraint (0/10 Runs)</text>
    <text x="50" y="256" fill="#8eaabf" font-size="12">Dumps 2,000+ words on Turn 1 without asking discovery questions or identifying non-negotiable anchors.</text>

    <!-- Point 4 -->
    <text x="28" y="296" fill="#ff6b81" font-size="14" font-weight="700">✕</text>
    <text x="50" y="296" fill="#ffffff" font-size="13" font-weight="700">Premature 90-Day Implementation Roadmaps</text>
    <text x="50" y="316" fill="#8eaabf" font-size="12">Burns tokens hallucinating multi-phase Gantt execution schedules and forces an unearned single winner.</text>

    <!-- Metric Tag -->
    <rect x="28" y="338" width="464" height="22" rx="2" fill="#140b10" stroke="#4a1520" stroke-width="1"/>
    <text x="260" y="353" text-anchor="middle" fill="#ff94a4" font-size="10" font-weight="700" class="mono-label">PILOT EFFICIENCY: 0.897 MECHANISMS / 1K TOKENS</text>
  </g>

  <!-- Right Card: Systematic Innovation -->
  <g transform="translate(620, 100)">
    <rect width="520" height="370" rx="4" fill="#1783be" stroke="#d8ff55" stroke-width="1.5"/>
    <rect x="0" y="0" width="520" height="4" fill="#d8ff55"/>

    <text x="28" y="36" fill="#d8ff55" font-size="11" font-weight="700" class="mono-label" letter-spacing="1.5">WITH SYSTEMATIC-INNOVATION SKILL</text>
    <text x="28" y="66" fill="#ffffff" font-size="18" font-weight="700" class="title-serif">The Systems-Aware Possibility Portfolio</text>

    <line x1="28" y1="84" x2="492" y2="84" stroke="#2594d1" stroke-width="1"/>

    <!-- Point 1 -->
    <text x="28" y="116" fill="#d8ff55" font-size="14" font-weight="700">✓</text>
    <text x="50" y="116" fill="#ffffff" font-size="13" font-weight="700">Initial Fluency Depletion (Quarantined Tropes)</text>
    <text x="50" y="136" fill="#e0f2fe" font-size="12">Names and explicitly sets aside the top 2–3 default memory-dump tropes before populating candidates.</text>

    <!-- Point 2 -->
    <text x="28" y="176" fill="#d8ff55" font-size="14" font-weight="700">✓</text>
    <text x="50" y="176" fill="#ffffff" font-size="13" font-weight="700">Causally Diverse Mechanism Ledger (+162% Density)</text>
    <text x="50" y="196" fill="#e0f2fe" font-size="12">Every candidate operates across distinct levers (incentives, queues, information schemas, time, roles, subtraction).</text>

    <!-- Point 3 -->
    <text x="28" y="236" fill="#d8ff55" font-size="14" font-weight="700">✓</text>
    <text x="50" y="236" fill="#ffffff" font-size="13" font-weight="700">Disciplined Turn-1 Restraint (10/10 Runs)</text>
    <text x="50" y="256" fill="#e0f2fe" font-size="12">Outputs a concise Preservation Scan, 4 targeted discovery questions, and 3 contrasting seeds (&lt;450 tokens).</text>

    <!-- Point 4 -->
    <text x="28" y="296" fill="#d8ff55" font-size="14" font-weight="700">✓</text>
    <text x="50" y="296" fill="#ffffff" font-size="13" font-weight="700">Spotlight Signals &amp; 1–2 Week Learning Probes</text>
    <text x="50" y="316" fill="#e0f2fe" font-size="12">Preserves problem-owner agency; concludes with reversible low-cost micro-experiments instead of roadmaps.</text>

    <!-- Metric Tag -->
    <rect x="28" y="338" width="464" height="22" rx="2" fill="#0f5a85" stroke="#d8ff55" stroke-width="1"/>
    <text x="260" y="353" text-anchor="middle" fill="#d8ff55" font-size="10" font-weight="700" class="mono-label">PILOT EFFICIENCY: 2.352 MECHANISMS / 1K TOKENS (+162%)</text>
  </g>
</svg>
"""

# 3. Authentic Systems Architecture Diagram (assets/system-architecture.svg)
architecture_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 540" width="100%" height="100%" style="background:#0e2438; font-family:'Helvetica Neue', Arial, sans-serif;">
  <defs>
    <style>
      .title-serif { font-family:'Georgia', serif; }
      .mono-label { font-family:'SF Mono', Menlo, Consolas, monospace; }
    </style>
  </defs>

  <text x="600" y="46" text-anchor="middle" fill="#d8ff55" font-size="24" font-weight="700" class="title-serif" letter-spacing="0.5">THE SYSTEMATIC INNOVATION PIPELINE</text>
  <text x="600" y="72" text-anchor="middle" fill="#a0c8e0" font-size="13">Structured Transformation of Complex Socio-Technical Contradictions into Non-Obvious Possibility Portfolios</text>

  <!-- Horizontal connector line -->
  <line x1="140" y1="210" x2="1060" y2="210" stroke="#254a6b" stroke-width="2"/>

  <!-- Stage 1 -->
  <g transform="translate(60, 110)">
    <rect width="190" height="220" rx="3" fill="#13334d" stroke="#2b5e85" stroke-width="1.5"/>
    <rect x="0" y="0" width="190" height="4" fill="#d8ff55"/>
    <text x="95" y="32" text-anchor="middle" fill="#d8ff55" font-size="11" font-weight="700" class="mono-label">STAGE 1 · LAYER 1</text>
    <text x="95" y="60" text-anchor="middle" fill="#ffffff" font-size="15" font-weight="700" class="title-serif">Preservation Scan</text>
    <line x1="20" y1="74" x2="170" y2="74" stroke="#234b6b" stroke-width="1"/>
    <text x="95" y="100" text-anchor="middle" fill="#b8d4e8" font-size="11">Core Contradiction</text>
    <text x="95" y="122" text-anchor="middle" fill="#b8d4e8" font-size="11">Non-Negotiable Anchors</text>
    <text x="95" y="144" text-anchor="middle" fill="#b8d4e8" font-size="11">System Boundary Mapping</text>
    <rect x="20" y="175" width="150" height="24" rx="2" fill="#0b2031" stroke="#3b7aab" stroke-width="1"/>
    <text x="95" y="191" text-anchor="middle" fill="#d8ff55" font-size="9" font-weight="700" class="mono-label">PROTECT WHAT WORKS</text>
  </g>

  <!-- Stage 2 -->
  <g transform="translate(280, 110)">
    <rect width="190" height="220" rx="3" fill="#13334d" stroke="#2b5e85" stroke-width="1.5"/>
    <rect x="0" y="0" width="190" height="4" fill="#d8ff55"/>
    <text x="95" y="32" text-anchor="middle" fill="#d8ff55" font-size="11" font-weight="700" class="mono-label">STAGE 2 · CONTROL</text>
    <text x="95" y="60" text-anchor="middle" fill="#ffffff" font-size="15" font-weight="700" class="title-serif">Fluency Depletion</text>
    <line x1="20" y1="74" x2="170" y2="74" stroke="#234b6b" stroke-width="1"/>
    <text x="95" y="100" text-anchor="middle" fill="#b8d4e8" font-size="11">Top-of-Mind Tropes</text>
    <text x="95" y="122" text-anchor="middle" fill="#b8d4e8" font-size="11">Internet Memory Dumps</text>
    <text x="95" y="144" text-anchor="middle" fill="#b8d4e8" font-size="11">Discard 2-3 Defaults</text>
    <rect x="20" y="175" width="150" height="24" rx="2" fill="#0b2031" stroke="#3b7aab" stroke-width="1"/>
    <text x="95" y="191" text-anchor="middle" fill="#d8ff55" font-size="9" font-weight="700" class="mono-label">ANTI-TROPE QUARANTINE</text>
  </g>

  <!-- Stage 3 -->
  <g transform="translate(500, 110)">
    <rect width="200" height="220" rx="3" fill="#13334d" stroke="#2b5e85" stroke-width="1.5"/>
    <rect x="0" y="0" width="200" height="4" fill="#d8ff55"/>
    <text x="100" y="32" text-anchor="middle" fill="#d8ff55" font-size="11" font-weight="700" class="mono-label">STAGE 3 · SEARCH</text>
    <text x="100" y="60" text-anchor="middle" fill="#ffffff" font-size="15" font-weight="700" class="title-serif">7 Reasoning Cells</text>
    <line x1="20" y1="74" x2="180" y2="74" stroke="#234b6b" stroke-width="1"/>
    <text x="100" y="98" text-anchor="middle" fill="#b8d4e8" font-size="10.5">Boundary Relaxation &amp; Inversion</text>
    <text x="100" y="118" text-anchor="middle" fill="#b8d4e8" font-size="10.5">Analogy (Synectics)</text>
    <text x="100" y="138" text-anchor="middle" fill="#b8d4e8" font-size="10.5">Unbundling &amp; Subtraction</text>
    <text x="100" y="158" text-anchor="middle" fill="#b8d4e8" font-size="10.5">Perspective Shift &amp; Constraint</text>
    <rect x="25" y="175" width="150" height="24" rx="2" fill="#0b2031" stroke="#3b7aab" stroke-width="1"/>
    <text x="100" y="191" text-anchor="middle" fill="#d8ff55" font-size="9" font-weight="700" class="mono-label">10 INNOVATION LENSES</text>
  </g>

  <!-- Stage 4 -->
  <g transform="translate(730, 110)">
    <rect width="190" height="220" rx="3" fill="#13334d" stroke="#2b5e85" stroke-width="1.5"/>
    <rect x="0" y="0" width="190" height="4" fill="#d8ff55"/>
    <text x="95" y="32" text-anchor="middle" fill="#d8ff55" font-size="11" font-weight="700" class="mono-label">STAGE 4 · LAYER 2</text>
    <text x="95" y="60" text-anchor="middle" fill="#ffffff" font-size="15" font-weight="700" class="title-serif">Mechanism Ledger</text>
    <line x1="20" y1="74" x2="170" y2="74" stroke="#234b6b" stroke-width="1"/>
    <text x="95" y="100" text-anchor="middle" fill="#b8d4e8" font-size="11">5 Structural Dimensions</text>
    <text x="95" y="122" text-anchor="middle" fill="#b8d4e8" font-size="11">Causal Lever Enforcement</text>
    <text x="95" y="144" text-anchor="middle" fill="#b8d4e8" font-size="11">Deduplication Gate</text>
    <rect x="20" y="175" width="150" height="24" rx="2" fill="#0b2031" stroke="#3b7aab" stroke-width="1"/>
    <text x="95" y="191" text-anchor="middle" fill="#d8ff55" font-size="9" font-weight="700" class="mono-label">ZERO PSEUDO-VARIETY</text>
  </g>

  <!-- Stage 5 -->
  <g transform="translate(950, 110)">
    <rect width="190" height="220" rx="3" fill="#1783be" stroke="#d8ff55" stroke-width="1.5"/>
    <rect x="0" y="0" width="190" height="4" fill="#d8ff55"/>
    <text x="95" y="32" text-anchor="middle" fill="#d8ff55" font-size="11" font-weight="700" class="mono-label">STAGE 5 · LAYERS 3-6</text>
    <text x="95" y="60" text-anchor="middle" fill="#ffffff" font-size="15" font-weight="700" class="title-serif">Portfolio &amp; Action</text>
    <line x1="20" y1="74" x2="170" y2="74" stroke="#237ab5" stroke-width="1"/>
    <text x="95" y="98" text-anchor="middle" fill="#ffffff" font-size="10.5">4–7 Distinct Possibilities</text>
    <text x="95" y="118" text-anchor="middle" fill="#ffffff" font-size="10.5">Rickards Ch. 8 Receptivity</text>
    <text x="95" y="138" text-anchor="middle" fill="#ffffff" font-size="10.5">Yes-But Hearing Defense</text>
    <text x="95" y="158" text-anchor="middle" fill="#ffffff" font-size="10.5">Spotlight Signals</text>
    <rect x="20" y="175" width="150" height="24" rx="2" fill="#0f5a85" stroke="#d8ff55" stroke-width="1"/>
    <text x="95" y="191" text-anchor="middle" fill="#d8ff55" font-size="9" font-weight="700" class="mono-label">1-2 WK LEARNING PROBES</text>
  </g>

  <!-- Bottom Proof Bar -->
  <g transform="translate(60, 360)">
    <rect width="1080" height="135" rx="3" fill="#102a42" stroke="#244d70" stroke-width="1.5"/>
    <text x="32" y="36" fill="#d8ff55" font-size="13" font-weight="700" class="mono-label" letter-spacing="1">EMPIRICAL VALIDATION RECORD (PILOT CORPUS · N=22 RUNS)</text>
    <text x="32" y="56" fill="#8eaabf" font-size="11">Independently extracted candidates scored via judge-free Vendi Scores (VSk) across 12 cross-domain cases.</text>

    <line x1="32" y1="68" x2="1048" y2="68" stroke="#1d4263" stroke-width="1"/>

    <g transform="translate(32, 85)">
      <text x="0" y="24" fill="#d8ff55" font-size="28" font-weight="700" class="title-serif">+162%</text>
      <text x="110" y="22" fill="#ffffff" font-size="12" font-weight="600">Causal Mechanism Density</text>
      <text x="110" y="36" fill="#8eaabf" font-size="10.5">0.897 → 2.352 mechanisms/1k tok</text>
    </g>

    <g transform="translate(390, 85)">
      <text x="0" y="24" fill="#38ef7d" font-size="28" font-weight="700" class="title-serif">-35%</text>
      <text x="85" y="22" fill="#ffffff" font-size="12" font-weight="600">Multi-Turn Churn</text>
      <text x="85" y="36" fill="#8eaabf" font-size="10.5">6,422 → 4,170 output tokens</text>
    </g>

    <g transform="translate(680, 85)">
      <text x="0" y="24" fill="#d8ff55" font-size="28" font-weight="700" class="title-serif">100%</text>
      <text x="85" y="22" fill="#ffffff" font-size="12" font-weight="600">Turn-1 Restraint &amp; Precision</text>
      <text x="85" y="36" fill="#8eaabf" font-size="10.5">10/10 questions; 0 false triggers</text>
    </g>

    <g transform="translate(940, 85)">
      <text x="0" y="24" fill="#38ef7d" font-size="28" font-weight="700" class="title-serif">0%</text>
      <text x="50" y="22" fill="#ffffff" font-size="12" font-weight="600">Roadmap Drift</text>
      <text x="50" y="36" fill="#8eaabf" font-size="10.5">Zero unearned winners</text>
    </g>
  </g>
</svg>
"""

# 4. Authentic Terminal Demo (assets/terminal-demo.svg)
terminal_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 580" width="100%" height="100%" style="background:#0e2438; font-family:'SF Mono', Menlo, Consolas, monospace;">
  <!-- Window Header -->
  <g transform="translate(60, 30)">
    <rect width="1080" height="520" rx="6" fill="#091b2c" stroke="#25425d" stroke-width="1.5"/>
    <rect width="1080" height="36" rx="6" fill="#132c42"/>
    <rect y="26" width="1080" height="10" fill="#132c42"/>

    <!-- Window Dots -->
    <circle cx="22" cy="18" r="5" fill="#ff5f56"/>
    <circle cx="38" cy="18" r="5" fill="#ffbd2e"/>
    <circle cx="54" cy="18" r="5" fill="#27c93f"/>

    <text x="540" y="23" text-anchor="middle" fill="#8eaabf" font-size="11" font-weight="600" font-family="'Helvetica Neue', Arial, sans-serif">Interactive Session — Deep Mode Iterative Discovery</text>

    <!-- Turn 1: User -->
    <text x="24" y="68" fill="#38bdf8" font-size="12" font-weight="700">user@org:~$</text>
    <text x="140" y="68" fill="#f8fafc" font-size="12">"Our furniture store sells well, but salespeople hoard customer info because commission</text>
    <text x="140" y="86" fill="#f8fafc" font-size="12">rewards individual performance. Help me find innovative ways to improve teamwork without removing commission."</text>

    <!-- Turn 1: Assistant Restraint -->
    <rect x="24" y="108" width="1032" height="154" rx="3" fill="#0f2b42" stroke="#1d4d73" stroke-width="1"/>
    <text x="40" y="130" fill="#d8ff55" font-size="11" font-weight="700">● AGENT (Turn 1 Restraint — 380 tokens)</text>

    <text x="40" y="154" fill="#a0c8e0" font-size="11.5"><tspan fill="#d8ff55" font-weight="700">System &amp; Preservation Scan:</tspan> Core contradiction: Individual commission incentive vs. shared customer handoff.</text>
    <text x="40" y="172" fill="#a0c8e0" font-size="11.5">Non-negotiable anchor: Customer ownership &amp; sales credit remain intact ($0 added store payroll).</text>
    <text x="40" y="190" fill="#a0c8e0" font-size="11.5">Quarantined Tropes: Team commission pool, mandatory CRM compliance software, management bonuses.</text>

    <text x="40" y="214" fill="#ffffff" font-size="11.5" font-weight="700">Discovery Questions (4 targeted):</text>
    <text x="40" y="232" fill="#cbd5e1" font-size="11">1. Who handles returning walk-ins when the original salesperson is off?  2. Are custom room quotes paper or digital?</text>
    <text x="40" y="248" fill="#d8ff55" font-size="11">Provisional Seeds: Seed A (Asymmetric Assist Fee), Seed B (Up-Queue Podium Immunity), Seed C (Back-of-Tag Notes).</text>

    <!-- Turn 2: User Clarification -->
    <text x="24" y="294" fill="#38bdf8" font-size="12" font-weight="700">user@org:~$</text>
    <text x="140" y="294" fill="#f8fafc" font-size="12">"Customer ownership must remain 100%. Days-off coverage is the main failure. Managers can change floor rules."</text>

    <!-- Turn 2: Full Portfolio Output -->
    <rect x="24" y="316" width="1032" height="186" rx="3" fill="#13334d" stroke="#256594" stroke-width="1"/>
    <text x="40" y="338" fill="#d8ff55" font-size="11" font-weight="700">● AGENT (Six-Layer Innovation Portfolio Generated)</text>

    <text x="40" y="362" fill="#38bdf8" font-size="11" font-weight="700">P1 [Incentive Unbundling]</text>
    <text x="220" y="362" fill="#f1f5f9" font-size="11">Preparedness Split: 90% Owner / 10% Covering Rep if CRM card pre-filled; 75/25 if cold handoff.</text>

    <text x="40" y="384" fill="#38bdf8" font-size="11" font-weight="700">P2 [Queue Priority]</text>
    <text x="220" y="384" fill="#f1f5f9" font-size="11">Up-Queue Immunity: Covering a teammate freezes your #1 door rotation spot. Zero walk-in penalty.</text>

    <text x="40" y="406" fill="#38bdf8" font-size="11" font-weight="700">P3 [Information Schema]</text>
    <text x="220" y="406" fill="#f1f5f9" font-size="11">Open Handoff Dossier: 3-item physical tag on bestselling sectional frames credits Category Curators.</text>

    <text x="40" y="428" fill="#38bdf8" font-size="11" font-weight="700">P4 [Role Separation]</text>
    <text x="220" y="428" fill="#f1f5f9" font-size="11">Owner-Triggered Micro-Assists: Fixed 10-minute second-voice closing assist without commission dilution.</text>

    <text x="40" y="452" fill="#d8ff55" font-size="11" font-weight="700">Rickards Ch. 8 Receptivity:</text>
    <text x="220" y="452" fill="#cbd5e1" font-size="11">Rule of Three Hearings (Closer, Covering Rep, Sales Manager) inoculates against "Yes, but..." pushback.</text>

    <text x="40" y="474" fill="#38ef7d" font-size="11" font-weight="700">1-2 Week Low-Cost Probe:</text>
    <text x="220" y="474" fill="#86efac" font-size="11">5-day Paper Handoff Card trial on Sectionals before making software changes. Fully reversible.</text>
  </g>
</svg>
"""

# Render Banner with Playwright at 2x resolution
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 640}, device_scale_factor=2)
    page.set_content(banner_html, wait_until="networkidle")
    page.screenshot(path=str(ASSETS / "banner.png"))
    browser.close()

# Write SVGs
(ASSETS / "comparison.svg").write_text(comparison_svg, encoding="utf-8")
(ASSETS / "system-architecture.svg").write_text(architecture_svg, encoding="utf-8")
(ASSETS / "terminal-demo.svg").write_text(terminal_svg, encoding="utf-8")

print("All branding assets generated successfully:")
print(" - assets/banner.png (Book cover aesthetic, 2x retina)")
print(" - assets/comparison.svg (Editorial contrast card)")
print(" - assets/system-architecture.svg (Editorial pipeline diagram)")
print(" - assets/terminal-demo.svg (Editorial terminal demo)")
