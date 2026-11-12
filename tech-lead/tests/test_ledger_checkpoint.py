from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest

import helpers  # noqa: F401  (adds scripts to sys.path)
from helpers import make_ledger, make_task

import ledger_checkpoint as cp


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
    return subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True,
                          text=True, env=env).stdout.strip()


PROGRESS = """# Progress
Task 1: complete
Ruling: a
Task 2: Ruling: b
Task 3: parked — f — Ruling: c
  Attempt: Task 1 sonnet/low failed, cause brief, x
Plain note
"""


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(self.repo)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "T")
        git(self.repo, "config", "commit.gpgsign", "false")
        with open(os.path.join(self.repo, "README"), "w") as f:
            f.write("x\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "init")
        self.base = git(self.repo, "rev-parse", "HEAD")
        os.makedirs(os.path.join(self.repo, "src"))
        for p in ("src/t1.py", "other.txt"):
            with open(os.path.join(self.repo, p), "w") as f:
                f.write("y\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "work")
        self.log = os.path.join(self.tmp, "scratch", "sub", "log.txt")
        self.ledger_path = os.path.join(self.tmp, "ledger.json")

    def run_cp(self, verify=("true",), checks=(), base=None):
        ledger = make_ledger([make_task(1, verify=list(verify))], checks=list(checks))
        return cp.run_checkpoint(ledger, 1, base or self.base, self.repo, self.log)

    def test_out_of_scope_with_directory_prefix(self):
        self.assertEqual(cp.out_of_scope(["src/a.py", "x.txt"], ["src/"]), ["x.txt"])

    def test_pass(self):
        r = self.run_cp(checks=["true"])
        self.assertTrue(r.passed)
        out = cp.format_result(r)
        self.assertIn("Task 1: pass", out)
        self.assertIn("Checks: pass", out)
        self.assertIn("Out of scope: other.txt", out)
        self.assertTrue(os.path.isabs(r.log_path))

    def test_failing_verify(self):
        r = self.run_cp(verify=["exit 3"])
        self.assertFalse(r.passed)
        self.assertIn("Task 1: fail (exit 3)", cp.format_result(r))

    def test_failing_check(self):
        r = self.run_cp(checks=["exit 2"])
        self.assertFalse(r.passed)
        self.assertIn("Check failed: exit 2 (exit 2)", cp.format_result(r))

    def test_output_goes_to_log_only(self):
        r = self.run_cp(verify=["echo hello"])
        with open(self.log, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("hello", text)
        self.assertIn("$ echo hello", text)
        self.assertNotIn("hello", cp.format_result(r))

    def test_bad_base_raises(self):
        with self.assertRaises(cp.CheckpointError) as cm:
            self.run_cp(base="nope")
        self.assertTrue(str(cm.exception).startswith("git diff failed"))

    def test_non_ascii_declared_file_is_in_scope(self):
        name = "src/za\u017c\u00f3\u0142\u0107.py"
        with open(os.path.join(self.repo, name), "w") as f:
            f.write("z\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "nonascii")
        ledger = make_ledger([make_task(1, files=[name, "other.txt", "src/t1.py"])])
        r = cp.run_checkpoint(ledger, 1, self.base, self.repo, self.log)
        self.assertEqual(r.out_of_scope, [])

    def test_empty_wave_raises(self):
        ledger = make_ledger([make_task(1)])
        with self.assertRaises(cp.CheckpointError) as cm:
            cp.run_checkpoint(ledger, 5, self.base, self.repo, self.log)
        self.assertEqual(str(cm.exception), "wave 5 has no tasks")
        self.assertFalse(os.path.exists(self.log))
        with self.assertRaises(cp.CheckpointError):
            cp.mark_done(self.ledger_path, ledger, 5, None, "2026-11-11")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "journal.md")))

    def test_unwritable_log_raises(self):
        blocker = os.path.join(self.tmp, "file")
        with open(blocker, "w") as f:
            f.write("x")
        ledger = make_ledger([make_task(1)])
        with self.assertRaises(cp.CheckpointError) as cm:
            cp.run_checkpoint(ledger, 1, self.base, self.repo, os.path.join(blocker, "l.txt"))
        self.assertTrue(str(cm.exception).startswith("cannot write log "))

    def _marked(self, progress=PROGRESS):
        ledger = make_ledger([make_task(1)])
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            json.dump(ledger, f)
        pp = None
        if progress is not None:
            pp = os.path.join(self.tmp, "progress.md")
            with open(pp, "w", encoding="utf-8") as f:
                f.write(progress)
        return ledger, pp

    def journal(self):
        with open(os.path.join(self.tmp, "journal.md"), encoding="utf-8") as f:
            return f.read()

    def test_mark_done_updates_ledger_and_journal(self):
        ledger, pp = self._marked()
        written = cp.mark_done(self.ledger_path, ledger, 1, pp, "2026-11-11")
        self.assertEqual(sorted(written), sorted([self.ledger_path,
                                                  os.path.join(self.tmp, "journal.md")]))
        with open(self.ledger_path, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["done"], [1])
        j = self.journal()
        for s in ("## 2026-11-11 wave 1", "Tasks done: 1", "Ruling: a", "Task 2: Ruling: b",
                  "Task 3: parked — f — Ruling: c",
                  "Attempt: Task 1 sonnet/low failed, cause brief, x"):
            self.assertIn(s, j)
        self.assertNotIn("Task 1: complete", j)

    def test_mark_done_does_not_duplicate_copied_lines(self):
        ledger, pp = self._marked()
        cp.mark_done(self.ledger_path, ledger, 1, pp, "2026-11-11")
        cp.mark_done(self.ledger_path, ledger, 1, pp, "2026-11-12")
        j = self.journal()
        self.assertEqual(j.count("Ruling: a"), 1)
        self.assertEqual(j.count("Task 2: Ruling: b"), 1)
        self.assertEqual(j.count("Attempt:"), 1)

    def test_mark_done_without_progress(self):
        ledger, _ = self._marked(None)
        cp.mark_done(self.ledger_path, ledger, 1, None, "2026-11-11")
        self.assertEqual(self.journal(), "## 2026-11-11 wave 1\nTasks done: 1\n")

    def test_done_order_and_no_duplicates(self):
        ledger = make_ledger([make_task(1), make_task(2), make_task(3, depends_on=[1])],
                             done=[2])
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            json.dump(ledger, f)
        cp.mark_done(self.ledger_path, ledger, 1, None, "2026-11-11")
        self.assertEqual(ledger["done"], [2, 1])

    def test_non_ascii_journal(self):
        line = "Ruling: zmiana nazwy pliku — powód"
        ledger, pp = self._marked(line + "\n")
        ledger["title"] = "ż"
        cp.mark_done(self.ledger_path, ledger, 1, pp, "2026-11-11")
        self.assertIn(line, self.journal())
        with open(self.ledger_path, encoding="utf-8") as f:
            raw = f.read()
        self.assertIn("ż", raw)
        self.assertNotIn("\\u017c", raw)


if __name__ == "__main__":
    unittest.main()
