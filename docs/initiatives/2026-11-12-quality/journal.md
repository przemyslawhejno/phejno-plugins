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
