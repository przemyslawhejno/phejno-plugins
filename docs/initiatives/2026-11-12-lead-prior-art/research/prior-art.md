# Prior art for tech-lead (2026-11-12)

Method note: `gh api` returned 403 for every repo in this session, so GitHub search endpoints were not usable. Facts below come from github.com pages and `commits/main.atom` feeds (read 2026-11-12) plus WebSearch. Star counts are page snapshots. MetaGPT and crewAI were not checked: they are general multi-agent frameworks (Python libraries), not Claude Code workflows, and add nothing a plugin can adopt. Roo "boomerang tasks" could not be confirmed on the (archived) repo page.

## Projects

| Project | What it is | Last activity | License | Ideas tech-lead lacks or does worse |
|---|---|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) (317k stars) | Skills framework tech-lead builds on | 2026-11-03 (v7.0.2) | MIT | v7 retunes skills to survive compaction; `diagnosing-superpowers` for post-mortems. Nothing to copy beyond tracking v7 changes to SDD helpers. |
| [github/spec-kit](https://github.com/github/spec-kit) (149k) | Spec-driven kit: constitution, specify, plan, tasks, implement, converge | 2026-11-11 | MIT | Extensions/presets that swap templates, commands and quality gates per organisation; an explicit `converge` loop ("repeat until Converged"). |
| [ruvnet/claude-flow (Ruflo)](https://github.com/ruvnet/claude-flow) (81k) | Swarm "meta-harness", vector memory, ~27 hooks | 2026-11-11 | MIT | Little worth taking. Most accuracy and speed figures are self-reported; 298 open issues. |
| [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) (55k) | Persona-based agile method, modules | 2026-11-08 | MIT | "Right-sized process": small changes go straight to build. A loop module that builds, verifies and runs a retro for a whole epic unattended. |
| [wshobson/agents](https://github.com/wshobson/agents) (42k) | Marketplace of 94 plugins, 202 agents, 185 skills | 2026-11-08 | MIT | Model aliases (opus/sonnet/haiku/fable/inherit) declared per agent; large specialist catalogue. Catalogue breadth is not a quality signal. |
| [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) (41k) | Teams-first orchestration; staged plan, PRD, exec, verify, fix pipeline | 2026-11-11 | MIT | `/deep-interview` scores requirement clarity before any code; session "friction report" on context bloat; cost tracking across sessions; premium/balanced/budget model presets. |
| [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core) (11.5k; predecessor gsd-build/get-shit-done archived, 64k) | Context-engineering spec-driven system | 2026-11-05 | MIT | `STATE.md`/`CONTEXT.md` that survive sessions; fresh 200k context per executor; verify step produces fix plans. All of this tech-lead already does in another shape. |
| [dsifry/metaswarm](https://github.com/dsifry/metaswarm) (430) | 9-phase issue-to-merged-PR pipeline | 2026-11-12 (v0.16.0) | MIT | JSONL fact store plus `/self-reflect` after merge and `/prime` to load only relevant facts; PR-shepherd phase; orchestrator re-runs validation instead of trusting reports; reviewers cite file:line per Definition-of-Done item; review rounds capped (10), then human; `metaswarm-usage` reports subagent cost and review rounds. Small project, so treat as ideas, not proof. |
| [eyaltoledano/claude-task-master](https://github.com/eyaltoledano/claude-task-master) (28k) | PRD-to-tasks CLI/MCP | 2026-04-23 (slowing) | MIT + Commons Clause | Per-task complexity scoring and expansion; separate main, research and fallback models. Pattern only. |
| [buildermethods/agent-os](https://github.com/buildermethods/agent-os) (5.6k) | Standards discovery and injection | 2026-10-07 | MIT | Standards are indexed and only the relevant ones are injected per build. tech-lead hands every brief the whole `standards.md`. |
| [SuperClaude-Org/SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) (24k) | Commands, 20 personas, 7 modes | 2026-09-27 | MIT | ReflexionMemory (error learning), confidence-check skill. Persona zoo is the part to avoid. |
| [musistudio/claude-code-router](https://github.com/musistudio/claude-code-router) (38k) | Local gateway routing to providers with fallbacks | 2026-10-10 | MIT | Ordered fallback models, per-request cost/latency logs. Operates at the proxy, outside tech-lead's remit. |
| [smtg-ai/claude-squad](https://github.com/smtg-ai/claude-squad) (8.8k) | tmux + worktree session manager for humans | 2026-08-20 | AGPL-3.0 | Nothing new: worktree lanes exist. Auto-yes flag is the opposite of tech-lead's stop rules. Copyleft: pattern only. |
| Kiro (AWS, closed; [overview](https://sdtimes.com/ai/amazon-launches-spec-driven-ai-ide-kiro/)) | IDE with requirements, design, tasks and hooks | n/a | proprietary | EARS "WHEN ... THE SYSTEM SHALL ..." acceptance phrasing; steering files; event hooks. EARS fixes phrasing, not testability. |
| [RooCodeInc/Roo-Code](https://github.com/RooCodeInc/Roo-Code) | Editor agent with custom modes | archived, shut down May 2026 | Apache-2.0 | Skip: unmaintained. OpenHands ([repo](https://github.com/OpenHands/OpenHands), 93k, MIT, active) is now a control center that hosts other agents; no workflow idea to port. |

## Proposals (ranked)

1. **Quick track for small work.** A `--quick` path (or auto-selected at 1 to 3 tasks, no risk tag) that skips mockup, prior art, automatic plan review, hygiene task and lenses, keeping ledger, verify checkpoint and one final review. Why: every tool with a process (BMAD, GSD, spec-kit) has a light path; tech-lead's full ceremony costs more than the work on small specs. From: BMAD, OMC. Effort M. Risk: dilutes "lose nothing from the spec"; keep requirement coverage and `checkpoint` mandatory, and force the full path on any `risk` tag. Mode: pattern.

2. **Lessons store and retrospective.** At finish, the lead writes 0-5 lessons (escalation causes, recurring review findings, wrong assumptions) to `docs/lessons.md` (one line each, tagged by area); planning and briefs load only matching tags. Why: today only lens yield and journal carry learning; escalations repeat across initiatives. From: metaswarm, SuperClaude, BMAD retros. Effort M. Risk: unbounded growth and stale rules; cap the file, require a source initiative per line, prune in the hygiene step. Mode: pattern.

3. **Circuit breaker and attempt telemetry.** Cap fix-loop rounds per task and review rounds per wave (for example 3 and 2); on a repeated identical finding, force a cause reclassification instead of another dispatch; record attempts per task and total subagent dispatches in the checkpoint line and the finish report. Why: the ladder has no explicit stop, so a stuck task can burn opus tokens silently. From: metaswarm (round cap, usage report), OMC (cost tracking), spec-kit (converge). Effort S. Risk: caps must route to "back to you" rather than abandon work. Mode: pattern.

4. **Targeted standards injection.** Tag `standards.md` sections and add an optional `standards` list per ledger task; briefs get only those sections plus a mandatory core. Why: smaller briefs, fewer ignored rules, cheaper cache-cold dispatches. From: Agent OS. Effort S. Risk: a missed tag hides a rule; `ledger.py check` should require the core and plan review should check tags. Mode: pattern.

5. **Model-yield calibration.** Mirror `Lens yield`: record per model/effort tier whether first attempts passed or escalated, and by which cause, in `standards.md`; the plan reviewer sees it when judging "too high wastes cost, too low risks failure". Why: model assignment is the plugin's core promise and currently has no feedback loop. From: task-master complexity scoring, OMC presets. Effort S. Risk: tiny samples; show counts, not percentages, and ignore until 10+ tasks. Mode: pattern (task-master is Commons Clause).

6. **Evidence-citing reviews.** Batch and lens reviewers must cite file:line (or command output) for each acceptance criterion they mark met, and the lead spot-checks one per batch. Why: cuts rubber-stamp approvals cheaply. From: metaswarm. Effort S. Risk: longer review reports; keep to one line per criterion. Mode: pattern.

7. **Optional PR shepherd after finish.** After `finishing-a-development-branch` opens a PR, offer to watch CI and review comments and loop fixes through the normal ladder. Why: finish currently ends at the report. From: metaswarm phase 8. Effort M. Risk: push and merge are existing autopilot stop reasons, so always ask first. Mode: pattern.

8. **Project overrides ("presets").** A small `docs/tech-lead.md` that sets lane count, default lenses per path glob, extra `Checks` and disabled steps. Why: teams otherwise fork the skill. From: spec-kit presets/extensions. Effort M. Risk: config surface grows; allow only keys already in the ledger or standards. Mode: pattern.

9. **Requirement clarity score before the spec is accepted.** Brainstorming asks questions but has no exit criterion; add a short checklist (every requirement has an observable outcome and one verify idea, no "TBD") the lead scores before step 4. From: OMC deep-interview, Kiro EARS (light use). Effort S. Risk: pseudo-precision; use a checklist, not a numeric score. Mode: pattern.

10. **Cross-vendor reviewer for `irreversible` tasks.** Optional second review by another model family when a CLI is installed. From: metaswarm, OMC team. Effort M. Risk: sends code to another vendor, needs consent like superdesign, and model-manager only knows Claude tiers. Mode: skip unless a user asks.

## Do not adopt

- **Swarm topologies, consensus protocols, vector memory, neural routing** (claude-flow): self-reported benefits, large surface, no evidence they beat wave plus ledger.
- **Persona catalogues** (SuperClaude 20, wshobson 202, BMAD personas): tech-lead's risk-scaled lenses cost less and only run when the task's files and risks call for them.
- **Proxy-level model routing** (claude-code-router): conflicts with "never switch the main session's model" and bypasses model-manager's dispatch table; assignment by task with a recorded reason is more auditable.
- **Auto-accept and endless persistence loops** (claude-squad `--autoyes`, OMC ralph): contradict the autopilot stop rules and make cost unbounded without proposal 3.
- **Constitution gate** (spec-kit): `standards.md` plus ADRs already serve it; a second document would drift.
- **Experimental agent teams** (OMC): depends on an experimental flag and a shared task list that duplicates the ledger.
- **AGPL and Commons Clause code** (claude-squad, task-master): read for ideas only.
