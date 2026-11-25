# Region-record control-character boundary validation — 2026-11-25

## Scope

The normalized region-record validator now rejects C0 (U+0000–U+001F) and C1 (U+007F–U+009F) control characters against the raw text value before whitespace trimming. This closes the same boundary-normalization gap previously fixed in the crosswalk validator.

## Fields covered

- `region_id`
- `name`
- `region_type`
- `parent_region_id`
- `source_system`
- `source_code`

Existing field-specific issue codes are preserved: `{field}_contains_control_character`.

## Regression coverage

- Existing interior C0/C1 tests remain.
- Added leading and trailing TAB cases for all six fields.
- Added leading and trailing NEL (U+0085) cases for all six fields.
- Acceptance: all 24 boundary probes return the field-specific control-character issue; existing valid fixture behavior and normalization remain unchanged.

## Review boundary

This is structural validation only. It does not establish official code provenance, hierarchy completeness, licensing, or geographic equivalence. No official region archive was imported and no live API was connected.

## Test status

- GitHub Actions: **PENDING** for this code/test change.
- Local test execution: **NOT RUN**; this connector session cannot execute a repository checkout.
- No merge to `main` or deployment performed.
