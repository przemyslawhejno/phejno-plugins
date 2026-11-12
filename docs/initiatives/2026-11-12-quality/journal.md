# tech-lead quality: journal

## 2026-11-12 session

- Requested by the user: keep code and tests free of obsolete content after many iterations, faster test suites, minimal comments (no history, the code speaks for itself), and a risk-scaled panel of parallel experts for best quality.
- Checked what superpowers and the engineering plugin already cover; the design references them instead of copying.
- Draft spec written; independent design review requested by the user before approval.
- Added on request: UI/UX expert and current UI standards for projects with a graphical interface (Part 3); the running design review covers Parts 1-2, a scoped round will cover Part 3.

## 2026-11-12 design review, round 1 (opus/medium)

- Report: research/design-review.md. Verdict: DESIGN NEEDS CHANGES, 6 blocking, 8 minor, 5 gaps. Verified at the source: model-manager routes the named review agents to opus high/xhigh and sonnet high; dispatching-parallel-agents excludes related failures.
- Accepted all blocking (hygiene pass only for plans with 3+ code tasks or `replaces`; suite command, median timing, 20% + 2 s per-test rule, ratchet in standards.md; whole-suite inventory by haiku; explicit model/effort on every lens; escalation cause `unknown` with one investigation before any panel; `risk` field mapping risks to lenses), all minor, gaps 1-4; gap 5 covered by the `[hygiene]` audit trigger.
- Round 2 (scoped to the changes and the new Part 3 UI/UX) next.

## 2026-11-12 design review, round 2 (opus/medium, scoped to changes and Part 3)

- Verdict: DESIGN NEEDS CHANGES, 2 blocking, 11 minor. Last allowed round; fixes applied without a third.
- R2-B1: per-task `ui-ux` lens only with new risk `ux` (screen, flow or component change; required on every non-haiku `kind: ui` task); haiku style or copy fixes rely on the axe check and the batch review; the lens replaces the batch review's mockup check. The UI/UX expert still always reviews spec and mockup and the changed flows at the finish (user's requirement for GUI projects).
- R2-B2: a render harness task in the first UI wave (Playwright, axe-core, Lighthouse CI via prior art, shown at the gate); `verify` writes screenshots, axe JSON and Lighthouse summary to scratch; reviewers only read them; "not rendered" fallback.
- Minor 1-11 applied: hygiene trigger needs 2+ tasks with `replaces`; inventory also on added test files; lens yield persisted in standards.md; first timing seeds the ratchet only when absent; WCAG 2.2 criteria named (2.5.8 over 2.5.5); Core Web Vitals as field target with Lighthouse lab budgets; Fluent 2 and platform accessibility APIs; opus for ui-ux keyed on risk `system-wide`; design skills briefed with mockup and harness output, no questions to the user, `design-handoff` dropped, `design-system` added; keyboard and focus read in code; finish UI pass on sonnet medium.
- Next: user approval of the design.

## 2026-11-12 spec approved, planning

- User approved the spec; autopilot carries on from the earlier agreement (ledger `mode: autopilot`).
- Ruling: schema 2 gates every new ledger rule, so the finished 0.1.0 ledger stays valid — without it status.py would show the done initiative as a ledger error — cost if wrong: one extra field per new ledger.
- Suite baseline: median 1.58 s, 91 tests (3 runs).
- Added on request mid-planning: Part 4, codemap integration (navigation through the index, pending sync across lanes at checkpoint, session-start proposals for /codemap, finish update or rebuild). Found while reading claude-codemap 0.5.0: its PostToolUse hook records lane-worktree edits with wrong paths, hence the checkpoint sync. New Task 10.
- Plan and ledger written; plan review next.

## 2026-11-12 plan review, round 1 (opus/medium)

- Report: research/plan-review.md. Verdict: PLAN NEEDS CHANGES, 2 blocking, 10 minor; all accepted.
- B1: Task 3 tests lenses against a literal list; the cross-check with `ledger_core.LENSES` moves to Task 7. B2: corrected codemap commands (a full rebuild is plain `/codemap`; `/codemap update` only processes `pending.md`) in spec, Task 4 and Task 10.
- Minor: exact test edits named in Tasks 5 and 6; haiku tasks cannot carry a risk; Task 4 told the placeholders Task 3 writes; inventory before the hygiene wave; hygiene timing fallback to a `[hygiene]` backlog item and three timings in the report; `sync_codemap` drops `.claude/codemap/` and keeps deleted paths; codemap brief line only in a non-empty brief; full-suite verify for Tasks 3, 4, 6; Task 7 moved to wave 3.
- Ruling: the hygiene pass covers scripts and tests only; skill and prompt documents were reviewed by their own tasks — cost if wrong: noise in documents survives until the next pass.
- Ruling: Task 1 (`docs/standards.md`) is committed before the wave 1 base is taken, so the checkpoint does not flag it out of scope — cost if wrong: none.

## 2026-11-12 plan review, round 2 (sonnet/medium, scoped)

- PLAN APPROVED; one minor finding left as is (Task 4's test term is written by Task 3 per its brief).

## 2026-11-12 gate (autopilot)

- Status note posted; execution starts. 10 tasks in 5 waves: sonnet 7, opus 1, lead 2.

## 2026-11-12 wave 1
Tasks done: 1, 2, 3, 4
Task 3: Ruling: gaps found while following batch-review-prompt.md (none placeholders, lenses per task, implementer report path, severity scale) are Important though reported as observations — every future reviewer hits them — cost if wrong: one fix round
Task 4: Ruling: the cross-lane reference failure is expected within wave 1 and is verified by the wave checkpoint after both lanes merge — tasks in one wave may reference each other's new files by plan contract — cost if wrong: one fix round after merge
Task 3: Ruling: lens-review-prompt "up to 4 tasks" conflicts with one dispatch per lens per wave; fixed at integration after the wave 1 merge (file is in lane-1) — cost if wrong: one small fix dispatch

## 2026-11-12 wave 2
Tasks done: 5, 6
Timing: Task 5 1.9s, Task 6 1.7s, checks 0.0s
- Out-of-scope lines in wave 2 are the lead's integration fix (bda4c29), expected.

## 2026-11-12 wave 3
Tasks done: 7, 10
Timing: Task 7 2.2s, Task 10 2.2s, checks 0.0s
