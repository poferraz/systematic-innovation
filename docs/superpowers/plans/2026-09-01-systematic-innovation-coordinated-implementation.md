# Systematic Innovation Coordinated Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute the three approved component plans as one dependency-ordered program while adding the canonical-core evidence shell required by the approved repository architecture.

**Architecture:** `skills/systematic-innovation/` remains the only editable behavioral authority. The existing skill, runner, and study plans retain ownership of their component files; this plan owns only root routing, repository validation, deterministic distribution, compatibility evidence validation, restricted-run authorization, CI, release provenance, and cross-plan acceptance evidence. The execution order below interleaves those four workstreams so no file or public claim has competing owners.

**Tech Stack:** CPython 3.13 development runtime with 3.11-3.14 compatibility, uv 0.12.8 and one committed benchmark lockfile, Python standard library for core repository tooling, locked PyYAML for YAML evidence, pytest 8, Ruff, Mypy, GitHub Actions pinned to full commit SHAs, deterministic ZIP, SHA-256, GitHub artifact attestations

**Spec:** `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md` and `docs/superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md`

## Global Constraints

1. `skills/systematic-innovation/` is the sole editable authority for public skill behavior.
2. Plans execute approved specifications and never supersede them.
3. The public skill has no runtime dependency on Python, uv, GitHub, a provider, or repository tooling.
4. Repository development uses CPython 3.13; code must pass on CPython 3.11, 3.13, and 3.14.
5. uv is pinned to `0.12.8`; `benchmark/uv.lock` is committed and CI uses `uv run --locked`.
6. Generated distributions are release-only, ignored by Git, reproducible, provenance-bound, and tested after extraction.
7. Compatibility dimensions remain independent and use only the states approved in the architecture specification.
8. No adapter is built until retained host evidence demonstrates a specific incompatibility.
9. Restricted material remains outside Git, ordinary CI, generated archives, caches, logs, and automatic agent context.
10. Restricted execution fails closed unless every frozen revision, digest, custody, provider, egress, credential, storage, and authorization field passes.
11. Public development diagnostics may guide changes; restricted validation yields only the preregistered release decision; the sealed test is terminal.
12. CI uses least privilege, bounded timeouts, concurrency cancellation, and full-SHA action pins.
13. GitHub Releases is the initial release channel; releases are gate-driven SemVer tags rather than calendar-driven.
14. GitHub artifact attestations authenticate public releases; SHA-256 alone is recorded as integrity evidence, not origin proof.
15. Generated archives remain release-only until evidence demonstrates a need for a committed catalog.
16. Every task follows RED, GREEN, REFACTOR and ends with a focused commit.

---

## Ownership and Execution Order

| Sequence | Work | File owner | Gate unlocked |
| --- | --- | --- | --- |
| 1 | Coordinated Task 1 | This plan | AR-02 and AR-12 routing baseline |
| 2 | Skill plan Tasks 1-8 | Skill plan | Canonical candidate exists |
| 3 | Runner plan Task 1 | Runner plan | `benchmark/pyproject.toml` exists |
| 4 | Coordinated Tasks 2-4 | This plan | Locked tooling, repository validation, reproducible artifact |
| 5 | Runner plan Tasks 2-13 | Runner plan | Provider-neutral runner exists |
| 6 | Coordinated Tasks 5-7 | This plan | Compatibility, restricted preflight, and CI contracts exist |
| 7 | Study plan Tasks 1-11 | Study plan | Public development candidate is frozen |
| 8 | Study plan Task 12 | Study plan, gated by Coordinated Task 6 | Restricted validation decision exists |
| 9 | Study plan Task 13 | Study plan, consuming Coordinated Task 5 | Compatibility evidence exists |
| 10 | Study plan Tasks 14-15 | Study plan | Sealed study stops and handoff exists |
| 11 | Coordinated Tasks 8-9 | This plan | Authenticated release and AR-01..AR-12 record |

`README.md`, `SECURITY.md`, and `LICENSE` remain owned by Skill plan Task 7. `benchmark/study/integration-matrix.yaml` remains owned by Study plan Task 13. This plan validates those files but does not maintain a second copy.

## Planned File Map

