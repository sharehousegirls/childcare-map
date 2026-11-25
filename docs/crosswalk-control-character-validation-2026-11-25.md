# Crosswalk control-character validation — 2026-11-25

## Scope
The versioned legal-dong → administrative-dong crosswalk validator now rejects embedded C0 controls (U+0000–U+001F) and C1 controls (U+007F–U+009F) in text metadata and effective-date strings.

- Text fields: `legal_region_id`, `admin_region_id`, `crosswalk_version`, `source_system`, and `source_reference`.
- Date fields: `valid_from` and `valid_to` receive an explicit control-character check before ISO-date parsing.
- Existing field-specific issue codes are preserved as `{field}_contains_control_character`.
- Validation remains structural only; it does not establish official provenance, legal-dong/admin-dong geographic equivalence, or license compliance.

## Regression tests
Two tests inject U+0085 (NEL) into interior positions, keeping string lengths unchanged:
1. Each crosswalk text field is checked for its field-specific control-character issue.
2. Both date fields are checked for their field-specific control-character issue before date parsing.

## Verification
- Local test execution: **NOT RUN**. A local checkout attempt failed because the container could not resolve `github.com`.
- GitHub Actions: **pending** for the latest branch commit.
- No official region files were imported, no live API was called, and no deployment or merge to `main` was performed.
