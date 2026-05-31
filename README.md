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

CI gate example:

```bash
maintainer-health . --fail-under 75
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

## Example

```text
Repository: /path/to/project
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

- Language-specific checks for Python, JavaScript, Rust, and Go.
- `--fix-plan` output that creates a prioritized maintenance task list.
- Markdown report output for CI comments and issue bodies.

## License

MIT
