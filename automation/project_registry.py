#!/usr/bin/env python3
"""
Local project registry for New Build Governance Agent.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "new-build-governance-agent"
DB_PATH = DATA_DIR / "registry.sqlite3"


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            path TEXT NOT NULL UNIQUE,
            project_type TEXT NOT NULL,
            risk_tier TEXT NOT NULL,
            builder TEXT NOT NULL,
            stack TEXT NOT NULL,
            scope_json TEXT NOT NULL DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT NOT NULL,
            path TEXT NOT NULL,
            status TEXT NOT NULL,
            missing_files_json TEXT NOT NULL DEFAULT '[]',
            warnings_json TEXT NOT NULL DEFAULT '[]',
            audited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def register_project(args: argparse.Namespace) -> None:
    init_db()
    payload = {
        "problem": args.problem or "",
        "user_desc": args.user_desc or "",
        "mvp": args.mvp or "",
        "governance_level": args.governance_level or "",
    }
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO projects (project_name, slug, path, project_type, risk_tier, builder, stack, scope_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            project_name=excluded.project_name,
            path=excluded.path,
            project_type=excluded.project_type,
            risk_tier=excluded.risk_tier,
            builder=excluded.builder,
            stack=excluded.stack,
            scope_json=excluded.scope_json,
            updated_at=CURRENT_TIMESTAMP
        """,
        (
            args.project_name,
            args.slug,
            args.path,
            args.project_type,
            args.risk_tier,
            args.builder,
            args.stack,
            json.dumps(payload, sort_keys=True),
        ),
    )
    conn.commit()
    conn.close()


def record_audit(args: argparse.Namespace) -> None:
    init_db()
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO audits (slug, path, status, missing_files_json, warnings_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            args.slug,
            args.path,
            args.status,
            json.dumps(args.missing_files or []),
            json.dumps(args.warnings or []),
        ),
    )
    conn.commit()
    conn.close()


def list_projects(_: argparse.Namespace) -> None:
    init_db()
    conn = connect()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT p.*, a.status AS latest_audit_status, a.audited_at AS latest_audit_at
        FROM projects p
        LEFT JOIN audits a
          ON a.id = (
            SELECT id FROM audits
            WHERE slug = p.slug
            ORDER BY audited_at DESC, id DESC
            LIMIT 1
          )
        ORDER BY p.updated_at DESC, p.project_name ASC
        """
    ).fetchall()
    for row in rows:
        print(json.dumps(dict(row), sort_keys=True))
    conn.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage the New Build Governance Agent project registry."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    register = subparsers.add_parser("register", help="Register or update a project.")
    register.add_argument("--project-name", required=True)
    register.add_argument("--slug", required=True)
    register.add_argument("--path", required=True)
    register.add_argument("--project-type", required=True)
    register.add_argument("--risk-tier", required=True)
    register.add_argument("--governance-level")
    register.add_argument("--builder", required=True)
    register.add_argument("--stack", required=True)
    register.add_argument("--problem")
    register.add_argument("--user-desc")
    register.add_argument("--mvp")
    register.set_defaults(func=register_project)

    audit = subparsers.add_parser("record-audit", help="Record an audit result.")
    audit.add_argument("--slug", required=True)
    audit.add_argument("--path", required=True)
    audit.add_argument("--status", required=True)
    audit.add_argument("--missing-files", nargs="*", default=[])
    audit.add_argument("--warnings", nargs="*", default=[])
    audit.set_defaults(func=record_audit)

    listed = subparsers.add_parser("list", help="List known projects.")
    listed.set_defaults(func=list_projects)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
