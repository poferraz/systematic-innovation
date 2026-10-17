from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

COMMON_FONTS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;800;900&family=Fraunces:opsz,wght@9..144,800;9..144,900&family=Optima&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
"""

# 1. HERO BANNER (assets/banner.png) - 1280x640
banner_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
{COMMON_FONTS}
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1280px;
    height: 640px;
    background-color: #025d9c;
    background-image:
      linear-gradient(90deg, rgba(0,0,0,0.18) 0px, rgba(255,255,255,0.06) 28px, rgba(0,0,0,0.08) 34px, transparent 48px),
      radial-gradient(circle at 35% 25%, rgba(255,255,255,0.06) 0%, transparent 65%);
    color: #f5d818;
    font-family: 'Fraunces', Georgia, serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 58px 88px 52px 96px;
    position: relative;
    overflow: hidden;
  }}

  .top-section {{
    width: 100%;
  }}

  /* Exact thin-over-thick rule from the 1985 hardcover */
  .rule-top-thin {{
    height: 3px;
    background: #f5d818;
    width: 100%;
    margin-bottom: 6px;
  }}
  .rule-top-thick {{
    height: 7px;
    background: #f5d818;
    width: 100%;
    margin-bottom: 22px;
  }}

  .title {{
    font-family: 'Fraunces', serif;
    font-size: 92px;
    line-height: 0.94;
    font-weight: 900;
    letter-spacing: -0.02em;
    color: #f5d818;
    text-transform: uppercase;
    font-variation-settings: 'opsz' 144, 'wght' 900, 'SOFT' 0;
  }}

  .rule-mid-thick {{
    height: 7px;
    background: #f5d818;
    width: 100%;
    margin-top: 22px;
    margin-bottom: 14px;
  }}

  .subtitle {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 36px;
    font-weight: 600;
    color: #f5d818;
    text-align: center;
    letter-spacing: -0.01em;
    line-height: 1.15;
  }}

  .rule-sub-thick {{
    height: 7px;
    background: #f5d818;
    width: 100%;
    margin-top: 14px;
  }}

  /* Minimalist Systems Feedback Diagram in the open blue field */
  .middle-section {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 18px;
  }}

  .edition-note {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.88);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    line-height: 1.7;
  }}
  .edition-note strong {{
    color: #f5d818;
    font-weight: 800;
  }}

  .footer-section {{
    width: 100%;
  }}

  .footer-row {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 10px;
  }}

  .author {{
    font-family: 'Fraunces', serif;
    font-size: 46px;
    font-weight: 900;
    color: #f5d818;
    letter-spacing: -0.02em;
  }}

  .meta-right {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    color: #f5d818;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}

  .rule-bottom {{
    height: 4px;
    background: #f5d818;
    width: 100%;
  }}
</style>
</head>
<body>
  <div class="top-section">
    <div class="rule-top-thin"></div>
    <div class="rule-top-thick"></div>
    <div class="title">
      SYSTEMATIC<br>
      INNOVATION
    </div>
    <div class="rule-mid-thick"></div>
    <div class="subtitle">A Systems Approach to LLM Ideation</div>
    <div class="rule-sub-thick"></div>
  </div>

  <div class="middle-section">
    <div class="edition-note">
      <strong>Agent Skills Standard</strong> · Pure Markdown<br>
      Grounded in <strong>Stimulating Innovation</strong> (1985)
    </div>

    <svg width="520" height="108" viewBox="0 0 520 108">
      <rect x="2" y="14" width="136" height="54" fill="none" stroke="#f5d818" stroke-width="2.5"/>
      <text x="70" y="38" text-anchor="middle" fill="#f5d818" font-family="'Plus Jakarta Sans', sans-serif" font-size="12" font-weight="800" letter-spacing="1">1. PRESERVE</text>
      <text x="70" y="55" text-anchor="middle" fill="#ffffff" font-family="'Plus Jakarta Sans', sans-serif" font-size="11" font-weight="600">System Scan</text>

      <line x1="138" y1="41" x2="188" y2="41" stroke="#f5d818" stroke-width="2.5"/>
      <polygon points="188,41 178,35 178,47" fill="#f5d818"/>

      <rect x="188" y="14" width="144" height="54" fill="#f5d818" stroke="#f5d818" stroke-width="2.5"/>
      <text x="260" y="38" text-anchor="middle" fill="#025d9c" font-family="'Plus Jakarta Sans', sans-serif" font-size="12" font-weight="800" letter-spacing="1">2. TRANSFORM</text>
      <text x="260" y="55" text-anchor="middle" fill="#025d9c" font-family="'Plus Jakarta Sans', sans-serif" font-size="11" font-weight="700">7 Reasoning Cells</text>

      <line x1="332" y1="41" x2="382" y2="41" stroke="#f5d818" stroke-width="2.5"/>
      <polygon points="382,41 372,35 372,47" fill="#f5d818"/>

      <rect x="382" y="14" width="136" height="54" fill="none" stroke="#f5d818" stroke-width="2.5"/>
      <text x="450" y="38" text-anchor="middle" fill="#f5d818" font-family="'Plus Jakarta Sans', sans-serif" font-size="12" font-weight="800" letter-spacing="1">3. VALIDATE</text>
      <text x="450" y="55" text-anchor="middle" fill="#ffffff" font-family="'Plus Jakarta Sans', sans-serif" font-size="11" font-weight="600">Learning Probes</text>

      <path d="M 450 68 L 450 96 L 70 96 L 70 68" fill="none" stroke="#f5d818" stroke-width="2" stroke-dasharray="5,5"/>
      <polygon points="70,68 65,77 75,77" fill="#f5d818"/>
      <text x="260" y="90" text-anchor="middle" fill="#f5d818" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="700" letter-spacing="1">SELECTION ENVIRONMENT FEEDBACK</text>
    </svg>
  </div>

  <div class="footer-section">
    <div class="footer-row">
      <div class="author">After Tudor Rickards</div>
      <div class="meta-right">Pilot Lift: +162% Causal Density · 0% Roadmap Drift</div>
    </div>
    <div class="rule-bottom"></div>
  </div>
</body>
</html>
"""

