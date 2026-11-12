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
| 5 | Standalone check is loose | Allowed remote resources: public `https://` images returned by superdesign uploads, and the Tailwind and Lucide scripts or styles only with a version pinned in the URL. An unpinned one is pinned by the mockup builder to the version current at export and recorded. Any other `<script src>`, `<link>` to a script or style host, `<iframe>`, or inline `fetch`, `XMLHttpRequest` or `WebSocket` code fails the check and is removed in the local rebuild. |
| 6 | Canvas and preview links in the committed journal | Record project and draft ids only; the links stay in the CLI output and on the user's account. |
| 7 | `cwd` in `ledger.py` | Document in the `main` docstring that `cwd` exists for tests: it sets where git runs and where a relative `--log` resolves; the ledger path and `--progress` are resolved by the caller. No behaviour change. |
| 8 | The init subagent still has Bash | The Agent tool cannot remove Bash from that subagent, so the lead checks after it returns that `git status --porcelain` lists only paths under `.superdesign/init/`; anything else is reverted and the analysis is redone by the lead. |
| 9 | `test_readmes` checks four superdesign strings | Assert the stored "no", withdrawal, verbatim retention, the allowlist and the autopilot rule in the README. |

Version 0.3.1.

## Out of scope

Pinning the CLI version for a whole run (stays as the disclosed "unpinned CLI"); live run (B1).
