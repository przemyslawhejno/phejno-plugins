---
description: Configure Claude Code's status line to use this plugin's script
allowed-tools: ["Read", "Edit", "Bash"]
---

Configure the user's status line to point at this plugin's script.

1. **Check dependencies first**, before touching any config:
   - Run `command -v jq`. This is a hard requirement — the script parses the
     stdin JSON with `jq` and prints nothing useful without it.
   - Run `command -v git` (soft requirement — only disables the branch
     segment if missing).
   - If `jq` is missing, **stop here**. Do not edit `settings.json`. Tell the
     user `jq` is required and not on PATH, give the install command for
     their platform (`sudo apt install jq` / `brew install jq` /
     `sudo snap install jq` / `sudo dnf install jq`), and ask them to
     install it and re-run this command.
   - If `git` is missing, warn that the git-branch segment will stay blank
     but continue with setup.
2. Determine `${CLAUDE_PLUGIN_ROOT}` (the absolute path of this plugin's installed directory) and confirm `${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh` exists and is executable.
3. Read `~/.claude/settings.json` (create it with `{}` if it doesn't exist).
4. Set (or overwrite) the top-level `statusLine` key to:
   ```json
   "statusLine": {
     "type": "command",
     "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh"
   }
   ```
   Substitute `${CLAUDE_PLUGIN_ROOT}` with its actual resolved absolute path (settings.json commands are not expanded at runtime the way plugin components are, so write the literal path).
5. Preserve every other existing key in `settings.json` — only add/replace `statusLine`.
6. Tell the user the status line is now configured and that they need to restart Claude Code (or start a new session) for it to take effect.
