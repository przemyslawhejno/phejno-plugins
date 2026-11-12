# Final whole-branch review: tech-lead 0.3.0 (superdesign, B16)

Range: 06a9eb3..ee21cf8 (17 commits). Reviewer: final whole-branch review, read-only, one pass by document and one by script.
Read in full: SKILL.md, mockup-prompt.md, README.md, the superdesign and .gitignore parts of layout.md, spec, progress.md, the lens reports, the task 1-3 reviews, and the script and test diffs. Claims were checked against the superdesign source at f9f05cd (SKILL.md, references/SUPERDESIGN.md, RESUME.md, README.md, INSTALL.md).
Suite: `python3 -m unittest discover tech-lead/tests`: 166 tests, OK, 0.915 s (ratchet 1.12 s).

## Strengths

- One story across the four documents for the main line. The conditions are checked in order: skill, then consent, then the authenticated preflight (SKILL.md:37-40). Consent is checked before the first `npx` run, so the CLI never runs without a recorded yes. Consent is bound to the clone and the user (git-ignored, `check-ignore`, `user.email`), with withdrawal and retention stated (layout.md:76-92). The lead-only rule and the narrow init exception are stated (SKILL.md:42), and the never-invoke line is in all six `*-prompt.md` files, the implementer rule (SKILL.md:58) and the Paths rule (SKILL.md:178), all under test.
- The built-in path is unchanged for users without superdesign. The only changes to it are wording, the `.tech-lead/` ignore entry at every start (SKILL.md:28), which is harmless and better, and the never-invoke line.
- The claims checked against the source hold: the bare `npx --yes @superdesign/cli@latest` is the preflight and prints an `auth:` line; `get-design --output`, `import-design-draft --into` (no credits), `iterate-design-draft`, `list-components`, the `--user-request` retention text, the public asset URLs and the `/plugin marketplace add superdesigndev/superdesign-skill` + `/plugin install superdesign@superdesign` install lines are all in the source.
- The fix routes (SKILL.md:44 (7)) match the spec, and the credit-free local fallback is kept.
- B16 keeps behaviour. Called without `cwd` (the CLI entry, ledger.py:114), `_repo_root(None)` and `os.path.join("", args.log)` act exactly as before. The `worst` → `first_failure` change is a rename only. The `_esc` fold is equivalent and nothing else used `_esc`. The annotations are correct and safe on 3.9 under `from __future__ import annotations`. The tests no longer call `os.chdir`.

## Issues

### Critical

None.

### Important

1. **Autopilot superdesign has no defined draft pick and no design approval.**
   - SKILL.md:39-40 and :44 (2); README.md:56; spec "When it is used", last bullet.
   - Autopilot from an existing spec may run superdesign when consent is recorded, but flow step (2) is "The user picks a draft on the canvas", and no user is present. SKILL.md:42 itself says superdesign "needs the user's pick". The spec meets superdesign's "implement only after the user approves a design" rule through the user's spec-and-mockup review, and autopilot skips that review. A lead following the text either stalls or picks a draft and spends credits with nobody looking. Uploading code and spending credits is also a side effect outside the worktree, which step 9 lists as an autopilot stop reason, and nothing says that recorded consent counts as the advance agreement.
   - Fix (pick one): (a) in autopilot from an existing spec, always use the built-in builder (simplest, and consistent with "needs the user's pick"); or (b) state that recorded consent is the advance agreement, generate the reproduction draft plus at most one variant, have the lead pick the draft closest to the spec and record `Ruling: draft <id> picked by the lead (autopilot)`, and put the canvas link in the finish report for the user's later review. Mirror the choice in README.md:56.

2. **Nothing stops the main session from loading superdesign outside the gated flow.**
   - SKILL.md:37-44.
   - The never-invoke rule covers subagents only. The reason it gives is that superdesign "can trigger itself on design requests", and that applies to the lead too. The superdesign description fires on "design a page, feature, flow ... even if they never say the word 'design tool'", which is what a tech-lead request with a UI looks like during Orient, Spec or brainstorming (steps 1-3), before the consent check at step 4. Loaded there, it runs its own preflight, the repository analysis, context selection and uploads, with no consent check, no file list and no allowlist.
   - Fix: add one sentence to step 4, for example: "Outside this flow, and until all three conditions hold, do not load the superdesign skill or run its CLI, even when a request looks like a design task, unless the user asks for superdesign by name."

