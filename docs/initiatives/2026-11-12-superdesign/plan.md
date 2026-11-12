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

1. Without the plugin, without consent, or without an authenticated CLI, step 4 behaves exactly as in 0.2.0 (Task 1).
2. The consent question lists credits, lead tokens, everything sent to superdesign (spec, request, project files, uploaded images as public URLs) and the unpinned CLI; consent lives in git-ignored `.tech-lead/superdesign-consent` and is asked once (Task 1).
3. Every subagent brief forbids invoking the superdesign skill or CLI; only the repository-analysis brief is the documented exception (Task 1).
4. Autopilot without recorded consent uses the built-in builder without asking (Task 1).
5. A non-standalone export falls back to a local rebuild; screen ids and the screen-to-requirement mapping exist on both paths (Task 1).
6. `.gitignore` allowlist: only `.superdesign/design-system.md` is committed (Task 1).
7. Hygiene changes keep every message and exit code (Task 3).
8. Live behaviour with a real superdesign account is untested in this initiative (backlog B1); tests cover the documents only.

---

Waves: 1 = Tasks 1, 2 (lane 1: Task 1; lane 2: Task 2); 2 = Task 3; 3 = Task 4.

### Task 1: Superdesign in the skill documents

**Files:** `tech-lead/skills/tech-lead/SKILL.md`, `layout.md`, `mockup-prompt.md`, `scout-prompt.md`, `lens-review-prompt.md`, `batch-review-prompt.md`, `inventory-prompt.md`, `plan-review-prompt.md` (all in `tech-lead/skills/tech-lead/`), `tech-lead/tests/test_skill_docs.py`, `tech-lead/tests/test_prompts.py`

- [ ] Tests first: every `*-prompt.md` and SKILL.md's implementer-brief rule contain `Never invoke the superdesign skill or the superdesign CLI.`; SKILL.md mentions `superdesign:superdesign`, `.tech-lead/superdesign-consent`, `credits`, `main session`, `get-design --draft-id`, `import-design-draft --into`, `built-in` and still names the built-in builder with `mockup-prompt.md` (built-in path unchanged); the consent text in SKILL.md or layout.md names `public URLs` and `unpinned`; layout.md mentions `.superdesign/*`, `!.superdesign/design-system.md`, `Design system: .superdesign/design-system.md`; `mockup-prompt.md` describes the superdesign-export mode with `sd-component`, the allowed remote resources (Tailwind CDN, Lucide) and adding screen ids and the mapping. In SKILL.md, assert the step-4 conditions appear in this order: `superdesign:superdesign`, then `.tech-lead/superdesign-consent`, then `login`, then the built-in fallback; assert the repository-analysis exception says it writes only `.superdesign/init/` and never runs the CLI; assert the sentence listing what every subagent brief carries includes the never-invoke line (it reaches SDD's own implementer and reviewer briefs that way).
- [ ] Edit SKILL.md step 4 per spec Part 1 (requirements, conditions incl. autopilot, consent, lead-only with the init exception, flow steps 1-7 — a few lines, details to layout.md and mockup-prompt.md), the implementer-brief rule, the tier rows and the finish report line; layout.md and mockup-prompt.md per the spec; add the never-invoke line to every `*-prompt.md`.
- [ ] Full suite passes; commit `tech-lead: superdesign as optional mockup provider (docs)`.

### Task 2: README and version 0.3.0

**Files:** `tech-lead/README.md`, `tech-lead/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `tech-lead/tests/test_packaging.py`

- [ ] Tests first: README mentions `superdesign`, `/plugin marketplace add superdesigndev/superdesign-skill`, `npx --yes @superdesign/cli@latest login`, `credits`; the two manifests agree (existing test).
- [ ] README: a short optional section (what it adds; requirements: shell, Node, browser; install and login commands; consent per user with what it costs and sends; fallback to the built-in builder; not yet run live, see backlog B1); version `0.3.0` in both manifests; marketplace description mentions the optional superdesign mockup provider.
- [ ] Full suite passes; commit `tech-lead: 0.3.0 README and version`.

### Task 3: Hygiene pass (B16)

**Files:** `tech-lead/scripts/`, `tech-lead/tests/`

Input: the B16 line of `docs/backlog.md` and `research/hygiene-candidates-2.md` from the lead's inventory (haiku low) over the wave. Apply spec Part 2; may edit `tech-lead/tests/helpers.py` for the `run()`/`cwd` change. No behaviour change; every guard test from 0.2.1 (locale, stdin, abbreviation, missing git, status import, schema int, show escape) must still fail without its fix. Time the suite 3 times before and after; per-test time may exceed the ratchet by at most a 10% noise margin. Commits `tech-lead: hygiene — <kind>`.

### Task 4: Lead verification (lead)

- [ ] Full suite; `ledger.py check` on all initiative ledgers; version 0.3.0 in both manifests; close B15 and B16 in `docs/backlog.md`; update the suite ratchet when there is no regression; `status.py --write`; final whole-branch review.
