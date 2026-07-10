import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import self_update


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def commit_file(repo: Path, name: str, body: str, message: str) -> str:
    path = repo / name
    path.write_text(body, encoding="utf-8")
    git(repo, "add", name)
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


class SelfUpdateTests(unittest.TestCase):
    def setUp(self):
        if not shutil.which("git"):
            self.skipTest("git is required for self-update tests")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.remote = self.root / "origin.git"
        self.seed = self.root / "seed"
        self.work = self.root / "work"

        subprocess.run(
            ["git", "init", "--bare", str(self.remote)], check=True, capture_output=True, text=True
        )
        subprocess.run(["git", "init", str(self.seed)], check=True, capture_output=True, text=True)
        git(self.seed, "config", "user.email", "test@example.com")
        git(self.seed, "config", "user.name", "Test User")
        commit_file(self.seed, "README.md", "one\n", "initial")
        git(self.seed, "branch", "-M", "main")
        git(self.seed, "remote", "add", "origin", str(self.remote))
        git(self.seed, "push", "-u", "origin", "main")
        subprocess.run(
            ["git", "--git-dir", str(self.remote), "symbolic-ref", "HEAD", "refs/heads/main"],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "clone", str(self.remote), str(self.work)],
            check=True,
            capture_output=True,
            text=True,
        )
        git(self.work, "config", "user.email", "test@example.com")
        git(self.work, "config", "user.name", "Test User")

    def tearDown(self):
        self.tmp.cleanup()

    def push_remote_commit(self, body: str = "two\n") -> str:
        new_sha = commit_file(self.seed, "README.md", body, "remote update")
        git(self.seed, "push", "origin", "main")
        return new_sha

    def test_fast_forward_updates_clean_checkout(self):
        new_sha = self.push_remote_commit()

        result = self_update.self_update(self.work)

        self.assertEqual(self_update.STATUS_UPDATED, result.status)
        self.assertEqual(new_sha, git(self.work, "rev-parse", "HEAD"))

    def test_dry_run_does_not_move_head(self):
        self.push_remote_commit()
        before = git(self.work, "rev-parse", "HEAD")

        result = self_update.self_update(self.work, dry_run=True)

        self.assertEqual(self_update.STATUS_WOULD_UPDATE, result.status)
        self.assertEqual(before, git(self.work, "rev-parse", "HEAD"))

    def test_refuses_dirty_worktree(self):
        (self.work / "local.txt").write_text("local\n", encoding="utf-8")

        result = self_update.self_update(self.work)

        self.assertEqual(self_update.STATUS_REFUSED, result.status)
        self.assertIn("?? local.txt", result.dirty_files)

    def test_refuses_local_ahead_branch(self):
        commit_file(self.work, "local.txt", "local\n", "local update")

        result = self_update.self_update(self.work)

        self.assertEqual(self_update.STATUS_REFUSED, result.status)
        self.assertIn("ahead", result.message)

    def test_reports_up_to_date(self):
        result = self_update.self_update(self.work)

        self.assertEqual(self_update.STATUS_UP_TO_DATE, result.status)

    def test_reports_failed_for_file_path_repo(self):
        not_a_repo_dir = self.root / "not-a-repo"
        not_a_repo_dir.write_text("not a directory\n", encoding="utf-8")

        result = self_update.self_update(not_a_repo_dir)

        self.assertEqual(self_update.STATUS_FAILED, result.status)


if __name__ == "__main__":
    unittest.main()
