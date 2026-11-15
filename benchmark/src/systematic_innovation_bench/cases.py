"""Load public case packs without disclosing malformed case values."""

from collections import Counter, defaultdict
from collections.abc import Sequence
from pathlib import Path

import yaml

from .models import BenchmarkCase


def load_cases(
    paths: Sequence[Path], expected_split: str | None = None, *, public_root: Path | None = None
) -> list[BenchmarkCase]:
    cases: list[BenchmarkCase] = []
    for path in paths:
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            if (
                not isinstance(payload, dict)
                or set(payload) != {"cases"}
                or not isinstance(payload["cases"], list)
            ):
                raise ValueError("invalid case pack structure")
            loaded = [BenchmarkCase.model_validate(item) for item in payload["cases"]]
        except (ValueError, TypeError, KeyError, OSError, yaml.YAMLError):
            raise ValueError("invalid case pack structure") from None
        if (
            public_root is not None
            and path.resolve().is_relative_to(public_root.resolve())
            and any(case.split != "development" for case in loaded)
        ):
            raise ValueError("restricted cases must remain outside public worktree")
        cases.extend(loaded)
    ids = [case.id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate case id")
    if expected_split and any(case.split != expected_split for case in cases):
        raise ValueError("case split mismatch")
    return sorted(cases, key=lambda case: case.id)


def summarize_strata(cases: Sequence[BenchmarkCase]) -> dict[str, dict[str, int]]:
    counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for case in cases:
        counts["domain"][case.domain] += 1
        for key, value in case.strata.items():
            counts[key][value] += 1
    return {key: dict(sorted(values.items())) for key, values in sorted(counts.items())}
