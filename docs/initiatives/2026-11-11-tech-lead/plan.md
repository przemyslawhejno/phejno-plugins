# tech-lead Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `tech-lead` Claude Code plugin: a lead-orchestrator skill with its prompts, a command, a SessionStart status hook, and two stdlib Python scripts (`ledger.py`, `status.py`).

**Architecture:** Behaviour lives in prose (skill, prompts, command). Mechanics live in small Python modules under `tech-lead/scripts/`: `ledger_core.py` (load, validate, waves, next), `ledger_report.py` (show), `ledger_checkpoint.py` (checkpoint, mark), wired by a thin CLI `ledger.py`; `status.py` stands alone and imports `ledger_core`. Each module has its own test file, so tasks touch disjoint files and can run in parallel lanes.

**Tech Stack:** Python 3.9+ stdlib, `unittest`, git, Markdown, JSON.

**Spec:** `docs/initiatives/2026-11-11-tech-lead/spec.md`

**Ledger:** `docs/initiatives/2026-11-11-tech-lead/ledger.json` (task ids below match it).

## Global Constraints

- Spec: `docs/initiatives/2026-11-11-tech-lead/spec.md`. A task that names spec sections reads them there.
- Python 3.9+ compatible: `from __future__ import annotations` in every module; no `match`, no `X | Y` unions evaluated at runtime (in `isinstance` or outside annotations), no parenthesised multi-item `with`, no `zip(strict=...)`. Stdlib only, no third-party packages.
- CLIs reconfigure stdout and stderr to UTF-8 (`reconfigure(encoding="utf-8")`). Usage errors are one `error: <message>` line on stderr and exit 1, not argparse's multi-line exit 2.
- Tests that create git repositories set `user.email`, `user.name` and `commit.gpgsign=false` locally, run git with `GIT_DIR` and `GIT_WORK_TREE` removed from the environment, and compare paths after `os.path.realpath`.
- Every file read or written as UTF-8; JSON written with `indent=2`, `ensure_ascii=False` and a trailing newline.
- A malformed or unreadable input is one error line on stderr (`error: <message>`) and exit 1, never a traceback.
- Every file a script writes is announced as `Wrote <absolute path>` on its own stdout line; paths in reports are absolute.
- Allowed values: models `haiku`, `sonnet`, `opus`, `fable`, `lead`; efforts `low`, `medium`, `high`, `xhigh`, `max`; reuse modes `dependency`, `copy`, `pattern`.
- No `model` or `effort` key in any skill or command frontmatter, and no text that switches or suggests a model for the main session.
- Plugin name `tech-lead`, version `0.1.0`; command file `commands/run.md` (invoked as `/tech-lead:run`).
- Tests run with `python3 -m unittest discover tech-lead/tests` from the repository root.
- Scripts are found from the skill as `../../scripts/` relative to the skill's base directory; from hooks and commands as `${CLAUDE_PLUGIN_ROOT}/scripts/`.

## Review Focus

1. Polish or other non-ASCII text in titles, journal and backlog: must round-trip unchanged (UTF-8 read and write, `ensure_ascii=False`). Test in Task 4 (journal) and Task 2 (status).
2. A task `id` given as the string `"1"` instead of the integer `1`: reported as a validation error, not a crash or silent mismatch with `done`. Test in Task 1.
3. `checkpoint` with a `--base` ref that does not exist, or outside a git repository: one `error:` line, exit 1, ledger untouched. Test in Task 4.
4. `checkpoint --mark` when SDD's `progress.md` is absent: marks done and writes the wave entry without copied lines. Test in Task 4.
5. The SessionStart hook runs with the project root in `CLAUDE_PROJECT_DIR` while the working directory differs: `status.py` must use that variable when `ROOT` is not given. Test in Task 2.

---

## File structure

```
tech-lead/
  .claude-plugin/plugin.json             Task 8
  hooks/hooks.json                       Task 8
  commands/run.md                        Task 8
  README.md                              Task 8
  skills/tech-lead/SKILL.md              Task 6
  skills/tech-lead/layout.md             Task 6
  skills/tech-lead/scout-prompt.md       Task 7
  skills/tech-lead/mockup-prompt.md      Task 7
  skills/tech-lead/batch-review-prompt.md  Task 7
  skills/tech-lead/plan-review-prompt.md   Task 7
  scripts/ledger_core.py                 Task 1
  scripts/status.py                      Task 2
  scripts/ledger_report.py               Task 3
  scripts/ledger_checkpoint.py           Task 4
  scripts/ledger.py                      Task 5
  tests/helpers.py                       Task 1
  tests/test_ledger_core.py              Task 1
  tests/test_status.py                   Task 2
  tests/test_ledger_report.py            Task 3
  tests/test_ledger_checkpoint.py        Task 4
  tests/test_ledger_cli.py               Task 5
  tests/test_skill_docs.py               Task 6
  tests/test_prompts.py                  Task 7
  tests/test_packaging.py                Task 8
.claude-plugin/marketplace.json          Task 8
README.md                                Task 8
```

