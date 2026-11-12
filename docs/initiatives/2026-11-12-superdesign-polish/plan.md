# tech-lead 0.3.1 superdesign polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the nine decisions of the spec and release 0.3.1.

**Architecture:** Wording in the skill documents and README, one docstring in `ledger.py`, tests for the new wording.

**Tech Stack:** Markdown, JSON, Python 3.9+ stdlib `unittest`.

**Spec:** `docs/initiatives/2026-11-12-superdesign-polish/spec.md`

## Global Constraints

- Spec decisions 1-9 are binding, with their exact wording where quoted. Terse imperative style; smallest edits; `SKILL.md` under 300 lines; no frontmatter changes; nothing switches or suggests the main session's model.
- Never invoke the superdesign skill or the superdesign CLI.
- No behaviour change in scripts. Tests: `python3 -m unittest discover tech-lead/tests` (167 tests; ratchet 1.12 s / 166).

## Review Focus

1. The standalone-check rule (decision 5) is decidable from the HTML alone.
2. The init check (decision 8) uses a baseline taken before dispatch, sees ignored files, and never reverts the user's work automatically.
3. The consent text names every channel: spec, request (stored verbatim), project files, images, fonts and logos, component templates, unpinned CLI.

---

Waves: 1 = Task 1; 2 = Task 3; 3 = Task 2.

### Task 1: Superdesign polish and 0.3.1

**Files:** `tech-lead/skills/tech-lead/SKILL.md`, `layout.md`, `mockup-prompt.md` (same directory), `tech-lead/README.md`, `tech-lead/scripts/ledger.py`, `tech-lead/tests/test_skill_docs.py`, `tech-lead/tests/test_prompts.py`, `tech-lead/tests/test_packaging.py`, `tech-lead/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

- [ ] Tests first: SKILL.md contains `before the first upload or generation`; SKILL.md or layout.md contain `not answering`, `registry latest`, `create-component`, `fonts and logos`, `git status --porcelain --ignored`, `baseline`, and state that changes outside `.superdesign/init/` are never reverted automatically; neither SKILL.md step (6) nor layout.md asks to record the canvas or preview link (ids only); `mockup-prompt.md` names `fetch`, `XMLHttpRequest`, `WebSocket`, `<iframe>`, a full version `x.y.z` for Tailwind and Lucide, and the local rebuild on failure; extend the existing README test only with the strings it does not yet assert; manifests agree (existing test).
- [ ] Apply decisions 1-9; version 0.3.1 in both manifests.
- [ ] Full suite passes; commit `tech-lead: superdesign polish (B17), 0.3.1`.

### Task 3: Project docs pointer (B18)

**Files:** `tech-lead/skills/tech-lead/SKILL.md`, `tech-lead/skills/tech-lead/layout.md`, `tech-lead/tests/test_skill_docs.py`

- [ ] Tests first: SKILL.md "Start of work" mentions `CLAUDE.md` and `## Project docs`; layout.md lists `CLAUDE.md` and contains the section text from the spec verbatim.
- [ ] Add one Start-of-work item to SKILL.md (add the section when missing, leave an existing one, commit it with the initiative) and the layout.md entry with the exact section text.
- [ ] Full suite passes; commit `tech-lead: project docs pointer in CLAUDE.md (B18)`.

### Task 2: Lead verification (lead)

- [ ] Add the `## Project docs` section to this repository's `CLAUDE.md`.
- [ ] Full suite; `ledger.py check` on all ledgers; close B17 and B18 in `docs/backlog.md`; `status.py --write`; review.