# 2. DISTILLED COMPARISON GRAPHIC (assets/comparison.png) - 1280x420
comparison_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
{COMMON_FONTS}
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1280px;
    height: 420px;
    background: #025d9c;
    color: #ffffff;
    font-family: 'Plus Jakarta Sans', sans-serif;
    padding: 36px 56px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-top: 3px solid #f5d818;
    border-bottom: 6px solid #f5d818;
    padding: 12px 0;
  }}
  .header h2 {{
    font-family: 'Fraunces', serif;
    font-size: 30px;
    font-weight: 900;
    color: #f5d818;
    text-transform: uppercase;
    letter-spacing: -0.01em;
  }}
  .header span {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    color: #f5d818;
    text-transform: uppercase;
  }}
  .grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 36px;
    height: 275px;
    margin-top: 24px;
  }}
  .panel {{
    border: 2.5px solid rgba(255,255,255,0.28);
    padding: 24px 28px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: rgba(1, 52, 92, 0.55);
  }}
  .panel.active {{
    border: 3px solid #f5d818;
    background: #014c82;
  }}
  .panel-title {{
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .panel-title h3 {{
    font-family: 'Fraunces', serif;
    font-size: 24px;
    font-weight: 900;
    color: #ffffff;
  }}
  .panel.active .panel-title h3 {{
    color: #f5d818;
  }}
  .badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 10px;
    border: 1.5px solid rgba(255,255,255,0.5);
    color: #ffffff;
  }}
  .panel.active .badge {{
    background: #f5d818;
    color: #025d9c;
    border-color: #f5d818;
  }}
  .boxes {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin: 18px 0;
  }}
  .box {{
    height: 76px;
    border: 2px dashed rgba(255,255,255,0.35);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 6px;
  }}
  .box .lbl {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: rgba(255,255,255,0.7);
  }}
  .box .sub {{
    font-size: 11px;
    color: rgba(255,255,255,0.55);
    margin-top: 4px;
  }}
  .panel.active .box {{
    border: 2px solid #f5d818;
    background: rgba(245, 216, 24, 0.1);
  }}
  .panel.active .box .lbl {{
    color: #f5d818;
  }}
  .panel.active .box .sub {{
    color: #ffffff;
    font-weight: 600;
  }}
  .footer-bar {{
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    font-weight: 600;
    padding-top: 12px;
    border-top: 1.5px solid rgba(255,255,255,0.2);
    color: rgba(255,255,255,0.85);
  }}
  .panel.active .footer-bar {{
    border-top: 2px solid #f5d818;
    color: #f5d818;
    font-weight: 700;
  }}
