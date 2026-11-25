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

- **PASS — GitHub Actions run #303:** 137 backend tests, 76 frontend tests, and JavaScript syntax checks passed. https://github.com/sharehousegirls/childcare-map/actions/runs/45548657224
- Runs #299–#302 failed because the test fixture used a literal backslash-plus-t instead of TAB; the fixture was corrected to Python `\\t` source (a runtime TAB) and run #303 passed. The validator code did not change for this fixture correction.
- Local test execution: **NOT RUN**; this connector session cannot execute a repository checkout.
- No merge to `main` or deployment performed.
