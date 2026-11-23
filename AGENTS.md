# Contributor guide

Start with the [decision record](CONTEXT.md), [skill and evaluation specification](docs/specifications/skill-and-evaluation.md) and [repository specification](docs/specifications/repository.md). The installable [skill](skills/systematic-innovation/SKILL.md) is the single editable source of public behavior. Host adapters require evidence of an installation or activation difference.

The public skill is plain Markdown. Generated archives in `dist/` and benchmark run directories are derived outputs. Restricted validation and sealed cases belong outside public Git, CI and distribution archives. Keep test data, historical results and new study claims distinct. The [release procedure](docs/release.md) covers verification and attestations.

Run the repository checks from the root:

```sh
python3 -m unittest discover tests -v
python3 tools/validate_skill.py skills/systematic-innovation
python3 -m tools.repository.authority
python3 -m tools.repository validate
python3 -m tools.repository acceptance --evidence evidence/architecture/acceptance.json --stage full
```

The [benchmark guide](benchmark/README.md) explains the separate Python environment and offline example. From `benchmark/`, check the lock with `uv lock --check`, then run `uv run --locked pytest -q`, `uv run --locked ruff check .` and `uv run --locked mypy src task9`.

The [study decision](benchmark/study/task9-readiness-approval.yaml) authorizes preparation and offline tests. The [six-case protocol](benchmark/study/six-case-protocol.md) and [stage gates](benchmark/study/stage-gates.yaml) define the requirements for a future live run. The [v2 evaluation report](evals/v2-loop/report.md) covers the earlier, bounded development diagnostics.