</style>
</head>
<body>
  <div class="header">
    <h2>Mode Collapse vs. Mechanism Diversity</h2>
    <span>22 Fresh-Context Pilot Runs</span>
  </div>
  <div class="grid">
    <div class="panel">
      <div class="panel-title">
        <h3>Vanilla LLM Brainstorming</h3>
        <span class="badge">0.90 MECH / 1K TOK</span>
      </div>
      <div class="boxes">
        <div class="box"><span class="lbl">IDEA 1</span><span class="sub">Same Lever</span></div>
        <div class="box"><span class="lbl">IDEA 2</span><span class="sub">Same Lever</span></div>
        <div class="box"><span class="lbl">IDEA 3</span><span class="sub">Same Lever</span></div>
        <div class="box"><span class="lbl">IDEA 4</span><span class="sub">Same Lever</span></div>
        <div class="box"><span class="lbl">IDEA 5</span><span class="sub">Same Lever</span></div>
      </div>
      <div class="footer-bar">
        <span>✕ 0/10 Turn-1 Discovery</span>
        <span>✕ 55% Duplicate Collapse</span>
        <span>✕ 90% Roadmap Drift</span>
      </div>
    </div>

    <div class="panel active">
      <div class="panel-title">
        <h3>Systematic Innovation</h3>
        <span class="badge">2.35 MECH / 1K TOK (+162%)</span>
      </div>
      <div class="boxes">
        <div class="box"><span class="lbl">LEVER A</span><span class="sub">Incentives</span></div>
        <div class="box"><span class="lbl">LEVER B</span><span class="sub">Queue Rule</span></div>
        <div class="box"><span class="lbl">LEVER C</span><span class="sub">Info Schema</span></div>
        <div class="box"><span class="lbl">LEVER D</span><span class="sub">Inversion</span></div>
        <div class="box"><span class="lbl">LEVER E</span><span class="sub">Subtraction</span></div>
      </div>
      <div class="footer-bar">
        <span>✓ 10/10 Turn-1 Restraint</span>
        <span>✓ 100% Preservation Scan</span>
        <span>✓ 1–2 Wk Probes</span>
      </div>
    </div>
  </div>
</body>
</html>
"""

# 3. DISTILLED ARCHITECTURE PIPELINE (assets/system-architecture.png) - 1280x360
arch_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
{COMMON_FONTS}
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1280px;
    height: 360px;
    background: #025d9c;
    color: #ffffff;
    font-family: 'Plus Jakarta Sans', sans-serif;
    padding: 36px 56px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-top: 3px solid #f5d818;
    border-bottom: 6px solid #f5d818;
    padding: 12px 0;
  }}
  .header h2 {{
    font-family: 'Fraunces', serif;
    font-size: 30px;
    font-weight: 900;
    color: #f5d818;
    text-transform: uppercase;
  }}
  .header span {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    color: #f5d818;
    text-transform: uppercase;
  }}
  .flow {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 18px;
    margin-top: 22px;
  }}
  .step {{
    border: 2.5px solid #f5d818;
    background: #014c82;
    padding: 18px 16px;
    height: 145px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .step.highlight {{
    background: #f5d818;
    color: #025d9c;
  }}
  .num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    color: #f5d818;
    letter-spacing: 0.08em;
  }}
  .step.highlight .num {{
    color: #025d9c;
  }}
  .step h4 {{
    font-family: 'Fraunces', serif;
    font-size: 20px;
    font-weight: 900;
    line-height: 1.15;
    color: #ffffff;
  }}
  .step.highlight h4 {{
    color: #025d9c;
  }}
  .step p {{
    font-size: 12.5px;
    font-weight: 600;
    color: rgba(255,255,255,0.88);
  }}
  .step.highlight p {{
    color: #013c66;
    font-weight: 700;
  }}
  .feedback {{
    border-top: 3px solid #f5d818;
    padding-top: 12px;
    display: flex;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
    font-weight: 700;
    color: #f5d818;
    letter-spacing: 0.05em;
  }}
</style>
</head>
<body>
  <div class="header">
    <h2>Five-Stage Systems Architecture</h2>
    <span>Rickards (1985) Search &amp; Selection Model</span>
  </div>

  <div class="flow">
    <div class="step">
      <div class="num">01 · LAYER 1</div>
      <h4>Preservation Scan</h4>
      <p>Protect core anchors &amp; map boundaries</p>
    </div>
    <div class="step">
      <div class="num">02 · QUARANTINE</div>
      <h4>Fluency Depletion</h4>
      <p>Set aside top 2–3 default cliches</p>
    </div>
    <div class="step highlight">
      <div class="num">03 · SEARCH</div>
      <h4>7 Reasoning Cells</h4>
      <p>Inversion, Synectics, Unbundling, Purge</p>
    </div>
    <div class="step">
      <div class="num">04 · LAYER 2</div>
      <h4>Mechanism Ledger</h4>
      <p>Enforce 5 structural dimensions</p>
    </div>
    <div class="step">
      <div class="num">05 · LAYERS 3–6</div>
      <h4>Action Portfolio</h4>
      <p>Ch. 8 Receptivity &amp; 1–2 Wk Probes</p>
    </div>
  </div>

  <div class="feedback">
    <span>▲ DEEP MODE: TURN-1 RESTRAINT (&le; 4 Questions + 3 Seeds)</span>
    <span>QUICK MODE: SINGLE-TURN 6-LAYER PORTFOLIO ▲</span>
  </div>
</body>
</html>
"""

