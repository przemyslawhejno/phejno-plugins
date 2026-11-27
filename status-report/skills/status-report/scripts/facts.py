#!/usr/bin/env python3
"""Collect the facts for an owner status report: releases since the last report, milestone progress, in-progress and owner-waiting issues."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys

CONFIG = pathlib.Path(".claude") / "status-report.json"
LAST = pathlib.Path(".claude") / "status-report.last"
BOX = re.compile(r"^\s*[-*] \[([ xX])\]", re.M)


def run(argv: list[str], cwd: pathlib.Path) -> str:
    res = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=120)
    if res.returncode != 0:
        raise RuntimeError(f"{' '.join(argv[:3])}: {res.stderr.strip()[:200]}")
    return res.stdout


def checklist(body: str) -> tuple[int, int]:
    marks = BOX.findall(body or "")
    return sum(m in "xX" for m in marks), len(marks)


def milestone(issue: dict, paused_labels: set[str]) -> dict:
    done, total = checklist(issue.get("body", ""))
    labels = {lab["name"] for lab in issue.get("labels", [])}
    closed = issue.get("state") == "CLOSED"
    pct = 100 if closed and (total == 0 or done == total) else (round(100 * done / total) if total else None)
    return {"number": issue["number"], "title": issue["title"], "state": issue["state"], "done": done, "total": total,
            "pct": pct, "paused": bool(labels & paused_labels)}


def releases(root: pathlib.Path, pattern: str, since: str | None) -> list[dict]:
    fmt = "%(refname:short)\t%(creatordate:iso-strict)\t%(subject)"
    out = run(["git", "for-each-ref", "--sort=creatordate", f"--format={fmt}", f"refs/tags/{pattern}"], root)
    rows = []
    for line in out.splitlines():
        tag, when, subject = (line.split("\t", 2) + ["", ""])[:3]
        if since and dt.datetime.fromisoformat(when) <= dt.datetime.fromisoformat(since):
            continue
        rows.append({"tag": tag, "when": when, "subject": subject})
    return rows


def issues(root: pathlib.Path, label: str) -> list[dict]:
    out = run(["gh", "issue", "list", "--state", "open", "--label", label, "--limit", "100",
               "--json", "number,title,updatedAt"], root)
    return json.loads(out)


def collect(root: pathlib.Path, cfg: dict, since: str | None) -> dict:
    paused = set(cfg.get("paused_labels", []))
    ms = []
    for m in cfg.get("milestones", []):
        issue = json.loads(run(["gh", "issue", "view", str(m["issue"]), "--json", "number,title,state,body,labels"], root))
        ms.append({"label": m.get("label", f"#{m['issue']}"), **milestone(issue, paused)})
    facts = {"now": dt.datetime.now().astimezone().isoformat(timespec="minutes"), "since": since, "milestones": ms,
             "releases": releases(root, cfg["tag_pattern"], since) if cfg.get("tag_pattern") else [],
             "in_progress": [], "waiting_on_owner": []}
    for key, labels in (("in_progress", cfg.get("in_progress_labels", [])), ("waiting_on_owner", cfg.get("owner_labels", []))):
        seen = set()
        for lab in labels:
            for i in issues(root, lab):
                if i["number"] not in seen:
                    seen.add(i["number"])
                    facts[key].append(i)
    return facts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="project root (holds .claude/status-report.json)")
    ap.add_argument("--since", help="ISO time of the previous report; default: the time saved by --mark")
    ap.add_argument("--mark", action="store_true", help="save now as the time of the last report and exit")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root).resolve()
    if a.mark:
        (root / LAST).parent.mkdir(exist_ok=True)
        (root / LAST).write_text(dt.datetime.now().astimezone().isoformat(timespec="seconds") + "\n", encoding="utf-8")
        print(f"Wrote {root / LAST}")
        return 0
    try:
        cfg = json.loads((root / CONFIG).read_text(encoding="utf-8")) if (root / CONFIG).exists() else {}
        since = a.since or ((root / LAST).read_text(encoding="utf-8").strip() if (root / LAST).exists() else None)
        print(json.dumps(collect(root, cfg, since), ensure_ascii=False, indent=2))
    except (RuntimeError, ValueError, KeyError, OSError, subprocess.TimeoutExpired) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
