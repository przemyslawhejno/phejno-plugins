# Hygiene candidates 4: tech-lead plugin since 48c6f2e

Scope: changes in `tech-lead/` since commit 48c6f2e (ledger schema 2, checkpoint timings, codemap health and sync, report columns, prompt and lens docs). Test roots: `tech-lead/tests/`. Code roots: `tech-lead/scripts/`. Read only; nothing was changed except this report.

Tooling: `vulture` and `knip` are not installed, so no dead-code tool ran. `.claude/codemap/` does not exist in the repository, so search used Grep. Dead-code search was a reference count of every `def` across scripts and tests.

Counts: obsolete 2, duplicate 8, dead 1, comment 3, slow 4.

## Obsolete

1. `tech-lead/tests/test_skill_docs.py:55-58`: `REQUIRED_IN_SKILL` entries `"risk"`, `"experts"`, `"hygiene"`, `"ui-ux"` are bare words. They pass if the word appears anywhere in SKILL.md, so they assert nothing about the schema 2 behaviour they were added for. Replace with the rule text, or drop them.
2. `tech-lead/tests/test_packaging.py:85`: `test_readmes` checks bare words `"lenses"`, `"hygiene"`, `"schema"`, `"codemap"` in README.md. Same problem: any mention passes. Replace with the sentence the README must contain.

## Duplicate

1. `tech-lead/tests/test_ledger_checkpoint.py:83-88` (`test_durations_formatted`) and `tech-lead/tests/test_ledger_cli.py:97-102` (`test_checkpoint_prints_durations`): the same `Task N: pass (N.Ns)` and `Checks: pass (N.Ns)` format, asserted at unit and CLI level. Keep one (the unit test) and drop the CLI regex pair, or keep the CLI test only for the wiring.
2. `tech-lead/tests/test_status.py:126`, `:210` and `:279`: the same "brief ends with the Propose next steps instruction" assertion is repeated in three tests. Keep the check in `test_brief_limit_and_instruction` and drop the other two.
3. `tech-lead/tests/test_prompts.py:47`, `:50` and `:60`: the severity words `Critical`, `Important`, `Minor` are asserted in three prompt tests (batch review, plan review, lens review). Move them into one table-driven test over the three files.
4. `tech-lead/tests/test_skill_docs.py:58-59` (`` `unknown` ``, `` `brief` ``, `` `context` ``, `` `plan` ``, `` `capability` `` and `` `unknown` ``) and `:146` (`test_failure_causes_in_escalation`): the same five escalation causes are checked twice in one file. The Escalation-scoped test is the stronger one. Remove the five entries from `REQUIRED_IN_SKILL`.
5. Code duplicate, codemap thresholds: `tech-lead/scripts/status.py:25-26` (`CODEMAP_UPDATE_MIN = 16`, `CODEMAP_REBUILD_MIN = 51`) and `tech-lead/scripts/ledger_checkpoint.py:50-51` (`CODEMAP_INLINE_MAX = 15`, `CODEMAP_UPDATE_MAX = 50`) encode the same pending-count rule. The constants agree today only by convention. Define them once in one module and import them. The boundary tests (`test_ledger_checkpoint.py:262-264`, `test_status.py:102-107`) would then share one source.
6. Unit and CLI test of the same rule, bad base: `tech-lead/tests/test_ledger_checkpoint.py:104-107` (`test_bad_base_raises`) and `tech-lead/tests/test_ledger_cli.py:127-131` (the `nope` base case in `test_checkpoint_errors`). Keep both only if the CLI check is about the one-line stderr format; otherwise drop the CLI case.
7. Helper code, git test setup: `git()` in `tech-lead/tests/test_ledger_checkpoint.py:17-20`, `_git()` in `tech-lead/tests/test_status.py:50-54`, `git()` and `make_repo()` in `tech-lead/tests/test_ledger_cli.py:25-38`, and the repo init block (`init`, `config user.email`, `config user.name`, `config commit.gpgsign`) repeated at `test_ledger_checkpoint.py:39-42` and `:218-221`, and `test_status.py:62-65`. Also the `GIT_DIR`/`GIT_WORK_TREE` env filter is repeated in `test_ledger_checkpoint.py:18`, `test_status.py:51`, `test_status.py:230-231` and `test_ledger_cli.py:17`. Move one `git` helper, one `make_repo` and one `clean_env` into `tests/helpers.py`.
8. Code duplicate, empty wave guard: `tech-lead/scripts/ledger_checkpoint.py:95-96` (in `run_checkpoint`) and `:156-157` (in `mark_done`) raise the same "wave N has no tasks" error. Keep one check, or let `mark_done` rely on `run_checkpoint` having run first in the CLI path.

