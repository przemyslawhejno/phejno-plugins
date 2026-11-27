from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "skills" / "status-report" / "scripts" / "facts.py"
spec = importlib.util.spec_from_file_location("facts", SCRIPT)
facts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(facts)
REAL_RUN = facts.run


def issue(n, state="OPEN", body="", labels=()):
    return {"number": n, "title": f"T{n}", "state": state, "body": body, "labels": [{"name": x} for x in labels]}


class Milestones(unittest.TestCase):
    def test_checklist_gives_the_percentage_and_closed_complete_is_100(self):
        self.assertEqual(facts.milestone(issue(1, body="- [x] a\n- [ ] b\n* [X] c\n- [ ] d"), set())["pct"], 50)
        self.assertEqual(facts.milestone(issue(2, "CLOSED", "- [x] a"), set())["pct"], 100)
        self.assertEqual(facts.milestone(issue(3, "CLOSED", "- [x] a\n- [ ] b"), set())["pct"], 50)
        self.assertIsNone(facts.milestone(issue(4, body="no list"), set())["pct"])
        self.assertTrue(facts.milestone(issue(5, labels=["odłożone"]), {"odłożone"})["paused"])


class Collect(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        git = ["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        for tag, date in (("v1", "2026-01-01T10:00:00+00:00"), ("v2", "2026-01-02T10:00:00+00:00")):
            env = {"GIT_COMMITTER_DATE": date, "GIT_AUTHOR_DATE": date, "PATH": "/usr/bin:/bin"}
            subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", f"release {tag}"], check=True, env=env)
            subprocess.run([*git, "tag", "-a", tag, "-m", f"Release {tag}"], check=True, env=env)

    def fake(self, argv, cwd):
        if argv[0] == "git":
            return REAL_RUN(argv, cwd)
        if argv[:3] == ["gh", "issue", "view"]:
            return json.dumps(issue(int(argv[3]), body="- [x] a\n- [ ] b"))
        if argv[:3] == ["gh", "issue", "list"]:
            label = argv[argv.index("--label") + 1]
            return json.dumps([{"number": 7, "title": "q", "updatedAt": "x"}] if label in ("q", "q2") else [])
        raise AssertionError(argv)

    def test_releases_after_since_and_issues_by_label_without_duplicates(self):
        cfg = {"tag_pattern": "v*", "milestones": [{"label": "M1", "issue": 9}], "owner_labels": ["q", "q2"]}
        with mock.patch.object(facts, "run", side_effect=self.fake):
            out = facts.collect(self.root, cfg, "2026-01-01T12:00:00+00:00")
        self.assertEqual([r["tag"] for r in out["releases"]], ["v2"])
        self.assertEqual(out["milestones"][0]["label"], "M1")
        self.assertEqual(out["milestones"][0]["pct"], 50)
        self.assertEqual([i["number"] for i in out["waiting_on_owner"]], [7])
        self.assertEqual(out["in_progress"], [])

    def test_mark_then_since_defaults_to_it_and_gh_failure_is_one_error_line(self):
        self.assertEqual(facts.main(["--root", str(self.root), "--mark"]), 0)
        self.assertTrue((self.root / facts.LAST).read_text().strip())
        (self.root / facts.CONFIG).write_text(json.dumps({"milestones": [{"issue": 1}]}))
        with mock.patch.object(facts, "run", side_effect=RuntimeError("gh issue view: boom")), \
                mock.patch("sys.stderr") as err:
            self.assertEqual(facts.main(["--root", str(self.root)]), 1)
        self.assertTrue(any("error: gh issue view: boom" in str(c) for c in err.write.call_args_list))


if __name__ == "__main__":
    unittest.main()
