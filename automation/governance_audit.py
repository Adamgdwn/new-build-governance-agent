#!/usr/bin/env python3
"""Generate an AUD-class governance audit report for a governed project."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path


_DATE_FIELDS = re.compile(
    r"(Last Updated|Effective Date|Last Reviewed|Date)\s*:\s*(\S+)", re.IGNORECASE
)
_STATUS_FIELD = re.compile(r"^Status\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_OWNER_FIELD = re.compile(r"^Owner\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_DOC_ID_FIELD = re.compile(r"^Document ID\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_SUPERSEDED_BY = re.compile(
    r"(Superseded by|Replaced by|See|See also)\s*:\s*\S+", re.IGNORECASE
)
_STALE_THRESHOLD_DAYS = 30
_CARRY_FORWARD_THRESHOLD_DAYS = 7


def _read_header(path: Path, lines: int = 30) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return "\n".join(text.splitlines()[:lines])
    except OSError:
        return ""


def _full_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _has_status(header: str) -> bool:
    return bool(_STATUS_FIELD.search(header))


def _has_owner(header: str) -> bool:
    return bool(_OWNER_FIELD.search(header))


def _has_date_field(header: str) -> bool:
    return bool(_DATE_FIELDS.search(header))


def _get_status(header: str) -> str:
    m = _STATUS_FIELD.search(header)
    return m.group(1).strip().lower() if m else ""


def _get_last_updated(header: str) -> date | None:
    for field in ("Last Updated", "Last Reviewed", "Effective Date", "Date"):
        m = re.search(rf"{field}\s*:\s*(\d{{4}}-\d{{2}}-\d{{2}})", header, re.IGNORECASE)
        if m:
            try:
                return date.fromisoformat(m.group(1))
            except ValueError:
                continue
    return None


def _is_pathway_or_plan(path: Path) -> bool:
    name = path.stem.lower()
    return (
        "pathway" in name
        or "build-plan" in name
        or "build_plan" in name
        or "deployment" in name
        or name.endswith("-plan")
        or name.endswith("_plan")
    )


def _next_audit_sequence(audits_dir: Path) -> int:
    highest = 0
    if audits_dir.is_dir():
        pattern = re.compile(r"AUD-ENG-(\d+)")
        for f in audits_dir.glob("*.md"):
            try:
                m = pattern.search(f.read_text(encoding="utf-8", errors="ignore")[:500])
                if m:
                    highest = max(highest, int(m.group(1)))
            except OSError:
                pass
    return highest + 1


def _docs_md_files(project: Path) -> list[Path]:
    docs = project / "docs"
    if not docs.is_dir():
        return []
    return sorted(p for p in docs.rglob("*.md") if p.is_file())


def _check_carry_forward_staleness(project: Path) -> list[str]:
    cf = project / "CARRY_FORWARD.md"
    if not cf.is_file():
        return []
    today = date.today()
    warnings: list[str] = []
    try:
        text = cf.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        flag, added, _owner, status, _notes = cells[0], cells[1], cells[2], cells[3], cells[4]
        if flag in ("Flag", "---", "(none)", ""):
            continue
        if status.lower() in ("resolved", "closed", "done", ""):
            continue
        m = re.search(r"(\d{4}-\d{2}-\d{2})", added)
        if m:
            try:
                added_date = date.fromisoformat(m.group(1))
                age = (today - added_date).days
                if age > _CARRY_FORWARD_THRESHOLD_DAYS:
                    warnings.append(
                        f"Carry-forward flag `{flag}` open for {age} days (added {added_date}) "
                        "— review, resolve, or update its status."
                    )
            except ValueError:
                pass
    return warnings


def run_audit(project_path: Path) -> dict:
    today = date.today()
    now = datetime.now().astimezone()
    timestamp_str = now.isoformat(timespec="seconds")

    docs_files = _docs_md_files(project_path)

    findings: dict[str, list[str]] = {
        "blockers": [],
        "required_gaps": [],
        "warnings": [],
    }
    positives: list[str] = []
    checks_run: list[str] = []

    # Check 1: Document metadata presence
    checks_run.append(
        "Document metadata presence (Status, Owner, date field) in first 30 lines of every docs/*.md"
    )
    missing_status: list[str] = []
    missing_owner: list[str] = []
    missing_date: list[str] = []
    for f in docs_files:
        rel = str(f.relative_to(project_path))
        header = _read_header(f)
        if not _has_status(header):
            missing_status.append(rel)
        if not _has_owner(header):
            missing_owner.append(rel)
        if not _has_date_field(header):
            missing_date.append(rel)

    if missing_status:
        for rel in missing_status:
            findings["required_gaps"].append(
                f"`{rel}` — add `Status: <draft|active|superseded|retired>` in the first 30 lines."
            )
    else:
        positives.append("All docs/ files have a Status field.")

    if missing_owner:
        for rel in missing_owner:
            findings["warnings"].append(
                f"`{rel}` — add `Owner: <name>` in the first 30 lines."
            )
    else:
        positives.append("All docs/ files have an Owner field.")

    if missing_date:
        for rel in missing_date:
            findings["warnings"].append(
                f"`{rel}` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines."
            )
    else:
        positives.append("All docs/ files have a date field.")

    # Check 2: Supersession markers
    checks_run.append("Superseded docs reference their replacement")
    superseded_no_ref: list[str] = []
    for f in docs_files:
        header = _read_header(f)
        if _get_status(header) == "superseded":
            if not _SUPERSEDED_BY.search(_full_text(f)):
                superseded_no_ref.append(str(f.relative_to(project_path)))

    if superseded_no_ref:
        for rel in superseded_no_ref:
            findings["required_gaps"].append(
                f"`{rel}` has `Status: superseded` but no replacement reference "
                "— add `Superseded by: <path>` near the top."
            )
    else:
        positives.append("All superseded docs reference their replacement.")

    # Check 3: Multiple active pathways
    checks_run.append("At most one active pathway / build-plan document")
    active_pathways: list[str] = []
    for f in docs_files:
        if _is_pathway_or_plan(f):
            if _get_status(_read_header(f)) == "active":
                active_pathways.append(str(f.relative_to(project_path)))

    if len(active_pathways) > 1:
        joined = ", ".join(f"`{p}`" for p in active_pathways)
        findings["blockers"].append(
            f"Multiple active pathway/plan documents: {joined} "
            "— supersede all but one, or confirm which is authoritative."
        )
    elif len(active_pathways) == 1:
        positives.append(f"Single active pathway document: `{active_pathways[0]}`.")
    else:
        positives.append(
            "No active pathway/plan documents (expected if project is not yet underway)."
        )

    # Check 4: Stale active pathway
    checks_run.append("Active pathway updated within last 30 days")
    for f in docs_files:
        if _is_pathway_or_plan(f):
            header = _read_header(f)
            if _get_status(header) == "active":
                last_updated = _get_last_updated(header)
                rel = str(f.relative_to(project_path))
                if last_updated is not None:
                    age = (today - last_updated).days
                    if age > _STALE_THRESHOLD_DAYS:
                        findings["warnings"].append(
                            f"`{rel}` active but last updated {age} days ago ({last_updated}) "
                            "— review and update, or retire if complete."
                        )
                else:
                    findings["warnings"].append(
                        f"`{rel}` is active but has no parseable last-updated date "
                        "— add `Last Updated: YYYY-MM-DD`."
                    )

    # Check 5: Plan / pathway / deployment orphans (no Status field)
    checks_run.append("Build plan / pathway / deployment docs have a Status field")
    for f in docs_files:
        if _is_pathway_or_plan(f):
            if not _has_status(_read_header(f)):
                rel = str(f.relative_to(project_path))
                findings["required_gaps"].append(
                    f"`{rel}` is a plan/pathway/deployment doc with no `Status:` field — add one."
                )

    # Check 6: Document ID gaps in controlled dirs
    checks_run.append(
        "Standards, policies, and processes have Document ID fields"
    )
    controlled_dirs = ["docs/standards", "docs/policy", "docs/processes"]
    id_gaps: list[str] = []
    for rel_dir in controlled_dirs:
        dir_path = project_path / rel_dir
        if not dir_path.is_dir():
            continue
        for f in sorted(dir_path.glob("*.md")):
            if not _DOC_ID_FIELD.search(_read_header(f)):
                id_gaps.append(str(f.relative_to(project_path)))

    if id_gaps:
        for rel in id_gaps:
            findings["required_gaps"].append(
                f"`{rel}` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter."
            )
    else:
        positives.append("All standards/policy/processes files have Document ID fields.")

    # Check 7: CARRY_FORWARD.md staleness
    checks_run.append(
        f"CARRY_FORWARD.md open flags not stale (>{_CARRY_FORWARD_THRESHOLD_DAYS} days)"
    )
    cf_warnings = _check_carry_forward_staleness(project_path)
    if cf_warnings:
        findings["warnings"].extend(cf_warnings)
    else:
        positives.append("No stale carry-forward flags.")

    audits_dir = project_path / "docs" / "audits"
    doc_id = f"AUD-ENG-{_next_audit_sequence(audits_dir):03d}"

    return {
        "doc_id": doc_id,
        "timestamp": timestamp_str,
        "date_str": today.isoformat(),
        "project": project_path,
        "checks_run": checks_run,
        "findings": findings,
        "positives": positives,
    }


def render_report(result: dict) -> str:
    doc_id = result["doc_id"]
    timestamp = result["timestamp"]
    date_str = result["date_str"]
    project = result["project"]
    checks_run = result["checks_run"]
    findings = result["findings"]
    positives = result["positives"]

    blockers = findings["blockers"]
    required_gaps = findings["required_gaps"]
    warnings = findings["warnings"]
    total = len(blockers) + len(required_gaps) + len(warnings)

    if blockers or required_gaps:
        conclusion = "ATTENTION — required gaps or blockers need resolution before next release."
    else:
        conclusion = "PASS — no required gaps or blockers found."

    lines: list[str] = [
        f"# Governance Audit — {Path(project).name}",
        "",
        f"Document ID: {doc_id}",
        f"Date: {date_str}",
        f"Timestamp: {timestamp}",
        f"Scope: {project}",
        "Status: active",
        "Owner: Project Owner",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        (
            f"Automated governance audit of `{Path(project).name}`. "
            f"{len(positives)} positive finding(s). "
            f"{len(blockers)} blocker(s), {len(required_gaps)} required gap(s), {len(warnings)} warning(s)."
        ),
        "",
        f"**Conclusion:** {conclusion}",
        "",
        "---",
        "",
        "## Validation Run",
        "",
        "Checks performed:",
        "",
    ]
    for check in checks_run:
        lines.append(f"- {check}")
    lines += ["", "---", "", "## Positive Findings", ""]
    if positives:
        for p in positives:
            lines.append(f"- {p}")
    else:
        lines.append("- None.")

    lines += ["", "---", "", "## Findings", ""]

    if blockers:
        lines += ["### Blockers", ""]
        for b in blockers:
            lines.append(f"- [ ] {b}")
        lines.append("")

    if required_gaps:
        lines += ["### Required Gaps", ""]
        for g in required_gaps:
            lines.append(f"- [ ] {g}")
        lines.append("")

    if warnings:
        lines += ["### Warnings", ""]
        for w in warnings:
            lines.append(f"- [ ] {w}")
        lines.append("")

    if not blockers and not required_gaps and not warnings:
        lines += ["No findings. All checks passed.", ""]

    lines += [
        "---",
        "",
        "## Recommended Remediation Order",
        "",
        "1. Resolve all **Blockers** — these prevent release or introduce governance risk.",
        "2. Resolve all **Required Gaps** — missing metadata, orphaned docs, missing Document IDs.",
        "3. Address **Warnings** at your discretion — stale docs and open carry-forward flags.",
        "",
        "---",
        "",
        "## Audit Conclusion",
        "",
        f"{conclusion}",
        (
            f"Total findings: {total} "
            f"({len(blockers)} blocker, {len(required_gaps)} required gap, {len(warnings)} warning)."
        ),
        "",
        "_This report was generated automatically. Review each finding and tick the checkbox when resolved._",
        "",
    ]
    return "\n".join(lines)


def write_audit_report(project_path: Path, report_text: str, date_str: str) -> Path:
    audits_dir = project_path / "docs" / "audits"
    audits_dir.mkdir(parents=True, exist_ok=True)
    report_path = audits_dir / f"governance-audit-{date_str}.md"
    report_path.write_text(report_text, encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an AUD-class governance audit report."
    )
    parser.add_argument("project", help="Path to the governed project")
    parser.add_argument(
        "--open", action="store_true", help="Open the report in VS Code after writing"
    )
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        print(f"ERROR: Project path does not exist: {project}", file=sys.stderr)
        return 2

    result = run_audit(project)
    report_text = render_report(result)
    report_path = write_audit_report(project, report_text, result["date_str"])

    print(str(report_path))
    findings = result["findings"]
    total = (
        len(findings["blockers"])
        + len(findings["required_gaps"])
        + len(findings["warnings"])
    )
    print(
        f"Audit complete: {len(findings['blockers'])} blocker(s), "
        f"{len(findings['required_gaps'])} required gap(s), "
        f"{len(findings['warnings'])} warning(s). Total: {total}."
    )

    if args.open:
        subprocess.run(["code", str(report_path)], check=False)

    return 0 if not findings["blockers"] and not findings["required_gaps"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
