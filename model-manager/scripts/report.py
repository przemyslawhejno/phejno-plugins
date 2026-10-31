#!/usr/bin/env python3
"""Report token use and estimated API-equivalent cost per model from transcripts.

Usage: report.py [--days N] [--project SUBSTRING]
Prices are USD per MTok: input, 5m write, 1h write, cache read, output.
"""
import argparse
import glob
import json
import os
import time
from collections import defaultdict
from datetime import datetime

PRICES = {
    "opus": (4, 5, 8, 0.20, 20),
    "sonnet": (2, 2.5, 4, 0.10, 10),
    "haiku": (0.10, 0.125, 0.20, 0.01, 0.50),
    "fable": (4, 5, 8, 0.20, 20),
}
GAP_SECONDS = 300


def family(model):
    return next((name for name in PRICES if name in (model or "")), None)


def scan(path, totals, gaps):
    role = "subagent" if "/subagents/" in path else "main"
    seen, previous = set(), None
    agent_models = set()
    for line in open(path, errors="ignore"):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        message = entry.get("message") or {}
        if entry.get("type") != "assistant" or message.get("id") in seen:
            continue
        seen.add(message.get("id"))
        name = family(message.get("model"))
        if not name:
            continue
        agent_models.add(name)
        usage = message.get("usage") or {}
        split = usage.get("cache_creation") or {}
        write_1h = split.get("ephemeral_1h_input_tokens", 0) or 0
        write_total = usage.get("cache_creation_input_tokens", 0) or 0
        row = totals[(name, role)]
        row["msgs"] += 1
        row["input"] += usage.get("input_tokens", 0) or 0
        row["write_5m"] += write_total - write_1h
        row["write_1h"] += write_1h
        row["read"] += usage.get("cache_read_input_tokens", 0) or 0
        row["output"] += usage.get("output_tokens", 0) or 0
        stamp = entry.get("timestamp")
        now = datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp() if stamp else None
        if role == "subagent" and now and previous and now - previous > GAP_SECONDS:
            gaps["count"] += 1
            gaps["tokens"] += write_total
        previous = now or previous
    if role == "subagent":
        for name in agent_models:
            totals[(name, role)]["agents"] += 1


def cost(name, row):
    p = PRICES[name]
    return (row["input"] * p[0] + row["write_5m"] * p[1] + row["write_1h"] * p[2]
            + row["read"] * p[3] + row["output"] * p[4]) / 1e6


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=float, default=14)
    parser.add_argument("--project", default="")
    args = parser.parse_args()
    cutoff = time.time() - args.days * 86400
    pattern = os.path.expanduser("~/.claude/projects/*/**/*.jsonl")
    totals, gaps = defaultdict(lambda: defaultdict(int)), defaultdict(int)
    for path in glob.iglob(pattern, recursive=True):
        if args.project in path and os.path.getmtime(path) > cutoff:
            scan(path, totals, gaps)
    all_cost = sum(cost(name, row) for (name, _), row in totals.items()) or 1
    print(f"{'model':8}{'role':10}{'agents':>7}{'msgs':>8}{'write M':>9}{'read M':>9}{'out M':>7}{'USD':>9}{'share':>7}")
    for (name, role), row in sorted(totals.items(), key=lambda kv: -cost(kv[0][0], kv[1])):
        usd = cost(name, row)
        write = (row["write_5m"] + row["write_1h"]) / 1e6
        print(f"{name:8}{role:10}{row['agents']:>7}{row['msgs']:>8}{write:>9.1f}{row['read'] / 1e6:>9.1f}"
              f"{row['output'] / 1e6:>7.2f}{usd:>9.2f}{usd / all_cost:>7.0%}")
    print(f"\ntotal about {all_cost:.0f} USD API-equivalent at current prices (Haiku below 100k prompts)")
    print(f"subagent cache rewrites after a gap over 5 min: {gaps['count']}, {gaps['tokens'] / 1e6:.1f}M tokens")


main()
