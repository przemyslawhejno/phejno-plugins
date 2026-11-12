# tech-lead 0.3.0 (superdesign provider, hygiene leftovers) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add superdesign as an optional, consented mockup provider to the `tech-lead` skill, close the B16 hygiene leftovers, and release 0.3.0.

**Architecture:** Behaviour lives in the skill documents (SKILL.md, layout.md, mockup-prompt.md) and the README; no script changes for Part 1. Part 2 is a hygiene pass over scripts and tests.

**Tech Stack:** Markdown, JSON, Python 3.9+ stdlib `unittest`.

**Spec:** `docs/initiatives/2026-11-12-superdesign/spec.md`

## Global Constraints

- Spec: `docs/initiatives/2026-11-12-superdesign/spec.md`; facts about superdesign: `journal.md` in the same folder. Command names and flags exactly as the spec writes them.
- Skill documents: terse imperative style, smallest edits; `SKILL.md` under 300 lines (192 now); no `model` or `effort` in frontmatter; nothing switches or suggests the main session's model.
- Superdesign is never run by a subagent; nothing in the documents may tell a subagent to invoke it.
- Hygiene per `docs/standards.md`; tests: `python3 -m unittest discover tech-lead/tests` (156 tests; ratchet 1.11 s / 156). Do not edit `tech-lead/tests/helpers.py` unless the task says so.

## Review Focus

1. Without the plugin, or with `Mockup provider: built-in`, step 4 behaves exactly as in 0.2.0 (Task 1).
2. The consent question states both costs (credits, code sent to superdesign) and is asked once per project (Task 1).
3. A non-standalone export (`<sd-component`, relative or `file://` assets) falls back to the built-in builder (Task 1).
4. `.superdesign/init/` and `.superdesign/tmp/` are ignored; `design-system.md` and `resume.json` are committed (Task 1).
5. Hygiene changes keep every message and exit code (Task 3).

---

Waves: 1 = Tasks 1, 2 (lane 1: Task 1; lane 2: Task 2); 2 = Task 3; 3 = Task 4.

### Task 1: Superdesign in the skill documents

**Files:** `tech-lead/skills/tech-lead/SKILL.md`, `tech-lead/skills/tech-lead/layout.md`, `tech-lead/skills/tech-lead/mockup-prompt.md`, `tech-lead/tests/test_skill_docs.py`, `tech-lead/tests/test_prompts.py`

- [ ] Tests first: `SKILL.md` mentions `superdesign:superdesign`, `Mockup provider:`, `credits`, `main session`, `get-design`, `built-in`; `layout.md` mentions `Mockup provider: superdesign`, `Mockup provider: built-in`, `Design system: .superdesign/design-system.md`, `.superdesign/init/`, `.superdesign/tmp/`, `resume.json`; `mockup-prompt.md` mentions rebuilding from a superdesign export and `sd-component`. No document tells a subagent to run superdesign (assert that the briefs `scout-prompt.md`, `lens-review-prompt.md`, `batch-review-prompt.md`, `inventory-prompt.md`, `plan-review-prompt.md` do not contain `superdesign`).
- [ ] Edit SKILL.md step 4 (provider check, consent, lead runs it, export and standalone check, fallback, journal record, expert review and fix routes — keep it to a few lines and point to layout.md for the standards and gitignore details), the tier table row and the finish report line; layout.md and mockup-prompt.md per the spec.
- [ ] Full suite passes; commit `tech-lead: superdesign as optional mockup provider (docs)`.

### Task 2: README and version 0.3.0

**Files:** `tech-lead/README.md`, `tech-lead/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `tech-lead/tests/test_packaging.py`

- [ ] Tests first: README mentions `superdesign`, `/plugin marketplace add superdesigndev/superdesign-skill`, `credits`; the two manifests agree (existing test).
- [ ] README: a short optional section (what it adds, install commands from the spec's journal facts, the two costs, consent once per project, fallback to the built-in builder); version `0.3.0` in both manifests; marketplace description mentions the optional superdesign mockup provider.
- [ ] Full suite passes; commit `tech-lead: 0.3.0 README and version`.

### Task 3: Hygiene pass (B16)

**Files:** `tech-lead/scripts/`, `tech-lead/tests/`

Input: the B16 line of `docs/backlog.md` and `research/hygiene-candidates-2.md` from the lead's inventory (haiku low) over the wave. Apply spec Part 2; may edit `tech-lead/tests/helpers.py` for the `run()`/`cwd` change. No behaviour change; every guard test from 0.2.1 (locale, stdin, abbreviation, missing git, status import, schema int, show escape) must still fail without its fix. Time the suite 3 times before and after. Commits `tech-lead: hygiene — <kind>`.

### Task 4: Lead verification (lead)

- [ ] Full suite; `ledger.py check` on all initiative ledgers; version 0.3.0 in both manifests; close B15 and B16 in `docs/backlog.md`; update the suite ratchet when there is no regression; `status.py --write`; final whole-branch review.
