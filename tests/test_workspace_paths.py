import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import workspace_paths


class WorkspacePathTests(unittest.TestCase):
    def setUp(self):
        self.previous = os.environ.pop(workspace_paths.ENV_CODE_ROOT, None)

    def tearDown(self):
        if self.previous is not None:
            os.environ[workspace_paths.ENV_CODE_ROOT] = self.previous
        else:
            os.environ.pop(workspace_paths.ENV_CODE_ROOT, None)

    def test_prefers_explicit_code_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ[workspace_paths.ENV_CODE_ROOT] = tmp

            self.assertEqual(Path(tmp), workspace_paths.default_code_root(Path("/ignored/repo")))

    def _workspace_parent(self) -> Path:
        # Absolute on every platform so resolve() cannot prepend the cwd.
        return Path(tempfile.gettempdir()).resolve() / "01. Code Projects"

    def test_uses_windows_workspace_parent_when_installed_there(self):
        parent = self._workspace_parent()
        root = parent / "New Build Agent"

        self.assertEqual(parent, workspace_paths.default_code_root(root))

    def test_category_roots_are_stable(self):
        parent = self._workspace_parent()
        root = parent / "New Build Agent"
        agents, applications = workspace_paths.category_roots(root)

        self.assertEqual(parent / "agents", agents)
        self.assertEqual(parent / "Applications", applications)


if __name__ == "__main__":
    unittest.main()
