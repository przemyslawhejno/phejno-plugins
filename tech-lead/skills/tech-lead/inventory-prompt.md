# Hygiene inventory

Find tests and code made obsolete, duplicated or dead by the changes below. You are read-only: change nothing except your report.

Never invoke the superdesign skill or the superdesign CLI.

Changes (symbols, strings and behaviours changed or removed):
{{CHANGES}}

Test roots: {{TEST_ROOTS}}
Code roots: {{CODE_ROOTS}}

When `.claude/codemap/INDEX.md` exists, find code through `symbols.md` and `INDEX.md` there before Glob or Grep. The index is read-only for you: never edit topic files, `symbols.md` or `pending.md`.

## Search

1. Search the whole test tree under the test roots for tests covering those symbols, strings and behaviours, not only the tests of the changed files.
2. Search the code tree under the code roots for references to removed symbols and strings.
3. Run a dead-code tool (`vulture`, `knip` or the stack's equivalent) only if it is already installed. Never install anything.

## Output

List candidates, each marked `obsolete`, `duplicate` or `dead`, with path:line and a one-line reason. Do not fix or delete anything.

Write the report to {{REPORT_PATH}}. Reply with its absolute path and the number of candidates.
