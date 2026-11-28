# status-report

Owner status report for long, autonomous Claude Code sessions. Sent periodically (every few hours) and after each release or closed stage.

Five sections: ✅ released since the last report · 🔄 in progress with % · ⏭️ next · milestones with % · ⚠️ waiting on the owner.

After the report, the decisions waiting on the owner are asked with the AskUserQuestion dialog (recommended option first); answers are recorded with their date.

## Project config

`.claude/status-report.json` in the project root (all fields optional):

```json
{
  "language": "pl",
  "interval_hours": 3,
  "tag_pattern": "atlas-v*",
  "milestones": [
    {"label": "M1", "issue": 449},
    {"label": "M2", "issue": 450}
  ],
  "paused_labels": ["odłożone"],
  "in_progress_labels": ["in-progress"],
  "owner_labels": ["question"]
}
```

- `tag_pattern`: release tags; those newer than the last report go to section 1.
- `milestones`: issues whose `- [ ]` / `- [x]` checklist gives the %. A closed issue is 100% when its checklist is complete.
- `paused_labels`: a milestone carrying one of these shows as paused.
- `in_progress_labels`, `owner_labels`: open issues listed in sections 2 and 5.

## Script

`skills/status-report/scripts/facts.py --root <project>` prints the facts as JSON (needs `git` and an authenticated `gh`).
`--mark` saves now as the time of the last report, which is the default `--since` for the next run.
