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

Plans execute approved specifications and never amend or supersede them.

## Canonical Skill Authority

- `skills/systematic-innovation/` is the single editable authority for public skill behavior.
- No root instruction file, benchmark prompt, example, generated archive, or host adapter may maintain a second copy of skill behavior.
- Host-specific mechanics may translate installation or discovery only after demonstrated host evidence; they must never change the skill's behavioral contract.

## Generated and Restricted Boundaries

- `dist/` and `benchmark/runs/` are generated or runtime outputs and are never editable authorities.
- Restricted validation and sealed-test packs (`restricted/`, `*.restricted.*`, `*.validation.yaml`, `*.sealed.yaml`) remain outside public Git, ordinary CI, generated distributions, and automatic agent context.
