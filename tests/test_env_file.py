import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import env_file


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


if __name__ == "__main__":
    unittest.main()
