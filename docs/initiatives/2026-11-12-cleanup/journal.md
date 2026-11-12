# tech-lead 0.2.1 cleanup: journal

## 2026-11-12 session

- The user asked to start the cleanup initiative (backlog B2-B14) after PR #1 was merged; the branch restarted from master (ed680e2).
- Backlog checked against 0.2.0 by haiku low: 9 open, 4 partly done (research/backlog-check.md).
- Spec written with decisions per item; B5 help and B10 test-gap parts closed with reasons.

## 2026-11-12 plan review, round 1 (sonnet/medium)

- PLAN NEEDS CHANGES: 4 Important, 7 Minor; all accepted: Task 5 owns test_skill_docs.py and the B14 wording is fixed; a locale test that can fail (PYTHONUTF8=0, PYTHONCOERCECLOCALE=0); in-process missing-git test; `replaces` on tasks 1-4; status._load_core patch target; explicit closures in Task 7; no hard-coded version test; lens bullet parse rule; tasks 4 and 5 raised to sonnet medium; guard tests must fail without their fix; lanes 1+3+5 and 2+4.

## 2026-11-12 plan review, round 2 (sonnet/low, scoped)

- PLAN APPROVED; two minor findings applied (journal measurement line keeps `Suite time:`; hygiene pass confirms each `replaces` entry is gone). The 136 in the ratchet is correct: it was set at 136 tests.
- Next: gate (this initiative is gated, not autopilot).

## 2026-11-12 gate

- Approved by the user: execution in waves (gated mode; no stop between waves unless a decision is the user's). Superdesign integration discussed; backlog decision pending with the user.

## 2026-11-12 wave 1
Tasks done: 1, 2, 3, 4, 5
Timing: Task 1 2.3s, Task 2 2.3s, Task 3 2.3s, Task 4 2.2s, Task 5 2.1s, checks 0.0s
- Out-of-scope mockup-prompt.md in wave 1 is B8 (expected). Suite after wave 1: median 2.33 s, 156 tests (14.9 ms per test, +39%; total +0.88 s, under the 2 s floor) — target for the hygiene pass.

## 2026-11-12 wave 2
Tasks done: 6
Timing: Task 6 1.0s, checks 0.0s
Task 5: Ruling: mockup-prompt.md edit outside the declared files is B8's own requirement (test asserts id= there) — cost if wrong: none
- Wave 2 done; suite after hygiene: median 1.11 s, 156 tests (7.1 ms per test); ratchet updated in docs/standards.md.
- Backlog B2-B14 closed with notes (closures recorded: B4 files, B5 help, B9 README, B10 test gaps, B11 and B13 parts done in 0.2.0).

## 2026-11-12 wave 3
Tasks done: 7
Timing: checks 0.0s
- Suite time: 1.11s, 156 tests (measured; ratchet 1.11s in standards.md)

## 2026-11-12 session

- Done: tech-lead 0.2.1 — backlog B2-B14 closed (fixes and recorded closures), 7 tasks in 3 waves (gated, approved): sonnet 6, lead 1; haiku for the backlog check and the inventory. Every per-task review clean on the first pass; guard tests verified to fail without their fixes by implementers and reviewers.
- Suite: 137 tests in about 1.4 s at the start, 156 tests in 1.11 s at the finish (7.1 ms per test, ratchet was 10.7 ms); the hygiene pass moved the one-line-error CLI tests in process.
- Final review (opus/medium): ready to merge; two minors fixed at the finish, the rest in backlog B16.
- Open: B1 (interactive dry run), B15 (superdesign initiative, proposed), B16 ([hygiene] leftovers).
- Next: user decides on merging the PR.
