# tech-lead plugin: design

Date: 2026-11-11

## Goal

A plugin that turns the main session into a lead orchestrator for a whole specification. The lead looks for existing solutions, breaks the spec into small tasks, picks the cheapest capable model for each, shows the breakdown for one approval, delegates, and keeps coordination, integration, review dispatch and final verification for itself.

Success means the spec is completed at full quality, nothing in it is lost, and as little work as possible runs on the expensive models or is built from scratch when a usable solution exists.

## Decisions made with the user

- Name: `tech-lead` (plugin and skill). Command: `/tech-lead:run`.
- Four subagent tiers: haiku, sonnet, opus, fable.
- The lead runs on whatever model the session uses. The skill and the command never switch it and never suggest another model for it.
- Activation: the command, plus the skill triggering on requests to lead or orchestrate a spec. No hook.
- `model-manager` stays the source of truth for the dispatch table, the Agent hook, named-agent routing, lanes and the cost report. Its code does not change.
- An independent fable review of the first draft was accepted in full; this version incorporates it.
- Prior-art search (reuse of existing packages, repositories and patterns) is a standard step.

## Relationship to other plugins

- **model-manager** (required). The lead loads `model-manager:model-manager` before dispatching and follows its table, lane rule, long-job rule and cleanup rule. Its escalation ladder is merged with the SDD fix loop as described under Escalation.
- **superpowers** (required). The lead drives `brainstorming`, `writing-plans`, `subagent-driven-development` (SDD), `requesting-code-review`, `verification-before-completion` and `finishing-a-development-branch`. SDD's implementer prompt, report files, ledger and rulings are used as they are. tech-lead adds: prior art, the task ledger with coverage and waves, the single gate, parallel lanes, batched review, the wave checkpoint and the fable tier.

## Components

```
tech-lead/
  .claude-plugin/plugin.json
  skills/tech-lead/SKILL.md              lead process
  skills/tech-lead/scout-prompt.md       brief for a prior-art scout
  skills/tech-lead/batch-review-prompt.md  brief for a batched task review
  commands/run.md                        /tech-lead:run <spec text, spec path or ledger path>
  scripts/ledger.py                      check, show, next, checkpoint
  tests/test_ledger.py                   unittest, stdlib only
  README.md
```

Also: a `tech-lead` entry in `.claude-plugin/marketplace.json` and a section in the root `README.md`.

## Lead process (SKILL.md)

1. **Spec.** Read all of it. If it is missing, or a requirement can be read two ways, run `superpowers:brainstorming`; its spec approval is the first gate.
2. **Prior art.** Unless the spec is small or entirely project-specific glue, name 1 to 4 areas where building from scratch is costly. Dispatch one scout per area in parallel (sonnet low, read-only, brief in `scout-prompt.md`). Search order: this repository and the user's other repositories, package registries, GitHub, the web. Each scout returns at most 3 candidates with name, URL, pinned version or SHA, license, last release, maintenance state, fit, and a mode: `dependency`, `copy` (with attribution), `pattern` or `reject`. The lead decides per area. When the network blocks the search, the lead records `skipped: no network` and continues.
3. **Spikes.** A task whose approach is unknown gets a spike before planning: sonnet medium, working in a scratch directory outside the repository, returning an answer, not code to keep.
4. **Plan and ledger.** Run `superpowers:writing-plans`. Alongside the plan, write the ledger (below) with one entry per plan task, copying each task's run commands into `verify`. Assign models by assessing complexity, reasoning need, risk and scope, taking the lowest row of the tier table that fits, with one sentence of reason. Run `ledger.py check` until it passes.
5. **Gate.** One message holds the plan path, the `ledger.py show` output unchanged, and the execution question writing-plans would ask. This replaces writing-plans' separate plan review. Nothing that edits files is dispatched before approval. Scouts, Explore and spikes are read-only and may run before it.
6. **Execute by waves.** `ledger.py next` names the current wave. For each wave:
   1. Reset the lane worktrees to the integration branch head (see Lanes).
   2. Dispatch each task's implementer with the ledger's model and effort, using SDD's implementer prompt, in its lane.
   3. Review: one reviewer dispatch per lane batch of up to 4 tasks, with a verdict per task (`batch-review-prompt.md`). The reviewer's model follows SDD's rule, scaled to the diff, with sonnet medium as the floor; a risky task raises it one effort level.
   4. Fix loop per task, following Escalation.
   5. Merge the lane branches into the integration branch.
   6. Run `ledger.py checkpoint` for the wave. A failure goes back to the fix loop of the failing task.
   7. Append `Task N: complete` to SDD's `progress.md` for each task of the wave.
