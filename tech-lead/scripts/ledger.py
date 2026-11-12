"""Ledger command line: check, show, next, checkpoint."""
from __future__ import annotations

import argparse
import datetime
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ledger_checkpoint import CheckpointError, format_result, mark_done, run_checkpoint, sync_codemap  # noqa: E402
from ledger_core import LedgerError, load, next_wave, validate  # noqa: E402
from ledger_report import render_show  # noqa: E402


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        print(f"error: {message}", file=sys.stderr)
        raise SystemExit(1)


def _build() -> argparse.ArgumentParser:
    p = _Parser(prog="ledger.py", allow_abbrev=False)
    sub = p.add_subparsers(dest="cmd", required=True, parser_class=_Parser)
    for name in ("check", "show", "next"):
        sub.add_parser(name, allow_abbrev=False).add_argument("ledger")
    c = sub.add_parser("checkpoint", allow_abbrev=False)
    c.add_argument("ledger")
    c.add_argument("--wave", type=int, required=True)
    c.add_argument("--base", required=True)
    c.add_argument("--log")
    c.add_argument("--progress")
    c.add_argument("--mark", action="store_true")
    return p


def _repo_root(cwd: str | None = None) -> str:
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
    try:
        p = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                           env=env, cwd=cwd)
    except OSError:
        raise CheckpointError("git is not installed")
    if p.returncode != 0:
        raise CheckpointError("not a git repository")
    return p.stdout.decode("utf-8", "replace").strip()


def _run(args, cwd: str | None = None) -> int:
    ledger = load(args.ledger)
    errors = validate(ledger)
    if errors:
        print("\n".join(errors))
        return 1
    if args.cmd == "check":
        return 0
    if args.cmd == "show":
        print(render_show(ledger))
        return 0
    if args.cmd == "next":
        nxt = next_wave(ledger)
        if nxt is None:
            print("all tasks complete")
            return 0
        wave, tasks = nxt
        print(f"Wave {wave}")
        for t in tasks:
            if t["model"] == "lead":
                print(f"Task {t['id']}: {t['title']} (lead)")
            else:
                print(f"Task {t['id']}: {t['title']} ({t['model']}/{t.get('effort', '')})")
        return 0
    repo = _repo_root(cwd)
    if args.log:
        log = os.path.join(cwd or "", args.log)
    else:
        log = os.path.join(repo, ".tech-lead", "scratch", f"checkpoint-{args.wave}.log")
    result = run_checkpoint(ledger, args.wave, args.base, repo, log)
    print(format_result(result))
    print(f"Wrote {result.log_path}")
    if not result.passed:
        return 1
    if args.mark:
        today = datetime.date.today().isoformat()
        for path in mark_done(args.ledger, ledger, args.wave, args.progress, today, result):
            print(f"Wrote {path}")
        try:
            synced = sync_codemap(repo, args.base)
        except CheckpointError as e:
            print(f"warning: codemap sync failed: {e}", file=sys.stderr)
            return 0
        if synced is not None:
            print(f"Codemap: {synced[0]} pending ({synced[1]})")
            print(f"Wrote {os.path.join(repo, '.claude', 'codemap', 'pending.md')}")
    return 0


def main(argv: list, cwd: str | None = None) -> int:
    """Run the CLI. `cwd` exists for tests: it sets where git runs and where a
    relative `--log` resolves; the ledger path and `--progress` are resolved by the caller."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args = _build().parse_args(argv)
    try:
        return _run(args, cwd)
    except (LedgerError, CheckpointError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
