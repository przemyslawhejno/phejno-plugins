# model-manager

Keeps delegated work on the cheapest capable model. It complements `superpowers`.

- A SessionStart hook injects the dispatch table into each new session.
- A PreToolUse hook denies a generic `Agent` call that lacks `model` and `effort`; the denial explains the table, so the agent retries.
- The same hook routes named agents (Explore, reviewers, validators) through `updatedInput`, using `hooks/agents.json`, when the call passes neither `model` nor `effort`. Forks and unlisted agents pass. `MODEL_MANAGER_ENFORCE=0` turns the whole hook off.
- The `model-manager` skill covers classification, escalation, lanes and long jobs.
- `/model-manager:mm-report` shows estimated cost by model.

Requires Claude Code 2.1.292+ (the `effort` parameter on `Agent`) and `python3`.

## Named agents

`hooks/agents.json` maps agent names to a model and an effort. To change an entry or add one, put a file at `~/.claude/model-manager/agents.json` with the same shape. Its entries replace the defaults, and `null` removes one:

```json
{ "pr-review-toolkit:code-reviewer": { "model": "opus", "effort": "high" }, "Explore": null }
```

The table replaces patching agent frontmatter in `~/.claude/plugins/cache`, which every plugin update overwrites. A model on the `Agent` call beats frontmatter, so the routing survives updates. Without it, an agent with `model: inherit` runs on the main session's model, and `CLAUDE_CODE_SUBAGENT_MODEL` does not apply to it.

A routed call returns only `updatedInput`, without a permission decision, so your permission rules for `Agent` still apply.

## Main session stays yours

The plugin routes only subagents. It never sets a model or effort on skills, because skills run in the main session and skill frontmatter overrides `/effort` for the rest of the turn. To set a default effort per model, use `modelSettings` in `~/.claude/settings.json`. A plugin cannot set it. Opus 5.5 and later read effort only from there, not from the top-level `effortLevel`:

```json
{ "modelSettings": { "claude-opus-5-5": { "effortLevel": "medium" } } }
```

## Optional: one-hour cache for subagents

Subagents default to a five-minute cache, so a pause rewrites their whole context. When they often wait, add this to `~/.claude/settings.json`:

```json
{ "subagentPromptCacheTtl": "1h" }
```

Writes cost 60% more, so compare `/model-manager:mm-report` before and after.

## Limits

- `Workflow` agents do not pass through the Agent hook.
- A running session needs `/reload-plugins` for the hook and a manual note for the policy, because SessionStart has already fired.
- Costs are API-equivalent estimates, and the Haiku price assumes prompts under 100k tokens.

## What came from other projects

| Project | Adopted | Left out |
|---|---|---|
| `obra/superpowers` | turn count beats token price, batching, explicit model | |
| `Yeachan-Heo/oh-my-claudecode` | failures and risk raise the tier, an explicit choice wins | keyword scoring, full orchestration layer |
| `modu-ai/moai-adk` | role table of model plus effort, effort by task class | the whole harness |
| `NeoLabHQ/context-engineering-kit` | decision-table shape only (GPL-3.0, no text copied) | Opus as the default, mandatory self-critique |
| `gargpratyush/jev-router` | | sends routing through an external API key |

## Ongoing measurement

`scripts/report.py --since YYYY-MM-DD --json` adds dispatches by model and effort, named agents and hook denials. `scripts/review.sh` asks a short Sonnet run for conclusions from JSON snapshots in `~/.claude/model-manager/snapshots/` and writes them to `reviews/`. To schedule both, run `bash scripts/install-timers.sh` yourself; the file header shows how to remove them.
