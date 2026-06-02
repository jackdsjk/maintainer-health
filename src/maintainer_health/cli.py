from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from maintainer_health.audit import (
    PROFILE_CHECKS,
    PROFILE_DESCRIPTIONS,
    AuditResult,
    audit_repository,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="maintainer-health",
        description="Audit a local open-source repository for maintenance health.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository path to audit. Defaults to the current directory.",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON.",
    )
    output_group.add_argument(
        "--fix-plan",
        action="store_true",
        help="Print a Markdown checklist for missing maintenance basics.",
    )
    output_group.add_argument(
        "--format",
        choices=["markdown"],
        help="Print a report in the selected format.",
    )
    parser.add_argument(
        "--fail-under",
        type=int,
        default=None,
        metavar="PERCENT",
        help="Exit with status 2 if the score percentage is below this threshold.",
    )
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILE_CHECKS),
        default="all",
        help=(
            "Audit against a specific maintenance scenario. "
            "Defaults to all checks."
        ),
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available maintenance profiles and exit.",
    )

    args = parser.parse_args(argv)

    if args.list_profiles:
        print(_to_profile_list())
        return 0

    try:
        result = audit_repository(args.path, profile=args.profile)
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(_to_json(result))
    elif args.fix_plan:
        print(_to_fix_plan(result))
    elif args.format == "markdown":
        print(_to_markdown(result))
    else:
        print(_to_text(result))

    if args.fail_under is not None and result.percentage < args.fail_under:
        return 2
    return 0


def _to_json(result: AuditResult) -> str:
    payload = asdict(result)
    payload["path"] = str(result.path)
    payload["profile"] = result.profile
    payload["grade"] = result.grade
    payload["percentage"] = result.percentage
    return json.dumps(payload, indent=2, sort_keys=True)


def _to_profile_list() -> str:
    lines = ["Available profiles:"]
    for profile in sorted(PROFILE_DESCRIPTIONS):
        lines.append(f"  {profile}: {PROFILE_DESCRIPTIONS[profile]}")
    return "\n".join(lines)


def _to_text(result: AuditResult) -> str:
    lines = [
        f"Repository: {Path(result.path)}",
        f"Profile: {result.profile}",
        f"Profile goal: {PROFILE_DESCRIPTIONS[result.profile]}",
        (
            f"Score: {result.score}/{result.max_score} "
            f"({result.percentage}%) - Grade {result.grade}"
        ),
        f"Ecosystems: {_format_ecosystems(result)}",
        "",
        "Checks:",
    ]

    for check in result.checks:
        mark = "PASS" if check.passed else "FAIL"
        lines.append(f"  [{mark}] {check.title} ({check.weight} pts)")
        lines.append(f"        {check.detail}")
        if not check.passed:
            lines.append(f"        Next: {check.recommendation}")

    if result.failed_checks:
        lines.extend(["", "Top next steps:"])
        for check in result.failed_checks[:5]:
            lines.append(f"  - {check.recommendation}")
    else:
        lines.extend(["", "No missing maintenance basics found."])

    return "\n".join(lines)


def _to_fix_plan(result: AuditResult) -> str:
    lines = [
        f"# Maintenance Fix Plan: {result.path.name}",
        "",
        f"Profile: {result.profile}",
        f"Profile goal: {PROFILE_DESCRIPTIONS[result.profile]}",
        "",
        (
            f"Current score: {result.score}/{result.max_score} "
            f"({result.percentage}%) - Grade {result.grade}"
        ),
        "",
    ]

    if not result.failed_checks:
        lines.append("No missing maintenance basics found.")
        return "\n".join(lines)

    lines.append("## Checklist")
    lines.append("")
    for check in result.failed_checks:
        lines.append(f"- [ ] **{check.title}** ({check.weight} pts)")
        lines.append(f"  - Finding: {check.detail}")
        lines.append(f"  - Next: {check.recommendation}")

    return "\n".join(lines)


def _to_markdown(result: AuditResult) -> str:
    lines = [
        f"# Maintenance Health Report: {result.path.name}",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Profile | {result.profile} |",
        f"| Profile goal | {PROFILE_DESCRIPTIONS[result.profile]} |",
        f"| Score | {result.score}/{result.max_score} |",
        f"| Percentage | {result.percentage}% |",
        f"| Grade | {result.grade} |",
        f"| Ecosystems | {_format_ecosystems(result)} |",
        "",
        "## Checks",
        "",
        "| Status | Check | Weight | Finding |",
        "| --- | --- | ---: | --- |",
    ]

    for check in result.checks:
        status = "PASS" if check.passed else "FAIL"
        lines.append(
            f"| {status} | {check.title} | {check.weight} | {check.detail} |"
        )

    if result.failed_checks:
        lines.extend(["", "## Recommended Next Steps", ""])
        for check in result.failed_checks[:5]:
            lines.append(f"- **{check.title}:** {check.recommendation}")

    return "\n".join(lines)


def _format_ecosystems(result: AuditResult) -> str:
    if not result.ecosystems:
        return "none detected"
    return ", ".join(result.ecosystems)
