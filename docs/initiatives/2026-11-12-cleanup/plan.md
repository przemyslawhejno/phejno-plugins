# tech-lead 0.2.1 backlog cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close backlog items B2-B14 of the `tech-lead` plugin as the spec decides, and release 0.2.1.

**Architecture:** Each task owns one module and its test file, or the skill documents, so all five code and docs tasks run in one wave; a hygiene pass follows.

**Tech Stack:** Python 3.9+ stdlib, `unittest`, Markdown, JSON.

**Spec:** `docs/initiatives/2026-11-12-cleanup/spec.md` (decisions per item). Locations: `docs/initiatives/2026-11-12-cleanup/research/backlog-check.md` (file:line per item, checked at ed680e2).

## Global Constraints

- Read the spec's decision row and the backlog-check rows for each item you own; the decision wins where they differ.
- No behaviour change beyond what an item states; all error, output and validation messages stay byte-identical unless the spec names a new one (`error: tech-lead scripts incomplete: <reason>`, `error: git is not installed`).
- Python 3.9+ compatible (`from __future__ import annotations`; no `match`, no runtime `X | Y`, no `zip(strict=)`), stdlib only, UTF-8.
- Hygiene per `docs/standards.md`: minimal comments, no history, one behaviour one test, remove what a change makes obsolete.
- Tests: `python3 -m unittest discover tech-lead/tests` from the repository root (137 tests at the start); suite ratchet 1.45 s / 136 tests; tests that build git repositories share them per class. Do not edit `tech-lead/tests/helpers.py`.
- A new test that guards a fix must fail without that fix: check it once by reverting the fix locally before committing, and say so in the report.
- No `model` or `effort` in skill or command frontmatter; `SKILL.md` under 300 lines.

## Review Focus

1. A `schema` of `2.0`, `"2"` or `true` is rejected with `invalid schema '<v>'`; `2` still works (Task 1).
2. Splitting `_schema2_errors` changes no message and no order of messages for the existing tests (Task 1).
3. `status.py --brief` stays silent and exits 0 when `ledger_core` cannot be imported (Task 4).
4. The `show` escape keeps `<br>` between list items while flattening newlines inside items (Task 3).
5. Help output (`-h`) still exits 0 (Task 2).
6. Task 2's locale, stdin, abbreviation and missing-git tests fail without their fixes.
7. Task 5 keeps `test_skill_docs.py` green and `SKILL.md` under 300 lines (189 now).

---

Waves: 1 = Tasks 1-5 (lane 1: Tasks 1, 3, 5; lane 2: Tasks 2, 4); 2 = Task 6; 3 = Task 7.

### Task 1: ledger_core cleanup (B10, B12)

**Files:** `tech-lead/scripts/ledger_core.py`, `tech-lead/tests/test_ledger_core.py`

- [ ] Tests first: `test_schema_must_be_int_two` (`2.0`, `"2"`, `True` rejected with `invalid schema '<v>'`); `test_ui_tasks_count_toward_hygiene_threshold` (3 `kind: ui` tasks without a hygiene task give `missing hygiene task`).
- [ ] Replaces: the duplicate risk-vocabulary guard in `_schema2_errors`.
- [ ] Split `_schema2_errors` into helpers by concern (field types; risk and lens rules; hygiene threshold and dependencies) with identical messages and order; check risk vocabulary once; add the missing annotations listed for B10.
- [ ] Full suite passes; commit `tech-lead: ledger_core cleanup (B10, B12)`.

### Task 2: checkpoint and CLI (B2 part, B4, B5, B11)

**Files:** `tech-lead/scripts/ledger_checkpoint.py`, `tech-lead/scripts/ledger.py`, `tech-lead/tests/test_ledger_checkpoint.py`, `tech-lead/tests/test_ledger_cli.py`

- [ ] Tests first: checkpoint — log truncated on a rerun, lead task's verify skipped, worst exit code of several verify commands, only the requested wave's tasks run; CLI — missing argument, non-integer `--wave`, relative `--log` resolved to an absolute `Wrote` path, unknown wave, abbreviated option (`--wav`) rejected; locale: run `ledger.py show` as a subprocess with `LC_ALL=C`, `PYTHONUTF8=0`, `PYTHONCOERCECLOCALE=0` and no `PYTHONIOENCODING`, on a ledger whose title is `Zażółć`, and assert exit 0 and the UTF-8 bytes of the title in stdout (it must fail when the stdout `reconfigure` in `ledger.py` is removed); missing git: call `ledger.main(["checkpoint", ...])` in process with `ledger.subprocess.run` patched to raise `FileNotFoundError` and assert the stderr line `error: git is not installed` and exit 1; stdin: patch `ledger_checkpoint.subprocess.run` and assert it is called with `stdin=subprocess.DEVNULL`.
- [ ] Replaces: the timing-based stdin test in `test_ledger_checkpoint.py` (delete it).
- [ ] `allow_abbrev=False`; `OSError` from git → `error: git is not installed`; `mark_done` docstring states it updates the ledger dict it receives. `-h` unchanged.
- [ ] Full suite passes; commit `tech-lead: checkpoint and CLI cleanup (B2, B4, B5, B11)`.

