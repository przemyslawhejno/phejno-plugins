# Lens re-review: security, wave 1, fix round 2

Fix 62892f5..96187f8 (commit 96187f8). Paths are in `/home/user/phejno-plugins/.worktrees/lane-1/tech-lead/`. Read-only; no tests run (diff and report answer every question).

## Finding verdicts

1. **CSP meta added only "when missing"; a permissive export CSP could stand in for ours** — ADDRESSED.
   - Built-in path: `skills/tech-lead/mockup-prompt.md:20` (Rules, "in every mockup"): "Remove any existing `<meta http-equiv="Content-Security-Policy">` and add exactly this as the first element in `<head>`".
   - Superdesign-export path: `mockup-prompt.md:27` ends with "Always remove every existing `<meta http-equiv="Content-Security-Policy">` and insert exactly the Rules' Content-Security-Policy as the first element in `<head>`." The "when missing" wording is gone.
   - `SKILL.md:44` step (4) summary: "the builder removes any existing Content-Security-Policy meta and always inserts the one from `mockup-prompt.md` as the first element in `<head>`". Matches.
   - `tests/test_prompts.py` asserts "Always remove every existing" and "as the first element in `<head>`".
2. **Tailwind v4 browser build not among allowed shapes** — ADDRESSED.
   - `mockup-prompt.md:27` adds `https://cdn.jsdelivr.net/npm/@tailwindcss/browser@<x.y.z>...` under "each with a full version `x.y.z`". No trailing `/`, so the bare package URL (default file) is allowed, which is how v4 is usually loaded.
   - CSP `script-src` already includes `https://cdn.jsdelivr.net`; the build injects a `<style>` element, allowed by `style-src 'unsafe-inline'` (verified on 4.1.11 in fix round 1: no eval, no fetch).
   - Listed consistently: `SKILL.md:44` names "Tailwind, `@tailwindcss/browser` and Lucide"; no other file (layout.md, README) lists the shapes. Test asserts the new shape.

## New breakage in the fix diff

None Critical or Important.

- **Minor**, `mockup-prompt.md:27`: the new shape has `...` directly after `<x.y.z>` (no `/`), so it is looser than the others (e.g. `@4.1.11-anything`, or path segments). Pinned-version intent is clear and the CSP caps capability; the earlier Minor about `..` segments applies here too.
- **Minor**, `mockup-prompt.md:20,27`: "Remove any existing ... meta" does not say the `http-equiv` match is case-insensitive (`content-security-policy`). A builder reading literally could miss a lowercase one; an extra policy only tightens, so a leftover permissive one cannot loosen ours now that ours is always inserted. Exposure low.

## Out-of-scope observations

None new (fix round 1 Minors 2-4 remain as ledgered).

## Verdict

**Fix round:** All findings addressed, no new Critical/Important breakage.
