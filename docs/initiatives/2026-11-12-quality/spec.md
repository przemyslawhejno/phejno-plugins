# tech-lead 0.2.0: code hygiene, expert panels and UI/UX — design (draft, round 2)

Date: 2026-11-12

## Goal

Three additions to the `tech-lead` plugin (0.1.0 spec: `docs/initiatives/2026-11-11-tech-lead/spec.md`):

1. **Hygiene.** After many iterations a project keeps no obsolete code, no obsolete or duplicated tests and no noise comments, and its test suite gets faster rather than slower.
2. **Expert panels.** Each task gets the parallel experts its risk justifies, decidable from ledger data, and the lead learns from their yield which experts pay off.
3. **UI/UX.** Every project with a graphical interface gets a UI/UX expert at spec, review and finish, and follows current standards.

All three reference existing skills instead of copying them, and work without them. The standing goal holds: maximum quality at the lowest token, time and cost; no stronger model or extra agent where it adds nothing.

## What already exists (not duplicated)

- `superpowers:test-driven-development` and `writing-good-tests.md`: Red-Green-Refactor, "Name the Break", exercise the real thing, the mutation check.
- SDD reviewer rubric: separation of concerns, error handling, DRY; Important for verbatim duplication, swallowed errors, tests that assert nothing.
- `superpowers:systematic-debugging`: one hypothesis at a time. `superpowers:dispatching-parallel-agents`: parallel work on independent problems only.
- Optional `engineering`: `code-review`, `testing-strategy`, `tech-debt`, `system-design`, `architecture`, `debug`. Optional `design`: `design-critique`, `accessibility-review` (WCAG 2.1 AA), `ux-copy`, `design-handoff`. Optional `modern-web-guidance`.
- `security-review` and `simplify` review a branch's pending changes, not one lane task's diff; tech-lead uses them only where a whole branch or working tree is the subject.
- Named review agents (`pr-review-toolkit:*`) may not be installed; where they are, model-manager routes them to opus high/xhigh or sonnet high unless the call passes `model` and `effort`.

Gaps none of them covers: comment policy; removing what a behaviour change made obsolete; duplicates across the whole suite; suite speed as a measured requirement; choosing experts by risk; current UI standards.

## Ledger additions

| Field | Where | Values | Default |
|---|---|---|---|
| `ui` | top level | boolean | `false` |
| `kind` | task | `code`, `ui`, `hygiene` | `code` (`lead` tasks: ignored) |
| `risk` | task | list of `security`, `data`, `irreversible`, `system-wide` | `[]` |
| `experts` | task | list of lens names (Part 2) | `[]` |
| `replaces` | task | existing paths or test names this task makes obsolete and removes | `[]` |

`ledger.py check` adds the rules stated in Parts 1-3. `ledger.py show` adds `Risk` and `Experts` columns and, in the summary, the number of lens dispatches per wave.

## Part 1: Hygiene

### Standards

When the lead creates or discovers `docs/standards.md`, it adds two sections. Existing project conventions win where they are stricter; a weaker convention is raised only with the user's approval, recorded as a ruling.

`Hygiene`:
- Comments only where the code cannot say it: why, a non-obvious constraint, a workaround with its link. No change history, no commented-out code, no restating the code, no TODO without a backlog id (`B<n>`). History lives in git.
- A change of behaviour removes the code and tests it made obsolete in the same task, listed in the task's `replaces`.
- One behaviour, one test: a new test extends or replaces an existing one instead of duplicating it, anywhere in the suite.
- Tests follow `writing-good-tests.md`; strategy follows `engineering:testing-strategy` when installed.
- Speed: the fastest test level that proves the behaviour, no sleeps, shared fixtures for expensive setup.
- Mechanical enforcement: where the stack has them, the lint rules for commented-out code and untracked TODOs (for example ruff `ERA001` and `FIX002`, ESLint `no-warning-comments`) go into `Checks`; otherwise a grep command does.

`Suite`:
- `Suite: <command>` — the full test suite command; `Suite time: <seconds>s (<date>, <test count> tests)` — the ratchet.

### Suite timing

