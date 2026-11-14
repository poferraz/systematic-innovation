# SkillEvaluator Final Gate Report (2026-11-14)

- **Tool:** `skillevaluator, version 0.9.0` (external installation invoked outside repository tree)
- **Target:** `skills/systematic-innovation/` (`version: "2.0.0"`, `license: MIT`, `guide-only`)
- **Verified Commit State:** `a16cad08a4b5302086ff2dbdade7fce77bc52110` (`stress-test/five-cycle-refinement`; skill pack unchanged since `05a23b1`, `SKILL.md` SHA-256 `d5971f6e3e646916e2a287c5a8fde96a93b811ed071c362526c605ef222a890b`)
- **Commands Run:**
  - `skillevaluator quality-check skills/systematic-innovation -r cli,json`
  - `skillevaluator tier1 skills/systematic-innovation --no-llm -r cli,json`
- **Raw Output Artifact (machine paths redacted):** [`evals/audits/2026-11-14-skillevaluator-tier1-final.json`](2026-11-14-skillevaluator-tier1-final.json)

---

## 1. Baseline vs. Final Comparison (`--no-llm`, Keyless Gate)

| Dimension / Indicator | Baseline (`2026-11-14-skillevaluator-tier1-baseline.json`) | Final (`2026-11-14-skillevaluator-tier1-final.json`) | Change |
| --- | ---: | ---: | --- |
| **Overall Quality Score** | `86.0 / 100` (`Grade B`) | **`100.0 / 100` (`Grade A`)** | `+14.0` (`B -> A`) |
| **Correctness** (`w = 0.35`) | `80.0` (`4` issues) | `100.0` (`0` issues) | `+20.0` |
| **Discoverability** (`w = 0.25`) | `90.0` (`2` issues) | `100.0` (`0` issues) | `+10.0` |
| **Reliability** (`w = 0.25`) | `85.0` (`3` issues) | `100.0` (`0` issues) | `+15.0` |
| **Efficiency** (`w = 0.15`) | `95.0` (`1` issue) | `100.0` (`0` issues) | `+5.0` |
| **Total Unique Findings** | `15` (`5 medium, 8 low, 2 info`) | **`4` (`0 critical, 0 high, 0 medium, 1 low, 3 info`)** | `-11` (`0 medium+`) |
| **`has_examples` / `has_instructions`** | `false` / `false` | `true` / `true` | Resolved |
| **`SKILL.md` Lines / Tokens** | `2,565` total est. tokens | `126 / 500` lines; `3,116 / 5,000` est. tokens (`characters/4`) | Within budget |
| **Progressive Pack Split (`wc -w`)** | — | `SKILL.md`: `1,640` of `5,327` words (`30.8%`) | Balanced split |

---

## 2. Final Tier 1 Validator Matrix (`9/9` Passed, `4` N/A)

| Validator | Status | Outcome Details |
| --- | --- | --- |
| `Schema & Repository Governance` | `PASS` | `10` checks passed (`manifest_exists`, `frontmatter_valid` desc len `139`, `folder_hierarchy`, `naming_convention`, `line_count` `126/500`, `body_heading`, `## Instructions`, `## Examples`, `optional_files: ['references']`, `name_consistency`) |
| `Security Scan` | `PASS` | `skillspector` security scan passed (`1` check passed, `0` findings) |
| `PII Scan` | `PASS` | `2` checks passed, `0` findings |
| `License Compliance` | `PASS` | `1` check passed (`MIT`), `0` findings |
| `Secrets Detection` | `PASS` | `gitleaks` check passed (`1` check passed, `0` findings) |
| `Code Integrity & Hygiene` | `PASS` | `0` security findings (`guide-only` package without runnable Python tests under `skills/`) |
| `Unicode Smuggling Detection` | `PASS` | `1` check passed, `0` findings |
| `QUALITY` | `PASS` | `1` check passed; `100.0 / 100` (`Grade A`) |
| `Harness Compatibility` | `PASS` | `OK` (`0` errors; reload advisories noted below) |
| `Semantic Version Validation` | `N/A` | No semver git tag label present |
| `Code Risk Analysis` | `N/A` | No code files inside skill folder (`guide-only`) |
| `Dependency Vulnerability Audit` | `N/A` | Zero dependency manifests inside skill folder |
| `SCRIPT_LINT` | `N/A` | No `scripts/` or `tools/` directory inside skill folder |

---

## 3. Residual Non-Blocking Findings (`4` Unique)

1. **`[SCHEMA-LOW]` `unknown_field` (`skills/systematic-innovation/SKILL.md`):** Top-level `version: "2.0.0"` field outside the `agentskills.io` minimal frontmatter spec. Retained intentionally for internal pack manifest compatibility enforced by [`tests/test_skill_structure.py`](../../tests/test_skill_structure.py).
2. **`[SCHEMA-INFO]` `author_without_email` (`skills/systematic-innovation/SKILL.md`):** `metadata.author: systematic-innovation maintainers` omits a contact email address (`registry` profile optional rule; accepted under `default` profile).
3. **`[HARNESS-INFO]` `CP-RELOAD` (`copilot-cli`):** New skills require `/skills reload` or restart in `copilot-cli`.
4. **`[HARNESS-INFO]` `OC-RELOAD` (`opencode`):** Skill list and text cache at startup in `opencode`.

---

## 4. Scope Boundary (`--no-llm`)

- `workflow.tier = 1`, `workflow.stages.validation.status = "passed"`, and `publication_status = "incomplete"` because `workflow.stages.llm.status = "skipped"` (`"LLM checks disabled by --no-llm."`).
- `SkillEvaluator` Tier 2 (embedding similarity/deduplication) and Tier 3 (live Harbor sandbox evaluation) require external LLM/embedding provider configuration (`SKILL_EVAL_LLM_PROVIDER` and API credentials) and were not run in this keyless check.
- Live v2 bounded stress diagnostics (`40` persisted + `1` transient = `41` `codex exec` calls on `gpt-5.6-luna`) are documented separately with full calibration limits in [`evals/v2-loop/report.md`](../v2-loop/report.md).
