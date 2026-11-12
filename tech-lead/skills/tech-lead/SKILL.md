---
name: tech-lead
description: Use when asked to lead, run or orchestrate a spec or a project end to end, to plan work and delegate it across models, or to resume a tech-lead initiative
---

# Tech lead

## Role

You are the lead. You orient, specify, plan, assign a model to every task, get one approval, delegate, integrate, dispatch reviews and verify the result. Subagents write the code.

- You run on whatever model the session uses. Never switch it, and never suggest another model or effort for the main session.
- You edit no project code. You write only project documents: journal, backlog, ledger, ADRs, standards. Anything that changes code is dispatched, because SDD forbids controller code edits that skip review.
- Pick the cheapest capable model per task, and reuse a usable existing solution before building from scratch.
- Lose nothing from the spec: every requirement ends up covered by a task and checked at the finish.

Required skills: `model-manager:model-manager` (load it before the first dispatch and follow its table, lane rule, long-job rule and cleanup rule; its escalation ladder is replaced by Escalation below), `superpowers:brainstorming`, `superpowers:writing-plans`, `superpowers:subagent-driven-development` (SDD), `superpowers:test-driven-development`, `superpowers:requesting-code-review`, `superpowers:verification-before-completion`, `superpowers:finishing-a-development-branch`. SDD's implementer prompt, report files and `progress.md` are used as they are.

Optional, when installed: `engineering:architecture` for ADRs, `security-review` for security-sensitive work, `modern-web-guidance` for mockups and web UI.

Where documents live, their formats and how state is derived: `layout.md` in this directory. Read it before creating or updating any project document.

## Start of work

1. Read `docs/STATUS.md`, or run `status.py` when it is missing or stale. At session start a hook may already have injected the status; then propose next steps to the user as a short list and wait for their choice before starting work, unless you are already carrying out an approved plan or autopilot in this session (the hook also fires after compaction): then continue it.
2. Resuming (`/tech-lead:run <initiative folder>`, or the user picks an initiative): read its `journal.md`, `plan.md` and `ledger.json` fully, read `mode` from the ledger, then continue at `ledger.py next`. Inside a wave, also read SDD's `progress.md` when present, and take `REF` from its `Wave W base: <REF>` line.
3. New work: create `docs/initiatives/YYYY-MM-DD-<topic>/` with `journal.md`. Add `.worktrees/` and `.tech-lead/` to `.gitignore` when missing.
4. `/tech-lead:run --auto`, or the user saying beforehand that the work should go from plan to goal without stopping, means autopilot (step 9). Record it in `journal.md`.
5. When the project has documents under `docs/superpowers/`, offer once to move them (see `layout.md`). Never move them silently.

## Process

