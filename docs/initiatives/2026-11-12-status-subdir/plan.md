# tech-lead 0.3.2 status from a subdirectory (B19) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `status.py` finds the repository-level `docs/initiatives/` when a session starts in a subdirectory; release 0.3.2.

**Architecture:** one helper `resolve_root` in `status.py`, applied in `main`.

**Tech Stack:** Python 3.9+ stdlib, `unittest`.

**Spec:** `docs/initiatives/2026-11-12-status-subdir/spec.md`

## Global Constraints

- Python 3.9+ (`from __future__ import annotations`), stdlib only; `--brief` never raises or prints noise; git calls with a 5 s timeout, `GIT_DIR`/`GIT_WORK_TREE` not relied on.
- Tests share one temporary git repository per test class (local identity, `commit.gpgsign=false`, `GIT_DIR`/`GIT_WORK_TREE` removed, paths compared after `os.path.realpath`).
- Suite: `python3 -m unittest discover tech-lead/tests` (169 tests; ratchet 1.12 s / 166 in `docs/standards.md`).

## Review Focus

1. A subdirectory that has its own `docs/initiatives/` keeps priority over the top level.
2. `--brief` stays silent and exits 0 when git is missing, slow or fails.

---

Waves: 1 = Task 1; 2 = Task 2.

### Task 1: resolve_root and 0.3.2

**Files:** `tech-lead/scripts/status.py`, `tech-lead/tests/test_status.py`, `tech-lead/skills/tech-lead/SKILL.md`, `tech-lead/README.md`, `tech-lead/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

- [ ] Tests first: the five cases in the spec's Tests section (each must fail before the change where it guards new behaviour).
- [ ] Implement `resolve_root(root: Path) -> Path` via `_git` with a `timeout` parameter and apply it in `main`; SKILL.md ROOT line; README sentence; version 0.3.2 in both manifests.
- [ ] Full suite passes; commit `tech-lead: status finds docs/initiatives from a subdirectory session (B19), 0.3.2`.

### Task 2: Lead verification (lead)

- [ ] Full suite; `ledger.py check` on all ledgers; close B19 in `docs/backlog.md`; `status.py --write`; final review.