- `ledger.py checkpoint` prints each command's wall time (`Task 3: pass (2.1s)`, `Checks: pass (14.8s)`); the wave journal entry records them.
- Timing the suite means: the median of 3 runs of the `Suite` command, or one run when a single run exceeds 4 minutes (then in the background per model-manager, the log triaged by haiku low). When `checks` contains the suite command, the last checkpoint timing counts as one run.
- At the first wave the lead records the suite time in `journal.md`; at the finish it times the suite again.
- Regression: the time per test grew by more than 20% **and** the total grew by more than 2 seconds compared with the ratchet. Then the hygiene pass gets the slowest tests (the runner's durations report, top 10) as a target; if it cannot recover, a `[hygiene]` backlog item records both numbers.
- At the finish, when there is no regression, `Suite time` in `standards.md` is updated, so the ratchet carries across initiatives.

### Obsolete and duplicate test discovery

Before the batch review of a wave with any `replaces`, and before the hygiene pass, a haiku low inventory dispatch searches the **whole** test tree (and the code tree, for removed symbols) for the symbols, strings and behaviours the changed tasks touched or removed. When installed, it also runs a dead-code tool (`vulture`, `knip`, or the stack's equivalent) and coverage contexts. It writes candidates to `research/hygiene-candidates-<wave>.md`; reviewers and the hygiene task receive that path.

### Briefs and reviews

- Implementer briefs: "leave the area cleaner" — remove what the change made dead, list it in the report, follow `standards.md` Hygiene.
- `batch-review-prompt.md`: obsolete code or test left behind, or a new test duplicating one in the candidates file or the diff, is **Important**; a noise comment is **Minor**.
- `plan-review-prompt.md`: each behaviour change names its `replaces`; planned tests do not duplicate existing ones.

### Hygiene pass

- Required when the plan has at least 3 tasks of kind `code` or `ui`, or any task with a non-empty `replaces`. Otherwise the batch review's hygiene checks suffice.
- One task of kind `hygiene`, sonnet medium, depending on every `code` and `ui` task. `files`: the union of those tasks' files plus their test directories. `verify`: the `Suite` command. Acceptance: suite green; no regression by the rule above.
- It removes dead code, merges duplicate tests, deletes obsolete tests and noise comments, using the candidates file, and runs `simplify` on its working tree when installed.
- `ledger.py check`: a required hygiene task is missing, or it does not depend on every `code`/`ui` task.

### Periodic audit

At the finish, when `docs/backlog.md` has 10 or more open `[hygiene]` items, or the suite regressed and the hygiene pass could not recover it, the lead proposes a cleanup initiative prioritised with `engineering:tech-debt` when installed. The backlog line format gains an optional tag: `- [ ] B<n> [hygiene] <title> — from … — <date>`.

## Part 2: Expert panels

### Where experts are used

| Stage | Experts | Rule |
|---|---|---|
| Architectural choice | 2-3 independent proposals, sonnet medium (opus medium when the task has a risk) | Only when spikes and prior art leave 2 or more viable options. Ambiguous requirements go to brainstorming with the user, never to a panel. The lead compares, or a fable subagent when the decision is beyond the lead's model; the decision becomes an ADR (`engineering:architecture` when installed). |
| Hard bug | 1, then at most 3 | New escalation cause `unknown`: first one sonnet medium investigation following `superpowers:systematic-debugging`. Only when it ends with 2 or more concrete competing hypotheses, one expert per hypothesis, each in its own scratch worktree under `.tech-lead/scratch/` so it can experiment; `dispatching-parallel-agents` for the dispatch mechanics. The lead picks the confirmed cause; one implementer fixes it. |
| Task review | batch reviewer plus lenses | Below. |
| Implementation | one implementer per task | Parallel implementers on the same code conflict. |

### Lenses

`lenses.md` in the skill directory: a short checklist per lens and what it uses when installed.

| Lens | Checks | Uses when installed |
|---|---|---|
| `security` | input validation, authn/authz, secrets, injection, dependencies | `engineering:code-review` security dimension |
| `data` | migrations, consistency, reversibility, backups | — |
| `api` | contracts, backward compatibility, error shapes | — |
| `architecture` | module boundaries, dependencies, coupling, types | `engineering:code-review` maintainability; `pr-review-toolkit:type-design-analyzer` |
| `performance` | complexity, queries, memory, hot paths | `engineering:code-review` performance dimension |
| `errors` | swallowed errors, silent fallbacks | `pr-review-toolkit:silent-failure-hunter` |
| `tests` | test architecture: fixtures, runners, levels, speed | `engineering:testing-strategy`; `pr-review-toolkit:pr-test-analyzer` |
| `ui-ux` | Part 3 | Part 3 |

### Which and how many

- Each `risk` needs at least one matching lens: `security` → `security`; `data` → `data`; `irreversible` → `data`, `api` or `architecture`; `system-wide` → `architecture`.
- Further lenses only when the task's files are in the lens's domain (`performance` on a hot path, `errors` on error handling, `tests` on test infrastructure), with the reason in `reason`.
- Tasks on haiku, or sonnet low with no `risk`, have no lenses, except `ui-ux` on `kind: ui` tasks.
- At most 4 lenses per task.
- `ledger.py check` enforces the first, third and fourth rules and rejects unknown lens names and lenses on `lead` tasks.

### Dispatch

- One dispatch per lens per wave, covering every task of the wave that lists it, in the same message as the batch reviews. Brief: `lens-review-prompt.md` with `{{LENS}}`, `{{TASKS}}` (task id, brief path, diff path per task), `{{SPEC_PATH}}`, `{{STANDARDS_PATH}}`, `{{LENSES_PATH}}`, `{{CANDIDATES_PATH}}`, `{{REPORT_PATH}}`.
- The lead always passes `model` and `effort` on the call, overriding model-manager's routing: sonnet medium; opus medium for `security` and `architecture` on tasks with a risk. A named agent from the table is used only for tasks with a risk, given the diff path.
- A lens finding enters the task's fix loop like a review finding; the lens that raised it re-reviews only the fix diff. Any Important finding blocks the task.
- At the finish, the whole-branch `security-review` is skipped when every task with risk `security` had the `security` lens and nothing outside those tasks touched security code.

### Yield

The wave journal entry records each lens's result: `Lens yield: security 1 Important, 2 Minor; data 0`. The finish report sums yield per lens. A lens with zero Important findings across three consecutive initiatives is flagged by the plan review when chosen without a risk, so lenses that do not pay off fall away.

## Part 3: UI and UX

Applies to every project with a graphical interface (web, desktop, mobile): the ledger has `"ui": true`.

### Current standards

`docs/standards.md` gets a `UI` section (stricter existing conventions win; weaker ones are raised with the user's approval):

- Accessibility: WCAG 2.2 level AA, including focus not obscured, target size minimum, dragging movements, consistent help, redundant entry and accessible authentication.
- Performance: Core Web Vitals "good" at the 75th percentile: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1.
- Web platform choices (HTML, CSS, client JS) checked against `modern-web-guidance` when installed; native apps follow current platform guidelines (Apple Human Interface Guidelines, Material Design 3).
- Responsive from the smallest supported viewport; light and dark themes when the product has both; empty, loading, error and success states designed.
- A design system or component library from prior art before custom components; design tokens instead of hard-coded values.

### UI/UX expert

| Stage | Work | Uses when installed |
|---|---|---|
| Spec and mockup | Reviews spec and `mockup.html` before the user sees them: flows, hierarchy, states, copy, accessibility, responsiveness, the standards above. The mockup builder fixes the findings (resumed), then the user reviews spec and mockup together. | `design:design-critique`, `design:accessibility-review` plus the WCAG 2.2 additions, `design:ux-copy`, `modern-web-guidance` |
| Planning | Every task creating or changing UI is `kind: ui`; its `verify` includes an automated accessibility check (web: axe-core through Playwright) when the stack allows it. | `design:design-handoff` |
| Review | The `ui-ux` lens on every `kind: ui` task: compares with the mockup using Playwright screenshots at mobile and desktop widths, checks the UI standards, copy and states. | as above |
| Finish | One pass over the changed flows when more than one `kind: ui` task ran. | `design:design-critique` |

- Model: sonnet medium; opus medium for a new product UI or a redesign.
- `ledger.py check`: a `kind: ui` task without the `ui-ux` lens; `kind: ui` in a ledger without `"ui": true`.

## Changes by file

- `skills/tech-lead/SKILL.md`: standards sections; suite timing and ratchet; inventory step; hygiene pass rule; expert stages, lens choice, dispatch and yield; escalation cause `unknown`; UI/UX stages.
- `skills/tech-lead/layout.md`: `standards.md` Hygiene, Suite and UI sections; `[hygiene]` backlog tag; journal lines for suite time and lens yield.
- New `skills/tech-lead/lenses.md`, `lens-review-prompt.md`, `inventory-prompt.md`.
- `batch-review-prompt.md`, `plan-review-prompt.md`, `mockup-prompt.md`: hygiene, candidates, risk/expert checks, UI standards and the UI/UX review loop.
- `scripts/ledger_core.py`: new fields and rules. `ledger_checkpoint.py`, `ledger.py`: timings. `ledger_report.py`: Risk and Experts columns, lens totals.
- Tests, README, plugin and marketplace version `0.2.0`.
- Finish: a hygiene pass over the plugin itself.

## Out of scope

- Competing parallel implementations of one task.
- Building deduplication or dead-code tooling; existing tools are used when installed.
- Changing superpowers, engineering, design or model-manager.
