#!/usr/bin/env python3
"""SessionStart hook: inject the dispatch policy into the main session."""
import json
from pathlib import Path

policy = (Path(__file__).parent / "policy.md").read_text(encoding="utf-8")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": policy}}))
