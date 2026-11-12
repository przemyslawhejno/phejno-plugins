# Lens re-review: security, wave 1, fix round 1

Fix 959f486..62892f5. Paths are in `/home/user/phejno-plugins/.worktrees/lane-1/tech-lead/`. Read-only. No browser render was possible (cdn.tailwindcss.com is blocked by the network proxy). `@tailwindcss/browser@4.1.11` was taken from npm and grepped.

## Finding verdicts

1. **Allowlist matched by substring** — ADDRESSED. `skills/tech-lead/mockup-prompt.md:27` now lists four exact URL shapes with `x.y.z`, and "Anything else fails". `SKILL.md:44` step (4) points to them ("exact CDN URLs with a pinned x.y.z"). `tests/test_prompts.py` asserts all four shapes.
2. **Open-ended network list; enforce with CSP** — ADDRESSED.
   - `mockup-prompt.md:20` makes the CSP meta the first element in `<head>` in every mockup, so it covers both paths. It has `default-src 'none'` (which also covers object, media and worker), `connect-src 'none'`, `frame-src 'none'`, `form-action 'none'` and `base-uri 'none'`. Scripts and styles may come only from the CDN hosts plus inline. Images and fonts may come from `https:` or `data:`.
   - `mockup-prompt.md:27` fails meta refresh, `<iframe>`, `<object>`, `<embed>` and a remote `<form action>`.
   - The tests assert these strings.
   - See new breakage 1 for a gap in "when missing".
3. **Init check scope differs between SKILL and layout** — ADDRESSED. `SKILL.md:42` and `layout.md:94` both say "outside `.superdesign/init/`". The conflicting sentence "Entries under `.superdesign/` are allowed" is gone. `tests/test_skill_docs.py` asserts the scope in both files and rejects the old wording.

Folded minors:
- **Fail closed when `git status` fails** — ADDRESSED (`SKILL.md:42`, `layout.md:94`).
- **`.gitignore` before the baseline** — ADDRESSED. "with the `.gitignore` entries already added" (`SKILL.md:42`, `layout.md:94`) is consistent with "Before this first CLI call" at `SKILL.md:40`, which comes before flow step (1).
- **Limit includes `.git/` and writes outside the repo** — ADDRESSED (`layout.md:94`). Not taken from the earlier Minor 3, and non-blocking:
  - edits to files already ignored
  - deleted entries counting as a change

## Questions asked

**CSP allows whole hosts (jsdelivr, unpkg) that serve every npm package.** This is acceptable as Minor, not Important:
- The URL-shape check gates every `src` and `href` in the markup.
- The only way to reach another package is inline script, for example `import()` or a script element created by script. Inline script is already arbitrary code under `'unsafe-inline'`.
- What any code can do is capped by the same CSP, whatever its origin: no connect, no frames, no forms, no base. So the extra npm code gains no capability.
- The gain for an attacker is concealment: the payload is not visible in the file.
- Optional tightening: the builder could replace each host with the exact pinned URLs it kept. CSP path sources match exactly unless they end in `/`, though they are ignored after a redirect.

**Does Tailwind's Play CDN work under this CSP?** Probably, but this is not verified in a browser.
- The Play CDN generates CSS in the page and injects a `<style>` element. `style-src 'unsafe-inline'` allows that, and nothing needs `connect-src`.
- `@tailwindcss/browser@4.1.11`: no `new Function`, no `eval(`, no `fetch` or XHR, and one `createElement("style")`. It works under this CSP.
- The v3 Play CDN (`cdn.tailwindcss.com/<x.y.z>`, the shape that is allowed) could not be fetched here. If it uses `eval` or `new Function`, the CSP (no `'unsafe-eval'`) leaves the page unstyled. The fix report shows no browser check. Open one export once.
- The v4 Play CDN (`@tailwindcss/browser@<x.y.z>`) is not among the allowed shapes, so a superdesign export that uses it always goes to a local rebuild. That is safe but costly. Consider adding `https://cdn.jsdelivr.net/npm/@tailwindcss/browser@<x.y.z>/...`.

## New breakage in the fix diff

1. **Important**, `mockup-prompt.md:27`: "Add the Content-Security-Policy meta from Rules when missing." The fix also removed `fetch`/`XMLHttpRequest`/`WebSocket` from the failures and now relies on `connect-src 'none'` for them.
   - An export that brings its own permissive CSP meta (for example `default-src *`) can be read as "not missing". The builder then adds nothing, so inline network calls are neither blocked nor flagged.
   - Fix: "The mockup has exactly the CSP meta from Rules as the first element in `<head>`. Remove any other Content-Security-Policy meta, then add that one." Extra policies would only tighten, but a lone permissive policy replaces ours.
2. **Minor**, `mockup-prompt.md:20`: inline script can still beacon or navigate.
   - `img-src https:` lets inline script send image beacons to any host.
   - `location` and `window.open` navigation are not governed by CSP, and the check no longer names them.
   - Exposure is low: fake data, `file://`, mostly the viewer's IP. Option: name `window.open` and `location` to a remote URL among the failures.
3. **Minor**, `mockup-prompt.md:27`: `...` in the shapes does not exclude `..` or `%2e%2e` path segments. Browsers normalise them, so `https://cdn.jsdelivr.net/npm/lucide@1.2.3/../evil@1.0.0/x.js` loads `/npm/evil@1.0.0/x.js`. Fix: add "no `..` or percent-encoded dot segments".
4. **Minor**, `mockup-prompt.md:20`: the CSP now applies to built-in mockups as well. A simulation that uses `blob:` images, workers or `data:` media breaks under `default-src 'none'`. State this in the Rules, or add `blob:` to `img-src`.

## Out-of-scope observations

None.

## Verdict

**Fix round:** All findings addressed. One new Important remains: the CSP is added only "when missing", so a permissive CSP in the export can stand in for the required one.
