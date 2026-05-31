from __future__ import annotations

import json
from pathlib import Path

from maintainer_health.cli import main


def test_cli_json_output(tmp_path: Path, capsys) -> None:
    exit_code = main([str(tmp_path), "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["path"] == str(tmp_path.resolve())
    assert "checks" in payload


def test_cli_fail_under_returns_status_two(tmp_path: Path) -> None:
    exit_code = main([str(tmp_path), "--fail-under", "90"])

    assert exit_code == 2
