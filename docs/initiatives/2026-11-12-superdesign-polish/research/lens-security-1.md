# Lens review: security, wave 1

Task 1, "Superdesign polish and 0.3.1" (commit 959f486, diff b4d6bd0..959f486). Mockup: none. Harness: none (not rendered; documentation-only change).

Counts: Critical 0, Important 3, Minor 5.

Paths are in the lane-1 worktree (`/home/user/phejno-plugins/.worktrees/lane-1/`).

## What holds

- Consent text (`layout.md:88-92`, `README.md` consent bullets) names every channel the spec lists: the spec, the request (stored verbatim, `layout.md:91` and README), selected project files, images, fonts and logos as public URLs, component templates from project source (`create-component`), and the unpinned CLI. SKILL step (1) asks before the first upload or generation.
- Ids only: SKILL step (6) (`SKILL.md:44`) and the journal template (`layout.md:142-145`) no longer record canvas or preview links. Nothing in the repository records such links.
- Init check never destroys user work. Nothing is reverted automatically, and a mismatch stops superdesign for the run (fails closed on a detected change).
- No secrets in the diff. The `ledger.py` change is a docstring only.

## Important

1. **The standalone allowlist is matched by substring, so any host passes.** `tech-lead/skills/tech-lead/mockup-prompt.md:26` allows any script or style "whose URL names the package `tailwindcss` or `lucide` ... and contains a full version `x.y.z`". Read literally, `https://evil.example/tailwindcss@3.4.1/x.js` and `https://evil.example/a.js?lucide=1.2.3` both pass. The x.y.z rule pins a version but does not pin who serves the file. Fix: name the hosts and the path shape. For example: "scripts or styles from `cdn.tailwindcss.com/<x.y.z>`, `cdn.jsdelivr.net/npm/<pkg>@<x.y.z>/` or `unpkg.com/<pkg>@<x.y.z>/`, where `<pkg>` is `tailwindcss`, `@tailwindcss/browser` or `lucide`; any other host fails". Apply the same wording to SKILL step (4) ("pinned Tailwind and Lucide only", `SKILL.md:44`). Add a test for a host name.

2. **The check's list of network calls reads as complete but misses several, and only the static resources are caught.** The catch-all at `mockup-prompt.md:26` ("any remote resource other than ...") covers tags and CSS: `<object>`/`<embed>`, `<link rel=preload|modulepreload|prefetch|icon>`, CSS `@import`/`url()`, and `<video>`/`<audio>`/`srcset`. The list of JavaScript calls is closed ("inline `fetch`, `XMLHttpRequest` or `WebSocket` code") and misses:
   - `import('https://…')`
   - `navigator.sendBeacon`
   - `EventSource`
   - `new Image().src = …`
   - `document.createElement('script')` and links or iframes created by script
   - `window.open` or `location` to a remote URL
   - code that looks up these calls by computed strings or `eval`/`Function`

   `<form action="https://…">` and `<meta http-equiv="refresh" content="…;url=https://…">` are not resources at all, so a builder that reads the list literally passes them. Fix, in two parts:
   - (a) Make the list open: "any other inline JS that opens a connection or loads code or a page (for example `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `navigator.sendBeacon`, `import()`, scripts, links or iframes created by script, image or media `src` set by script, `window.open`/`location` to a remote URL, `eval`/`Function` on built strings), a remote `<form action>` and a `<meta http-equiv="refresh">`".
   - (b) Better, enforce rather than inspect: the builder adds `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' <pinned URLs>; style-src 'unsafe-inline' <pinned URLs>; img-src data: <upload host>; font-src data:; connect-src 'none'; frame-src 'none'; object-src 'none'; form-action 'none'; base-uri 'none'">` as the first element of `<head>`. Check once in a browser that the CDN Tailwind build still styles the page under it.

   (b) goes beyond decision 5's wording, so it is the lead's call. (a) stays within "Anything else fails the check".

3. **SKILL.md and layout.md give different scopes for the init check, so SKILL lets the committed `design-system.md` through.** `SKILL.md:42` flags only entries "outside `.superdesign/`". Decision 8 and `layout.md:94` flag anything "outside `.superdesign/init/`". The lead reads SKILL first. `.superdesign/design-system.md` is not ignored (README: the allowlist keeps it) and becomes the project's design-system reference (`layout.md:74`). Under SKILL's wording, an init subagent that writes or changes that file passes. `layout.md:94` also contradicts itself: "Entries under `.superdesign/` are allowed", then "outside `.superdesign/init/`". Fix:
   - In `SKILL.md:42`, change "outside `.superdesign/`" to "outside `.superdesign/init/`".
   - In `layout.md:94`, use one rule: "Allowed: entries under `.superdesign/init/`, or a single `!! .superdesign/` line when git collapses the ignored directory; anything else, including `.superdesign/design-system.md`, is a change."
   - Assert `outside \`.superdesign/init/\`` in both files in `test_superdesign_polish`.

## Minor

1. **The image rule cannot be checked.** "Public `https://` images returned by superdesign uploads" (`mockup-prompt.md:26`) gives the builder no list or host to compare against, so an `<img>` or CSS `url()` from any host, such as a tracking pixel, can pass. Fix: the lead passes the upload URLs, or the asset host, from the upload output in the builder brief. Any other image host fails.
2. **No integrity on allowed scripts.** `cdn.tailwindcss.com/<version>` is served by Tailwind and is not an immutable npm path. Consider requiring `integrity="sha384-…"` with `crossorigin`, or preferring the npm CDN paths, which are immutable per version.
3. **The init check's stated limit is incomplete** (`layout.md:94`). `git status --porcelain --ignored` also does not show:
   - changes inside `.git/` (hooks, or `config` keys such as `core.fsmonitor` or `core.hooksPath`, which run a command on the lead's very next `git status`, the compare itself)
   - edits to files that are already ignored, and anything inside a collapsed ignored directory
   - deleted ignored files (their line disappears; the rule names only "new or changed" entries)
   - writes outside the repository

   Fix: list these in the Limit sentence. Also say that a disappeared entry counts as a change.
4. **The check's own failure is unspecified.** The docs do not say what happens when either `git status` command fails (no repository, or a git error). Fix: one clause: "if either command fails, treat it as a change". This keeps the check fail-closed.
5. **Order of the `.gitignore` edit.** README says the lead adds the `.superdesign/*` and `.tech-lead/` lines to `.gitignore` "before the first CLI call", which can fall between the baseline and the compare. It would then show as a change and stop superdesign. It also changes how `.superdesign/` is collapsed between the two snapshots. Fix: say the `.gitignore` edit happens before the baseline is taken.

## Assumptions

- The threat considered is a superdesign export or third-party skill text (the unpinned plugin's INIT.md, or server-generated HTML) that misbehaves. The mockup is opened from `file://` by the user and by reviewers. The render harness renders the implementation, not the mockup.
- `import-design-draft --into` and `iterate-design-draft` send back only content that is already disclosed (the draft, plus spec-derived screen ids). They are not counted as an undisclosed channel.
