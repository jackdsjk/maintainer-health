from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckResult:
    """One maintenance health check."""

    key: str
    title: str
    passed: bool
    weight: int
    detail: str
    recommendation: str


@dataclass(frozen=True)
class AuditResult:
    """Complete repository audit result."""

    path: Path
    score: int
    max_score: int
    checks: tuple[CheckResult, ...]
    ecosystems: tuple[str, ...]

    @property
    def grade(self) -> str:
        percentage = self.percentage
        if percentage >= 90:
            return "A"
        if percentage >= 75:
            return "B"
        if percentage >= 60:
            return "C"
        if percentage >= 40:
            return "D"
        return "F"

    @property
    def percentage(self) -> int:
        if self.max_score == 0:
            return 0
        return round((self.score / self.max_score) * 100)

    @property
    def failed_checks(self) -> tuple[CheckResult, ...]:
        return tuple(check for check in self.checks if not check.passed)


def audit_repository(path: str | Path) -> AuditResult:
    """Audit a local repository path for open-source maintenance readiness."""

    repo_path = Path(path).expanduser().resolve()
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
    if not repo_path.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {repo_path}")

    ecosystems = _detect_ecosystems(repo_path)
    checks = (
        _check_readme(repo_path),
        _check_license(repo_path),
        _check_contributing(repo_path),
        _check_code_of_conduct(repo_path),
        _check_security_policy(repo_path),
        _check_ci(repo_path),
        _check_tests(repo_path),
        _check_issue_templates(repo_path),
        _check_pull_request_template(repo_path),
        _check_changelog(repo_path),
        _check_release_metadata(repo_path),
        _check_package_metadata(repo_path),
        *_check_ecosystems(repo_path, ecosystems),
    )
    score = sum(check.weight for check in checks if check.passed)
    max_score = sum(check.weight for check in checks)
    return AuditResult(
        path=repo_path,
        score=score,
        max_score=max_score,
        checks=checks,
        ecosystems=ecosystems,
    )


def _detect_ecosystems(path: Path) -> tuple[str, ...]:
    ecosystems = []
    ecosystem_markers = (
        ("python", ("pyproject.toml", "setup.py", "requirements.txt")),
        ("javascript", ("package.json", "pnpm-lock.yaml", "yarn.lock")),
        ("rust", ("Cargo.toml",)),
        ("go", ("go.mod",)),
    )
    for ecosystem, markers in ecosystem_markers:
        if any((path / marker).exists() for marker in markers):
            ecosystems.append(ecosystem)
    return tuple(ecosystems)


def _check_ecosystems(
    path: Path,
    ecosystems: tuple[str, ...],
) -> tuple[CheckResult, ...]:
    checks = []
    if "python" in ecosystems:
        checks.append(_check_python_project(path))
    if "javascript" in ecosystems:
        checks.append(_check_javascript_project(path))
    if "rust" in ecosystems:
        checks.append(_check_rust_project(path))
    if "go" in ecosystems:
        checks.append(_check_go_project(path))
    return tuple(checks)


def _check_python_project(path: Path) -> CheckResult:
    pyproject = path / "pyproject.toml"
    if not pyproject.exists():
        return _fail(
            "python_metadata",
            "Python metadata",
            6,
            "Detected Python files but no pyproject.toml.",
            "Add pyproject.toml with project metadata and supported Python versions.",
        )

    text = _read_text(pyproject)
    has_project = "[project]" in text
    has_python = "requires-python" in text
    has_tests = "pytest" in text or (path / "tests").exists()
    if has_project and has_python and has_tests:
        return _pass(
            "python_metadata",
            "Python metadata",
            6,
            "Found pyproject.toml with project metadata, runtime, and test signal.",
        )
    return _fail(
        "python_metadata",
        "Python metadata",
        6,
        "Python metadata is missing project, runtime, or test information.",
        "Add [project], requires-python, and a documented test dependency or tests/.",
    )


def _check_javascript_project(path: Path) -> CheckResult:
    package_json = path / "package.json"
    if not package_json.exists():
        return _fail(
            "javascript_metadata",
            "JavaScript metadata",
            6,
            "Detected JavaScript markers but no package.json.",
            "Add package.json with scripts, license, and supported Node version.",
        )

    text = _read_text(package_json)
    has_scripts = '"scripts"' in text
    has_test = '"test"' in text
    has_engines = '"engines"' in text
    if has_scripts and has_test and has_engines:
        return _pass(
            "javascript_metadata",
            "JavaScript metadata",
            6,
            "Found package.json with scripts, test command, and engines.",
        )
    return _fail(
        "javascript_metadata",
        "JavaScript metadata",
        6,
        "package.json is missing scripts, test command, or engines.",
        (
            "Add scripts.test and engines.node so contributors know how to "
            "validate changes."
        ),
    )


