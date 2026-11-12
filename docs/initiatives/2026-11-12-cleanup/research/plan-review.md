# Plan review: tech-lead 0.2.1 cleanup

Ledger check passes (exit 0). Suite today: 137 tests, 1.225 s.

## Coverage
B2-B14 each map to a task: B2 -> 2/3/4, B3 -> 4, B4 -> 2, B5 -> 2, B6 -> 3, B7/B8/B9/B13 doc/B14 -> 5, B10/B12 -> 1, B11 -> 2, B13 tests -> 4/5. Recorded closures (B4 lead files, B5 help, B10 "remaining gaps", B9 README, B11 fix) have no explicit home: Task 7 only says "mark done or closed with reasons".

Spec decisions: B3 brief silence, B5 help kept, B14 single ratchet are sound. B11 mock is sound and runner-independent.

## Critical
None.

## Important
1. Task 5 (Files) and test_skill_docs.py: `tests/test_skill_docs.py` asserts required strings in SKILL.md/layout.md (`Suite time`, `Suite time:`, `Timing:`, `Lens yield`, section order, length). Task 5 rewrites exactly that wording (B14, B7 heading, B12) but does not own that file. Fix: add `tech-lead/tests/test_skill_docs.py` to Task 5 files, or state "keep these strings; do not edit that test". State the B14 edit concretely: `journal.md` keeps `Suite time:` as an event line that points to the ratchet; `standards.md` holds the value.
2. Task 2, non-UTF-8 locale test: Python 3.7+ coerces the C locale to UTF-8 and `ledger.main` already reconfigures stdout, so `LC_ALL=C` alone cannot fail and proves nothing. Fix: run in a subprocess with `LC_ALL=C`, `PYTHONUTF8=0`, `PYTHONCOERCECLOCALE=0`, `PYTHONIOENCODING` unset, a non-ASCII title, on a command that prints ledger text (`show`, or a `check` error). The implementer must confirm it fails when the `reconfigure` loop is removed, or drop it as an unfalsifiable guard and record that.
3. Task 2, missing-git test: "PATH without git" is under-specified. Fix: patch `ledger.subprocess.run` to raise `FileNotFoundError` in process (fast, no PATH or venv dependence); if a subprocess is used, call `sys.executable` by absolute path with `PATH` set to an empty directory. Name the command (`checkpoint`, since only it calls `_repo_root`). Note `_changed_files` still reports `git diff failed: ...` for OSError, which is intended.
4. Ledger `replaces` missing: Task 2 replaces the timing-based stdin test (the plan says so, yet Task 6 says "if still present"), Task 4 replaces the duplicate instruction-line assertion, Task 1 the duplicate risk guard, Task 3 the ad hoc `|` escapes. No task carries `replaces`. Fix: set `replaces` in the ledger for tasks 1-4 and drop the "if still present" hedge in Task 6.

## Minor (7)
1. Task 4 test: "patch the import" depends on `_core` design after the change. Fix: say "patch `status._load_core` (or whatever the single import function is) to raise ImportError; for the waves failure, patch `ledger_core.waves` to raise for one initiative's data".
2. Task 7 / Task 5: list the closures explicitly (B4 no code change, B5 help, B9 README, B10 gaps never written, B11 fix done) so the backlog notes are not improvised.
3. Task 5 `test_packaging`: hardcoding `0.2.1` goes stale next release; assert the two manifests agree and match `0.2.1` only in this initiative's check, or rely on the existing equality check.
4. Task 5 `test_prompts` 8-line limit: say how bullets of a lens checklist are delimited in `lenses.md` so the parse is deterministic.
5. Model/effort: Task 5 (four documents plus two tests, coupled to test_skill_docs) and Task 4 (import refactor with hook safety) could use `medium`; Tasks 1-3 and 6 are fine, Task 1 is not overspent.
6. Review Focus lacks: the Task 2 tests must fail without their fix (locale, stdin, abbrev); Task 5 must not break `test_skill_docs`; SKILL.md stays under 300 lines (currently 189).
7. Housekeeping: `standards.md` and the spec say 136 tests, the suite has 137; `tests/helpers.py` is unowned (a wave-1 conflict if two tasks edit it, say "do not edit"); the plan states no lane assignment for the two lanes (suggest 1+3+5 vs 2+4).

No wave-1 file overlap among Tasks 1-5. Hygiene task 6 depends on all code tasks as required. No risks or lenses are set, which fits routine work.

PLAN NEEDS CHANGES

## Round 2

Round-1 findings: I1 resolved (Task 5 owns test_skill_docs.py, B14 wording concrete). I2 resolved (flags, falsifiability stated). I3 resolved (in-process patch, command named). I4 resolved (`replaces` in plan and ledger tasks 1-4; Task 6 hedge dropped). M1 resolved. M2 resolved. M3 resolved. M4 resolved. M5 resolved. M6 resolved. M7 partly: lanes and helpers.py done; "136 tests" remains in the ratchet line, standards.md and the spec (plan now says 137 at start).

New findings:
- Minor: B14 journal format `Suite timed: <s>s` differs from the `Suite time:` string that test_skill_docs.py asserts; "Suite timed:" does not contain "Suite time:". Fix: Task 5 states which string each file must keep, or use `Suite time: <s>s ...` as the event line.
- Minor: the ledger `replaces` entries are prose, not testable; fine, but Task 6 should confirm each is gone.

No contradictions among spec, plan and ledger; no wave-1 file overlap; all tests are writable as specified.

PLAN APPROVED
