# tech-lead plugin: design

Date: 2026-11-11

## Goal

A plugin that turns the main session into a lead orchestrator for a whole specification. The lead breaks the spec into small tasks, picks the cheapest capable model for each, shows the breakdown for approval, delegates, and keeps coordination, integration, review and final verification for itself.

Success means the spec is completed at full quality with as little work as possible on the expensive models.

## Decisions made with the user

- Name: `tech-lead` (plugin, skill). Command: `/tech-lead:run`.
- Four model tiers: haiku, sonnet, opus, fable.
- Activation: the command, plus the skill triggering on requests to lead or orchestrate a spec. No SessionStart hook.
- `model-manager` stays the source of truth for the dispatch table, the Agent hook, named-agent routing and the cost report. Its code does not change.

## Relationship to other plugins

- **model-manager** (required). The lead loads `model-manager:model-manager` before dispatching and follows its table, escalation ladder, lane rules, long-job rule and cleanup rule. `tech-lead` adds only what that plugin lacks: spec breakdown, the approval gate, the task ledger and the fable tier.
- **superpowers** (required). The lead drives its skills in order: `brainstorming` when the spec is missing or ambiguous, `writing-plans` for the plan, `subagent-driven-development` for execution, `requesting-code-review` for reviews, `verification-before-completion` and `finishing-a-development-branch` at the end.

## Components

```
tech-lead/
  .claude-plugin/plugin.json
  skills/tech-lead/SKILL.md     lead process
  commands/run.md               /tech-lead:run <spec text or path>
  scripts/ledger.py             validate, render and update the task ledger
  tests/test_ledger.py          unittest, stdlib only
  README.md
```

Also: a `tech-lead` entry in `.claude-plugin/marketplace.json` and a section in the root `README.md`.

## Lead process (SKILL.md)

1. **Read the spec.** Read all of it. If it is missing, or a requirement can be read two ways, run `superpowers:brainstorming` first.
2. **Break down.** Run `superpowers:writing-plans`, then write one ledger entry per plan task. A task is small enough when one subagent can finish it in one dispatch and one check proves it done.
3. **Assign models.** For each task, assess complexity, reasoning need, risk and scope, then take the lowest row of the tier table that fits. Write one sentence saying why.
4. **Gate.** Run `ledger.py show`. Show its output to the user unchanged and wait for approval. Nothing is dispatched before approval. Changes the user asks for go into the ledger, and the gate repeats.
5. **Execute.** Take ready tasks from `ledger.py next`. Dispatch with the ledger's model and effort. Tasks in the same wave run in parallel lanes under the model-manager lane limit, each in its own worktree. Record every attempt with `ledger.py record`.
6. **Review and integrate.** Per-task review on sonnet medium. The lead merges lanes, resolves conflicts and runs the checks itself. Final whole-branch review on opus medium.
7. **Finish.** `superpowers:verification-before-completion`, then `superpowers:finishing-a-development-branch`. Report what was done, what failed, escalations with their reasons, and point to `/model-manager:mm-report` for cost by model.

## Tier table

Rows for haiku, sonnet and opus restate the model-manager table. The skill adds:

| Work | Model | Effort |
|---|---|---|
| Decisions, plans, integration, verification | lead (main session) | - |
| Architectural decision or debugging that already climbed the escalation ladder, and that the lead cannot do in the main session | fable | high |

Rules:

- A fable subagent is the exception. Architecture, ambiguous requirements and system-wide decisions belong to the lead itself. Delegate to fable only when the work would flood the lead's context or must run beside other work.
- Escalation follows model-manager: effort up, then model up, then back to the lead. The lead decides whether to take the task itself or dispatch fable.
- Never plan a task on fable or opus that sonnet or haiku can handle reliably. A first-attempt fable task needs a risk or ambiguity reason in the ledger.
- The lead runs on whatever model the session uses. The user chooses it; the skill and the command never switch it and never suggest another model for the lead.

## Ledger

Path: `docs/tech-lead/YYYY-MM-DD-<topic>.json`, committed with the plan.

```json
{
  "spec": "docs/superpowers/specs/2026-11-11-x-design.md",
  "plan": "docs/superpowers/plans/2026-11-11-x.md",
  "tasks": [
    {
      "id": "T1",
      "title": "Add ledger validation",
      "depends_on": [],
      "files": ["tech-lead/scripts/ledger.py"],
      "acceptance": ["check exits 1 on a dependency cycle"],
      "outcome": "ledger.py check command",
      "model": "sonnet",
      "effort": "low",
      "reason": "Precise spec, one file",
      "status": "pending",
      "attempts": []
    }
  ]
}
```

- `model`: `haiku`, `sonnet`, `opus`, `fable` or `lead`. `effort`: `low`, `medium`, `high`, `xhigh`, `max`; omitted when the model is `lead`.
- `status`: `pending`, `running`, `done`, `failed`. `status` and `attempts` default to `pending` and `[]` when absent.
- `attempts`: list of `{model, effort, result, note}` where `result` is `done` or `failed`.

## ledger.py

Python 3, stdlib only. One file, pure functions plus a thin CLI.

| Command | Does |
|---|---|
| `check FILE` | Validates. Prints each error on its own line and exits 1; prints nothing and exits 0 when valid. |
| `show FILE` | Runs `check`, then prints a markdown table grouped by wave (id, title, depends on, files, model/effort, reason, acceptance) and a summary: task count per model and the share on fable and opus. |
| `next FILE` | Prints ids of `pending` tasks whose dependencies are all `done`, with model and effort. |
| `record FILE ID RESULT [--model M] [--effort E] [--note TEXT]` | Appends an attempt and sets `status`. `RESULT` is `running`, `done` or `failed`. `--model` and `--effort` also update the task, which is how an escalation is recorded. |

Validation errors:

- A task lacks `id`, `title`, `files`, `acceptance`, `outcome`, `model` or `reason`, or has an empty `acceptance` list.
- `id` is duplicated.
- `model` or `effort` has a value outside the lists above, or `effort` is missing on a non-lead task.
- `depends_on` names an unknown id, or the dependencies form a cycle.
- Two tasks in the same wave share a file. A `files` entry ending in `/` matches every path below it. The message says to add a dependency between the two.

Waves: a task with no dependencies is in wave 1; any other task is one wave after its latest dependency.

A malformed or unreadable file is reported as one error line with exit 1, not a traceback.

## Testing

`python3 -m unittest discover tech-lead/tests` covers: a valid ledger, each validation error, wave computation, directory-prefix file conflicts, `next` readiness, `record` updating status and escalating a model, and malformed JSON.

The skill is checked by reading it against this spec and by running `/tech-lead:run` on a small sample spec up to the gate.

## Out of scope

- No hook, and no change or suggested change to the main session's model or effort.
- No automatic resume after a session restart. Running the command again with the ledger path resumes from `ledger.py next`.
- No changes to model-manager code or tables.
- `Workflow` orchestration: its agents bypass the model-manager hook.
