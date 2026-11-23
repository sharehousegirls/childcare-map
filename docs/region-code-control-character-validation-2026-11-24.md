# Region metadata control-character validation — 2026-11-24

## Scope

A bounded hardening change to the normalized region-record validator. The validator rejects C0 control characters (U+0000–U+001F) and C1 control characters (U+007F–U+009F) in non-empty text fields after trimming outer whitespace. The fields covered are `region_id`, `name`, `region_type`, `parent_region_id`, `source_system`, and `source_code`.


## Behavior

- Outer whitespace is still trimmed before validation, preserving the existing normalization behavior.
- Empty optional values remain null; required fields are rejected by their existing required-field checks.
- Embedded C0/C1 control characters produce a field-specific `*_contains_control_character` validation issue.
- Codes remain strings; no official code format, length, or source schema is assumed.
- Input records are not mutated.
- No official region data was imported, no live API request was made, and no mapping or reuse permission was established by this change.


## Acceptance criteria

- [x] Every normalized region text field rejects embedded C0 controls.
- [x] Every normalized region text field rejects embedded C1 controls.
- [x] Existing trimming, leading-zero preservation, and source-code uniqueness behavior remain covered.
- [x] No official-code assumptions or external dependencies were added.
- [x] Repository CI for this change is verified.


## Test status

- **CI pending** for code/test commits `e96101b` and `b567423` at the time this note was added.
- **NOT RUN:** direct local repository checkout, official source import, live API, map/geospatial checks, browser and accessibility review.


## Verification outcome — 2026-11-24

- **PASS — GitHub Actions run #208:** 118 backend tests, 40 frontend tests, and JavaScript syntax checks succeeded on commit `36b2acd8ea77906c4635b12a1e162957626aba2d`. https://github.com/sharehousegirls/childcare-map/actions/runs/45219072602
- **Correction:** Runs #204–#207 initially failed because the test cases appended U+001F and U+0085, which Python `str.strip()` removes at the ends. The tests were corrected to insert both control characters inside each value, ensuring they exercise the embedded-control validation. The implementation was not changed for this test-placement issue.
- **NOT RUN:** direct local checkout, official source import, live API, CRS/spatial assignment, browser and accessibility checks.
