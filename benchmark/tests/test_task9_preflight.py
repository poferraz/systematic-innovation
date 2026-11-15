"""Launch packet generation is read-only and never calls a provider."""
import json
from pathlib import Path

import pytest
import yaml

from task9.cli import main

BENCH = Path(__file__).resolve().parents[1]


def test_preflight_records_actual_scope_and_denies_current_launch(monkeypatch):
    from task9.preflight import build_launch_preflight

    def forbidden(*args, **kwargs):
        raise AssertionError("preflight attempted provider traffic")

    monkeypatch.setattr("task9.transport.HTTPTransport.send", forbidden)
    monkeypatch.setattr("task9.transport.HTTPCountTransport.send", forbidden)
    paths = [BENCH / "study/stage-gates.yaml", BENCH / "study/preregistration.yaml",
             BENCH / "study/task9-readiness-approval.yaml",
             BENCH / "configs/feasibility-six.proposed.yaml"]
    before = [path.read_bytes() for path in paths]
    report = build_launch_preflight()
    assert report.launch_ready is False and report.live_execution_authorized is False
    assert report.generation_calls_made == report.provider_requests_made == 0
    assert report.scope.parent_jobs == 30 and report.scope.generation_requests == 70
    assert report.scope.count_requests_proposed == 70
    assert report.scope.total_http_requests_proposed == 140
    assert report.scope.usage_cap_usd == "5.00" and report.scope.retries == 0
    assert report.accounting.method == "provider-exact-input-count"
    assert report.accounting.observed_count_requests == 0
    assert report.accounting.local_framing_certified is False
    assert report.accounting.count_timeout_seconds == 10
    assert report.operator.account_id is None and report.operator.project_id is None
    assert "OWNER_LIVE_AUTHORIZATION_MISSING" in report.blockers
    assert "COUNT_TRAFFIC_APPROVAL_MISSING" in report.blockers
    assert "MODEL_ACCESS_UNVERIFIED" in report.blockers
    assert [path.read_bytes() for path in paths] == before


def test_preflight_cli_needs_no_run_or_credential_and_exits_blocked(tmp_path, capsys):
    result = main(["preflight"])
    assert result == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["launch_ready"] is False
    assert payload["provider_requests_made"] == payload["generation_calls_made"] == 0
    assert not list(tmp_path.iterdir())


def test_preflight_rejects_changed_proposal_without_reporting_payload(tmp_path):
    from task9.preflight import PreflightError, build_launch_preflight

    proposal = yaml.safe_load((BENCH / "configs/feasibility-six.proposed.yaml").read_text())
    proposal["retry_limit"] = 1
    path = tmp_path / "changed.yaml"
    path.write_text(yaml.safe_dump(proposal))
    with pytest.raises(PreflightError, match="^TASK9_PREFLIGHT_CONFIG_INVALID$"):
        build_launch_preflight(config_path=path)


@pytest.mark.parametrize("change", [
    {"ablation": "ledger"},
    {"skill_path": str(BENCH.parent / "skills/systematic-innovation")},
    {"embedded_output_cap": 99},
])
def test_preflight_rejects_settings_that_the_execution_guard_refuses(tmp_path, change):
    from task9.preflight import PreflightError, build_launch_preflight

    proposal = yaml.safe_load((BENCH / "configs/feasibility-six.proposed.yaml").read_text())
    if "embedded_output_cap" in change:
        proposal["model_parameters"]["max_output_tokens"] = change["embedded_output_cap"]
    else:
        proposal.update(change)
    path = tmp_path / "unsupported.yaml"
    path.write_text(yaml.safe_dump(proposal))
    with pytest.raises(PreflightError, match="^TASK9_PREFLIGHT_CONFIG_INVALID$"):
        build_launch_preflight(config_path=path)
