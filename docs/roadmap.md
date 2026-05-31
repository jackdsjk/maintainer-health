# Roadmap

This roadmap keeps near-term maintenance work concrete and reviewable. The project stays offline-first by default; network-backed checks should be optional and clearly labeled.

## Near Term

### Language-specific maintenance checks

Add focused checks for common package ecosystems:

- Python: build backend, test command, supported Python versions, package classifiers.
- JavaScript: package scripts, lockfile presence, supported Node version, test command.
- Rust: crate metadata, MSRV note, cargo test availability.
- Go: module metadata, test packages, supported Go version.

### Fix plan output

Add `--fix-plan` to emit a prioritized Markdown checklist for missing maintenance basics. The output should be useful as an issue body or local cleanup plan.

### Markdown report output

Add `--format markdown` for CI summaries and pull request comments. It should include score, grade, failed checks, and top next steps.

## Later

### Optional GitHub enrichment

Add opt-in GitHub API checks for repository activity signals such as releases, stale issues, stale pull requests, and response time. This must remain optional and must not require credentials for local audits.

### SARIF output

Add SARIF output so repository maintenance gaps can appear in GitHub code scanning or other compatible viewers.

### Check configuration

Add a small config file for teams that want to disable checks, change weights, or raise/lower CI thresholds.
