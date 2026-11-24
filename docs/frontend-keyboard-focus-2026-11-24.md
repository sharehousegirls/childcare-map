# Frontend keyboard focus visibility — 2026-11-24

## Scope

A small accessibility improvement for keyboard navigation in the static demo. A shared `:focus-visible` rule now gives links, buttons, inputs, selects, and textareas a consistent high-contrast outline and two-pixel offset. Existing component-specific focus styles remain more specific and can continue to override the shared rule.

## Expected behavior

- Keyboard focus on a common interactive control shows a visible outline.
- The shared rule does not force an outline on pointer-only focus because it uses `:focus-visible`.
- No new dependency, data source, network request, storage behavior, or deployment configuration was introduced.

## Acceptance criteria

- [x] Shared selector covers links and common interactive controls.
- [x] Focus outline is 3px and offset by 2px.
- [x] A Node test checks the shared selector and its outline declarations.
- [ ] Keyboard-only manual check in a browser.
- [ ] Contrast and screen-reader review.

## Tests

- **PASS — GitHub Actions #243:** Backend tests, JavaScript syntax checks, and frontend tests all completed successfully for commit `859e00c2`. The frontend suite includes this static focus-rule regression test. https://github.com/sharehousegirls/childcare-map/actions/runs/45357878490
- **NOT RUN:** local checkout tests, manual keyboard/browser review, mobile and assistive-technology testing.

This is a CSS-level acceptance check, not a substitute for a manual accessibility review.
