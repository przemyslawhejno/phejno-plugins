# Plan review

Review the plan against the spec. You are read-only: edit nothing except your report.

Spec: {{SPEC_PATH}}
Plan: {{PLAN_PATH}}
Ledger: {{LEDGER_PATH}}

When `.claude/codemap/INDEX.md` exists, find code through `symbols.md` and `INDEX.md` there before Glob or Grep.

## Check

- Spec coverage: every requirement maps to a task.
- Task size and boundaries: small, with clear file ownership and no overlap.
- Interfaces between tasks: producers and consumers agree.
- Dependencies and waves: correct order, real parallelism, no cycles.
- Model and effort per task, in both directions: overspend (a stronger model or higher effort than needed) and underpowered (too weak for the task).
- `verify` commands really prove the acceptance criteria.
- Review Focus is specific and points at the real risks.
- Risks the plan ignores.
- Each behaviour change names what it `replaces`, and planned tests do not duplicate existing ones.
- A hygiene task exists as the hygiene rule requires.
- Risks and lenses, both ways: a task with a risk lacks a matching lens; a lens sits on routine work without a risk; a lens that `standards.md` flags in its Lens yield section is chosen without a risk.

## Output

Mark each finding `blocking` or `minor`, with the plan section and a concrete fix. End with exactly one line: `PLAN APPROVED` or `PLAN NEEDS CHANGES`.

Write the report to {{REPORT_PATH}}. Reply with its absolute path and the findings.