Waves: 1 = Tasks 1, 6, 7; 2 = Tasks 2, 3, 4; 3 = Task 5; 4 = Task 8; 5 = Task 9.

---

### Task 1: Ledger core (load, validate, waves, next)

**Files:**
- Create: `tech-lead/scripts/ledger_core.py`
- Create: `tech-lead/tests/helpers.py`
- Test: `tech-lead/tests/test_ledger_core.py`

**Interfaces:**
- Produces, in `ledger_core.py`:
  - `MODELS`, `EFFORTS`, `REUSE_MODES`: tuples of the allowed values.
  - `class LedgerError(Exception)`.
  - `load(path: str) -> dict`: raises `LedgerError("<path>: <reason>")` for a missing file, invalid JSON, or a top level that is not an object.
  - `validate(ledger: dict) -> list[str]`: error messages, empty when valid. Never raises on wrong types.
  - `waves(tasks: list[dict]) -> dict[int, int]`: task id to wave number. Callers validate first (acyclic).
  - `paths_overlap(a: str, b: str) -> bool`.
  - `next_wave(ledger: dict) -> tuple[int, list[dict]] | None`: earliest wave with a task whose id is not in `done`, and those tasks in id order; `None` when all are done.
- Produces, in `tests/helpers.py`: `SCRIPTS` (absolute path of `tech-lead/scripts`, inserted at the front of `sys.path` on import), `make_task(id: int, **overrides) -> dict` (a valid sonnet/low task with `files=[f"src/t{id}.py"]`, `acceptance=["works"]`, `verify=["true"]`, `depends_on=[]`, `reason="r"`, `title=f"Task {id}"`), `make_ledger(tasks: list[dict], **overrides) -> dict`: top-level `prior_art="done"`, `checks=[]`, `done=[]`, `requirements=[{"id": "R1", "text": "r"}]`, `tasks`; sets the first task's `covers` to `["R1"]` unless it already has `covers`; then `overrides` replace top-level keys.

Validation messages (tests assert these substrings; `N` is the task id):

| Rule | Message |
|---|---|
| missing field | `task N: missing field '<name>'` |
| empty acceptance | `task N: acceptance is empty` |
| id not a positive int (bool excluded) | `task <repr>: id must be a positive integer` |
| duplicate id | `duplicate task id N` / `duplicate requirement id <id>` |
| unknown done id | `done: unknown task id <x>` |
| bad model / effort / reuse mode | `task N: invalid model '<v>'` (same shape for `effort`, `reuse.mode`) |
| reuse without source or license | `task N: reuse needs source and license` |
| unknown dependency / covers | `task N: depends on unknown task <x>` / `task N: covers unknown requirement <x>` |
| cycle | `dependency cycle: 1 -> 2 -> 1` |
| uncovered requirement | `requirement <id> is covered by no task` |
| lead with files / non-lead without | `task N: lead tasks edit no files` / `task N: files is empty` |
| empty verify | `task N: verify is empty and no_verify gives no reason` |
| path | `task N: path '<p>' is not normalised` |
| same-wave conflict | `wave W: tasks A and B share '<p>'; add a dependency between them` |
| prior art | `missing field 'prior_art'` |
| mode | `invalid mode '<v>'` (allowed `gated`, `autopilot`; absent means `gated`) |

Required fields: `id`, `title`, `depends_on`, `files`, `acceptance`, `model`, `reason`; `effort` and `verify` unless `model` is `lead`. Top-level `requirements`, `done`, `checks` default to `[]` when absent. A path is not normalised when it is empty, starts with `/` or `./`, contains `\`, `//` or a `..` segment. `paths_overlap`: equal, or one ends with `/` and the other starts with it. Wave and conflict checks are skipped when there is a cycle, an unknown dependency, or an invalid or duplicate task id.

- [ ] **Step 1: Write `tests/helpers.py` and the failing tests**

