# Backlog check: tech-lead B2 to B14

Checked against `tech-lead/` at HEAD ed680e2 (plugin 0.2.0). No repository files were changed. Paths are repository-relative.

Status key: `open` = still true as written; `partly` = some part done, the rest listed; `done` = resolved (none qualifies in full, so `done` count is 0).

Estimate key: `mechanical` = exact edit obvious; `judgement` = the change needs a design decision or a new test design.

## Summary

| Item | Status | Remaining part |
|---|---|---|
| B2 | open | all CLI, checkpoint, show and status tests missing |
| B3 | open | single clear error still missing |
| B4 | open | lead-task scope and `mark_done` note still missing |
| B5 | open | all three parts still present |
| B6 | open | newline escaping missing in four list columns |
| B7 | open | three of four parts still present |
| B8 | partly | stronger `id` assertion and explicit `none` for `MOCKUP_PATH` |
| B9 | partly | packaging test does not check the scripts |
| B10 | open | annotations still missing |
| B11 | partly | stdin test does not fail without the fix |
| B12 | open | all five parts still present |
| B13 | partly | 8-line lens limit and duplicate assertion remain |
| B14 | open | both parts still present |

Counts: **open 9, partly 4, done 0.**

## Detail

| Item | Status | Location (file:line) | Change needed | Estimate |
|---|---|---|---|---|
| B2 | open | `tech-lead/tests/test_ledger_checkpoint.py:58-135` | Add tests for log truncation on re-run (`ledger_checkpoint.py:95` opens with `"w"`), lead-task `verify` skip (`ledger_checkpoint.py:85`), first failing exit code with several verify commands (`ledger_checkpoint.py:105-106`), and multi-wave selection (`ledger_checkpoint.py:83-88`). | judgement |
| B2 | open | `tech-lead/tests/test_ledger_report.py` (no empty-ledger test); `tests/test_ledger_report.py:69-77` covers only an exact 50% share | Add an empty-ledger `show` test and a rounding test for the share (`ledger_report.py:69`). | mechanical |
| B2 | open | `tech-lead/tests/test_ledger_cli.py:122-126` covers only `frobnicate` | Add CLI tests for a missing argument, bad `--wave` (non-integer), relative `--log` (`ledger.py:73-75`), an unknown wave, and a non-UTF-8 locale run (`ledger.py:97-101`). | judgement |
| B2 | open | `tech-lead/tests/test_status.py:165-169` | Add a test where `ledger_core.waves` fails for one initiative and check that `status.py` reports it (`status.py:83-93`). | judgement |
| B3 | open | `tech-lead/scripts/status.py:70-79` | `_core()` import and `load` sit inside `except Exception`, so an import failure sets `ledger_error` for every initiative. Import `ledger_core` once outside the per-initiative loop and raise one clear error line. | judgement |
| B3 | open | `tech-lead/scripts/status.py:98-99` | Stops showing `unknown (ledger error)` per initiative once the single error exists. | judgement |
| B4 | open | `tech-lead/scripts/ledger_checkpoint.py:85-89` | `allowed` is built from `members`, which excludes `lead` tasks. `ledger_core.py:247-248` already forbids files on lead tasks, so this is a documented-invariant question: state it in a comment or the docstring, or include lead files if they can exist. | judgement |
| B4 | open | `tech-lead/scripts/ledger_checkpoint.py:143-154` | `mark_done` writes `ledger["done"]` (line 154) into the dict it receives. Add a docstring saying the caller's ledger is mutated. | mechanical |
| B5 | open | `tech-lead/scripts/ledger.py:24` | `_Parser(prog="ledger.py")` needs `allow_abbrev=False` (argparse argument for `ArgumentParser`). | mechanical |
| B5 | open | `tech-lead/scripts/ledger.py:24-35` | `-h` uses argparse's default multi-line help and exit 0. Decide the one-line contract for help, then override it in `_Parser`. | judgement |
| B5 | open | `tech-lead/scripts/ledger.py:41-44` | A missing git binary raises `OSError`, caught and reported as "not a git repository". Report "git is not installed" for `OSError` separately. | mechanical |
| B6 | open | `tech-lead/scripts/ledger_report.py:7-8` | `_cell` joins list items with `<br>` but does not escape newlines inside items. Replace `\n` with a space in `_cell`, as `_esc` does. | mechanical |
| B6 | open | `tech-lead/scripts/ledger_report.py:39-41` | Columns 2, 3, 5, 6 and 8 (depends, files, risk, experts, acceptance) escape only `\|`, not `\n`. Route them through `_esc`. | mechanical |
| B7 | open | `tech-lead/skills/tech-lead/SKILL.md:47,52,53,146,188` | "integration branch" is used but never defined. Add a one-line definition in Process or Lanes. | mechanical |
| B7 | open | `tech-lead/skills/tech-lead/SKILL.md:66` | The ledger format block is a plain line under "## Process". Give it its own heading, `### Ledger format`. | mechanical |
| B7 | open | `tech-lead/skills/tech-lead/layout.md:189-191` | Duplicates `SKILL.md:161-163`. Remove the bullets here and keep the SKILL.md ones. | mechanical |
| B7 | partly | `tech-lead/skills/tech-lead/SKILL.md:17` | Says "load it before the first dispatch", but steps 2, 4 and 5 (lines 36-37, 41) dispatch subagents with no mention of the load. Add the load to those steps. | mechanical |
| B8 | partly | `tech-lead/skills/tech-lead/batch-review-prompt.md:10,13` | The generic `none` rule (line 13) exists, but `{{MOCKUP_PATH}}` is not stated as `none` for batches without UI tasks. Add that to line 10. | mechanical |
| B8 | partly | `tech-lead/tests/test_prompts.py:44` | The `"id"` check is a bare substring. Assert the `id` attribute pattern (for example `id="`) in `mockup-prompt.md`. | mechanical |
| B9 | partly | `tech-lead/README.md:57-59` | Done: the optional skills list includes `engineering:architecture`, `security-review` and `modern-web-guidance`. | none |
| B9 | partly | `tech-lead/tests/test_packaging.py:69-74` | `test_skill_references_exist` checks only prompt and lens file names. Add a check that `../../scripts/*.py` names in `SKILL.md:178-182` exist. | mechanical |
| B10 | open | `tech-lead/scripts/ledger_core.py:46,54,80-81,95,399` | Missing annotations: `_valid_id(x)`, `_normalised(p)`, the inner `wave_of(i)`, `_find_cycle(deps_of: dict)` (no return type), `next_wave` (no return type). Also `result: dict` at 80. | judgement |
| B10 | open | `tech-lead/tests/test_ledger_core.py` | "Remaining test gaps from the Task 1 review" are not listed in the repository, so they cannot be checked. Name them in the item first. | judgement |
| B11 | partly | `tech-lead/scripts/ledger_checkpoint.py:70` | Done: `stdin=subprocess.DEVNULL` is set. | none |
| B11 | partly | `tech-lead/tests/test_ledger_checkpoint.py:96-99` | The test does not fail without the fix on a runner whose stdin is already `/dev/null`. Make it fail without the fix, for example by starting the command with an open stdin pipe that is never closed, or by asserting the `stdin` argument of `subprocess.run`. | judgement |
| B12 | open | `tech-lead/scripts/ledger_core.py:293-367` | `_schema2_errors` is 75 lines. Split it by concern (per-task list fields, risk and lens rules, hygiene threshold). | judgement |
| B12 | open | `tech-lead/scripts/ledger_core.py:134` | `schema != 2` accepts `2.0` because `2.0 == 2`. Require `type(schema) is int`. | mechanical |
| B12 | open | `tech-lead/scripts/ledger_core.py:324-326` and `350-351` | Risk vocabulary is checked twice. Keep the check at 324-326 and drop the guard at 350-351 by moving the `RISK_LENSES` lookup behind it. | mechanical |
| B12 | open | `tech-lead/tests/test_ledger_core.py:237-242` | No test that `kind: ui` counts toward the hygiene threshold (`ledger_core.py:306-312`, `358-361`). Add one. | mechanical |
| B12 | open | `tech-lead/skills/tech-lead/SKILL.md:42` and `layout.md` | The lead-task interpretation of the hygiene threshold is not stated. Add one sentence: lead tasks do not count as `code`/`ui`. | mechanical |
| B13 | partly | `tech-lead/tests/test_ledger_checkpoint.py:82-84` | Done: `assertIsNotNone` (line 83) precedes `m.group(1)`. | none |
| B13 | partly | `tech-lead/scripts/ledger_checkpoint.py:68` | Done: `_run` is annotated `tuple[int, float]`, not bare `tuple`. | none |
| B13 | partly | `tech-lead/tests/test_status.py:134` and `218-219` | Instruction line is asserted in two tests (line 134 and lines 218-219). Keep one assertion per test. | mechanical |
| B13 | partly | `tech-lead/skills/tech-lead/lenses.md` and `tech-lead/tests/test_prompts.py:57-61` | The 8-line checklist limit is not written in any file. Current checklists have at most 5 bullets (security). Document the limit in `lenses.md` and assert it in `test_prompts.py`. | judgement |
| B14 | open | `tech-lead/skills/tech-lead/SKILL.md:47` and `:58`; `tech-lead/skills/tech-lead/layout.md:55` and `:115-118` | `Suite time` is written in two places: `journal.md` at first wave (SKILL.md:47), and `standards.md` at finish (SKILL.md:58, layout.md:55). Name one file for the value, and make the other a reference. | judgement |
| B14 | open | `tech-lead/skills/tech-lead/lenses.md:75`; `tech-lead/skills/tech-lead/layout.md:33` | The lens re-review writes no report path. Lens reports use `research/lens-<lens>-<wave>.md` (layout.md:33) with no re-review variant. Define the re-review report path (for example a `-fix-<n>` suffix) in `lenses.md` and `layout.md`. | judgement |

## Notes

- B1 was ignored as instructed.
- Several items were written against 0.1.0. Items that 0.2.0 resolved were checked and recorded as done or partly done above (B9 README, B11 stdin, B13 `m.group`, B13 bare `tuple`).
- Lead-task file scope (B4) is partly moot: `ledger_core.py:247-248` rejects files on lead tasks, so `allowed` excluding lead tasks is correct today. The `mark_done` documentation is still missing.
