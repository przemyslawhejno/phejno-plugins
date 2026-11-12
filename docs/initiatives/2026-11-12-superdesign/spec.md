# tech-lead 0.3.0: superdesign as mockup provider, and hygiene leftovers — design

Date: 2026-11-12

## Goal

1. **Superdesign (B15).** When the `superdesign` plugin is installed and the user agrees for the project, the lead uses it at step 4 (mockup) to produce better-designed UI drafts, while `mockup.html` in the initiative folder stays the canonical, reviewable artifact and every 0.2.0 quality gate (UI/UX expert, standards, harness) still applies. Without the plugin or consent nothing changes.
2. **Hygiene leftovers (B16).** Close the minor items left by the 0.2.1 final review.

Source of facts about superdesign: `journal.md` in this folder (read from superdesigndev/superdesign-skill at f9f05cd).

## Part 1: Superdesign

### Requirements

Shell access, Node.js (`npx`) and a browser for `npx --yes @superdesign/cli@latest login`. It does not work in headless or cloud sessions without that; there the built-in builder runs. The CLI is fetched from npm at its latest version on each run; the consent question says so.

### When it is used

All of these hold, checked by the lead at step 4:

- The work needs a mockup (step 4 rule unchanged).
- The `superdesign:superdesign` skill is available in the session.
- The current user has consented: `.tech-lead/superdesign-consent` (git-ignored, per clone and user, because credits and uploads belong to the user's own superdesign account) contains `consent: yes` with a date. The lead asks once, while the user is present in the spec and mockup review, and states what it costs and what leaves the machine:
  - generation credits on the user's superdesign account: on an existing codebase at least one reproduction draft of the current screen plus each requested variant;
  - lead tokens: the superdesign skill (about 900 lines) and, the first time, its repository analysis;
  - sent to superdesign's servers: the written spec as the design brief, the user's request, selected project files as design context, and uploaded images, which become public URLs;
  - the CLI runs unpinned from npm.
  A "no" is stored as `consent: no` and not asked again.
- The CLI preflight (`npx --yes @superdesign/cli@latest`) reports an authenticated session. Otherwise the lead asks the user to run `npx --yes @superdesign/cli@latest login` once; if that does not happen, the built-in builder runs and the journal says why.
- In autopilot runs that start from an existing spec (no user present at step 4), superdesign runs only with consent already recorded; without it the built-in builder runs without asking.

Otherwise the built-in mockup builder (sonnet medium, `mockup-prompt.md`) runs as in 0.2.0.

### Who runs it

- The lead, in the main session: superdesign asks the user questions, spends credits and needs the user's choice of draft. Its rule that code is implemented only after the user approves a design is satisfied by the spec-and-mockup review with the user that step 4 already requires, before the plan gate.
- Subagents never invoke the superdesign skill or CLI. Every subagent brief (the implementer brief rule in SKILL.md and each `*-prompt.md`) carries the line "Never invoke the superdesign skill or the superdesign CLI." because that skill can trigger itself on design requests.
- One exception: the repository analysis superdesign needs on an existing codebase (its INIT.md: local files only, no CLI, no credits) may be delegated by the lead to a sonnet medium subagent, whose brief points at that file and writes only `.superdesign/init/`.

### Flow at step 4

1. Load `superdesign:superdesign` and follow it for the screens and flows of the written spec. Before the first generation, tell the user the planned number of generations (reproduction draft plus variants). Count every generation call and record the total.
2. The user picks a draft on the canvas.
3. Export it: `npx --yes @superdesign/cli@latest get-design --draft-id <id> --output docs/initiatives/<initiative>/mockup.html` (if the CLI rejects this form, run `get-design --help` once and use the documented flag).
4. Standalone check: no `<sd-component` tags; no relative or `file://` paths; remote resources limited to public `https://` images from superdesign, the Tailwind CDN script and the Lucide icon CDN. Anything else fails the check.
5. A mockup builder subagent (sonnet medium, `mockup-prompt.md` in its superdesign-export mode) then works on the local file only: it adds one element `id` per screen or state and the screen-to-requirement mapping that the two-way coverage check needs, and, when the standalone check failed, rebuilds the file from the export (with `list-components` output from the lead for unresolved templates) keeping the design. It never needs network access.
6. Record in `journal.md`: project id, draft id, canvas link, preview link, generations used.
7. The UI/UX expert reviews spec and `mockup.html` as in 0.2.0. Fixes: a mockup builder subagent applies exact HTML/CSS fixes to the local `mockup.html`; when the user wants the canvas in sync, the lead imports the edited file (`import-design-draft --into`, no credits). Changes that need design judgement: the lead runs `iterate-design-draft` after telling the user the credit cost, then steps 3-5 again; or, if the user prefers no further credits, the builder subagent makes the change locally.

### Design system and repository files

- When superdesign creates or updates `.superdesign/design-system.md`, the UI section of `docs/standards.md` points to it (`Design system: .superdesign/design-system.md`) instead of repeating tokens; existing accessibility and performance rules stay in standards.md and are authoritative.
- `.gitignore` gets an allowlist: `.superdesign/*` ignored, `!.superdesign/design-system.md` committed. Everything else there (`init/`, `resume.json` with per-account ids, `tmp/`, `replica_html_template/`, `website/`) stays local; a fresh clone pays the repository analysis again, which the journal notes.

### Tiers and cost

- Tier rows: `Mockup via superdesign | lead (main session) | -` (credits plus lead tokens); `Superdesign repository analysis | sonnet | medium`; the mockup builder row also covers the export mode.
- The finish report lists superdesign generations used, next to `/model-manager:mm-report`.

## Part 2: Hygiene leftovers (B16)

- Test helper `run()` passes its `env` parameter through; tests stop changing the process-wide working directory (`os.chdir`) and pass `cwd` instead.
- The variable `worst` in `ledger_checkpoint.py` is renamed for what it holds (the first failing exit code).
- Missing annotations on the `ledger_core` helpers added in 0.2.1.
- `_esc` is folded into `_cell` in `ledger_report.py` if nothing else uses it.
- No behaviour change; the suite stays green and not slower per test than the ratchet in `docs/standards.md` beyond a 10% noise margin.

## Changes by file

- `skills/tech-lead/SKILL.md`: step 4 provider choice and flow (short; detail in `layout.md`/`mockup-prompt.md`), tier row, finish report line.
- `skills/tech-lead/layout.md`: `.tech-lead/superdesign-consent`, the `Design system:` line in the standards UI section, the `.superdesign/` allowlist, the journal entry for a superdesign mockup.
- `skills/tech-lead/mockup-prompt.md`: superdesign-export mode (step 5 above) and the subagent rule.
- Every `*-prompt.md` and the implementer brief rule in SKILL.md: "Never invoke the superdesign skill or the superdesign CLI."
- `README.md` of the plugin: optional superdesign section: requirements, install and login commands, consent and its costs, fallback, and that the integration has not yet been run live (backlog B1).
- Version 0.3.0 in `plugin.json` and the marketplace entry.
- Scripts and tests: B16 only.

## Out of scope

- Installing or logging into superdesign for the user; using superdesign for presentations or graphics; any change to the superdesign skill.
- Running superdesign in this cloud session (its hosts are not reachable here); the integration is verified by tests on the documents and by a dry run in the user's own session (backlog B1).
