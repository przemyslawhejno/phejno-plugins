# Final whole-branch review: tech-lead 0.3.1 (B17 superdesign polish, B18 project docs pointer)

Range: b342df8..9df56eb (14 commits). Spec: `docs/initiatives/2026-11-12-superdesign-polish/spec.md`. Single pass over the full diff, the spec, the plan, the journal, the ledger, progress.md and the three security-lens reports. Tests: `python3 -m unittest discover tech-lead/tests`, 169 tests, OK (1.04 s). Read-only; superdesign skill and CLI not invoked; no CLAUDE.md touched.

## Strengths

- All nine B17 decisions landed, and the wording matches across SKILL.md, layout.md and README:
  - D1: "before the first upload or generation" appears in SKILL.md:45 and layout.md:99, and the old wording is gone (a test asserts its absence).
  - D2: "not answering in this conversation at step 4" appears in SKILL.md:38, layout.md:95 and README:57.
  - D3: "registry latest at run time" appears in SKILL.md:45 and in the layout.md journal format.
  - D4: fonts and logos, and `create-component` templates, appear in all three consent texts.
  - D6: ids only. Step (6) and the journal template no longer carry links, and a test checks both.
  - D7: the docstring is the only change in scripts (ledger.py:100-101). No behaviour changed.
  - D9: the README test adds the three strings it did not already assert. The five decision-9 strings were already asserted.
- The standalone check is now decidable from the HTML alone:
  - It lists five exact URL shapes with a pinned `x.y.z`.
  - It lists the failures the CSP cannot stop: `<meta http-equiv="refresh">`, `<iframe>`, `<object>`, `<embed>` and a remote `<form action>`.
  - Inline network calls are handled by enforcement (`connect-src 'none'`) instead of inspection.
  - The CSP is always replaced and always inserted as the first element in `<head>`, in both modes (mockup-prompt.md:20, 27; SKILL.md:45). A permissive CSP in an export can no longer stand in for ours.
- The init check fails closed and keeps user work:
  - The baseline is taken after the `.gitignore` edit (lens minor 5 fixed).
  - The scope is narrowed to `.superdesign/init/`, tighter than the spec's `.superdesign/` and justified by the lens.
  - It never reverts anything automatically.
  - A `git status` failure stops superdesign for the run (lens minor 4 fixed).
- B18 is additive only. "When `CLAUDE.md` has no `## Project docs` section, add ... leave an existing section as it is" (SKILL.md:31, layout.md:31) cannot overwrite an existing section. The section text in layout.md matches the spec verbatim, and a test checks it.
- Version 0.3.1 matches in plugin.json, marketplace.json and test_packaging.

## Issues

### Critical

None.

### Important

1. **Security-lens minors were dropped without being recorded.**
   - Where: `.superpowers/sdd/plan/progress.md`, `docs/backlog.md`.
   - What is wrong: lens-security-1-fix2.md says "fix round 1 Minors 2-4 remain as ledgered". The journal says "two lens minors moved into Task 3" (both were done). But no progress line, ruling or backlog item holds the rest.
   - Still open from round 1:
     - Minor 1: the image rule cannot be checked.
     - Minor 2: no `integrity` on the allowed CDN scripts.
     - The rest of minor 3: edits to already-ignored files, writes inside collapsed ignored or untracked directories, and deleted ignored entries do not show in the init comparison.
   - Still open from fix round 1:
     - Minor 2: `img-src https:` beacons and `location`/`window.open` navigation.
     - Minor 3: `..` and `%2e%2e` segments inside the allowed shapes.
     - Minor 4: `blob:` media and workers break under `default-src 'none'` in built-in simulations.
   - Why it matters: under "nothing set aside is dropped silently", these are lost once the initiative closes.
   - Fix: add one backlog item (B19 [hygiene] superdesign standalone-check and init-check leftovers) that lists them with the lens report paths. Alternatively, fix the cheap ones now; see Minor 1 and 2.

### Minor

