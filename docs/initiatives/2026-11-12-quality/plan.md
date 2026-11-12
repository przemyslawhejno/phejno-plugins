# tech-lead 0.2.0 (hygiene, expert panels, UI/UX) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the `tech-lead` plugin to 0.2.0 with code and test hygiene, risk-scaled expert panels, UI/UX expertise and codemap integration, as the spec defines.

**Architecture:** Mechanics go into the existing stdlib modules: validation in `ledger_core.py`, timing in `ledger_checkpoint.py` and `ledger.py`, columns in `ledger_report.py`. Behaviour goes into the skill (`SKILL.md`, `layout.md`), one new reference file (`lenses.md`) and the prompt templates (two new, three updated). A hygiene pass over the plugin closes the work.

**Tech Stack:** Python 3.9+ stdlib, `unittest`, Markdown, JSON.

**Spec:** `docs/initiatives/2026-11-12-quality/spec.md`

**Ledger:** `docs/initiatives/2026-11-12-quality/ledger.json` (task ids match).

## Global Constraints

- Spec: `docs/initiatives/2026-11-12-quality/spec.md`. A task that names spec parts reads them there. The 0.1.0 spec is `docs/initiatives/2026-11-11-tech-lead/spec.md`.
- Python 3.9+ compatible: `from __future__ import annotations` in every module; no `match`, no runtime `X | Y` unions, no parenthesised multi-item `with`, no `zip(strict=...)`. Stdlib only.
- UTF-8 for every read and write; JSON with `indent=2`, `ensure_ascii=False`, trailing newline. Errors are one `error: <message>` line on stderr and exit 1, never a traceback. Every written file is announced as `Wrote <absolute path>`.
- Backward compatibility: every new ledger rule applies only when the ledger has `"schema": 2`. A ledger without `schema` validates exactly as in 0.1.0; existing tests that use 0.1.0-shaped ledgers keep passing unchanged.
- Hygiene (this repository's `docs/standards.md`, written by Task 1): comments only where the code cannot say it (why, a non-obvious constraint); no change history, no commented-out code, no restating code, no TODO without a backlog id. Remove what a change makes obsolete, in the same task. One behaviour, one test: extend or replace an existing test instead of adding a near-duplicate.
- No `model` or `effort` key in any skill or command frontmatter; nothing switches or suggests the main session's model.
- Plugin version `0.2.0` in `tech-lead/.claude-plugin/plugin.json` and the marketplace entry.
- Tests: `python3 -m unittest discover tech-lead/tests` from the repository root. Suite baseline: median 1.58 s for 91 tests (2026-11-12).
- Scripts are found from the skill as `../../scripts/` relative to the skill's base directory.

## Review Focus

1. A 0.1.0 ledger (no `schema`) with many tasks and no hygiene task must stay valid; the finished `docs/initiatives/2026-11-11-tech-lead/ledger.json` must still pass `ledger.py check`. Test in Task 2.
2. A lens name or risk given in a different case (`"Security"`) is rejected, not silently accepted. Test in Task 2.
3. Timing output keeps the existing pass/fail line prefixes (`Task N: pass`, `Task N: fail (exit X`), so earlier consumers and tests matching prefixes keep working. Test in Task 5.
4. `show` on a 0.1.0 ledger (no `risk`, `experts`, `kind`) renders `-` in the new columns and `Lens dispatches: none`. Test in Task 6.
5. The hygiene task's own edits are inside its declared `files`, so its checkpoint reports nothing out of scope. Checked by the checkpoint in Task 8.

---

## File structure

```
docs/standards.md                                   Task 1 (lead)
tech-lead/scripts/ledger_core.py                    Task 2
tech-lead/tests/helpers.py                          Task 2
tech-lead/tests/test_ledger_core.py                 Task 2
tech-lead/skills/tech-lead/lenses.md                Task 3 (new)
tech-lead/skills/tech-lead/lens-review-prompt.md    Task 3 (new)
tech-lead/skills/tech-lead/inventory-prompt.md      Task 3 (new)
tech-lead/skills/tech-lead/batch-review-prompt.md   Task 3
tech-lead/skills/tech-lead/plan-review-prompt.md    Task 3
tech-lead/skills/tech-lead/mockup-prompt.md         Task 3
tech-lead/tests/test_prompts.py                     Task 3
tech-lead/skills/tech-lead/SKILL.md                 Task 4
tech-lead/skills/tech-lead/layout.md                Task 4
tech-lead/tests/test_skill_docs.py                  Task 4
tech-lead/scripts/ledger_checkpoint.py              Task 5
tech-lead/scripts/ledger.py                         Task 5
tech-lead/tests/test_ledger_checkpoint.py           Task 5
tech-lead/tests/test_ledger_cli.py                  Task 5
tech-lead/scripts/ledger_report.py                  Task 6
tech-lead/scripts/status.py (+ checkpoint, ledger.py again) Task 10
tech-lead/tests/test_ledger_report.py               Task 6
tech-lead/.claude-plugin/plugin.json, README.md, tests/test_packaging.py, .claude-plugin/marketplace.json, README.md   Task 7
tech-lead/scripts/, tech-lead/tests/                Task 8 (hygiene pass)
```

Waves: 1 = Tasks 1, 2, 3, 4; 2 = Tasks 5, 6; 3 = Task 10; 4 = Task 7; 5 = Task 8; 6 = Task 9.

---

### Task 1: Project standards for this repository (lead)

The lead writes `docs/standards.md` following the spec's Part 1 (`Hygiene`, `Suite`, `Lens yield` sections): `Suite: python3 -m unittest discover tech-lead/tests`, `Suite time: 1.58s (2026-11-12, 91 tests)`, an empty `Lens yield` section, and `Checks:` empty (no linter in this repository). No `UI` section: this repository has no graphical interface.

---

### Task 2: Ledger schema 2 validation

**Files:**
- Modify: `tech-lead/scripts/ledger_core.py`
- Modify: `tech-lead/tests/helpers.py`
- Test: `tech-lead/tests/test_ledger_core.py`

**Interfaces:**
- Produces in `ledger_core.py`: `KINDS = ("code", "ui", "hygiene")`, `RISKS = ("security", "data", "irreversible", "system-wide", "ux")`, `LENSES = ("security", "data", "api", "architecture", "performance", "errors", "tests", "ui-ux")`, `RISK_LENSES: dict[str, tuple[str, ...]]` = `security: (security,)`, `data: (data,)`, `irreversible: (data, api, architecture)`, `system-wide: (architecture,)`, `ux: (ui-ux,)`; and `validate` applying the rules below when `ledger.get("schema") == 2`. `schema` present with any other value: `invalid schema '<v>'`.
- Produces in `helpers.py`: `make_ledger(..., schema=2)` is reached through the existing `**overrides`; new `make_hygiene(id: int, depends_on: list[int]) -> dict` (a valid sonnet/medium task with `kind="hygiene"`, `files=["src/", "tests/"]`, `verify=["true"]`).

Rules for schema 2 (messages are asserted by tests; `N` is the task id):

| Rule | Message |
|---|---|
| top-level `ui` not a boolean | `ui must be a boolean` |
| `kind` not in `KINDS` (non-lead tasks) | `task N: invalid kind '<v>'` |
| `risk`, `experts`, `replaces` not lists of strings | `task N: <field> must be a list of strings` |
| risk not in `RISKS` (exact case) | `task N: invalid risk '<v>'` |
| lens not in `LENSES` (exact case) | `task N: unknown lens '<v>'` |
| more than 4 lenses | `task N: more than 4 experts` |
| lenses on a `lead` task | `task N: lead tasks take no experts` |
| a risk without a matching lens (`system-wide` also matches `ui-ux` on a `kind: ui` task) | `task N: risk '<r>' needs one of the lenses <l1>, <l2>` (in `RISK_LENSES` order) |
| lenses on a haiku task, or a sonnet/low task with no risk | `task N: routine task takes no experts` |
| `kind: ui` while top-level `ui` is not `true` | `task N: kind 'ui' needs top-level ui: true` |
| `kind: ui` not on haiku without risk `ux` | `task N: ui task not on haiku needs risk 'ux'` |
| hygiene task missing when 3+ `code`/`ui` tasks, or 2+ such tasks and any has non-empty `replaces` | `missing hygiene task` |
| hygiene task not depending on a `code`/`ui` task | `task N: hygiene task must depend on task M` (one per missing M) |

`kind` defaults to `code`; `risk`, `experts`, `replaces` default to `[]`; `lead` tasks ignore `kind`.

- [ ] **Step 1: Write the failing tests** in `test_ledger_core.py`, one per rule above (`test_schema2_<rule>`), plus `test_schema_absent_keeps_v1_rules` (a 4-task ledger without hygiene and with an unknown lens is valid without `schema`), `test_invalid_schema`, `test_case_sensitive_lens_and_risk` (`"Security"` rejected in both), `test_system_wide_matches_ui_ux_on_ui_task`, `test_valid_schema2_ledger` (3 code tasks, a hygiene task depending on all, risks with matching lenses: `[]` errors), and `test_finished_v1_initiative_ledger_valid` (loads `docs/initiatives/2026-11-11-tech-lead/ledger.json` relative to the repository root and expects `[]`).
- [ ] **Step 2: Run** `python3 -m unittest discover tech-lead/tests -p 'test_ledger_core.py'` — expected FAIL on the new tests.
- [ ] **Step 3: Implement** the constants, the helper and the rules; keep 0.1.0 behaviour for ledgers without `schema`.
- [ ] **Step 4: Run** the same command, then the full suite — expected PASS.
- [ ] **Step 5: Commit** `tech-lead: ledger schema 2 validation`.

---

### Task 3: Lenses and prompts

**Files:**
- Create: `tech-lead/skills/tech-lead/lenses.md`, `lens-review-prompt.md`, `inventory-prompt.md`
- Modify: `batch-review-prompt.md`, `plan-review-prompt.md`, `mockup-prompt.md` (same directory)
- Test: `tech-lead/tests/test_prompts.py`

Content (source: spec Parts 1-3):
- `lenses.md`: one section per lens in `LENSES` order, each with a checklist of at most 8 lines and a "Uses when installed" line exactly as the spec's lens table and Part 3; a closing section on dispatch (one per lens per wave, explicit `model` and `effort` on the call, sonnet medium, opus medium for `security` and `architecture` with a risk and for `ui-ux` with risk `system-wide`, named agents only for tasks with a risk, the diff path given) and on yield (journal line format `Lens yield: <lens> <I> Important, <M> Minor`).
- `lens-review-prompt.md`, placeholders `{{LENS}}`, `{{TASKS}}`, `{{SPEC_PATH}}`, `{{STANDARDS_PATH}}`, `{{LENSES_PATH}}`, `{{CANDIDATES_PATH}}`, `{{REPORT_PATH}}`: review only through this lens; read the lens checklist in `{{LENSES_PATH}}`; read-only, run nothing (for `ui-ux`, read the harness output under `.tech-lead/scratch/`; say "not rendered" when absent); per task findings `Important` or `Minor` with file:line and fix; no questions to the user; write to `{{REPORT_PATH}}`, return its absolute path and counts per task.
- `inventory-prompt.md`, placeholders `{{CHANGES}}` (symbols, strings, behaviours changed or removed), `{{TEST_ROOTS}}`, `{{CODE_ROOTS}}`, `{{REPORT_PATH}}`: search the whole test tree for tests covering those, and the code tree for references to removed symbols; run a dead-code tool (`vulture`, `knip` or the stack's equivalent) only if already installed; list candidates (obsolete, duplicate, dead) with path:line and one-line reason; change nothing; write to `{{REPORT_PATH}}`, return its absolute path and the count.
- `batch-review-prompt.md`: add `{{CANDIDATES_PATH}}`; hygiene checks (obsolete code or test left, or a new test duplicating one in the diff or the candidates file: **Important**; noise comment: **Minor**); skip the mockup check for tasks that have the `ui-ux` lens.
- `plan-review-prompt.md`: checks that behaviour changes name `replaces`, planned tests do not duplicate existing ones, the hygiene task rule, risks and lenses both ways (missing lens on a risk, lens on routine work, a lens flagged in `standards.md` Lens yield chosen without a risk).
- `lens-review-prompt.md`, `inventory-prompt.md`, `batch-review-prompt.md`, `plan-review-prompt.md`: one line each — when `.claude/codemap/INDEX.md` exists, find code through `symbols.md` and `INDEX.md` before Glob or Grep (spec Part 4).
- `mockup-prompt.md`: the UI standards of spec Part 3 (WCAG 2.2 AA with the six criteria named, 2.5.8 over 2.5.5, states, responsive, tokens, `modern-web-guidance` when installed); after the UI/UX expert's review it is resumed to fix the findings.

- [ ] **Step 1: Write the failing tests** in `test_prompts.py`: `test_lenses_cover_all` (each name in `ledger_core.LENSES` is a heading in `lenses.md`), `test_lens_review_placeholders`, `test_inventory_placeholders_and_read_only` (contains `change nothing`), `test_batch_review_hygiene` (contains `{{CANDIDATES_PATH}}`, `obsolete`, `duplicat`, `ui-ux`), `test_plan_review_risk_and_hygiene` (contains `replaces`, `risk`, `hygiene`, `Lens yield`), `test_mockup_standards` (contains `WCAG 2.2`, `2.5.8`, `modern-web-guidance`), `test_codemap_navigation` (the four prompts named above contain `.claude/codemap/`). Keep the existing tests.
- [ ] **Step 2: Run** `python3 -m unittest discover tech-lead/tests -p 'test_prompts.py'` — expected FAIL.
- [ ] **Step 3: Write** the files.
- [ ] **Step 4: Run** the same command, then the full suite — expected PASS.
- [ ] **Step 5: Commit** `tech-lead: lenses, inventory and lens review prompts; hygiene and UI checks in prompts`.

---

### Task 4: Skill and layout for 0.2.0

**Files:**
- Modify: `tech-lead/skills/tech-lead/SKILL.md`, `tech-lead/skills/tech-lead/layout.md`
- Test: `tech-lead/tests/test_skill_docs.py`

Source: spec Parts 1-3 and "Changes by file". `SKILL.md` gains: the `Hygiene`, `Suite`, `Lens yield` and `UI` sections of `standards.md` in step 2; suite timing and the ratchet (first wave, finish, median of 3, the 20% per test and 2 s rule, 4-minute rule); the inventory step (when, haiku low, `inventory-prompt.md`, `research/hygiene-candidates-<wave>.md`); the hygiene pass rule; expert stages (architectural proposals, hard bugs with escalation cause `unknown`, lenses via `lenses.md` and `lens-review-prompt.md`, yield); UI/UX stages, the render harness and risk `ux`; codemap use and freshness (spec Part 4: navigation in the lead and in every brief, the `Codemap:` checkpoint line and the after-wave `/codemap update`, the finish update or rebuild, the session-start proposals); the schema 2 ledger fields in the ledger format block, with `"schema": 2` in the example. `layout.md` gains the four `standards.md` sections, the `[hygiene]` backlog tag, and journal lines `Suite time:`, `Timing:` and `Lens yield:`. Keep `SKILL.md` under 300 lines; point to `lenses.md` instead of repeating it. Ledger rule names and messages are Task 2's; command output formats are Task 5's (`Task N: pass (2.1s)`) and Task 10's (`Codemap: <n> pending (<action>)`, brief lines of spec Part 4).

- [ ] **Step 1: Extend `test_skill_docs.py`**: `SKILL.md` mentions `lenses.md`, `lens-review-prompt.md`, `inventory-prompt.md`, `"schema": 2`, `replaces`, `risk`, `experts`, `hygiene`, `ui-ux`, `unknown`, `Suite time`, `WCAG 2.2`, `systematic-debugging`, `.claude/codemap/`, `/codemap update`, `pending.md`; `layout.md` mentions `[hygiene]`, `Suite time:`, `Lens yield`, `Timing:`; line limit still 300.
- [ ] **Step 2: Run** `python3 -m unittest discover tech-lead/tests -p 'test_skill_docs.py'` — expected FAIL.
- [ ] **Step 3: Edit** the two files.
- [ ] **Step 4: Run** the same command, then the full suite — expected PASS.
- [ ] **Step 5: Commit** `tech-lead: skill and layout for hygiene, experts and UI/UX`.

---

### Task 5: Checkpoint timings

**Files:**
- Modify: `tech-lead/scripts/ledger_checkpoint.py`, `tech-lead/scripts/ledger.py`
- Test: `tech-lead/tests/test_ledger_checkpoint.py`, `tech-lead/tests/test_ledger_cli.py`

**Interfaces:**
- `CheckpointResult.tasks: list[tuple[int, int, float]]` (id, worst exit, total seconds of its verify commands); `checks: list[tuple[str, int, float]]`. `passed` unchanged.
- `format_result`: `Task N: pass (2.1s)`, `Task N: fail (exit X, 2.1s)`, `Checks: pass (14.8s)` (sum), `Check failed: <command> (exit X, 1.2s)`; one decimal; `time.monotonic`.
- `mark_done(ledger_path, ledger, wave, progress_path, today, result=None)`: when `result` is given, the wave entry gains `Timing: Task 1 2.1s, Task 2 0.4s, checks 14.8s` after `Tasks done:`. `ledger.py checkpoint --mark` passes the result.

- [ ] **Step 1: Update and add tests**: existing assertions on `Task 1: pass` and `Task 1: fail (exit 3` keep matching by prefix; new `test_durations_formatted` (a `sleep 0.2` verify reports between 0.1 and 2.0 seconds), `test_timing_line_in_journal`, CLI `test_checkpoint_prints_durations`.
- [ ] **Step 2: Run** the two test files — expected FAIL on the new tests.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** them, then the full suite — expected PASS.
- [ ] **Step 5: Commit** `tech-lead: checkpoint timings`.

---

### Task 6: Report columns for risk and experts

**Files:**
- Modify: `tech-lead/scripts/ledger_report.py`
- Test: `tech-lead/tests/test_ledger_report.py`

`render_show`: wave table columns become `| Task | Title | Depends on | Files | Model | Risk | Experts | Reason | Acceptance |`; Model cell appends ` (hygiene)` or ` (ui)` for those kinds; empty lists render `-`. Summary adds `Lens dispatches: wave 1: 2, wave 2: 0 (total 2)` counting distinct lenses per wave, or `Lens dispatches: none` when no task has experts.

- [ ] **Step 1: Write tests**: `test_risk_and_experts_columns`, `test_kind_suffix`, `test_lens_dispatch_counts_distinct_per_wave` (two tasks in wave 1 both with `security` count 1), `test_v1_ledger_renders_dashes_and_none`.
- [ ] **Step 2: Run** `python3 -m unittest discover tech-lead/tests -p 'test_ledger_report.py'` — expected FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** it, then the full suite — expected PASS.
- [ ] **Step 5: Commit** `tech-lead: show risk, experts and lens dispatches`.

---

### Task 10: Codemap in status and checkpoint

**Files:**
- Modify: `tech-lead/scripts/status.py`, `tech-lead/scripts/ledger_checkpoint.py`, `tech-lead/scripts/ledger.py`
- Test: `tech-lead/tests/test_status.py`, `tech-lead/tests/test_ledger_checkpoint.py`, `tech-lead/tests/test_ledger_cli.py`

**Interfaces** (source: spec Part 4):
- `ledger_checkpoint.codemap_action(count: int) -> str`: `inline` (≤ 15), `update` (16-50), `rebuild` (> 50).
- `ledger_checkpoint.sync_codemap(repo: str, base: str) -> tuple[int, str] | None`: `None` when `<repo>/.claude/codemap/` does not exist; otherwise appends `git diff --name-only <base>..HEAD` paths (quotepath off, as in `run_checkpoint`) to `pending.md`, drops lines under `.worktrees/`, de-duplicates keeping first order, rewrites the file, and returns (unique count, action). A git failure raises `CheckpointError`.
- `ledger.py checkpoint --mark`, after a passing mark: calls `sync_codemap(repo, base)` and, when not `None`, prints `Codemap: <n> pending (<action>)` and `Wrote <absolute path of pending.md>`.
- `status.codemap_lines(root: Path) -> list[str]`: the brief lines of spec Part 4's table (at most one line), never raising (any error returns `[]`); `render_brief` places it before the instruction line, counted in the 25-line cap; `render_full` adds `## Codemap` with: index present or not, `Generated:` date, pending count, `symbols.md` present, and the proposed action or `up to date`.

- [ ] **Step 1: Write the failing tests**: `codemap_action` boundaries 15/16/50/51; `sync_codemap` returns `None` without the directory, merges diff paths, drops `.worktrees/` lines, de-duplicates; CLI `--mark` prints the `Codemap:` line only when the directory exists; `codemap_lines` for each table row (no index with 30 tracked code files in a temporary git repo; 20 pending; 60 pending; missing `symbols.md`; old index with 20 commits since, using commit dates set by `GIT_COMMITTER_DATE`; up to date → `[]`; not a git repo → `[]`); brief contains the line before `Propose next steps`; full status has `## Codemap`.
- [ ] **Step 2: Run** the three test files — expected FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** them, then the full suite — expected PASS.
- [ ] **Step 5: Commit** `tech-lead: codemap health and pending sync`.

---

### Task 7: Version 0.2.0 and docs

**Files:**
- Modify: `tech-lead/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (version `0.2.0`, description mentions hygiene, expert panels and UI/UX), `tech-lead/README.md` (sections for hygiene, expert panels, UI/UX, codemap integration with `claude-codemap`, and the optional skills `engineering:*`, `design:*`, `modern-web-guidance`, `simplify`, `security-review`), root `README.md` (one updated sentence)
- Test: `tech-lead/tests/test_packaging.py`

- [ ] **Step 1: Extend tests**: version `0.2.0` in both and equal; `lenses.md` exists next to `SKILL.md` and is mentioned there; README mentions `lenses`, `hygiene`, `WCAG 2.2`, `schema`, `codemap`.
- [ ] **Step 2: Run** `python3 -m unittest discover tech-lead/tests -p 'test_packaging.py'` — expected FAIL.
- [ ] **Step 3: Edit.**
- [ ] **Step 4: Run** the full suite — expected PASS.
- [ ] **Step 5: Commit** `tech-lead: 0.2.0`.

---

### Task 8: Hygiene pass over the plugin

**Files:** `tech-lead/scripts/`, `tech-lead/tests/`

Input: `research/hygiene-candidates-4.md` from the lead's inventory dispatch. Remove dead code; merge duplicate tests and delete obsolete ones (keeping one test per behaviour, including the Review Focus tests); remove noise comments; no behaviour change. Acceptance: full suite green; median of 3 suite runs per test not more than 20% above the baseline of 1.58 s / 91 tests unless the total grew by 2 s or less; the report lists every removed or merged test with the test that now covers its behaviour.

- [ ] **Step 1: Run** the full suite three times and record the median and the test count.
- [ ] **Step 2: Apply** the cleanups, one commit per kind (dead code, tests, comments).
- [ ] **Step 3: Run** the full suite three times; compare with Step 1 and the baseline.
- [ ] **Step 4: Commit** messages `tech-lead: hygiene — <kind>`.

---

### Task 9: Lead verification (lead)

- [ ] Full suite passes; `ledger.py check` passes on both initiatives' ledgers; `status.py --write`.
- [ ] Time the suite (median of 3) and update `Suite time` in `docs/standards.md` when there is no regression.
- [ ] Read `SKILL.md`, `layout.md`, `lenses.md` and the prompts against the spec.
- [ ] Final whole-branch review (opus medium), then `superpowers:verification-before-completion`.
