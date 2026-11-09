import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import new_build_headless


class SlugifyTests(unittest.TestCase):
    def test_slugify_normal(self):
        self.assertEqual("my-project", new_build_headless.slugify("My Project"))

    def test_slugify_strips_special_chars(self):
        # special chars are dropped, not replaced with separators
        self.assertEqual("helloworld", new_build_headless.slugify("hello!!!world"))

    def test_slugify_empty_after_strip(self):
        self.assertEqual("", new_build_headless.slugify("!!!"))

    def test_slugify_path_traversal_input(self):
        # Path separators become dashes then are stripped — must not produce a traversal string
        result = new_build_headless.slugify("../../etc")
        self.assertNotIn("..", result)
        self.assertNotIn("/", result)

    def test_slugify_very_long_name(self):
        result = new_build_headless.slugify("a" * 256)
        self.assertNotIn("/", result)
        self.assertGreater(len(result), 0)


class FailOutputSchemaTests(unittest.TestCase):
    def test_fail_output_matches_freedom_tool_schema(self):
        """fail() must emit the four required fields from freedom.tool.yaml."""
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                new_build_headless.fail("test error")
        except SystemExit:
            pass
        output = buf.getvalue().strip()
        data = json.loads(output)
        self.assertEqual("failed", data["status"])
        self.assertIn("project_path", data)
        self.assertIn("slug", data)
        self.assertIn("files_created", data)
        self.assertIsInstance(data["files_created"], list)
        self.assertIn("error", data)
        self.assertNotIn("ok", data, "old 'ok' key must not appear in output")

    def test_fail_output_no_ok_key(self):
        """Ensure the old ok:false schema is gone."""
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                new_build_headless.fail("another error")
        except SystemExit:
            pass
        data = json.loads(buf.getvalue().strip())
        self.assertNotIn("ok", data)


class TargetRootTests(unittest.TestCase):
    def test_agent_projects_route_to_agents_category(self):
        self.assertEqual(
            new_build_headless.AGENTS_ROOT, new_build_headless.resolve_target_root("agent", "agent")
        )

    def test_application_projects_route_to_applications_category(self):
        self.assertEqual(
            new_build_headless.APPS_ROOT,
            new_build_headless.resolve_target_root("app", "application"),
        )

    def test_harness_projects_route_to_agents_category(self):
        # The GUI puts harnesses with agents; headless must agree.
        self.assertEqual(
            new_build_headless.AGENTS_ROOT,
            new_build_headless.resolve_target_root("other", "agentic-harness"),
        )


class PlanModeTests(unittest.TestCase):
    """--plan is what the terminal launchers preview with; it must never write."""

    def _plan(self, code_root: str, params: dict) -> tuple[int, dict]:
        env = {**os.environ, "NEW_BUILD_CODE_ROOT": code_root}
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / "automation" / "new_build_headless.py"), "--plan"],
            input=json.dumps(params),
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
            check=False,
        )
        return completed.returncode, json.loads(completed.stdout.strip().splitlines()[-1])

    def test_plan_reports_target_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, plan = self._plan(tmp, {"project_name": "Plan Probe", "build_type": "app"})

            self.assertEqual(0, code)
            self.assertEqual("planned", plan["status"])
            self.assertEqual(str(Path(tmp) / "Applications" / "plan-probe"), plan["project_path"])
            self.assertFalse(plan["already_exists"])
            self.assertEqual([], list(Path(tmp).iterdir()), "--plan must not create anything")

    def test_plan_routes_harness_to_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, plan = self._plan(
                tmp,
                {
                    "project_name": "Harness Probe",
                    "build_type": "other",
                    "governance_type": "agentic-harness",
                },
            )

            self.assertEqual(0, code)
            self.assertEqual(str(Path(tmp) / "agents" / "harness-probe"), plan["project_path"])

    def test_plan_reports_undecided_topology_for_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, plan = self._plan(tmp, {"project_name": "Agent Probe", "build_type": "agent"})

            self.assertEqual(0, code)
            self.assertEqual("agent", plan["governance_type"])
            self.assertEqual("undecided", plan["harness_topology"])

    def test_plan_rejects_unknown_topology(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, plan = self._plan(
                tmp,
                {"project_name": "Agent Probe", "build_type": "agent", "harness_topology": "swarm"},
            )

            self.assertEqual(1, code)
            self.assertIn("harness_topology", plan["error"])

    def test_plan_reports_validation_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, plan = self._plan(tmp, {"project_name": "!!!", "build_type": "app"})

            self.assertEqual(1, code)
            self.assertEqual("failed", plan["status"])
            self.assertEqual([], list(Path(tmp).iterdir()))


class SlugValidationTests(unittest.TestCase):
    def _call_fail_guard(self, slug, project_name):
        """Simulate the post-slugify guard by running the validation inline."""
        errors = []
        if not slug:
            errors.append("empty slug")
        elif len(slug) < 2:
            errors.append("single char slug")
        elif "/" in slug or "\\" in slug:
            errors.append("path separator in slug")
        elif slug.lower() in new_build_headless.RESERVED_OS_NAMES:
            errors.append("reserved name")
        return errors

    def test_empty_slug_detected(self):
        slug = new_build_headless.slugify("!!!")
        self.assertTrue(self._call_fail_guard(slug, "!!!"))

    def test_single_char_slug_detected(self):
        slug = new_build_headless.slugify("a")
        self.assertTrue(self._call_fail_guard(slug, "a"))

    def test_reserved_name_detected(self):
        self.assertIn("nul", new_build_headless.RESERVED_OS_NAMES)
        self.assertIn("con", new_build_headless.RESERVED_OS_NAMES)
        self.assertTrue(self._call_fail_guard("nul", "nul"))

    def test_normal_slug_passes(self):
        slug = new_build_headless.slugify("My Awesome Project")
        self.assertFalse(self._call_fail_guard(slug, "My Awesome Project"))

    def test_space_only_name_produces_empty_slug(self):
        slug = new_build_headless.slugify("   ")
        self.assertEqual("", slug)
        self.assertTrue(self._call_fail_guard(slug, "   "))


if __name__ == "__main__":
    unittest.main()
