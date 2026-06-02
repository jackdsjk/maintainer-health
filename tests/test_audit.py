from __future__ import annotations

from pathlib import Path

import pytest

from maintainer_health.audit import audit_repository


def write(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_audit_scores_complete_repository(tmp_path: Path) -> None:
    write(
        tmp_path / "README.md",
        "Usage\n\n"
        + "This project audits maintenance health for open-source repositories. "
        * 12,
    )
    write(tmp_path / "LICENSE", "MIT")
    write(tmp_path / "CONTRIBUTING.md", "Run tests before opening a PR.")
    write(tmp_path / "CODE_OF_CONDUCT.md", "Be respectful.")
    write(tmp_path / "SECURITY.md", "Report vulnerabilities privately.")
    write(tmp_path / ".github" / "workflows" / "ci.yml", "name: CI")
    write(tmp_path / "tests" / "test_sample.py", "def test_sample(): assert True")
    write(tmp_path / ".github" / "ISSUE_TEMPLATE" / "bug_report.md", "Bug report")
    write(tmp_path / ".github" / "PULL_REQUEST_TEMPLATE.md", "Summary\nTests")
    write(tmp_path / "CHANGELOG.md", "# Changelog")
    write(tmp_path / ".github" / "release.yml", "changelog:")
    write(
        tmp_path / "pyproject.toml",
        "[project]\nname='demo'\nrequires-python='>=3.10'\n",
    )

    result = audit_repository(tmp_path)

    assert result.percentage == 100
    assert result.grade == "A"
    assert result.ecosystems == ("python",)
    assert not result.failed_checks


def test_audit_reports_missing_maintenance_files(tmp_path: Path) -> None:
    result = audit_repository(tmp_path)

    failed_keys = {check.key for check in result.failed_checks}
    assert "readme" in failed_keys
    assert "license" in failed_keys
    assert "ci" in failed_keys
    assert result.grade == "F"


def test_audit_rejects_missing_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        audit_repository(tmp_path / "missing")


def test_audit_detects_javascript_project_metadata(tmp_path: Path) -> None:
    write(
        tmp_path / "package.json",
        '{"scripts":{"test":"node --test"},"engines":{"node":">=20"}}',
    )

    result = audit_repository(tmp_path)

    assert "javascript" in result.ecosystems
    javascript_check = next(
        check for check in result.checks if check.key == "javascript_metadata"
    )
    assert javascript_check.passed


def test_audit_profile_limits_checks_to_real_maintenance_scenario(
    tmp_path: Path,
) -> None:
    write(tmp_path / "SECURITY.md", "Report vulnerabilities privately.")

    result = audit_repository(tmp_path, profile="security-baseline")

    checked_keys = {check.key for check in result.checks}
    assert result.profile == "security-baseline"
    assert "security" in checked_keys
    assert "readme" not in checked_keys
    assert "contributing" not in checked_keys
    assert "changelog" not in checked_keys


def test_audit_rejects_unknown_profile(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unknown profile"):
        audit_repository(tmp_path, profile="made-up")


def test_audit_flags_incomplete_go_project(tmp_path: Path) -> None:
    write(tmp_path / "go.mod", "module example.com/demo\n\ngo 1.23\n")

    result = audit_repository(tmp_path)

    assert "go" in result.ecosystems
    go_check = next(check for check in result.checks if check.key == "go_metadata")
    assert not go_check.passed
    assert "*_test.go" in go_check.recommendation
