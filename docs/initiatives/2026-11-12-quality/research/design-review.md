# Design review: tech-lead 0.2.0 hygiene and expert panels

Reviewer: independent, read-only. Sources checked: the draft spec, tech-lead 0.1.0 (SKILL.md, layout.md, prompts, ledger scripts, 91 tests), model-manager (policy.md, SKILL.md, agents.json), superpowers and engineering skills.

## Claims about existing skills

Mostly accurate: writing-good-tests (Name the Break, Exercise the Real Thing, Tests Ship With the Implementation, mutation check), the SDD reviewer calibration, the tech-debt formula, the code-review dimensions, the testing-strategy pyramid and "Skip" list, and the 91-test count are all correct. Three are wrong or risky:
- `dispatching-parallel-agents` is for *independent* failures. It says "Don't use when failures are related" and points to one agent investigating them together. `systematic-debugging` says "Form Single Hypothesis". Running competing hypotheses on one bug is not what either skill describes (see B5).
- The `pr-review-toolkit:*` agents are not installed here. Where they are installed, `agents.json` routes them expensively (see B4).
- `security-review` and `simplify` are built-in commands that review the current branch's pending changes. They do not review the diff of a single lane task.

## Blocking

**B1. The hygiene task is forced on every plan (Hygiene pass, Ledger and gate).** On a 1-2 task plan, an extra sonnet medium dispatch, its review and its wave cost more than they return. The batch review already checks hygiene. The rule also says "non-lead task", but the goal says "plan that changes code", so a docs-only plan of `kind: docs` tasks would need a hygiene task. Fix: require the hygiene task only when the plan has at least 3 `kind: code` tasks or changes existing behaviour or tests. Otherwise the hygiene check in the batch review is enough. Count only `kind: code` tasks.

**B2. The suite-timing rule is flaky and lets the suite drift slower (Suite timing).**
- One wall-clock run with a pure 20% threshold trips on noise in small suites (0.5s becomes 0.6s).
- The baseline is per initiative, so 19% per initiative compounds without limit, and nothing makes the suite *faster*.
- The checkpoint's per-task `verify` timings measure subsets and cannot be compared with the full suite.
- "Full suite" is not defined anywhere.

Fix:
- Add a `Suite:` command and its last time to `standards.md`. Update the time at each finish so it ratchets across initiatives.
- Take the median of 3 runs. Flag only when the time exceeds both 20% and an absolute floor (for example 2s).
- Allow growth in proportion to the tests added (compare time per test).
- Give the hygiene task the top-10 slowest tests (`--durations` or the runner's equivalent).

**B3. Duplicate and obsolete tests stay invisible (Briefs and reviews, Hygiene pass).** Scoping review to "tests of the touched modules" misses duplicates that live elsewhere: integration tests repeating unit tests, or prompt-text tests spread across files. The spec itself rules out tooling, so goal 1 rests on reviewers who cannot see these tests. Fix: before the review or hygiene pass, run a haiku low inventory step that greps the *whole* test tree for the symbols and strings the initiative changed or removed. Its candidate list goes into the reviewer and hygiene briefs.

**B4. Lens model routing contradicts itself and overspends (Lenses).** `agents.json` routes these agents:
- `silent-failure-hunter`: opus xhigh
- `type-design-analyzer`: opus high
- `pr-test-analyzer`: sonnet high

The spec says lenses run on "sonnet medium, opus medium for risky". A single `errors` lens on a *standard* task would cost more than the batch review. These agents also review a whole branch or PR, not a lane task's diff. Fix: tech-lead passes `model` and `effort` explicitly for every lens dispatch, which overrides the hook. Use the named agents only on risky tasks. Hand every lens the diff path.

**B5. The hard-bug panel conflicts with Escalation and model-manager (Where experts are used).** The Escalation cause table has no "cause unknown" row. model-manager says debugging "starts on sonnet medium". Experts that are read-only cannot run experiments to test a hypothesis. Fix: add an Escalation cause `unknown`. The first step is one sonnet medium `systematic-debugging` investigation. Open a panel only if that investigation ends with 2 or more concrete competing hypotheses. Each hypothesis then gets its own scratch worktree, not read-only access. Cite `dispatching-parallel-agents` only for the dispatch mechanics.

**B6. "How many" cannot be decided or checked (How many, Ledger and gate).** Risk lives only in the free-text `reason`, so `check` cannot enforce the tiers. "Risky: 2-4 lenses" contradicts "a lens just in case is a plan defect": a data migration has one natural lens. Fix: add a `risk` list field (`security`, `data`, `irreversible`, `system-wide`), and have `check` enforce:
- each risk is covered by a matching lens;
- haiku tasks, and sonnet low tasks with no risk, have `experts: []`.

Replace the minimum of 2 with at least 1 lens per risk, at most 4 lenses in total.

## Minor

1. **Ambiguous requirements (Where experts are used).** Sending them to an expert panel bypasses step 3, where brainstorming resolves them *with the user*. Fix: panels only for architectural choices that a spike or prior art left with 2 or more viable options. Name the proposal model: sonnet medium, or opus medium when risky.
2. **Dispatch granularity is ambiguous (`lens-review-prompt.md`).** `{{TASKS}}` is plural, but it is unclear whether a lens is dispatched once per task or once per wave. It is also unclear who re-reviews a lens fix. Fix: one dispatch per lens per wave covering every task that lists it. The lens that raised a finding re-reviews only its fix diff.
3. **Lenses overlap with other reviews.** The `security` lens overlaps the finish `security-review`, and the `tests` lens overlaps the batch review's new hygiene checks. Fix: skip the finish `security-review` when every security-risk task had the lens. Use the `tests` lens only for test-architecture risk.
4. **Mechanical rules are left to agents (Standards).** "No TODO without `B<n>`" and "no commented-out code" can be checked by tools. Fix: put a grep, or the project linter's rule (for example ruff ERA001), into `Checks`.
5. **Undefined trigger (Periodic audit).** "10 open hygiene items" has no definition, because backlog lines have no category. Fix: a `[hygiene]` tag in the backlog line format in `layout.md`.
6. **The hygiene task is underspecified.** Its `files` must be known up front, or the checkpoint flags its edits as out of scope. Its `acceptance` and `verify` are not given, and "not slower than baseline" fails on noise. Fix: files are the union of the other tasks' files plus their test directories. `verify` is the suite command, and timing uses the B2 tolerance.
7. **Extra suite runs and long-job rule (Suite timing).** The baseline and finish runs ignore model-manager's rule that anything over 4 minutes runs in the background with haiku triage. When `checks` already runs the suite, reuse the checkpoint timing instead of adding runs.
8. **`kind: docs` has no consumer (Ledger).** Drop it (YAGNI) or say which rule reads it.

## Gaps (ranked)

1. **No feedback on whether experts pay off.** The ledger counts lens dispatches (cost) but not their yield (value). Record each lens's Important/Minor count in the wave journal, and report yield per lens at the finish. Lenses that keep finding nothing should then be dropped from the tiers. This is the only way to reach "the right number of experts".
2. **No timing trend across initiatives.** Timing has no history beyond one initiative and no per-test breakdown (B2).
3. **No discovery of duplicates and dead code across the whole suite (B3).** Optional coverage contexts or dead-code tools (vulture, knip) run when installed.
4. **Hygiene cannot be checked mechanically (Minor 4).**
5. **Debt outside the initiative's files is never reached** until the vague audit threshold fires (Minor 5).

DESIGN NEEDS CHANGES
