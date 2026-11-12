from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import helpers
from helpers import make_ledger, make_task

import status

SCRIPT = os.path.join(helpers.SCRIPTS, "status.py")


def add(root, name, ledger=None, spec=False, journal=None, raw_ledger=None):
    d = Path(root) / "docs" / "initiatives" / name
    d.mkdir(parents=True, exist_ok=True)
    if ledger is not None:
        (d / "ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
    if raw_ledger is not None:
        (d / "ledger.json").write_text(raw_ledger, encoding="utf-8")
    if spec:
        (d / "spec.md").write_text("spec\n", encoding="utf-8")
    if journal is not None:
        (d / "journal.md").write_text(journal, encoding="utf-8")
    return d


def backlog(root, text):
    p = Path(root) / "docs" / "backlog.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def three_tasks(done):
    return make_ledger(
        [make_task(1), make_task(2, depends_on=[1]), make_task(3, depends_on=[2])],
        done=done)


class StatusTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_states(self):
        two = [make_task(1), make_task(2)]
        add(self.root, "2026-01-01-proposed", journal="## x session\n")
        add(self.root, "2026-01-02-specified", spec=True)
        add(self.root, "2026-01-03-planned", ledger=make_ledger(two))
        add(self.root, "2026-01-04-progress", ledger=make_ledger(two, done=[1]))
        add(self.root, "2026-01-05-done", ledger=make_ledger(two, done=[1, 2]))
        add(self.root, "2026-01-06-closed", ledger=make_ledger(two),
            journal="## s\nClosed: abandoned — no\n")
        add(self.root, "2026-01-07-broken", raw_ledger="{nope")
        base = Path(self.root) / "docs" / "initiatives"
        got = {p.name[11:]: status.initiative_state(p)["state"] for p in sorted(base.iterdir())}
        self.assertEqual(got, {
            "proposed": "proposed", "specified": "specified", "planned": "planned",
            "progress": "in progress", "done": "done", "closed": "closed",
            "broken": "unknown (ledger error)",
        })

    def test_waves_and_next(self):
        d = add(self.root, "2026-02-01-w", ledger=three_tasks([1]))
        info = status.initiative_state(d)
        self.assertEqual((info["waves_done"], info["waves_total"], info["next_wave"]), (1, 3, 2))
        self.assertEqual(info["date"], "2026-02-01")
        self.assertTrue(os.path.isabs(info["path"]))

    def test_no_date_prefix(self):
        d = add(self.root, "topic", spec=True)
        self.assertEqual(status.initiative_state(d)["date"], "")

    def test_backlog_open_items_only(self):
        backlog(self.root, "- [ ] B1 a\n- [x] B2 b\n- [x-link](i/) B3 c\n")
        self.assertEqual(status.read_backlog(Path(self.root) / "docs" / "backlog.md"), ["B1 a"])
        self.assertEqual(status.read_backlog(Path(self.root) / "nope.md"), [])

    def test_full_lists_absolute_paths_and_sections(self):
        d = add(self.root, "2026-02-01-w", ledger=three_tasks([1]))
        add(self.root, "2026-02-02-p", ledger=make_ledger([make_task(1)]))
        add(self.root, "2026-02-03-d", ledger=make_ledger([make_task(1)], done=[1]))
        backlog(self.root, "- [ ] B1 first\n")
        out = status.render_full(Path(self.root))
        self.assertTrue(out.startswith("# Project status"))
        self.assertIn(f"- 2026-02-01-w (in progress, waves 1/3, next wave 2): {d}", out)
        self.assertIn("(planned, waves 0/1, next wave 1)", out)
        self.assertIn("(done, waves 1/1):", out)
        heads = [l for l in out.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["## In progress", "## Planned", "## Recently done", "## Backlog"])
        self.assertIn("- B1 first", out)

    def test_recently_done_limited_to_five_newest(self):
        for n in range(1, 8):
            add(self.root, f"2026-03-0{n}-d{n}", ledger=make_ledger([make_task(1)], done=[1]))
        out = status.render_full(Path(self.root))
        sect = out.split("## Recently done")[1].split("## Backlog")[0]
        self.assertEqual(sect.count("- 2026"), 5)
        self.assertIn("2026-03-07-d7", sect)
        self.assertNotIn("2026-03-01-d1", sect)

    def test_full_without_initiatives(self):
        self.assertIn("No initiatives yet.", status.render_full(Path(self.root)))

    def test_brief_silent_without_initiatives(self):
        self.assertEqual(status.render_brief(Path(self.root)), "")

    def test_brief_limit_and_instruction(self):
        for n in range(40):
            add(self.root, f"2026-04-{n + 1:02d}-p{n}", ledger=make_ledger([make_task(1)]))
        backlog(self.root, "".join(f"- [ ] B{n} item\n" for n in range(9)))
        out = status.render_brief(Path(self.root))
        lines = out.splitlines()
        self.assertLessEqual(len(lines), 25)
        self.assertTrue(lines[0].startswith("tech-lead status for "))
        self.assertTrue(lines[-1].startswith("Propose next steps"))
        self.assertIn("If you are already carrying out an approved tech-lead plan or autopilot in this session, continue it instead.", lines[-1])
        self.assertEqual(sum(1 for l in lines if l.startswith("- B")), 5)

    def test_write_header_and_path(self):
        add(self.root, "2026-05-01-x", spec=True)
        p = status.write_status(Path(self.root))
        self.assertEqual(p, Path(self.root).absolute() / "docs" / "STATUS.md")
        text = p.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("<!-- generated by tech-lead status.py, do not edit -->\n"))
        self.assertIn("# Project status", text)

    def test_non_ascii_round_trip(self):
        add(self.root, "2026-05-01-x", spec=True)
        backlog(self.root, "- [ ] B3 Zażółć gęślą jaźń\n")
        self.assertIn("- B3 Zażółć gęślą jaźń", status.render_full(Path(self.root)))
        p = status.write_status(Path(self.root))
        self.assertIn("Zażółć gęślą jaźń", p.read_text(encoding="utf-8"))

    def _run(self, args, env_extra=None, cwd=None):
        env = {k: v for k, v in os.environ.items()
               if k not in ("CLAUDE_PROJECT_DIR", "TECH_LEAD_STATUS")}
        env.update(env_extra or {})
        return subprocess.run([sys.executable, SCRIPT] + args, cwd=cwd, env=env,
                              capture_output=True)

    def test_root_from_env(self):
        add(self.root, "2026-05-01-x", ledger=make_ledger([make_task(1)]))
        with tempfile.TemporaryDirectory() as elsewhere:
            r = self._run(["--brief"], {"CLAUDE_PROJECT_DIR": self.root}, cwd=elsewhere)
        out = r.stdout.decode("utf-8")
        self.assertEqual(r.returncode, 0)
        first = out.splitlines()[0]
        self.assertEqual(os.path.realpath(first[len("tech-lead status for "):]),
                         os.path.realpath(self.root))

    def test_cli_write_announces_path(self):
        add(self.root, "2026-05-01-x", spec=True)
        r = self._run([self.root, "--write"])
        self.assertEqual(r.returncode, 0)
        line = r.stdout.decode("utf-8").strip()
        self.assertEqual(line, f"Wrote {os.path.abspath(os.path.join(self.root, 'docs', 'STATUS.md'))}")

    def test_cli_usage_error(self):
        r = self._run(["--bogus"])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len(r.stderr.decode("utf-8").strip().splitlines()), 1)
        self.assertTrue(r.stderr.decode("utf-8").startswith("error: "))

    def test_brief_disabled_by_env(self):
        add(self.root, "2026-05-01-x", spec=True)
        r = self._run([self.root, "--brief"], {"TECH_LEAD_STATUS": "0"})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, b"")

    def test_brief_swallows_errors(self):
        buf = io.StringIO()
        with mock.patch.object(status, "render_brief", side_effect=RuntimeError("boom")):
            with contextlib.redirect_stdout(buf):
                rc = status.main([self.root, "--brief"])
        self.assertEqual(rc, 0)
        self.assertEqual(buf.getvalue(), "")

    def test_brief_status_path_only_when_present(self):
        add(self.root, "2026-05-01-x", spec=True)
        self.assertNotIn("Full status:", status.render_brief(Path(self.root)))
        p = status.write_status(Path(self.root))
        out = status.render_brief(Path(self.root))
        self.assertTrue(out.splitlines()[-1].endswith(f" Full status: {p}"))
        self.assertTrue(out.splitlines()[-1].startswith("Propose next steps"))


if __name__ == "__main__":
    unittest.main()
