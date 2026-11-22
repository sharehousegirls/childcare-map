# Saved facilities implementation — 2026-11-22

## Scope
- Browser-local saved facility bookmarks to support return visits without account/backend persistence.
- Save only facilities with an identifier in the current dataset. Demo facilities have explicit fictional `demo-` IDs; live API rows use the provider facility ID when present.
- Save/load/delete UI. Loading filters the current list to the exact ID and scrolls the matching card into view.
- Maximum 50 bookmarks per browser.

## Stored fields
`facilityId`, `name`, `region`, `type`, `address`, `savedAt`.
Strings are trimmed, bounded, and control characters rejected. Saved display values use `textContent`, not HTML insertion.

## Safeguards and limitations
- Duplicate facility IDs are rejected; stored duplicate IDs are normalized away.
- Malformed JSON/records are ignored.
- Storage access/write errors are handled. Failed reads do not overwrite stored data.
- Loading uses exact ID. A stale/missing source ID produces a message rather than falling back to a similar facility name.
- Facilities without IDs cannot be saved.
- Demo IDs are fictional, not official facility IDs.
- LocalStorage only; no account, sync, backend, cross-device restore. Browser data can be cleared.

## Acceptance criteria
- Save, load exact facility, and delete are available for facilities with IDs.
- Duplicate saves and >50 items are prevented.
- Invalid stored data and storage failures are handled safely.
- Stored metadata is rendered as text.
- No-ID save controls are disabled.
- Visible keyboard focus is retained for controls.

## Verification
- **PASS:** 12 unit tests in isolated Node 22 harness.
- **PASS:** GitHub Actions run #114: 68 backend tests, 40 frontend tests (8 regional summary, 11 saved regions, 9 saved searches, 12 saved facilities) and JavaScript syntax checks.
- **NOT RUN:** manual browser, responsive, and screen-reader verification.

## Future
Canonicalize saved facility identifiers if source ID stability is confirmed; do not add cross-device accounts/sync in this prototype phase.
