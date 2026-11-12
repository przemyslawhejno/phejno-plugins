# tech-lead 0.3.1: superdesign wording and safety polish (B17) — design

Date: 2026-11-12

## Goal

Close backlog B17: the open minor findings from the 0.3.0 reviews (`docs/initiatives/2026-11-12-superdesign/research/review-final-superdesign.md` minors 4, 7-10 and `rereview-final-superdesign.md` minors). Minors 1, 2, 3, 5 and 6 of the final review were already fixed in 0.3.0.

## Decisions

| # | Finding | Decision |
|---|---|---|
| 1 | "get a yes before the first generation" | "before the first upload or generation" (the skill uploads assets and creates components before generating). |
| 2 | "No user present" undefined for `--auto` runs | Define: the user is not answering in this conversation at step 4. In an `--auto` run where the user is still in the conversation at step 4, the lead asks as usual. |
| 3 | `npm view` reports the registry's latest | Record it as "registry latest at run time"; the journal says the executed version may differ when npx used a cache. |
| 4 | Consent text misses two channels | Add: fonts and logos uploaded as brand assets (public URLs), and component templates converted from project source (`create-component`). |
| 5 | Standalone check is loose | Allowed remote resources: public `https://` images returned by superdesign uploads, and scripts and styles whose URL names the package `tailwindcss` or `lucide` (or its host is `cdn.tailwindcss.com`) and contains a full version `x.y.z` (for example `tailwindcss@3.4.1`). Anything else fails the check: an unpinned Tailwind or Lucide URL, any other `<script src>`, a `<link>` to another script or style host, an `<iframe>`, or inline `fetch`, `XMLHttpRequest` or `WebSocket` code. On failure the mockup builder rebuilds the file locally without those resources (inline CSS and SVG), keeping the design. |
| 6 | Canvas and preview links in the committed journal | Record project and draft ids only; the links stay in the CLI output and on the user's account. |
| 7 | `cwd` in `ledger.py` | Document in the `main` docstring that `cwd` exists for tests: it sets where git runs and where a relative `--log` resolves; the ledger path and `--progress` are resolved by the caller. No behaviour change. |
| 8 | The init subagent still has Bash | The Agent tool cannot remove Bash from that subagent. Before dispatch the lead saves `git status --porcelain --ignored` as a baseline; after the subagent returns it runs the same command and compares. Any new or changed entry outside `.superdesign/init/` is never reverted automatically (it could be the user's work): the lead shows it to the user and stops using superdesign for this run until the user decides. Entries under `.superdesign/` are allowed (an ignored directory may show as one `!! .superdesign/` line). Limit, stated in layout.md: further edits to files that were already dirty before dispatch do not show up in this comparison. |
| 9 | `test_readmes` checks four superdesign strings | Extend the existing README test with the strings it does not yet assert among: stored "no", withdrawal, verbatim retention, the allowlist, the autopilot rule. |

Version 0.3.1.

## Out of scope

Pinning the CLI version for a whole run (stays as the disclosed "unpinned CLI"); live run (B1).