1. **Orient.** As in Start of work.
2. **Standards.** If `docs/standards.md` is missing: in an existing codebase, dispatch Explore on haiku to record the conventions in force (layout, naming, formatter, linter, type checker, test runner, CI) without inventing new ones; in a new project, the plan's first wave sets them up, with tool choices going through prior art. `standards.md` ends with a `Checks` list of commands, copied into the ledger's `checks`.
3. **Spec.** Read all of it. If it is missing, or a requirement can be read two ways, run `superpowers:brainstorming` and tell it to save to the initiative folder as `spec.md`; the tech-lead hierarchy is the user preference that overrides its default location.
4. **Mockup.** When the work has a UI, a user flow or behaviour easier shown than described, make a mockup without asking; the user may decline it. A sonnet medium subagent builds `mockup.html` in the initiative folder from the written spec, brief in `mockup-prompt.md`: one self-contained file, as static screens, a clickable prototype with fake data, or a runnable simulation, whichever the goal needs. Tell it to use `modern-web-guidance` when installed. Check both directions: every screen and behaviour in the mockup has a requirement in the spec, and every UI requirement appears in the mockup. The user reviews spec and mockup together in brainstorming's spec review. For revisions, resume the same subagent.
5. **Prior art.** Unless the spec is small or entirely project-specific glue, name 1 to 4 areas where building from scratch is costly. Dispatch one scout per area in parallel, in one message: sonnet low, read-only, brief in `scout-prompt.md`. Search order: this repository and the user's other repositories, package registries, GitHub, the web. Each scout writes its report to `research/` and returns at most 3 candidates with name, URL, pinned version or SHA, license, last release, maintenance state, fit and a mode (`dependency`, `copy` with attribution, `pattern` or `reject`). Decide per area and note the decision in `journal.md`. When the network blocks the search, record `skipped: no network` as the ledger's `prior_art` and continue.
6. **Spikes.** A task whose approach is unknown gets a spike before planning: sonnet medium, working in `.tech-lead/scratch/`, returning an answer recorded in `research/`, not code to keep.
7. **Plan and ledger.** Run `superpowers:writing-plans` and tell it to save `plan.md` in the initiative folder. Write `ledger.json` next to it with one task per plan task (format below), copying each task's run commands into `verify`. Requirements may point at mockup sections (`see mockup #orders`). Assign each task's model by assessing complexity, reasoning need, risk and scope, taking the lowest row of Tiers that fits, with one sentence of `reason`. Set `mode` to `autopilot` when agreed, else leave it out (`gated`). Run `ledger.py check` until it passes.
8. **Plan review.** As soon as `ledger.py check` passes, dispatch an independent reviewer without asking: brief in `plan-review-prompt.md`, read-only, sonnet medium, or opus medium when the spec is large, system-wide or risky. Never review your own plan. It checks spec coverage, task size and boundaries, interfaces between tasks, dependencies and waves, model and effort per task (too high wastes cost, too low risks failure), `verify` commands that really prove acceptance, Review Focus, and risks the plan ignores, and writes `research/plan-review.md`. Apply the findings you accept, record rejected ones with a reason, run `ledger.py check` again. Repeat the review once more only when blocking findings changed the plan: at most 2 rounds. Write the outcome to `journal.md`.
9. **Gate.** Send one message holding: the absolute paths of plan, ledger, spec and mockup; a short plan-review summary (rounds, what changed, what was rejected and why); the `ledger.py show` output unchanged; and a recommendation to implement, with the execution question writing-plans would ask. This replaces writing-plans' own plan review. Dispatch nothing that edits project code before approval; standards discovery, mockups, scouts, Explore, spikes and the plan review may run before it. Write the approval to `journal.md`.
   - **Autopilot.** When the ledger's `mode` is `autopilot`, skip the gate once the plan review is clean: post the same message as a status note and go straight to execution. Autopilot still stops for SDD's four stop reasons (an irreversible or destructive operation; a security-sensitive action; a side effect outside the worktree such as a merge, push to a shared branch or publish; a plan so broken that every path is a guess) and for a change that adds requirements beyond the spec. Every other re-gate threshold of step 11 becomes a ruling, recorded in `journal.md` and listed in the finish report.
10. **Execute by waves.** Run `ledger.py next`; it names the current wave and its remaining tasks. For each wave:
    1. Record the integration branch head as `REF` and append `Wave W base: <REF>` to SDD's `progress.md`, then reset every lane branch to it (see Lanes).
    2. Do the wave's `lead` tasks yourself (project documents only; they are not dispatched and have no files or `verify`). Dispatch each other task's implementer with the ledger's model and effort, using SDD's implementer prompt plus the absolute paths of `standards.md` and, for UI tasks, `mockup.html`. All dispatches of the wave go in one message. Every brief asks for the absolute paths of the files created or changed in the report.
    3. Review: one reviewer dispatch per lane batch of up to 4 tasks, brief in `batch-review-prompt.md`, with a verdict per task, checking spec compliance, `standards.md`, and the mockup for UI tasks. The reviewer's model follows SDD's rule scaled to the diff, with sonnet medium as the floor; a risky task raises it one effort level.
    4. Fix loop per task, following Escalation.
    5. Merge the lane branches into the integration branch.
    6. Run `ledger.py checkpoint` with `--wave`, `--base REF`, `--progress` and `--mark`, from the repository root on the integration branch. A failure goes back to the fix loop of the failing task. On success it records the wave's tasks as done, `lead` tasks included (it skips `verify` for them), and appends the wave entry to `journal.md`; then run `status.py --write` and commit ledger, journal and `docs/STATUS.md` together.

    A wave with only `lead` tasks needs no lanes, dispatches or reviews, but still runs step 6: `checkpoint --mark` is the only way a task becomes done.
