# Batch task review

Review the tasks below. You are read-only: do not edit any file except your report.

Tasks (up to 4: task id, brief path, diff path):
{{TASKS}}

Spec: {{SPEC_PATH}}
Standards: {{STANDARDS_PATH}}
Mockup (UI tasks only): {{MOCKUP_PATH}}

## For each task check

1. Spec compliance: the diff does what the brief and spec require, nothing missing, nothing extra.
2. Code quality against {{STANDARDS_PATH}}.
3. Tests prove the acceptance criteria and were not weakened, skipped or deleted.
4. For UI tasks, the result matches the mockup.

## Output

Give each task a verdict: `APPROVED` or `CHANGES_REQUIRED`. List findings, each marked `blocking` or `minor`, with file:line. Any blocking finding means `CHANGES_REQUIRED`.

Write the report to {{REPORT_PATH}}. Reply with its absolute path and the verdicts.
