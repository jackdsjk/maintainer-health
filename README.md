# maintainer-health

`maintainer-health` is an offline CLI that audits a local open-source repository for maintenance basics: README quality, license, contribution docs, security policy, CI, tests, issue templates, release metadata, and package metadata.

The goal is practical: give maintainers a quick checklist they can run before inviting contributors, applying to open-source programs, or cleaning up an older project. It does not claim that a repository is important, popular, or eligible for any external program. It only checks whether the local repo has the maintenance signals that contributors usually need.

## Quickstart

```bash
python -m pip install -e ".[dev]"
maintainer-health .
```

Machine-readable output:

```bash
maintainer-health . --json
```

Markdown fix plan:

```bash
maintainer-health . --fix-plan
```

The fix plan is prioritized by maintainer impact. It shows the top three fixes
first, then groups the full checklist by maintenance area.

Markdown report:

```bash
maintainer-health . --format markdown
```

CI gate example:

```bash
maintainer-health . --fail-under 75
```

Audit a specific maintenance scenario:

```bash
maintainer-health . --profile contributor-ready
maintainer-health . --profile release-ready
maintainer-health . --profile security-baseline
```

## What It Checks

| Check | Why it matters |
| --- | --- |
| README | Contributors need purpose, setup, usage, and project status. |
| License | Users need clear permission to use and contribute. |
| Contributing guide | New contributors need setup, testing, and PR expectations. |
| Code of conduct | Community norms should be explicit. |
| Security policy | Vulnerability reports need a clear private path. |
| CI | Maintainers need automated confidence on pull requests. |
| Tests | Core behavior should be verifiable. |
| Issue templates | Triage is faster when reports are structured. |
| Pull request template | Reviews are easier with summary, tests, and risk notes. |
| Changelog | Users need to understand release history. |
| Release metadata | Maintainers need a repeatable release process. |
| Package metadata | Tooling and users need project identity and runtime support. |
| Ecosystem metadata | Python, JavaScript, Rust, and Go projects need runtime-specific validation signals. |

Each check also includes a category, priority, and estimated effort so maintainers
can decide what to fix first.

## Profiles

Most repositories do not need the same checklist every day. Profiles let maintainers
run the audit against the job they are actually doing.

| Profile | Use it when |
| --- | --- |
| `all` | You want the full maintenance baseline. |
| `contributor-ready` | You are preparing a repo for outside contributors. |
| `release-ready` | You are checking whether a repo is ready to publish or tag. |
| `security-baseline` | You want a small baseline for security reporting, CI, tests, and metadata. |

## Example

```text
Repository: /path/to/project
Profile: all
Score: 78/100 (78%) - Grade B

Checks:
  [PASS] README (12 pts)
        Found README.md with usage context.
  [FAIL] Security policy (7 pts)
        No security policy found.
        Next: Add SECURITY.md with supported versions and vulnerability reporting steps.
```

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m maintainer_health . --json
```

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for planned maintenance work.

Near-term focus:

- Prioritized fix plans that show the highest-leverage next work first.
- Lightweight config for disabled checks and profile-specific thresholds.
- SARIF output for CI and code scanning integrations.

## License

MIT