def _check_rust_project(path: Path) -> CheckResult:
    cargo_toml = path / "Cargo.toml"
    text = _read_text(cargo_toml)
    has_package = "[package]" in text
    has_edition = "edition" in text
    has_ci_or_tests = (
        (path / ".github" / "workflows").exists() or (path / "tests").exists()
    )
    if has_package and has_edition and has_ci_or_tests:
        return _pass(
            "rust_metadata",
            "Rust metadata",
            6,
            "Found Cargo.toml with package metadata, edition, and validation signal.",
        )
    return _fail(
        "rust_metadata",
        "Rust metadata",
        6,
        "Cargo.toml is missing package metadata, edition, or validation signal.",
        "Add package metadata, edition, and CI or tests for cargo test.",
    )


def _check_go_project(path: Path) -> CheckResult:
    go_mod = path / "go.mod"
    text = _read_text(go_mod)
    has_module = text.startswith("module ") or "\nmodule " in text
    has_go_version = "\ngo " in text
    has_tests = any(path.rglob("*_test.go"))
    if has_module and has_go_version and has_tests:
        return _pass(
            "go_metadata",
            "Go metadata",
            6,
            "Found go.mod with module, Go version, and tests.",
        )
    return _fail(
        "go_metadata",
        "Go metadata",
        6,
        "Go project is missing module metadata, Go version, or tests.",
        "Add module metadata, a Go version, and at least one *_test.go file.",
    )


def _check_readme(path: Path) -> CheckResult:
    readme = _first_existing(path, ["README.md", "README.rst", "README.txt"])
    if not readme:
        return _fail(
            "readme",
            "README",
            12,
            "No README file found.",
            "Add a README with purpose, install steps, usage examples, and status.",
        )

    text = _read_text(readme)
    has_usage = any(word in text.lower() for word in ("usage", "quickstart", "example"))
    if has_usage and len(text.strip()) >= 500:
        return _pass("readme", "README", 12, f"Found {readme.name} with usage context.")
    return _fail(
        "readme",
        "README",
        12,
        f"Found {readme.name}, but it looks thin.",
        "Expand the README with a concrete usage example and maintenance status.",
    )


def _check_license(path: Path) -> CheckResult:
    license_file = _first_existing(path, ["LICENSE", "LICENSE.md", "COPYING"])
    if license_file:
        return _pass("license", "License", 10, f"Found {license_file.name}.")
    return _fail(
        "license",
        "License",
        10,
        "No license file found.",
        "Add an OSI-approved license so others know how they can use the project.",
    )


def _check_contributing(path: Path) -> CheckResult:
    contributing = _first_existing(
        path,
        ["CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md"],
    )
    if contributing:
        return _pass(
            "contributing",
            "Contributing guide",
            8,
            f"Found {contributing.relative_to(path)}.",
        )
    return _fail(
        "contributing",
        "Contributing guide",
        8,
        "No contributing guide found.",
        "Add CONTRIBUTING.md with setup, tests, issue scope, and PR expectations.",
    )


def _check_code_of_conduct(path: Path) -> CheckResult:
    conduct = _first_existing(
        path,
        ["CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"],
    )
    if conduct:
        return _pass(
            "code_of_conduct",
            "Code of conduct",
            5,
            f"Found {conduct.relative_to(path)}.",
        )
    return _fail(
        "code_of_conduct",
        "Code of conduct",
        5,
        "No code of conduct found.",
        "Add a code of conduct to make contribution norms explicit.",
    )


def _check_security_policy(path: Path) -> CheckResult:
    security = _first_existing(path, ["SECURITY.md", ".github/SECURITY.md"])
    if security:
        return _pass(
            "security",
            "Security policy",
            7,
            f"Found {security.relative_to(path)}.",
        )
    return _fail(
        "security",
        "Security policy",
        7,
        "No security policy found.",
        "Add SECURITY.md with supported versions and vulnerability reporting steps.",
    )


def _check_ci(path: Path) -> CheckResult:
    workflows = path / ".github" / "workflows"
    has_github_workflow = workflows.exists() and (
        any(workflows.glob("*.yml")) or any(workflows.glob("*.yaml"))
    )
    if has_github_workflow:
        return _pass(
            "ci",
            "Continuous integration",
            12,
            "Found GitHub Actions workflow.",
        )

    other_ci = _first_existing(
        path,
        [".gitlab-ci.yml", ".circleci/config.yml", "azure-pipelines.yml"],
    )
    if other_ci:
        return _pass("ci", "Continuous integration", 12, f"Found {other_ci.name}.")

    return _fail(
        "ci",
        "Continuous integration",
        12,
        "No CI workflow found.",
        "Add CI that runs tests and lint on pull requests.",
    )


