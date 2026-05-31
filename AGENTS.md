# maintainer-health

This repository contains a Python CLI that audits open-source repository maintenance health.

## Editing Boundaries

- Core audit logic lives in `src/maintainer_health/`.
- Tests live in `tests/` and should use temporary directories rather than real GitHub network calls.
- Documentation should stay honest about what the tool checks locally; do not imply it proves project quality or eligibility for any external program.

## Validation

- Run `python -m pytest` for tests.
- Run `python -m ruff check .` for lint.
- Run `python -m maintainer_health --help` for the CLI smoke check.
- Run `python -m maintainer_health . --json` to verify the local audit output.

## Constraints

- Keep the package dependency-light and offline-first.
- Do not add telemetry, network calls, or credential handling without explicit approval.
- Keep examples and fixtures small enough to review in normal diffs.