### Task 3: show escaping (B2 part, B6)

**Files:** `tech-lead/scripts/ledger_report.py`, `tech-lead/tests/test_ledger_report.py`

- [ ] Replaces: the ad hoc per-column escaping in `render_show`.
- [ ] Tests first: a title, a file and an acceptance item containing `\n` and `|` render on one table row; an empty task list renders the sections without error; the share rounds (1 of 3 → `33%`, 2 of 3 → `67%`).
- [ ] One escape helper for every cell; list cells keep `<br>` between items.
- [ ] Full suite passes; commit `tech-lead: show escaping and tests (B2, B6)`.

### Task 4: status (B2 part, B3, B13 part)

**Files:** `tech-lead/scripts/status.py`, `tech-lead/tests/test_status.py`

- [ ] Replaces: the duplicate instruction-line assertion in `test_status.py`.
- [ ] Interface: `status._load_core() -> module`, the single place that imports `ledger_core` (raises `ImportError` on failure).
- [ ] Tests first: with `status._load_core` patched to raise `ImportError`, full mode prints one `error: tech-lead scripts incomplete: <reason>` line and exits 1, `--brief` prints nothing and exits 0; with `ledger_core.waves` patched to raise for one initiative's ledger, that initiative shows `unknown (ledger error)` while others render; the instruction line is asserted in one test only.
- [ ] Import `ledger_core` once; per-initiative errors stay per initiative.
- [ ] Full suite passes; commit `tech-lead: status import error and tests (B2, B3, B13)`.

### Task 5: skill documents, prompts and version (B7, B8, B9, B12 doc, B13 doc, B14)

**Files:** `tech-lead/skills/tech-lead/SKILL.md`, `layout.md`, `lenses.md`, `batch-review-prompt.md` (same directory), `tech-lead/tests/test_prompts.py`, `tech-lead/tests/test_packaging.py`, `tech-lead/tests/test_skill_docs.py`, `tech-lead/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

- [ ] Tests first: `test_prompts.py` asserts `id="` in `mockup-prompt.md` and that each lens checklist in `lenses.md` has at most 8 bullet lines (bullets are lines starting `- ` between a lens's `##` heading and the next heading or its `Uses when installed` line); `test_packaging.py` asserts every `../../scripts/<name>.py` in `SKILL.md` exists (the existing test already checks that both manifests carry the same version). Keep the strings `test_skill_docs.py` asserts (`Suite time`, `Suite time:`, `Timing:`, `Lens yield`, section order); update that test only where a decided wording changes.
- [ ] Edits per the spec rows B7, B8, B12 (lead tasks do not count as `code`/`ui`), B13 (state the 8-line limit), B14 (SKILL.md and layout.md say: the `Suite time:` line in `docs/standards.md` is the ratchet; `journal.md` records each timing as `Suite timed: <s>s, <n> tests (ratchet <r>s)`; re-review report path `research/lens-<lens>-<wave>-fix<n>.md` in `lenses.md` and `layout.md`); version `0.2.1`.
- [ ] Full suite passes; commit `tech-lead: skill and prompt cleanup, 0.2.1 (B7, B8, B9, B12, B13, B14)`.

### Task 6: Hygiene pass

**Files:** `tech-lead/scripts/`, `tech-lead/tests/`

Input: `research/hygiene-candidates-2.md` from the lead's inventory (haiku low) over this initiative's changes. Remove what the wave made obsolete or duplicated, starting with the tasks' `replaces` lists; no behaviour change. Acceptance: suite green; median of 3 runs per test not more than 20% above 1.45 s / 136 tests unless the total grew by 2 s or less; report timings and every removed test with its replacement. Commit `tech-lead: hygiene — <kind>` per kind.

### Task 7: Lead verification (lead)

- [ ] Full suite; `ledger.py check` on all three initiatives' ledgers; version `0.2.1` in both manifests; mark B2-B14 `[x]` in `docs/backlog.md` with a link to this initiative, noting the closures: B4 lead-task files (already rejected by validation), B5 help kept multi-line (help is not an error), B9 README part (done in 0.2.0), B10 test gaps (never written down), B11 and B13 fixes done in 0.2.0; update the suite ratchet when there is no regression; `status.py --write`; final whole-branch review.
