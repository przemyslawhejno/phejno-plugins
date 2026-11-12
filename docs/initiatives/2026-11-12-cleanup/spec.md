# tech-lead 0.2.1: backlog cleanup — design

Date: 2026-11-12

## Goal

Close backlog items B2-B14 from `docs/backlog.md` in one initiative, so the 0.1.0 and 0.2.0 review leftovers stop accumulating. Source of truth for what is still open: `research/backlog-check.md` (checked against 0.2.0 at ed680e2: 9 open, 4 partly done). B1 (interactive dry run) stays open; it needs a new interactive session.

Success: every item below is fixed or closed with a recorded reason, behaviour stays the same except where an item says otherwise, the suite stays green and not slower per test than the ratchet in `docs/standards.md` (1.45 s, 136 tests).

## Decisions

| Item | Decision |
|---|---|
| B2 | Add the missing tests listed in backlog-check.md (checkpoint: log truncation, lead-task verify skip, first failing exit code, multi-wave selection; show: empty ledger, share rounding; CLI: missing argument, non-integer `--wave`, relative `--log`, unknown wave, non-UTF-8 locale; status: one initiative whose `waves` fails). |
| B3 | `status.py` imports `ledger_core` once. If the import fails, the full and `--write` modes print one `error: tech-lead scripts incomplete: <reason>` line and exit 1; `--brief` stays silent (hook safety). Per-initiative `unknown (ledger error)` remains only for an initiative whose own ledger is broken. |
| B4 | No code change for lead-task files: `ledger_core` already rejects files on lead tasks. `mark_done` documents in its docstring that it updates the ledger dict it receives. |
| B5 | `allow_abbrev=False`; a missing git binary (`OSError`) reports `error: git is not installed`. `-h` keeps argparse's multi-line help and exit 0: the one-line rule covers errors, and help is not an error (closed, reason recorded). |
| B6 | All list and text cells in `show` go through one escape that replaces newlines with spaces and escapes `|`. |
| B7 | Define "integration branch" once (Lanes); the ledger format block gets its own `### Ledger format` heading; remove the absolute-path bullets duplicated in `layout.md`; steps that dispatch before planning (standards discovery, mockup, scouts) say to load `model-manager:model-manager` first. |
| B8 | `batch-review-prompt.md` states that `{{MOCKUP_PATH}}` is `none` for batches without UI tasks; `test_prompts.py` asserts `id="` in `mockup-prompt.md` instead of a bare `id`. |
| B9 | README part done in 0.2.0. `test_packaging.py` also checks that every `../../scripts/*.py` named in `SKILL.md` exists. |
| B10 | Add the missing annotations in `ledger_core.py`. The "remaining test gaps" part is closed: it was never written down (reason recorded). |
| B11 | Fix done in 0.2.0. The test asserts that `subprocess.run` is called with `stdin=subprocess.DEVNULL` (mock), so it fails without the fix on any runner. |
| B12 | Split `_schema2_errors` by concern (field types, risk and lens rules, hygiene threshold) without changing messages; require `schema` to be the integer `2` (`2.0` is rejected); check risk vocabulary once; test that `kind: ui` counts toward the hygiene threshold; SKILL.md and layout.md say lead tasks do not count as `code`/`ui`. |
| B13 | `m.group` and `_run` parts done in 0.2.0. `test_status.py` asserts the instruction line in one test only; `lenses.md` states the 8-line checklist limit and `test_prompts.py` asserts it. |
| B14 | `docs/standards.md` holds the suite-time ratchet; `journal.md` records each measurement as an event and points to the ratchet — the wording in SKILL.md and layout.md says so. Lens re-review reports go to `research/lens-<lens>-<wave>-fix<n>.md`, stated in `lenses.md` and `layout.md`. |

Version `0.2.1` in `plugin.json` and the marketplace entry. Closed items get `[x]` in `docs/backlog.md` with a link to this initiative.

## Out of scope

B1; new features; changes to model-manager, superpowers or codemap.
