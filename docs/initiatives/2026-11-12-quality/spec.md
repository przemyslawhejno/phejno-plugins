# tech-lead 0.2.0: code hygiene, expert panels and UI/UX — design (approved 2026-11-12)

Date: 2026-11-12

## Goal

Three additions to the `tech-lead` plugin (0.1.0 spec: `docs/initiatives/2026-11-11-tech-lead/spec.md`):

1. **Hygiene.** After many iterations a project keeps no obsolete code, no obsolete or duplicated tests and no noise comments, and its test suite gets faster rather than slower.
2. **Expert panels.** Each task gets the parallel experts its risk justifies, decidable from ledger data, and the lead learns from their yield which experts pay off.
3. **UI/UX.** Every project with a graphical interface gets a UI/UX expert at spec, review and finish, and follows current standards.
4. **Codemap.** tech-lead navigates through the `claude-codemap` index when present, keeps it fresh across lanes, and proposes mapping when it would pay off.

All three reference existing skills instead of copying them, and work without them. The standing goal holds: maximum quality at the lowest token, time and cost; no stronger model or extra agent where it adds nothing.

## What already exists (not duplicated)

- `superpowers:test-driven-development` and `writing-good-tests.md`: Red-Green-Refactor, "Name the Break", exercise the real thing, the mutation check.
- SDD reviewer rubric: separation of concerns, error handling, DRY; Important for verbatim duplication, swallowed errors, tests that assert nothing.
- `superpowers:systematic-debugging`: one hypothesis at a time. `superpowers:dispatching-parallel-agents`: parallel work on independent problems only.
- Optional `engineering`: `code-review`, `testing-strategy`, `tech-debt`, `system-design`, `architecture`, `debug`. Optional `design`: `design-critique`, `accessibility-review` (WCAG 2.1 AA), `ux-copy`, `design-system` — interactive commands that expect a mockup, screenshot or description. Optional `modern-web-guidance`.
- `security-review` and `simplify` review a branch's pending changes, not one lane task's diff; tech-lead uses them only where a whole branch or working tree is the subject.
- Named review agents (`pr-review-toolkit:*`) may not be installed; where they are, model-manager routes them to opus high/xhigh or sonnet high unless the call passes `model` and `effort`.

Gaps none of them covers: comment policy; removing what a behaviour change made obsolete; duplicates across the whole suite; suite speed as a measured requirement; choosing experts by risk; current UI standards.

## Ledger additions

| Field | Where | Values | Default |
|---|---|---|---|
| `schema` | top level | `2`; the rules below apply only to ledgers with `schema: 2`, so 0.1.0 ledgers stay valid | absent (0.1.0 rules) |
| `ui` | top level | boolean | `false` |
| `kind` | task | `code`, `ui`, `hygiene` | `code` (`lead` tasks: ignored) |
| `risk` | task | list of `security`, `data`, `irreversible`, `system-wide`, `ux` | `[]` |
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

`Lens yield`: one line per lens, updated at each finish (Part 2).

### Suite timing

