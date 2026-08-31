import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import promotion_plan
import schema_validation


class SchemaValidationTests(unittest.TestCase):
    def test_project_control_schema_accepts_current_repo(self):
        errors = schema_validation.validate_project_control(REPO_ROOT / "project-control.yaml")
        self.assertEqual([], errors)

    def test_project_control_schema_rejects_invalid_governance_level(self):
        data = schema_validation.load_project_control(REPO_ROOT / "project-control.yaml")
        data["governance_level"] = 9

        errors = schema_validation.validate_project_control_data(data)

        self.assertIn("governance_level must be an integer from 0 through 4", errors)

    def test_project_control_schema_rejects_invalid_complexity_control(self):
        data = schema_validation.load_project_control(REPO_ROOT / "project-control.yaml")
        data["quality_controls"]["cyclomatic_complexity"]["mode"] = "magic-score"
        data["quality_controls"]["cyclomatic_complexity"]["refactor_or_exception_above"] = 5

        errors = schema_validation.validate_project_control_data(data)

        self.assertTrue(any("cyclomatic_complexity.mode" in error for error in errors))
        self.assertTrue(any("greater than or equal to review_above" in error for error in errors))

    def test_project_control_schema_rejects_invalid_alignment_cadence(self):
        data = schema_validation.load_project_control(REPO_ROOT / "project-control.yaml")
        data["governance_alignment"]["review_cadence_days"] = 0

        errors = schema_validation.validate_project_control_data(data)

        self.assertIn(
            "governance_alignment.review_cadence_days must be a positive integer",
            errors,
        )

    def test_promotion_plan_schema_accepts_generated_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            (project / "automation").mkdir(parents=True)
            (project / "tests").mkdir()
            (project / "README.md").write_text("# Project\n", encoding="utf-8")
            (project / "automation" / "tool.py").write_text("print('ok')\n", encoding="utf-8")
            (project / "tests" / "test_sample.py").write_text("import unittest\n", encoding="utf-8")

            plan = promotion_plan.build_plan(project)

            self.assertEqual([], schema_validation.validate_promotion_plan(plan))

    def test_promotion_plan_schema_requires_argv_for_automated_checks(self):
        plan = promotion_plan.build_plan(REPO_ROOT)
        pre_checks = next(
            stage for stage in plan["stages"] if stage["name"] == "pre_promotion_checks"
        )["checks"]
        pre_checks[0].pop("argv", None)

        errors = schema_validation.validate_promotion_plan(plan)

        self.assertTrue(any("argv must be a non-empty string list" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
