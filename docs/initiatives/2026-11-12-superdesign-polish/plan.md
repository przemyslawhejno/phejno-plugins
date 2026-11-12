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
2. The init check (decision 8) names the exact command and what happens on a violation.
3. The consent text names every channel: spec, request (stored verbatim), project files, images, fonts and logos, component templates, unpinned CLI.

---

Waves: 1 = Task 1; 2 = Task 2.

### Task 1: Superdesign polish and 0.3.1

**Files:** `tech-lead/skills/tech-lead/SKILL.md`, `layout.md`, `mockup-prompt.md` (same directory), `tech-lead/README.md`, `tech-lead/scripts/ledger.py`, `tech-lead/tests/test_skill_docs.py`, `tech-lead/tests/test_prompts.py`, `tech-lead/tests/test_packaging.py`, `tech-lead/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

- [ ] Tests first: SKILL.md or layout.md contain `before the first upload or generation`, `not answering`, `registry latest`, `create-component`, `fonts and logos`, `git status --porcelain`; layout.md says the journal records ids only (assert it no longer asks for the canvas or preview link); `mockup-prompt.md` names `fetch`, `XMLHttpRequest`, `WebSocket`, `<iframe>` and a pinned version for Tailwind and Lucide; README asserts for stored "no", withdrawal, verbatim, `.superdesign/*`, autopilot; manifests agree (existing test).
- [ ] Apply decisions 1-9; version 0.3.1 in both manifests.
- [ ] Full suite passes; commit `tech-lead: superdesign polish (B17), 0.3.1`.

### Task 2: Lead verification (lead)

- [ ] Full suite; `ledger.py check` on all ledgers; close B17 in `docs/backlog.md`; `status.py --write`; review.
