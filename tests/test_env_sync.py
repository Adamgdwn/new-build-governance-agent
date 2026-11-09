import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import env_file
import env_sync


class EnvSyncTests(unittest.TestCase):
    def test_parse_env_value_and_privileged_classification(self):
        self.assertEqual("hello world", env_sync.parse_env_value('"hello world"'))
        self.assertEqual("value", env_sync.parse_env_value("value # comment"))
        self.assertTrue(env_sync.is_privileged_key("SUPABASE_SERVICE_ROLE_KEY"))
        self.assertFalse(env_sync.is_privileged_key("NEXT_PUBLIC_SUPABASE_URL"))
        self.assertFalse(env_sync.is_privileged_key("STRIPE_PUBLISHABLE_KEY"))

    def test_build_sync_plan_redacts_values_and_counts_privileged_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            (project / ".env.example").write_text(
                "NEXT_PUBLIC_SUPABASE_URL=\nSUPABASE_SERVICE_ROLE_KEY=\nMISSING_KEY=\n",
                encoding="utf-8",
            )
            master = root / ".env.master"
            master.write_text(
                "NEXT_PUBLIC_SUPABASE_URL=https://example.supabase.co\n"
                "SUPABASE_SERVICE_ROLE_KEY=service-role-secret\n",
                encoding="utf-8",
            )

            plan = env_sync.build_sync_plan(project, master, ".env.local", False, [])
            entries = {entry["key"]: entry for entry in plan["entries"]}

            self.assertEqual("ready", entries["NEXT_PUBLIC_SUPABASE_URL"]["status"])
            self.assertFalse(entries["NEXT_PUBLIC_SUPABASE_URL"]["privileged"])
            self.assertEqual("ready", entries["SUPABASE_SERVICE_ROLE_KEY"]["status"])
            self.assertTrue(entries["SUPABASE_SERVICE_ROLE_KEY"]["privileged"])
            self.assertEqual("missing_from_master", entries["MISSING_KEY"]["status"])
            self.assertEqual(1, plan["summary"]["privileged_ready"])
            self.assertNotIn("service-role-secret", str(plan))


class EnvSyncPathContainmentTests(unittest.TestCase):
    def test_build_sync_plan_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            master = root / ".env.master"
            master.write_text("KEY=value\n", encoding="utf-8")
            with self.assertRaises(ValueError, msg="path traversal should raise ValueError"):
                env_sync.build_sync_plan(project, master, "../../etc/env", False, [])

    def test_build_sync_plan_rejects_absolute_outside_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            outside = root / "outside"
            outside.mkdir()
            master = root / ".env.master"
            master.write_text("KEY=value\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                env_sync.build_sync_plan(project, master, "../outside/.env", False, [])

    def test_apply_sync_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            master = root / ".env.master"
            master.write_text("KEY=value\n", encoding="utf-8")
            bad_plan = {
                "master_env": str(master),
                "target_env": str(root / "outside" / ".env.local"),
                "project_path": str(project),
                "entries": [],
            }
            with self.assertRaises(ValueError):
                env_sync.apply_sync(bad_plan, False, False)

    def test_build_sync_plan_allows_valid_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            master = root / ".env.master"
            master.write_text("KEY=value\n", encoding="utf-8")
            plan = env_sync.build_sync_plan(project, master, ".env.local", False, [])
            self.assertEqual(str(project.resolve()), plan["project_path"])


class EnvSyncApplyTests(unittest.TestCase):
    def make_plan(self, root: Path) -> tuple[Path, dict]:
        project = root / "project"
        project.mkdir()
        (project / ".env.example").write_text(
            "NEXT_PUBLIC_SUPABASE_URL=\nSUPABASE_SERVICE_ROLE_KEY=\n", encoding="utf-8"
        )
        master = root / ".env.master"
        master.write_text(
            "NEXT_PUBLIC_SUPABASE_URL=https://example.supabase.co\n"
            "SUPABASE_SERVICE_ROLE_KEY=service-role-secret\n",
            encoding="utf-8",
        )
        return project, env_sync.build_sync_plan(project, master, ".env.local", False, [])

    def test_apply_sync_writes_planned_values_and_skips_privileged_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            project, plan = self.make_plan(Path(tmp))

            result = env_sync.apply_sync(plan, include_privileged=False, overwrite=False)

            target = project / ".env.local"
            self.assertEqual(
                {"NEXT_PUBLIC_SUPABASE_URL": "https://example.supabase.co"},
                env_sync.parse_env_file(target),
            )
            self.assertEqual(["NEXT_PUBLIC_SUPABASE_URL"], result["applied_keys"])
            self.assertEqual(
                [
                    {
                        "key": "SUPABASE_SERVICE_ROLE_KEY",
                        "reason": "privileged_requires_include_privileged",
                    }
                ],
                result["skipped"],
            )

    @unittest.skipIf(os.name == "nt", "POSIX file modes do not apply on Windows")
    def test_apply_sync_target_is_owner_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            project, plan = self.make_plan(Path(tmp))

            env_sync.apply_sync(plan, include_privileged=False, overwrite=False)

            self.assertEqual(0o600, stat.S_IMODE((project / ".env.local").stat().st_mode))

    def test_apply_sync_writes_nothing_when_protection_fails(self):
        refused = env_file.SecretFileProtectionError("restriction refused")
        with tempfile.TemporaryDirectory() as tmp:
            project, plan = self.make_plan(Path(tmp))
            with mock.patch.object(env_file, "restrict_to_owner", side_effect=refused):
                with self.assertRaises(env_file.SecretFileProtectionError):
                    env_sync.apply_sync(plan, include_privileged=False, overwrite=False)

            self.assertFalse((project / ".env.local").exists())


if __name__ == "__main__":
    unittest.main()
