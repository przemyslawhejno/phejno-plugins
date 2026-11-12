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