| File | Responsibility |
| --- | --- |
| `AGENTS.md` | Thin provider-neutral orientation and authority routing |
| `.python-version` | CPython `3.13` development pin |
| `.gitignore` | Exclude environments, generated artifacts, runs, caches, and restricted material |
| `.gitattributes` | Stable text normalization and archive inputs |
| `tools/repository/__main__.py` | `validate`, `package`, `verify-artifact`, `verify-compatibility`, and `acceptance` commands |
| `tools/repository/authority.py` | Authority, link, shadow-source, and plan-supremacy checks |
| `tools/repository/isolation.py` | Restricted-content, secret, and release-input isolation checks |
| `tools/repository/package.py` | Deterministic canonical-skill ZIP builder and verifier |
| `tools/repository/compatibility.py` | Compatibility matrix schema, state, staleness, and claim-profile validation |
| `tools/repository/acceptance.py` | AR-01 through AR-12 evidence inventory and blocking gate |
| `tests/repository/` | Deterministic tests and safe fixtures for repository tooling |
| `release/policy.json` | Tag, artifact, normalization, attestation identity, and verification policy |
| `release/manifest.schema.json` | Public release provenance contract |
| `release/revocations.json` | Explicit denylist of withdrawn artifact digests with reason and date |
| `compatibility/schema.json` | Host evidence contract for six independent dimensions |
| `compatibility/claim-profiles.json` | Exact conjunctions allowed for named public claim profiles |
| `benchmark/src/systematic_innovation_bench/restricted_preflight.py` | Fail-closed restricted-run authorization |
| `benchmark/schemas/restricted-preflight.schema.json` | Content-free public preflight contract |
| `.github/workflows/ci.yml` | Least-privilege deterministic public checks |
| `.github/workflows/release.yml` | Tag-gated reproducible build, verification, attestation, and GitHub Release |
| `.github/dependabot.yml` | Reviewable monthly Python and Actions updates |
| `docs/governance/control-register.md` | Active controls, protected risks, and explicit deferral triggers |
| `docs/release.md` | Public build, digest, attestation, and install-from-release verification |
| `docs/security/restricted-execution.md` | Operator custody and fail-closed preflight procedure |
| `evidence/architecture/acceptance.json` | Machine-readable AR-01..AR-12 result inventory |

### Task 1: Establish Thin Root Routing and Authority Tests

**Files:**

- Create: `AGENTS.md`
- Create: `.gitignore`
- Create: `.gitattributes`
- Create: `tools/__init__.py`
- Create: `tools/repository/__init__.py`
- Create: `tools/repository/authority.py`
- Create: `tests/repository/__init__.py`
- Create: `tests/repository/test_authority.py`

**Interfaces:**

- Produces: `scan_authority(root: Path) -> list[str]` where an empty list is a pass.
- Constrains: every later plan and generated artifact.

- [ ] **Step 1: Write the failing authority tests**

```python
from pathlib import Path
import unittest
from tools.repository.authority import scan_authority

ROOT = Path(__file__).resolve().parents[2]

class AuthorityTests(unittest.TestCase):
    def test_repository_has_one_declared_behavioral_authority(self):
        self.assertEqual(scan_authority(ROOT), [])

    def test_plans_do_not_claim_contractual_supremacy(self):
        for plan in (ROOT / "docs/superpowers/plans").glob("*.md"):
            text = plan.read_text(encoding="utf-8").lower()
            forbidden = "supersede " + "conflicting"
            self.assertNotIn(forbidden, text, plan)
```

- [ ] **Step 2: Run RED**

Run: `uv run --no-project --python 3.13 python -m unittest discover -s tests/repository -v`

Expected: import failure because `tools.repository.authority` is absent.

- [ ] **Step 3: Implement routing and checks**

Write `AGENTS.md` with only: project purpose; the reading order `CONTEXT.md`, both specs, coordinated plan, then the applicable component plan; the canonical skill path; generated and restricted boundaries; and the rule that host mechanics cannot change behavior. Implement `scan_authority` to require those links, require exactly one declared canonical path, reject behavioral copies outside the canonical skill, and reject plan-supremacy language.

