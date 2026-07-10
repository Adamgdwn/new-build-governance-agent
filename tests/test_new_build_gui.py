import os
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import new_build_gui


class _FakeVar:
    def __init__(self, value: str):
        self._value = value

    def get(self) -> str:
        return self._value


class NewBuildGuiTests(unittest.TestCase):
    def test_window_fonts_are_scaled_for_readability(self):
        self.assertEqual(new_build_gui.FONT_SCALE, 2)
        self.assertEqual(new_build_gui.FONT, ("Sans", 20))
        self.assertEqual(new_build_gui.SMALL, ("Sans", 18))
        self.assertEqual(new_build_gui.TITLE, ("Sans", 36, "bold"))
        self.assertEqual(new_build_gui.MONO, ("Monospace", 18))

    def test_activity_log_is_compact_by_default(self):
        self.assertTrue(new_build_gui.ACTIVITY_LOG_COLLAPSED_BY_DEFAULT)
        self.assertEqual(new_build_gui.ACTIVITY_LOG_EXPANDED_HEIGHT, 6)

    def test_update_affordance_allows_only_fast_forward(self):
        summary, allowed = new_build_gui.build_update_affordance_summary("behind", "would_update")

        self.assertTrue(allowed)
        self.assertIn("Safe fast-forward update is available.", summary)

    def test_update_affordance_blocks_refused_state(self):
        summary, allowed = new_build_gui.build_update_affordance_summary("behind", "refused")

        self.assertFalse(allowed)
        self.assertIn("blocked", summary)

    def test_update_affordance_blocks_up_to_date_state(self):
        summary, allowed = new_build_gui.build_update_affordance_summary("current", "up_to_date")

        self.assertFalse(allowed)
        self.assertIn("already up to date", summary)


class ProjectNameValidationTests(unittest.TestCase):
    def test_reserved_names_produce_an_error(self):
        for name in ["con", "CON", "nul", "COM1", "lpt9"]:
            self.assertIsNotNone(
                new_build_gui.project_name_error(name),
                f"{name!r} should be rejected as a reserved OS name",
            )

    def test_single_character_names_produce_an_error(self):
        self.assertIsNotNone(new_build_gui.project_name_error("a"))
        self.assertIsNotNone(new_build_gui.project_name_error("!!!"))

    def test_ordinary_names_are_accepted(self):
        self.assertIsNone(new_build_gui.project_name_error("My Cool App"))

    def test_gui_slugify_is_the_shared_implementation(self):
        import project_naming

        self.assertIs(new_build_gui.slugify, project_naming.slugify)

    def test_on_create_rejects_reserved_name_before_creating(self):
        errors: list[tuple[str, str]] = []
        fake_messagebox = types.SimpleNamespace(
            showerror=lambda title, message: errors.append((title, message)),
        )
        dummy = types.SimpleNamespace(v_name=_FakeVar("con"), v_mvp=_FakeVar("something useful"))

        original_messagebox = new_build_gui.messagebox
        new_build_gui.messagebox = fake_messagebox
        try:
            new_build_gui.App._on_create(dummy)
        finally:
            new_build_gui.messagebox = original_messagebox

        self.assertEqual(1, len(errors), "reserved name should be rejected with one error dialog")
        title, message = errors[0]
        self.assertEqual("Invalid project name", title)
        self.assertIn("reserved OS name", message)


class SubprocessEnvTests(unittest.TestCase):
    def test_path_uses_native_separator_and_keeps_existing_entries(self):
        env = new_build_gui.build_subprocess_env()
        entries = env["PATH"].split(os.pathsep)
        for item in os.environ.get("PATH", "").split(os.pathsep):
            if item:
                self.assertIn(item, entries)

    def test_posix_directories_only_prepended_off_windows(self):
        env = new_build_gui.build_subprocess_env()
        entries = env["PATH"].split(os.pathsep)
        if os.name == "nt":
            self.assertNotIn("/usr/bin", entries)
        else:
            self.assertIn("/usr/bin", entries)

    def test_governance_home_is_set(self):
        env = new_build_gui.build_subprocess_env()
        self.assertTrue(env.get("GOVERNANCE_HOME"))


if __name__ == "__main__":
    unittest.main()
