# tech-lead 0.2.0: code hygiene, expert panels and UI/UX — design (draft, under review)

Date: 2026-11-12

## Goal

Two additions to the `tech-lead` plugin (spec of 0.1.0: `docs/initiatives/2026-11-11-tech-lead/spec.md`):

1. **Hygiene.** After many iterations a project keeps no obsolete code, no obsolete or duplicated tests, and no noise comments, and its test suite gets faster rather than slower.
2. **Expert panels.** Each task gets the number of parallel experts its risk and complexity justify, so quality is the best the work needs, without spending experts on routine work.
3. **UI/UX.** Every project with a graphical interface gets a UI/UX expert at spec, review and finish, and follows current standards.

Both reference existing skills instead of copying them, and work without them.

## What already exists (not to be duplicated)

- `superpowers:test-driven-development` and its `writing-good-tests.md`: Red-Green-Refactor, "Name the Break", exercise the real thing, the mutation check, tests ship with the implementation.
- `superpowers:subagent-driven-development` reviewer rubric: separation of concerns, error handling, DRY without premature abstraction; Important for verbatim duplication, swallowed errors, tests that assert nothing.
- `superpowers:brainstorming` / `writing-plans`: YAGNI, DRY, one responsibility per file. `receiving-code-review`: remove unused code (YAGNI).
- `superpowers:dispatching-parallel-agents`: parallel independent investigations.
- Optional `engineering` plugin: `code-review` (security, performance, correctness, maintainability), `testing-strategy` (pyramid, what not to test), `tech-debt` (categories, priority = (impact + risk) x (6 - effort)), `system-design`, `architecture` (ADR), `debug`.
- Optional `simplify` skill: reuse, simplification and efficiency cleanups of changed code.

Gaps none of them covers: comment policy; removing code and tests made obsolete by a behaviour change; duplicate tests across iterations (reviews see only the task diff); test-suite speed as a measured requirement; choosing how many experts a task gets.

## Part 1: Hygiene

### Standards

When the lead creates or discovers `docs/standards.md`, it adds a `Hygiene` section (existing project conventions win where they conflict, recorded as a ruling):

- Comments only where the code cannot say it: why, a non-obvious constraint, a workaround with its link. No change history, no commented-out code, no restating what the code does, no TODO without a backlog id (`B<n>`). History lives in git.
- A change of behaviour removes the code and the tests it made obsolete, in the same task.
- One behaviour, one test. A new test extends or replaces an existing one instead of duplicating it, including tests from earlier iterations.
- Tests follow `superpowers:test-driven-development` `writing-good-tests.md`; test strategy follows `engineering:testing-strategy` when installed.
- Suite speed is a requirement: the fastest test level that proves the behaviour; no sleeps; no repeated expensive setup that a fixture can share.

### Briefs and reviews

- Implementer briefs carry "leave the area cleaner": remove what the change made dead; no history comments; follow `standards.md` Hygiene.
- `batch-review-prompt.md` checks hygiene in the diff and in the tests of the touched modules: obsolete code or test left behind, or a new test duplicating an existing one, is **Important**; a noise comment is **Minor**.
- `plan-review-prompt.md` checks that the plan says which old code and tests a task removes or replaces, and that planned tests do not duplicate existing ones.

### Suite timing

- `ledger.py checkpoint` measures each command's wall time and prints it: `Task 3: pass (2.1s)`, `Checks: pass (14.8s)`; the wave journal entry records the same.
- Before the first wave the lead runs the full suite once and records `Suite baseline: <command> <seconds>s` in `journal.md`.
- At the finish, the lead re-times the full suite. More than 20% slower than baseline without a reason stated in the plan → a hygiene task now (autopilot) or a backlog item with both numbers (gated, if the user declines).

### Hygiene pass

- Every plan that changes code ends its implementation with one task of `"kind": "hygiene"`, depending on all other code tasks: sonnet medium, scoped to the files changed in the initiative and the tests of those modules. It removes dead code, merges duplicate tests, deletes obsolete tests, strips noise comments, uses `simplify` when installed, and must keep the full suite green and not slower than baseline.
- `ledger.py check`: a ledger with at least one non-lead task and no `hygiene` task is an error; the `hygiene` task must be in the last code wave.

### Periodic audit

When the suite is >20% over the initiative's baseline after a hygiene pass, or `docs/backlog.md` holds 10 or more open hygiene items, the lead proposes a cleanup initiative at the finish, prioritised with `engineering:tech-debt` when installed.

## Part 2: Expert panels

### Where experts are used

| Stage | Parallel experts | Rule |
|---|---|---|
| Architectural decision or ambiguous requirement | 2-3 independent proposals | Each expert gets the same brief and designs alone (`engineering:system-design` when installed); the lead, or a fable subagent when the decision is beyond the lead's model, compares and decides; the decision becomes an ADR |
| Hard bug (failed once, cause unknown) | 2-3 hypotheses | Via `superpowers:dispatching-parallel-agents`, read-only, each testing one hypothesis (`engineering:debug` when installed); the lead picks the confirmed cause, then one implementer fixes it |
| Task review | batch reviewer plus lens experts | Below |
| Implementation | always one implementer per task | Parallel implementers on the same code conflict; quality comes from lenses and review |

### Lenses

A new `lenses.md` in the skill directory: for each lens a short checklist and the installed skill or named agent it uses when available.

