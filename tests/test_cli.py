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
    assert payload["profile"] == "all"
    assert "checks" in payload
    assert "ecosystems" in payload


def test_cli_fail_under_returns_status_two(tmp_path: Path) -> None:
    exit_code = main([str(tmp_path), "--fail-under", "90"])

    assert exit_code == 2


def test_cli_fix_plan_outputs_markdown_checklist(tmp_path: Path, capsys) -> None:
    exit_code = main([str(tmp_path), "--fix-plan"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# Maintenance Fix Plan:" in captured.out
    assert "- [ ] **README**" in captured.out
    assert "Add a README with purpose" in captured.out


def test_cli_fix_plan_reports_when_nothing_is_missing(tmp_path: Path, capsys) -> None:
    (tmp_path / "README.md").write_text("Usage\n" + "example " * 100)
    (tmp_path / "LICENSE").write_text("MIT")
    (tmp_path / "CONTRIBUTING.md").write_text("Run tests.")
    (tmp_path / "CODE_OF_CONDUCT.md").write_text("Be respectful.")
    (tmp_path / "SECURITY.md").write_text("Report privately.")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: CI")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_sample.py").write_text("def test_sample(): assert True")
    (tmp_path / ".github" / "ISSUE_TEMPLATE").mkdir()
    (tmp_path / ".github" / "ISSUE_TEMPLATE" / "bug.md").write_text("Bug")
    (tmp_path / ".github" / "PULL_REQUEST_TEMPLATE.md").write_text("Summary")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog")
    (tmp_path / ".github" / "release.yml").write_text("changelog:")
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='demo'\nrequires-python='>=3.10'\n"
    )

    exit_code = main([str(tmp_path), "--fix-plan"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "No missing maintenance basics found." in captured.out


def test_cli_markdown_output_includes_score_and_checks(tmp_path: Path, capsys) -> None:
    exit_code = main([str(tmp_path), "--format", "markdown"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# Maintenance Health Report:" in captured.out
    assert "| Profile | all |" in captured.out
    assert "| Score |" in captured.out
    assert "| FAIL | README |" in captured.out


def test_cli_profile_changes_audit_scope(tmp_path: Path, capsys) -> None:
    exit_code = main([str(tmp_path), "--profile", "release-ready", "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    checked_keys = {check["key"] for check in payload["checks"]}
    assert exit_code == 0
    assert payload["profile"] == "release-ready"
    assert "changelog" in checked_keys
    assert "security" not in checked_keys


def test_cli_lists_profiles(capsys) -> None:
    exit_code = main(["--list-profiles"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Available profiles:" in captured.out
    assert "contributor-ready:" in captured.out
    assert "security-baseline:" in captured.out