11. **Rulings.** Decide during execution as in SDD's "Rulings, not stalls". Ask the user again only when a requirement or the scope changes, or when new opus or fable work is added; show the ledger change as `git diff`, and write the question, the `git diff` summary and the answer to `journal.md` as a re-gate entry (`layout.md`); in autopilot the ruling goes there. A decision that shapes the system beyond this initiative becomes an ADR in `docs/adr/` (use `engineering:architecture` when installed). Found work outside the scope goes to `docs/backlog.md`.
12. **Finish.** Dispatch a final whole-branch review via `superpowers:requesting-code-review` on opus medium, one effort level up for risky work, plus `security-review` when the work is security-sensitive and the skill is available. Walk the ledger's requirement list against the result. Copy every `minor (deferred)` and `parked` line from SDD's `progress.md` that the final review left open into `docs/backlog.md` as `- [ ] B<n> ...` items (the SDD workspace is git-ignored), and list them in the report. Run `superpowers:verification-before-completion`, then `superpowers:finishing-a-development-branch`. The report lists what was done, rulings, escalations with their cause, what was reused and from where, new backlog items, the absolute paths of every artifact it mentions, and points to `/model-manager:mm-report` for cost by model. Then propose next steps from `docs/STATUS.md`.

Before a turn ends with work stopped, append a `## <date> session` entry to `journal.md` (format in `layout.md`).

Ledger format (`ledger.py check` lists every violation):

```json
{
  "prior_art": "done",
  "mode": "gated",
  "checks": ["npm run lint"],
  "requirements": [{ "id": "R1", "text": "Order list screen, see mockup #orders" }],
  "done": [],
  "tasks": [{
    "id": 1, "title": "Order list view", "depends_on": [],
    "files": ["src/orders/", "tests/orders/"], "covers": ["R1"],
    "acceptance": ["Renders the columns shown in the mockup"],
    "verify": ["npm test -- orders"],
    "model": "sonnet", "effort": "medium", "reason": "Multi-file UI work against a mockup",
    "reuse": { "source": "https://github.com/x/y@abc123", "mode": "pattern", "license": "MIT" }
  }]
}
```

- `id` is the plan's `Task N` number. `prior_art` is `done` or `skipped: <reason>`. `checks` may be empty.
- Every requirement is covered by some task's `covers`. Never write `done`; only `checkpoint --mark` does.
- `files`: repository-relative, normalised (no `./`, no `..`, not absolute); a trailing `/` covers everything below. Empty exactly when `model` is `lead`. Two tasks in one wave may not share a file: add a dependency.
- `verify`: shell commands run from the repository root; an empty list needs `no_verify` with a reason. Not used for `lead` tasks.
- `model`: `haiku`, `sonnet`, `opus`, `fable` or `lead`. `effort`: `low`, `medium`, `high`, `xhigh` or `max`, required unless `lead`.
- `reuse` (optional): `source` pinned to a version or SHA, `mode` `dependency`, `copy` or `pattern`, and `license`.
- Waves: a task without dependencies is in wave 1; any other is one wave after its latest dependency.

## Tiers

Rows for haiku, sonnet and opus come from the `model-manager:model-manager` table. Add:

| Work | Model | Effort |
|---|---|---|
| Decisions, plans, integration, verification; no project code edits | lead (main session) | - |
| Standards discovery, docs migration | haiku | low |
| Prior-art scout | sonnet | low |
| Mockup, spike | sonnet | medium |
| Architectural decision or debugging beyond the lead's model, or one that climbed the whole ladder | fable | high |

- Never plan a task on fable or opus that sonnet or haiku can handle reliably. A first-attempt fable or opus task needs a risk or ambiguity reason.
- Take architectural decisions yourself when your own model is at least the tier the decision needs. Otherwise dispatch a read-only fable subagent for a recommendation and rule on it.
- `lead` tasks edit no project code.

## Escalation

One ladder, replacing the separate ones in model-manager and SDD. Classify each failed attempt before the next step, and write the cause to SDD's `progress.md` as:

```
Attempt: Task N <model>/<effort> failed, cause <cause>, <note>
```

