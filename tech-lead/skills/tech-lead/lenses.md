# Lenses

A lens is a focused review of a task's diff. Each section gives the checklist (at most 8 bullet lines) and what the lens uses when installed. Use an installed skill as an extra input to the checklist. An installed named agent replaces the generic dispatch, never adds to it (Dispatch).

## security

- Input validation at every trust boundary.
- Authentication and authorization on each new path.
- Secrets in code, logs, config or test fixtures.
- Injection: SQL, shell, template, path traversal, deserialization.
- New or upgraded dependencies: known advisories, scope of permissions.
- Uses when installed: `engineering:code-review` security dimension.

## data

- Migrations: ordered, idempotent, safe on existing rows and large tables.
- Consistency: transactions, constraints, concurrent writers.
- Reversibility: a rollback path, or an explicit decision that there is none.
- Backups and retention before any destructive change.
- Uses when installed: none.

## api

- Contracts: names, types, required and optional fields match the spec.
- Backward compatibility: existing callers and stored data keep working.
- Error shapes and status codes are consistent and documented.
- Versioning and deprecation of anything removed.
- Uses when installed: none.

## architecture

- Module boundaries respected; no layer reaching around another.
- Dependencies point one way; no new cycle.
- Coupling: shared state, hidden globals, leaky abstractions.
- Types make invalid states hard to represent.
- Uses when installed: `engineering:code-review` maintainability; `pr-review-toolkit:type-design-analyzer`.

## performance

- Algorithmic complexity on realistic input sizes.
- Queries: N+1, missing indexes, unbounded result sets.
- Memory: unbounded growth, large copies, leaks.
- Hot paths: work that can move out of the loop or be cached.
- Uses when installed: `engineering:code-review` performance dimension.

## errors

- Swallowed exceptions and empty catch blocks.
- Silent fallbacks that hide a failure from the caller or the user.
- Error messages say what failed and what to do next.
- Cleanup and resources released on every failure path.
- Uses when installed: `pr-review-toolkit:silent-failure-hunter`.

## tests

- Test architecture: fixtures shared, levels chosen for speed (unit before integration).
- Each behaviour has one test; no near-duplicates.
- Runners and configuration: deterministic, no sleeps beyond what a timing test needs.
- Tests assert behaviour, not implementation details.
- Uses when installed: `engineering:testing-strategy`; `pr-review-toolkit:pr-test-analyzer`.

## ui-ux

- Read the harness output at the path in the task entry: screenshots at mobile and desktop widths, axe JSON, Lighthouse summary.
- When the path is `none`, say "not rendered" and review the code. Compare with the mockup: flows, hierarchy, states (empty, loading, error, success), copy.
- Check the UI standards in `standards.md`: WCAG 2.2 AA (including 2.5.8 target size), responsive, tokens, themes.
- Check keyboard order and focus by reading the code; axe finds only part of the issues.
- Uses when installed: `design:design-critique`, `design:accessibility-review`, `design:ux-copy`, `design:design-system`, `modern-web-guidance`. Give these the mockup path and the harness output, and forbid questions to the user: they are interactive and otherwise ask for a Figma link or a description.

## Dispatch

- One dispatch per lens per wave, covering every task of the wave that lists it, in the same message as the batch reviews.
- Pass `model` and `effort` explicitly on every call, overriding model-manager's routing: sonnet medium. Opus medium for `security` and `architecture` on tasks with a risk, and for `ui-ux` on tasks with risk `system-wide`.
- When a lens has a named agent in its `Uses when installed` line and a task carries a risk, that agent replaces the generic lens dispatch for the lens: same `lens-review-prompt.md` brief and report path, called with the same explicit `model` and `effort` the generic lens would get. Its findings count in the lens yield. Never dispatch both.
- A lens finding enters the task's fix loop like a review finding; the lens that raised it re-reviews only the fix diff and writes `research/lens-<lens>-<wave>-fix<n>.md`. Any Critical or Important finding blocks the task.

## Yield

Record each lens's result in the wave journal entry, in this format: `Lens yield: <lens> <C+I> Critical/Important, <M> Minor`; separate lenses with `; `, and write a lens with no findings as `<lens> 0`.