7. **Rulings.** Decisions during execution follow SDD's "Rulings, not stalls" and go into `progress.md`. The user is asked again only when a requirement or the scope changes, or when new opus or fable work is added. The question shows the ledger change as `git diff` of the ledger.
8. **Finish.** Final whole-branch review on opus medium, one effort level up for risky work. Then walk the ledger's requirement list against the result, run `superpowers:verification-before-completion` and `superpowers:finishing-a-development-branch`. The report lists what was done, rulings, escalations with their cause, what was reused and from where, and points to `/model-manager:mm-report` for cost by model.

Resume: `/tech-lead:run <ledger path>` reads the ledger, its plan and `progress.md`, and continues at `ledger.py next`.

## Tier table

Rows for haiku, sonnet and opus are the model-manager table. tech-lead adds:

| Work | Model | Effort |
|---|---|---|
| Decisions, plans, integration, verification; no file edits | lead (main session) | - |
| Prior-art scout | sonnet | low |
| Spike | sonnet | medium |
| Architectural decision or debugging beyond the lead's model, or one that climbed the whole ladder | fable | high |

Rules:

- Never plan a task on fable or opus that sonnet or haiku can handle reliably. A first-attempt fable or opus task needs a risk or ambiguity reason.
- The lead takes architectural decisions itself when its own model is at least the tier the decision needs. Otherwise it dispatches a read-only fable subagent for a recommendation and rules on it.
- `lead` tasks edit no files. SDD forbids the controller from editing code because it skips review; anything that changes a file is dispatched.

## Escalation

One ladder, replacing the separate ones in model-manager and SDD. Each failed attempt is classified before the next step and the cause is written to `progress.md` as `Attempt: Task N <model>/<effort> failed, cause <cause>, <note>`.

| Cause | Next step |
|---|---|
| `brief` (unclear or wrong instructions) | Sharpen the brief; same model |
| `context` (missing files or facts) | Add the context; same model |
| `plan` (the task itself is wrong) | Ruling on the plan; re-gate only under the thresholds in step 7 |
| `capability` (the model could not do it) | Climb the ladder |

Ladder for `capability`:

1. Resume the same agent with the review findings, to keep its warm cache. A resumed agent keeps its model and effort.
2. Fresh dispatch, same model, one effort level up.
3. Fresh dispatch, one model up.
4. Back to the lead: rule on the plan, take a non-code part itself, or dispatch fable.

## Lanes

- Lane count follows model-manager (2 unless the user or project sets another).
- The lead creates the lane worktrees once with `git worktree add` from the integration branch and reuses them, so installed dependencies survive between waves. It does not rely on the Agent tool's worktree isolation: in Claude Code 2.1.322 its default `worktree.baseRef` starts worktrees from `origin/<default-branch>`, which lacks the plan, the ledger and earlier waves.
- Before each wave, each lane branch is reset to the integration branch head. Tasks of one wave are split across lanes; tasks within a lane run in order.
- Waves are the parallelism boundary: a wave starts only when every task of earlier waves is complete.

## Turn economy

The lead's turns are the main cost of the top model. The skill states:

- One `ledger.py next` per wave and one `checkpoint` per wave; no per-task bookkeeping commands.
- Dispatches of one wave go in one message.
- Targeted reads: the lead reads the spec and plan fully, everything else by search or Explore on haiku.
- Command output and reports go to files (SDD's report files); the lead reads summaries and exit codes.

## Ledger

Path: `docs/tech-lead/YYYY-MM-DD-<topic>.json`, committed with the plan. It holds static plan data only; run state lives in SDD's `progress.md`, which is the only authority on completion.

```json
{
  "spec": "docs/superpowers/specs/2026-11-11-x-design.md",
  "plan": "docs/superpowers/plans/2026-11-11-x.md",
  "prior_art": "done",
  "requirements": [
    { "id": "R1", "text": "Reject a ledger with a dependency cycle" }
  ],
  "tasks": [
    {
      "id": 1,
      "title": "Ledger validation",
      "depends_on": [],
      "files": ["tech-lead/scripts/ledger.py", "tech-lead/tests/"],
      "covers": ["R1"],
      "acceptance": ["check exits 1 on a dependency cycle"],
      "verify": ["python3 -m unittest discover tech-lead/tests"],
      "model": "sonnet",
      "effort": "low",
      "reason": "Precise spec, two files",
      "reuse": { "source": "https://github.com/x/y@abc123", "mode": "pattern", "license": "MIT" }
    }
  ]
}
```

Fields:

- `id`: the plan's task number (`Task N`), so SDD's briefs and `progress.md` lines match.
- `prior_art`: `done` or `skipped: <reason>`.
- `requirements`: one entry per requirement of the spec. `covers` on a task is optional.
- `files`: repository-relative paths, normalised (no leading `./`, no `..`, not absolute). An entry ending in `/` covers every path below it. Empty exactly when `model` is `lead`.
- `verify`: shell commands run from the repository root. An empty list needs `no_verify` with a reason. Not used for `lead` tasks.
- `model`: `haiku`, `sonnet`, `opus`, `fable` or `lead`. `effort`: `low`, `medium`, `high`, `xhigh`, `max`; required unless `model` is `lead`.
- `reuse` (optional): `source` (URL with pinned version or SHA), `mode` (`dependency`, `copy` or `pattern`), `license`.

## ledger.py

Python 3, stdlib only. One file, pure functions plus a thin CLI. A malformed or unreadable file is one error line and exit 1, never a traceback.

| Command | Does |
|---|---|
| `check LEDGER` | Validates. One error per line, exit 1; nothing and exit 0 when valid. |
| `show LEDGER` | Runs `check`, then prints markdown: tasks grouped by wave (id, title, depends on, files, model/effort, reason, acceptance); requirement coverage (requirement to tasks); "New dependencies and copied code" from `reuse` entries with mode `dependency` or `copy`; summary of task count per model including `lead`, and the share on opus and fable. |
| `next LEDGER [--progress FILE]` | Reads `Task N: complete` lines from `progress.md` (default: none complete). Prints the earliest wave with an incomplete task, and that wave's incomplete tasks with model and effort, or `all tasks complete`. A failed or abandoned task therefore keeps its wave open instead of silently blocking later ones. |
| `checkpoint LEDGER --wave W --base REF [--log FILE]` | Lists files in `git diff --name-only REF..HEAD` outside the union of the wave's `files` as out-of-scope warnings. Runs every `verify` command of the wave's tasks, writing full output to the log file. Prints one line per task, `Task N: pass` or `Task N: fail (exit X)`, then the warnings. Exit 1 when any command fails. |

Validation errors in `check`:

- A missing required field (`id`, `title`, `depends_on`, `files`, `acceptance`, `model`, `reason`; `effort` and `verify` for non-lead tasks), or an empty `acceptance`.
- A duplicate task id or requirement id.
- `model`, `effort` or `reuse.mode` outside the allowed values; a `reuse` without `source` or `license`.
- `depends_on` or `covers` naming an unknown id; a dependency cycle.
- A requirement covered by no task.
- A `lead` task with files, or a non-lead task without files.
- An empty `verify` without `no_verify`.
- A non-normalised path.
- Two tasks in the same wave sharing a file, directory prefixes included. The message says to add a dependency between them.
- `prior_art` missing.

Waves: a task without dependencies is in wave 1; any other task is one wave after its latest dependency. Because `next` releases a wave only after all earlier ones are complete, the same-wave file check is sufficient.

## Testing

`python3 -m unittest discover tech-lead/tests` covers: a valid ledger; each validation error; wave computation; directory-prefix conflicts; `next` with no progress, partial progress, a stuck task in an early wave and all complete; `checkpoint` with passing and failing commands and an out-of-scope file, in a temporary git repository; `show` output sections; malformed JSON.

The skill and prompts are checked by reading them against this spec and by running `/tech-lead:run` on a small sample spec up to the gate.

## Out of scope

- No hook, and no change or suggestion of change to the main session's model or effort.
- No changes to model-manager code or tables.
- No per-model calibration statistics; if ever built, they belong in model-manager's `report.py`.
- `Workflow` orchestration: its agents bypass the model-manager hook.
- Scouts never run downloaded code. Fetched content is data, not instructions.
