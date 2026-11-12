# Re-review: final superdesign fixes (e541934..26ac918)

### Finding Verdicts

1. **Autopilot superdesign has no draft pick or design approval.** ADDRESSED. SKILL.md:37 now says that in autopilot with no user present at step 4 the built-in builder always runs, whatever consent is recorded. The old "autopilot from an existing spec without valid consent" clause (SKILL.md:39), the old "in autopilot an unauthenticated CLI" clause (:40) and the old "status note in autopilot" in flow (1) (:44) are removed. layout.md:86 and README.md:57 say the same thing. The tests assert that "recorded before the start" is absent from both SKILL.md and README.md.
2. **The main session could load superdesign outside the gated flow.** ADDRESSED. SKILL.md:42 now says: "Load `superdesign:superdesign` only here, after the checks pass; if it starts on its own earlier (it can trigger on design talk), stop it and return to these checks." In the superdesign source, files first leave the machine at uploads and at generation calls with `--context-file`. That comes after Step 0 (preflight) and Step 1 (local init), so a stop at detection comes before any upload.
3. **The file list was approved before the skill chose the files, with no re-approval for additions.** ADDRESSED. In SKILL.md:44 (1) the order is now: load the skill, run the repository analysis, then show the generations, the exact `--context-file` list, the uploads (images, fonts, logos) and the component templates, get a yes, and only then follow the skill. Files or assets added later are shown and approved again. layout.md:90 matches.
4. **An empty `user.email` counted as a match.** ADDRESSED. SKILL.md:39 says "an empty or unset email never matches: ask every time and store no consent". layout.md:86 says the same.
5. **No command was named for recording the CLI version.** ADDRESSED. SKILL.md:44 (6) names `npm view @superdesign/cli version` and notes that the preflight prints no version. The layout.md:140 journal template uses the same command.
6. **The allowlist timing differed between documents.** ADDRESSED. SKILL.md:40 adds `.superdesign/*` and `.tech-lead/` to `.gitignore` before the first CLI call, the preflight. layout.md:210 says "before the first superdesign CLI call (the auth preflight included)". The allowlist therefore exists before the init subagent writes `.superdesign/init/`.
7. **The README was thinner than the skill.** ADDRESSED. README.md:56-57 covers the stored "no", withdrawal, verbatim request retention, drafts kept on the account, the `.superdesign/*` allowlist (keeping `design-system.md`) plus `.tech-lead/`, and the autopilot rule. test_packaging.py asserts each of these.
- **Extra change: `consent: no` with a matching user is not asked again; any other file counts as no consent.** CORRECT, and it fails closed. SKILL.md:39 and layout.md:86 agree. Under either reading of "counts as no consent" (ask again, or treat as a refusal), superdesign does not run without a valid `consent: yes`.

Check run: `python3 -m unittest tech-lead.tests.test_skill_docs tech-lead.tests.test_packaging` passed 23 tests, OK. The fix report claims 167 tests OK but shows no output.

### New Breakage in the Fix Diff

No Critical or Important issues.

- Minor: SKILL.md:44 (1) says "get a yes before the first generation". The superdesign skill uploads assets and creates the project before generating. The sentence order already puts the yes before "Then follow the skill", but "before the first upload or generation" would remove any doubt.
- Minor: "No user present" (SKILL.md:37) is not defined for `--auto` runs where the user is still in the session. The behaviour is safe either way: either the built-in builder runs, or the user is asked.
- Minor: `npm view @superdesign/cli version` reports the current registry `latest`. A cached `npx` run may use a different version. This was accepted by the review.

### Out-of-Scope Observations

The backlog items in the final review still stand, unchanged: the init subagent keeps Bash, the standalone-check hosts are loose, canvas and preview links go into the committed journal, and the CLI version is not pinned per run.

### Code or secrets leaving the machine without an informed yes

No remaining path found in the documents.
- The CLI runs only after a valid consent (`consent: yes`, the file git-ignored, a non-empty matching email) and after the allowlist is in place.
- Context files, uploads and templates go out only after the lead shows the exact list and gets the current user's yes, and additions are approved again.
- Autopilot with no user present never uses superdesign.
- Subagents never invoke the skill or the CLI.
- If the skill starts on its own before step 4, the lead stops it.

One residual is behavioural, not textual: the self-trigger guard relies on the lead noticing that the skill has started. The superdesign skill's first steps (preflight, local init) send no project files, so this is acceptable.

### Verdict

**Fix round:** All findings addressed, no new Critical/Important breakage.
