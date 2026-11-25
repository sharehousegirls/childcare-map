# Crosswalk control-character validation — 2026-11-25

## Scope
The versioned legal-dong → administrative-dong crosswalk validator rejects embedded C0 controls (U+0000–U+001F) and C1 controls (U+007F–U+009F) in text metadata and effective-date strings. C1 checks occur before whitespace trimming, so boundary NEL characters are not silently removed.

- Text fields: `legal_region_id`, `admin_region_id`, `crosswalk_version`, `source_system`, and `source_reference`.
- Date fields: `valid_from` and `valid_to` receive an explicit control-character check before ISO-date parsing.
- Existing field-specific issue codes are preserved as `{field}_contains_control_character`.
- Validation remains structural only; it does not establish official provenance, legal-dong/admin-dong geographic equivalence, or license compliance.

## Regression tests
Two tests inject U+0085 (NEL) into interior, leading, and trailing positions:
1. Each crosswalk text field is checked for its field-specific control-character issue at all three positions.
2. Both date fields are checked for their field-specific control-character issue before date parsing at all three positions.

## Verification
- Local test execution: **NOT RUN**. A local checkout attempt failed because the container could not resolve `github.com`.
- **PASS — GitHub Actions run #283:** 133 backend tests, 76 frontend tests, and JavaScript syntax checks passed. https://github.com/sharehousegirls/childcare-map/actions/runs/45519664581
- **PASS — run #287:** boundary-probe code/test commit passed with 133 backend tests, 76 frontend tests, and JavaScript syntax checks. https://github.com/sharehousegirls/childcare-map/actions/runs/45519924178
- **PASS — run #281:** code/test commit also passed with 133 backend and 76 frontend tests. https://github.com/sharehousegirls/childcare-map/actions/runs/45519621808
- Initial run #280 failed three text-field probes because U+0085 was appended at the end of short values and removed by Python `strip()`; probes were corrected to keep the character interior. The code implementation was unchanged for this fixture correction. https://github.com/sharehousegirls/childcare-map/actions/runs/45519593914
- No official region files were imported, no live API was called, and no deployment or merge to `main` was performed.