3. **The approved file list is shown before the skill chooses the files, and is not shown again when files are added.** This is the deferred security minor, promoted.
   - SKILL.md:44 (1); layout.md:90.
   - The flow shows "the exact list of files you will pass as `--context-file`" and only then says "Then load the skill". The skill builds that list from the repository analysis (`pages.md`) and from import tracing (SUPERDESIGN.md:52), so the lead cannot know it beforehand. Later calls also add files: RESUME.md "targeted context expansion", `execute-flow-pages --context-file`, `iterate-design-draft`, and `create-component` templates converted from source. A user who said yes to a list of 12 files reasonably expects only those 12 to leave the machine. The never-select patterns still block the obvious secrets, but source code beyond the approved list goes out without a yes.
   - Fix: reorder flow step (1): allowlist, then load the skill and run the repository analysis, then show the generations, context files, uploads (images, fonts, logos) and component templates and get a yes, then generate. Add: "Before any later call that passes a file or asset not yet approved, show the additions and get a yes (a status note in autopilot)."

### Minor

1. **An empty email counts as a consent match** (deferred). SKILL.md:39, layout.md:86. When `git config user.email` is unset, `user:` (empty) matches the empty current value. Fix: "an empty or unset `user.email` is no match; ask every time and store no consent".
2. **No command is named for recording the CLI version** (deferred). SKILL.md:44 (6) and layout.md:139 say "version from the preflight", but the source shows the preflight prints the `auth:` line and recent projects, not a version. Fix: name `npm view @superdesign/cli version` (known to work) and record its output. Pinning `@<version>` for the rest of the run (lens minor 4) can go to the backlog.
3. **The allowlist timing differs between the documents.** SKILL.md:44 (1) says "Before the first generation", while layout.md:210 says "before the repository analysis or the first CLI call". The preflight (SKILL.md:40) is the first CLI call and comes before flow step (1). Fix: SKILL.md:40 says to add the allowlist before the preflight.
4. **The consent text leaves out two channels.** layout.md:90 names "uploaded images", but the skill also uploads brand fonts and logos (`upload-asset --purpose brand --type font`) and component templates converted from project source (`create-component`, SUPERDESIGN.md:121-126). Fix: "uploaded images, fonts and logos (public URLs), and component templates converted from project source".
5. **The ruling for `consent: no` is ambiguous.** SKILL.md:39 says "valid only when ... `consent: yes` ... Otherwise ask", yet also "never ask again" after a no. It is unclear whether another user's `consent: no` blocks or triggers a question. Fix: "A `consent: no` whose `user:` matches is not asked again; any other file is treated as no consent."
6. **The README is thinner than the skill.** README.md:55-56 has no stored "no", no withdrawal, no retention ("stored by superdesign") and no `.superdesign/` allowlist. It also says "Autopilot uses it only if consent was recorded before the start", while SKILL.md:39 limits that to autopilot from an existing spec (deferred Task 2 minor). Fix: add one line each and align the autopilot wording.
7. **The standalone check is loose** (lens minor 5). mockup-prompt.md:26 does not name the Tailwind and Lucide hosts. Tailwind's Play CDN is unpinned third-party JavaScript that runs in the reviewers' browsers and the harness whenever the committed `mockup.html` opens. Fix (backlog): name the exact hosts and URLs, and fail on any other `<script src>`, `<link>`, `<iframe>`, and on inline fetch, XHR or WebSocket code.
8. **Canvas and preview links go into the committed journal** (lens minor 8). layout.md:139. The source does not say whether `preview/draft/<id>` needs a login. Fix (backlog): record the ids only, or record the links only once they are confirmed to need the account's login.
9. **The ledger path and `--progress` still resolve against the process cwd** (deferred Task 3 minor). ledger.py:51 and :85. Only tests pass `cwd`, and they use absolute paths. The new `run(env=...)` merges into `os.environ`, while `run_script` replaces it, and no test uses it yet. Fix (backlog): document `cwd` as test-only, or join it to the relative paths.
10. **The init subagent still has Bash** (lens minor 7) and **test_readmes checks only four superdesign strings** (Task 2 minor). Backlog.

