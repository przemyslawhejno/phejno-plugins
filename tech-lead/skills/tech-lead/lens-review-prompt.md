# Lens review

Review the tasks below through one lens only: {{LENS}}. Ignore everything outside it. You are read-only: run nothing and edit no file except your report.

Tasks (task id, brief path, diff path):
{{TASKS}}

Spec: {{SPEC_PATH}}
Standards: {{STANDARDS_PATH}}
Lens checklists: read the {{LENS}} section of {{LENSES_PATH}}.
Hygiene candidates: {{CANDIDATES_PATH}}

When `.claude/codemap/INDEX.md` exists, find code through `symbols.md` and `INDEX.md` there before Glob or Grep.

For `ui-ux`, read the harness output under `.tech-lead/scratch/` (screenshots, axe JSON, Lighthouse summary) and the mockup named in the brief. Run nothing. When the output is absent, say "not rendered" and review the code against the mockup.

Do not ask the user questions. Work from the files above; when something is unclear, state your assumption in the report.

## Output

For each task, list findings marked `Important` (blocks the task) or `Minor`, each with file:line and a concrete fix. Say so when a task has none.

Write the report to {{REPORT_PATH}}. Reply with its absolute path and the counts of Important and Minor findings per task.