- `ledger.py checkpoint` prints each command's wall time (`Task 3: pass (2.1s)`, `Checks: pass (14.8s)`); the wave journal entry records them.
- Timing the suite means: the median of 3 runs of the `Suite` command, or one run when a single run exceeds 4 minutes (then in the background per model-manager, the log triaged by haiku low). When `checks` contains the suite command, the last checkpoint timing counts as one run.
- At the first wave the lead times the suite and records it in `journal.md`; it becomes the ratchet only when `standards.md` has no `Suite time` yet. At the finish it times the suite again.
- Regression: the time per test grew by more than 20% **and** the total grew by more than 2 seconds compared with the ratchet. Then the hygiene pass gets the slowest tests (the runner's durations report, top 10) as a target; if it cannot recover, a `[hygiene]` backlog item records both numbers.
- At the finish, when there is no regression, `Suite time` in `standards.md` is updated, so the ratchet carries across initiatives.

### Obsolete and duplicate test discovery

Before the batch review of a wave with any `replaces` or any added test file, and before the hygiene pass, a haiku low inventory dispatch searches the **whole** test tree (and the code tree, for removed symbols) for the symbols, strings and behaviours the changed tasks touched or removed. When installed, it also runs a dead-code tool (`vulture`, `knip`, or the stack's equivalent) and coverage contexts. It writes candidates to `research/hygiene-candidates-<wave>.md`; reviewers and the hygiene task receive that path.

### Briefs and reviews

- Implementer briefs: "leave the area cleaner" — remove what the change made dead, list it in the report, follow `standards.md` Hygiene.
- `batch-review-prompt.md`: obsolete code or test left behind, or a new test duplicating one in the candidates file or the diff, is **Important**; a noise comment is **Minor**.
- `plan-review-prompt.md`: each behaviour change names its `replaces`; planned tests do not duplicate existing ones.

### Hygiene pass

- Required when the plan has at least 3 tasks of kind `code` or `ui`, or at least 2 such tasks and any of them has a non-empty `replaces`. Otherwise each task cleans up after itself and the batch review's hygiene checks suffice.
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

- Each `risk` needs at least one matching lens: `security` → `security`; `data` → `data`; `irreversible` → `data`, `api` or `architecture`; `system-wide` → `architecture` (or `ui-ux` on a `kind: ui` task); `ux` → `ui-ux`.
- Further lenses only when the task's files are in the lens's domain (`performance` on a hot path, `errors` on error handling, `tests` on test infrastructure), with the reason in `reason`.
- Tasks on haiku, or sonnet low with no `risk`, have no lenses.
- At most 4 lenses per task.
- `ledger.py check` enforces the first, third and fourth rules and rejects unknown lens names and lenses on `lead` tasks.

### Dispatch

- One dispatch per lens per wave, covering every task of the wave that lists it, in the same message as the batch reviews. Brief: `lens-review-prompt.md` with `{{LENS}}`, `{{TASKS}}` (task id, brief path, diff path per task), `{{SPEC_PATH}}`, `{{STANDARDS_PATH}}`, `{{LENSES_PATH}}`, `{{CANDIDATES_PATH}}`, `{{REPORT_PATH}}`.
- The lead always passes `model` and `effort` on the call, overriding model-manager's routing: sonnet medium; opus medium for `security` and `architecture` on tasks with a risk, and for `ui-ux` on tasks with risk `system-wide`. A named agent from the table is used only for tasks with a risk, given the diff path.
- A lens finding enters the task's fix loop like a review finding; the lens that raised it re-reviews only the fix diff. Any Important finding blocks the task.
- At the finish, the whole-branch `security-review` is skipped when every task with risk `security` had the `security` lens and nothing outside those tasks touched security code.

### Yield

The wave journal entry records each lens's result: `Lens yield: security 1 Important, 2 Minor; data 0`. The finish report sums yield per lens. At the finish the lead also updates a `Lens yield` section in `standards.md`: per lens, the initiatives it ran in, its Important findings in total, and the count of consecutive initiatives with none. A lens at three or more such initiatives is flagged by the plan review when chosen without a risk, so lenses that do not pay off fall away.

## Part 3: UI and UX

Applies to every project with a graphical interface (web, desktop, mobile): the ledger has `"ui": true`. The UI/UX expert always reviews the spec and mockup and the changed flows at the finish; per task it is risk-scaled like every other lens.

### Current standards

`docs/standards.md` gets a `UI` section (stricter existing conventions win; weaker ones are raised with the user's approval):

- Accessibility: WCAG 2.2 level AA, explicitly including 2.4.11 Focus Not Obscured (Minimum), 2.5.7 Dragging Movements, 2.5.8 Target Size (Minimum, 24×24 CSS px), 3.2.6 Consistent Help, 3.3.7 Redundant Entry, 3.3.8 Accessible Authentication (Minimum); 4.1.1 Parsing is obsolete. Where a WCAG 2.1 checklist (such as `design:accessibility-review`) cites 2.5.5 Target Size (44×44 px, level AAA), 2.5.8 governs at AA.
- Performance (web): Core Web Vitals "good" at the 75th percentile of field data (LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1) is the production target; the verify gate uses lab budgets (Lighthouse: LCP ≤ 2.5 s, CLS ≤ 0.1, TBT ≤ 200 ms as the INP proxy).
- Web platform choices (HTML, CSS, client JS) checked against `modern-web-guidance` when installed; native and desktop apps follow current platform guidelines (Apple Human Interface Guidelines, Material Design 3, Fluent 2) and expose controls through the platform accessibility API.
- Responsive from the smallest supported viewport; light and dark themes when the product has both; empty, loading, error and success states designed.
- A design system or component library from prior art before custom components; design tokens instead of hard-coded values (`design:design-system` when installed).

### Render harness

- The first wave that contains a `kind: ui` task includes a harness task (`kind: code`) unless the project has one: for the web, Playwright with `@axe-core/playwright` and Lighthouse CI, chosen through prior art and listed in the ledger's `reuse`, so `show` presents the new dependencies at the gate; for native apps, the platform's UI test and accessibility audit tooling when it exists.
- A `kind: ui` task's `verify` runs the harness for its screens and writes screenshots (mobile and desktop widths), the axe JSON and the Lighthouse summary to `.tech-lead/scratch/<initiative>/task-<N>/`. Reviewers read these files and run nothing.
- When the stack has no harness (no browser download possible, no native tooling), `verify` runs the remaining checks and the reviewers review code against the mockup, reporting "not rendered".

### UI/UX expert

| Stage | Work | Model |
|---|---|---|
| Spec and mockup | Reviews spec and `mockup.html` before the user sees them: flows, hierarchy, states, copy, accessibility, responsiveness, the standards above. The mockup builder fixes the findings (resumed); then the user reviews spec and mockup together. | sonnet medium; opus medium when the initiative is a new product UI or a redesign (the lead records this as risk `system-wide` on the UI tasks) |
| Per task | The `ui-ux` lens (Part 2), only for tasks with risk `ux`; it reads the harness output, compares with the mockup, checks the UI standards, copy and states, and checks keyboard order and focus by reading the code, because axe finds only part of the issues. For a task with the lens, the batch review skips its mockup check. | Part 2 dispatch rule |
| Finish | One pass over the changed flows when more than one `kind: ui` task ran, using the last harness output. | sonnet medium |

- Risk `ux`: the task adds or changes a screen, a user flow or a component. A `kind: ui` task not on haiku must carry `ux`; a haiku `kind: ui` task (a style or copy fix) is covered by its axe check and the batch review's mockup check.
- Briefs for experts that use `design:design-critique`, `design:accessibility-review`, `design:ux-copy` or `design:design-system` give them the mockup path and the harness output, and forbid questions to the user: these are interactive commands that otherwise ask for a Figma link or a description.
- `ledger.py check`: a `kind: ui` task not on haiku without risk `ux`; `kind: ui` in a ledger without `"ui": true`.

## Part 4: Codemap

The `claude-codemap` plugin keeps `.claude/codemap/` (`INDEX.md`, `symbols.md`, topic files) and tracks edited files in `pending.md` through a PostToolUse hook. Its thresholds: up to 15 pending files are updated inline (`codemap-usage` skill), 16-50 by `/codemap update` (haiku writers), more than 50 by a full `/codemap` rebuild (sonnet planner plus haiku writers). tech-lead uses it when the index exists and proposes it when it would pay off; without the plugin nothing changes.

### Using the index

- When `.claude/codemap/INDEX.md` exists, the lead and every subagent brief navigate through it before Glob or Grep: `symbols.md` for a named symbol, `INDEX.md` then 1-2 topic files for a concept (the `codemap-usage` skill). This applies to orientation, standards discovery, prior-art scouting of the own repository, spikes, planning (task `files` taken from topic files), implementer briefs, reviews, lenses and the inventory step.
- Briefs carry one line with the absolute paths of `INDEX.md` and `symbols.md`; they do not paste index content.

### Keeping it fresh

- Edits made in lane worktrees reach `pending.md` with wrong paths, because the hook resolves paths against the session's directory. So `ledger.py checkpoint --mark`, when `.claude/codemap/` exists, appends the paths from `git diff --name-only REF..HEAD` to `pending.md`, drops entries under `.worktrees/` and `.claude/codemap/` (as the hook does), keeps deleted paths (the update procedure drops unmapped ones), de-duplicates, and prints `Codemap: <n> pending (<action>)` where the action is `inline`, `update` or `rebuild` by the thresholds above.
- After each wave checkpoint, when the action is `update`, the lead runs the `/codemap update` procedure (haiku writers, cheap); `inline` is left to the next navigation (the `codemap-usage` skill handles it); `rebuild` waits for the finish.
- At the finish, the lead brings the index up to date: `update` when pending, a full rebuild when the action is `rebuild` or the initiative moved or renamed modules. In autopilot it runs it; otherwise it proposes it in the finish report. The index is committed with the initiative.

### Proposing cyclic mapping

`status.py` reports codemap health, and the session-start brief turns it into a proposed next step:

| State | Brief line |
|---|---|
| No `.claude/codemap/`, 30 or more tracked code files | `Codemap: none for <n> code files — propose /codemap (claude-codemap plugin)` |
| `pending.md` 16-50 unique paths | `Codemap: <n> pending — propose /codemap update` |
| `pending.md` over 50, or `symbols.md` missing | `Codemap: stale — propose /codemap (full rebuild)` |
| `INDEX.md` `Generated:` older than 30 days with 20 or more commits since | `Codemap: <days> days old, <commits> commits since — propose /codemap (full rebuild)` |
| otherwise | nothing |

Code files are `git ls-files` entries outside `docs/`, `.claude/` and dot directories; any git failure skips the line. The brief shows the codemap line only when it is otherwise non-empty (initiatives exist). `/codemap update` only processes `pending.md`; a full rebuild is plain `/codemap`. The full status gains a `## Codemap` section with the same facts.

## Changes by file

- `skills/tech-lead/SKILL.md`: standards sections; suite timing and ratchet; inventory step; hygiene pass rule; expert stages, lens choice, dispatch and yield; escalation cause `unknown`; UI/UX stages and render harness.
- `skills/tech-lead/layout.md`: `standards.md` Hygiene, Suite, Lens yield and UI sections; `[hygiene]` backlog tag; journal lines for suite time and lens yield.
- New `skills/tech-lead/lenses.md`, `lens-review-prompt.md`, `inventory-prompt.md`.
- `batch-review-prompt.md`, `plan-review-prompt.md`, `mockup-prompt.md`: hygiene, candidates, risk/expert checks, UI standards, the UI/UX review loop, harness output paths.
- `scripts/status.py`: codemap health in the full status and the brief. `ledger_checkpoint.py`, `ledger.py`: codemap pending sync on `--mark`.
- `scripts/ledger_core.py`: new fields and rules. `ledger_checkpoint.py`, `ledger.py`: timings. `ledger_report.py`: Risk and Experts columns, lens totals.
- Tests, README, plugin and marketplace version `0.2.0`.
- Finish: a hygiene pass over the plugin itself.

## Out of scope

- Competing parallel implementations of one task.
- Building deduplication or dead-code tooling; existing tools are used when installed.
- Changing superpowers, engineering, design or model-manager.
