from __future__ import annotations

import os
import sys

SCRIPTS = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
)
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)


def make_task(id, **overrides):
    task = {
        "id": id,
        "title": f"Task {id}",
        "depends_on": [],
        "files": [f"src/t{id}.py"],
        "acceptance": ["works"],
        "model": "sonnet",
        "effort": "low",
        "reason": "r",
        "verify": ["true"],
    }
    task.update(overrides)
    return task


def make_ledger(tasks, **overrides):
    tasks = list(tasks)
    if tasks and isinstance(tasks[0], dict) and "covers" not in tasks[0]:
        tasks[0] = dict(tasks[0], covers=["R1"])
    ledger = {
        "prior_art": "done",
        "checks": [],
        "done": [],
        "requirements": [{"id": "R1", "text": "r"}],
        "tasks": tasks,
    }
    ledger.update(overrides)
    return ledger
