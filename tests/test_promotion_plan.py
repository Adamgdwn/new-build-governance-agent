import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import promotion_plan


class PromotionPlanTests(unittest.TestCase):
    def test_local_checks_detect_python_shell_and_unittest(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            (project / "automation").mkdir(parents=True)
            (project / "scripts").mkdir()
            (project / "tests").mkdir()
            (project / "automation" / "tool.py").write_text("print('ok')\n", encoding="utf-8")
            (project / "scripts" / "governance-preflight.sh").write_text(
                "#!/usr/bin/env bash\ntrue\n", encoding="utf-8"
            )
            (project / "tests" / "test_sample.py").write_text("import unittest\n", encoding="utf-8")

            checks = promotion_plan.build_local_checks(project)
            names = {check["name"] for check in checks["pre"]}

            self.assertIn("governance_preflight", names)
            self.assertIn("python_compile", names)
            self.assertIn("shell_syntax", names)
            self.assertIn("python_unittest", names)
            self.assertNotIn("manual_smoke_review", names)
            self.assertTrue(all("argv" in check for check in checks["pre"]))


class PromotionPlanShellInjectionTests(unittest.TestCase):
    def test_shell_syntax_checks_use_per_file_argv(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            (project / "automation").mkdir(parents=True)
            (project / "scripts").mkdir()
            safe_script = project / "scripts" / "run.sh"
            safe_script.write_text("#!/usr/bin/env bash\ntrue\n", encoding="utf-8")
            spaced_script = project / "scripts" / "my script.sh"
            spaced_script.write_text("#!/usr/bin/env bash\ntrue\n", encoding="utf-8")

            checks = promotion_plan.build_local_checks(project)
            syntax_checks = [c for c in checks["pre"] if c["name"] == "shell_syntax"]

            self.assertGreater(len(syntax_checks), 0)
            for c in syntax_checks:
                argv = c["argv"]
                self.assertEqual("bash", argv[0])
                self.assertEqual("-n", argv[1])
                self.assertNotIn("-c", argv, "shell=True style '-c' must not be used")
                shell_file = argv[2]
                self.assertIsInstance(shell_file, str)
                self.assertNotIn(
                    ";", shell_file, "shell metacharacters must not appear in argv elements"
                )

    def test_shell_syntax_check_filename_with_spaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            (project / "scripts").mkdir(parents=True)
            spaced = project / "scripts" / "my special script.sh"
            spaced.write_text("#!/usr/bin/env bash\ntrue\n", encoding="utf-8")

            checks = promotion_plan.build_local_checks(project)
            syntax_checks = [c for c in checks["pre"] if c["name"] == "shell_syntax"]
            argvs = [c["argv"] for c in syntax_checks]
            file_args = [av[2] for av in argvs]
            self.assertTrue(
                any("my special script.sh" in f for f in file_args),
                "filename with spaces must appear as a single argv element",
            )


if __name__ == "__main__":
    unittest.main()
