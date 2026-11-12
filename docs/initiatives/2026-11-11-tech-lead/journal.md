# tech-lead plugin: journal

## 2026-11-11 session

- Brainstorming: four model tiers; activation by command and skill; name `tech-lead`; the lead runs on the session's model and never suggests another.
- Independent fable review of the first design accepted in full: static ledger with `done` written by checkpoint, wave-gated `next`, lead-managed lane worktrees, one escalation ladder with failure causes, batched review, merged gate.
- Added on request: prior-art step, quality foundation (standards, checks, ADRs), HTML mockup in the spec, project document hierarchy with journal, backlog and generated status, session-start status hook, absolute paths for every artifact.
- Spec approved. Moved from `docs/superpowers/specs/` to this folder.
- Plan and ledger written. Prior art: model-manager and superpowers in this environment were the references; no external search for this plugin.
- Next: plan review and execution approach at the gate.

## 2026-11-11 plan review, round 1 (opus/medium)

- Report: research/plan-review.md. Verdict: PLAN NEEDS CHANGES, 6 blocking, 12 minor.
- Accepted all blocking: rulings copied by "contains Ruling:" (SDD writes `Task N: Ruling:`), `--progress` path from `sdd-workspace` documented in the skill, CLI synopsis and spec path given to Task 6, skill-reference test limited to layout.md and prompts, checkpoint error test outside git, dry run added to Task 9.
- Accepted minor M1-M9, M11, M12; Task 2 raised to sonnet/medium.
- Rejected M10 (JSON hook output): plain SessionStart stdout becomes context and is simpler to test.

## 2026-11-12 plan review, round 2 (sonnet/medium, scoped to the fix diff)

- Verdict: PLAN APPROVED. B1-B6 resolved; M1 partial; three new minor findings.
- Fixed without a further round: Task 6 asserts `backlog.md`, `research/plan-review.md`, `docs/superpowers/` and the backticked failure causes; the dry-run sample lives in a scratch git repository.
- Not changed: patching `status.render_brief` works because `main` resolves the module global at call time.
- Next: gate.

## 2026-11-12 gate

- Approved by the user: subagent-driven execution in two lanes, autopilot to the end (ledger `mode: autopilot`).

## 2026-11-12 wave 1
Tasks done: 1, 6, 7
Ruling: T8 hook test asserts the command contains `scripts/status.py` and `--brief` separately — the plan's literal substring cannot match the plan's own quoted command — cost if wrong: none, both parts are still pinned.
Checkpoint run by hand (ledger.py not built yet): 40 tests pass, no out-of-scope files. Fix rounds: Task 1 x1 (requirement id type safety, cycle rotation), Task 6 x1 (migration targets, lead tasks in waves).

## 2026-11-12 wave 2
Tasks done: 2, 3, 4
Task 4: Ruling: unknown wave raises CheckpointError and an OSError on the log becomes CheckpointError — the reviewer's ⚠️ item and the no-traceback global constraint make both real gaps — cost if wrong: two extra error paths

## 2026-11-12 wave 3
Tasks done: 5

## 2026-11-12 wave 4
Tasks done: 8

## 2026-11-12 lead verification (task 9)

- 90 tests pass; `ledger.py check` on this ledger passes; `status.py --write` wrote docs/STATUS.md; `--brief` from another directory with CLAUDE_PROJECT_DIR reports this initiative; `TECH_LEAD_STATUS=0` silences it.
- SKILL.md read against the spec: consistent, including plan review, autopilot, lead tasks and absolute paths.
- Headless smoke tests (`claude -p --plugin-dir tech-lead`): the skill and `/tech-lead:run` load; the SessionStart hook is silent without docs/initiatives and, in a sample project, injects the status and the agent proposes next steps and waits.
- Not run here: the full dry run up to the gate (brainstorming is interactive and stops a headless run at its first question). To do in a new interactive session: `/tech-lead:run <sample spec with a UI>`.
- Final whole-branch review dispatched (opus/medium).

## 2026-11-12 wave 5
Tasks done: 9

## 2026-11-12 session

- Done: all 9 tasks in 5 waves, autopilot. Final whole-branch review (opus/medium): ready with fixes; one fix wave (session-start brief no longer halts work in progress, deferred findings copied to backlog at finish, wave base recorded for resume, re-gate journal entry, checkpoint commands get no stdin, scout `copy` with attribution), scoped re-review clean. 91 tests pass, also on Python 3.9 per the final reviewer.
- Open: backlog B1 (interactive dry run up to the gate, needs a new session) and B2-B11 (minor polish and test gaps from the reviews).
- Next: user decides on merging PR #1; then B1.
