import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import update_check


def fake_fetch(payloads):
    def _fetch(url, timeout):
        return payloads[url]

    return _fetch


class UpdateCheckTests(unittest.TestCase):
    def test_reports_current_from_latest_release(self):
        result = update_check.check_for_updates(
            local_version="0.3.0",
            fetch_json=fake_fetch(
                {
                    "https://api.github.com/repos/Adamgdwn/new-build-governance-agent/releases/latest": {
                        "tag_name": "v0.3.0"
                    }
                }
            ),
        )

        self.assertEqual(update_check.STATUS_CURRENT, result.status)
        self.assertEqual("0.3.0", result.latest_version)
        self.assertEqual("GitHub release", result.source)

    def test_reports_behind_from_tags_when_release_is_not_semver(self):
        result = update_check.check_for_updates(
            local_version="0.3.0",
            fetch_json=fake_fetch(
                {
                    "https://api.github.com/repos/Adamgdwn/new-build-governance-agent/releases/latest": {
                        "tag_name": "preview"
                    },
                    "https://api.github.com/repos/Adamgdwn/new-build-governance-agent/tags?per_page=50": [
                        {"name": "v0.4.0"},
                        {"name": "v0.2.0"},
                    ],
                }
            ),
        )

        self.assertEqual(update_check.STATUS_BEHIND, result.status)
        self.assertEqual("0.4.0", result.latest_version)
        self.assertEqual("GitHub tags", result.source)

    def test_reports_ahead(self):
        result = update_check.check_for_updates(
            local_version="0.5.0",
            fetch_json=fake_fetch(
                {
                    "https://api.github.com/repos/Adamgdwn/new-build-governance-agent/releases/latest": {
                        "tag_name": "0.4.0"
                    }
                }
            ),
        )

        self.assertEqual(update_check.STATUS_AHEAD, result.status)

    def test_reports_unable_when_no_semver_remote_exists(self):
        result = update_check.check_for_updates(
            local_version="0.3.0",
            fetch_json=fake_fetch(
                {
                    "https://api.github.com/repos/Adamgdwn/new-build-governance-agent/releases/latest": {
                        "tag_name": "preview"
                    },
                    "https://api.github.com/repos/Adamgdwn/new-build-governance-agent/tags?per_page=50": [
                        {"name": "preview"}
                    ],
                }
            ),
        )

        self.assertEqual(update_check.STATUS_UNABLE, result.status)
        self.assertIn("no semantic version tags", result.error)


if __name__ == "__main__":
    unittest.main()
