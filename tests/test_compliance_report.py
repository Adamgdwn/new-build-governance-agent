import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import compliance_report
import promotion_checks
import scaffold_project


class ComplianceReportTests(unittest.TestCase):
    def test_missing_required_file_is_required_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-app"
            scaffold_project.scaffold_project(target, "application", "2")
            (target / "README.md").unlink()

            report = compliance_report.build_compliance_report(target)

            self.assertEqual("failed", report["overall_status"])
            self.assertTrue(
                any(
                    "README.md" == finding["path"]
                    for finding in report["findings"]["required_gaps"]
                )
            )

    def test_advisory_findings_do_not_block_low_risk_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-app"
            scaffold_project.scaffold_project(target, "application", "1")
            (target / "docs" / "domain-language.md").unlink()

            report = compliance_report.build_compliance_report(target)

            self.assertEqual("passed", report["overall_status"])
            self.assertFalse(report["findings"]["required_gaps"])
            self.assertTrue(
                any(
                    "docs/domain-language.md" == finding["path"]
                    for finding in report["findings"]["recommended_improvements"]
                )
            )

    def test_riskier_use_case_creates_owner_decision_not_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-agent"
            scaffold_project.scaffold_project(target, "agent", "1")

            report = compliance_report.build_compliance_report(target)
            control = (target / "project-control.yaml").read_text(encoding="utf-8")

            self.assertEqual("passed", report["overall_status"])
            self.assertIn("governance_level: 1", control)
            self.assertTrue(report["findings"]["owner_decisions_needed"])
            self.assertTrue(
                any(
                    "Governance mismatch warning" in finding["message"]
                    for finding in report["findings"]["owner_decisions_needed"]
                )
            )

    def test_promotion_checks_classify_failed_and_manual_results(self):
        self.assertEqual(
            "required_gaps",
            promotion_checks.categorize_check_result({"status": "failed"}),
        )
        self.assertEqual(
            "owner_decisions_needed",
            promotion_checks.categorize_check_result({"status": "manual_required"}),
        )
        self.assertEqual(
            "passed_checks",
            promotion_checks.categorize_check_result({"status": "passed"}),
        )


if __name__ == "__main__":
    unittest.main()
