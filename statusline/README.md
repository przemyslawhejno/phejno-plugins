# statusline

Custom Claude Code status line: model + effort, context usage %, prompt cache
hit rate, 5h/7d rate-limit usage with reset countdown, session/daily/monthly
cost tracking, git branch (with dirty marker), and cwd.

## Setup

After installing this plugin, run:

```
/statusline:setup-statusline
```

This writes the `statusLine` entry into `~/.claude/settings.json` pointing at
the script bundled with this plugin. Restart Claude Code afterward.

Requires `jq` and `git` on PATH.
