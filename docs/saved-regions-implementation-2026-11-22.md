# Saved regions — implementation note (2026-11-22)

## Scope

Added browser-local save/select/delete for an individual region using the existing region selector. This is a bounded Lock-in First feature intended to make return visits easier without accounts or server storage.

## Files

- `saved-regions.mjs`: storage normalization, duplicate-region prevention, maximum of 20 entries, safe handling of malformed JSON and browser storage errors.
- `tests/saved-regions.test.mjs`: eleven module tests.
- `index.html`, `app.js`, `styles.css`: accessible status area, region save button/list, load/delete actions, responsive layout.
- `.github/workflows/backend-tests.yml`: checks the module syntax and runs all `tests/*.test.mjs` files.

## Storage contract

Key: `childcare-map:saved-regions:v1`

Each entry stores:
- `id`: client-generated item ID
- `region`: current selector value (display-name string in this prototype)
- `savedAt`: ISO timestamp

The “all regions” selector value is not saveable. Duplicate region labels are prevented. Maximum 20 entries. No accounts, server synchronization or cross-device sync.

## Acceptance criteria

- Save one selected region; it appears in the list.
- Saving the same region again is rejected as a duplicate.
- Load an existing entry and select it in the region selector.
- Delete an entry and verify it no longer appears.
- Empty/all selection is rejected.
- Malformed data and storage access failures do not crash the app or overwrite data on read failure.
- Responsive styles and accessible button names/status messages are present.

## Verification

- **PASS (isolated local Node harness):** 11/11 tests; module syntax check. Duplicate region IDs are rejected and malformed stored entries with duplicate IDs are skipped.
- **PASS — GitHub Actions run #98:** all 45 backend tests, JavaScript syntax checks, 9 saved-search tests and 11 saved-region tests passed for code commit `1d8825a5560e9100774494d0234bf53bbacd6657. https://github.com/sharehousegirls/childcare-map/actions/runs/44985738434
- **NOT RUN:** browser manual interaction, mobile viewport, screen-reader check.

## Limitations and migration

Current selector values are display names, not verified official region IDs. A region name may change or collide when canonical code data is imported. The UI refuses to load a saved value if it is absent from the current selector; it does not silently fall back to another region. When official IDs are integrated, use a versioned key or migration that retains old display names only as fallback labels and never invents a code.
