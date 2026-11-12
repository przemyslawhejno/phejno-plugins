"""Ledger core: load, validate, wave computation and next-wave selection."""
from __future__ import annotations

import json
from typing import Optional

MODELS = ("haiku", "sonnet", "opus", "fable", "lead")
EFFORTS = ("low", "medium", "high", "xhigh", "max")
REUSE_MODES = ("dependency", "copy", "pattern")
MODES = ("gated", "autopilot")
KINDS = ("code", "ui", "hygiene")
RISKS = ("security", "data", "irreversible", "system-wide", "ux")
LENSES = ("security", "data", "api", "architecture", "performance", "errors", "tests", "ui-ux")
RISK_LENSES = {
    "security": ("security",),
    "data": ("data",),
    "irreversible": ("data", "api", "architecture"),
    "system-wide": ("architecture",),
    "ux": ("ui-ux",),
}
MAX_EXPERTS = 4
CODEMAP_INLINE_MAX = 15
CODEMAP_UPDATE_MAX = 50

REQUIRED_FIELDS = ("id", "title", "depends_on", "files", "acceptance", "model", "reason")


class LedgerError(Exception):
    pass


def load(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise LedgerError(f"{path}: file not found")
    except json.JSONDecodeError as e:
        raise LedgerError(f"{path}: invalid JSON ({e})")
    except (OSError, UnicodeDecodeError) as e:
        raise LedgerError(f"{path}: cannot read ({e})")
    if not isinstance(data, dict):
        raise LedgerError(f"{path}: top level must be a JSON object")
    return data


def _valid_id(x: object) -> bool:
    return isinstance(x, int) and not isinstance(x, bool) and x > 0


def _is_list(x: object) -> bool:
    return isinstance(x, list)


def _normalised(p: object) -> bool:
    if not isinstance(p, str) or not p:
        return False
    if p.startswith("/") or p.startswith("./") or "\\" in p or "//" in p:
        return False
    return ".." not in p.split("/")


def paths_overlap(a: str, b: str) -> bool:
    if a == b:
        return True
    return (a.endswith("/") and b.startswith(a)) or (b.endswith("/") and a.startswith(b))


def _deps(task: dict) -> list:
    deps = task.get("depends_on")
    return deps if _is_list(deps) else []


def codemap_action(count: int) -> str:
    if count <= CODEMAP_INLINE_MAX:
        return "inline"
    return "update" if count <= CODEMAP_UPDATE_MAX else "rebuild"


def waves(tasks: list) -> dict:
    by_id = {t["id"]: t for t in tasks}
    result: dict[int, int] = {}

    def wave_of(i: int) -> int:
        if i in result:
            return result[i]
        deps = [d for d in _deps(by_id[i]) if d in by_id]
        result[i] = 1 + max((wave_of(d) for d in deps), default=0)
        return result[i]

    for i in sorted(by_id):
        wave_of(i)
    return result


def _find_cycle(deps_of: dict) -> Optional[list]:
    state: dict = {}
    for start in sorted(deps_of):
        if start in state:
            continue
        stack = [start]
        state[start] = 1
        iters = {start: iter(sorted(deps_of[start]))}
        while stack:
            node = stack[-1]
            nxt = next(iters[node], None)
            if nxt is None:
                state[node] = 2
                stack.pop()
                continue
            if state.get(nxt) == 1:
                path = stack[stack.index(nxt):] + [nxt]
                path = path[:-1]
                k = path.index(min(path))
                path = path[k:] + path[:k]
                return path + [path[0]]
            if nxt not in state:
                state[nxt] = 1
                stack.append(nxt)
                iters[nxt] = iter(sorted(deps_of[nxt]))
    return None


def validate(ledger: dict) -> list:
    errors: list = []
    if not isinstance(ledger, dict):
        return ["ledger is not an object"]

    if "prior_art" not in ledger:
        errors.append("missing field 'prior_art'")
    if "mode" in ledger and ledger["mode"] not in MODES:
        errors.append(f"invalid mode '{ledger['mode']}'")

    schema = ledger.get("schema")
    schema_is_two = type(schema) is int and schema == 2
    if "schema" in ledger and not schema_is_two:
        errors.append(f"invalid schema '{schema}'")

    tasks = ledger.get("tasks")
    if not _is_list(tasks):
        errors.append("tasks must be a list")
        tasks = []
    requirements = ledger.get("requirements", [])
    if not _is_list(requirements):
        errors.append("requirements must be a list")
        requirements = []
    done = ledger.get("done", [])
    if not _is_list(done):
        errors.append("done must be a list")
        done = []
    if not _is_list(ledger.get("checks", [])):
        errors.append("checks must be a list")

    req_ids: list = []
    for r in requirements:
        if not isinstance(r, dict):
            errors.append(f"requirement {r!r}: requirement must be an object")
            continue
        if not isinstance(r.get("id"), str) or not r["id"]:
            errors.append(f"requirement {r.get('id')!r}: id must be a non-empty string")
            continue
        if r["id"] in req_ids:
            errors.append(f"duplicate requirement id {r['id']}")
        else:
            req_ids.append(r["id"])

    ids: list = []
    ids_ok = True
    for t in tasks:
        if not isinstance(t, dict):
            errors.append(f"task {t!r}: task must be an object")
            ids_ok = False
            continue
        i = t.get("id")
        if "id" not in t:
            errors.append(f"task {i!r}: missing field 'id'")
            ids_ok = False
        elif not _valid_id(i):
            errors.append(f"task {i!r}: id must be a positive integer")
            ids_ok = False
        elif i in ids:
            errors.append(f"duplicate task id {i}")
            ids_ok = False
        else:
            ids.append(i)

    graph_ok = ids_ok
    covered: set = set()
    for t in tasks:
        if not isinstance(t, dict) or not _valid_id(t.get("id")):
            continue
        n = t["id"]
        for f in REQUIRED_FIELDS:
            if f != "id" and f not in t:
                errors.append(f"task {n}: missing field '{f}'")
        lead = t.get("model") == "lead"
        if not lead:
            for f in ("effort", "verify"):
                if f not in t:
                    errors.append(f"task {n}: missing field '{f}'")

        if "model" in t and t["model"] not in MODELS:
            errors.append(f"task {n}: invalid model '{t['model']}'")
        if "effort" in t and t["effort"] not in EFFORTS:
            errors.append(f"task {n}: invalid effort '{t['effort']}'")

        reuse = t.get("reuse")
        if reuse is not None:
            if not isinstance(reuse, dict):
                errors.append(f"task {n}: reuse must be an object")
            else:
                if reuse.get("mode") not in REUSE_MODES:
                    errors.append(f"task {n}: invalid reuse.mode '{reuse.get('mode')}'")
                if not reuse.get("source") or not reuse.get("license"):
                    errors.append(f"task {n}: reuse needs source and license")

        if "acceptance" in t:
            acc = t["acceptance"]
            if not _is_list(acc):
                errors.append(f"task {n}: acceptance must be a list")
            elif not acc:
                errors.append(f"task {n}: acceptance is empty")

        if "depends_on" in t:
            deps = t["depends_on"]
            if not _is_list(deps):
                errors.append(f"task {n}: depends_on must be a list")
                graph_ok = False
            else:
                for d in deps:
                    if not (_valid_id(d) and d in ids):
                        errors.append(f"task {n}: depends on unknown task {d}")
                        graph_ok = False

        covers = t.get("covers", [])
        if not _is_list(covers):
            errors.append(f"task {n}: covers must be a list")
        else:
            for c in covers:
                if c in req_ids:
                    covered.add(c)
                else:
                    errors.append(f"task {n}: covers unknown requirement {c}")

        if "files" in t:
            files = t["files"]
            if not _is_list(files):
                errors.append(f"task {n}: files must be a list")
            elif lead and files:
                errors.append(f"task {n}: lead tasks edit no files")
            elif not lead and not files:
                errors.append(f"task {n}: files is empty")
            if _is_list(files):
                for p in files:
                    if not _normalised(p):
                        errors.append(f"task {n}: path '{p}' is not normalised")

        if not lead and "verify" in t:
            verify = t["verify"]
            if not _is_list(verify):
                errors.append(f"task {n}: verify must be a list")
            elif not verify:
                nv = t.get("no_verify")
                if not (isinstance(nv, str) and nv.strip()):
                    errors.append(f"task {n}: verify is empty and no_verify gives no reason")

    if schema_is_two:
        errors.extend(_schema2_errors(ledger, tasks))

    for x in done:
        if not (_valid_id(x) and x in ids):
            errors.append(f"done: unknown task id {x}")

    for r in req_ids:
        if r not in covered:
            errors.append(f"requirement {r} is covered by no task")

    if graph_ok:
        valid_tasks = [t for t in tasks if isinstance(t, dict)]
        deps_of = {t["id"]: list(t["depends_on"]) for t in valid_tasks
                   if _is_list(t.get("depends_on"))}
        if len(deps_of) == len(valid_tasks):
            cycle = _find_cycle(deps_of)
            if cycle:
                errors.append("dependency cycle: " + " -> ".join(str(c) for c in cycle))
            else:
                errors.extend(_conflicts(valid_tasks))
    return errors


def _string_list(x) -> bool:
    return _is_list(x) and all(isinstance(v, str) for v in x)


def _field_errors(n: int, t: dict, lead: bool, kind: object) -> tuple[list, list, list, list]:
    errors: list = []
    if not lead and kind not in KINDS:
        errors.append(f"task {n}: invalid kind '{kind}'")
    lists: dict = {}
    for f in ("risk", "experts", "replaces"):
        value = t.get(f, [])
        if _string_list(value):
            lists[f] = value
        else:
            lists[f] = []
            errors.append(f"task {n}: {f} must be a list of strings")
    risks, lenses = lists["risk"], lists["experts"]
    known_risks: list = []
    for r in risks:
        if r in RISKS:
            known_risks.append(r)
        else:
            errors.append(f"task {n}: invalid risk '{r}'")
    for lens in lenses:
        if lens not in LENSES:
            errors.append(f"task {n}: unknown lens '{lens}'")
    if len(lenses) > MAX_EXPERTS:
        errors.append(f"task {n}: more than {MAX_EXPERTS} experts")
    return errors, risks, known_risks, lenses


def _risk_lens_errors(
    n: int, t: dict, lead: bool, kind: object, risks: list, known_risks: list, lenses: list,
    ui_enabled: bool,
) -> list:
    errors: list = []
    if lead:
        if lenses:
            errors.append(f"task {n}: lead tasks take no experts")
        return errors

    model = t.get("model")
    if kind == "ui":
        if not ui_enabled:
            errors.append(f"task {n}: kind 'ui' needs top-level ui: true")
        if model != "haiku" and "ux" not in risks:
            errors.append(f"task {n}: ui task not on haiku needs risk 'ux'")
    if model == "haiku" and risks:
        for r in risks:
            errors.append(f"task {n}: haiku task cannot carry risk '{r}'")
        return errors
    if lenses and (model == "haiku" or (model == "sonnet" and t.get("effort") == "low" and not risks)):
        errors.append(f"task {n}: routine task takes no experts")
    for r in known_risks:
        wanted = RISK_LENSES[r]
        if r == "system-wide" and kind == "ui":
            wanted = wanted + ("ui-ux",)
        if not any(lens in wanted for lens in lenses):
            errors.append(f"task {n}: risk '{r}' needs one of the lenses {', '.join(wanted)}")
    return errors


def _hygiene_errors(code_tasks: list, hygiene_tasks: list) -> list:
    errors: list = []
    if not hygiene_tasks and (
        len(code_tasks) >= 3 or (len(code_tasks) >= 2 and _any_replaces(code_tasks))
    ):
        errors.append("missing hygiene task")
    for h in hygiene_tasks:
        deps = _deps(h)
        for m in sorted(c["id"] for c in code_tasks):
            if m not in deps:
                errors.append(f"task {h['id']}: hygiene task must depend on task {m}")
    return errors


def _schema2_errors(ledger: dict, tasks: list) -> list:
    errors: list = []
    if "ui" in ledger and not isinstance(ledger["ui"], bool):
        errors.append("ui must be a boolean")
    ui_enabled = ledger.get("ui") is True
    code_tasks: list = []
    hygiene_tasks: list = []
    for t in tasks:
        if not isinstance(t, dict) or not _valid_id(t.get("id")):
            continue
        n = t["id"]
        lead = t.get("model") == "lead"
        kind = t.get("kind", "code")
        if not lead and kind in KINDS:
            (hygiene_tasks if kind == "hygiene" else code_tasks).append(t)
        field_errors, risks, known_risks, lenses = _field_errors(n, t, lead, kind)
        errors.extend(field_errors)
        errors.extend(_risk_lens_errors(n, t, lead, kind, risks, known_risks, lenses, ui_enabled))
    errors.extend(_hygiene_errors(code_tasks, hygiene_tasks))
    return errors


def _any_replaces(tasks: list) -> bool:
    return any(_string_list(t.get("replaces")) and t["replaces"] for t in tasks)


def _conflicts(tasks: list) -> list:
    errors: list = []
    wave_of = waves(tasks)
    by_wave: dict = {}
    for t in sorted(tasks, key=lambda t: t["id"]):
        if _is_list(t.get("files")):
            by_wave.setdefault(wave_of[t["id"]], []).append(t)
    for w in sorted(by_wave):
        group = by_wave[w]
        for ai in range(len(group)):
            for bi in range(ai + 1, len(group)):
                a, b = group[ai], group[bi]
                shared = next(
                    (p for p in a["files"] for q in b["files"]
                     if isinstance(p, str) and isinstance(q, str) and paths_overlap(p, q)),
                    None,
                )
                if shared is not None:
                    errors.append(
                        f"wave {w}: tasks {a['id']} and {b['id']} share '{shared}'; "
                        "add a dependency between them"
                    )
    return errors


def next_wave(ledger: dict) -> Optional[tuple]:
    tasks = ledger.get("tasks", [])
    done = set(ledger.get("done", []))
    wave_of = waves(tasks)
    pending = [t for t in tasks if t["id"] not in done]
    if not pending:
        return None
    w = min(wave_of[t["id"]] for t in pending)
    return w, sorted((t for t in pending if wave_of[t["id"]] == w), key=lambda t: t["id"])
