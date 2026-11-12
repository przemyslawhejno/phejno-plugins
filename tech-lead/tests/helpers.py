from __future__ import annotations

import atexit
import os
import shutil
import subprocess
import sys
import tempfile

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


def make_hygiene(id, depends_on):
    return make_task(id, kind="hygiene", depends_on=depends_on, files=["src/", "tests/"])


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


def clean_env():
    return {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}


def git(repo, *args, env=None):
    return subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True,
                          text=True, env=env or clean_env()).stdout.strip()


def init_repo(repo):
    os.makedirs(repo, exist_ok=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    git(repo, "config", "commit.gpgsign", "false")


_template = []


def make_repo(dest):
    """Copy a one-commit repository (README) into dest; built once per process."""
    if not _template:
        root = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, root, True)
        init_repo(root)
        with open(os.path.join(root, "README"), "w") as f:
            f.write("x\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "init")
        _template.append(root)
    shutil.copytree(_template[0], dest, dirs_exist_ok=True)
