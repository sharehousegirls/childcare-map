# Region source-manifest boundary control validation — 2026-11-25

## Scope

Harden the metadata validator used to gate future region-code archive imports. No archive was downloaded, extracted, imported, or published.

## Issue found

The manifest text validator trimmed the value before checking C0 controls. A leading or trailing TAB could therefore be removed by normalization and escape the control-character check. Provenance, source/terms URLs, filename, hash, effective date, download timestamp, attribution, and reuse-review fields all pass through this helper.

## Change

- Reject raw C0 controls (U+0000–U+001F) and C1 controls (U+007F–U+009F) before normalization.
- Keep trimming and existing required/length validation for otherwise clean text.
- No new dependencies or changes to the reuse/import gate logic.

## Regression acceptance criteria

- Every covered text field rejects a leading or trailing TAB.
- Every covered text field rejects a leading or trailing NEL (U+0085).
- Existing valid manifest fixtures, HTTPS checks, filename checks, digest validation, date checks, archive preflight, and reuse gates remain unchanged.
- No live API or archive operations occur.

The test matrix covers 12 text fields × 2 boundaries × 2 control families = **48 boundary probes**.

## Test evidence

- **FAIL — GitHub Actions #309 and #310:** fixture escaping initially supplied a literal backslash-plus-`t`, not an actual TAB. These failures were in test input generation.
- Fixture corrected to use the Python TAB escape.
- **PASS — GitHub Actions #311:** 139 backend tests, 76 frontend tests, all JavaScript syntax checks passed: https://github.com/sharehousegirls/childcare-map/actions/runs/45561635420
- Local test execution: **NOT RUN** in this connector session.

## Review

The change is limited to raw string validation and tests. It does not loosen validation, mutate input records, or enable import. Existing pending/verified redistribution and commercial-use gates remain fail-closed. Official archive terms, layout, and geographic correctness remain unverified.

## Repository state

Working branch: `dev/region-validator-boundary-controls-2026-11-25`

No merge to `main`, live API request, archive import, or deployment was performed.
