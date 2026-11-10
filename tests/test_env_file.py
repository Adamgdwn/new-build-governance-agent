import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import env_file

POSIX_ONLY = unittest.skipIf(os.name == "nt", "POSIX file modes do not apply on Windows")
WINDOWS_ONLY = unittest.skipUnless(os.name == "nt", "needs real Windows access-control lists")
FAKE_SID = "S-1-5-21-1111-2222-3333-1001"


class ParseEnvValueTests(unittest.TestCase):
    def test_plain_value(self):
        self.assertEqual("value", env_file.parse_env_value("value"))

    def test_blank_value(self):
        self.assertEqual("", env_file.parse_env_value(""))
        self.assertEqual("", env_file.parse_env_value("   "))

    def test_double_quoted_value_with_spaces(self):
        self.assertEqual("hello world", env_file.parse_env_value('"hello world"'))

    def test_single_quoted_value(self):
        self.assertEqual("hello world", env_file.parse_env_value("'hello world'"))

    def test_unquoted_value_strips_trailing_comment(self):
        self.assertEqual("value", env_file.parse_env_value("value # comment"))

    def test_hash_inside_quoted_value_is_preserved(self):
        self.assertEqual("val#ue", env_file.parse_env_value('"val#ue"'))

    def test_unbalanced_quote_falls_back_to_stripping_quotes(self):
        self.assertEqual("oops", env_file.parse_env_value('"oops'))