Tests in `test_ledger_core.py`, one per line:
- `test_valid_ledger_has_no_errors`: `validate(make_ledger([make_task(1), make_task(2, depends_on=[1])])) == []`.
- `test_missing_field`, `test_empty_acceptance`, `test_string_id_rejected` (`make_task("1")` gives `id must be a positive integer`), `test_duplicate_ids`, `test_unknown_done_id` (including `done: ["1"]`), `test_invalid_model_effort_reuse_mode`, `test_reuse_needs_source_and_license`, `test_unknown_dependency_and_covers`, `test_cycle_reported` (tasks 1 and 2 depending on each other give `dependency cycle: 1 -> 2 -> 1`), `test_uncovered_requirement`, `test_lead_task_files_rules`, `test_lead_task_needs_no_effort_or_verify`, `test_empty_verify_needs_reason` (`no_verify="docs only"` clears it), `test_paths_not_normalised` (each of `/a`, `./a`, `a/../b`, `a//b`, `a\\b`, `""`), `test_same_wave_conflict_with_directory_prefix` (files `src/` and `src/a.py` in wave 1 give `wave 1: tasks 1 and 2 share`), `test_conflict_cleared_by_dependency`, `test_prior_art_missing`, `test_invalid_mode`, `test_wrong_types_do_not_raise` (`tasks="x"`, `files=5`, `depends_on=None` each yield errors).
- `test_waves`: 1 and 2 independent, 3 depends on 1 and 2, 4 on 3: `{1: 1, 2: 1, 3: 2, 4: 3}`.
- `test_paths_overlap`: `("src/", "src/a.py")` True, `("src/a.py", "src/a.py")` True, `("src", "src2")` False, `("src/a", "src/ab")` False.
- `test_next_wave`: nothing done gives wave 1 with tasks 1 and 2; `done=[1]` still gives wave 1 with task 2 (a stuck task keeps its wave open); `done=[1, 2]` gives wave 2; all done gives `None`.
- `test_load_errors`: missing file, invalid JSON and a JSON list each raise `LedgerError` whose message starts with the path.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_ledger_core.py'`
Expected: FAIL with `ModuleNotFoundError: No module named 'ledger_core'`

- [ ] **Step 3: Implement `ledger_core.py` with the interfaces above**

Cycle detection by depth-first search reporting the first cycle found, in path order from its smallest id. Wave of a task = 1 + max wave of its dependencies.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_ledger_core.py'`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tech-lead/scripts/ledger_core.py tech-lead/tests/helpers.py tech-lead/tests/test_ledger_core.py
git commit -m "tech-lead: ledger core validation, waves and next"
```

---

### Task 2: Project status (`status.py`)

**Files:**
- Create: `tech-lead/scripts/status.py`
- Test: `tech-lead/tests/test_status.py`

**Interfaces:**
- Consumes: `ledger_core.load`, `validate`, `waves`, `LedgerError`.
- Produces:
  - `initiative_state(folder: Path) -> dict` with keys `name`, `path` (absolute str), `date` (`YYYY-MM-DD` from the folder name prefix, else `""`), `state`, `waves_done`, `waves_total`, `next_wave` (int or `None`).
  - `read_backlog(path: Path) -> list[str]`: the open items, each line starting `- [ ] ` with that prefix removed, in file order.
  - `render_full(root: Path) -> str`, `render_brief(root: Path) -> str`, `write_status(root: Path) -> Path`.
  - `main(argv: list[str]) -> int` and CLI `status.py [ROOT] [--brief | --write]`.

State rules, checked in this order: a line in `journal.md` starting `Closed:` → `closed`; `ledger.json` present but failing `load` or `validate` → `unknown (ledger error)`; `ledger.json` with every task id in `done` → `done`; some done → `in progress`; none done → `planned`; `spec.md` → `specified`; otherwise `proposed`. `waves_done` counts waves whose tasks are all done.

Output rules:
- `render_full`: `# Project status` and one `## <State>` section per non-empty state in the order in progress, planned, specified, proposed, unknown, then `## Recently done` (the 5 newest done or closed by `date`), then `## Backlog`. An initiative line: `- <name> (<state>, waves <done>/<total>, next wave <n>): <absolute path>`, dropping the parts that do not apply. Without `docs/initiatives/` it prints `No initiatives yet.`
- `write_status`: writes `docs/STATUS.md` starting with `<!-- generated by tech-lead status.py, do not edit -->`, returns its path; the CLI prints `Wrote <absolute path>`.
- `render_brief`: empty string when `docs/initiatives/` is missing. Otherwise at most 25 lines: `tech-lead status for <absolute root>`, initiatives in progress, planned and specified (one line each, as above), the first 5 backlog items, then exactly: `Propose next steps to the user as a short list based on this status, and wait for their choice before starting work.`, followed by ` Full status: <absolute path of docs/STATUS.md>` on the same line only when that file exists. Initiative lines are cut first when over the limit.
- ROOT defaults to `$CLAUDE_PROJECT_DIR`, else the current directory.
- `--brief` prints nothing and exits 0 when `TECH_LEAD_STATUS=0`, and on any exception; the `ledger_core` import sits inside the guarded code, so a broken install cannot break a session.

- [ ] **Step 1: Write the failing tests**

