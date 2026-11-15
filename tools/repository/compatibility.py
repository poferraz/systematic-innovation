from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
import re
from typing import Any

from tools.repository.isolation import Violation

DIMENSIONS = (
    "format_conformance",
    "installation",
    "discovery",
    "explicit_activation",
    "automatic_activation",
    "behavioral_conformance",
)

ALLOWED_DIMENSION_STATES: dict[str, frozenset[str]] = {
    "format_conformance": frozenset({"passed", "failed", "not-assessed"}),
    "installation": frozenset({"passed", "failed", "not-supported", "not-assessed"}),
    "discovery": frozenset({"passed", "failed", "not-supported", "not-assessed"}),
    "explicit_activation": frozenset({"passed", "failed", "not-supported", "not-assessed"}),
    "automatic_activation": frozenset({"passed", "failed", "not-supported", "not-claimed", "not-assessed"}),
    "behavioral_conformance": frozenset({"passed", "failed", "not-assessed"}),
}

REQUIRED_RECORD_FIELDS = (
    "agent_family",
    "host",
    "host_version",
    "model_family",
    "skill_revision",
    "artifact_digest",
    "format_version",
    "installation_procedure",
    "invocation_mode",
    "test_scenario",
    "tested_at",
    "review_after",
    "run_ids",
    "claim_profiles",
    "limitations",
)

REQUIRED_ADAPTER_EVIDENCE_FIELDS = (
    "host",
    "host_version",
    "demonstrated_incompatibility",
    "why_docs_insufficient",
    "minimal_translation",
    "preservation_test",
)

REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DEFAULT_PROFILES_PATH = Path(__file__).resolve().parents[2] / "compatibility/claim-profiles.json"


@dataclass(frozen=True)
class ClaimResult:
    profile_name: str
    passed: bool
    qualifying_families: tuple[str, ...]
    qualifying_hosts: tuple[str, ...]
    violations: tuple[Violation, ...]
    dimension_summary: dict[str, dict[str, str]]


def _parse_iso_date(value: date | str | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value).strip())


def _extract_raw_dimensions(record: dict[str, Any]) -> dict[str, Any]:
    nested = record.get("dimensions")
    result: dict[str, Any] = {}
    for dim in DIMENSIONS:
        if dim in record:
            result[dim] = record[dim]
        elif isinstance(nested, dict) and dim in nested:
            result[dim] = nested[dim]
    return result


