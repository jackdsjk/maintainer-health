# Roadmap

This roadmap keeps near-term maintenance work concrete and reviewable. The project stays offline-first by default; network-backed checks should be optional and clearly labeled.

## Near Term

### Optional GitHub enrichment

Add opt-in GitHub API checks for repository activity signals such as releases, stale issues, stale pull requests, and response time. This must remain optional and must not require credentials for local audits.

### SARIF output

Add SARIF output so repository maintenance gaps can appear in GitHub code scanning or other compatible viewers.

### Check configuration

Add a small config file for teams that want to disable checks, change weights, or raise/lower CI thresholds.

## Completed

- `2026-06-01`: Added `--fix-plan` Markdown checklist output.
- `2026-06-02`: Added ecosystem detection and Markdown report output.