Each builds a temporary project with `tempfile.TemporaryDirectory` and ledgers from `helpers.make_ledger`:
- `test_states`: one folder per state (proposed, specified, planned, in progress, done, closed, broken ledger) maps to the expected `state`.
- `test_waves_and_next`: three-wave ledger with wave 1 done gives `waves_done == 1`, `waves_total == 3`, `next_wave == 2`.
- `test_backlog_open_items_only`: `- [ ] B1 a` and `- [x] B2 b` give `["B1 a"]`.
- `test_full_lists_absolute_paths_and_sections`.
- `test_full_without_initiatives`: `No initiatives yet.`
- `test_brief_silent_without_initiatives`: `""`.
- `test_brief_limit_and_instruction`: 40 planned initiatives give at most 25 lines, and the last line starts `Propose next steps`.
- `test_write_header_and_path`: the file starts with the generated header.
- `test_non_ascii_round_trip`: a backlog item `- [ ] B3 Zażółć gęślą jaźń` appears unchanged in `render_full`.
- `test_root_from_env`: running the CLI with `cwd` elsewhere and `CLAUDE_PROJECT_DIR` set reports that root.
- `test_brief_disabled_by_env`: no output, exit 0.
- `test_brief_swallows_errors`: with `status.render_brief` patched to raise `RuntimeError`, `main([root, "--brief"])` returns 0 and prints nothing (capture stdout).
- `test_brief_status_path_only_when_present`: no `Full status:` before `write_status`, present after.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_status.py'`
Expected: FAIL with `ModuleNotFoundError: No module named 'status'`

- [ ] **Step 3: Implement `status.py` with the interfaces and rules above**

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_status.py'`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tech-lead/scripts/status.py tech-lead/tests/test_status.py
git commit -m "tech-lead: project status report and session brief"
```

---

### Task 3: Ledger report (`show`)

**Files:**
- Create: `tech-lead/scripts/ledger_report.py`
- Test: `tech-lead/tests/test_ledger_report.py`

**Interfaces:**
- Consumes: `ledger_core.waves`.
- Produces: `render_show(ledger: dict) -> str` for a valid ledger.

Sections, in order:
1. `## Wave W` per wave, each with a table: `| Task | Title | Depends on | Files | Model | Reason | Acceptance |`. Model cell `sonnet/low`, or `lead` alone. List cells joined with `<br>`.
2. `## Requirement coverage`: `| Requirement | Text | Tasks |`.
3. `## New dependencies and copied code`: `- Task N: <source> (<mode>, <license>)` for `reuse` modes `dependency` and `copy`, or `None.`
4. `## Summary`: one line per model in `MODELS` order with a non-zero count (`- sonnet: 3`), then `Opus and fable share: X% (k of n tasks)` with X rounded to a whole number, plus `Prior art: <prior_art>`.

- [ ] **Step 1: Write the failing tests**

- `test_sections_in_order`.
- `test_wave_tables`: tasks of waves 1 and 2 appear under the right headings, with `sonnet/low` and `lead`.
- `test_coverage_lists_tasks`: `R1` row lists task 1.
- `test_reuse_list_excludes_pattern`: a `pattern` reuse is absent, `dependency` and `copy` are listed; without any, `None.`
- `test_summary_counts_and_share`: 2 sonnet, 1 opus, 1 fable gives `Opus and fable share: 50% (2 of 4 tasks)`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_ledger_report.py'`
Expected: FAIL with `ModuleNotFoundError: No module named 'ledger_report'`

