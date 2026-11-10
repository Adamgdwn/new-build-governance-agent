import os
import stat
import sys
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import master_env

POSIX_ONLY = unittest.skipIf(os.name == "nt", "POSIX file modes do not apply on Windows")

# Distinctive fake values. No command may print one, so every test checks its
# stdout and stderr for all of them. They stay clear of the secret scanner's
# patterns (tests/test_secret_hygiene.py).
FAKE_A = "fake_value_a"
FAKE_B = "fake_value_b"
FAKE_C = "fake_value_c"
FAKE_OLD = "fake_value_old"
FAKE_NEW = "fake_value_new"
FAKE_VALUES = (FAKE_A, FAKE_B, FAKE_C, FAKE_OLD, FAKE_NEW)


def setUpModule():
    # The parser's --master default is the real master env file. Point it at a
    # path that does not exist, so a test that forgets --master cannot reach it.
    tmp = tempfile.TemporaryDirectory()
    unittest.addModuleCleanup(tmp.cleanup)
    guard = mock.patch.object(master_env, "DEFAULT_MASTER", Path(tmp.name) / "not-the-master.env")
    guard.start()
    unittest.addModuleCleanup(guard.stop)


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


class MasterEnvCase(unittest.TestCase):
    """Each test gets its own temporary master env file and captures all output."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.master = self.root / ".env.master"

    def write_master(self, text):
        self.master.write_text(text, encoding="utf-8")

    def master_values(self):
        return master_env.parse_env_file(self.master)

    def run_cli(self, *argv):
        """Run one command against the temporary master: (exit code, stdout, stderr)."""
        args = master_env.build_parser().parse_args(["--master", str(self.master), *argv])
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = args.func(args)
        return code, out.getvalue(), err.getvalue()

    def assert_no_value_printed(self, out, err):
        for value in FAKE_VALUES:
            self.assertNotIn(value, out)
            self.assertNotIn(value, err)


class StatusTests(MasterEnvCase):
    def test_named_keys_report_set_or_missing(self):
        self.write_master(f"SET_KEY={FAKE_A}\nBLANK_KEY=\n")

        code, out, err = self.run_cli(
            "status", "--key", "SET_KEY", "--key", "BLANK_KEY", "--key", "ABSENT_KEY"
        )

        self.assertEqual(0, code)
        self.assertEqual("set\tSET_KEY\nmissing\tBLANK_KEY\nmissing\tABSENT_KEY\n", out)
        self.assertEqual("", err)
        self.assert_no_value_printed(out, err)

    def test_control_plane_reports_every_control_plane_key(self):
        # OPENAI_API_KEY is a priority key, not a control-plane one: it is not reported.
        self.write_master(f"VERCEL_TOKEN={FAKE_A}\nOPENAI_API_KEY={FAKE_B}\n")

        code, out, err = self.run_cli("status", "--control-plane")

        self.assertEqual(0, code)
        expected = [
            f"{'set' if key == 'VERCEL_TOKEN' else 'missing'}\t{key}"
            for key in master_env.CONTROL_PLANE_KEYS
        ]
        self.assertEqual(expected, out.splitlines())
        self.assert_no_value_printed(out, err)

    def test_default_reports_the_priority_keys(self):
        self.write_master(f"OPENAI_API_KEY={FAKE_A}\n")

        code, out, err = self.run_cli("status")

        self.assertEqual(0, code)
        expected = [
            f"{'set' if key == 'OPENAI_API_KEY' else 'missing'}\t{key}"
            for key in master_env.PRIORITY_KEYS
        ]
        self.assertEqual(expected, out.splitlines())
        self.assert_no_value_printed(out, err)


class MissingTests(MasterEnvCase):
    def setUp(self):
        super().setUp()
        self.write_master(
            f"VERCEL_TOKEN={FAKE_A}\n"  # both lists, set
            "SUPABASE_ORG_ID=\n"  # both lists, blank
            f"OPENAI_API_KEY={FAKE_B}\n"  # priority only, set
            "CLOUDFLARE_ZONE_ID=\n"  # control plane only, blank
            "LOCAL_ONLY_FLAG=\n"  # neither list, blank
        )

    def test_default_lists_the_blank_keys_in_the_file(self):
        code, out, err = self.run_cli("missing")

        self.assertEqual(0, code)
        self.assertEqual(
            ["SUPABASE_ORG_ID", "CLOUDFLARE_ZONE_ID", "LOCAL_ONLY_FLAG"], out.splitlines()
        )
        self.assert_no_value_printed(out, err)

    def test_priority_lists_unset_priority_keys_including_absent_ones(self):
        code, out, err = self.run_cli("missing", "--priority")

        self.assertEqual(0, code)
        expected = [
            key for key in master_env.PRIORITY_KEYS if key not in {"VERCEL_TOKEN", "OPENAI_API_KEY"}
        ]
        self.assertEqual(expected, out.splitlines())
        self.assert_no_value_printed(out, err)

    def test_control_plane_lists_unset_control_plane_keys_including_absent_ones(self):
        code, out, err = self.run_cli("missing", "--control-plane")

        self.assertEqual(0, code)
        expected = [key for key in master_env.CONTROL_PLANE_KEYS if key != "VERCEL_TOKEN"]
        self.assertEqual(expected, out.splitlines())
        self.assert_no_value_printed(out, err)


class SetTests(MasterEnvCase):
    def test_value_fills_a_blank_key_without_prompting(self):
        self.write_master(f"# shared services\nSHARED_KEY=\nOTHER_KEY={FAKE_B}\n")

        with (
            mock.patch.object(master_env.getpass, "getpass") as hidden,
            mock.patch("builtins.input") as visible,
        ):
            code, out, err = self.run_cli("set", "SHARED_KEY", "--value", FAKE_A)

        self.assertEqual(0, code)
        hidden.assert_not_called()
        visible.assert_not_called()
        self.assertEqual("filled\tSHARED_KEY\n", out)
        self.assertEqual("", err)
        self.assertEqual(
            f"# shared services\nSHARED_KEY={FAKE_A}\nOTHER_KEY={FAKE_B}\n",
            self.master.read_text(encoding="utf-8"),
        )
        self.assert_no_value_printed(out, err)

    @POSIX_ONLY
    def test_written_master_is_readable_by_its_owner_only(self):
        self.write_master("SHARED_KEY=\n")
        self.master.chmod(0o644)

        code, _, _ = self.run_cli("set", "SHARED_KEY", "--value", FAKE_A)

        self.assertEqual(0, code)
        self.assertEqual(0o600, stat.S_IMODE(self.master.stat().st_mode))

    def test_prompts_without_echo_by_default(self):
        self.write_master("SHARED_KEY=\n")

        with (
            mock.patch.object(
                master_env.getpass, "getpass", return_value=f"  {FAKE_A}  "
            ) as hidden,
            mock.patch("builtins.input") as visible,
        ):
            code, out, err = self.run_cli("set", "SHARED_KEY")

        self.assertEqual(0, code)
        hidden.assert_called_once_with("SHARED_KEY: ")
        visible.assert_not_called()
        self.assertEqual("filled\tSHARED_KEY\n", out)
        self.assertEqual(FAKE_A, self.master_values()["SHARED_KEY"])  # whitespace stripped
        self.assert_no_value_printed(out, err)

    def test_visible_prompts_through_input(self):
        self.write_master("SHARED_KEY=\n")

        with (
            mock.patch.object(master_env.getpass, "getpass") as hidden,
            mock.patch("builtins.input", return_value=FAKE_A) as visible,
        ):
            code, out, err = self.run_cli("set", "SHARED_KEY", "--visible")

        self.assertEqual(0, code)
        visible.assert_called_once_with("SHARED_KEY: ")
        hidden.assert_not_called()
        self.assertEqual("filled\tSHARED_KEY\n", out)
        self.assertEqual(FAKE_A, self.master_values()["SHARED_KEY"])
        self.assert_no_value_printed(out, err)

    def test_blank_answer_skips_that_key_only(self):
        self.write_master("FIRST_KEY=\nSECOND_KEY=\n")

        with mock.patch.object(
            master_env.getpass, "getpass", side_effect=["   ", FAKE_B]
        ) as hidden:
            code, out, err = self.run_cli("set", "FIRST_KEY", "SECOND_KEY")

        self.assertEqual(0, code)
        self.assertEqual(
            [mock.call("FIRST_KEY: "), mock.call("SECOND_KEY: ")], hidden.call_args_list
        )
        self.assertEqual("filled\tSECOND_KEY\n", out)
        self.assertEqual("Skipped FIRST_KEY: blank value\n", err)
        self.assertEqual({"FIRST_KEY": "", "SECOND_KEY": FAKE_B}, self.master_values())
        self.assert_no_value_printed(out, err)

    def test_existing_value_is_kept_without_overwrite(self):
        self.write_master(f"SHARED_KEY={FAKE_OLD}\n")

        code, out, err = self.run_cli("set", "SHARED_KEY", "--value", FAKE_NEW)

        self.assertEqual(0, code)
        self.assertEqual("skipped\tSHARED_KEY\n", out)
        self.assertEqual(f"SHARED_KEY={FAKE_OLD}\n", self.master.read_text(encoding="utf-8"))
        self.assert_no_value_printed(out, err)

    def test_overwrite_replaces_an_existing_value(self):
        self.write_master(f"SHARED_KEY={FAKE_OLD}\n")

        code, out, err = self.run_cli("set", "SHARED_KEY", "--value", FAKE_NEW, "--overwrite")

        self.assertEqual(0, code)
        self.assertEqual("updated\tSHARED_KEY\n", out)
        self.assertEqual(f"SHARED_KEY={FAKE_NEW}\n", self.master.read_text(encoding="utf-8"))
        self.assert_no_value_printed(out, err)

    def test_refuses_a_value_that_spans_lines(self):
        # The env file holds one line per key. Written across lines, a value is cut
        # short, and a continuation such as "QmFzZTY0ZmFrZTE=" reads back as a blank
        # key, which `missing` then prints: part of the value on stdout.
        fragment = "QmFzZTY0ZmFrZTE"
        self.write_master("SHARED_KEY=\n")
        before = self.master.read_bytes()
        values = {
            "newline": f"BEGIN fake\n{fragment}=\nEND fake",
            "carriage return": f"{FAKE_A}\r{fragment}=",
            "trailing newline": f"{FAKE_A}\n",
        }

        for name, value in values.items():
            with self.subTest(name):
                code, out, err = self.run_cli("set", "SHARED_KEY", "--value", value)

                self.assertEqual(2, code)
                self.assertEqual("", out)
                self.assertIn("Rejected SHARED_KEY", err)
                self.assertNotIn(fragment, out + err)
                self.assert_no_value_printed(out, err)
                self.assertEqual(before, self.master.read_bytes())

    def test_refuses_a_prompted_value_that_spans_lines_and_writes_nothing(self):
        fragment = "QmFzZTY0ZmFrZTE"
        self.write_master("FIRST_KEY=\nSECOND_KEY=\n")
        before = self.master.read_bytes()

        with mock.patch.object(
            master_env.getpass, "getpass", side_effect=[FAKE_A, f"{FAKE_B}\r{fragment}="]
        ):
            code, out, err = self.run_cli("set", "FIRST_KEY", "SECOND_KEY")

        self.assertEqual(2, code)
        self.assertEqual("", out)
        self.assertIn("Rejected SECOND_KEY", err)
        self.assertNotIn(fragment, out + err)
        self.assert_no_value_printed(out, err)
        self.assertEqual(before, self.master.read_bytes())


class MergeTests(MasterEnvCase):
    def setUp(self):
        super().setUp()
        self.source = self.root / "project.env"

    def test_key_merges_only_the_named_keys_that_have_a_value(self):
        self.write_master("FIRST_KEY=\nSECOND_KEY=\nBLANK_IN_SOURCE=\n")
        self.source.write_text(
            f"FIRST_KEY={FAKE_A}\nSECOND_KEY={FAKE_B}\nBLANK_IN_SOURCE=\nPROJECT_ONLY={FAKE_C}\n",
            encoding="utf-8",
        )

        code, out, err = self.run_cli(
            "merge",
            "--source",
            str(self.source),
            "--key",
            "FIRST_KEY",
            "--key",
            "BLANK_IN_SOURCE",
        )

        self.assertEqual(0, code)
        self.assertEqual(
            [
                f"source\t{self.source}",
                "candidate_keys\t1",
                "ignored_unregistered_keys\t0",
                "applied_keys\t1",
                "filled\tFIRST_KEY",
            ],
            out.splitlines(),
        )
        self.assertEqual("", err)
        self.assertEqual(
            {"FIRST_KEY": FAKE_A, "SECOND_KEY": "", "BLANK_IN_SOURCE": ""}, self.master_values()
        )
        self.assert_no_value_printed(out, err)

    def test_key_refuses_a_key_the_master_does_not_list(self):
        self.write_master("FIRST_KEY=\n")
        self.source.write_text(f"FIRST_KEY={FAKE_A}\nPROJECT_ONLY={FAKE_C}\n", encoding="utf-8")
        before = self.master.read_bytes()

        code, out, err = self.run_cli(
            "merge", "--source", str(self.source), "--key", "FIRST_KEY", "--key", "PROJECT_ONLY"
        )

        self.assertEqual(2, code)
        self.assertEqual("", out)
        self.assertIn("Rejected PROJECT_ONLY: it is not a reviewed shared-service key", err)
        self.assertNotIn("FIRST_KEY", err)
        self.assertEqual(before, self.master.read_bytes())
        self.assert_no_value_printed(out, err)


class MainTests(MasterEnvCase):
    def argv(self, *command):
        return ["master_env.py", "--master", str(self.master), *command]

    def test_refuses_value_with_more_than_one_key(self):
        self.write_master("FIRST_KEY=\nSECOND_KEY=\n")
        before = self.master.read_bytes()
        out, err = StringIO(), StringIO()

        argv = self.argv("set", "FIRST_KEY", "SECOND_KEY", "--value", FAKE_A)
        with mock.patch.object(sys, "argv", argv), redirect_stdout(out), redirect_stderr(err):
            with self.assertRaises(SystemExit) as raised:
                master_env.main()

        self.assertEqual(2, raised.exception.code)
        self.assertIn("set --value can only be used with one key", err.getvalue())
        self.assertEqual(before, self.master.read_bytes())
        self.assert_no_value_printed(out.getvalue(), err.getvalue())

    def test_runs_the_named_command(self):
        self.write_master(f"SHARED_KEY={FAKE_A}\n")
        out, err = StringIO(), StringIO()

        argv = self.argv("status", "--key", "SHARED_KEY")
        with mock.patch.object(sys, "argv", argv), redirect_stdout(out), redirect_stderr(err):
            code = master_env.main()

        self.assertEqual(0, code)
        self.assertEqual("set\tSHARED_KEY\n", out.getvalue())
        self.assert_no_value_printed(out.getvalue(), err.getvalue())


if __name__ == "__main__":
    unittest.main()
