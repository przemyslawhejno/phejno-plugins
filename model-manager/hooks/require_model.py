#!/usr/bin/env python3
"""PreToolUse hook on Agent: deny a generic dispatch without model and effort.

Forks run on the parent's model and named agents carry their own frontmatter,
so only generic dispatches are checked. Any failure here allows the call: a bug
in this hook must never stop work. MODEL_MANAGER_ENFORCE=0 turns the check off.
"""
import json
import os
import sys

GENERIC = {"", "general-purpose", "claude"}
REASON = (
    "model-manager: pass {missing} on this Agent call. haiku low = search, logs; "
    "haiku medium = edit with full code in the plan; sonnet low = precise spec, 1-2 files; "
    "sonnet medium = integration, debugging, per-task review; opus medium = final branch review."
)


def main():
    if os.environ.get("MODEL_MANAGER_ENFORCE") == "0":
        return
    tool_input = json.load(sys.stdin).get("tool_input") or {}
    if tool_input.get("subagent_type", "") not in GENERIC:
        return
    missing = [key for key in ("model", "effort") if not tool_input.get(key)]
    if missing:
        decision = {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": REASON.format(missing=" and ".join(missing)),
        }
        print(json.dumps({"hookSpecificOutput": decision}))


try:
    main()
except Exception:
    pass
