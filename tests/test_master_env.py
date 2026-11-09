import sys
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import master_env


class MasterEnvRegistryTests(unittest.TestCase):
    def test_registered_master_keys_returns_existing_keys_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            master = Path(tmp) / ".env.master"
            master.write_text("OPENAI_API_KEY=set\nSHARED_FLAG=true\n", encoding="utf-8")

            self.assertEqual(
                {"OPENAI_API_KEY", "SHARED_FLAG"},
                master_env.registered_master_keys(master),
            )

    def test_merge_ignores_unregistered_source_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            master = root / ".env.master"
            source = root / "project.env"
            master.write_text("SHARED_FLAG=\n", encoding="utf-8")
            source.write_text("SHARED_FLAG=enabled\nPROJECT_ONLY=secret\n", encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                result = master_env.cmd_merge(
                    Namespace(master=str(master), source=str(source), key=None, overwrite=False)
                )

            self.assertEqual(0, result)
            self.assertEqual("enabled", master_env.parse_env_file(master)["SHARED_FLAG"])
            self.assertIn("ignored_unregistered_keys\t1", output.getvalue())
            self.assertNotIn("PROJECT_ONLY", master_env.parse_env_file(master))

    def test_set_rejects_unregistered_key_before_prompting(self):
        with tempfile.TemporaryDirectory() as tmp:
            master = Path(tmp) / ".env.master"
            master.write_text("SHARED_FLAG=enabled\n", encoding="utf-8")
            errors = StringIO()

            with redirect_stderr(errors):
                result = master_env.cmd_set(
                    Namespace(
                        master=str(master),
                        key=["PROJECT_ONLY"],
                        value=None,
                        visible=False,
                        overwrite=False,
                    )
                )

            self.assertEqual(2, result)
            self.assertIn("not a reviewed shared-service key", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
