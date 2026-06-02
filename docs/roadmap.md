# Roadmap

`maintainer-health` should become a practical readiness tool for small open-source
maintainers, not a vanity score generator.

The product bet is simple: many maintainers do not need another dashboard. They need
a fast local command that answers, "What is blocking this repository from being
usable by contributors, safe enough to publish, or ready for a release?"

The project stays offline-first by default. Network-backed checks can exist later,
but they must be opt-in, clearly labeled, and useful without handling secrets.

## Real Users

### Solo maintainer preparing a repo for contributors

They want to know whether a stranger can understand the project, run it, report bugs,
and open a pull request without asking basic setup questions.

Useful outcome: a short, ranked checklist for contributor readiness.

### Student or early developer publishing a project

They want the repository to look credible without pretending the project is more
mature than it is.

Useful outcome: honest release and metadata checks that make the repo easier to
review, install, and improve.

### Team using CI as a maintenance gate

They want a repeatable check that can fail a pull request when maintenance basics
regress.

Useful outcome: stable JSON, Markdown, and future SARIF output that integrate with
existing workflows.

## Product Principles

- Prefer actionable findings over broad scores.
- Keep local audits fast, dependency-light, and deterministic.
- Make profiles match real maintainer jobs.
- Avoid claiming project quality, popularity, or program eligibility.
- Use network calls only when they add information the local filesystem cannot know.

## Phase 1: Scenario-Based Audits

Status: in progress.

Goal: make the tool useful at the moment a maintainer has a concrete job to do.

Delivered:

- `--profile contributor-ready`
- `--profile release-ready`
- `--profile security-baseline`
- `--list-profiles`
- Profile descriptions in text, Markdown, and fix-plan output.

Next:

- Add tests that protect each profile's expected check set.

## Phase 2: Prioritized Fix Plans

Goal: turn the audit from "what failed" into "what should I fix first?"

Planned work:

- Add severity or priority metadata to checks.
- Group recommendations by maintainer job: docs, trust, automation, release, ecosystem.
- Make `--fix-plan` output the top three highest-leverage fixes first.
- Include small examples for common missing files such as `SECURITY.md` and PR templates.

Useful outcome: a maintainer can run one command and know the next hour of work.

## Phase 3: Config Without Complexity

Goal: let real projects adapt the audit without making configuration the product.

Planned work:

- Add a small `maintainer-health.toml` config file.
- Support disabled checks for repositories where a check is intentionally irrelevant.
- Support profile-specific `fail-under` thresholds.
- Support check weight overrides only after the default weighting has proven stable.

Useful outcome: teams can adopt the tool in CI without fighting the defaults.

## Phase 4: CI And Report Integrations

Goal: make findings visible where maintainers already work.

Planned work:

- Add SARIF output for code scanning viewers.
- Add a GitHub Actions example workflow.
- Add a `--changed-files` mode later if the tool grows into regression checks.
- Keep JSON output stable enough for downstream scripts.

Useful outcome: maintenance regressions can appear in pull requests, not just in a
terminal after someone remembers to run the tool.

## Phase 5: Optional GitHub Enrichment

Goal: add activity context that local files cannot reveal.

Potential checks:

- Recent release activity.
- Stale open pull requests.
- Stale open issues.
- Default branch protection signals when available.
- Whether issue and PR templates are actually used in recent activity.

Constraints:

- This must be opt-in.
- Local audits must keep working without credentials.
- Output must clearly separate local facts from GitHub API facts.

Useful outcome: the tool can identify repos that have good files but unhealthy
maintainer workflows.

## Phase 6: Maintainer Operating Rhythm

Goal: help maintainers keep a repo healthy over time.

Planned work:

- Add a monthly maintenance report format.
- Add trend-friendly JSON fields so teams can compare scores over time.
- Add a lightweight "maintenance review" checklist for release notes, stale issues,
  security policy, and contributor docs.

Useful outcome: `maintainer-health` becomes part of a maintenance habit, not a
one-time cleanup script.

## Completed

- `2026-06-01`: Added `--fix-plan` Markdown checklist output.
- `2026-06-02`: Added ecosystem detection and Markdown report output.
