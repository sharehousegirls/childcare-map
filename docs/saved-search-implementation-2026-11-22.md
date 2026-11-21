# Saved-search feature — 2026-11-22

## Scope
Adds browser-local saved filters to the static prototype to support repeat visits without account infrastructure. It stores only search settings: selected region, facility-name query, facility type, and zero-wait toggle.

## User behavior
- Save the current filters; the name is optional and otherwise generated from the filter values.
- Restore a saved filter to the controls and refresh the facility list.
- Delete saved entries.
- Maximum 20 entries.
- The feature is local to one browser profile/device; no server, login, analytics, or facility data is stored.

## Storage and safety
- Versioned localStorage key: childcare-map:saved-searches:v1.
- Validate persisted records and ignore malformed entries.
- Treat unavailable/quota-restricted storage as a recoverable UI error; never block facility search. If reads fail, do not overwrite stored data based on an assumed empty list.
- Saved names and descriptions are rendered with DOM textContent, not HTML injection.
- Search settings are not a claim of real data. The demo/live status remains controlled by the existing data source indicator.

## Acceptance criteria
1. Save selected region, query, type and zero-wait toggle.
2. Reload the page and retain the saved item when browser storage is available.
3. Restore all four controls and rerender the facility list.
4. Delete one item without affecting other saved entries.
5. Enforce the 20-entry limit.
6. Invalid/corrupt storage and storage exceptions do not crash the page.
7. No backend or third-party dependency is required.

## Verification
- Node built-in test suite covers persistence round-trip, duplicate handling, corrupt storage, invalid items, cap, deletion, and storage errors.
- GitHub Actions run #57 successfully ran backend tests and the saved-search test step for commit e3dd6039132e545e2512f4a4162f41d7a2ad277a (8 saved-search tests at that point): https://github.com/sharehousegirls/childcare-map/actions/runs/44957889342.
- Run #58 succeeded for backend tests, JavaScript syntax checks, and the updated saved-search suite: https://github.com/sharehousegirls/childcare-map/actions/runs/44958036482.
- An isolated local harness passed all 9 saved-search tests after read-error protection was added.
- Read failures now return a storage error without attempting to overwrite the saved list; a regression test verifies this.
- Local repository checkout and browser interaction were not available in this run; CI verifies the syntax and storage module, not DOM behavior.
