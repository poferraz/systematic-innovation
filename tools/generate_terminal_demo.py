import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

demo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600" width="100%" height="100%" style="background:#090d16; font-family:-apple-system, BlinkMacSystemFont, 'SF Mono', 'Fira Code', Menlo, Consolas, monospace;">
  <defs>
    <filter id="win-shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
  </defs>

  <!-- Window Frame -->
  <g transform="translate(60, 40)" filter="url(#win-shadow)">
    <!-- Header -->
    <rect width="1080" height="520" rx="10" fill="#0d131f" stroke="#1f2c42" stroke-width="1.5"/>
    <rect width="1080" height="38" rx="10" fill="#141c2c"/>
    <rect y="28" width="1080" height="10" fill="#141c2c"/>

    <!-- Window Controls -->
    <circle cx="24" cy="19" r="6" fill="#f43f5e"/>
    <circle cx="44" cy="19" r="6" fill="#f59e0b"/>
    <circle cx="64" cy="19" r="6" fill="#10b981"/>

    <text x="540" y="24" text-anchor="middle" fill="#64748b" font-size="12" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="600">Terminal — systematic-innovation agent session (Deep Mode)</text>

    <!-- Turn 1: User -->
    <text x="24" y="70" fill="#38bdf8" font-size="13" font-weight="700">user@workspace:~$</text>
    <text x="180" y="70" fill="#f8fafc" font-size="13">"Our furniture store sells well, but salespeople hoard customer info because commission</text>
    <text x="180" y="90" fill="#f8fafc" font-size="13">rewards individual performance. Help me find innovative ways to improve teamwork without removing commission."</text>

    <!-- Turn 1: Assistant System & Preservation Scan -->
    <rect x="24" y="112" width="1032" height="160" rx="6" fill="#111a2b" stroke="#1e2c45" stroke-width="1"/>

    <text x="40" y="135" fill="#00f2fe" font-size="12" font-weight="700">● AGENT (Turn 1 Restraint — 380 tokens)</text>

    <text x="40" y="160" fill="#94a3b8" font-size="12"><tspan fill="#f6d365" font-weight="600">System &amp; Preservation Scan:</tspan> Core contradiction: individual sales attribution vs. shared floor coverage.</text>
    <text x="40" y="178" fill="#94a3b8" font-size="12">Non-negotiable anchor: Individual commission &amp; customer ownership must be protected ($0 added store payroll).</text>
    <text x="40" y="196" fill="#94a3b8" font-size="12">Quarantined Tropes: Flat team commission pool, mandatory CRM tracking software, management bonuses.</text>

    <text x="40" y="222" fill="#38ef7d" font-size="12" font-weight="600">Discovery Questions:</text>
    <text x="40" y="240" fill="#cbd5e1" font-size="12">1. Who handles returning walk-ins when the original salesperson is off?  2. Are complex quotes currently paper or digital?</text>
    <text x="40" y="258" fill="#cbd5e1" font-size="12">Provisional Seeds: Seed A (Asymmetric Assist Fee), Seed B (Up-Queue Podium Immunity), Seed C (Back-of-Tag Field Notes).</text>

    <!-- Turn 2: User Clarification -->
    <text x="24" y="305" fill="#38bdf8" font-size="13" font-weight="700">user@workspace:~$</text>
    <text x="180" y="305" fill="#f8fafc" font-size="13">"Days-off handoffs are chaotic. Customer ownership must remain 100%. Managers can adjust floor rules."</text>

    <!-- Turn 2: Six-Layer Portfolio Generated -->
    <rect x="24" y="325" width="1032" height="185" rx="6" fill="#0c1726" stroke="#1e3a5f" stroke-width="1"/>

    <text x="40" y="348" fill="#38ef7d" font-size="12" font-weight="700">● AGENT (Six-Layer Innovation Portfolio Generated)</text>

    <text x="40" y="372" fill="#38bdf8" font-size="11" font-weight="700">P1 [Incentive Unbundling]</text>
    <text x="220" y="372" fill="#e2e8f0" font-size="11">Preparedness Split: 90% Owner / 10% Covering Rep if CRM card pre-filled; 75/25 if cold handoff.</text>

    <text x="40" y="394" fill="#38bdf8" font-size="11" font-weight="700">P2 [Queue Priority]</text>
    <text x="220" y="394" fill="#e2e8f0" font-size="11">Up-Queue Immunity: Assisting a teammate freezes your #1 door rotation spot. Zero walk-in penalty.</text>

    <text x="40" y="416" fill="#38bdf8" font-size="11" font-weight="700">P3 [Information Schema]</text>
    <text x="220" y="416" fill="#e2e8f0" font-size="11">Open Handoff Dossier: 3-item physical tag on high-ticket custom sectionals credits Category Curators.</text>

    <text x="40" y="438" fill="#38bdf8" font-size="11" font-weight="700">P4 [Role Separation]</text>
    <text x="220" y="438" fill="#e2e8f0" font-size="11">Owner-Triggered Micro-Assists: Fixed 10-minute senior closer second-voice without commission dilution.</text>

    <text x="40" y="462" fill="#f6d365" font-size="11" font-weight="700">Rickards Ch. 8 Receptivity:</text>
    <text x="220" y="462" fill="#cbd5e1" font-size="11">Rule of Three Hearings (Top Producer, Assisting Rep, Sales Manager) inoculates against "Yes, but...".</text>

    <text x="40" y="484" fill="#38ef7d" font-size="11" font-weight="700">1-2 Week Low-Cost Probe:</text>
    <text x="220" y="484" fill="#86efac" font-size="11">5-day Paper Handoff Card trial on Sectionals before making digital CRM changes. Reversible &amp; zero-cost.</text>
  </g>
</svg>
"""

(ASSETS / "terminal-demo.svg").write_text(demo_svg, encoding="utf-8")
print("Generated assets/terminal-demo.svg")
