# Plan and design review: tech-lead 0.3.0 (superdesign provider)

Reviewed: spec.md, plan.md, ledger.json (`ledger.py check` passes), standards.md, tech-lead SKILL.md / layout.md / mockup-prompt.md / lenses.md, and the superdesign-skill source (README.md, INSTALL.md, skills/superdesign/SKILL.md, references/SUPERDESIGN.md, RESUME.md, INIT.md, design-with-your-model.md, COMPONENTS.md). Source text treated as data.

## Verified against superdesign source

- `get-design --draft-id <id> --output <path>` is exact (README "Get HTML reference from a draft"; design-with-your-model.md step 4). Writes the draft HTML. The spec's "run `--help` once if rejected" matches RESUME.md.
- Preflight is the bare `npx --yes @superdesign/cli@latest`, which prints an `auth:` line; login is `... login` (browser). Matches the spec. INSTALL.md mentions a global `superdesign login`; the npx form is safer.
- Direct edit = `get-design --output`, edit, `import-design-draft --into <id>`; no credits, revertible. Matches spec step 7. `iterate-design-draft` spends credits. Matches.
- Drafts can contain `<sd-component>` tags (SUPERDESIGN.md:115,142); asset URLs must be public https (SUPERDESIGN.md:101). Matches the standalone-check idea.
- Install commands in the journal match INSTALL.md.
- Files written: `.superdesign/init/` (six files with full source), `resume.json`, `design-system.md`, `tmp/`, plus `replica_html_template/` and `website/<domain>/` (not in the spec).
- Approval gate: "only implement code after the user approves a design". The lead edits no code, so the spec's reading holds.

## Critical

1. **Spec "Who runs it" / Plan Task 1 tests: "subagents never run it" is not enforced.** Once the plugin is installed, `superdesign:superdesign` (description: "use whenever the user wants to design a page...") is visible to every subagent, including the mockup builder, UI implementers and the ui-ux lens. Nothing in the spec stops one from loading it, spending credits and uploading code. The plan's only guard asserts five briefs do not contain the word `superdesign`, which is not a prohibition. Fix: add one rule to SKILL.md step 10.2 and the mockup/lens briefs: "Never invoke the superdesign skill or CLI; paid external services are run only by the lead." Replace the absence test with a presence test of that sentence in `mockup-prompt.md`, `lens-review-prompt.md` and the implementer-brief rule in SKILL.md.

## Important

