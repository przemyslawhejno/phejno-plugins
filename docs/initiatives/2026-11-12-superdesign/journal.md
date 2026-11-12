# tech-lead 0.3.0: superdesign as mockup provider — journal

## 2026-11-12 session

- Proposed by the user after the 0.2.0 release; to start after the cleanup initiative (2026-11-12-cleanup).
- Findings from reading superdesigndev/superdesign-skill (MIT, commit f9f05cd; superdesign.dev itself was outside this session's network):
  - The skill drives a commercial cloud service through `@superdesign/cli` (`npx --yes @superdesign/cli@latest`): browser login, generation credits per draft, designs on a canvas at superdesign.dev; a draft's HTML can be fetched with `get-design --output`.
  - Install in Claude Code: `/plugin marketplace add superdesigndev/superdesign-skill`, `/plugin install superdesign@superdesign` (command `/superdesign:superdesign`).
  - It sends selected project files (`--context-file`) to its servers, asks the user questions, and requires the user's approval of a design before implementation.
  - It writes `.superdesign/` in the repository (`init/` analysis, `resume.json`, `design-system.md`, `tmp/`); generated HTML may only reference public https asset URLs.
- Proposed design (to be specified):
  - Optional mockup provider at step 4 when the plugin and CLI are installed and the user agrees per project (credits, code leaving the machine); run by the lead in the main session, not by subagents, because it is interactive.
  - The chosen draft is exported to `docs/initiatives/<initiative>/mockup.html`, which stays the canonical artifact; the canvas link goes into the journal.
  - `docs/standards.md` UI section points to `.superdesign/design-system.md` instead of duplicating it.
  - The UI/UX expert still reviews the mockup (WCAG 2.2, states, accessibility).
  - In autopilot only with consent given before start.
- Next: spec via brainstorming when the user picks this initiative.

## 2026-11-12 session (start)

- The user asked to execute B15 and B16 ("Wykonaj b15 i b16"). Ruling: read as advance agreement to go from plan to implementation (ledger `mode: autopilot`), with an independent review of spec and plan first; merging to master stays the user's decision — cost if wrong: the user stops the run.
- B16 folded in as the required hygiene pass (Task 3).
- Export syntax checked in the skill source: `get-design --draft-id <id> --json` and `get-design --output`; drafts may use `<sd-component>` templates and public asset URLs, hence the standalone check and fallback.
- Task 1 carries risk `system-wide` (behaviour of every UI run, paid external service) with the `architecture` lens.
- Spec, plan and ledger written.
