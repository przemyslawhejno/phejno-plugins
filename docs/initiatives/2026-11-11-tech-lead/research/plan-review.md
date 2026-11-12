# Plan review: tech-lead

Reviewer: independent, read-only. Inputs: spec.md, plan.md, ledger.json, model-manager conventions, the installed superpowers SDD skill.

## Blocking

B1. **Ruling lines are lost (Task 4, spec Journal).** SDD writes rulings as `Task <N>: Ruling: …` and `Task <N>: parked — … — Ruling: …`. SDD's own Finish step collects lines *containing* `Ruling:`. The plan copies only lines *starting* `Ruling:`/`Attempt:`, so most rulings never reach `journal.md`. Fix: in `mark_done`, copy lines that contain `Ruling:`, or that start with `Attempt:`. Add a `Task 2: Ruling: x` line to the `test_mark_done_*` fixtures. Fix the spec wording to match.

B2. **`--progress` has no default and the skill is never told to pass it (Tasks 5, 6).** The plan adds `--progress FILE` correctly. SDD's ledger lives at `<repo>/.superpowers/sdd/<slug>/progress.md`, and the slug can be disambiguated (`plan-<parent>`, `-2`), so it cannot be guessed. Every initiative's plan is called `plan.md`, so collisions are certain. If `SKILL.md` omits the flag, nothing is ever copied. Fix: in Task 6, require the exact invocation `ledger.py checkpoint LEDGER --wave W --base REF --progress "$(bash <sdd>/scripts/sdd-workspace PLAN)/progress.md" --mark`, and add `--progress`, `--wave` and `--base` to `test_mentions_required_items`. Record in the spec that `--progress` was added.

B3. **Task 6 cannot see the CLI contracts it consumes.** Subagents see only their own task text. Task 6 runs in wave 1, before `ledger.py`/`status.py` exist, yet it must write "exact invocations". Fix: copy a CLI synopsis (four ledger commands with all flags, and `status.py [ROOT] [--brief|--write]`) into Task 6. Also put the spec path into Global Constraints, because Tasks 6 and 7 are told to use spec sections they have no path to.

B4. **`test_skill_references_exist` is impossible or forces a spec violation (Task 8).** `SKILL.md` must name `spec.md`, `plan.md`, `journal.md`, `STATUS.md`, `backlog.md`, `standards.md`, `progress.md` and `plan-review.md`, and none of them sit next to `SKILL.md`. Fix: check only `layout.md` and the names matching `*-prompt.md`.

B5. **Review Focus 3 is half untested.** "Outside a git repository" and "ledger untouched" have no test. The `git rev-parse --show-toplevel` failure lives in Task 5 (not Task 4) and is the likeliest place for a traceback. Fix: add Task 5 `test_checkpoint_errors`: bad `--base`, and cwd in a non-git temp dir. Each gives exit 1, one `error:` stderr line, and a ledger byte-identical to before.

B6. **Spec testing step dropped (Task 9).** The spec requires running `/tech-lead:run` on a small sample spec up to the gate, including the mockup and a session start that proposes next steps. Task 9 does not do this. Fix: add it to Task 9 in a scratch project with the plugin installed from this checkout (this is a user-visible step if a new session is needed), and record the result in `journal.md`.

## Minor

M1. **Missing spec mentions in `SKILL.md` tests (Task 6).** Add `superpowers:test-driven-development`, `superpowers:requesting-code-review`, `security-review`, `engineering:architecture`, `modern-web-guidance`, `fable`, `backlog.md`, `research/plan-review.md` and `../../scripts/` to `test_mentions_required_items`. Add `docs/superpowers/`, `git mv` and `.worktrees/` to `test_layout_paths`. The migration offer should also appear in the Orient step. The words `brief`, `context` and `capability` pass trivially; assert `` `brief` ``, `` `context` `` and `` `capability` `` (with backticks) or the `Attempt: Task` format.

M2. **Task 7 Step 3 says "three prompt files"; there are four.**

M3. **Weak test (Task 2).** `test_brief_swallows_errors` can pass trivially when the code checks `is_dir()`. Also patch `render_brief` to raise and call `main(["--brief"])` in-process. In `status.py`, import `ledger_core` inside the guarded path, so that an import error under `--brief` also prints nothing.

M4. **Model for Task 2.** sonnet/low is underpowered. It has 12 tests, state ordering, truncation, env and CLI handling, and it is the hook that runs in every session. Use sonnet/medium. Other assignments are sound. Task 6 on opus/medium has a valid risk reason. No task fits haiku: Task 8 contains README prose, and Task 7 is prose without complete text. Leaving haiku unused is correct.