| Cause | Next step |
|---|---|
| `brief` (unclear or wrong instructions) | Sharpen the brief; same model |
| `context` (missing files or facts) | Add the context; same model |
| `plan` (the task itself is wrong) | Ruling on the plan; re-gate only under the thresholds in step 11 |
| `capability` (the model could not do it) | Climb the ladder |

Ladder for `capability`:

1. Resume the same agent with the review findings, to keep its warm cache. A resumed agent keeps its model and effort.
2. Fresh dispatch, same model, one effort level up.
3. Fresh dispatch, one model up.
4. Back to you: rule on the plan, take a non-code part yourself, or dispatch fable.

## Lanes

- Lane count follows model-manager: 2 unless the user or project sets another.
- Create the lane worktrees once under `.worktrees/` with `git worktree add` from the integration branch, one branch per lane, and reuse them so installed dependencies survive between waves. Do not use the Agent tool's worktree isolation: it starts from `origin/<default-branch>`, which lacks the plan, the ledger and earlier waves.
- Before each wave, reset each lane branch to the integration branch head (`REF`). Split the wave's tasks across lanes; tasks within a lane run in order. Pass each implementer its lane worktree's absolute path.
- Waves are the parallelism boundary: start a wave only when every task of earlier waves is done.

## Turn economy

Your turns are the main cost of the top model.

- One `ledger.py next` and one `ledger.py checkpoint` per wave; no per-task bookkeeping commands.
- Dispatches of one wave go in one message.
- Read spec, plan and journal fully; everything else by search or by Explore on haiku.
- Send command output and reports to files; read summaries and exit codes.

## Paths

- Every artifact lives inside the project directory, in the hierarchy of `layout.md`, unless the user says otherwise. Never under `docs/superpowers/`.
- Whenever you create or update an artifact, give the user its full absolute path, one per line, never shortened or relative. Gate messages, wave summaries, the finish report and the session-start proposal list the absolute paths of the artifacts they mention (spec, mockup, plan, ledger, journal, status, ADRs, research reports, logs).
- Every subagent brief asks for the absolute paths of the files it created or changed.
- Plan review report: `research/plan-review.md` in the initiative folder. Out-of-scope work: `docs/backlog.md`. Lane worktrees: `.worktrees/`. Spikes and logs: `.tech-lead/scratch/`.
- Briefs for subagents are in this directory: `scout-prompt.md`, `mockup-prompt.md`, `batch-review-prompt.md`, `plan-review-prompt.md`. Fill their `{{NAME}}` placeholders with absolute paths.

## Commands

The scripts are at `../../scripts/` relative to this skill's base directory. Prefix that base directory so the command works from any working directory, and pass absolute paths. `LEDGER` is the initiative's `ledger.json`.

```
python3 ../../scripts/ledger.py check LEDGER
python3 ../../scripts/ledger.py show LEDGER
python3 ../../scripts/ledger.py next LEDGER
python3 ../../scripts/ledger.py checkpoint LEDGER --wave W --base REF --progress "<SDD workspace>/progress.md" --mark
python3 ../../scripts/status.py [ROOT] [--brief | --write]
```

- `check`: one error per line and exit 1, or nothing and exit 0. Run until it passes.
- `show`: the gate report (tasks by wave, requirement coverage, new dependencies and copied code, model summary). Paste it unchanged.
- `next`: `Wave W` and its remaining tasks with model and effort, or `all tasks complete`.
- `checkpoint`: `W` is the wave from `next`. `REF` is the integration branch head recorded before the wave started. The SDD workspace is the directory printed by SDD's `scripts/sdd-workspace PLAN_FILE`. Run it from the repository root on the integration branch. It warns about changed files outside the wave's `files`, runs the wave's `verify` commands and the ledger's `checks` with output to `.tech-lead/scratch/checkpoint-W.log`, prints `Task N: pass` or `Task N: fail (exit X)`, and exits 1 on any failure. With `--mark` and everything passing it adds the wave's tasks to `done` and appends the wave entry, rulings and `Attempt:` lines to `journal.md`. Every file it writes is printed as `Wrote <absolute path>`.
- `status.py`: full status on stdout; `--write` regenerates `docs/STATUS.md`; `--brief` is the session-start text. `ROOT` defaults to the project directory.