`.gitignore` must include `.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `dist/`, `benchmark/runs/`, `restricted/`, `*.restricted.*`, and the imported `systematic-innovation-session.bundle`. `.gitattributes` must set `* text=auto eol=lf` and mark `*.zip binary`.

- [ ] **Step 4: Run GREEN and commit**

```bash
uv run --no-project --python 3.13 python -m unittest discover -s tests/repository -v
git add AGENTS.md .gitignore .gitattributes tools tests/repository
git commit -m "chore: establish repository authority routing"
```

### Task 2: Pin the Development Toolchain and Lock Runner Dependencies

**Files:**

- Create: `.python-version`
- Modify after Runner Task 1 creates it: `benchmark/pyproject.toml`
- Create: `benchmark/uv.lock`
- Create: `tests/repository/test_toolchain.py`

**Interfaces:**

- Produces: CPython `3.13`, uv `0.12.8`, and a lock compatible with Python 3.11-3.14.
- Depends on: Runner plan Task 1.

- [ ] **Step 1: Write the failing pin test**

```python
from pathlib import Path
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[2]

class ToolchainTests(unittest.TestCase):
    def test_toolchain_is_explicit_and_locked(self):
        self.assertEqual((ROOT / ".python-version").read_text().strip(), "3.13")
        data = tomllib.loads((ROOT / "benchmark/pyproject.toml").read_text())
        self.assertEqual(data["project"]["requires-python"], ">=3.11,<3.15")
        self.assertEqual(data["tool"]["uv"]["required-version"], "==0.12.8")
        self.assertTrue((ROOT / "benchmark/uv.lock").is_file())
