import contextlib
import io
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import project_naming


class SlugifyTests(unittest.TestCase):
    def test_basic_name(self):
        self.assertEqual("my-project", project_naming.slugify("My Project"))

    def test_underscores_and_slashes_become_hyphens(self):
        self.assertEqual("a-b-c", project_naming.slugify("a_b/c"))

    def test_special_chars_are_stripped(self):
        self.assertEqual("helloworld", project_naming.slugify("hello!!!world"))

    def test_hyphen_runs_collapse_and_trim(self):
        self.assertEqual("a-b", project_naming.slugify("--a---b--"))

    def test_empty_after_normalization(self):
        self.assertEqual("", project_naming.slugify("!!!"))
        self.assertEqual("", project_naming.slugify("   "))

    def test_path_traversal_input_is_neutralized(self):
        result = project_naming.slugify("../../etc")
        self.assertNotIn("/", result)
        self.assertNotIn("..", result)


class SlugValidationTests(unittest.TestCase):
    def test_valid_name_has_no_error(self):
        slug, error = project_naming.validate_project_name("My Awesome Project")
        self.assertEqual("my-awesome-project", slug)
        self.assertIsNone(error)

    def test_empty_slug_is_rejected(self):
        _, error = project_naming.validate_project_name("!!!")
        self.assertIsNotNone(error)
        self.assertIn("empty slug", error)

    def test_single_character_slug_is_rejected(self):
        _, error = project_naming.validate_project_name("a")
        self.assertIsNotNone(error)
        self.assertIn("single-character", error)

    def test_two_character_slug_is_accepted(self):
        slug, error = project_naming.validate_project_name("ab")
        self.assertEqual("ab", slug)
        self.assertIsNone(error)

    def test_reserved_names_are_rejected(self):
        for name in ["con", "CON", "Nul", "prn", "aux", "COM1", "com9", "lpt1", "LPT9"]:
            _, error = project_naming.validate_project_name(name)
            self.assertIsNotNone(error, f"{name!r} should be rejected")
            self.assertIn("reserved OS name", error)

    def test_reserved_list_contents(self):
        self.assertIn("con", project_naming.RESERVED_OS_NAMES)
        self.assertIn("nul", project_naming.RESERVED_OS_NAMES)
        for i in range(1, 10):
            self.assertIn(f"com{i}", project_naming.RESERVED_OS_NAMES)
            self.assertIn(f"lpt{i}", project_naming.RESERVED_OS_NAMES)

    def test_name_containing_reserved_word_is_allowed(self):
        slug, error = project_naming.validate_project_name("con-troller app")
        self.assertEqual("con-troller-app", slug)
        self.assertIsNone(error)


class GovernanceMappingTests(unittest.TestCase):
    def test_governance_to_risk_table(self):
        self.assertEqual(
            {"0": "low", "1": "low", "2": "medium", "3": "high", "4": "critical"},
            project_naming.GOVERNANCE_TO_RISK,
        )

    def test_risk_to_governance_table(self):
        self.assertEqual(
            {"low": "1", "medium": "2", "high": "3", "critical": "4"},
            project_naming.RISK_TO_GOVERNANCE,
        )

    def test_resolve_governance_from_level(self):
        self.assertEqual(("3", "high"), project_naming.resolve_governance("3"))

    def test_resolve_governance_from_legacy_tier(self):
        self.assertEqual(("2", "medium"), project_naming.resolve_governance("medium"))

    def test_resolve_governance_default_is_level_two(self):
        self.assertEqual(("2", "medium"), project_naming.resolve_governance(None))

    def test_resolve_governance_rejects_unknown(self):
        with self.assertRaises(ValueError):
            project_naming.resolve_governance("extreme")

    def test_build_type_map_defaults(self):
        self.assertEqual("application", project_naming.BUILD_TYPE_GOV_MAP["app"])
        self.assertEqual("agent", project_naming.BUILD_TYPE_GOV_MAP["agent"])
        self.assertEqual("internal-tool", project_naming.BUILD_TYPE_GOV_MAP["tool"])
        self.assertEqual("internal-tool", project_naming.BUILD_TYPE_GOV_MAP["other"])


class RenderInitialScopeTests(unittest.TestCase):
    def _render(self, **overrides) -> str:
        params = dict(
            project_name="Demo App",
            slug="demo-app",
            governance_type="application",
            governance_level="2",
            risk_tier="medium",
            stack="python",
            primary_builder="claude",
            target_dir="/tmp/demo-app",
            generated_at="2026-01-01T00:00:00-07:00",
        )
        params.update(overrides)
        return project_naming.render_initial_scope(**params)

    def test_classification_table_and_checklist(self):
        text = self._render()
        self.assertIn("# Initial Scope — Demo App", text)
        self.assertIn("| Slug / dir     | demo-app |", text)
        self.assertIn("| Risk tier      | medium |", text)
        self.assertIn("Generated: 2026-01-01T00:00:00-07:00", text)
        self.assertIn("## First session checklist", text)
        self.assertTrue(text.endswith("\n"))

    def test_scope_brief_when_captured(self):
        text = self._render(scope_problem="a problem", scope_user="a user", scope_mvp="an mvp")
        self.assertIn("**Problem:** a problem", text)
        self.assertIn("**User / consumer:** a user", text)
        self.assertIn("**MVP:** an mvp", text)

    def test_scope_brief_placeholder_when_missing(self):
        text = self._render()
        self.assertIn("Not captured at intake.", text)


class CliTests(unittest.TestCase):
    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = project_naming.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_slug_command_prints_slug(self):
        code, out, err = self._run(["slug", "My Project"])
        self.assertEqual(0, code)
        self.assertEqual("my-project", out.strip())

    def test_slug_command_rejects_reserved_name(self):
        code, out, err = self._run(["slug", "con"])
        self.assertEqual(1, code)
        self.assertEqual("", out)
        self.assertIn("reserved OS name", err)

    def test_slug_command_rejects_empty_slug(self):
        code, _, err = self._run(["slug", "!!!"])
        self.assertEqual(1, code)
        self.assertIn("empty slug", err)

    def test_risk_tier_command(self):
        code, out, _ = self._run(["risk-tier", "3"])
        self.assertEqual(0, code)
        self.assertEqual("high", out.strip())

    def test_risk_tier_command_rejects_unknown(self):
        code, _, err = self._run(["risk-tier", "extreme"])
        self.assertEqual(1, code)
        self.assertIn("Unsupported governance level", err)


if __name__ == "__main__":
    unittest.main()
