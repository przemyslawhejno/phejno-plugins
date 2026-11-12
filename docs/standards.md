# Project standards

Conventions for this repository (Claude Code plugin marketplace: Markdown skills, commands, JSON manifests, stdlib Python scripts with `unittest`). tech-lead reviewers check work against this file.

## Conventions in force

- Python 3.9+, stdlib only, `from __future__ import annotations`; UTF-8 everywhere; JSON with two-space indent and a trailing newline.
- Scripts report errors as one `error: <message>` line on stderr and exit 1; written files are announced as `Wrote <absolute path>`.
- Skills, commands and prompts: terse imperative English; no `model` or `effort` in skill or command frontmatter.
- One plugin per top-level directory, registered in `.claude-plugin/marketplace.json` with the same version as its `plugin.json`.

## Hygiene

- Comments only where the code cannot say it: why, a non-obvious constraint, a workaround with its link. No change history, no commented-out code, no restating the code, no TODO without a backlog id (`B<n>`). History lives in git.
- A change of behaviour removes the code and tests it made obsolete in the same task.
- One behaviour, one test: extend or replace an existing test instead of adding a near-duplicate, anywhere in the suite.
- Tests follow `superpowers:test-driven-development` (`writing-good-tests.md`).
- Speed: the fastest test level that proves the behaviour; no sleeps beyond what a timing test needs; shared fixtures for expensive setup such as temporary git repositories.

## Suite

- Suite: `python3 -m unittest discover tech-lead/tests`
- Suite time: 1.12s (2026-11-12, 166 tests)

## Checks

None: the repository has no linter configured.

## Lens yield

No lens has run yet.
