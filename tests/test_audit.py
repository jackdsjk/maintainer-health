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
    write(tmp_path / "pyproject.toml", "[project]\nname='demo'")

    result = audit_repository(tmp_path)

    assert result.percentage == 100
    assert result.grade == "A"
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
