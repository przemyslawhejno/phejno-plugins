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