M5. **Duplicate log path (Tasks 4/5).** `format_result` prints `Log: <path>` and the CLI then prints `Wrote <log>`. Keep only `Wrote`. Also truncate the log at the start of each run, so that re-runs do not mix results.

M6. **argparse usage errors.** These exit 2 with multi-line stderr, which contradicts "one error line, exit 1". Override `ArgumentParser.error`.

M7. **Validation robustness (Task 1).** Skip waves and the conflict check also when ids are invalid or duplicated. Add `done: ["1"]` to `test_string_id_rejected` (Review Focus 2 names the mismatch with `done`). State whether `make_ledger` sets `covers=["R1"]` on a copy of `tasks[0]`, and how it treats `tasks=` overrides used by `test_wrong_types_do_not_raise`.

M8. **Temp git repos (Tasks 4, 5).** Commit with `-c commit.gpgsign=false`. Clear `GIT_DIR`/`GIT_WORK_TREE` from env. Compare paths via `os.path.realpath`: on macOS `/var` becomes `/private/var`, and `git rev-parse --show-toplevel` returns the resolved path.

M9. **Encoding.** `sys.stdout.reconfigure(encoding="utf-8")` in both CLIs. Otherwise non-UTF-8 consoles raise on Polish text, and `--brief` silently prints nothing. Python 3.9 compatibility is never exercised: the environment runs 3.13. Name banned constructs (`match`, `zip(strict=)`, runtime `X | Y` types) in Global Constraints.

M10. **Hook output form.** Plain stdout from a SessionStart hook does become context, so the plan works. model-manager emits `hookSpecificOutput.additionalContext` JSON; consider the same for consistency, and test whichever form is chosen.

M11. **Brief points at `docs/STATUS.md`, which may not exist yet.** Say "run status.py" when the file is missing.

M12. **Ledger requirements.** R10 does not mention the `.gitignore` entries or the migration offer. Add them, or add an R17 covered by Task 6.

## Checked and fine

Waves and file disjointness (1/6/7, 2/3/4, 5, 8, 9). `helpers.py` is imported via the discover start dir, does not match `test*.py`, and `tech-lead/tests` needs no `__init__.py` (say so). Script imports work via `sys.path[0]` when run as a script. `shell=True` with `exit N` is fine on POSIX. Review Focus items 1, 2, 4 and 5 have concrete tests. The `mode` field is validated. Autopilot and plan review are in Tasks 6 and 7.

PLAN NEEDS CHANGES

## Round 2

Scope: fix commit a9c5057 against round-1 findings.

- B1 resolved: "contains `Ruling:`" in plan Task 4 and spec; fixture now has `Task 2:` and parked forms.
- B2 resolved: `--progress` in spec table, Task 5 and Task 6 synopsis; `--progress`, `--wave`, `--base`, `sdd-workspace` in the skill test.
- B3 resolved: synopsis in Task 6; spec path in Global Constraints.
- B4 resolved: test limited to `layout.md` and `*-prompt.md`.
- B5 resolved: `test_checkpoint_errors` (non-git dir, bad base, ledger byte-identical).
- B6 resolved: dry-run step in Task 9.
- M1 partially: most mentions added; `backlog.md` and `research/plan-review.md` not in the test, and the migration offer in Orient is not asserted. Minor.
- M2 resolved. M3 resolved (patched `render_brief`, guarded import). M4 resolved (plan and ledger say sonnet/medium).
- M5 resolved (`Wrote` only, log truncated). M6 resolved (constraint plus `test_usage_error_one_line`). M7 resolved. M8 resolved. M9 resolved.
- M10 rejected by lead; the reason is valid (plain stdout is injected as context). Not reopened.
- M11 resolved by the alternative: the path is shown only when the file exists, with a test.
- M12 resolved (R10 extended, matching `test_layout_paths`).

New problems:

1. minor: Task 9 dry run says `claude -p --plugin-dir tech-lead` in a scratch git repository but writes the sample spec under `.tech-lead/scratch/sample/` of an unspecified repo. Fix: say the sample lives in the scratch repository, not in phejno-plugins, so the real tree stays clean.
2. minor: Task 6 `test_mentions_required_items` has `` `plan` `` and `` `brief` `` in backticks. Fix: make sure SKILL.md's `Attempt: Task N <model>/<effort> failed, cause <brief|context|capability|plan>, <note>` format uses exactly these backticked words.
3. minor: Task 2 `test_brief_swallows_errors` patches `status.render_brief`, so `main` must call it through the module attribute. Fix: add one clause to the Task 2 text.

No contradictions found between spec, plan and ledger; no test that cannot pass; Task 5 and Task 4 interfaces match (`Wrote` paths, `progress_path`).

PLAN APPROVED