1. **The image allowance cannot be enforced.**
   - Where: mockup-prompt.md:27, "public `https://` images returned by superdesign uploads".
   - What is wrong: the builder works on the local file only and gets no upload URL or host to compare against, so any https image passes. The CSP's `img-src https:` does not narrow it either.
   - Exposure is low (fake data, mostly the viewer's IP).
   - Fix: the lead passes the upload URLs (or the asset host) from step (1) in the builder brief, and any other image host fails. Optionally narrow `img-src` the same way.
2. **The init-check limit statement is incomplete.**
   - Where: layout.md:103.
   - What is wrong: `git status --porcelain --ignored` also misses:
     - edits to files that are already ignored (for example `.env`);
     - anything written inside a directory that git collapses (`!! node_modules/`, `?? dir/`);
     - a deleted entry, unless "changed" is read to include a disappeared line.
   - Fix: add these to the Limit sentence, and say that a missing entry counts as a change.
3. **Fonts are disclosed as uploads, but the standalone check does not allow them.**
   - Where: mockup-prompt.md:27, against D4.
   - What is wrong: a font uploaded as a brand asset and referenced through `@font-face url()` is not an "image", so the check fails and the rebuild drops the font. This fails closed, which is safe.
   - Fix: either allow "images and fonts returned by superdesign uploads", or say that uploaded fonts are dropped.
4. **The D2 wording names `--auto` only.**
   - Where: SKILL.md:38, layout.md:95, README:57.
   - What is wrong: SKILL.md:29 also defines autopilot as the user saying beforehand that the work should run without stopping (as this initiative did). Read literally, a conversational autopilot with an absent user is not covered, and the lead would wait at the consent question.
   - The text follows the spec, so this is a spec gap.
   - Fix: "In autopilot (Start of work, item 5) where the user is not answering ...".
5. **The B18 commit can sweep up the user's uncommitted CLAUDE.md edits.**
   - Where: SKILL.md:31, "commit it with the initiative".
   - What is wrong: if `CLAUDE.md` already has uncommitted user changes, committing the file commits them too.
   - Fix: "when `CLAUDE.md` has uncommitted changes, add the section but leave it uncommitted and tell the user" (or stage only the added hunk).
6. **The README does not mention the B18 pointer.**
   - Where: tech-lead/README.md:29-31 (Document hierarchy).
   - Fix: one sentence: "The lead adds a `## Project docs` pointer to `CLAUDE.md` (an existing one is kept) so sessions without tech-lead save specs and plans in the initiative folder."
7. **The case-insensitive match is stated only in Rules.** This is the deferred minor; see Triage.
   - Where: mockup-prompt.md:27.
   - What is wrong: the export bullet repeats "remove every existing `<meta http-equiv="Content-Security-Policy">`" without "case-insensitively". Rules line 20 applies to every mockup, and an extra policy only tightens.
   - Fix: append "(`http-equiv` compared case-insensitively)" to the export bullet. The same applies to `http-equiv="refresh"`.

## Triage of deferred minors and rulings

| Item (progress.md / journal) | Ruling |
|---|---|
| Task 3: minor (deferred): case-insensitive http-equiv rule not repeated in the export-mode bullet | **Fix now.** It is a five-word edit in a security rule and also covers `refresh`. Minor 7 above. |
| Ruling (journal): pinned version instead of allowlisted host; cost if wrong: an unpinned script is removed | **Accept.** The exact shapes now give both host and version. Watch it in the B1 live run: superdesign exports commonly reference `https://cdn.tailwindcss.com` unpinned, which forces a full local rebuild every time. |
| Ruling (journal): no separate plan review for B18 | **Accept.** The change is additive, the text is fixed in the spec, and the batch review and this review cover it. |
| Unledgered lens minors (see Important 1) | **Record in backlog** (B19). Fix image upload URLs and the limit sentence now if the lead wants them cheap; the rest (SRI, `..` segments, `blob:`, navigation) can wait. |

## Merge preconditions (plan Task 2, lead, not yet done)

- This repository's `CLAUDE.md` with the `## Project docs` section does not exist yet.
- B17 and B18 are still `[ ]` in `docs/backlog.md`.
- `status.py --write` and `ledger.py check` are still to be run. These are expected after this review.

## Declined to judge

- Whether superdesign exports actually use the pinned shapes, and whether the CSP-wrapped Tailwind build renders. This needs a live run (B1, out of scope in the spec).
- "relative paths" in the check catching fragment-only `href="#id"` links. The wording predates 0.3.1 and is outside the diff.
- Whether the lead can reliably tell that the user is "not answering". This is a judgement the spec deliberately leaves to the lead.
- `CLAUDE.md` variants (`## Project Docs` with different casing, `CLAUDE.local.md`, a symlinked file). The worst case is a duplicate section, never an overwrite.

## Assessment

**Ready to merge: with fixes.**

**Reasoning:** All nine B17 decisions and B18 landed consistently and are tested. The CSP and standalone-check rules are exact and fail closed, the init check never reverts user work, and the only script change is the docstring. Before merge:
- Record the dropped lens minors in the backlog.
- Apply the one-phrase case-insensitivity fix.
- Complete Task 2.

The remaining Minors are optional wording.
