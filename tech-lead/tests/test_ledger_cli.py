from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

from helpers import make_ledger, make_task

LEDGER_PY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "..", "scripts", "ledger.py"))


def clean_env():
    return {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}


def run(args, cwd=None):
    return subprocess.run([sys.executable, LEDGER_PY] + args, capture_output=True,
                          text=True, encoding="utf-8", cwd=cwd, env=clean_env())


def git(repo, *args):
    subprocess.run(["git"] + list(args), cwd=repo, check=True, capture_output=True,
                   env=clean_env())


def make_repo(tmp):
    git(tmp, "init", "-q")
    git(tmp, "config", "user.email", "t@example.com")
    git(tmp, "config", "user.name", "T")
    git(tmp, "config", "commit.gpgsign", "false")
    with open(os.path.join(tmp, "README"), "w") as f:
        f.write("x\n")
    git(tmp, "add", ".")
    git(tmp, "commit", "-q", "-m", "init")


class CliTest(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = os.path.realpath(self._td.name)
        self.addCleanup(self._td.cleanup)

    def write(self, ledger, name="ledger.json"):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=2)
            f.write("\n")
        return path

    def test_check_valid_and_invalid(self):
        ok = run(["check", self.write(make_ledger([make_task(1)]))])
        self.assertEqual((ok.returncode, ok.stdout), (0, ""))
        cyc = make_ledger([make_task(1, depends_on=[2]), make_task(2, depends_on=[1])])
        bad = run(["check", self.write(cyc, "c.json")])
        self.assertEqual(bad.returncode, 1)
        self.assertIn("cycle", bad.stdout)

    def test_show_prints_report(self):
        r = run(["show", self.write(make_ledger([make_task(1)]))])
        self.assertEqual(r.returncode, 0)
        self.assertIn("## Wave 1", r.stdout)
        self.assertIn("## Summary", r.stdout)

    def test_next_and_all_complete(self):
        r = run(["next", self.write(make_ledger([make_task(1)]))])
        self.assertEqual(r.returncode, 0)
        self.assertIn("Wave 1", r.stdout)
        self.assertIn("Task 1: Task 1 (sonnet/low)", r.stdout)
        done = run(["next", self.write(make_ledger([make_task(1)], done=[1]), "d.json")])
        self.assertIn("all tasks complete", done.stdout)

    def test_checkpoint_mark_end_to_end(self):
        make_repo(self.tmp)
        path = self.write(make_ledger([make_task(1, files=["README"])]))
        r = run(["checkpoint", path, "--wave", "1", "--base", "HEAD", "--mark"], cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Task 1: pass", r.stdout)
        self.assertGreaterEqual(sum(1 for l in r.stdout.splitlines() if l.startswith("Wrote /")), 2)
        with open(path, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["done"], [1])

    def test_checkpoint_mark_reports_codemap_only_when_present(self):
        make_repo(self.tmp)
        path = self.write(make_ledger([make_task(1, files=["README"])]))
        args = ["checkpoint", path, "--wave", "1", "--base", "HEAD", "--mark"]
        self.assertNotIn("Codemap:", run(args, cwd=self.tmp).stdout)
        pending = os.path.join(self.tmp, ".claude", "codemap", "pending.md")
        os.makedirs(os.path.dirname(pending))
        r = run(args, cwd=self.tmp)
        self.assertIn("Codemap: 0 pending (inline)\n", r.stdout)
        self.assertIn(f"Wrote {pending}\n", r.stdout)

    def test_checkpoint_prints_durations(self):
        make_repo(self.tmp)
        path = self.write(make_ledger([make_task(1, files=["README"])]))
        r = run(["checkpoint", path, "--wave", "1", "--base", "HEAD"], cwd=self.tmp)
        self.assertRegex(r.stdout, r"Task 1: pass \(\d+\.\ds\)")
        self.assertRegex(r.stdout, r"Checks: pass \(\d+\.\ds\)")

    def test_checkpoint_failure_does_not_mark(self):
        make_repo(self.tmp)
        path = self.write(make_ledger([make_task(1, verify=["false"])]))
        r = run(["checkpoint", path, "--wave", "1", "--base", "HEAD", "--mark"], cwd=self.tmp)
        self.assertEqual(r.returncode, 1)
        with open(path, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["done"], [])

    def test_malformed_json_one_line(self):
        path = os.path.join(self.tmp, "bad.json")
        with open(path, "w") as f:
            f.write("{nope")
        r = run(["check", path])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len(r.stderr.strip().splitlines()), 1)
        self.assertTrue(r.stderr.startswith("error:"))
        self.assertNotIn("Traceback", r.stderr)

    def test_checkpoint_errors(self):
        path = self.write(make_ledger([make_task(1)]))
        with open(path, "rb") as f:
            before = f.read()
        plain = tempfile.mkdtemp(dir=self.tmp)
        r1 = run(["checkpoint", path, "--wave", "1", "--base", "HEAD", "--mark"], cwd=plain)
        repo = os.path.join(self.tmp, "repo")
        os.mkdir(repo)
        make_repo(repo)
        r2 = run(["checkpoint", path, "--wave", "1", "--base", "nope", "--mark"], cwd=repo)
        for r in (r1, r2):
            self.assertEqual(r.returncode, 1)
            self.assertEqual(len(r.stderr.strip().splitlines()), 1, r.stderr)
            self.assertTrue(r.stderr.startswith("error:"))
        self.assertIn("not a git repository", r1.stderr)
        with open(path, "rb") as f:
            self.assertEqual(f.read(), before)

    def test_usage_error_one_line(self):
        r = run(["frobnicate"])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len(r.stderr.strip().splitlines()), 1)
        self.assertTrue(r.stderr.startswith("error:"))


if __name__ == "__main__":
    unittest.main()
