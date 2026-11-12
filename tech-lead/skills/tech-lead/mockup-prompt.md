# Mockup builder

Build a mockup of the interface described in the spec so the user can judge it before implementation.

Spec: read {{SPEC_PATH}}.
Output file: {{MOCKUP_PATH}}
Kind: {{KIND}}

- `static`: screens only, no behavior.
- `prototype`: clickable, moving between screens and states.
- `simulation`: models the real behavior with fake data and logic.

## Rules

- One self-contained HTML file: inline CSS and JS, no network requests (no CDN, fonts, images or fetches), so it opens straight from the file system.
- Use fake data only.
- Give one element with an `id` to each screen or state, so requirements can point at `#id`.
- Do not touch any other file.

## Deliverable

At the end of the file, or in your reply, include a mapping list from each screen id to the spec requirements it shows. Reply with the absolute path of the mockup and that list.
