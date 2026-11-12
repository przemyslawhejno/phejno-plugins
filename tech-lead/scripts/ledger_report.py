"""Ledger report: markdown shown to the user at the approval gate."""
from __future__ import annotations

from ledger_core import MODELS, waves


def _esc(x) -> str:
    return str(x).replace("|", "\\|").replace("\n", " ")


def _cell(x) -> str:
    if isinstance(x, (list, tuple)):
        return "<br>".join(_esc(i) for i in x) or "-"
    return _esc(x)


def _model(t: dict) -> str:
    if t["model"] == "lead":
        return "lead"
    kind = t.get("kind", "code")
    suffix = f" ({kind})" if kind in ("hygiene", "ui") else ""
    return f"{t['model']}/{t.get('effort', '')}{suffix}"


def render_show(ledger: dict) -> str:
    tasks = sorted(ledger.get("tasks", []), key=lambda t: t["id"])
    wave_of = waves(tasks)
    out: list = []

    for w in sorted(set(wave_of.values())):
        out.append(f"## Wave {w}")
        out.append("")
        out.append("| Task | Title | Depends on | Files | Model | Risk | Experts | Reason | Acceptance |")
        out.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for t in tasks:
            if wave_of[t["id"]] != w:
                continue
            row = [t["id"], t["title"], t["depends_on"], t["files"], _model(t),
                   t.get("risk", []), t.get("experts", []), t["reason"], t["acceptance"]]
            out.append("| " + " | ".join(_cell(c) for c in row) + " |")
        out.append("")

    out.append("## Requirement coverage")
    out.append("")
    out.append("| Requirement | Text | Tasks |")
    out.append("| --- | --- | --- |")
    for r in ledger.get("requirements", []):
        ids = [str(t["id"]) for t in tasks if r["id"] in t.get("covers", [])]
        out.append(f"| {_cell(r['id'])} | {_cell(r.get('text', ''))} | {', '.join(ids)} |")
    out.append("")

    out.append("## New dependencies and copied code")
    out.append("")
    lines = [f"- Task {t['id']}: {t['reuse']['source']} ({t['reuse']['mode']}, {t['reuse']['license']})"
             for t in tasks
             if isinstance(t.get("reuse"), dict) and t["reuse"].get("mode") in ("dependency", "copy")]
    out.extend(lines or ["None."])
    out.append("")

    out.append("## Summary")
    out.append("")
    counts = {m: sum(1 for t in tasks if t["model"] == m) for m in MODELS}
    for m in MODELS:
        if counts[m]:
            out.append(f"- {m}: {counts[m]}")
    n = len(tasks)
    k = counts["opus"] + counts["fable"]
    pct = int(round(100 * k / n + 1e-9)) if n else 0
    out.append("")
    if any(t.get("experts") for t in tasks):
        per_wave = [len({lens for t in tasks if wave_of[t["id"]] == w
                         for lens in t.get("experts", [])})
                    for w in sorted(set(wave_of.values()))]
        parts = ", ".join(f"wave {i}: {c}" for i, c in enumerate(per_wave, 1))
        out.append(f"Lens dispatches: {parts} (total {sum(per_wave)})")
    else:
        out.append("Lens dispatches: none")
    out.append("")
    out.append(f"Opus and fable share: {pct}% ({k} of {n} tasks)")
    out.append("")
    out.append(f"Prior art: {ledger.get('prior_art', '')}")
    return "\n".join(out) + "\n"