- [ ] **Step 3: Implement `render_show` in `ledger_report.py`**

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_ledger_report.py'`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tech-lead/scripts/ledger_report.py tech-lead/tests/test_ledger_report.py
git commit -m "tech-lead: ledger show report"
```

---

### Task 4: Wave checkpoint and mark

**Files:**
- Create: `tech-lead/scripts/ledger_checkpoint.py`
- Test: `tech-lead/tests/test_ledger_checkpoint.py`

**Interfaces:**
- Consumes: `ledger_core.waves`, `paths_overlap`.
- Produces:
  - `class CheckpointError(Exception)`.
  - `@dataclass CheckpointResult`: `tasks: list[tuple[int, int]]` (task id, worst exit code of its `verify` commands, 0 when all pass), `checks: list[tuple[str, int]]`, `out_of_scope: list[str]`, `log_path: str` (absolute); property `passed: bool` (every code is 0; out-of-scope files do not fail).
  - `out_of_scope(changed: list[str], allowed: list[str]) -> list[str]`: changed paths that overlap no allowed path, in input order.
  - `run_checkpoint(ledger: dict, wave: int, base: str, repo: str, log_path: str) -> CheckpointResult`: `git diff --name-only <base>..HEAD` in `repo` (a git failure or unknown ref raises `CheckpointError("git diff failed: <stderr first line>")`); runs each `verify` command of the wave's non-lead tasks, then each of `checks`, with `shell=True`, `cwd=repo`; truncates the log, then appends each command's header (`$ <command>`), combined output and exit code, creating its parent directories. Nothing from the commands goes to stdout.
  - `format_result(result: CheckpointResult) -> str`: `Task N: pass` or `Task N: fail (exit X)` per task, `Checks: pass` or `Check failed: <command> (exit X)` per failing check, and `Out of scope: <path>` per file. The log path is printed by the CLI as `Wrote <path>`, not here.
  - `mark_done(ledger_path: str, ledger: dict, wave: int, progress_path: str | None, today: str) -> list[str]`: adds the wave's task ids to `done` (keeping existing order, appending new ids ascending, no duplicates), rewrites the ledger, appends to `journal.md` in the ledger's folder (created if missing), returns the absolute paths written.

Journal entry appended by `mark_done`:

```
## <today> wave <W>
Tasks done: <ids comma-separated>
<each line of progress.md that contains "Ruling:" or starts with "Attempt:" (after stripping), and does not already appear in journal.md>
```

- [ ] **Step 1: Write the failing tests**

Fixture: a temporary git repository (`git init`, `user.email`/`user.name` set locally, an initial commit used as base), then a commit changing `src/t1.py` and `other.txt`.
- `test_out_of_scope_with_directory_prefix`: `out_of_scope(["src/a.py", "x.txt"], ["src/"]) == ["x.txt"]`.
- `test_pass`: verify `true`, check `true` gives `passed` and `Task 1: pass`, `Checks: pass`, `Out of scope: other.txt`.
- `test_failing_verify`: verify `exit 3` gives `Task 1: fail (exit 3)` and not `passed`.
- `test_failing_check`: check `exit 2` gives `Check failed: exit 2 (exit 2)`.
- `test_output_goes_to_log_only`: verify `echo hello` writes `hello` into the log; `format_result` does not contain it.
- `test_bad_base_raises`: base `nope` raises `CheckpointError` starting `git diff failed`.
- `test_mark_done_updates_ledger_and_journal`: `done` becomes `[1]`; the journal contains `## 2026-11-11 wave 1`, `Tasks done: 1`, and from a sample `progress.md` the lines `Ruling: a`, `Task 2: Ruling: b`, `Task 3: parked — f — Ruling: c` and `Attempt: Task 1 sonnet/low failed, cause brief, x`, but not `Task 1: complete`.
- `test_mark_done_does_not_duplicate_copied_lines`: two marks with the same `progress.md` copy each `Ruling:` line once.
- `test_mark_done_without_progress`: `progress_path=None` writes the entry without copied lines.
- `test_non_ascii_journal`: a `Ruling: zmiana nazwy pliku — powód` line round-trips unchanged; the ledger file contains `ż` literally, not `ż`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_ledger_checkpoint.py'`
Expected: FAIL with `ModuleNotFoundError: No module named 'ledger_checkpoint'`

- [ ] **Step 3: Implement `ledger_checkpoint.py` with the interfaces above**

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_ledger_checkpoint.py'`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tech-lead/scripts/ledger_checkpoint.py tech-lead/tests/test_ledger_checkpoint.py
git commit -m "tech-lead: wave checkpoint and mark"
```

---

### Task 5: Ledger CLI (`ledger.py`)

**Files:**
- Create: `tech-lead/scripts/ledger.py`
- Test: `tech-lead/tests/test_ledger_cli.py`

**Interfaces:**
- Consumes: Task 1 (`load`, `validate`, `next_wave`, `LedgerError`), Task 3 (`render_show`), Task 4 (`run_checkpoint`, `format_result`, `mark_done`, `CheckpointError`).
- Produces: `main(argv: list[str]) -> int` and the commands:

| Command | Output and exit |
|---|---|
| `check LEDGER` | Each error on its own stdout line, exit 1; nothing, exit 0 when valid. |
| `show LEDGER` | Errors and exit 1 when invalid; else `render_show`, exit 0. |
| `next LEDGER` | `Wave W` then `Task N: <title> (<model>/<effort>)`, or `(lead)` for lead tasks; or `all tasks complete`. Exit 1 when invalid. |
| `checkpoint LEDGER --wave W --base REF [--log FILE] [--progress FILE] [--mark]` | Exit 1 when invalid. Repo root from `git rev-parse --show-toplevel` in the current directory. Log default `<repo>/.tech-lead/scratch/checkpoint-W.log`. Prints `format_result`, then `Wrote <log>`. With `--mark` and a passing result, calls `mark_done` with today's date and prints `Wrote <path>` for each path. Exit 1 when not passed. |

`LedgerError` and `CheckpointError` print `error: <message>` on stderr and exit 1. The file runs as a script (`if __name__ == "__main__": sys.exit(main(sys.argv[1:]))`) and imports its sibling modules from its own directory.

- [ ] **Step 1: Write the failing tests**

Run the script with `subprocess.run([sys.executable, LEDGER_PY, ...])`. `checkpoint` takes the repository root from `git rev-parse --show-toplevel`; its failure is reported as `error: not a git repository`.
- `test_check_valid_and_invalid`: exit 0 with empty stdout; a cycle gives exit 1 and the cycle line.
- `test_show_prints_report`: contains `## Wave 1` and `## Summary`.
- `test_next_and_all_complete`: `Wave 1` and `Task 1: Task 1 (sonnet/low)`; all done gives `all tasks complete`.
- `test_checkpoint_mark_end_to_end`: in a temporary git repo, `--mark` exits 0, prints `Task 1: pass`, two or more `Wrote /` lines, and the ledger's `done` is `[1]`.
- `test_checkpoint_failure_does_not_mark`: verify `false` exits 1 and leaves `done` empty.
- `test_malformed_json_one_line`: exit 1, stderr is one line starting `error:`, no `Traceback`.
- `test_checkpoint_errors`: run from a temporary directory that is not a git repository, and separately with `--base nope` in a repository: each exits 1 with one stderr line starting `error:`, and the ledger file is byte-identical afterwards.
- `test_usage_error_one_line`: an unknown subcommand exits 1 with one stderr line starting `error:`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_ledger_cli.py'`
Expected: FAIL (script missing, non-zero exits)

