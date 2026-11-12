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

## 2026-11-12 final review (opus/medium)

- Ready with fixes: 1 Important (security-lens minors not recorded → backlog B20), fix-now minor (case-insensitive http-equiv in the export bullet), optional wording items folded into the fix wave.
- From the user's dom-z-widokiem CLAUDE.md (commit 33da20b, a bullet in Work Tracking, not a ## Project docs heading): B18 must detect the rule by content (any mention routing specs and plans to docs/initiatives/), not by heading, or it adds a duplicate. Folded into the fix wave.
- Proposed to the user: B19, status.py finds docs/initiatives/ at the git top level when the session starts in a subdirectory (dom-z-widokiem sessions start in topology/).

## 2026-11-12 wave 3
Tasks done: 2
Timing: checks 0.0s

## 2026-11-12 session

- Done: tech-lead 0.3.1 — B17 (superdesign wording and safety: consent names every channel, exact CDN URL shapes, a Content-Security-Policy always replaced and first in the mockup head, baseline check after the repository analysis that fails closed and never reverts user work, ids only in the journal) and B18 (the lead adds a `## Project docs` section to CLAUDE.md unless CLAUDE.md already routes specs and plans to docs/initiatives/; asks first when CLAUDE.md has uncommitted changes). This repository now has a CLAUDE.md with that section.
- 3 tasks in 3 waves on autopilot: sonnet 2, lead 1. The security lens ran on Task 1 twice more after fixes (4 Important in total, all fixed). Final review (opus/medium): ready with fixes; one fix wave, scoped re-review clean.
- Open: B1 (live run), B19 (proposed: status from a subdirectory session, awaiting the user), B20 (security leftovers).
- Next: user decides on merging the PR and on B19.