class ParseEnvFileTests(unittest.TestCase):
    def _parse(self, content: str) -> dict[str, str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text(content, encoding="utf-8")
            return env_file.parse_env_file(path)

    def test_missing_file_returns_empty_dict(self):
        self.assertEqual({}, env_file.parse_env_file(Path("does-not-exist-anywhere.env")))

    def test_skips_comments_and_blank_lines(self):
        values = self._parse("# comment\n\nKEY=value\n   \n# other\n")
        self.assertEqual({"KEY": "value"}, values)

    def test_export_prefix_is_stripped(self):
        values = self._parse("export KEY=value\n")
        self.assertEqual({"KEY": "value"}, values)

    def test_value_containing_equals_is_kept_whole(self):
        values = self._parse("DATABASE_URL=postgres://u:p@host/db?sslmode=require\n")
        self.assertEqual("postgres://u:p@host/db?sslmode=require", values["DATABASE_URL"])

    def test_invalid_keys_are_skipped(self):
        values = self._parse("9BAD=value\nGOOD_KEY=ok\nBAD-KEY=nope\n")
        self.assertEqual({"GOOD_KEY": "ok"}, values)

    def test_line_without_equals_is_skipped(self):
        values = self._parse("JUSTTEXT\nKEY=value\n")
        self.assertEqual({"KEY": "value"}, values)


class FormatEnvValueTests(unittest.TestCase):
    def test_empty_value(self):
        self.assertEqual("", env_file.format_env_value(""))

    def test_simple_value_unquoted(self):
        self.assertEqual("abc123", env_file.format_env_value("abc123"))

    def test_value_with_space_is_quoted(self):
        self.assertEqual('"hello world"', env_file.format_env_value("hello world"))

    def test_value_with_hash_is_quoted(self):
        self.assertEqual('"val#ue"', env_file.format_env_value("val#ue"))

    def test_embedded_double_quotes_are_escaped(self):
        self.assertEqual('"say \\"hi\\" now"', env_file.format_env_value('say "hi" now'))

    def test_round_trip_through_parse(self):
        for original in ["plain", "hello world", "val#ue", "a=b=c", "postgres://u:p@h/db"]:
            formatted = env_file.format_env_value(original)
            self.assertEqual(original, env_file.parse_env_value(formatted))


class UpdateEnvValuesTests(unittest.TestCase):
    def test_fills_blank_and_appends_missing_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text("# header\nEMPTY_KEY=\nSET_KEY=existing\n", encoding="utf-8")

            applied = env_file.update_env_values(
                path,
                {"EMPTY_KEY": "filled-in", "SET_KEY": "changed", "NEW_KEY": "added"},
                overwrite=False,
                section_comment="# ===== test section =====",
            )

            self.assertEqual({"EMPTY_KEY": "filled", "NEW_KEY": "added"}, applied)
            values = env_file.parse_env_file(path)
            self.assertEqual("filled-in", values["EMPTY_KEY"])
            self.assertEqual("existing", values["SET_KEY"])
            self.assertEqual("added", values["NEW_KEY"])
            text = path.read_text(encoding="utf-8")
            self.assertIn("# header", text)
            self.assertIn("# ===== test section =====", text)

    def test_overwrite_replaces_existing_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text("SET_KEY=existing\n", encoding="utf-8")

            applied = env_file.update_env_values(path, {"SET_KEY": "changed"}, overwrite=True)

            self.assertEqual({"SET_KEY": "updated"}, applied)
            self.assertEqual("changed", env_file.parse_env_file(path)["SET_KEY"])

    def test_missing_file_gets_header_and_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sub" / ".env"
            header = ["# generated header", ""]

            applied = env_file.update_env_values(
                path,
                {"KEY": "value with spaces"},
                overwrite=False,
                missing_file_header=header,
            )

            self.assertEqual({"KEY": "added"}, applied)
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# generated header"))
            self.assertTrue(text.endswith("\n"))
            self.assertEqual("value with spaces", env_file.parse_env_file(path)["KEY"])

    def test_round_trip_preserves_comment_and_unrelated_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            original = "# keep me\nexport EXPORTED=kept\nUNTOUCHED=stays\n"
            path.write_text(original, encoding="utf-8")

            env_file.update_env_values(path, {"OTHER": "x"}, overwrite=False)

            text = path.read_text(encoding="utf-8")
            self.assertIn("# keep me", text)
            self.assertIn("export EXPORTED=kept", text)
            self.assertIn("UNTOUCHED=stays", text)

    def test_writes_through_the_protected_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            with mock.patch.object(env_file, "restrict_to_owner") as restrict:
                env_file.update_env_values(path, {"KEY": "placeholder"}, overwrite=False)
            restrict.assert_called_once_with(path)


class WritePrivateTextTests(unittest.TestCase):
    def test_restricts_before_any_content_is_written(self):
        seen: list[str] = []
        with tempfile.TemporaryDirectory() as tmp:
            new = Path(tmp) / "sub" / ".env"
            existing = Path(tmp) / ".env.master"
            existing.write_text("OLD=kept-until-protected\n", encoding="utf-8")
            with mock.patch.object(
                env_file,
                "restrict_to_owner",
                side_effect=lambda path: seen.append(path.read_text(encoding="utf-8")),
            ):
                env_file.write_private_text(new, "KEY=placeholder\n")
                env_file.write_private_text(existing, "KEY=placeholder\n")

            self.assertEqual(["", "OLD=kept-until-protected\n"], seen)
            self.assertEqual("KEY=placeholder\n", new.read_text(encoding="utf-8"))
            self.assertEqual("KEY=placeholder\n", existing.read_text(encoding="utf-8"))

    def test_failed_restriction_writes_nothing(self):
        refused = env_file.SecretFileProtectionError("restriction refused")
        with tempfile.TemporaryDirectory() as tmp:
            new = Path(tmp) / ".env"
            existing = Path(tmp) / ".env.master"
            existing.write_text("OLD=unchanged\n", encoding="utf-8")
            with mock.patch.object(env_file, "restrict_to_owner", side_effect=refused):
                for path in (new, existing):
                    with self.assertRaises(env_file.SecretFileProtectionError):
                        env_file.write_private_text(path, "KEY=placeholder\n")

            self.assertFalse(new.exists())
            self.assertEqual("OLD=unchanged\n", existing.read_text(encoding="utf-8"))

    def test_directory_target_is_refused_before_any_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / ".env"
            target.mkdir()
            with mock.patch.object(env_file, "restrict_to_owner") as restrict:
                with self.assertRaises(IsADirectoryError):
                    env_file.write_private_text(target, "KEY=placeholder\n")
            restrict.assert_not_called()


@POSIX_ONLY
class PosixOwnerOnlyTests(unittest.TestCase):
    def test_new_file_is_never_wider_than_owner_only(self):
        modes: list[int] = []
        old_umask = os.umask(0)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / ".env"
                with mock.patch.object(
                    env_file,
                    "restrict_to_owner",
                    side_effect=lambda p: modes.append(stat.S_IMODE(p.stat().st_mode)),
                ):
                    env_file.write_private_text(path, "KEY=placeholder\n")
                path.unlink()
                env_file.write_private_text(path, "KEY=placeholder\n")
                final_mode = stat.S_IMODE(path.stat().st_mode)
        finally:
            os.umask(old_umask)

        # Created owner-only before the chmod runs, and owner-only afterwards.
        self.assertEqual([0o600], modes)
        self.assertEqual(0o600, final_mode)

    def test_existing_readable_file_becomes_owner_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text("OLD=1\n", encoding="utf-8")
            path.chmod(0o644)

            env_file.write_private_text(path, "KEY=placeholder\n")

            self.assertEqual(0o600, stat.S_IMODE(path.stat().st_mode))
            self.assertEqual("KEY=placeholder\n", path.read_text(encoding="utf-8"))

    def test_chmod_failure_raises_protection_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text("OLD=1\n", encoding="utf-8")
            with mock.patch.object(env_file.os, "chmod", side_effect=PermissionError("not owner")):
                with self.assertRaises(env_file.SecretFileProtectionError) as caught:
                    env_file.restrict_to_owner(path)

        message = str(caught.exception)
        self.assertIn(str(path), message)
        self.assertIn("chmod 0600 failed", message)
        self.assertNotIn("icacls", message)


class FakeSecurityApi:
    """Stands in for the Windows security calls and records what they receive."""

    DESCRIPTOR = 0x1000
    DACL = 0x1010

    def __init__(self):
        self.calls = []
        self.builds = True
        self.dacl = self.DACL
        self.set_result = 0

    def api(self):
        return env_file._SecurityApi(
            self.string_to_descriptor,
            self.get_dacl,
            self.set_named_security_info,
            self.local_free,
            lambda: 87,
            lambda code: f"Windows message {code}.\r\n",
        )

    def string_to_descriptor(self, sddl, revision, descriptor, size):
        self.calls.append(("build", sddl, revision, size))
        if self.builds:
            descriptor.contents.value = self.DESCRIPTOR
        return int(self.builds)

    def get_dacl(self, descriptor, present, dacl, defaulted):
        self.calls.append(("get_dacl", descriptor.value))
        present.contents.value = 1
        dacl.contents.value = self.dacl
        return 1

    def set_named_security_info(self, name, object_type, information, owner, group, dacl, sacl):
        self.calls.append(("set", name, object_type, information, owner, group, dacl.value, sacl))
        return self.set_result

    def local_free(self, memory):
        self.calls.append(("free", memory.value))


class WindowsBranchTests(unittest.TestCase):
    """The Windows branch with whoami and the security calls replaced, so it runs on every OS."""

    def setUp(self):
        self.fake = FakeSecurityApi()
        for patcher in (
            mock.patch.object(env_file, "_is_windows", return_value=True),
            mock.patch.dict(os.environ, {"SystemRoot": r"D:\Win", "USERNAME": "builder"}),
            mock.patch.object(env_file, "_load_security_api", side_effect=lambda: self.fake.api()),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.commands: list[list[str]] = []
        self.path = Path("project") / ".env.local"
        self.build = ("build", f"D:P(A;;FA;;;{FAKE_SID})", 1, None)

    def fake_whoami(self, output=None):
        if output is None:
            # Console code-page output: the user name is not valid UTF-8.
            output = b'"pc\\caf\x82","' + FAKE_SID.encode() + b'"\r\n'

        def run(command, **kwargs):
            self.commands.append(command)
            self.assertFalse(kwargs.get("shell", False))
            self.assertTrue(command[0].endswith("whoami.exe"), command)
            return subprocess.CompletedProcess(command, 0, stdout=output, stderr=b"")

        return mock.patch.object(env_file.subprocess, "run", side_effect=run)

    def restrict(self):
        with self.fake_whoami():
            env_file.restrict_to_owner(self.path)

    def test_replaces_the_list_with_one_protected_entry_for_the_current_user(self):
        self.restrict()

        self.assertEqual(
            [[r"D:\Win\System32\whoami.exe", "/user", "/fo", "csv", "/nh"]], self.commands
        )
        descriptor, dacl = FakeSecurityApi.DESCRIPTOR, FakeSecurityApi.DACL
        self.assertEqual(
            [
                self.build,
                ("get_dacl", descriptor),
                # SE_FILE_OBJECT, then DACL_SECURITY_INFORMATION together with
                # PROTECTED_DACL_SECURITY_INFORMATION, which blocks inheritance.
                ("set", os.path.abspath(self.path), 1, 0x80000004, None, None, dacl, None),
                ("free", descriptor),
            ],
            self.fake.calls,
        )

    def test_refused_change_raises_with_a_fix_naming_the_user(self):
        self.fake.set_result = 50
        with self.assertRaises(env_file.SecretFileProtectionError) as caught:
            self.restrict()

        message = str(caught.exception)
        self.assertIn(str(self.path), message)
        self.assertIn("SetNamedSecurityInfoW error 50: Windows message 50.", message)
        self.assertIn('/grant:r "builder:F"', message)
        self.assertEqual(("free", FakeSecurityApi.DESCRIPTOR), self.fake.calls[-1])

    def test_missing_sid_raises_before_the_access_list_is_touched(self):
        with self.fake_whoami(b"ERROR: no user information\r\n"):
            with self.assertRaises(env_file.SecretFileProtectionError):
                env_file.restrict_to_owner(self.path)

        self.assertEqual(1, len(self.commands))
        self.assertEqual([], self.fake.calls)

    def test_tool_or_library_that_cannot_run_raises_protection_error(self):
        cases = {
            "whoami missing": mock.patch.object(
                env_file.subprocess, "run", side_effect=FileNotFoundError("whoami.exe")
            ),
            "security functions missing": mock.patch.object(
                env_file, "_load_security_api", side_effect=OSError("advapi32 not found")
            ),
        }
        for name, patcher in cases.items():
            with self.subTest(name):
                with self.fake_whoami(), patcher:
                    with self.assertRaises(env_file.SecretFileProtectionError):
                        env_file.restrict_to_owner(self.path)

        self.assertEqual([], self.fake.calls)

    def test_list_that_cannot_be_built_is_never_applied(self):
        descriptor = FakeSecurityApi.DESCRIPTOR
        cases = {
            # Nothing was allocated, so nothing is freed.
            "descriptor not built": ("builds", False, [self.build]),
            # A NULL list would grant everyone full control.
            "descriptor without a list": (
                "dacl",
                None,
                [self.build, ("get_dacl", descriptor), ("free", descriptor)],
            ),
        }
        for name, (attribute, value, expected_calls) in cases.items():
            with self.subTest(name):
                self.fake = FakeSecurityApi()
                setattr(self.fake, attribute, value)
                with self.assertRaises(env_file.SecretFileProtectionError) as caught:
                    self.restrict()

                self.assertIn("Windows error 87", str(caught.exception))
                self.assertEqual(expected_calls, self.fake.calls)

    def test_failed_restriction_leaves_no_new_file(self):
        self.fake.set_result = 5
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env.local"
            with self.fake_whoami():
                with self.assertRaises(env_file.SecretFileProtectionError):
                    env_file.write_private_text(path, "KEY=placeholder\n")

            self.assertFalse(path.exists())


@WINDOWS_ONLY
class WindowsAccessControlTests(unittest.TestCase):
    """Reads the real access-control list back with icacls /save (SDDL text).

    Entries look like "A;;FA;;;S-1-5-21-...": type, flags ("ID" means
    inherited), rights, two object fields, then the SID or an SDDL alias.
    """

    def saved_dacl(self, path):
        saved = path.with_name(path.name + ".acl")
        subprocess.run(
            [env_file._system_tool("icacls.exe"), str(path), "/save", str(saved)],
            check=True,
            capture_output=True,
        )
        text = saved.read_bytes().decode("utf-16-le", errors="replace").lstrip("\ufeff")
        saved.unlink()
        # At least one "(...)" entry, so a "D:\..." path in the file cannot match.
        match = re.search(r"D:([A-Z]*)((?:\([^)]*\))+)", text)
        self.assertIsNotNone(match, text)
        assert match is not None
        return match.group(1), re.findall(r"\(([^)]*)\)", match.group(2))

    def temp_folder(self):
        folder = Path(tempfile.gettempdir()) / f"nbga-acl-{uuid.uuid4().hex}"
        os.mkdir(folder)
        self.addCleanup(shutil.rmtree, folder, ignore_errors=True)
        return folder

    def inheriting_folder(self):
        # A folder that passes its entries on as inherited entries. On the CI
        # runner even a plain mkdir under the temp folder passes explicit copies
        # instead (run 42557263741), so reset the folder to inherited entries
        # and check that new files there really receive inherited entries.
        folder = self.temp_folder()
        subprocess.run(
            [env_file._system_tool("icacls.exe"), str(folder), "/reset"],
            check=True,
            capture_output=True,
        )
        probe = folder / "probe.txt"
        probe.write_text("probe\n", encoding="utf-8")
        _, entries = self.saved_dacl(probe)
        self.assertTrue(
            all("ID" in entry.split(";")[1] for entry in entries),
            f"the reset folder should pass inherited entries to new files: {entries}",
        )
        return folder

    def assert_restricted(self, path):
        flags, entries = self.saved_dacl(path)
        self.assertIn("P", flags, "inherited entries should be blocked")
        sid = env_file._current_user_sid(path)
        # SDDL writes the built-in Administrator account (RID 500) as "LA".
        user = {sid, "LA"} if sid.endswith("-500") else {sid}
        self.assertEqual(1, len(entries), entries)
        ace_type, ace_flags, rights, _, _, ace_sid = entries[0].split(";")[:6]
        self.assertEqual(("A", "", "FA"), (ace_type, ace_flags, rights), entries)
        self.assertIn(ace_sid, user, entries)

    def assert_new_and_rewritten_files_are_restricted(self, folder):
        path = folder / ".env"
        env_file.write_private_text(path, "KEY=first\n")
        self.assert_restricted(path)

        # Another tool adds an explicit entry: BUILTIN\Users, by SID so a
        # translated group name cannot break the test (SDDL writes it as "BU").
        # Confirm it is there, so the rewrite has something to remove.
        subprocess.run(
            [env_file._system_tool("icacls.exe"), str(path), "/grant", "*S-1-5-32-545:R"],
            check=True,
            capture_output=True,
        )
        _, entries = self.saved_dacl(path)
        self.assertIn("BU", [entry.split(";")[5] for entry in entries], entries)

        env_file.write_private_text(path, "KEY=second\n")
        self.assert_restricted(path)
        self.assertEqual("KEY=second\n", path.read_text(encoding="utf-8"))

    def test_inheriting_folder_new_and_rewritten_files_keep_one_entry(self):
        self.assert_new_and_rewritten_files_are_restricted(self.inheriting_folder())

    def test_entries_copied_from_a_folder_without_auto_inheritance_are_removed(self):
        # CI runs 42556335162 and 42557263741: files created in these folders
        # receive explicit SYSTEM, Administrators and Owner Rights entries,
        # which icacls /inheritance:r used to keep.
        with tempfile.TemporaryDirectory() as tmp:
            for name, folder in (("mkdtemp", Path(tmp)), ("plain mkdir", self.temp_folder())):
                with self.subTest(name):
                    self.assert_new_and_rewritten_files_are_restricted(folder)


if __name__ == "__main__":
    unittest.main()