def validate_host_record(
    record: dict[str, Any],
    as_of: date | str | None = None,
) -> list[Violation]:
    """Validate a single host compatibility evidence record without mutating it."""
    violations: list[Violation] = []
    host_id = str(record.get("host") or record.get("agent_family") or "<unknown-host>")

    for field in REQUIRED_RECORD_FIELDS:
        if field not in record or record[field] in (None, ""):
            violations.append(
                Violation(
                    code="MISSING_FIELD",
                    path=host_id,
                    message=f"missing required compatibility field '{field}'",
                )
            )

    raw_dims = _extract_raw_dimensions(record)
    for dim in DIMENSIONS:
        if dim not in raw_dims:
            violations.append(
                Violation(
                    code="MISSING_DIMENSION",
                    path=host_id,
                    message=f"missing compatibility dimension '{dim}'",
                )
            )
            continue
        state = str(raw_dims[dim])
        if state not in ALLOWED_DIMENSION_STATES[dim]:
            violations.append(
                Violation(
                    code="INVALID_DIMENSION_STATE",
                    path=host_id,
                    message=f"invalid state '{state}' for dimension '{dim}'; allowed: {sorted(ALLOWED_DIMENSION_STATES[dim])}",
                )
            )

    rev = str(record.get("skill_revision", ""))
    if rev and not REVISION_RE.match(rev):
        violations.append(
            Violation(
                code="INVALID_FIELD",
                path=host_id,
                message="skill_revision must be a 40-character lowercase hex commit SHA",
            )
        )

    digest = str(record.get("artifact_digest", ""))
    if digest and not SHA256_RE.match(digest):
        violations.append(
            Violation(
                code="INVALID_FIELD",
                path=host_id,
                message="artifact_digest must be a 64-character lowercase hex SHA-256 digest",
            )
        )

    run_ids = record.get("run_ids")
    if not isinstance(run_ids, list) or not run_ids or not all(isinstance(r, str) and r.strip() for r in run_ids):
        violations.append(
            Violation(
                code="INVALID_FIELD",
                path=host_id,
                message="run_ids must be a non-empty list of non-empty run identifier strings",
            )
        )

    for list_field in ("claim_profiles", "limitations"):
        val = record.get(list_field)
        if not isinstance(val, list) or not all(isinstance(item, str) and item.strip() for item in val):
            violations.append(
                Violation(
                    code="INVALID_FIELD",
                    path=host_id,
                    message=f"{list_field} must be a list of non-empty strings",
                )
            )

    tested_date: date | None = None
    review_date: date | None = None
    try:
        if "tested_at" in record:
            tested_date = _parse_iso_date(record["tested_at"])
    except ValueError:
        violations.append(
            Violation(
                code="INVALID_DATE",
                path=host_id,
                message=f"invalid ISO date in tested_at: {record.get('tested_at')!r}",
            )
        )
    try:
        if "review_after" in record:
            review_date = _parse_iso_date(record["review_after"])
    except ValueError:
        violations.append(
            Violation(
                code="INVALID_DATE",
                path=host_id,
                message=f"invalid ISO date in review_after: {record.get('review_after')!r}",
            )
        )

    if tested_date and review_date and review_date < tested_date:
        violations.append(
            Violation(
                code="INVALID_DATE",
                path=host_id,
                message="review_after cannot precede tested_at",
            )
        )

    # AR-05: Reject unsupported adapters unless complete host delta evidence is recorded
    if record.get("adapter_used") or record.get("adapter"):
        evidence = record.get("adapter_evidence")
        if not isinstance(evidence, dict):
            violations.append(
                Violation(
                    code="UNSUPPORTED_ADAPTER",
                    path=host_id,
                    message="host adapter requires adapter_evidence object with demonstrated host delta (AR-05)",
                )
            )
        else:
            missing_ev = [
                key
                for key in REQUIRED_ADAPTER_EVIDENCE_FIELDS
                if not isinstance(evidence.get(key), str) or not str(evidence.get(key)).strip()
            ]
            if missing_ev:
                violations.append(
                    Violation(
                        code="UNSUPPORTED_ADAPTER",
                        path=host_id,
                        message=f"adapter_evidence missing required fields: {missing_ev}",
                    )
                )

    # Study Plan Task 13 quantitative thresholds when metrics are supplied
    if raw_dims.get("automatic_activation") == "passed":
        metrics = record.get("automatic_activation_metrics")
        if isinstance(metrics, dict):
            precision = float(metrics.get("precision", 0.0))
            recall = float(metrics.get("recall", 0.0))
            if precision < 0.90 or recall < 0.85:
                violations.append(
                    Violation(
                        code="THRESHOLD_FAILED",
                        path=host_id,
                        message=(
                            f"automatic_activation='passed' requires precision>=0.90 and recall>=0.85 "
                            f"(got precision={precision:.3f}, recall={recall:.3f})"
                        ),
                    )
                )

    if raw_dims.get("explicit_activation") == "passed" and "explicit_activation_rate" in record:
        if float(record["explicit_activation_rate"]) < 1.0:
            violations.append(
                Violation(
                    code="THRESHOLD_FAILED",
                    path=host_id,
                    message="explicit_activation='passed' requires explicit_activation_rate == 1.0",
                )
            )

    if raw_dims.get("behavioral_conformance") == "passed" and "disclosure_ordering_violations" in record:
        if int(record["disclosure_ordering_violations"]) != 0:
            violations.append(
                Violation(
                    code="THRESHOLD_FAILED",
                    path=host_id,
                    message="behavioral_conformance='passed' requires 0 controlled-disclosure ordering violations",
                )
            )

    return violations


def effective_dimension_states(
    record: dict[str, Any],
    as_of: date | str | None = None,
) -> dict[str, str]:
    """Return effective per-dimension states at `as_of`, marking overdue passed evidence as `stale` without mutating `record`."""
    raw_dims = _extract_raw_dimensions(record)
    as_of_date = _parse_iso_date(as_of)
    review_date: date | None = None
    try:
        if "review_after" in record:
            review_date = _parse_iso_date(record["review_after"])
    except ValueError:
        review_date = None

    is_overdue = bool(as_of_date and review_date and as_of_date > review_date)
    unassessed_change = bool(record.get("material_change_unassessed", False))

    effective: dict[str, str] = {}
    for dim in DIMENSIONS:
        state = str(raw_dims.get(dim, "not-assessed"))
        if state == "passed" and (is_overdue or unassessed_change):
            effective[dim] = "stale"
        else:
            effective[dim] = state
    return effective


def _resolve_profile(
    profile: str | dict[str, Any],
    profiles_path: Path | None = None,
) -> tuple[str, dict[str, Any]]:
    if isinstance(profile, dict):
        name = str(profile.get("name", "custom"))
        return name, profile

    path = profiles_path or DEFAULT_PROFILES_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    profiles = data.get("profiles", {})
    if profile not in profiles:
        raise ValueError(f"Unknown compatibility claim profile '{profile}'; available: {sorted(profiles)}")
    return profile, profiles[profile]


