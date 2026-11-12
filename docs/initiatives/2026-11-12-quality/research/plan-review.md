# Plan review: tech-lead 0.2.0 (hygiene, expert panels, UI/UX, codemap)

Reviewer: independent, read-only. Inputs: spec.md, plan.md, ledger.json (`ledger.py show`: 6 waves, check passes), current code and tests, and claude-codemap at the scratchpad checkout (README, commands/codemap.md, skills/codemap-usage, skills/codemap-format, hooks/track-changes.sh).

Overall the plan holds together. Spec coverage is complete (R1-R17 map to tasks), file ownership does not overlap within a wave, Tasks 5 and 10 are correctly serialized on `ledger_checkpoint.py`/`ledger.py`, and the plan's own ledger will validate under the schema 2 rules once Task 2 lands: 7 code tasks, and hygiene Task 8 depends on all of them. Model and effort are right in both directions: opus medium only for SKILL.md, sonnet low for the two narrow formatting tasks, sonnet medium elsewhere, and no lenses on this plan's own tasks, which is consistent with the rules.

## Blocking

**B1. Task 3 depends on code from a parallel task (Task 3, wave 1).** `test_lenses_cover_all` reads `ledger_core.LENSES`, but `LENSES` is created by Task 2, which runs in parallel in the other lane. In Task 3's worktree the attribute does not exist, so Task 3's own `verify` fails, and the implementer is likely to add `LENSES` to `ledger_core.py`, which is outside its files and conflicts with Task 2.
Fix: in Task 3, test against a literal tuple of the eight names, and add `test_lenses_match_core` (literal == `ledger_core.LENSES`) to Task 7, which depends on both. Alternatively, add `depends_on: [2]` to Task 3 so it moves to wave 2 next to Tasks 5 and 6.

**B2. Two codemap commands the plan proposes do not work as written (Spec Part 4 table, Task 10 `codemap_lines`).** I checked these against claude-codemap:
- `/codemap update` with no `pending.md` reports "Nothing pending. Index is up to date." and exits (commands/codemap.md, update step 2). The row "INDEX.md older than 30 days, 20+ commits" (commits made outside the hook, such as pulls) would therefore propose a command that does nothing.
- `rebuild` is not an argument. A full rebuild is plain `/codemap` (with no arguments, or with `--compact`/`--detailed`).

Fix: the "old index" row should propose `/codemap` (full rebuild), or `/codemap update` only when pending is greater than 0. The "stale" row should read `propose /codemap (full rebuild)`. Apply the same wording in SKILL.md (Task 4), and correct spec Part 4.

Everything else in Part 4 matches the plugin: the thresholds (≤15 inline, 16-50 update, >50 rebuild), the `Generated: YYYY-MM-DD` header in INDEX.md, `pending.md` holding one bare path per line, and the hook making absolute paths relative to `pwd`, which gives `.worktrees/...` entries for lane edits.

## Minor

1. **Global Constraints contradict Tasks 5 and 6.** "Existing tests that use 0.1.0-shaped ledgers keep passing unchanged" conflicts with assertions those tasks must change. `test_failing_verify` asserts `Task 1: fail (exit 3)` and `test_failing_check` asserts `(exit 2)`; both stop being substrings once times are added. `test_wave_tables` asserts the old header. Fix: limit the constraint to validation results, and name these three edits in Tasks 5 and 6 (switch to prefix asserts and the new header). Also state what `Checks: pass` shows when `checks` is empty.
2. **A haiku task with a risk cannot pass (Task 2).** "Each risk needs a lens" and "haiku takes no experts" cannot both be satisfied. Fix: add the rule `task N: haiku task cannot carry risk '<r>'` and skip the lens rules for that task. Also state whether the hygiene dependency must be direct; the current wording implies direct.
3. **Task 4 cannot see placeholders that Task 3 invents.** `inventory-prompt.md` uses `{{CHANGES}}`, `{{TEST_ROOTS}}` and `{{CODE_ROOTS}}`, and the batch review gains `{{CANDIDATES_PATH}}`. Neither is in the spec, and Task 4 runs in parallel. Fix: list both prompts' placeholders in Task 4's text. Also add `engineering:tech-debt`, `simplify` and `Lens yield` to Task 4's required terms, so the periodic audit, the hygiene pass's `simplify` and the yield flag are tested.
4. **Task 8's input file is misnamed.** The input is `research/hygiene-candidates-4.md`, but wave 4 (Task 7) has no `replaces` and adds no test file, so no rule produces that file. Fix: "Before wave 5 the lead dispatches the inventory (haiku low) over all initiative changes into `research/hygiene-candidates-5.md`." Name that path in Task 8.
5. **Task 8's acceptance is stricter than the spec, and its scope is narrower.** Task 10 adds tests that build git repos with about 20 commits, which can push per-test time past +20% and the total past +2 s for reasons cleanup cannot fix. The spec allows a `[hygiene]` backlog item with both numbers; add that fallback. `verify` (the suite only) does not prove the timing either: require the three timings in the report. The spec sets hygiene `files` to the union of the code tasks' files, but Task 8 excludes `skills/*.md` and the READMEs. Either widen it or record that exclusion as a ruling.
6. **`sync_codemap` should also drop `.claude/codemap/` paths, as the hook does.** Otherwise a committed index update re-enters `pending.md`. It should also state how deleted paths from `git diff` are handled (`--diff-filter=d`, or keep them so update can drop them).
7. **Task 10's brief and full status are underspecified.** The plan does not say whether the codemap line appears when there are no initiatives; `test_brief_silent_without_initiatives` currently requires silence. `## Codemap` in the generated `docs/STATUS.md` also changes with commit counts. Specify both, for example: brief codemap line only when the brief is otherwise non-empty.
8. **Some `verify` commands do not run the whole suite.** Tasks 3, 4 and 6 run one test file. The full suite takes 1.6 s, and Task 6 changes `render_show`, which `test_ledger_cli` also exercises. Use the full suite.
9. **Task 1's lead commit shows up as out of scope.** `docs/standards.md` will appear as `Out of scope` in the wave 1 checkpoint, because lead task files are not in `allowed`. Commit it before taking the wave base, or note that this line is expected.
10. **Task 7 waits longer than it needs to.** It needs Task 10 only for README prose, which is in the spec. With `depends_on [2,3,4,5,6]` it runs in wave 3 alongside Task 10 and saves one wave.

PLAN NEEDS CHANGES
