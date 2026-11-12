# tech-lead 0.3.1 superdesign polish: journal

## 2026-11-12 session

- The user asked to execute B17 ("B17 wykonaj"); treated as advance agreement to go to implementation (autopilot), merge left to the user.
- Final-review minors 1, 2, 3, 5, 6 were already fixed in 0.3.0; the rest are decided in the spec. Ruling: superdesign source names no CDN hosts, so remote scripts must carry a pinned version instead of an allowlisted host — cost if wrong: an unpinned script the builder could not pin is removed from the mockup.
- One task (sonnet medium, risk security with the security lens) plus lead verification; hygiene pass not required (one code task, no replaces).

## 2026-11-12 plan review, round 1 (sonnet/medium)

- PLAN NEEDS CHANGES: 2 Important, 4 Minor; all accepted. Decision 8 now baselines `git status --porcelain --ignored` before dispatch and never reverts automatically (the old rule could have destroyed the user's uncommitted work and missed ignored paths); decision 5 defines pinned as a full `x.y.z` version and rebuilds locally on failure; tests tightened.

## 2026-11-12 plan review, round 2 (sonnet/low, scoped)

- PLAN APPROVED; two minors applied to the spec (package names as the match key; stated limits of the baseline comparison). Execution starts (autopilot).
- The user asked whether superpowers find the documents without tech-lead (only through the tech-lead SessionStart hook; superpowers default to docs/superpowers/). B18 added on request and folded into this initiative as Task 3 (sonnet low) plus a CLAUDE.md for this repository in lead verification. Ruling: no separate plan review for this one-section addition; it goes through batch review and the final review — cost if wrong: a wording gap caught later.

## 2026-11-12 wave 1
Tasks done: 1
Timing: Task 1 1.0s, checks 0.0s
- Wave 1 (B17) done. Lens yield: security 4 Critical/Important (3 + 1 after the first fix), 7 Minor; all Important fixed over two fix rounds and re-reviewed by the lens. Two lens minors moved into Task 3.

## 2026-11-12 wave 2
Tasks done: 3
Timing: Task 3 1.1s, checks 0.0s
