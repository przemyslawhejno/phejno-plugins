# Batch task review

Review the tasks below. You are read-only: do not edit any file except your report. Do not trust the implementer reports: read each diff once and judge it yourself; do not re-run tests.

Tasks (up to 4), one entry per task: task id, title, brief path, implementer report path, diff path, lenses assigned, mockup section (`#id` in the mockup) or `none`:
{{TASKS}}

Spec: {{SPEC_PATH}}
Standards: {{STANDARDS_PATH}}
Mockup (UI tasks only): {{MOCKUP_PATH}}
Hygiene candidates: {{CANDIDATES_PATH}}

A value of `none` in a placeholder or entry field means that input does not exist: skip the checks that need it.

When `.claude/codemap/INDEX.md` exists, find code through `symbols.md` and `INDEX.md` there before Glob or Grep.

## For each task check

1. Spec compliance: the diff does what the brief and spec require, nothing missing, nothing extra.
2. Code quality against {{STANDARDS_PATH}}.
3. Tests prove the acceptance criteria and were not weakened, skipped or deleted.
4. For UI tasks, the result matches the mockup section of the entry. Skip this check for tasks whose lenses include `ui-ux`, and when the mockup section is `none`.
5. Hygiene: obsolete code or tests left behind, or a new test duplicating one in the diff or in {{CANDIDATES_PATH}}, is **Important**; a noise comment (restating code, change history, commented-out code) is **Minor**.

## Output

Give each task a verdict: `APPROVED` or `CHANGES_REQUIRED`. List findings, each marked `Critical` (breaks the spec or the build, or loses data), `Important` or `Minor`, with file:line and a concrete fix. Any Critical or Important finding is blocking and means `CHANGES_REQUIRED`; Minor findings do not.

Write the report to {{REPORT_PATH}}. Reply with its absolute path and the verdicts.
