# Repository Governance and Control Register

This control register maps active repository controls to the risks they mitigate and records the explicit triggers and rationale for deferred controls under [`docs/superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md`](../superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md) (§12 and §16 `AR-11`).

---

## 1. Active Controls

| Stage | Control | Authoritative Implementation | Protected Risk |
| --- | --- | --- | --- |
| Foundation | Single canonical skill authority routing & plan subordination | [`AGENTS.md`](../../AGENTS.md), [`tools/repository/authority.py`](../../tools/repository/authority.py), [`tests/repository/test_authority.py`](../../tests/repository/test_authority.py) | Prevents shadow behavioral copies outside `skills/systematic-innovation/` and prevents execution plans from silently overriding approved specifications (`AR-01`, `AR-02`, `AR-12`). |
| Foundation | Public-source isolation & secret redaction gate | [`tools/repository/isolation.py`](../../tools/repository/isolation.py), [`.gitignore`](../../.gitignore), [`tests/repository/test_isolation.py`](../../tests/repository/test_isolation.py) | Prevents restricted evaluation packs (`restricted/`, `*.validation.yaml`, `*.sealed.yaml`), generated archives (`dist/`, `*.zip`), or credential assignments from entering the public Git tree (`AR-01`, `AR-07`). |
| Foundation | Trust-zone security model & private vulnerability reporting | [`SECURITY.md`](../../SECURITY.md) | Separates the pure-Markdown public skill zone, the executable tooling zone, and the off-repo restricted evaluation pack zone; routes disclosures through GitHub Security Advisories. |
| Active Development | Least-privilege, SHA-pinned public CI across Python 3.11, 3.13, and 3.14 | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml), [`tests/repository/test_workflows.py`](../../tests/repository/test_workflows.py) | Exercises all stdlib unit tests, canonical skill format validation, authority checks, and public-source isolation with `contents: read`, 15-minute timeouts, and zero secrets (`AR-07`). |
| Active Development | Reviewable monthly dependency update cadence | [`.github/dependabot.yml`](../../.github/dependabot.yml) | Ensures GitHub Actions SHA pins and Python development dependencies receive reviewable monthly update pull requests gated by CI. |
| Active Development | Independent 6-dimension compatibility validation & adapter gate | [`compatibility/schema.json`](../../compatibility/schema.json), [`compatibility/claim-profiles.json`](../../compatibility/claim-profiles.json), [`tools/repository/compatibility.py`](../../tools/repository/compatibility.py) | Prevents conflating format, installation, discovery, explicit activation, automatic activation, and behavioral conformance; enforces staleness expiry and rejects unsupported host adapters (`AR-03`, `AR-05`, `AR-06`). |
| Release | Reproducible canonical skill ZIP packaging, attestation, and revocation denylist | [`tools/repository/package.py`](../../tools/repository/package.py), [`release/policy.json`](../../release/policy.json), [`release/revocations.json`](../../release/revocations.json), [`.github/workflows/release.yml`](../../.github/workflows/release.yml), [`docs/release.md`](../release.md) | Guarantees byte-for-byte reproducible release archives from `skills/systematic-innovation/`, verifies post-extraction installation before publication, attests provenance via `actions/attest`, and blocks revoked digests (`AR-04`). |
| Governance | Non-compensatory architecture acceptance inventory (`AR-01..AR-12`) | [`tools/repository/acceptance.py`](../../tools/repository/acceptance.py), [`evidence/architecture/acceptance.json`](../../evidence/architecture/acceptance.json) | Prevents composite maturity scores from masking failed or `not-ready` gates (`AR-10`). |

---

## 2. Deferred Controls

Per Specification §12.3–12.4 and §15 Rule 7, controls whose protected workflow does not yet exist are explicitly deferred rather than satisfied cosmetically:

| Deferred Control | Current Status | Activation Trigger | Rationale |
| --- | --- | --- | --- |
| External contributor templates (`CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md`, `CODEOWNERS`) | Deferred | Opening the repository to external pull requests or adding a second active maintainer. | Single-owner repository; empty contributor ceremony adds maintenance surface without mitigating an active coordination risk (§12.3). |
| Scheduled CI workflows (`on: schedule`) | Deferred | Completion of the formal cross-agent compatibility matrix (`benchmark/study/integration-matrix.yaml`) or live provider-drift monitoring. | Stable deterministic unit tests should run on push/PR; scheduled runs are warranted only when monitoring external host or provider drift (§12.4). |
| Host-specific adapters (`adapters/`) | Deferred | Retained host evidence demonstrating that a target host cannot install, discover, or activate `skills/systematic-innovation/` directly (`AR-05`). | `skills/systematic-innovation/` conforms directly to the open Agent Skills specification (`100.0/100 Grade A` on `NVIDIA/SkillEvaluator`); `tools/repository/compatibility.py` rejects any adapter lacking demonstrated host-delta evidence (§8.3). |
| Committed distribution catalog | Deferred | Demonstrated consumer requirement for in-repo prebuilt archives that cannot be served by attested GitHub Releases. | Generated archives remain release-only (`dist/` is gitignored) to eliminate working-tree drift from `skills/systematic-innovation/` (§8.2). |
