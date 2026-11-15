from __future__ import annotations

from datetime import date
import json
from pathlib import Path
from typing import Any

from tools.repository.isolation import Violation

EXPECTED_CRITERIA_IDS = tuple(f"AR-{i:02d}" for i in range(1, 13))
REPOSITORY_SHELL_CRITERIA_IDS = (
    "AR-01",
    "AR-02",
    "AR-03",
    "AR-04",
    "AR-05",
    "AR-06",
    "AR-07",
    "AR-10",
    "AR-11",
    "AR-12",
)
ALLOWED_STATUSES = frozenset({"passed", "failed", "not-ready"})
FORBIDDEN_SCORE_KEYS = frozenset(
    {
        "score",
        "average",
        "overall_score",
        "composite_score",
        "percentage",
        "grade",
        "maturity_score",
    }
)
REQUIRED_ROW_FIELDS = ("id", "criterion", "status", "evidence", "checked_at", "authoritative_gate")


def validate_acceptance_inventory(
    data: dict[str, Any],
    root: Path,
) -> list[Violation]:
    """Validate structure, prohibited aggregate scoring, and evidence resolution for AR-01..AR-12."""
    violations: list[Violation] = []
    root = root.resolve()

    for key in data:
        if key.lower() in FORBIDDEN_SCORE_KEYS:
            violations.append(
                Violation(
                    code="AGGREGATE_SCORE_PROHIBITED",
                    path="evidence/architecture/acceptance.json",
                    message=f"composite or aggregate score field '{key}' is prohibited (AR-10)",
                )
            )

    criteria = data.get("criteria")
    if not isinstance(criteria, list):
        violations.append(
            Violation(
                code="INVALID_SCHEMA",
                path="evidence/architecture/acceptance.json",
                message="'criteria' must be a list of AR-01..AR-12 objects",
            )
        )
        return violations

    seen_ids: list[str] = []
    for idx, row in enumerate(criteria):
        if not isinstance(row, dict):
            violations.append(
                Violation(
                    code="INVALID_SCHEMA",
                    path=f"criteria[{idx}]",
                    message="criterion entry must be an object",
                )
            )
            continue

        cid = str(row.get("id", f"criteria[{idx}]"))
        seen_ids.append(cid)

        for key in row:
            if key.lower() in FORBIDDEN_SCORE_KEYS:
                violations.append(
                    Violation(
                        code="AGGREGATE_SCORE_PROHIBITED",
                        path=cid,
                        message=f"composite or aggregate score field '{key}' is prohibited on {cid} (AR-10)",
                    )
                )

        for req in REQUIRED_ROW_FIELDS:
            if req not in row or row[req] in (None, ""):
                violations.append(
                    Violation(
                        code="MISSING_FIELD",
                        path=cid,
                        message=f"missing required field '{req}' on {cid}",
                    )
                )

        status = str(row.get("status", ""))
        if status not in ALLOWED_STATUSES:
            violations.append(
                Violation(
                    code="INVALID_STATUS",
                    path=cid,
                    message=f"invalid status '{status}' on {cid}; allowed: {sorted(ALLOWED_STATUSES)}",
                )
            )

        checked_at = str(row.get("checked_at", ""))
        try:
            date.fromisoformat(checked_at)
        except ValueError:
            violations.append(
                Violation(
                    code="INVALID_DATE",
                    path=cid,
                    message=f"invalid ISO date in checked_at on {cid}: {checked_at!r}",
                )
            )

        ev_list = row.get("evidence")
        if not isinstance(ev_list, list) or not ev_list or not all(isinstance(e, str) and e.strip() for e in ev_list):
            violations.append(
                Violation(
                    code="UNRESOLVABLE_EVIDENCE",
                    path=cid,
                    message=f"{cid} requires a non-empty list of evidence file paths",
                )
            )
        else:
            for ev_path_str in ev_list:
                candidate = (root / ev_path_str).resolve()
                try:
                    candidate.relative_to(root)
                except ValueError:
                    violations.append(
                        Violation(
                            code="UNRESOLVABLE_EVIDENCE",
                            path=cid,
                            message=f"evidence path escapes repository root: {ev_path_str}",
                        )
                    )
                    continue
                if not candidate.exists():
                    violations.append(
                        Violation(
                            code="UNRESOLVABLE_EVIDENCE",
                            path=cid,
                            message=f"evidence path does not exist on disk for {cid}: {ev_path_str}",
                        )
                    )

    if tuple(seen_ids) != EXPECTED_CRITERIA_IDS:
        violations.append(
            Violation(
                code="CRITERIA_MISMATCH",
                path="evidence/architecture/acceptance.json",
                message=f"expected exact ordered criteria {list(EXPECTED_CRITERIA_IDS)}, found {seen_ids}",
            )
        )

    return violations


def evaluate_acceptance(
    data: dict[str, Any],
    root: Path,
    stage: str = "full",
) -> tuple[bool, list[str]]:
    """Evaluate AR-01..AR-12 without averaging; return (passed, blocking_messages)."""
    if stage not in {"full", "repository-shell"}:
        raise ValueError(f"Unsupported acceptance stage '{stage}'; expected 'full' or 'repository-shell'")

    violations = validate_acceptance_inventory(data, root=root)
    blockers = [f"[{v.code}] {v.path}: {v.message}" for v in violations]
    if blockers:
        return False, blockers

    required_passed = set(EXPECTED_CRITERIA_IDS if stage == "full" else REPOSITORY_SHELL_CRITERIA_IDS)
    for row in data["criteria"]:
        cid = str(row["id"])
        status = str(row["status"])
        if status == "failed":
            blockers.append(f"[FAILED_GATE] {cid}: {row['criterion']} is 'failed' ({row['authoritative_gate']})")
        elif cid in required_passed and status != "passed":
            blockers.append(
                f"[BLOCKING_GATE] {cid}: {row['criterion']} has status '{status}' "
                f"(required 'passed' for stage '{stage}'; gate: {row['authoritative_gate']})"
            )

    return len(blockers) == 0, blockers


def run_acceptance_cli(
    evidence_path: Path,
    root: Path,
    stage: str = "full",
) -> tuple[int, list[str]]:
    if not evidence_path.is_file():
        return 1, [f"acceptance evidence file does not exist: {evidence_path}"]
    try:
        data = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return 1, [f"invalid acceptance JSON {evidence_path}: {exc}"]

    passed, blockers = evaluate_acceptance(data, root=root, stage=stage)
    lines: list[str] = []
    for row in data.get("criteria", []):
        if isinstance(row, dict) and "id" in row and "status" in row:
            lines.append(f"{row['id']}: {row['status']} — {row.get('criterion', '')}")
    for b in blockers:
        lines.append(b)
    return (0 if passed else 1), lines
