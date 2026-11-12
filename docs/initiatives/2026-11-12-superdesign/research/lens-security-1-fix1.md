# Lens re-review: security, wave 1, fix round 1

Scope: fix diff 00b84fc..f8e79ab (worktree HEAD confirmed f8e79ab). Paths are in `tech-lead/skills/tech-lead/` of the lane-1 worktree. Nothing run; the fix report claims the suite at 166 tests OK in 0.90 s, and the two new tests (`test_superdesign_consent_identity_and_withdrawal`, `test_superdesign_context_file_guard`) are in the diff.

### Finding Verdicts

- **1. Consent borrowed through git** — ADDRESSED. `SKILL.md:39` makes consent valid only with `consent: yes`, a passing `git check-ignore -q` and `user:` equal to `git config user.email`, else ask or (autopilot) the built-in builder. A tracked file fails `check-ignore` by default, so a committed file is no consent. `layout.md:82` adds `user:`, `layout.md:86` repeats the rule. `SKILL.md` Start of work step 4 adds `.tech-lead/` to `.gitignore` at every start, new or resumed. The `.superdesign/*` allowlist is added before the first generation (`SKILL.md` flow step 1) and, per `layout.md` .gitignore section, before the repository analysis or first CLI call.
- **2. Guard on files and images sent** — ADDRESSED. `SKILL.md` flow step (1) shows the planned generations and the exact `--context-file` and upload list and gets a yes (status note in autopilot), and bans `.env*`, `*.pem`, `*.key`, `*.p12`, `id_*`, `credentials*`, `secrets*`, git-ignored files and screenshots with real user data, plus secrets in `--user-request`. `layout.md` consent bullet repeats it. The init subagent copies no excluded file (`SKILL.md` step 4 init exception).
- **3. Retention not disclosed** — ADDRESSED. `layout.md` consent text: "Stored by superdesign: the request verbatim, to improve generation; drafts, uploaded assets and context stay on the user's superdesign account until deleted there."
- **Folded: withdrawal** — ADDRESSED (`SKILL.md:39`, `layout.md:86`: covers every initiative in this clone; `consent: no` or delete the file).
- **Folded: CLI version in journal** — ADDRESSED (`SKILL.md` flow step 6, `layout.md` journal template `CLI: <version from the preflight>`).
- **Folded: init brief forbids CLI and skill workflow** — ADDRESSED (brief carries the never-invoke line, reads INIT.md only, does not load the skill, never runs the CLI).
- **Folded: autopilot consented but unauthenticated → built-in** — ADDRESSED (`SKILL.md:40`).
- **Folded: `list-components` in step 5** — ADDRESSED (`SKILL.md` flow step 5; `mockup-prompt.md:27`).
- **Folded: export-mode wording** — ADDRESSED (`mockup-prompt.md:27`: replace with data URIs or plain CSS, drop and report what cannot be resolved).

### New Breakage in the Fix Diff

- Minor: `SKILL.md` flow step (1) orders "show the exact `--context-file` list and get a yes", then "load the skill and follow it". The skill chooses context files from the import tree, so the list shown precedes the skill's own selection, and later iterations may pass files that were not on the approved list. The never-select rule still blocks secrets. Suggest: load the skill first, then show the list, and show it again when a later call adds files.
- Minor: `SKILL.md:39` / `layout.md:86`: when `git config user.email` is unset, an empty `user:` matches an empty current value. Suggest treating an empty email as no match.
- Minor: "the CLI version the preflight reported" (`SKILL.md` flow step 6): the auth preflight is not stated to report a version; name the command (e.g. `npx --yes @superdesign/cli@latest --version`).

### Out-of-Scope Observations

- Earlier Minors 5 (CDN hosts and inline network calls in the standalone check), 7 (init subagent without Bash where the harness allows it) and 8 (canvas/preview links in the committed journal) are untouched; they remain for the final review.

### Verdict

**Fix round:** All findings addressed, no new Critical/Important breakage.