## Dead

1. `tech-lead/tests/test_ledger_checkpoint.py:212-264`: `class CodemapSyncTests` is defined after the `if __name__ == "__main__": unittest.main()` guard at lines 208-209. Running the file as a script (`python3 tests/test_ledger_checkpoint.py`) calls `unittest.main()` before the class exists, so these four tests never run that way. Discovery still finds them. Move the class above the guard.

## Comment (names that record history)

1. `tech-lead/tests/test_ledger_core.py:159`: `test_schema_absent_keeps_v1_rules`. The name records the schema 1 and 2 history rather than the behaviour. Suggested: `test_no_schema_field_skips_schema2_rules`.
2. `tech-lead/tests/test_ledger_core.py:251`: `test_finished_v1_initiative_ledger_valid`. The name records history, and the test depends on a real initiative file (`docs/initiatives/2026-11-11-tech-lead/ledger.json`) that will keep changing. Suggested: a fixture copied into the tests, named by behaviour.
3. `tech-lead/tests/test_ledger_report.py:49`: `test_v1_ledger_renders_dashes_and_none`. Same history-in-name problem. Suggested: `test_ledger_without_risk_or_experts_renders_dashes`.

Other notes (not counted): `tech-lead/tests/test_ledger_checkpoint.py:85-86` calls `m.group(1)` without a None check, so a format change gives an AttributeError instead of a clear failure. Use `self.assertIsNotNone(m)` first.

## Slow

Measured per test with `unittest` timing on this machine. Full suite: 136 tests, about 2.0 s of test time, about 2.2 s wall.

Per file (wall time for `python3 -m unittest discover tests -p <file>`): `test_ledger_cli.py` 1.08 s, `test_ledger_checkpoint.py` 0.96 s, `test_status.py` 0.49 s, `test_ledger_core.py` 0.07 s, `test_ledger_report.py` 0.08 s, `test_skill_docs.py` 0.06 s, `test_packaging.py` 0.07 s, `test_prompts.py` 0.05 s. Most of the cost is subprocesses (git and Python).

1. `tech-lead/tests/test_status.py:66-72`, `CodemapTests.setUpClass`: builds 20 commits with 20 separate `git commit` subprocesses. Measured 0.12 s here (the brief cited about 0.65 s; the difference may be machine speed). One `git fast-import` stream would create the same history in one process.
2. `tech-lead/tests/test_ledger_checkpoint.py:35-53`, `CheckpointTests.setUp`: every one of the 17 tests runs `git init` and two commits. Build the repository once in `setUpClass` and give the two tests that mutate it (`test_non_ascii_declared_file_is_in_scope`, the codemap-free checkpoint runs) their own copy.
3. `tech-lead/tests/test_ledger_cli.py:77`, `:87`, `:98`, `:105` and `:130`: `make_repo` runs per test (`git init` plus a commit each time), on top of two to three `ledger.py` subprocesses per test. `test_checkpoint_errors` is the slowest CLI test at 0.15 s. Share one repository per class and copy it with `shutil.copytree` where a test writes files.
4. `tech-lead/tests/test_ledger_checkpoint.py:84`, `test_durations_formatted`: a real `sleep 0.2` in the verify command. It is the slowest test at 0.25 s. Keep it if the duration formatting must be tested end to end, otherwise assert against a fixed `CheckpointResult`.
