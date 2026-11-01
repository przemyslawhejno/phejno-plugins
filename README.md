# phejno-plugins

Personal Claude Code plugin marketplace.

## Installation

```bash
claude plugins marketplace add przemyslawhejno/phejno-plugins
```

## Available Plugins

### claude-codemap

Generates and maintains a codemap in `.claude/codemap/` for fast file lookup and symbol navigation, reducing token usage and speeding up navigation.

```bash
claude plugins install claude-codemap@phejno-plugins
```

### statusline

Custom status line: model/effort, context usage, prompt cache hit rate, 5h/7d rate-limit usage, session/daily/monthly cost tracking, git branch, and cwd.

```bash
claude plugins install statusline@phejno-plugins
```

After installing, run `/statusline:setup-statusline` to wire it into `~/.claude/settings.json`, then restart Claude Code. Requires `jq` and `git` on PATH.

### model-manager

Per-task model and effort policy for subagents: Opus coordinates, Sonnet implements, Haiku does mechanical work. Enforces explicit dispatch choices, routes named agents such as reviewers and Explore, and reports cost by model.

```bash
claude plugins install model-manager@phejno-plugins
```
