READY

# Final review: tech-lead 0.3.2 status from a subdirectory (B19)

Scope: `git diff 8cca993..HEAD` on ccr-2b89ee94-nfyb7b, against spec.md, plan.md and docs/standards.md.
Suite: `python3 -m unittest discover tech-lead/tests` → 174 tests, OK, 1.113s (ratchet line 1.11s / 174 matches).
Manual check: `status.py --brief` run from `tech-lead/` (no CLAUDE_PROJECT_DIR) resolves to the repository top level and prints the in-progress initiative.

## Spec conformance

- `resolve_root`: own `docs/initiatives/` checked first and returned unchanged (subdirectory priority holds); git fallback catches exactly `(OSError, subprocess.TimeoutExpired, RuntimeError)`; 5 s timeout via the new `_git(timeout=)` parameter, default 10 s unchanged; `GIT_DIR`/`GIT_WORK_TREE` stripped by `_git`.
- Applied in `main` after `abspath` and `_load_core`, before the mode branch, so full, `--write`, `--brief` and an explicit ROOT all use it. A nonexistent ROOT makes `subprocess.run(cwd=...)` raise `FileNotFoundError`/`NotADirectoryError` (OSError) and keeps root.
- `--brief`: `TECH_LEAD_STATUS=0` returns before any git call; every other error is swallowed by the outer `except Exception` → exit 0, no output.
- Docs: SKILL.md ROOT line, README sentence, 0.3.2 in plugin.json and marketplace.json (plus the test_packaging pin, ruled in-scope in the journal), B19 closed in backlog, ratchet line, journal entries all present. STATUS.md matches the current `status.py` output.

## Edge cases

- Symlinks: when the fallback fires, the root becomes git's canonical top level (realpath) instead of the symlinked abspath, so the brief header and initiative paths print the real path. Consistent within one run (STATUS.md path, codemap `ls-files` cwd) and harmless; when the root has its own initiatives nothing changes.
- Worktrees: in `.worktrees/lane-N`, `--show-toplevel` returns the lane, which has its own checked-out `docs/initiatives/` anyway (first branch returns before git). Fine.
- Windows / non-UTF-8: Git for Windows prints `C:/...`, which `Path` accepts; an MSYS-style `/c/...` or a `replace`-decoded non-UTF-8 path fails the `is_dir` check and root is kept. Graceful.

## Findings

Critical: none. Important: none.

Minor
1. `test_git_failure_keeps_root_and_brief_silent`: the `main(["--brief"])` half is weak. `self.sub` has no initiatives, so the brief is empty whether or not `resolve_root` runs, and `--brief` swallows exceptions anyway; it also does not drop an inherited `TECH_LEAD_STATUS=0` (the `brief()` helper does), so in such an environment it passes trivially. The `resolve_root` assertion carries the test. Optional: clear `TECH_LEAD_STATUS` in the patch.dict.
2. `.strip()` on the `--show-toplevel` output would also drop leading/trailing spaces of a real directory name; `rstrip("\n")` is exact. Negligible in practice.
3. Plan said 169 tests; the suite has 174 (journal and standards record 174 correctly). Bookkeeping only.
4. Ledger shows task 2 not yet done and STATUS.md still says "waves 1/2"; mark wave 2 and rerun `status.py --write` after this review.
