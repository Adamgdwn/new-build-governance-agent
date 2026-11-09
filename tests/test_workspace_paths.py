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

    def test_numbered_code_root_is_recognised(self):
        with tempfile.TemporaryDirectory() as tmp:
            code_root = Path(tmp).resolve() / "01. Code"

            self.assertEqual(
                code_root, workspace_paths.default_code_root(code_root / "New Build Agent")
            )

    def test_installed_inside_category_folder_uses_its_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            code_root = Path(tmp).resolve() / "01. Code"
            repo = code_root / "03. Agents" / "New Build Agent"

            self.assertEqual(code_root, workspace_paths.default_code_root(repo))

    def test_existing_numbered_category_folders_are_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            code_root = Path(tmp).resolve() / "01. Code"
            (code_root / "03. Agents").mkdir(parents=True)
            (code_root / "02. Applications").mkdir()
            os.environ[workspace_paths.ENV_CODE_ROOT] = str(code_root)

            agents, applications = workspace_paths.category_roots()

            self.assertEqual(code_root / "03. Agents", agents)
            self.assertEqual(code_root / "02. Applications", applications)

    def test_real_category_folder_preferred_over_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            code_root = Path(tmp).resolve()
            (code_root / "03. Agents").mkdir()
            try:
                (code_root / "agents").symlink_to(
                    code_root / "03. Agents", target_is_directory=True
                )
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable on this platform")
            os.environ[workspace_paths.ENV_CODE_ROOT] = str(code_root)

            agents, _ = workspace_paths.category_roots()

            self.assertEqual(code_root / "03. Agents", agents)

    def test_category_roots_never_create_folders(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ[workspace_paths.ENV_CODE_ROOT] = tmp

            agents, applications = workspace_paths.category_roots()

            self.assertEqual(Path(tmp) / "agents", agents)
            self.assertEqual(Path(tmp) / "Applications", applications)
            self.assertEqual([], list(Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
