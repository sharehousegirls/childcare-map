# Childcare Map backend (API adapter scaffold)

This backend is intentionally not connected yet. The official provider's endpoint, required parameters, response structure, and field names must be confirmed from the API documentation and a sample response before configuring it. The service API requires credentials; never put the API key in frontend JavaScript or commit it.

## Local setup

Run the commands from the repository root, then enter `backend`:

1. Install Python 3.11+.
2. `cd backend`
3. Create a virtual environment: `python -m venv .venv`.
4. Activate it:
   - Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`.
6. Copy `.env.example` to `.env`:
   - Windows PowerShell: `Copy-Item .env.example .env`
   - macOS/Linux: `cp .env.example .env`
7. Fill the official API endpoint, key, query parameters, and field mapping only after verifying the API docs.
8. Run `uvicorn app.main:app --reload --port 8000`.
9. Check `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/api/facilities`.

## Environment variables

- `API_BASE_URL`: exact endpoint URL from official docs.
- `API_SERVICE_KEY`: issued key. Keep private.
- `API_KEY_PARAM`: key parameter name (defaults to `serviceKey`).
- `API_EXTRA_PARAMS`: JSON object of additional required query parameters.
- `API_FIELD_MAP`: JSON object mapping normalized field names to exact provider field names. Configure after reviewing a sample payload.

Normalized fields include facility_id, name, type, status, address, sido, sigungu, capacity, enrolled, latitude, longitude, wait_0..wait_5, wait_6_plus, wait_total, data_date. The adapter also exposes `wait_age_sum` and `wait_total_consistent` as quality diagnostics: the latter is true/false only when the provider total and all age buckets are available, otherwise null. A derived total from age buckets is not treated as an independently verified provider total.

- Facility IDs are trimmed; `facility_id_missing` flags blank IDs and `facility_id_duplicate` flags repeated IDs in the current response batch. Rows are retained for review rather than silently deduplicated. This batch-level check does not replace cross-page or nationwide deduplication.

## Security and data quality

- Request failures are sanitized before they are returned by the backend; raw HTTP exceptions can contain query URLs and service keys.
- `API_FIELD_MAP` must be a JSON object mapping known normalized fields to non-empty strings.
- API credentials must stay server-side. Do not put keys in frontend code, repository files, chat, or email.
- Missing values remain null; do not treat blanks as zero wait.
- Waitlist totals are application counts and may not represent unique children across facilities.
- `wait_total_consistent` reports whether the provider total equals the sum of age buckets when both are complete; null means a comparison was not possible. It does not rewrite the provider's reported total.

## SQLite snapshot storage (scaffold)

`app/storage.py` adds a file-backed SQLite repository for normalized records. It is independent of the unverified API adapter and is **not connected to `/api/facilities`**.

Tables created by `initialize_database(path)`:
- `facility`: latest provider-sourced identity/metadata keyed by provider facility ID.
- `facility_snapshot`: capacity, enrollment, age waitlist buckets, provider total, derived total, consistency flag, collection time, source date and quality flags.
- `ingestion_run`: batch fingerprint and received/stored/flagged/unresolved counts.
- `unresolved_record`: normalized audit rows for missing IDs and duplicate rows; raw provider payload is not retained.

`ingest_snapshot_batch(path, records, source=..., source_data_date=..., collected_at=..., run_id=...)` accepts already-normalized records. It uses a transaction, keeps explicit zero separate from unknown/null, derives an age total only when all buckets are present, preserves the reported total, and flags mismatches/invalid counts. Snapshot rows are append-only (updates blocked by a trigger; deletes remain available for future retention policy).

Idempotency: the same `run_id` and batch fingerprint returns the existing summary; reusing a `run_id` with different content raises an error. Missing facility IDs and duplicate rows are retained for review instead of silently discarded.

Use a file-backed SQLite path; `:memory:` is rejected because the functions open separate connections. This scaffold still lacks migrations/versioning, failed-run recording/retries, backup/retention policy, API integration, and production concurrency/load review.

Storage tests are in `tests/test_storage.py`; run the same test command below.

## Tests

Run from the backend directory:

```bash
python -m unittest discover -s tests -v
```

The tests cover XML/JSON record flattening, alias mapping, numeric/null handling, age-bucket sums, total consistency diagnostics, field-map validation, and credential-safe HTTP error messages.

## Important

- This is a connector scaffold, not a successful live data connection.
- The API adapter does not guess endpoint paths, request parameters, or response field names.
- Verify provider terms and commercial reuse before public deployment.
- Keep existing known-good demo files intact until live data is validated.