# 4. DISTILLED WORKFLOW DEMO (assets/quick-demo.png) - 1280x400
demo_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
{COMMON_FONTS}
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1280px;
    height: 400px;
    background: #025d9c;
    color: #ffffff;
    font-family: 'Plus Jakarta Sans', sans-serif;
    padding: 36px 56px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-top: 3px solid #f5d818;
    border-bottom: 6px solid #f5d818;
    padding: 12px 0;
  }}
  .header h2 {{
    font-family: 'Fraunces', serif;
    font-size: 30px;
    font-weight: 900;
    color: #f5d818;
    text-transform: uppercase;
  }}
  .header span {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    color: #f5d818;
  }}
  .turns {{
    display: grid;
    grid-template-columns: 1fr 1.25fr;
    gap: 32px;
    height: 255px;
    margin-top: 20px;
  }}
  .card {{
    background: #014c82;
    border: 2.5px solid #f5d818;
    padding: 22px 26px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .card-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid rgba(245,216,24,0.35);
    padding-bottom: 10px;
  }}
  .card-head h3 {{
    font-family: 'Fraunces', serif;
    font-size: 22px;
    font-weight: 900;
    color: #f5d818;
  }}
  .pill {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    background: #f5d818;
    color: #025d9c;
    padding: 3px 9px;
  }}
  .items {{
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}
  .item {{
    display: flex;
    align-items: baseline;
    gap: 10px;
    font-size: 14px;
    line-height: 1.35;
  }}
  .item strong {{
    color: #f5d818;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    min-width: 125px;
  }}
  .note {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    color: #f5d818;
    border-top: 1.5px solid rgba(245,216,24,0.35);
    padding-top: 8px;
  }}
</style>
</head>
<body>
  <div class="header">
    <h2>Interactive Protocol: Deep Mode In Action</h2>
    <span>Case: Retail Commission Teamwork</span>
  </div>

  <div class="turns">
    <div class="card">
      <div class="card-head">
        <h3>Turn 1: Diagnostic Restraint</h3>
        <span class="pill">413 TOKENS</span>
      </div>
      <div class="items">
        <div class="item"><strong>PRESERVE</strong><span>100% individual customer ownership &amp; commission</span></div>
        <div class="item"><strong>QUARANTINE</strong><span>Team pool splits, paid CRM software, cash spiffs</span></div>
        <div class="item"><strong>DISCOVER</strong><span>4 surgical questions on day-off handoffs &amp; quotes</span></div>
        <div class="item"><strong>3 SEEDS</strong><span>Contrasting 1-sentence directional previews</span></div>
      </div>
      <div class="note">✓ Zero premature solution dumping before constraints</div>
    </div>

    <div class="card">
      <div class="card-head">
        <h3>Turn 2: Six-Layer Portfolio</h3>
        <span class="pill">6 DISTINCT LEVERS</span>
      </div>
      <div class="items">
        <div class="item"><strong>P1 INCENTIVE</strong><span>90/10 Prepared Handoff Card vs. 75/25 Cold Rescue</span></div>
        <div class="item"><strong>P2 QUEUE</strong><span>Up-Queue Podium Immunity while assisting peers</span></div>
        <div class="item"><strong>P3 SCHEMA</strong><span>Back-of-Tag Field Notes crediting Category Curators</span></div>
        <div class="item"><strong>P4 CH. 8 PATH</strong><span>3 Stakeholder Hearings + 5-day paper card probe</span></div>
      </div>
      <div class="note">✓ 8.2x efficiency lift over vanilla baseline (1.36 vs 0.17)</div>
    </div>
  </div>
</body>
</html>
"""

with sync_playwright() as p:
    browser = p.chromium.launch()

    # 1. Banner
    p1 = browser.new_page(viewport={"width": 1280, "height": 640}, device_scale_factor=2)
    p1.set_content(banner_html, wait_until="networkidle")
    p1.screenshot(path=str(ASSETS / "banner.png"))

    # 2. Comparison
    p2 = browser.new_page(viewport={"width": 1280, "height": 420}, device_scale_factor=2)
    p2.set_content(comparison_html, wait_until="networkidle")
    p2.screenshot(path=str(ASSETS / "comparison.png"))

    # 3. System Architecture
    p3 = browser.new_page(viewport={"width": 1280, "height": 360}, device_scale_factor=2)
    p3.set_content(arch_html, wait_until="networkidle")
    p3.screenshot(path=str(ASSETS / "system-architecture.png"))

    # 4. Quick Demo
    p4 = browser.new_page(viewport={"width": 1280, "height": 400}, device_scale_factor=2)
    p4.set_content(demo_html, wait_until="networkidle")
    p4.screenshot(path=str(ASSETS / "quick-demo.png"))

    browser.close()

print("Rendered all 4 unified brand assets at 2x Retina in #025d9c & #f5d818")
