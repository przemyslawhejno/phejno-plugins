# Hygiene candidates 2 (tech-lead, changes since fef3c56)

Read-only inventory. Nothing was changed except this report.
Method: read the diff since fef3c56 for tech-lead/scripts and tech-lead/tests; grepped the test tree; ran the HEAD tests against the fef3c56 scripts (in a scratch copy from git archive) to find coverage-only tests; timed each file and class. No `.claude/codemap/INDEX.md` exists, and neither vulture nor knip is installed, so no dead-code scan was run.

## Counts

| Kind | Count |
| --- | --- |
| obsolete | 1 |
| duplicate | 4 |
| dead | 0 |
| comment | 1 |
| slow | 3 |

## Candidates

### obsolete
- tech-lead/tests/test_packaging.py:37 — `assertEqual(d["version"], "0.2.1")` hard-codes the version. It breaks on every bump and is already covered by the equality check between the plugin and marketplace manifests.

### duplicate
- tech-lead/tests/test_ledger_cli.py:487 `test_missing_argument_one_line` — same one-line `error:` shape as the existing `test_usage_error_one_line` (line ~127). Could be merged into one parameterised check.
- tech-lead/tests/test_ledger_cli.py:490 `test_non_integer_wave_one_line` — same shape again; also overlaps `test_checkpoint_errors`.
- tech-lead/tests/test_status.py:690-705 `test_import_failure_full_errors_and_brief_is_silent` — the same `mock.patch.object(status, "_load_core", ...)` plus redirect block is written three times. Extract a helper.
- tech-lead/tests/test_ledger_checkpoint.py:428 `test_first_failing_exit_code_wins` — likely overlaps the existing `test_failing_verify` (line 72), which exercises the same `run_cp` failure path. Not confirmed by reading the existing body.

### dead
- None found. Every new helper (`_field_errors`, `_risk_lens_errors`, `_hygiene_errors`, `_cell`, `_load_core`) has a caller. No dead-code tool is available.

### comment
- tech-lead/scripts/ledger_checkpoint.py:145 — the new docstring on `mark_done` restates what the body does. Low value; drop or keep as a one-liner.

### slow (subprocess tests that could run in process via `ledger.main([...])`)
- tech-lead/tests/test_ledger_cli.py:487 `test_missing_argument_one_line` (subprocess)
- tech-lead/tests/test_ledger_cli.py:490 `test_non_integer_wave_one_line` (subprocess)
- tech-lead/tests/test_ledger_cli.py:503-ish `test_unknown_wave_one_line` (subprocess, needs a repo)

## Checks on the known items

- Timing-based stdin test (`test_stdin_is_closed`): removed. Replaced by a mock-based `test_commands_run_with_stdin_closed`. Confirmed gone.
- Duplicate instruction-line assertion: removed from `CodemapTests` (`lines[-1].startswith("Propose next steps")`). The same assertion still exists at tech-lead/tests/test_status.py:217 in a different test (line cap). Not a duplicate of the removed one. Confirmed removed.
- Ad hoc per-column escaping in `render_show`: removed. Replaced by `_cell`/`_esc` in tech-lead/scripts/ledger_report.py. Confirmed gone.
- Duplicate risk-vocabulary guard: not found in the diff (no removal visible). Still present at tech-lead/tests/test_skill_docs.py:51 (`"`risk`: any of"`) and tech-lead/tests/test_prompts.py:87. Unconfirmed; check whether the test_skill_docs string guard duplicates the RISKS checks in test_ledger_core.py. Not counted.

## Coverage-only tests (pass on the fef3c56 scripts)

Run of HEAD tests against fef3c56 scripts. These pass on the old code, so they add coverage only:
- test_ledger_checkpoint.py: `test_commands_run_with_stdin_closed`, `test_log_truncated_on_rerun`, `test_lead_task_verify_is_skipped`, `test_first_failing_exit_code_wins`, `test_only_requested_wave_runs`
- test_ledger_cli.py: `test_missing_argument_one_line`, `test_non_integer_wave_one_line`, `test_relative_log_resolved_to_absolute`, `test_unknown_wave_one_line`, `test_show_in_non_utf8_locale`, `test_help_exits_zero`
- test_ledger_core.py: `test_ui_tasks_count_toward_hygiene_threshold`
- test_ledger_report.py: `test_empty_task_list_renders_sections`, `test_share_rounds_half_up`
- test_status.py: `test_waves_failure_marks_only_that_initiative`

Old-code failures (good, behaviour tests): `test_abbreviated_option_rejected`, `test_missing_git_reports_not_installed`, `test_schema_must_be_int_two`, `test_cells_stay_on_one_row`, plus `test_import_failure_full_errors_and_brief_is_silent` (needs `_load_core`).
The packaging, prompt and skill-doc tests errored on the old copy only because the scratch copy lacks the skills directory. They were not evaluated.

## Other finding (not a kind)
- tech-lead/tests/test_ledger_cli.py:13 — `import ledger` runs before `from helpers import ...` (which adds scripts/ to sys.path). Running this file alone fails with `ModuleNotFoundError: No module named 'ledger'`. The full suite passes (156 tests, OK). Move the import below `helpers`, or import `helpers` first.

## Timings

Per file (wall, one run each, includes interpreter startup ~0.05 s):

| File | Wall | Result |
| --- | --- | --- |
| test_status.py | 0.42 s | OK |
| test_ledger_checkpoint.py | 0.37 s | OK |
| test_ledger_core.py | 0.07 s | OK |
| test_ledger_report.py | 0.07 s | OK |
| test_packaging.py | 0.06 s | OK |
| test_prompts.py | 0.06 s | OK |
| test_skill_docs.py | 0.05 s | OK |
| test_ledger_cli.py | 0.09 s | ERROR alone (import order, see above) |

Full suite: 156 tests OK in 2.08-2.16 s (ratchet 1.45 s for 136 tests).

Slowest classes (in-process timing, summed over tests):
- test_ledger_cli.CliTest 1.27 s
- test_ledger_checkpoint.CheckpointTests 1.09 s
- test_status.CodemapTests 0.26 s
- test_status.StatusTests 0.23 s
- test_ledger_checkpoint.CodemapSyncTests 0.13 s

Slowest tests:
- test_ledger_checkpoint.CheckpointTests.test_durations_formatted 0.16 s
- test_ledger_cli.CliTest.test_checkpoint_mark_reports_codemap_only_when_present 0.15 s
- test_ledger_cli.CliTest.test_checkpoint_errors 0.11 s
- test_ledger_cli.CliTest.test_check_valid_and_invalid 0.11 s
- test_ledger_cli.CliTest.test_next_and_all_complete 0.10 s
- test_ledger_cli.CliTest.test_abbreviated_option_rejected 0.08 s
- test_ledger_cli.CliTest.test_checkpoint_mark_end_to_end 0.07 s
- test_ledger_cli.CliTest.test_unknown_wave_one_line 0.07 s

The CLI and checkpoint classes make up most of the suite time. The slow candidates above are the subprocess-heavy CLI tests.