- [ ] **Step 3: Implement `ledger.py` with `argparse` subcommands**

- [ ] **Step 4: Run all tests**

Run: `python3 -m unittest discover tech-lead/tests`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tech-lead/scripts/ledger.py tech-lead/tests/test_ledger_cli.py
git commit -m "tech-lead: ledger command line"
```

---

### Task 6: Lead skill and document layout

**Files:**
- Create: `tech-lead/skills/tech-lead/SKILL.md`
- Create: `tech-lead/skills/tech-lead/layout.md`
- Test: `tech-lead/tests/test_skill_docs.py`

**Interfaces:**
- Consumes: the CLI contracts of Tasks 2 and 5 (command names and flags as written there); prompt file names from Task 7.
- Produces: skill `tech-lead:tech-lead`.

Command synopsis to document (the scripts are built in parallel; this is their contract):

```
python3 ../../scripts/ledger.py check LEDGER
python3 ../../scripts/ledger.py show LEDGER
python3 ../../scripts/ledger.py next LEDGER
python3 ../../scripts/ledger.py checkpoint LEDGER --wave W --base REF --progress "<SDD workspace>/progress.md" --mark
python3 ../../scripts/status.py [ROOT] [--brief | --write]
```

`REF` is the integration branch head recorded before the wave started. The SDD workspace is the directory printed by SDD's `scripts/sdd-workspace PLAN_FILE`. Paths are relative to the skill's base directory.

Source: spec sections Decisions, Relationship to other plugins, Lead process, Tier table, Escalation, Lanes, Turn economy (into `SKILL.md`); Project document hierarchy, Journal, and the absolute-path rule (into `layout.md`). Write for an agent, imperative, no history or rationale beyond one clause where a rule would otherwise look arbitrary. Follow superpowers:writing-skills for structure. `SKILL.md` stays under 300 lines and points to `layout.md` instead of repeating it.

`SKILL.md` requirements:
- Frontmatter only `name: tech-lead` and a `description` starting `Use when`, covering: leading or orchestrating a spec or project end to end, planning and delegating work across models, and resuming a tech-lead initiative.
- Sections in this order: Role; Start of work (orient); Process (the 12 steps, including plan review and autopilot); Tiers; Escalation; Lanes; Turn economy; Paths; Commands (exact invocations of `ledger.py check|show|next|checkpoint` and `status.py`, located at `../../scripts/` relative to the skill's base directory).
- States that the lead runs on the session's model and never switches or suggests another.
- Names each required skill by its full id.

`layout.md` requirements: the hierarchy tree; one-line purpose per entry; state derivation rules; journal entry formats; backlog line format; `.gitignore` entries; the offer to migrate `docs/superpowers/`; the absolute-path rule with an example.

- [ ] **Step 1: Write the failing test `test_skill_docs.py`**

- `test_frontmatter`: exactly the keys `name` and `description`; name `tech-lead`; description starts `Use when`.
- `test_mentions_required_items`: `SKILL.md` contains each of `model-manager:model-manager`, `superpowers:brainstorming`, `superpowers:writing-plans`, `superpowers:subagent-driven-development`, `superpowers:verification-before-completion`, `superpowers:finishing-a-development-branch`, `ledger.py check`, `ledger.py show`, `ledger.py next`, `ledger.py checkpoint`, `--mark`, `status.py`, `layout.md`, `scout-prompt.md`, `mockup-prompt.md`, `batch-review-prompt.md`, `plan-review-prompt.md`, `autopilot`, `--auto`, `--progress`, `--wave`, `--base`, `sdd-workspace`, `../../scripts/`, `superpowers:test-driven-development`, `superpowers:requesting-code-review`, `security-review`, `engineering:architecture`, `modern-web-guidance`, `fable`, `` `brief` ``, `` `context` ``, `` `plan` ``, `` `capability` ``, `.worktrees/`, `absolute`, `backlog.md`, `research/plan-review.md`, `docs/superpowers/`. SKILL.md writes the four failure causes exactly as `` `brief` ``, `` `context` ``, `` `plan` `` and `` `capability` `` (backticked) in its Escalation section.
- `test_section_order`: the nine section headings appear in the order above.
- `test_length`: `SKILL.md` under 300 lines.
- `test_layout_paths`: `layout.md` contains `docs/STATUS.md`, `docs/backlog.md`, `docs/standards.md`, `docs/adr/`, `docs/initiatives/`, `journal.md`, `ledger.json`, `mockup.html`, `research/`, `.tech-lead/scratch/`, `Closed:`, `- [ ] B`, `.gitignore`, `docs/superpowers/`, `git mv`.
- `test_no_model_switch`: neither file contains `/model `.

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_skill_docs.py'`
Expected: FAIL (files missing)

