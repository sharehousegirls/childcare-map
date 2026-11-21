# SQLite snapshot storage scaffold — 2026-11-22

## Scope

Implemented `backend/app/storage.py` without connecting it to the live provider or API route. It uses only the Python standard library and a file-backed SQLite database.

## Tables
- `facility`: provider facility ID as current primary key, latest metadata, first/last seen timestamps.
- `facility_snapshot`: capacity/enrollment, age buckets, reported and derived totals, collection/source dates and quality flags. One snapshot per facility per ingestion run.
- `ingestion_run`: source, fingerprint, and received/stored/flagged/unresolved counters.
- `unresolved_record`: normalized audit data for missing IDs and duplicate rows. The full raw provider payload is not stored.

## Behavior
- Uses a transaction for each batch.
- Repeating the same run ID and normalized batch returns the previous summary; reusing that ID with different content raises an error.
- Missing IDs are retained for review and not inserted as canonical facilities.
- In-batch duplicate IDs: first row stored with duplicate flag; later rows retained as unresolved.
- Missing counts remain null; explicit zero remains zero. Invalid/negative/non-integer count values become null and receive a flag.
- Derived age total is available only if all age buckets are present. Provider total is preserved and mismatch is flagged.
- Snapshot rows are append-only for updates (SQLite trigger); deletes remain possible for future retention policy.

## Local verification
- PASS: 11 storage unit tests in an isolated local copy.
- PASS: Python `compileall` on the isolated storage module/tests.
- NOT RUN: direct repository checkout tests and browser/E2E tests.
- CI for the new commit is the next verification gate.

## Limitations / follow-up
- Storage is not wired to the API adapter or `/api/facilities`.
- No schema versioning/migrations, failed-run/retry records, retention/backup, or production load/concurrency review.
- Provider normalization currently may turn malformed numeric values into null before storage, so the storage layer cannot distinguish those cases unless provider diagnostics are extended.
- Geographic coordinates are parsed numerically only; CRS and axis order remain unverified.
- Do not connect live API until official schema, sample, access and reuse terms are verified.

## Next
1. Verify official API schema/rights and credentials.
2. Add versioned migrations and ingestion error/retry auditing.
3. Integrate only after API schema/rights/quality gates pass.
4. Implement verified administrative-region hierarchy and map/facility views.
