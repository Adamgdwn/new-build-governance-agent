import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import governance_audit


class CarryForwardStalenessTests(unittest.TestCase):
    def _warnings_for(self, table: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "CARRY_FORWARD.md").write_text(table, encoding="utf-8")
            return governance_audit._check_carry_forward_staleness(project)

    def test_recent_review_keeps_open_flag_current(self):
        added = date.today() - timedelta(days=60)
        reviewed = date.today()
        warnings = self._warnings_for(
            "| Flag | Added | Last Reviewed | Owner | Status | Notes |\n"
            "|---|---|---|---|---|---|\n"
            f"| Long-running decision | {added} | {reviewed} | Owner | open | Still relevant. |\n"
        )

        self.assertEqual([], warnings)

    def test_stale_review_warns_for_six_column_format(self):
        added = date.today() - timedelta(days=60)
        reviewed = date.today() - timedelta(days=8)
        warnings = self._warnings_for(
            "| Flag | Added | Last Reviewed | Owner | Status | Notes |\n"
            "|---|---|---|---|---|---|\n"
            f"| Long-running decision | {added} | {reviewed} | Owner | open | Still relevant. |\n"
        )

        self.assertEqual(1, len(warnings))
        self.assertIn("not reviewed for 8 days", warnings[0])
        self.assertIn("last reviewed", warnings[0])

    def test_legacy_five_column_format_uses_added_date(self):
        added = date.today() - timedelta(days=8)
        warnings = self._warnings_for(
            "| Flag | Added | Owner | Status | Notes |\n"
            "|---|---|---|---|---|\n"
            f"| Legacy decision | {added} | Owner | open | Still relevant. |\n"
        )

        self.assertEqual(1, len(warnings))
        self.assertIn("not reviewed for 8 days", warnings[0])
        self.assertIn("added", warnings[0])


class AuditDocumentIdTests(unittest.TestCase):
    def test_same_day_rerun_reuses_existing_document_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            audits = project / "docs" / "audits"
            audits.mkdir(parents=True)
            report = audits / f"governance-audit-{date.today().isoformat()}.md"
            report.write_text(
                "# Governance Audit\n\nDocument ID: AUD-ENG-010\n",
                encoding="utf-8",
            )

            result = governance_audit.run_audit(project)

            self.assertEqual("AUD-ENG-010", result["doc_id"])

    def test_new_day_uses_next_available_document_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            audits = project / "docs" / "audits"
            audits.mkdir(parents=True)
            (audits / "older-audit.md").write_text(
                "# Governance Audit\n\nDocument ID: AUD-ENG-004\n",
                encoding="utf-8",
            )

            result = governance_audit.run_audit(project)

            self.assertEqual("AUD-ENG-005", result["doc_id"])


if __name__ == "__main__":
    unittest.main()