def _check_tests(path: Path) -> CheckResult:
    test_dirs = [path / "tests", path / "test"]
    test_files = []
    for test_dir in test_dirs:
        if test_dir.exists():
            test_files.extend(test_dir.rglob("test_*.py"))
            test_files.extend(test_dir.rglob("*_test.py"))
            test_files.extend(test_dir.rglob("*.test.ts"))
            test_files.extend(test_dir.rglob("*.spec.ts"))

    if test_files:
        return _pass("tests", "Tests", 12, f"Found {len(test_files)} test file(s).")
    return _fail(
        "tests",
        "Tests",
        12,
        "No recognizable test files found.",
        "Add focused tests for the core behavior and run them in CI.",
    )


def _check_issue_templates(path: Path) -> CheckResult:
    template_dir = path / ".github" / "ISSUE_TEMPLATE"
    if template_dir.exists() and any(template_dir.iterdir()):
        return _pass(
            "issue_templates",
            "Issue templates",
            5,
            "Found issue template directory.",
        )

    single_template = path / ".github" / "ISSUE_TEMPLATE.md"
    if single_template.exists():
        return _pass(
            "issue_templates",
            "Issue templates",
            5,
            "Found single issue template.",
        )

    return _fail(
        "issue_templates",
        "Issue templates",
        5,
        "No issue templates found.",
        "Add bug report and feature request templates to improve triage quality.",
    )


def _check_pull_request_template(path: Path) -> CheckResult:
    template = _first_existing(
        path,
        [
            ".github/PULL_REQUEST_TEMPLATE.md",
            "PULL_REQUEST_TEMPLATE.md",
            "docs/PULL_REQUEST_TEMPLATE.md",
        ],
    )
    if template:
        return _pass(
            "pull_request_template",
            "Pull request template",
            5,
            f"Found {template.relative_to(path)}.",
        )
    return _fail(
        "pull_request_template",
        "Pull request template",
        5,
        "No pull request template found.",
        "Add a PR template with summary, tests, and risk checklist.",
    )


def _check_changelog(path: Path) -> CheckResult:
    changelog = _first_existing(path, ["CHANGELOG.md", "HISTORY.md", "RELEASES.md"])
    if changelog:
        return _pass("changelog", "Changelog", 7, f"Found {changelog.name}.")
    return _fail(
        "changelog",
        "Changelog",
        7,
        "No changelog found.",
        "Add a changelog so users can understand release history.",
    )


def _check_release_metadata(path: Path) -> CheckResult:
    if (path / ".github" / "release.yml").exists() or (
        path / ".github" / "release.yaml"
    ).exists():
        return _pass(
            "release_metadata",
            "Release metadata",
            5,
            "Found GitHub release metadata.",
        )

    if _first_existing(path, [".releaserc", "release-please-config.json"]):
        return _pass(
            "release_metadata",
            "Release metadata",
            5,
            "Found release automation config.",
        )

    return _fail(
        "release_metadata",
        "Release metadata",
        5,
        "No release metadata found.",
        "Add release notes configuration or document your release process.",
    )


def _check_package_metadata(path: Path) -> CheckResult:
    metadata = _first_existing(
        path,
        ["pyproject.toml", "package.json", "Cargo.toml", "go.mod"],
    )
    if metadata:
        return _pass(
            "package_metadata",
            "Package metadata",
            12,
            f"Found {metadata.name}.",
        )
    return _fail(
        "package_metadata",
        "Package metadata",
        12,
        "No package metadata found.",
        "Add package metadata with name, version, license, and supported runtimes.",
    )


def _first_existing(path: Path, candidates: list[str]) -> Path | None:
    for candidate in candidates:
        candidate_path = path / candidate
        if candidate_path.exists():
            return candidate_path
    return None


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")


def _pass(key: str, title: str, weight: int, detail: str) -> CheckResult:
    return CheckResult(
        key=key,
        title=title,
        passed=True,
        weight=weight,
        detail=detail,
        recommendation="No action needed.",
    )


def _fail(
    key: str,
    title: str,
    weight: int,
    detail: str,
    recommendation: str,
) -> CheckResult:
    return CheckResult(
        key=key,
        title=title,
        passed=False,
        weight=weight,
        detail=detail,
        recommendation=recommendation,
    )
