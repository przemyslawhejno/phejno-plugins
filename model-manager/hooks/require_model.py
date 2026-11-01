#!/usr/bin/env python3
"""PreToolUse hook on Agent: route named agents, deny generic dispatches without a choice.

Named agents listed in agents.json get that model and effort through updatedInput,
but only when the call passes neither: an explicit choice on the call wins whole.
The user file ~/.claude/model-manager/agents.json is merged over the defaults; a
null entry there removes a default. Generic dispatches without model and effort
are denied with the table. Forks and unlisted named agents pass untouched.

Only subagents are routed. Skills run in the main session, whose model and effort
belong to the user, so this plugin never sets them.

Any failure here allows the call unchanged: a bug in this hook must never stop work.
MODEL_MANAGER_ENFORCE=0 turns the whole hook off.
"""
import json
import os
import sys
from pathlib import Path

GENERIC = {"", "general-purpose", "claude"}
DEFAULTS = Path(__file__).with_name("agents.json")
USER_TABLE = Path.home() / ".claude" / "model-manager" / "agents.json"
REASON = (
    "model-manager: pass {missing} on this Agent call. haiku low = search, logs; "
    "haiku medium = edit with full code in the plan; sonnet low = precise spec, 1-2 files; "
    "sonnet medium = integration, debugging, per-task review; opus medium = final branch review."
)


def load_table():
    table = json.loads(DEFAULTS.read_text(encoding="utf-8"))
    try:
        table.update(json.loads(USER_TABLE.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        pass
    return {name: row for name, row in table.items() if isinstance(row, dict)}


def decide(tool_input, table):
    """Return the hookSpecificOutput for this call, or None to let it pass."""
    kind = tool_input.get("subagent_type", "") or ""
    if kind in GENERIC:
        missing = [key for key in ("model", "effort") if not tool_input.get(key)]
        if not missing:
            return None
        return {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                "permissionDecisionReason": REASON.format(missing=" and ".join(missing))}
    row = table.get(kind)
    if not row or tool_input.get("model") or tool_input.get("effort"):
        return None
    updated = dict(tool_input)
    for key in ("model", "effort"):
        if row.get(key):
            updated[key] = row[key]
    if updated == tool_input:
        return None
    # No permissionDecision: the input is rewritten, but permission rules still decide.
    return {"hookEventName": "PreToolUse", "updatedInput": updated}


def main():
    if os.environ.get("MODEL_MANAGER_ENFORCE") == "0":
        return
    tool_input = json.load(sys.stdin).get("tool_input") or {}
    output = decide(tool_input, load_table())
    if output:
        print(json.dumps({"hookSpecificOutput": output}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
