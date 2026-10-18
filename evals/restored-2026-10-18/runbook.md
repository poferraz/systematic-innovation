# Reproduce the restored-candidate diagnostic

The retained raw data is immutable evidence. Run the local summarizer first;
regenerating answers incurs new calls and produces a new study run.

## Read-only reproduction

```sh
UV_CACHE_DIR=/tmp/systematic-innovation-uv-cache PYTHONPATH=. /Users/poferraz/.local/bin/uv run --no-project --python 3.13 python evals/restored-2026-10-18/summarize.py
```

This checks actual injected pack hashes, exact ordered user disclosures, final
answers and cumulative counters across 80 conversations. It regenerates only
derived final-analysis artifacts from the raw records. Source digests are in the
measurement freeze files; older measurements and source snapshots are retained.

## Generation commands used

Prefix every command below with the Python invocation above, omitting its
`evals/restored-2026-10-18/summarize.py` argument. The installed CLI requires access
to its own app-server/session state outside the desktop filesystem sandbox. The
benchmark child itself uses a read-only sandbox. No restricted pack is involved.

```text
tools/stress_runner.py --cases evals/restored-2026-10-18/cases.json --output evals/restored-2026-10-18/before-six --conditions baseline_clean control_creative control_format skill_treatment --case broad-quick --case ambiguous-deep --case narrow-saturation --case complex-single --case impossible --case bypass --max-calls 40 --jobs 3
tools/stress_runner.py --cases evals/restored-2026-10-18/cases.json --output evals/restored-2026-10-18/before-boundaries --conditions baseline_clean control_creative control_format skill_treatment --case experiments-off --case experiments-on --case tight-budget --case negative --max-calls 16 --jobs 3
tools/stress_runner.py --cases evals/restored-2026-10-18/cases.json --output evals/restored-2026-10-18/discovery-only --conditions skill_treatment --case ambiguous-deep --replicates 2 --max-calls 8 --jobs 2
tools/stress_runner.py --cases evals/restored-2026-10-18/cases.json --output evals/restored-2026-10-18/after --conditions skill_treatment --replicates 2 --max-calls 26 --jobs 3
tools/stress_runner.py --cases evals/restored-2026-10-18/cases.json --output evals/restored-2026-10-18/budget-repair --conditions skill_treatment --case tight-budget --replicates 2 --max-calls 2 --jobs 2
tools/stress_runner.py --cases evals/restored-2026-10-18/cases.json --output evals/restored-2026-10-18/budget-final --conditions skill_treatment --case tight-budget --replicates 2 --max-calls 2 --jobs 2
tools/stress_runner.py --cases evals/restored-2026-10-18/public-holdout.json --output evals/restored-2026-10-18/holdout --conditions baseline_clean control_creative control_format skill_treatment --max-calls 8 --jobs 1
```

These commands used **different frozen canonical inputs at each documented
epoch**. Running them all against today's pack does not recreate the original
conditions. Exact initial user prompts, including injected packs, are in every
raw turn. `starting-prompts.json`, `revised-prompts.json`, pack snapshots and
freeze files make those inputs independently reviewable. For a new run, place the
required hashed files in a temporary skill directory outside the repository and
pass `--skill /absolute/path/to/frozen/skill`; choose new output paths.

The finite-space comparison reconstructed the five starting files with
`git show a36903a:skills/systematic-innovation/<relative-file>` in a temporary
directory, checked `load_skill_pack` against `starting-freeze.json`, then called
`run_case` once per pack with `saturation-reproducer.json`. Its exact prompts,
commands, events and usage are in `finite-saturation/`. The revised finite run
uses the allocation-only pack (`final-freeze.json`), before the last router edit.

The three usage probes used the exact command arrays in `probe-command*.json`
and exact `probe-prompt*.txt`; later commands resume the recorded session.
Their artificial one-word replies test usage semantics, not innovation quality.

## Deterministic verification

```sh
UV_CACHE_DIR=/tmp/systematic-innovation-uv-cache PYTHONPATH=. /Users/poferraz/.local/bin/uv run --no-project --python 3.13 python -m unittest discover -s tests -v
UV_CACHE_DIR=/tmp/systematic-innovation-uv-cache PYTHONPATH=. /Users/poferraz/.local/bin/uv run --no-project --python 3.13 python tools/validate_skill.py skills/systematic-innovation
git diff --check
```

Human review remains a separate dependency; see `human-review.md`. No command
here can infer qualified mechanisms from lexical clustering or declare the
formal study gates passed.
