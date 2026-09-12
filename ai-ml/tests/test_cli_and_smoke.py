"""Tests for the headless CLI and the end-to-end smoke flow."""

from __future__ import annotations

import json

import pytest

from autoflow_ai import samples
from autoflow_ai.cli import main

pytestmark = pytest.mark.contract


def test_smoke_flow_all_checks_pass():
    report = samples.smoke_flow()
    assert report["ok"] is True, report
    assert report["total"] >= 8
    assert all(c["passed"] for c in report["checks"])


def test_cli_version(capsys):
    assert main(["version"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["autoflow_ai"] == "0.1.0"


def test_cli_contracts_list(capsys):
    assert main(["contracts", "list"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == len(out["contracts"])
    assert "TaskGraph" in out["contracts"]
    assert "ApprovalRequest" in out["contracts"]


def test_cli_contracts_check_passes(capsys):
    rc = main(["contracts", "check"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["failed"] == 0
    assert out["passed"] == out["checked"] == 33


def test_cli_eval_smoke_passes(capsys):
    rc = main(["eval", "smoke"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["ok"] is True


def test_cli_phase_status(capsys):
    assert main(["phase", "status"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["current_phase"] == 1


def test_cli_requires_subcommand():
    with pytest.raises(SystemExit):
        main([])
