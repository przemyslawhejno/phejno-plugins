"""Wave checkpoint: run verification, flag out-of-scope changes, mark waves done."""
from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field

from ledger_core import codemap_action, paths_overlap, waves


class CheckpointError(Exception):
    pass


@dataclass
class CheckpointResult:
    tasks: list = field(default_factory=list)
    checks: list = field(default_factory=list)
    out_of_scope: list = field(default_factory=list)
    log_path: str = ""

    @property
    def passed(self) -> bool:
        return all(c == 0 for _, c, _ in self.tasks) and all(c == 0 for _, c, _ in self.checks)


def out_of_scope(changed: list, allowed: list) -> list:
    return [c for c in changed if not any(paths_overlap(c, a) for a in allowed)]


def _git_env() -> dict:
    return {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}


def _changed_files(base: str, repo: str) -> list:
    try:
        p = subprocess.run(["git", "-c", "core.quotepath=false", "diff", "--name-only", "-z",
                            f"{base}..HEAD"], cwd=repo,
                           capture_output=True, env=_git_env())
    except OSError as e:
        raise CheckpointError(f"git diff failed: {e}")
    if p.returncode != 0:
        err = p.stderr.decode("utf-8", "replace").strip().splitlines()
        raise CheckpointError("git diff failed: " + (err[0] if err else f"exit {p.returncode}"))
    return [l for l in p.stdout.decode("utf-8", "replace").split("\0") if l]


CODEMAP_IGNORED = (".worktrees/", ".claude/codemap/")


def sync_codemap(repo: str, base: str):
    pending = os.path.join(repo, ".claude", "codemap", "pending.md")
    if not os.path.isdir(os.path.dirname(pending)):
        return None
    lines = [l.strip() for l in _read(pending).splitlines()] + _changed_files(base, repo)
    unique = list(dict.fromkeys(
        l for l in lines if l and not l.startswith(CODEMAP_IGNORED)))
    try:
        with open(pending, "w", encoding="utf-8", newline="\n") as f:
            f.write("".join(l + "\n" for l in unique))
    except OSError as e:
        raise CheckpointError(f"cannot write {pending} ({e.strerror or e})")
    return len(unique), codemap_action(len(unique))


def _run(command: str, repo: str, log) -> tuple[int, float]:
    start = time.monotonic()
    p = subprocess.run(command, shell=True, cwd=repo, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    seconds = time.monotonic() - start
    out = p.stdout.decode("utf-8", "replace")
    log.write(f"$ {command}\n{out}")
    if out and not out.endswith("\n"):
        log.write("\n")
    log.write(f"exit {p.returncode}\n")
    return p.returncode, seconds


def run_checkpoint(ledger: dict, wave: int, base: str, repo: str,
                   log_path: str) -> CheckpointResult:
    tasks = ledger.get("tasks", [])
    wave_of = waves(tasks)
    members = sorted((t for t in tasks if wave_of[t["id"]] == wave and t.get("model") != "lead"),
                     key=lambda t: t["id"])
    if not any(wave_of[t["id"]] == wave for t in tasks):
        raise CheckpointError(f"wave {wave} has no tasks")
    allowed = [f for t in members for f in t.get("files", [])]
    changed = _changed_files(base, repo)
    result = CheckpointResult(out_of_scope=out_of_scope(changed, allowed),
                              log_path=os.path.abspath(log_path))
    try:
        os.makedirs(os.path.dirname(result.log_path), exist_ok=True)
        log = open(result.log_path, "w", encoding="utf-8")
    except OSError as e:
        raise CheckpointError(f"cannot write log {result.log_path}: {e.strerror or e}")
    try:
        for t in members:
            first_failure = 0
            total = 0.0
            for cmd in t.get("verify", []):
                code, seconds = _run(cmd, repo, log)
                total += seconds
                if code != 0 and first_failure == 0:
                    first_failure = code
            result.tasks.append((t["id"], first_failure, total))
        for cmd in ledger.get("checks", []):
            code, seconds = _run(cmd, repo, log)
            result.checks.append((cmd, code, seconds))
    except OSError as e:
        raise CheckpointError(f"cannot write log {result.log_path}: {e.strerror or e}")
    finally:
        log.close()
    return result


def format_result(result: CheckpointResult) -> str:
    lines = []
    for i, code, sec in result.tasks:
        lines.append(f"Task {i}: pass ({sec:.1f}s)" if code == 0
                     else f"Task {i}: fail (exit {code}, {sec:.1f}s)")
    failed = [(c, x, s) for c, x, s in result.checks if x != 0]
    if not failed:
        lines.append(f"Checks: pass ({sum(s for _, _, s in result.checks):.1f}s)")
    for c, x, s in failed:
        lines.append(f"Check failed: {c} (exit {x}, {s:.1f}s)")
    for p in result.out_of_scope:
        lines.append(f"Out of scope: {p}")
    return "\n".join(lines)


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except (OSError, UnicodeDecodeError) as e:
        raise CheckpointError(f"{path}: cannot read ({e})")


def mark_done(ledger_path: str, ledger: dict, wave: int, progress_path, today: str,
              result=None) -> list:
    """Mark the wave's tasks done in the ledger dict passed in, then write ledger and journal."""
    tasks = ledger.get("tasks", [])
    wave_of = waves(tasks)
    ids = sorted(t["id"] for t in tasks if wave_of[t["id"]] == wave)
    if not ids:
        raise CheckpointError(f"wave {wave} has no tasks")
    done = list(ledger.get("done", []))
    for i in ids:
        if i not in done:
            done.append(i)
    ledger["done"] = done

    ledger_path = os.path.abspath(ledger_path)
    journal_path = os.path.join(os.path.dirname(ledger_path), "journal.md")
    existing = _read(journal_path)
    seen = {l.strip() for l in existing.splitlines()}
    entry = [f"## {today} wave {wave}", "Tasks done: " + ", ".join(str(i) for i in ids)]
    if result is not None:
        parts = [f"Task {i} {sec:.1f}s" for i, _, sec in result.tasks]
        parts.append(f"checks {sum(s for _, _, s in result.checks):.1f}s")
        entry.append("Timing: " + ", ".join(parts))
    if progress_path:
        for raw in _read(progress_path).splitlines():
            line = raw.strip()
            if ("Ruling:" in line or line.startswith("Attempt:")) and line not in seen:
                seen.add(line)
                entry.append(line)
    text = existing
    if text and not text.endswith("\n"):
        text += "\n"
    if text:
        text += "\n"
    text += "\n".join(entry) + "\n"

    try:
        with open(ledger_path, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=2, ensure_ascii=False)
            f.write("\n")
        with open(journal_path, "w", encoding="utf-8") as f:
            f.write(text)
    except OSError as e:
        raise CheckpointError(f"cannot write ({e})")
    return [ledger_path, journal_path]
