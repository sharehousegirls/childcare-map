# Region manifest C1 control-character validation — 2026-11-25

## Scope

A bounded hardening change to the source metadata manifest validator. The shared text normalization now rejects C0 controls (U+0000–U+001F) and C1 controls (U+007F–U+009F) after outer whitespace trimming, across all manifest text fields.

## Behavior

- Keeps the existing field-specific validation issue suffix: `*_contains_control_character`.
- The regression test replaces an interior character with U+0085 without changing field length, avoiding unrelated maximum-length failures.
- Applies consistently to dataset kind, source system, dataset ID, URLs, filename, SHA-256 text, dates/timestamps, attribution, review status and optional license-review date.
- Validation still fails closed; contaminated fields are not normalized or accepted.
- No source archive is downloaded, imported, or re-published; no legal reuse decision is made.

## Acceptance criteria

- [x] C0 controls remain rejected by the shared text validator.
- [x] C1 controls are rejected for each manifest text field.
- [x] Field-specific issue codes remain stable.
- [x] No dependencies or live API connections are added.

## Test status

- CI: pending for this branch.
- Local checkout tests: NOT RUN; connector-only work session has no repository checkout.
- Live API, archive parsing, reuse/licensing and geospatial mapping: BLOCKED/PENDING independently of this change.
