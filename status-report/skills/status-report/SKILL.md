---
name: status-report
description: Use when the owner should hear where the work stands — on a schedule (every few hours of an autonomous session), right after a release or a closed stage, or when asked "status", "podsumowanie", "what's going on". Builds a five-section report from facts: released since last time, in progress with %, next, milestones with %, and the questions waiting on the owner.
---

# Status report

The owner reads this instead of the scrollback. Every number comes from a source you just checked, never from memory.

## When

- **Periodic.** In a long autonomous session, report every `interval_hours` from the config (default 3). Set it up once per session, when the owner asks for periodic reports or the session turns autonomous: schedule a recurring prompt "status report" (CronCreate or `/loop` with the interval). Say once that it is set and how to stop it.
- **On a stage.** Right after a release, a merged stage or a closed milestone, send the short form: section 1 for that release, plus section 5 if something now waits on the owner.
- **On request.** The full report.

## Gather facts

1. Run `python3 <skill dir>/scripts/facts.py --root <project root>`. It returns JSON with:
   - `releases`: tags since the last report;
   - `milestones`: checklist done/total and %, with the paused flag;
   - `in_progress` and `waiting_on_owner`: issues by label.

   The project config is `.claude/status-report.json`; its fields are in the `README.md` of this plugin.
2. Add what the script cannot see:
   - running agents, CI runs and background jobs, with their current state;
   - questions you are holding for the owner;
   - items marked `[do potwierdzenia]` / to be confirmed.
3. After sending a full report, run `facts.py --mark` so the next report starts from now.

## Format

Use the owner's language (the config's `language`, else the conversation's). The title is a heading with the date and time. Use tables, and keep each cell short.

1. **✅ Released since <time>.** Columns: release (version, time), what in owner terms, issues with checklist progress (`#504 4/4`).
2. **🔄 In progress.** Columns: what, state (the concrete current step, e.g. "train 2/3 parts green"), %. The % is the checklist share or your stated estimate; label an estimate `~`.
3. **⏭️ Next.** A numbered list of at most 5 items, in the order you will do them. Name the blocker if there is one.
4. **Milestones.** Columns: label, name, `done/total, **pct%**`. Use ✅ at 100% and ⏸️ when paused.
5. **⚠️ Waiting on you.** Columns: topic, when it is needed (now / when convenient / after X).
   - Each row is one decision, phrased so the owner can answer it.
   - Put the recommended answer in the row when you have one.
   - Never list a question the owner has already answered: check the conversation and the issue comments.

End with one line saying whether you keep working on your own.

## Rules

- Facts only. Write a red run as red and a skipped step as skipped. A guess carries `~` or [do potwierdzenia].
- Name things the way the project does (codes, issue numbers). Room or element codes come with a human name.
- Do not repeat what the previous report said unless it changed. "No change" is a valid cell.
- Keep the report under one screen. Detail lives in the issues; link them.
