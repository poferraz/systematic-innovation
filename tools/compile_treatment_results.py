"""Compatibility entry point for the retired, uncalibrated pilot importer."""

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> None:
    raise RuntimeError(
        "The historical importer is disabled: it assigns unverified quality ratings "
        "and treats extracted blocks as qualified mechanisms. Historical results must "
        "remain unchanged; use the retained raw data and calibrated review workflow."
    )

if __name__ == "__main__":
    main()