## Requirements

| Req | Evidence | Status |
|---|---|---|
| R1 conditions, otherwise built-in | SKILL.md:37-40 (ordered: skill, consent, auth preflight; headless/cloud built-in), layout.md:86, :143; tests `test_superdesign_conditions_in_order`, `test_superdesign_in_skill` | Met; Important 1 and 2 are gaps around it |
| R2 consent once per user and clone, with costs and what leaves | layout.md:76-92 (credits, lead tokens, what is sent, retention, unpinned CLI, withdrawal, user binding); SKILL.md:39; tests `test_superdesign_consent_text`, `test_superdesign_consent_identity_and_withdrawal` | Met; Important 3 and Minors 1, 4, 5 sharpen it |
| R3 lead only, subagents never | SKILL.md:42, :58, :178; mockup-prompt.md:5 and the five other prompts; init exception SKILL.md:42; tests in `test_prompts.py`, `test_superdesign_init_exception` | Met for subagents; Important 2 covers the main session |
| R4 export, standalone check, fallback, journal | SKILL.md:44 (3)-(6); mockup-prompt.md:22-29; layout.md:136-143 | Met; Minors 2 and 7 |
| R5 design-system pointer, .superdesign rules | layout.md:25, :74, :203-210; SKILL.md:44 (1) | Met; Minor 3 |
| R6 README section, version 0.3.0 | README.md:49-58; plugin.json:4 and marketplace.json:37 at 0.3.0; `test_packaging` | Met; Minor 6 |
| R7 B16 | ledger.py:38-79, ledger_checkpoint.py:100-107, ledger_core.py:295, :322-325, ledger_report.py:7-13, test_ledger_cli.py:27-35; 166 tests OK, 0.915 s against a 1.12 s ratchet | Met; behaviour kept |

## Deferred minors: triage

| Source | Item | Ruling |
|---|---|---|
| Task 1 / security | Empty git user.email counts as a consent match | Fix now (Minor 1, one clause) |
| Task 1 / security | File list shown before the skill picks its files | Fix now, promoted to Important 3 |
| Task 1 / security | No command named for recording the CLI version | Fix now (Minor 2, one clause) |
| Task 1 batch review | Allowlist step and other batch minors | Mostly addressed in f8e79ab; the timing inconsistency left is Minor 3, fix now |
| Security lens 4 | Pin the CLI version per run | Backlog (the spec chose unpinned, and it is disclosed) |
| Security lens 5 | Standalone check hosts and inline network code | Backlog (Minor 7) |
| Security lens 7 | Init subagent without Bash | Backlog |
| Security lens 8 | Canvas and preview links in the committed journal | Backlog (Minor 8) |
| Task 2 | README lacks stored "no" and the allowlist; test_readmes checks 4 strings | README lines: fix now with Minor 6; test breadth: backlog |
| Task 3 | Ledger path and --progress resolve against the process cwd | Backlog (Minor 9) |
| Ruling (no inventory before Task 3) | — | Accepted: no scripts changed in wave 1, and no duplicate tests found in review |

## Declined to judge

- That superdesign works live (CLI output shapes, whether `get-design --output` exists in the shipped CLI version): the spec puts the live run out of scope (backlog B1).
- Whether `git config user.email` is strong enough as identity: the spec and the security lens accepted it against the threat of consent borrowed through git; it is not authentication, and nothing claims it is.
- Superdesign's own server-side handling beyond what its documents say.

## Assessment

**Ready to merge: with fixes.**

**Reasoning:** The documents tell one consistent story on the main path, the built-in path is unchanged, B16 keeps behaviour and the suite is green and fast. Three gaps in consent and autopilot, all fixed by wording in SKILL.md, let code leave the machine, or let the flow stall, outside what the user actually approved: who picks the draft in autopilot, the main session loading superdesign on its own outside step 4, and a file list approved before the files are known. Fix those three and the four cheap minors (1, 2, 3, 6) before merging, and send the rest to the backlog.
