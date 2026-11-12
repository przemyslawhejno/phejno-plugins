# tech-lead 0.3.1 superdesign polish: journal

## 2026-11-12 session

- The user asked to execute B17 ("B17 wykonaj"); treated as advance agreement to go to implementation (autopilot), merge left to the user.
- Final-review minors 1, 2, 3, 5, 6 were already fixed in 0.3.0; the rest are decided in the spec. Ruling: superdesign source names no CDN hosts, so remote scripts must carry a pinned version instead of an allowlisted host — cost if wrong: an unpinned script the builder could not pin is removed from the mockup.
- One task (sonnet medium, risk security with the security lens) plus lead verification; hygiene pass not required (one code task, no replaces).

## 2026-11-12 plan review, round 1 (sonnet/medium)

- PLAN NEEDS CHANGES: 2 Important, 4 Minor; all accepted. Decision 8 now baselines `git status --porcelain --ignored` before dispatch and never reverts automatically (the old rule could have destroyed the user's uncommitted work and missed ignored paths); decision 5 defines pinned as a full `x.y.z` version and rebuilds locally on failure; tests tightened.

## 2026-11-12 plan review, round 2 (sonnet/low, scoped)

- PLAN APPROVED; two minors applied to the spec (package names as the match key; stated limits of the baseline comparison). Execution starts (autopilot).
