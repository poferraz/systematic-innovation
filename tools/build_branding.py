"""Render the README branding PNGs at 2x resolution via Playwright Chromium."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Final

from playwright.async_api import async_playwright

ROOT: Final[Path] = Path(__file__).resolve().parent.parent
ASSETS_DIR: Final[Path] = ROOT / "assets"

GOOGLE_FONTS_LINK: Final[str] = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?'
    "family=Fraunces:opsz,wght@9..144,600;9..144,700&"
    "family=JetBrains+Mono:wght@500;600;700&"
    "family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"
    '" rel="stylesheet">'
)

COMMON_RESET_CSS: Final[str] = """
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
html, body {
  width: 100%;
  height: 100%;
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.mono {
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
}
.serif {
  font-family: 'Fraunces', Georgia, 'Times New Roman', serif;
}
"""


def _wrap_html(width: int, height: int, css: str, body: str) -> str:
    """Wrap body markup in a fixed-viewport HTML document for Playwright."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
{GOOGLE_FONTS_LINK}
<style>
{COMMON_RESET_CSS}
body {{
  width: {width}px;
  height: {height}px;
}}
{css}
</style>
</head>
<body>
{body}
</body>
</html>"""


def build_banner_html() -> str:
    """Build v2.0.0 hero banner HTML (1280x640 logical, 2560x1280 rendered)."""
    css = """
    body {
      background: linear-gradient(135deg, #025d9c 0%, #01416f 62%, #00294a 100%);
      color: #ffffff;
      position: relative;
      padding: 46px 56px 42px 56px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .grid-overlay {
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(to right, rgba(255,255,255,0.055) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255,255,255,0.055) 1px, transparent 1px);
      background-size: 40px 40px;
      pointer-events: none;
    }
    .spine-rule {
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 10px;
      background: #f5d818;
    }
    .top-bar {
      position: relative;
      z-index: 1;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: rgba(0, 41, 74, 0.72);
      border: 1px solid rgba(245, 216, 24, 0.5);
      border-radius: 999px;
      padding: 7px 16px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: #f5d818;
    }
    .version-pill {
      background: #f5d818;
      color: #00294a;
      border-radius: 6px;
      padding: 6px 14px;
      font-size: 12.5px;
      font-weight: 700;
      letter-spacing: 0.04em;
    }
    .hero {
      position: relative;
      z-index: 1;
      margin-top: 12px;
    }
    .hero h1 {
      font-size: 68px;
      line-height: 1.04;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: #ffffff;
    }
    .hero h1 span {
      color: #f5d818;
    }
    .hero p {
      margin-top: 16px;
      max-width: 960px;
      font-size: 21px;
      line-height: 1.42;
      font-weight: 500;
      color: #d9ecfa;
    }
    .cards {
      position: relative;
      z-index: 1;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }
    .card {
      background: rgba(0, 32, 60, 0.78);
      border: 1px solid rgba(151, 206, 245, 0.28);
      border-top: 3px solid #f5d818;
      border-radius: 10px;
      padding: 16px 18px 18px 18px;
    }
    .card-kicker {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.09em;
      color: #f5d818;
      text-transform: uppercase;
      margin-bottom: 8px;
    }
    .card-title {
      font-size: 17px;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 6px;
    }
    .card-desc {
      font-size: 13px;
      line-height: 1.45;
      color: #cde3f5;
    }
    """
    body = """
    <div class="grid-overlay"></div>
    <div class="spine-rule"></div>
    <div class="top-bar">
      <div class="eyebrow mono">TUDOR RICKARDS (1985) × PROBABILISTIC ANTI-COLLAPSE ENGINE</div>
      <div class="version-pill mono">SKILL v2.0.0 · MIT</div>
    </div>
    <div class="hero">
      <h1 class="serif">Systematic <span>Innovation</span></h1>
      <p>
        Causally distinct, system-aware innovation options that preserve what already works
        while countering LLM mode collapse under hard output budgets.
      </p>
    </div>
    <div class="cards">
      <div class="card">
        <div class="card-kicker mono">01 · KERNEL</div>
        <div class="card-title">Invariant / Vehicle Split</div>
        <div class="card-desc">Separates survival constraints from swappable delivery vehicles and enforces a pre-ideation refusal gate.</div>
      </div>
      <div class="card">
        <div class="card-kicker mono">02 · DE-COLLAPSE</div>
        <div class="card-title">Trope Quarantine</div>
        <div class="card-desc">Bans a domain's top 2–3 cliches first, then dispatches 7 mechanism cells plus clustered variety checks.</div>
      </div>
      <div class="card">
        <div class="card-kicker mono">03 · BUDGET LOCK</div>
        <div class="card-title">Piped Compact Mode</div>
        <div class="card-desc">Bounded &lt;= 500w lock hit 286w &amp; 289w (2/2 on clinic &lt;= 350w; holdout 323w &lt;= 400w).</div>
      </div>
      <div class="card">
        <div class="card-kicker mono">04 · AUDIT GATE</div>
        <div class="card-title">SkillEvaluator Grade A</div>
        <div class="card-desc">100.0 / 100 (--no-llm), slim 1,640w SKILL.md (30.8%), progressive 4-file reference deck.</div>
      </div>
    </div>
    """
    return _wrap_html(1280, 640, css, body)


def build_comparison_html() -> str:
    """Build v2.0.0 comparison chart HTML (1280x420 logical, 2560x840 rendered)."""
    css = """
    body {
      background: #f4f7fb;
      color: #0f172a;
      padding: 28px 40px 26px 40px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      border-bottom: 2px solid #d5e2ef;
      padding-bottom: 12px;
    }
    .header h2 {
      font-size: 26px;
      font-weight: 700;
      color: #013a63;
      letter-spacing: -0.01em;
    }
    .header .badge {
      font-size: 11.5px;
      font-weight: 700;
      color: #025d9c;
      background: #e3eff9;
      border: 1px solid #b5d2ec;
      padding: 5px 11px;
      border-radius: 6px;
    }
    .cols {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-top: 14px;
      flex: 1;
    }
    .panel {
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      border: 1px solid #cbd9e8;
      background: #ffffff;
    }
    .panel.v2 {
      border: 2px solid #025d9c;
    }
    .panel-head {
      padding: 12px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 14px;
      font-weight: 700;
    }
    .panel.ctrl .panel-head {
      background: #e9eef5;
      color: #334155;
      border-bottom: 1px solid #cbd9e8;
    }
    .panel.v2 .panel-head {
      background: #025d9c;
      color: #ffffff;
    }
    .pill-muted {
      font-size: 11px;
      background: #cbd5e1;
      color: #1e293b;
      padding: 3px 8px;
      border-radius: 4px;
    }
    .pill-yellow {
      font-size: 11px;
      background: #f5d818;
      color: #00294a;
      padding: 3px 8px;
      border-radius: 4px;
      font-weight: 700;
    }
    .rows {
      padding: 12px 18px 14px 18px;
      display: flex;
      flex-direction: column;
      gap: 11px;
      flex: 1;
      justify-content: space-between;
    }
    .row {
      display: grid;
      grid-template-columns: 158px 1fr;
      gap: 12px;
      align-items: start;
      padding-bottom: 9px;
      border-bottom: 1px dashed #e2e8f0;
    }
    .row:last-child {
      border-bottom: none;
      padding-bottom: 0;
    }
    .tag {
      font-size: 11.5px;
      font-weight: 700;
      padding-top: 2px;
    }
    .ctrl .tag {
      color: #991b1b;
    }
    .v2 .tag {
      color: #025d9c;
    }
    .copy {
      font-size: 13px;
      line-height: 1.4;
      color: #1e293b;
    }
    .copy strong {
      color: #00294a;
    }
    """
    body = """
    <div class="header">
      <h2 class="serif">Default LLM Prompts vs. Systematic Innovation v2.0.0</h2>
      <div class="badge mono">BOUNDED BENCHMARK EVIDENCE · gpt-5.6-luna</div>
    </div>
    <div class="cols">
      <div class="panel ctrl">
        <div class="panel-head">
          <span>Typical LLM / Format-Only Control</span>
          <span class="pill-muted mono">MODE COLLAPSE RISK</span>
        </div>
        <div class="rows">
          <div class="row">
            <div class="tag mono">TYPICALITY TRAP</div>
            <div class="copy">Post-trained probability priors concentrate on mainstream tropes and near-synonym variants.</div>
          </div>
          <div class="row">
            <div class="tag mono">MISSING INVARIANTS</div>
            <div class="copy">Format control omitted Preserve checks and scored <strong>0.0 causal lever coverage</strong> on holdout.</div>
          </div>
          <div class="row">
            <div class="tag mono">BUDGET SPILLOVER</div>
            <div class="copy">Clinic &lt;= 350w prompt spilled to <strong>501w &amp; 446w (0/2 compliant)</strong>; holdout spilled to 447w.</div>
          </div>
          <div class="row">
            <div class="tag mono">BYPASS LEAKAGE</div>
            <div class="copy">On <code>fda-audit-bypass</code>, refused concealment yet still emitted <strong>10–15 options (858–1,021w)</strong>.</div>
          </div>
        </div>
      </div>
      <div class="panel v2">
        <div class="panel-head">
          <span>Systematic Innovation v2.0.0</span>
          <span class="pill-yellow mono">ANTI-COLLAPSE ENGINE</span>
        </div>
        <div class="rows">
          <div class="row">
            <div class="tag mono">TROPE QUARANTINE</div>
            <div class="copy">Bans the domain's top 2–3 cliches in negative space before dispatching 7 orthogonal mechanism cells.</div>
          </div>
          <div class="row">
            <div class="tag mono">CLUSTERED VARIETY</div>
            <div class="copy">Clinic &lt;= 350w achieved <strong>4.0/4.0 clusters</strong> &amp; <strong>VS_1.0 3.992 / 3.986</strong>; holdout hit <strong>5/5 clusters</strong>.</div>
          </div>
          <div class="row">
            <div class="tag mono">PIPED BUDGET LOCK</div>
            <div class="copy">Clinic hit <strong>286w &amp; 289w (2/2 &lt;= 350w)</strong>; public holdout hit <strong>323w (&lt;= 400w)</strong> with <strong>5/5 Preserve</strong> checks.</div>
          </div>
          <div class="row">
            <div class="tag mono">REFUSAL GATE</div>
            <div class="copy">On <code>fda-audit-bypass</code>, refused evasion upfront and withheld ideation (<strong>0 candidates, 83–105w</strong>).</div>
          </div>
        </div>
      </div>
    </div>
    """
    return _wrap_html(1280, 420, css, body)


def build_architecture_html() -> str:
    """Build v2.0.0 five-stage pipeline diagram HTML (1280x360 logical, 2560x720 rendered)."""
    css = """
    body {
      background: #00294a;
      color: #ffffff;
      padding: 26px 36px 22px 36px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(151, 206, 245, 0.25);
      padding-bottom: 11px;
    }
    .top h2 {
      font-size: 24px;
      font-weight: 700;
      color: #ffffff;
    }
    .top h2 span {
      color: #f5d818;
    }
    .top .meta {
      font-size: 11.5px;
      color: #f5d818;
      background: rgba(245, 216, 24, 0.12);
      border: 1px solid rgba(245, 216, 24, 0.45);
      border-radius: 6px;
      padding: 4px 10px;
    }
    .flow {
      display: grid;
      grid-template-columns: 1fr 22px 1fr 22px 1fr 22px 1fr 22px 1fr;
      align-items: stretch;
      margin: 14px 0 12px 0;
      flex: 1;
    }
    .stage {
      background: #01416f;
      border: 1px solid #2b7bb9;
      border-top: 3px solid #f5d818;
      border-radius: 9px;
      padding: 13px 14px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .stage-num {
      font-size: 11px;
      font-weight: 700;
      color: #f5d818;
      letter-spacing: 0.08em;
    }
    .stage-title {
      margin-top: 4px;
      font-size: 15.5px;
      font-weight: 700;
      color: #ffffff;
      line-height: 1.25;
    }
    .stage-body {
      margin-top: 8px;
      font-size: 12.2px;
      line-height: 1.42;
      color: #d6eaf8;
      flex: 1;
    }
    .stage-ref {
      margin-top: 9px;
      padding-top: 7px;
      border-top: 1px solid rgba(255,255,255,0.14);
      font-size: 10.5px;
      color: #93c5fd;
    }
    .arrow {
      display: flex;
      align-items: center;
      justify-content: center;
      color: #f5d818;
      font-size: 20px;
      font-weight: 700;
    }
    .footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(2, 93, 156, 0.45);
      border: 1px solid rgba(151, 206, 245, 0.25);
      border-radius: 7px;
      padding: 8px 14px;
      font-size: 11.5px;
      color: #e0f2fe;
    }
    .footer strong {
      color: #f5d818;
    }
    """
    body = """
    <div class="top">
      <h2 class="serif">Five-Stage Architecture — <span>Systematic Innovation v2.0.0</span></h2>
      <div class="meta mono">SOLE AUTHORITY: skills/systematic-innovation/SKILL.md</div>
    </div>
    <div class="flow">
      <div class="stage">
        <div class="stage-num mono">STAGE 01 · GATE</div>
        <div class="stage-title">Boundary &amp; Split</div>
        <div class="stage-body">Refusal gate blocks evasion prompts upfront; otherwise locks hard Invariant vs. swappable Vehicle.</div>
        <div class="stage-ref mono">SKILL.md Core Loop</div>
      </div>
      <div class="arrow">→</div>
      <div class="stage">
        <div class="stage-num mono">STAGE 02 · DE-BIAS</div>
        <div class="stage-title">Trope Quarantine</div>
        <div class="stage-body">Names and bans stereotypical surface fixes in negative space before candidate generation.</div>
        <div class="stage-ref mono">Anti-Collapse Filter</div>
      </div>
      <div class="arrow">→</div>
      <div class="stage">
        <div class="stage-num mono">STAGE 03 · LENSES</div>
        <div class="stage-title">Causal Dispatch</div>
        <div class="stage-body">Runs 3-cell Quick dispatch (System Dynamics + 2 cells), 2×2 Axes &amp; Metaphor Strip.</div>
        <div class="stage-ref mono">innovation-lenses.md</div>
      </div>
      <div class="arrow">→</div>
      <div class="stage">
        <div class="stage-num mono">STAGE 04 · FLOOR</div>
        <div class="stage-title">Clustered Variety</div>
        <div class="stage-body">Verbalized Sampling diversity floor + Preserve check guaranteeing non-negotiable survival.</div>
        <div class="stage-ref mono">lenses + output-contract</div>
      </div>
      <div class="arrow">→</div>
      <div class="stage">
        <div class="stage-num mono">STAGE 05 · LOCK</div>
        <div class="stage-title">Sell-In &amp; Output</div>
        <div class="stage-body">Applies Dual Sell-In / Sell-Out test and hard Standard, Deep, or Piped Compact (&lt;= 500w) cap.</div>
        <div class="stage-ref mono">output-contract.md</div>
      </div>
    </div>
    <div class="footer mono">
      <span><strong>PROGRESSIVE DISCLOSURE:</strong> SKILL.md = 1,640w (30.8%)</span>
      <span>deep-mode = 541w · lenses = 779w · output-contract = 1,223w · evidence = 1,144w</span>
      <span><strong>TOTAL PACK:</strong> 5,327w</span>
    </div>
    """
    return _wrap_html(1280, 360, css, body)


def build_quick_demo_html() -> str:
    """Build Piped Compact Mode demo visual HTML (1280x400 logical, 2560x800 rendered)."""
    css = """
    body {
      background: #f4f7fb;
      color: #0f172a;
      padding: 24px 36px 24px 36px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .head {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      margin-bottom: 12px;
    }
    .head h2 {
      font-size: 24px;
      font-weight: 700;
      color: #013a63;
    }
    .head .sub {
      font-size: 11.5px;
      color: #025d9c;
      font-weight: 700;
      background: #e1effa;
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid #b5d2ec;
    }
    .grid {
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 20px;
      flex: 1;
    }
    .left {
      background: #00294a;
      color: #ffffff;
      border-radius: 10px;
      border-left: 6px solid #f5d818;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .kicker {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: #f5d818;
      margin-bottom: 8px;
    }
    .prompt-box {
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.14);
      border-radius: 7px;
      padding: 11px 13px;
      font-size: 12.5px;
      line-height: 1.45;
      color: #e2f1fc;
      margin-bottom: 10px;
    }
    .spec-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 12px;
      line-height: 1.4;
      color: #cde3f5;
    }
    .spec-list strong {
      color: #f5d818;
    }
    .right {
      background: #ffffff;
      border: 2px solid #025d9c;
      border-radius: 10px;
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .telemetry {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid #dbe7f3;
      padding-bottom: 10px;
      margin-bottom: 10px;
    }
    .telemetry-title {
      font-size: 14.5px;
      font-weight: 700;
      color: #013a63;
    }
    .chips {
      display: flex;
      gap: 8px;
    }
    .chip {
      font-size: 10.5px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 5px;
      background: #025d9c;
      color: #ffffff;
      white-space: nowrap;
    }
    .chip.gold {
      background: #f5d818;
      color: #00294a;
    }
    .options {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      flex: 1;
    }
    .opt {
      background: #f8fbff;
      border: 1px solid #d4e3f2;
      border-left: 4px solid #025d9c;
      border-radius: 7px;
      padding: 10px 12px;
    }
    .opt-head {
      font-size: 12px;
      font-weight: 700;
      color: #025d9c;
      margin-bottom: 4px;
    }
    .opt-body {
      font-size: 12px;
      line-height: 1.38;
      color: #1e293b;
    }
    .preserve-bar {
      margin-top: 10px;
      background: #eef5fc;
      border: 1px solid #c3daf0;
      border-radius: 6px;
      padding: 7px 12px;
      font-size: 11.5px;
      color: #013a63;
    }
    """
    body = """
    <div class="head">
      <h2 class="serif">Piped Compact Mode — Causal Spread Under Hard Budgets</h2>
      <div class="sub mono">EVAL TRACE: iter3-budget · 286w &amp; 289w (&lt;= 350w LOCK)</div>
    </div>
    <div class="grid">
      <div class="left">
        <div>
          <div class="kicker mono">RURAL CLINIC TRACE · L1 BRIEF &amp; QUARANTINE</div>
          <div class="prompt-box">
            <strong>Prompt:</strong> Rural clinic appointment no-shows under &lt;= 350w. Preserve continuity of care; no new clinical staff.
          </div>
          <div class="spec-list">
            <div><strong>Preserve (L1):</strong> continuity of care · no new clinical staff · equitable access · privacy.</div>
            <div><strong>Constraints:</strong> existing resources; metrics inferred.</div>
            <div><strong>Quarantine:</strong> SMS reminders · late fees · gamified streaks.</div>
          </div>
        </div>
        <div class="mono" style="font-size:10.5px; color:#93c5fd; border-top:1px solid rgba(255,255,255,0.14); padding-top:9px;">
          SYNTAX: P1: &lt;Name&gt; | Lever | Intervention | Chain | Preserve | Failure | Fit
        </div>
      </div>
      <div class="right">
        <div class="telemetry">
          <div class="telemetry-title">Excerpted Rep-1 Portfolio · All L1 Preserved</div>
          <div class="chips mono">
            <span class="chip gold">286w / 350w CAP</span>
            <span class="chip">4.0 CLUSTERS</span>
            <span class="chip">VS_1.0 3.992</span>
            <span class="chip">LEVER 1.000</span>
          </div>
        </div>
        <div class="options">
          <div class="opt">
            <div class="opt-head mono">P1 · RIDE-LINKED RELEASE [conditional capacity]</div>
            <div class="opt-body"><strong>Booking rules:</strong> transport uncertainty → early release → fill. <em>Fit: negotiative—opt-in, no penalty.</em></div>
          </div>
          <div class="opt">
            <div class="opt-head mono">P2 · NEIGHBOR FILL WINDOW [reciprocal coordination]</div>
            <div class="opt-body"><strong>Cancel channel:</strong> likely absence → local network notify → nearby fill. <em>Fit: participative—consent-gated.</em></div>
          </div>
          <div class="opt">
            <div class="opt-head mono">P3 · TRAVEL-BUNDLED CLINICS [temporal accumulation]</div>
            <div class="opt-body"><strong>Schedule design:</strong> dispersed demand → same-area grouped visits. <em>Fit: mission—protect urgent slots.</em></div>
          </div>
          <div class="opt">
            <div class="opt-head mono">P4 · ARRIVAL-PROBLEM CONVERSION [liability reversal]</div>
            <div class="opt-body"><strong>Check-in process:</strong> late/no arrival → reason captured → timing adapts. <em>Fit: mission—no-shame intake.</em></div>
          </div>
        </div>
        <div class="preserve-bar">
          <strong>Preserve: all L1 + L4–L6:</strong> Spotlights (Selling-In/Out), shared tensions, and user-directed continuation — zero unrequested probes or automatic winner.
        </div>
      </div>
    </div>
    """
    return _wrap_html(1280, 400, css, body)


async def render_all() -> None:
    """Render all four README branding PNGs at 2x device scale factor."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    specs = [
        ("banner.png", 1280, 640, build_banner_html()),
        ("comparison.png", 1280, 420, build_comparison_html()),
        ("system-architecture.png", 1280, 360, build_architecture_html()),
        ("quick-demo.png", 1280, 400, build_quick_demo_html()),
    ]
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            for filename, width, height, html in specs:
                context = await browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=2,
                )
                page = await context.new_page()
                await page.set_content(html, wait_until="networkidle")
                await page.evaluate("() => document.fonts.ready")
                out_path = ASSETS_DIR / filename
                await page.screenshot(path=str(out_path))
                await context.close()
                print(f"Rendered {out_path.name} ({width * 2}x{height * 2})")
        finally:
            await browser.close()


def main() -> None:
    asyncio.run(render_all())


if __name__ == "__main__":
    main()
