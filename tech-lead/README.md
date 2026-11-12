# tech-lead

A lead orchestrator for specs and projects. It plans a spec into waves of tasks, assigns the cheapest capable model to each, delegates the work, reviews and verifies it, and keeps project docs, status and backlog in one hierarchy. It builds on `model-manager` and `superpowers`.

## Requirements

- `model-manager` and `superpowers` plugins
- `python3`
- Claude Code 2.1.292+

## Install

```bash
claude plugins install tech-lead@phejno-plugins
```

## Usage

`/tech-lead:run <spec text | spec path | initiative folder>` starts the work. With an existing initiative folder it resumes where the ledger says to continue.

`/tech-lead:run --auto ...` is your advance agreement to autopilot: after a clean plan review it skips the approval gate. It still stops for destructive or irreversible operations, security-sensitive actions, side effects outside the worktree and added requirements.

By default the lead sends one gate message with the plan, the ledger and the plan review, and waits for your approval before any code is edited.

## Automatic plan review

As soon as the ledger passes `ledger.py check`, an independent reviewer checks the plan: spec coverage, task size, dependencies, model and effort per task, `verify` commands and risks. The lead applies what it accepts, with at most two rounds, and reports the outcome at the gate.

## Document hierarchy

Everything lives under `docs/`: `STATUS.md`, `backlog.md`, `standards.md`, `adr/` and one folder per initiative (spec, mockup, plan, ledger, journal, research). Formats and how state is derived from files are in `skills/tech-lead/layout.md`.

## Session-start status

A SessionStart hook injects a short status brief (in progress, planned, backlog head) so the lead can propose next steps. When `.claude/codemap/` is missing or stale, the brief adds at most one `Codemap:` line proposing `/codemap` (no index for 30+ code files; more than 50 pending paths or `symbols.md` missing; index older than 30 days with 20+ commits since) or `/codemap update` (16-50 pending). The full status has a `## Codemap` section. Set `TECH_LEAD_STATUS=0` to turn it off.

## Hygiene

Plans with several `code` or `ui` tasks get a final `kind: hygiene` task: dead code, duplicated tests and obsolete leftovers are removed, with `simplify` when installed. A haiku inventory finds candidates first. The suite time is kept as a ratchet in `standards.md`, and open `[hygiene]` backlog items can trigger a proposed cleanup initiative.

## Expert panels

Each task can carry `experts`: review lenses chosen from its risk and files. The lenses are `security`, `data`, `api`, `architecture`, `performance`, `errors`, `tests` and `ui-ux`; checklists, dispatch rules and yield tracking are in `skills/tech-lead/lenses.md`. Lens findings enter the task's fix loop, and any Important finding blocks the task.

## UI/UX

Projects with a graphical interface set `ui: true`. The lead makes a mockup, a UI/UX expert reviews it with the spec, and `kind: ui` tasks are checked against WCAG 2.2 AA, responsive layout and theme standards, with screenshots, axe and Lighthouse output as evidence.

## Optional: superdesign mockups

With the `superdesign` plugin installed, the lead can make the step 4 mockup on superdesign's canvas instead of the built-in builder. The chosen draft is exported to `mockup.html`, which stays the canonical artifact.

- Requirements: shell access, Node.js (`npx`) and a browser for login. Headless and cloud sessions use the built-in builder.
- Install: `/plugin marketplace add superdesigndev/superdesign-skill`, then `/plugin install superdesign@superdesign`. Log in once with `npx --yes @superdesign/cli@latest login`.
- Consent is per user, stored in git-ignored `.tech-lead/superdesign-consent`. The lead asks once and says what it costs and sends: generation credits on your superdesign account, lead tokens for the superdesign skill, and, to superdesign's servers, the written spec, your request, selected project files and uploaded images (which become public URLs). The CLI runs unpinned from npm.
- Only the lead runs superdesign, never subagents. Autopilot uses it only if consent was recorded before the start.
- Without the plugin, login or consent, the built-in mockup builder runs as before.
- The integration has not yet been run live (backlog B1).

## Ledger schema

New ledgers carry `"schema": 2`, which enables the hygiene, lens and UI rules. Ledgers without `schema` keep the 0.1.0 validation unchanged.

## Codemap integration

When `.claude/codemap/` exists (from the `claude-codemap` plugin), the lead navigates through `INDEX.md` and `symbols.md` before Glob or Grep and gives subagents their paths. After a wave it proposes or, in autopilot, runs `/codemap update` when changes are pending, and a plain `/codemap` rebuild after a rebuild action or moved modules. `checkpoint --mark` appends the wave's changed paths to `.claude/codemap/pending.md`, correcting lane-worktree paths and dropping `.worktrees/` and `.claude/codemap/` entries, and prints `Codemap: <n> pending (inline|update|rebuild)`; it does this only when `.claude/codemap/` exists.

## Optional skills

Used when installed: `engineering:architecture`, `engineering:tech-debt`, `engineering:code-review`, `engineering:testing-strategy`, `design:design-critique`, `design:accessibility-review`, `design:ux-copy`, `design:design-system`, `modern-web-guidance`, `simplify` and `security-review`. Nothing requires them.

## Scripts

- `scripts/ledger.py`: `check`, `show`, `next` and `checkpoint` for an initiative's `ledger.json`; `checkpoint --mark` also records codemap pending paths.
- `scripts/status.py`: project status on stdout, `--brief` for the hook, `--write` to regenerate `docs/STATUS.md`; includes codemap health.

## Limits

- The plugin never switches the main session's model; it assigns models only to subagents.
- Workflow agents bypass `model-manager`'s dispatch enforcement.
- Prior-art search needs network access; when blocked it is recorded as skipped.
