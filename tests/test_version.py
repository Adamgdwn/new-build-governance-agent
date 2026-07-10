import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import version


class VersionTests(unittest.TestCase):
    def test_version_file_is_source_of_truth(self):
        self.assertEqual(
            (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip(), version.get_version()
        )
        self.assertEqual("New Build Governance Agent 0.3.0", version.get_version_string())

    def test_freedom_manifest_matches_version_file(self):
        manifest = (REPO_ROOT / "freedom.tool.yaml").read_text(encoding="utf-8")
        self.assertIn(f'version: "{version.get_version()}"', manifest)

    def test_version_cli_outputs_json(self):
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "automation" / "version.py"), "--json"],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(proc.stdout)
        self.assertEqual("New Build Governance Agent", payload["name"])
        self.assertEqual("new-build-governance-agent", payload["slug"])
        self.assertEqual(version.get_version(), payload["version"])

    def test_headless_version_flag(self):
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "automation" / "new_build_headless.py"), "--version"],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(version.get_version_string(), proc.stdout.strip())


if __name__ == "__main__":
    unittest.main()