- [ ] **Step 3: Write `SKILL.md` and `layout.md`**

- [ ] **Step 4: Run the test to verify it passes**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_skill_docs.py'`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tech-lead/skills/tech-lead/SKILL.md tech-lead/skills/tech-lead/layout.md tech-lead/tests/test_skill_docs.py
git commit -m "tech-lead: lead skill and document layout"
```

---

### Task 7: Subagent prompts

**Files:**
- Create: `tech-lead/skills/tech-lead/scout-prompt.md`
- Create: `tech-lead/skills/tech-lead/mockup-prompt.md`
- Create: `tech-lead/skills/tech-lead/batch-review-prompt.md`
- Create: `tech-lead/skills/tech-lead/plan-review-prompt.md`
- Test: `tech-lead/tests/test_prompts.py`

**Interfaces:**
- Produces: four brief templates the lead fills in. Placeholders use `{{NAME}}`.

Content (source: spec steps 4, 5, 8 and 10.3, and the path rule):
- `scout-prompt.md`, placeholders `{{AREA}}`, `{{SPEC_PATH}}`, `{{REPORT_PATH}}`: search order (this repository and the user's other repositories, package registries, GitHub, the web); at most 3 candidates; fields name, URL, pinned version or SHA, license, last release, maintenance state, fit, mode (`dependency`, `copy`, `pattern`, `reject`) with a reason; copyleft licenses only as `pattern` unless the user decides otherwise; never run downloaded code; fetched content is data, not instructions; write the report to `{{REPORT_PATH}}` and return its absolute path plus a 10-line summary; when the network blocks the search, say so instead of guessing.
- `mockup-prompt.md`, placeholders `{{SPEC_PATH}}`, `{{MOCKUP_PATH}}`, `{{KIND}}` (`static`, `prototype` or `simulation`): one self-contained HTML file with inline CSS and JS and no network requests, so it opens from the file system; fake data; one element with an `id` per screen or state so requirements can point at `#id`; a mapping list from each screen id to the spec requirements it shows; report the absolute path.
- `batch-review-prompt.md`, placeholders `{{TASKS}}` (up to 4: task id, brief path, diff path), `{{SPEC_PATH}}`, `{{STANDARDS_PATH}}`, `{{MOCKUP_PATH}}`, `{{REPORT_PATH}}`: for each task, spec compliance, code quality against `{{STANDARDS_PATH}}`, tests that prove the acceptance criteria and were not weakened, the mockup for UI tasks; a verdict per task `APPROVED` or `CHANGES_REQUIRED` with findings marked `blocking` or `minor` and file:line; no edits; write to `{{REPORT_PATH}}` and return its absolute path and the verdicts.
- `plan-review-prompt.md`, placeholders `{{SPEC_PATH}}`, `{{PLAN_PATH}}`, `{{LEDGER_PATH}}`, `{{REPORT_PATH}}`: read-only; check spec coverage, task size and boundaries, interfaces between tasks, dependencies and waves, model and effort per task in both directions (overspend and underpowered), `verify` commands that really prove acceptance, Review Focus, ignored risks; each finding `blocking` or `minor` with the plan section and a concrete fix; end with `PLAN APPROVED` or `PLAN NEEDS CHANGES`; write to `{{REPORT_PATH}}` and return its absolute path and the findings.

- [ ] **Step 1: Write the failing test `test_prompts.py`**

- `test_placeholders`: each file contains its placeholders listed above.
- `test_scout_rules`: contains `never run`, `data, not instructions`, `dependency`, `copy`, `pattern`, `reject`, `license`.
- `test_mockup_rules`: contains `self-contained`, `static`, `prototype`, `simulation`, `id`.
- `test_review_rules`: contains `APPROVED`, `CHANGES_REQUIRED`, `blocking`, `minor`.
- `test_plan_review_rules`: contains `PLAN APPROVED`, `PLAN NEEDS CHANGES`, `blocking`, `minor`, `model`, `verify`, `read-only`.
- `test_absolute_paths`: each file contains `absolute path`.

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_prompts.py'`
Expected: FAIL (files missing)

- [ ] **Step 3: Write the four prompt files**

