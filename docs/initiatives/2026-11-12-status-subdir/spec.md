# tech-lead 0.3.2: status from a subdirectory session (B19) — design

Date: 2026-11-12

## Problem

`status.py` takes the project root from its argument, else `$CLAUDE_PROJECT_DIR`, else the working directory. A session started in a subdirectory (for example `topology/` in the dom-z-widokiem repository, which has its own `.claude/settings.json`) gets that subdirectory as `CLAUDE_PROJECT_DIR`, while `docs/initiatives/`, `docs/backlog.md`, `docs/STATUS.md` and `.claude/codemap/` live at the repository's top level. The SessionStart brief then sees no initiatives and stays silent; the full status reports "No initiatives yet."

## Decision

- New function `status.resolve_root(root: Path) -> Path`: return `root` when `root/docs/initiatives/` is a directory; otherwise, when `git -C <root> rev-parse --show-toplevel` succeeds and the top level has `docs/initiatives/` as a directory, return the top level; otherwise return `root` unchanged.
- `main` applies it to the root it computed, for every mode (full, `--write`, `--brief`). An explicit `ROOT` argument is resolved the same way.
- Everything downstream (initiatives, backlog, `docs/STATUS.md`, codemap health, absolute paths printed) uses the resolved root, so a subdirectory session sees and writes the repository-level files.
- Safety: the git call reuses the existing `_git` helper with a new `timeout` parameter (5 s here, default unchanged), with `GIT_DIR` and `GIT_WORK_TREE` removed from its environment; `OSError` (git missing), `subprocess.TimeoutExpired` and a non-zero exit (`RuntimeError` from `_git`) all keep `root`: catch exactly `(OSError, subprocess.TimeoutExpired, RuntimeError)`; `--brief` stays silent on every error as before. No other behaviour change.
- An explicit `ROOT` with `--write` writes `docs/STATUS.md` at the resolved root (documented). When a subdirectory has its own `docs/initiatives/`, everything, codemap health included, stays at that subdirectory.
- SKILL.md's line "`ROOT` defaults to the project directory" says it falls back to the repository top level when the project directory has no `docs/initiatives/`.
- README: one sentence that the status works from a session started in a subdirectory of the repository.
- Version 0.3.2.

## Tests

- A temporary git repository with `docs/initiatives/<x>/journal.md` at the top level: `resolve_root(top/sub)` returns `top`; the CLI run with `CLAUDE_PROJECT_DIR=top/sub` and `--brief` prints the brief naming the top-level initiative path.
- `root` with its own `docs/initiatives/` is returned unchanged even inside a repository whose top level also has one.
- Not a git repository and no `docs/initiatives/` (real `git` exits non-zero, `_git` raises `RuntimeError`): `root` unchanged; `--brief` prints nothing.
- Top level without `docs/initiatives/`: `root` unchanged.
- git failing: with the git call patched to raise `FileNotFoundError`, and separately `subprocess.TimeoutExpired`, `resolve_root` returns `root`, and `--brief` prints nothing and exits 0.