| Lens | Checks | Uses when installed |
|---|---|---|
| `security` | input validation, authn/authz, secrets, injection, dependencies | `security-review`, `engineering:code-review` security dimension |
| `performance` | complexity, queries, memory, hot paths | `engineering:code-review` performance dimension |
| `data` | migrations, consistency, reversibility, backups | — |
| `ui-ux` | see Part 3; mandatory for `kind: ui` tasks | see Part 3 |
| `tests` | hygiene rules above, duplicates across the suite, speed | `engineering:testing-strategy`, `pr-review-toolkit:pr-test-analyzer` |
| `api` | contracts, backward compatibility, errors | — |
| `architecture` | module boundaries, dependencies, coupling | `engineering:code-review` maintainability, `pr-review-toolkit:type-design-analyzer` |
| `errors` | swallowed errors, silent fallbacks | `pr-review-toolkit:silent-failure-hunter` |

Named agents are routed to a model by model-manager's `agents.json`; a generic lens expert runs on sonnet medium, `security` and `architecture` on opus medium for risky tasks.

### How many

| Task | Lenses |
|---|---|
| Routine (haiku, or sonnet low on 1-2 files, no risk) | 0: the batch review suffices |
| Standard | 0-1, only when the change touches a lens's domain |
| Risky (security, data migration, hard to undo, system-wide) | 2-4 |

- At most 4 lenses per task. Each lens must follow from the files changed or a stated risk; a lens "just in case" is a plan defect.
- All lens experts of a wave go out in one message, with the batch reviews.
- A lens finding enters the same fix loop as review findings; an Important finding from any expert blocks the task.

### Ledger and gate

- Task field `experts`: list of lens names, optional, default `[]`. Task field `kind`: `code` (default), `ui`, `hygiene`, `docs`. Top-level `ui`: boolean, default `false`.
- `ledger.py check`: unknown lens name; more than 4 lenses; `experts` on a `lead` task; missing hygiene task (Part 1).
- `ledger.py show`: an `Experts` column, and in the summary the total number of lens dispatches.
- Plan review checks expert choice both ways: a missing lens on a risky task, a needless lens on a routine one.

## Part 3: UI and UX expertise

Applies to every project with a graphical interface (web, desktop, mobile). The lead records it in the ledger as top-level `"ui": true`.

### Current standards

`docs/standards.md` gets a `UI` section, set when the project has a UI:

- Accessibility: WCAG 2.2 level AA (the current W3C recommendation), including focus visibility, target size, keyboard operation, contrast, reduced motion and accessible names.
- Performance: Core Web Vitals "good" thresholds at the 75th percentile: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1.
- Web platform choices (HTML, CSS, client JS) are checked against `modern-web-guidance` when installed, because platform APIs change faster than model training; native apps follow the current platform guidelines (Apple Human Interface Guidelines, Material Design 3).
- Responsive from the smallest supported viewport; light and dark themes when the product has both; all states designed (empty, loading, error, success).
- A design system or component library comes from prior art before custom components are built; design tokens instead of hard-coded values.

Existing project conventions win where they are stricter; a weaker existing convention is raised to these standards only with the user's approval, recorded as a ruling.

### UI/UX expert

A `ui-ux` expert replaces the `ui` lens. It is mandatory, not risk-scaled, wherever a UI is designed or changed:

| Stage | What the expert does | Uses when installed |
|---|---|---|
| Spec and mockup (step 4) | Reviews the written spec and `mockup.html` before the user sees them: user flows, information hierarchy, states, copy, accessibility, responsiveness, fit with the standards above. The mockup builder fixes its findings; then the user reviews spec and mockup together. | `design:design-critique`, `design:accessibility-review`, `design:ux-copy`, `modern-web-guidance` |
| Planning | Every task that creates or changes UI has `"kind": "ui"`; its `verify` includes an automated accessibility check (for web: axe-core run through Playwright) when the stack allows it. | `design:design-handoff` for component specs |
| Review | Every `kind: ui` task gets the `ui-ux` lens in its wave: compares the result with the mockup (Playwright screenshots at mobile and desktop widths), checks the UI standards, copy and states. | as above |
| Finish | One whole-UI pass over the flows changed in the initiative, when more than one UI task ran. | `design:design-critique` |

- Model: sonnet medium; opus medium for a new product UI or a redesign.
- `ledger.py check`: a `kind: ui` task without `ui-ux` in `experts` is an error; `kind: ui` in a ledger without `"ui": true` is an error.
- The `ui-ux` lens counts toward the 4-lens limit.
- `design:accessibility-review` targets WCAG 2.1 AA; the expert applies it and adds the 2.2 criteria (focus not obscured, target size minimum, dragging movements, consistent help, redundant entry, accessible authentication).

## Changes by file

- `skills/tech-lead/SKILL.md`: hygiene in standards, briefs and finish; suite baseline and timing; expert stages, lens selection and dispatch; version references.
- `skills/tech-lead/layout.md`: `standards.md` Hygiene section; baseline journal line.
- `skills/tech-lead/mockup-prompt.md`: UI standards and the expert review loop.
- `skills/tech-lead/lenses.md` (new), `skills/tech-lead/lens-review-prompt.md` (new, placeholders `{{LENS}}`, `{{TASKS}}`, `{{SPEC_PATH}}`, `{{STANDARDS_PATH}}`, `{{LENSES_PATH}}`, `{{REPORT_PATH}}`).
- `batch-review-prompt.md`, `plan-review-prompt.md`: hygiene and expert checks.
- `scripts/ledger_core.py`: `kind`, `experts` validation, hygiene rule. `scripts/ledger_checkpoint.py` and `ledger.py`: timings. `scripts/ledger_report.py`: Experts column and total.
- Tests for each; README; plugin and marketplace version `0.2.0`.
- Finish: a hygiene pass over the plugin itself (91 tests after 0.1.0 iterations).

## Out of scope

- Competing parallel implementations of the same task.
- Automatic test deduplication tooling; duplicates are found by review and the hygiene pass.
- Changing superpowers or engineering skills.