- [ ] **Step 4: Run the test to verify it passes**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_prompts.py'`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tech-lead/skills/tech-lead/*-prompt.md tech-lead/tests/test_prompts.py
git commit -m "tech-lead: scout, mockup, batch review and plan review prompts"
```

---

### Task 8: Packaging, hook, command and docs

**Files:**
- Create: `tech-lead/.claude-plugin/plugin.json`
- Create: `tech-lead/hooks/hooks.json`
- Create: `tech-lead/commands/run.md`
- Create: `tech-lead/README.md`
- Modify: `.claude-plugin/marketplace.json` (add the entry after `model-manager`)
- Modify: `README.md` (add a `### tech-lead` section after `### model-manager`)
- Test: `tech-lead/tests/test_packaging.py`

**Interfaces:**
- Consumes: `status.py --brief` (Task 2), the skill (Task 6), the prompts (Task 7).

Values:
- `plugin.json`: `name` `tech-lead`, `version` `0.1.0`, `description` `Lead orchestrator: plans a spec into waves of tasks, assigns the cheapest capable model to each, delegates, reviews and verifies; keeps project docs, status and backlog in one hierarchy`, `author.name` `Przemyslaw Hejno`.
- `hooks.json`: `SessionStart`, matcher `startup|clear|compact`, command `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/status.py" --brief`.
- `run.md`: frontmatter `description` and `argument-hint: "[--auto] <spec text | spec path | initiative folder>"`; body tells the agent to load `tech-lead:tech-lead` and follow it with `$ARGUMENTS`, resuming when the argument is an existing initiative folder, treating `--auto` as the user's advance agreement to autopilot, and to report every artifact it creates by absolute path.
- Marketplace entry: same name, `source` `./tech-lead`, same description and version.
- `tech-lead/README.md`: what it does, requirements (`model-manager`, `superpowers`, `python3`, Claude Code 2.1.292+), install command `claude plugins install tech-lead@phejno-plugins`, usage of `/tech-lead:run` and `--auto`, the automatic plan review, the document hierarchy (short, pointing to `skills/tech-lead/layout.md`), the session-start status and `TECH_LEAD_STATUS=0`, the scripts, limits (no model switching, Workflow agents bypass model-manager, network-dependent prior art).
- Root `README.md` section: two sentences and the install command, in the style of the other sections.

- [ ] **Step 1: Write the failing test `test_packaging.py`**

- `test_plugin_json`: valid JSON with the values above.
- `test_marketplace_entry_matches_plugin`: entry exists, `source`, `version` and `description` equal `plugin.json`'s.
- `test_hook_points_to_existing_script`: the command contains `scripts/status.py --brief` and the file exists.
- `test_command_frontmatter`: `run.md` has `description` and `argument-hint`, no `model` or `effort`, and mentions `tech-lead:tech-lead`, `$ARGUMENTS` and `--auto`.
- `test_skill_references_exist`: `layout.md` and every `*-prompt.md` name mentioned in `SKILL.md` exist next to it.
- `test_readmes`: `tech-lead/README.md` mentions `/tech-lead:run`, `model-manager`, `superpowers` and `TECH_LEAD_STATUS`; root `README.md` has `### tech-lead`.

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest discover tech-lead/tests -p 'test_packaging.py'`
Expected: FAIL

- [ ] **Step 3: Write the files and entries**

- [ ] **Step 4: Run all tests**

Run: `python3 -m unittest discover tech-lead/tests`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tech-lead/.claude-plugin tech-lead/hooks tech-lead/commands tech-lead/README.md tech-lead/tests/test_packaging.py .claude-plugin/marketplace.json README.md
git commit -m "tech-lead: packaging, session-start hook, command and docs"
```

---

### Task 9: Lead verification (lead, no file edits by a subagent)

- [ ] Run `python3 -m unittest discover tech-lead/tests`: all pass.
- [ ] Run `python3 tech-lead/scripts/ledger.py check docs/initiatives/2026-11-11-tech-lead/ledger.json`: exit 0.
- [ ] Run `python3 tech-lead/scripts/status.py --write`: writes `docs/STATUS.md` and prints its absolute path; `--brief` lists this initiative.
- [ ] Simulate the hook: `CLAUDE_PROJECT_DIR=$PWD python3 tech-lead/scripts/status.py --brief` from another directory prints the brief; with `TECH_LEAD_STATUS=0` prints nothing.
- [ ] Read `SKILL.md`, `layout.md` and the four prompts against the spec, section by section.
- [ ] Dry run: create a scratch git repository at `.tech-lead/scratch/dry-run/` (git-ignored in this repository), put a small sample spec with a UI in it, and from inside it run `claude -p --plugin-dir tech-lead "/tech-lead:run <sample spec path>"` in a scratch git repository; it must reach the gate (mockup built, plan reviewed, ledger shown) without editing code. Then start a session there and confirm the status brief proposes next steps. If the `claude` CLI cannot run here, record that in the journal and ask the user to run both checks in a new session.
- [ ] Dispatch the final whole-branch review (opus medium), then `superpowers:verification-before-completion`.
