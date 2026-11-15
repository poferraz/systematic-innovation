from __future__ import annotations

import argparse
from pathlib import Path
import sys

from tools.repository.isolation import scan_public_tree
from tools.validate_skill import validate_skill

DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def _cmd_validate(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else DEFAULT_ROOT
    violations = scan_public_tree(root)

    skill_dir = root / "skills/systematic-innovation"
    if skill_dir.is_dir():
        for err in validate_skill(skill_dir):
            print(f"[SKILL_FORMAT] skills/systematic-innovation: {err}")
            return 1

    for v in violations:
        print(f"[{v.code}] {v.path}: {v.message}")

    return 1 if violations else 0


def _cmd_package(args: argparse.Namespace) -> int:
    from tools.repository.package import build_skill, write_manifest

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    manifest = build_skill(
        source=source,
        output=output,
        version=args.version,
        revision=args.revision,
    )
    if args.manifest:
        write_manifest(manifest, Path(args.manifest).resolve())
    print(f"{manifest.archive_sha256}  {output.name}")
    return 0


def _cmd_verify_artifact(args: argparse.Namespace) -> int:
    from tools.repository.package import verify_artifact

    errors = verify_artifact(
        archive_path=Path(args.archive).resolve(),
        manifest_path=Path(args.manifest).resolve() if args.manifest else None,
        source_dir=Path(args.source).resolve() if args.source else None,
        revocations_path=Path(args.revocations).resolve() if args.revocations else None,
        policy_path=Path(args.policy).resolve() if args.policy else None,
    )
    for err in errors:
        print(err)
    return 1 if errors else 0


def _cmd_verify_compatibility(args: argparse.Namespace) -> int:
    from tools.repository.compatibility import verify_compatibility_file

    errors = verify_compatibility_file(
        matrix_path=Path(args.matrix).resolve(),
        profile_name=args.profile,
        as_of=args.as_of,
        profiles_path=Path(args.profiles).resolve() if args.profiles else None,
    )
    for err in errors:
        print(err)
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.repository",
        description="Deterministic repository validation, packaging, and compatibility tooling.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_p = subparsers.add_parser("validate", help="Run public-source isolation, authority, and skill validation.")
    validate_p.add_argument("root", nargs="?", default=None, help="Repository root path (defaults to current repository).")
    validate_p.set_defaults(func=_cmd_validate)

    package_p = subparsers.add_parser("package", help="Build a reproducible canonical skill ZIP distribution.")
    package_p.add_argument(
        "--source",
        default=str(DEFAULT_ROOT / "skills/systematic-innovation"),
        help="Canonical skill directory.",
    )
    package_p.add_argument("--output", required=True, help="Output ZIP file path.")
    package_p.add_argument("--manifest", default=None, help="Optional output release manifest JSON path.")
    package_p.add_argument("--version", default="0.1.0", help="Semantic version string (e.g. 0.1.0).")
    package_p.add_argument("--revision", default="0" * 40, help="40-character Git revision SHA.")
    package_p.set_defaults(func=_cmd_package)

    verify_art_p = subparsers.add_parser("verify-artifact", help="Verify a built canonical skill ZIP and manifest.")
    verify_art_p.add_argument("archive", help="Path to the built ZIP archive.")
    verify_art_p.add_argument("--manifest", default=None, help="Optional release manifest JSON path.")
    verify_art_p.add_argument("--source", default=None, help="Optional canonical source directory for byte-for-byte rebuild check.")
    verify_art_p.add_argument(
        "--revocations",
        default=str(DEFAULT_ROOT / "release/revocations.json"),
        help="Path to release revocations JSON file.",
    )
    verify_art_p.add_argument(
        "--policy",
        default=str(DEFAULT_ROOT / "release/policy.json"),
        help="Path to release policy JSON file.",
    )
    verify_art_p.set_defaults(func=_cmd_verify_artifact)

    verify_compat_p = subparsers.add_parser("verify-compatibility", help="Validate a host compatibility matrix and claim profiles.")
    verify_compat_p.add_argument("matrix", help="Path to compatibility matrix YAML or JSON file.")
    verify_compat_p.add_argument("--profile", default=None, help="Optional claim profile to evaluate.")
    verify_compat_p.add_argument("--as-of", default=None, help="Evaluation date in YYYY-MM-DD format.")
    verify_compat_p.add_argument(
        "--profiles",
        default=str(DEFAULT_ROOT / "compatibility/claim-profiles.json"),
        help="Path to claim-profiles.json.",
    )
    verify_compat_p.set_defaults(func=_cmd_verify_compatibility)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
