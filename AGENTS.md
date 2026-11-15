# Systematic Innovation Agent Orientation

## Project Purpose

`systematic-innovation` is a provider-neutral Agent Skill and evaluation laboratory for producing causally distinct, system-aware innovation possibilities while preserving what already works.

## Authoritative Reading Order

Read these documents in order before proposing or executing changes:

1. [`CONTEXT.md`](CONTEXT.md) — durable project intent, provenance boundaries, and decision history.
2. [`docs/superpowers/specs/2026-08-31-systematic-innovation-design.md`](docs/superpowers/specs/2026-08-31-systematic-innovation-design.md) — approved behavioral and evaluation specification.
3. [`docs/superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md`](docs/superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md) — approved repository-architecture specification.
4. [`docs/superpowers/plans/2026-09-01-systematic-innovation-coordinated-implementation.md`](docs/superpowers/plans/2026-09-01-systematic-innovation-coordinated-implementation.md) — cross-plan ownership and execution order.
5. Applicable component plan:
   - [`docs/superpowers/plans/2026-08-31-systematic-innovation-skill.md`](docs/superpowers/plans/2026-08-31-systematic-innovation-skill.md)
   - [`docs/superpowers/plans/2026-08-31-systematic-innovation-benchmark-runner.md`](docs/superpowers/plans/2026-08-31-systematic-innovation-benchmark-runner.md)
   - [`docs/superpowers/plans/2026-08-31-systematic-innovation-benchmark-study.md`](docs/superpowers/plans/2026-08-31-systematic-innovation-benchmark-study.md)
   - [`docs/superpowers/plans/2026-10-29-systematic-innovation-audit-remediation.md`](docs/superpowers/plans/2026-10-29-systematic-innovation-audit-remediation.md)
6. Loop refinement specification and plan:
   - [`docs/superpowers/specs/2026-11-14-systematic-innovation-v2-loop-design.md`](docs/superpowers/specs/2026-11-14-systematic-innovation-v2-loop-design.md)
   - [`docs/superpowers/plans/2026-11-14-systematic-innovation-v2-loop.md`](docs/superpowers/plans/2026-11-14-systematic-innovation-v2-loop.md)
   - [`docs/superpowers/plans/2026-11-14-systematic-innovation-v2-skill.md`](docs/superpowers/plans/2026-11-14-systematic-innovation-v2-skill.md)

Plans execute approved specifications and never amend or supersede them.

## Canonical Skill Authority

- `skills/systematic-innovation/` is the single editable authority for public skill behavior.
- No root instruction file, benchmark prompt, example, generated archive, or host adapter may maintain a second copy of skill behavior.
- Host-specific mechanics may translate installation or discovery only after demonstrated host evidence; they must never change the skill's behavioral contract.

## Generated and Restricted Boundaries

- `dist/` and `benchmark/runs/` are generated or runtime outputs and are never editable authorities.
- Restricted validation and sealed-test packs (`restricted/`, `*.restricted.*`, `*.validation.yaml`, `*.sealed.yaml`) remain outside public Git, ordinary CI, generated distributions, and automatic agent context.

## Validation Commands

Root repository tests use Python's standard library `unittest`. The isolated `benchmark/` package uses pytest:

- `python3 -m unittest discover tests -v`
- `python3 tools/validate_skill.py skills/systematic-innovation`
- `python3 -m tools.repository.authority`
- `python3 -m tools.repository validate`
- `python3 -m tools.repository acceptance --evidence evidence/architecture/acceptance.json --stage repository-shell`

## Workstream 2 Completion and Next Boundary

The formal `benchmark/` runner, fail-closed restricted preflight, 60 public development cases, and draft study contracts are implemented. `evidence/architecture/acceptance.json` records AR-01 through AR-12; see `benchmark/runner-verification.md` for scope and retained verification. Root tooling remains standard-library only.

The canonical skill is frozen (`SKILL.md` SHA-256 `d5971f6e3e646916e2a287c5a8fde96a93b811ed071c362526c605ef222a890b`). Do not modify `skills/systematic-innovation/` without an approved behavioral amendment.

Benchmark checks (from `benchmark/`, uv 0.12.8):

- `uv lock --check`
- `uv run --locked pytest -q`
- `uv run --locked ruff check .`
- `uv run --locked mypy src`

Full repository acceptance: `python3 -m tools.repository acceptance --evidence evidence/architecture/acceptance.json --stage full`.

**Pause boundary:** Study Tasks 9–14 remain unexecuted: live six-case feasibility, twelve-case measurement rehearsal, 60-case development, human calibration, restricted validation, cross-agent evaluation, and sealed testing. Preregistration is `draft`; scientific stage statuses remain pending. No empirical efficacy or broad compatibility claim follows from implementation or fake-adapter tests. Follow `benchmark/HANDOFF.md` and obtain the applicable owner/operator authorization before live studies, restricted access, publication, or pushing to origin.
