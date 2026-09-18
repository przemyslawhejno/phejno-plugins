---
description: Configure Claude Code's status line to use this plugin's script
allowed-tools: ["Read", "Edit", "Bash"]
---

Configure the user's status line to point at this plugin's script.

1. Determine `${CLAUDE_PLUGIN_ROOT}` (the absolute path of this plugin's installed directory) and confirm `${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh` exists and is executable.
2. Read `~/.claude/settings.json` (create it with `{}` if it doesn't exist).
3. Set (or overwrite) the top-level `statusLine` key to:
   ```json
   "statusLine": {
     "type": "command",
     "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh"
   }
   ```
   Substitute `${CLAUDE_PLUGIN_ROOT}` with its actual resolved absolute path (settings.json commands are not expanded at runtime the way plugin components are, so write the literal path).
4. Preserve every other existing key in `settings.json` — only add/replace `statusLine`.
5. Tell the user the status line is now configured and that they need to restart Claude Code (or start a new session) for it to take effect.

Requires `jq` on PATH to render the status line (rate limits, cache %, cost tracking, git branch). If `jq` is missing, tell the user to install it.
