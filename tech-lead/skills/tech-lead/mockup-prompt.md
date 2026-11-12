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
- Give one element with an `id="<name>"` attribute to each screen or state, so requirements can point at `#id`.
- Do not touch any other file.

## UI standards

- Accessibility: WCAG 2.2 level AA, including 2.4.11 Focus Not Obscured (Minimum), 2.5.7 Dragging Movements, 2.5.8 Target Size (Minimum, 24x24 CSS px), 3.2.6 Consistent Help, 3.3.7 Redundant Entry and 3.3.8 Accessible Authentication (Minimum). 4.1.1 Parsing is obsolete. Where a checklist cites 2.5.5 Target Size (44x44 px, AAA), 2.5.8 governs.
- Design the empty, loading, error and success states.
- Responsive from the smallest supported viewport; light and dark themes when the product has both.
- Design tokens (CSS custom properties) instead of hard-coded values.
- Check HTML, CSS and JS choices against `modern-web-guidance` when installed.

## Review

A UI/UX expert reviews the mockup before the user sees it. You are resumed to fix its findings; fix them in the same file.

## Deliverable

At the end of the file, or in your reply, include a mapping list from each screen id to the spec requirements it shows. Reply with the absolute path of the mockup and that list.
