import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = [
    "automation",
    "scripts",
    "templates/project",
    "freedom.tool.yaml",
    "project-control.yaml",
]
SKIP_PARTS = {"docs", "__pycache__"}
SECRET_VALUE_PATTERNS = [
    re.compile(r"=\s*(sk_live_[A-Za-z0-9]{12,})"),
    re.compile(r"=\s*(gh[pousr]_[A-Za-z0-9_]{12,})"),
    re.compile(r"=\s*(xox[baprs]-[A-Za-z0-9-]{12,})"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
]


class SecretHygieneTests(unittest.TestCase):
    def test_no_obvious_secret_values_in_controlled_code(self):
        matches = []
        for root_name in SCAN_ROOTS:
            root = REPO_ROOT / root_name
            paths = (
                [root] if root.is_file() else [path for path in root.rglob("*") if path.is_file()]
            )
            for path in paths:
                relative = path.relative_to(REPO_ROOT)
                if any(part in SKIP_PARTS for part in relative.parts):
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                for pattern in SECRET_VALUE_PATTERNS:
                    if pattern.search(text):
                        matches.append(str(relative))

        self.assertEqual([], matches)


if __name__ == "__main__":
    unittest.main()