```

- [ ] **Step 2: Run RED**

Run: `uv run --no-project --python 3.13 python -m unittest tests.repository.test_toolchain -v`

Expected: failure because the pin and lock do not yet exist.

- [ ] **Step 3: Add the exact configuration and lock**

Add `requires-python = ">=3.11,<3.15"` under `[project]` and:

```toml
[tool.uv]
required-version = "==0.12.8"
```

Then run `cd benchmark && uv lock` and `uv run --locked pytest tests/test_models.py -v`.

- [ ] **Step 4: Verify the support matrix and commit**

Run the toolchain test on 3.13, then run the runner model tests with `uv run --locked --python 3.11`, `3.13`, and `3.14`. Commit `.python-version`, `benchmark/pyproject.toml`, `benchmark/uv.lock`, and the test with message `chore: pin reproducible Python toolchain`.

### Task 3: Enforce Public-Source Isolation and Repository Validation

**Files:**

- Create: `tools/repository/isolation.py`
- Create: `tools/repository/__main__.py`
- Create: `tests/repository/fixtures/leaking-tree/restricted/validation.yaml`
- Create: `tests/repository/test_isolation.py`

**Interfaces:**

- Produces: `scan_public_tree(root: Path) -> list[Violation]` and CLI `python -m tools.repository validate`.
- `Violation` has `code`, `path`, and `message`; messages never contain matched secret content.

- [ ] **Step 1: Write RED tests**

Test that the safe repository passes; the synthetic leaking tree fails with code `RESTRICTED_PATH`; likely credential names fail with `SECRET_KEY_NAME`; canonical behavior outside `skills/systematic-innovation/` fails with `SHADOW_AUTHORITY`; and no diagnostic echoes fixture content.

- [ ] **Step 2: Run RED**

Run: `uv run --no-project --python 3.13 python -m unittest tests.repository.test_isolation -v`

Expected: import failure for `tools.repository.isolation`.

- [ ] **Step 3: Implement deterministic, non-repairing validation**

Inspect tracked paths from `git ls-files -z`, never unrestricted filesystem globs. Reject restricted path markers, private-pack extensions, credential-key assignments, generated archives, broken canonical references, and source paths outside the declared release allowlist. Return path and rule code only; never print matched values and never alter files.

- [ ] **Step 4: Run and commit**

```bash
uv run --no-project --python 3.13 python -m tools.repository validate
uv run --no-project --python 3.13 python -m unittest discover -s tests/repository -v
git add tools/repository tests/repository
git commit -m "test: enforce public source isolation"
```

### Task 4: Build and Verify a Reproducible Canonical Distribution

**Files:**

- Create: `tools/repository/package.py`
- Create: `release/policy.json`
- Create: `release/manifest.schema.json`
- Create: `tests/repository/test_package.py`

**Interfaces:**

- Produces: `build_skill(source, output, version, revision) -> ReleaseManifest`.
- Archive contains one top-level `systematic-innovation/` directory and only canonical skill files.

- [ ] **Step 1: Write failing reproducibility and isolation tests**

Build twice in different temporary directories. Assert byte-identical ZIP SHA-256 values, sorted POSIX paths, timestamp `(1980, 1, 1, 0, 0, 0)`, normalized `0644` files, no symlinks, no traversal paths, no repository documents, and successful structural validation after extraction.

- [ ] **Step 2: Run RED**

Run: `uv run --no-project --python 3.13 python -m unittest tests.repository.test_package -v`

Expected: import failure for `tools.repository.package`.

- [ ] **Step 3: Implement normalized ZIP and manifest generation**

Use `zipfile.ZipFile(..., compression=ZIP_DEFLATED, compresslevel=9)`, sorted relative paths, fixed timestamps, explicit Unix permissions, UTF-8 names, and rejection of symlinks. Manifest fields are `schema_version`, `skill_name`, `version`, `source_revision`, `build_tool_version`, `payload_sha256`, `files` with per-file hashes, and `normalization`.

Set `release/policy.json` to GitHub Releases, SemVer tags matching `^v[0-9]+\.[0-9]+\.[0-9]+$`, release-only archives, and trusted workflow `.github/workflows/release.yml` on tag refs.

- [ ] **Step 4: Verify two clean builds and commit**

Run the package tests, then build twice from clean temporary clones and compare `shasum -a 256`. Commit with `feat: add reproducible skill packaging` without adding `dist/`.

### Task 5: Validate Independent Compatibility Evidence

**Files:**

- Create: `compatibility/schema.json`
- Create: `compatibility/claim-profiles.json`
- Create: `compatibility/README.md`
- Create: `tools/repository/compatibility.py`
- Create: `tests/repository/test_compatibility.py`

**Interfaces:**

- Produces: `validate_host_record(record, as_of) -> list[Violation]` and `evaluate_claim(profile, records, as_of) -> ClaimResult`.
- Consumed by: Study plan Task 13 and the release gate.

- [ ] **Step 1: Write failing matrix tests**

Cover all six dimensions and every allowed state. Prove that installation does not imply discovery, explicit activation does not imply automatic activation, `not-claimed` is legal only for automatic activation, overdue evidence becomes `stale`, and a broad claim fails unless its exact profile passes for three distinct families with `behavioral_conformance: passed`.

- [ ] **Step 2: Run RED**

Run: `uv run --no-project --python 3.13 python -m unittest tests.repository.test_compatibility -v`

Expected: import failure for `tools.repository.compatibility`.

- [ ] **Step 3: Implement schema and claim evaluation**

Require the fields listed in Study plan Task 13. Store statuses as maps keyed by `format_conformance`, `installation`, `discovery`, `explicit_activation`, `automatic_activation`, and `behavioral_conformance`. A claim profile declares required dimensions and minimum distinct families; evaluation never mutates or upgrades evidence.

- [ ] **Step 4: Run and commit**

Run compatibility tests plus `python -m tools.repository verify-compatibility benchmark/study/integration-matrix.yaml` after Study Task 13 creates the matrix. Commit with `feat: validate compatibility evidence matrix`.

### Task 6: Add Fail-Closed Restricted Execution Preflight

**Files:**

- Create: `benchmark/src/systematic_innovation_bench/restricted_preflight.py`
- Create: `benchmark/schemas/restricted-preflight.schema.json`
- Create: `benchmark/configs/restricted-preflight.example.yaml`
- Create: `benchmark/tests/test_restricted_preflight.py`
- Create: `docs/security/restricted-execution.md`
- Modify: `benchmark/src/systematic_innovation_bench/cli.py`

**Interfaces:**

- Produces: `authorize_restricted_run(declaration: RestrictedDeclaration) -> AuthorizationRecord` and `sib restricted-preflight`.
- A successful record contains digests and decisions but no prompts, labels, annotations, credentials, or restricted paths beyond operator-approved logical identifiers.

- [ ] **Step 1: Write failing authorization tests**

Parameterize failures for runner revision mismatch, dirty worktree, lock digest mismatch, pack digest mismatch, unauthorized stage, undeclared provider/model/account/adapter, excessive input or output access, undeclared egress, unfiltered environment, missing retention/training/regional policy, inadequate storage controls, and absent operator approval. Assert every case exits nonzero before adapter execution and never echoes fixture secrets.

- [ ] **Step 2: Run RED**

Run: `cd benchmark && uv run --locked pytest tests/test_restricted_preflight.py -v`

Expected: import failure for `restricted_preflight`.

- [ ] **Step 3: Implement authorization and CLI boundary**

Use typed Pydantic records, SHA-256 streaming digests, `git status --porcelain=v1`, exact revision comparison, explicit endpoint allowlists, environment-key allowlists, and an operator approval object containing approver, timestamp, study stage, candidate digest, and declaration digest. The command writes the authorization record only after every check passes and does not launch the run.

- [ ] **Step 4: Document custody and commit**

Document controlled external storage, access control, encryption at rest, backups/sync/indexing exclusions, temporary-file handling, retention/deletion, declared provider handling, contamination response, and the validation-versus-sealed feedback boundary. Run the full benchmark suite and commit with `feat: gate restricted execution with preflight`.

### Task 7: Add Least-Privilege Public CI

**Files:**

- Create: `.github/workflows/ci.yml`
- Create: `.github/dependabot.yml`
- Create: `tests/repository/test_workflows.py`

**Interfaces:**

- Produces: public CI requiring no secrets or restricted pack.
- Uses: `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` and `astral-sh/setup-uv@c771a70e6277c0a99b617c7a806ffedaca235ff9`.

- [ ] **Step 1: Write failing workflow-policy tests**

Require `permissions: contents: read`, `timeout-minutes: 15`, concurrency cancellation, full 40-character action SHAs, no `pull_request_target`, no secrets, no write token, and no restricted paths. Require jobs for repository checks and benchmark tests on Python 3.11, 3.13, and 3.14.

- [ ] **Step 2: Run RED**

Run: `uv run --no-project --python 3.13 python -m unittest tests.repository.test_workflows -v`

Expected: failure because CI is absent.

- [ ] **Step 3: Implement CI and dependency review cadence**

CI runs `python -m tools.repository validate`, root unit tests, `uv lock --check`, `uv run --locked pytest -q`, `uv run --locked ruff check .`, and `uv run --locked mypy src`. Dependabot runs monthly for `pip` in `/benchmark` and `github-actions` in `/`, with separate labeled pull requests.

- [ ] **Step 4: Run locally and commit**

Run every CI command locally. Commit with `ci: add least-privilege public checks`.

### Task 8: Publish Only Reproducible, Attested Releases

**Files:**

- Create: `.github/workflows/release.yml`
- Create: `docs/release.md`
- Create: `release/revocations.json`
- Create: `tests/repository/test_release_workflow.py`

**Interfaces:**

- Produces: tag-gated ZIP, manifest, SHA-256 file, GitHub attestation, install-from-release result, and GitHub Release.
- Uses: checkout and setup-uv pins from Task 7 plus `actions/attest@59d89421af93a897026c735860bf21b6eb4f7b26`.

- [ ] **Step 1: Write failing release-policy tests**

Require tag-only execution; release-job permissions limited to `contents: write`, `id-token: write`, and `attestations: write`; a clean build; two independent build directories; digest equality; source-isolation scan; extraction and install smoke test; attestation before publication; and failure on any mismatch. Require the verifier to reject every digest listed in `release/revocations.json` even when its historical attestation is cryptographically valid.

- [ ] **Step 2: Run RED**

Run: `uv run --no-project --python 3.13 python -m unittest tests.repository.test_release_workflow -v`

Expected: failure because the release workflow is absent.

- [ ] **Step 3: Implement authenticated release flow**

Build twice with Task 4, compare bytes, verify the manifest, extract into a temporary host-install root, run the skill validator against the extracted directory, call `actions/attest` with the ZIP subject path, then create the GitHub Release with ZIP, manifest, and SHA-256 file. Set `persist-credentials: false` on checkout and a 15-minute timeout.

- [ ] **Step 4: Document verification and commit**

Document `gh attestation verify ARTIFACT.zip --repo poferraz/systematic-innovation`, SHA-256 verification, trusted workflow identity, identity rotation through reviewed workflow changes, and install-from-artifact validation. Revocation means adding the digest, reason, and date to `release/revocations.json`, marking the GitHub Release withdrawn, removing its downloadable artifact, and publishing a security advisory; verification must check the denylist before accepting a valid attestation. Commit with `ci: attest reproducible skill releases`.

### Task 9: Close AR-01 Through AR-12 with Explicit Evidence

**Files:**

- Create: `tools/repository/acceptance.py`
- Create: `evidence/architecture/acceptance.json`
- Create: `docs/governance/control-register.md`
- Create: `tests/repository/test_acceptance.py`
- Modify: `CONTEXT.md`

**Interfaces:**

- Produces: `python -m tools.repository acceptance --evidence evidence/architecture/acceptance.json`.
- A failed or absent blocking criterion remains visible and makes the command nonzero; scores are never averaged.

- [ ] **Step 1: Write failing acceptance tests**

Require exactly `AR-01` through `AR-12`, each with `status`, `evidence`, `checked_at`, and `authoritative_gate`. Allow only `passed`, `failed`, and `not-ready`; reject aggregate scores and reject `passed` without resolvable evidence.

- [ ] **Step 2: Run RED**

Run: `uv run --no-project --python 3.13 python -m unittest tests.repository.test_acceptance -v`

Expected: failure because acceptance tooling is absent.

- [ ] **Step 3: Implement evidence resolution and the control register**

Map every architecture acceptance row to its deterministic command or retained record. The control register enables only foundation, active-development CI, and release controls now; it defers contributor templates/ownership until external contributions or multiple maintainers exist, schedules until compatibility/provider drift exists, and adapters until a demonstrated host delta exists.

- [ ] **Step 4: Run the complete coordinated gate**

```bash
uv run --no-project --python 3.13 python -m tools.repository validate
uv run --no-project --python 3.13 python -m unittest discover -s tests -v
cd benchmark
uv lock --check
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked mypy src
cd ..
uv run --no-project --python 3.13 python -m tools.repository acceptance --evidence evidence/architecture/acceptance.json
git diff --check
```

- [ ] **Step 5: Record completion without overstating claims and commit**

Update `CONTEXT.md` with passed and unresolved gates, exact compatibility scope, release identity, restricted-evidence status, and the next approved phase. Do not mark empirical study or host dimensions passed without retained evidence. Commit with `docs: record coordinated architecture acceptance`.

## Plan Self-Review Result

| Architecture criterion | Implementing task or existing gate |
| --- | --- |
| AR-01 | Coordinated Tasks 1, 3, and 4 |
| AR-02 | Coordinated Task 1 |
| AR-03 | Skill plan Task 3, Coordinated Task 5, and Study plan Task 13 |
| AR-04 | Coordinated Tasks 4 and 8 |
| AR-05 | Coordinated Task 5 rejects unsupported adapters; an adapter task is created only after demonstrated host evidence |
| AR-06 | Coordinated Task 5 and Study plan Task 13 |
| AR-07 | Coordinated Tasks 3 and 7 |
| AR-08 | Coordinated Task 6 and Study plan Task 12 |
| AR-09 | Runner plan Tasks 6-12, Study plan Tasks 7-14, and Coordinated Task 9 |
| AR-10 | Runner plan Tasks 8-12, Study plan Tasks 7-14, and Coordinated Task 9 |
| AR-11 | Coordinated Tasks 7-9 |
| AR-12 | Coordinated Task 1 |

- Specification coverage: behavioral and scientific work remains owned by the three component plans; every repository-architecture acceptance criterion has an explicit owner above.
- File ownership: no new task authors canonical skill content, public corpus cases, runner core records, or study outcomes; overlapping root documentation remains owned by Skill plan Task 7.
- Deferred choices: no initial adapters, no committed distribution catalog, no calendar release cadence, no premature external-contributor ceremony, and no hard-coded restricted provider or storage vendor.
- Tooling rationale: Python 3.13 is the primary maintained runtime; 3.11-3.14 testing preserves the approved compatibility floor. uv supplies exact dependency locking and fast execution without adding a JavaScript toolchain.
- Placeholder scan: passed; every code-producing step names concrete behavior, commands, and expected evidence.
