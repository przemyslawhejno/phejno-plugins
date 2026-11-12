# Plan review: superdesign polish 0.3.1

Coverage: spec decisions 1-9 map to the five open minors of the final review (4, 7-10, with 10 split into decisions 8 and 9) and the three rereview minors (decisions 1-3). Decisions 5-6 are the backlog items of review minors 7-8. Out of scope (CLI pinning, live run) has reasons. One task, one owner, no overlap, hygiene not required (one code task). Model sonnet/medium and the security lens suit consent and standalone-check work.

## Important

1. Decision 8 (spec, Review Focus 2): `git status --porcelain` on a dirty tree lists the user's own changes. Reverting "anything else" could destroy user work, and the check cannot tell the subagent's writes from existing ones. Also `.superdesign/` is git-ignored by the allowlist step, so writes there are invisible to porcelain. Fix: take a `git status --porcelain` baseline before dispatch, compare after, revert only paths that are new relative to the baseline (never pre-existing ones), and say that ignored paths are not covered.
2. Decision 5 (spec, Review Focus 1): "pinned by the mockup builder to the version current at export" is not decidable, because the builder works on a local file and has no defined source for the current version. Also "pinned" is undefined. Fix: define pinned as a full semver in the URL path or `@` segment (for example `tailwindcss@3.4.17`, `lucide@0.469.0`). The builder reads the version from the export (or fails the check and removes the resource, rebuilding without it). Name the test string the plan will assert for this.

## Minor

1. Decision 9 is largely done already. `test_readmes` (tests/test_packaging.py:91) asserts "not asked again", "deleting the file", "verbatim", ".superdesign/*" and "the built-in builder always runs". The plan's README asserts duplicate this. Fix: state the delta only (strings not yet asserted, or drop the item) and keep only the new tests.
2. Decision 6: SKILL.md step (6) also says "canvas and preview links". The plan's test checks only layout.md, so add the SKILL.md wording and an assertion.
3. Decision 1 touches three places (SKILL.md:44, layout.md:90, README if present). The plan's test names only one string, so assert it in both documents.
4. The test for decision 8 only checks the string `git status --porcelain`. Also assert the revert-and-redo wording, so Review Focus 2 is proven.

PLAN NEEDS CHANGES

## Round 2

Findings:
- Important 1 (dirty-tree revert): resolved. Baseline before dispatch, `--ignored`, no automatic revert.
- Important 2 (pinned undefined): resolved. Full `x.y.z` in the URL; local rebuild on failure. Test string "x.y.z" is asserted.
- Minor 1 (README duplicates): resolved. Plan extends the test only with strings not yet asserted.
- Minor 2 (SKILL.md step 6): resolved. Plan asserts neither SKILL.md step (6) nor layout.md records the links.
- Minor 3 (decision 1 in several places): partially. The plan asserts `before the first upload or generation` in SKILL.md only; layout.md:90 and the README are not asserted.
- Minor 4 (revert wording): resolved. The plan asserts `baseline` and the "never reverted automatically" statement.

New findings:
- Minor: `git status --porcelain --ignored` compares only status codes. A file the user already had modified (` M`) and the subagent edited again looks unchanged, and an ignored directory collapses to one entry such as `!! .superdesign/`. Fix: state the limit in the spec ("detects new paths and status changes, not further edits to already-dirty files") and treat `.superdesign/` as allowed.
- Minor: the allowed Tailwind and Lucide hosts are not named, so "Tailwind or Lucide URL" is decided by the builder's judgement. Fix: require the version segment in the URL and name the package (`tailwindcss`, `lucide`) as the match key.

PLAN APPROVED
