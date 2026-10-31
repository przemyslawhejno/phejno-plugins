---
name: model-manager
description: Use when about to dispatch a subagent, choosing a model or effort for delegated work, splitting a plan into parallel lanes, or when a subagent would wait on a long-running job
---

# Model manager

The coordinator decides and verifies; workers implement. The table in the session policy assigns `model` and `effort`. This skill covers the cases the table leaves open. It adds to superpowers:subagent-driven-development and fills its `[MODEL]` slot; the dispatches in superpowers:requesting-code-review and superpowers:dispatching-parallel-agents, which have no slot, take the same values.

## Classify by what the task needs

| Observable signal | Row |
|---|---|
| Plan contains the complete code | haiku medium |
| Output is a list or a summary, nothing is edited | haiku low |
| Spec states inputs, outputs and files; 1-2 files | sonnet low |
| Prose description, 3+ files, or the cause is unknown | sonnet medium |
| Last task review of a branch before merge | opus medium |

A task matching two rows takes the higher one. Security, data migration, hard-to-undo or system-wide work goes one effort level up, including the final review. A model the user names wins over this section. Several small edits of the same shape go in one dispatch.

## Escalation

1. Same model, one effort level up.
2. One model up.
3. Reaching opus returns to the coordinator, which decides.

Resume the same agent for a fix round so it keeps its warm cache.

## Lanes

Tasks run at the same time when their `Files:` lists are disjoint and neither depends on the other's interfaces. Each lane has its own worktree and branch, its task reviews run per lane, and the coordinator merges. Tasks sharing a file stay in one lane, in order. The default is 2 lanes; a user or project limit replaces it.

## Long jobs

The coordinator starts anything over 4 minutes in the background and hands the finished log to haiku low. Long waits inside a subagent expire its cache, and the next turn rewrites the whole context.

## Cleanup

A finished agent makes no requests and costs nothing. An agent still running costs tokens on every turn, and a leftover server, browser or test run holds CPU and can distort other sessions' tests.

Check the running list before ending a turn and after any change of direction:

| State | Action |
|---|---|
| Finished | none |
| Doing needed work, recent progress | keep |
| Work superseded or no longer needed | TaskStop |
| Repeating the same step, or no new output since the last check | read its output, then TaskStop and re-dispatch with a sharper brief |
| Shell, server or browser you started, its check is done | stop it; kill only your own PIDs |

## Brief

A brief holds the goal, the files, what is already ruled out, and the check that proves the task done. Point at files instead of pasting them.

## Quality

Cheaper routing never removes a gate. A haiku result passes the same tests and review as any other.
