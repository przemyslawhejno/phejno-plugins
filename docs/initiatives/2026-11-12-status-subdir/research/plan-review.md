# Plan review: status from a subdirectory (B19)

Verdict basis: spec and plan read against status.py, SKILL.md, hooks.json, ledger.py.

## Important

1. Plan Task 1 / spec Tests: Review Focus 2 (`--brief` silent when git is missing, slow or failing) has no test. Add a test that makes the git call raise (empty PATH, or patch `subprocess.run` to raise `TimeoutExpired` and `FileNotFoundError`) and asserts `resolve_root` returns `root` and `main(["--brief"])` prints nothing, exit 0.
2. Spec Decision / Safety: the git call must catch `OSError` and `subprocess.TimeoutExpired` (not only a nonzero return) and strip `GIT_DIR`/`GIT_WORK_TREE`. `_git` does the stripping but has a fixed 10 s timeout and raises on failure; reuse it with a `timeout` parameter (default 10, pass 5) rather than a second subprocess helper. State the catch explicitly so a TimeoutExpired cannot escape `main` in the non-brief modes either.

## Minor

1. SKILL.md line 205 says "`ROOT` defaults to the project directory"; adjust to "the project directory, or the repository top level when that has the initiatives". Add SKILL.md to Task 1 files (check `test_skill_docs.py`).
2. Explicit `ROOT` plus `--write`: a subdirectory passed as ROOT now writes `docs/STATUS.md` at the top level when it has no `docs/initiatives/` itself. Intended per spec, but say so in the README sentence.
3. When a subdirectory keeps priority (own `docs/initiatives/`), codemap health still reads `<subdir>/.claude/codemap`, while `ledger.py checkpoint` writes `pending.md` at the git top level. Mismatch is pre-existing; note it or add the top level as a codemap fallback later.
4. Only the git top level is probed, not intermediate directories (monorepo `pkg/` with its own docs). Submodules and nested repos resolve to their own toplevel (correct, no climbing into a superproject); worktrees resolve to the worktree root (correct). Add one line to the spec saying so; no test needed.
5. `show-toplevel` returns a realpath while `root` is `abspath`; a symlinked project dir prints a different path in the brief. Harmless; tests already use realpath.
6. Plan says 169 tests, standards.md says 166; update the ratchet after the change.

Other checks: coverage (R1, R2 to Task 1), single task, wave order, model/effort (sonnet/medium) and verify command are adequate; no hygiene task required (one code task, no `replaces`); no lenses needed. Fast path is good: a root with its own `docs/initiatives/` spawns no git process. The four specified tests are writable with the shared-repo helpers (`init_repo`, `clean_env`).

PLAN NEEDS CHANGES