def evaluate_claim(
    profile: str | dict[str, Any],
    records: list[dict[str, Any]],
    as_of: date | str | None = None,
    profiles_path: Path | None = None,
) -> ClaimResult:
    """Evaluate a named compatibility claim profile against a collection of host records."""
    profile_name, spec = _resolve_profile(profile, profiles_path=profiles_path)
    required_dims: dict[str, list[str]] = spec.get("required_dimensions", {})
    min_families = int(spec.get("min_distinct_families", 1))

    violations: list[Violation] = []
    qualifying_families: list[str] = []
    qualifying_hosts: list[str] = []
    dimension_summary: dict[str, dict[str, str]] = {}

    for rec in records:
        host_id = str(rec.get("host") or rec.get("agent_family") or "<unknown-host>")
        rec_violations = validate_host_record(rec, as_of=as_of)
        violations.extend(rec_violations)

        eff = effective_dimension_states(rec, as_of=as_of)
        dimension_summary[host_id] = eff

        if rec_violations:
            continue

        # Check if record meets every required dimension for this profile
        meets_all = True
        for dim, allowed_states in required_dims.items():
            actual = eff.get(dim, "not-assessed")
            if actual not in allowed_states:
                meets_all = False
                code = "STALE_EVIDENCE" if actual == "stale" else "DIMENSION_NOT_PASSED"
                violations.append(
                    Violation(
                        code=code,
                        path=host_id,
                        message=(
                            f"profile '{profile_name}' requires {dim} in {allowed_states}, "
                            f"but host '{host_id}' has effective state '{actual}'"
                        ),
                    )
                )

        if meets_all:
            qualifying_hosts.append(host_id)
            family = str(rec["agent_family"])
            if family not in qualifying_families:
                qualifying_families.append(family)

    distinct_families = tuple(qualifying_families)
    if len(distinct_families) < min_families:
        violations.append(
            Violation(
                code="INSUFFICIENT_FAMILIES",
                path=profile_name,
                message=(
                    f"claim profile '{profile_name}' requires at least {min_families} distinct agent families "
                    f"passing all required dimensions, found {len(distinct_families)}: {list(distinct_families)}"
                ),
            )
        )

    passed = len(distinct_families) >= min_families and not any(
        v.code in {"MISSING_FIELD", "MISSING_DIMENSION", "INVALID_DIMENSION_STATE", "INVALID_FIELD", "INVALID_DATE", "UNSUPPORTED_ADAPTER", "THRESHOLD_FAILED"}
        for v in violations
    )

    return ClaimResult(
        profile_name=profile_name,
        passed=passed,
        qualifying_families=distinct_families,
        qualifying_hosts=tuple(qualifying_hosts),
        violations=tuple(violations),
        dimension_summary=dimension_summary,
    )


def load_compatibility_matrix(matrix_path: Path) -> list[dict[str, Any]]:
    """Load compatibility records from JSON or YAML."""
    raw_text = matrix_path.read_text(encoding="utf-8")
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore[import-not-found]

            parsed = yaml.safe_load(raw_text)
        except ImportError as exc:
            raise ValueError(
                f"Failed to parse {matrix_path} as JSON-compatible YAML and PyYAML is not installed: {exc}"
            ) from exc

    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict) and isinstance(parsed.get("records"), list):
        return parsed["records"]
    if isinstance(parsed, dict) and isinstance(parsed.get("hosts"), list):
        return parsed["hosts"]
    raise ValueError(f"Expected compatibility matrix in {matrix_path} to contain a list of records")


def verify_compatibility_file(
    matrix_path: Path,
    profile_name: str | None = None,
    as_of: date | str | None = None,
    profiles_path: Path | None = None,
) -> list[str]:
    if not matrix_path.is_file():
        return [f"compatibility matrix file does not exist: {matrix_path}"]
    try:
        records = load_compatibility_matrix(matrix_path)
    except ValueError as exc:
        return [str(exc)]

    effective_as_of = as_of or date.today()
    errors: list[str] = []
    for rec in records:
        for v in validate_host_record(rec, as_of=effective_as_of):
            errors.append(f"[{v.code}] {v.path}: {v.message}")

    if profile_name:
        result = evaluate_claim(
            profile=profile_name,
            records=records,
            as_of=effective_as_of,
            profiles_path=profiles_path,
        )
        if not result.passed:
            for v in result.violations:
                msg = f"[{v.code}] {v.path}: {v.message}"
                if msg not in errors:
                    errors.append(msg)

    return errors
