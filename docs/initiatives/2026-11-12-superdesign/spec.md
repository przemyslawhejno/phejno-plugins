# tech-lead 0.3.0: superdesign as mockup provider, and hygiene leftovers — design

Date: 2026-11-12

## Goal

1. **Superdesign (B15).** When the `superdesign` plugin is installed and the user agrees for the project, the lead uses it at step 4 (mockup) to produce better-designed UI drafts, while `mockup.html` in the initiative folder stays the canonical, reviewable artifact and every 0.2.0 quality gate (UI/UX expert, standards, harness) still applies. Without the plugin or consent nothing changes.
2. **Hygiene leftovers (B16).** Close the minor items left by the 0.2.1 final review.

Source of facts about superdesign: `journal.md` in this folder (read from superdesigndev/superdesign-skill at f9f05cd).

## Part 1: Superdesign

### When it is used

All of these hold, checked by the lead at step 4:

- The work needs a mockup (step 4 rule unchanged).
- The `superdesign:superdesign` skill is available in the session.
- `docs/standards.md` has `Mockup provider: superdesign` in its UI section. The lead adds this line only after asking the user once per project, stating both costs: generation credits on the user's superdesign account, and selected project files sent to superdesign's servers as design context. A "no" is recorded as `Mockup provider: built-in` and not asked again.
- The CLI preflight (`npx --yes @superdesign/cli@latest`) reports an authenticated session. If not, the lead asks the user to run `superdesign login` (browser) once; if that does not happen, the built-in mockup builder runs instead and the journal says why.

Otherwise the built-in mockup builder (sonnet medium, `mockup-prompt.md`) runs as in 0.2.0.

### Who runs it

The lead, in the main session, never a subagent: superdesign asks the user questions, spends credits and needs the user's choice of draft. Its own rule that code is implemented only after the user approves a design is satisfied by the spec-and-mockup review with the user that step 4 already requires. This step happens before the plan gate, so autopilot does not skip it.

### Flow at step 4

1. Load the `superdesign:superdesign` skill and follow it to design the screens and flows the spec describes, passing the written spec as the brief. Ask for 2 or 3 variants only when the user wants a choice; each costs credits.
2. The user picks a draft on the canvas.
3. Export the chosen draft: `npx --yes @superdesign/cli@latest get-design --draft-id <id> --output docs/initiatives/<initiative>/mockup.html` (if the CLI rejects this form, run `get-design --help` once and use the documented flag).
4. Check the export stands alone: it opens from the file system, contains no `<sd-component` tags and no relative or `file://` asset paths. Public `https://` asset URLs from superdesign are allowed and noted in the journal. With a render harness, take the usual screenshots.
5. When the export does not stand alone, the built-in mockup builder (sonnet medium) rebuilds `mockup.html` from the exported HTML and the draft's preview link, keeping the design.
6. Record in `journal.md`: project id, draft id, canvas link, preview link, number of generations used.
7. The UI/UX expert reviews spec and `mockup.html` as in 0.2.0. Fixes: exact HTML/CSS corrections go through superdesign's direct edit (`get-design --output`, edit, `import-design-draft --into`, no credits) followed by a new export; changes that need design judgement use `iterate-design-draft` after telling the user it costs credits. The built-in builder may instead patch `mockup.html` directly when the user prefers no further credits.

### Design system

- When superdesign creates or updates `.superdesign/design-system.md`, the UI section of `docs/standards.md` points to it (`Design system: .superdesign/design-system.md`) instead of repeating tokens. An existing UI section stays authoritative for accessibility and performance rules.
- `.superdesign/design-system.md` and `.superdesign/resume.json` are committed (they make the next session cheaper). `.superdesign/init/` (regenerable analysis that copies source code) and `.superdesign/tmp/` are added to `.gitignore`.

### Tiers and cost

- Tier table row: `Mockup via superdesign | lead (main session) | -`, with the note that drafts cost superdesign credits, not tokens.
- The finish report lists the superdesign generations used, next to `/model-manager:mm-report`.

## Part 2: Hygiene leftovers (B16)

- Test helper `run()` passes its `env` parameter through; tests stop changing the process-wide working directory (`os.chdir`) and pass `cwd` instead.
- The variable `worst` in `ledger_checkpoint.py` is renamed for what it holds (the first failing exit code).
- Missing annotations on the `ledger_core` helpers added in 0.2.1.
- `_esc` is folded into `_cell` in `ledger_report.py` if nothing else uses it.
- No behaviour change; the suite stays green and not slower per test than the ratchet in `docs/standards.md`.

## Changes by file

- `skills/tech-lead/SKILL.md`: step 4 provider choice and flow (short; detail in `layout.md`/`mockup-prompt.md`), tier row, finish report line.
- `skills/tech-lead/layout.md`: `Mockup provider:` and `Design system:` lines in the standards UI section; `.superdesign/` commit and ignore rules; journal entry for a superdesign mockup.
- `skills/tech-lead/mockup-prompt.md`: rebuilding from a superdesign export (step 5 above).
- `README.md` of the plugin: optional superdesign section with install commands and the two costs.
- Version 0.3.0 in `plugin.json` and the marketplace entry.
- Scripts and tests: B16 only.

## Out of scope

- Installing or logging into superdesign for the user; using superdesign for presentations or graphics; any change to the superdesign skill.
- Running superdesign in this cloud session (its hosts are not reachable here); the integration is verified by tests on the documents and by a dry run in the user's own session (backlog B1).
