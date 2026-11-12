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

A SessionStart hook injects a short status brief (in progress, planned, backlog head) so the lead can propose next steps. Set `TECH_LEAD_STATUS=0` to turn it off.

## Scripts

- `scripts/ledger.py`: `check`, `show`, `next` and `checkpoint` for an initiative's `ledger.json`.
- `scripts/status.py`: project status on stdout, `--brief` for the hook, `--write` to regenerate `docs/STATUS.md`.

## Limits

- The plugin never switches the main session's model; it assigns models only to subagents.
- Workflow agents bypass `model-manager`'s dispatch enforcement.
- Prior-art search needs network access; when blocked it is recorded as skipped.
