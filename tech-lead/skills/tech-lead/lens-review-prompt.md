# Lens review

Review the tasks below through one lens only: {{LENS}}. Ignore everything outside it. You are read-only: run nothing and edit no file except your report.

Tasks (up to 4), one entry per task: task id, title, brief path, implementer report path, diff path, lenses assigned, mockup section (`#id` in the mockup) or `none`:
{{TASKS}}

Spec: {{SPEC_PATH}}
Standards: {{STANDARDS_PATH}}
Lens checklists: read the {{LENS}} section of {{LENSES_PATH}}.
Hygiene candidates: {{CANDIDATES_PATH}}. The `tests` lens, and any lens that sees a new test, checks it against the candidates for duplicates and obsolete tests. `none` means skip.

When `.claude/codemap/INDEX.md` exists, find code through `symbols.md` and `INDEX.md` there before Glob or Grep.

For `ui-ux`, read the harness output under `.tech-lead/scratch/` (screenshots, axe JSON, Lighthouse summary) and the mockup section of each task entry. Run nothing. When the output is absent, say "not rendered" and review the code against the mockup.

Do not ask the user questions. Work from the files above; when something is unclear, state your assumption in the report.

## Output

For each task, list findings marked `Critical` (breaks the spec or the build, or loses data), `Important` or `Minor`; Critical and Important block the task, each with file:line and a concrete fix. Say so when a task has none.

Write the report to {{REPORT_PATH}}. Reply with its absolute path and the counts of Critical, Important and Minor findings per task.