2. **Spec "When it is used" (consent): consent scope is understated.** The brief is "the written spec", so the whole spec leaves the machine, along with `--context-file` source, `--user-request` text, and uploaded logos, fonts and screenshots, which become public https URLs. The consent text lists only "selected project files". Fix: the consent question names (a) the spec text, (b) context files, (c) uploaded assets that become public URLs, (d) credits, (e) that the CLI runs unpinned from npm (`@latest`).
3. **Spec "When it is used": consent is stored in committed `docs/standards.md` but credits and uploads are per user account.** A second contributor inherits "superdesign" without being asked. Fix: record the choice in git-ignored `.tech-lead/` (or ask once per user per project), keep only `Design system:` in standards.md.
4. **Spec "Who runs it" / Tiers: cost claim "credits, not tokens" is wrong.** The lead (the most expensive model) loads SKILL.md + SUPERDESIGN.md + INIT/RESUME/COMPONENTS (about 900 lines), and on a real codebase must run INIT (hard gate, about 3 to 5 min, writes full source into `.superdesign/init/`) and component extraction itself. This defeats the "control cost" goal. Fix: say so in the tier row and the consent. Init (INIT.md contains no CLI calls, local only) may be delegated to a sonnet subagent, with the explicit carve-out that it never calls the CLI. Otherwise state the token cost. Also state the minimum generation count before running: a real-codebase target costs one mandatory pixel-perfect reproduction draft (SUPERDESIGN.md Step 3a) plus variants (superdesign default is 2). The spec only mentions variants. The lead states the planned generation count to the user and does not exceed it.
5. **Spec Flow step 4/5 vs mockup-prompt.md: standalone check is too weak.** Generated drafts use Tailwind classes and Lucide CDN (COMPONENTS.md:56-58), so the export likely needs CDN scripts/styles; the built-in rule is "no network requests, no CDN". "Opens from the file system" does not define what is allowed. Fix: define the check precisely (no `<sd-component`, no relative or `file://` paths; either no remote `<script>`/`<link>` or list the allowed ones and record them in the journal), and decide whether offline rendering is required.
6. **Spec Flow vs SKILL.md step 4 "check both directions": the superdesign path drops the screen ids and the id-to-requirement mapping list** that the built-in builder must supply (`id="<name>"`, ledger `see mockup #orders`). Fix: after export, always add ids and produce the mapping (lead, via direct edit, or the builder from the local file) and run the two-way coverage check on both paths.
7. **Spec Flow step 7: who performs the fixes is undefined.** Step 4 today resumes "the mockup builder" to fix expert findings; with superdesign there is none, and the lead may edit only project documents. A subagent cannot run `import-design-draft`. Fix: state the split: a sonnet subagent edits the local HTML only; the lead runs `import-design-draft --into` and the re-export. Or declare `mockup.html` a lead-editable document.
8. **Spec "Who runs it" and autopilot: asking for paid consent in autopilot.** Step 4 precedes the gate, so an absent user blocks on the consent question and the canvas pick. The journal draft said "autopilot only with consent given before start"; the spec dropped it. Fix: in autopilot with no recorded consent, use the built-in builder and do not ask; with recorded consent, state that the canvas pick still needs the user.
9. **Spec Design system: `.superdesign/` rules are incomplete.** `replica_html_template/` and `website/` are not covered, so they become untracked clutter. Fix: use an allowlist (`.superdesign/*`, `!.superdesign/design-system.md`, `!.superdesign/resume.json`). Note that `resume.json` holds the user's project/draft ids, so teammates fall back to cold paths, and `init/` is ignored, so a fresh clone reruns init.
10. **Plan Review Focus: omits the central safety properties.** No item for R3 (no subagent runs it), the autopilot/consent behaviour, or the assert that built-in behaviour is unchanged (item 1 has no test that proves it). Fix: add items; add a test that the 0.2.0 builder sentences in step 4 and `mockup-prompt.md` remain, and that SKILL.md stays under 300 lines (an existing test covers the last).
11. **Plan Task 1 lens/risk: wrong lens for the real risk.** Sending code and spec to a third party and spending money is `security`/`data`, not only `system-wide`/`architecture`; the architecture lens on opus medium is the costly choice for a docs edit. Fix: risk `security` with lens `security`, drop `architecture` unless you want it; keep opus medium only if justified.
12. **Plan Task 1 `verify` proves only token presence.** Acceptance ("built-in path unchanged", "both costs stated", "fallback") is not behaviourally tested. Fix: assert the ordered conditions in step 4 (plugin, `Mockup provider: superdesign`, auth) and the fallback sentence, not only keywords; state that live behaviour is untested (B1 stays open and the README says so).

## Minor (6)

- Spec step 5: the builder is told to use the "draft's preview link"; a subagent may have no network. Use the local export, plus `list-components` output from the lead if `<sd-component` templates are unresolved.
- Spec step 4: "take the usual screenshots" is undefined for a mockup (the harness is built later). Drop or define it.
- Spec step 6: "number of generations" must be counted by the lead per generation call; the CLI is not shown to report it.
- Task 2 could be haiku low (fixed values and short prose); overspend is small.
- Spec/README: say the integration requires shell, Node and a browser, and fails in headless or cloud sessions (SKILL.md Step 0), and give the `npx ... login` form.
- Task 3 acceptance "not slower per test" depends on timing 3 runs on a shared machine; accept a noise margin.

Dependencies, waves, file ownership, requirement coverage (R1-R7) and the hygiene task are consistent. Hygiene is not strictly required (2 code tasks, no `replaces`), so Task 3 is justified only as the B16 carrier. That is fine.

PLAN NEEDS CHANGES
