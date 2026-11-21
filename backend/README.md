# Childcare Map backend (API adapter scaffold)

This backend is intentionally not connected yet. The official provider's endpoint, required parameters, response structure, and field names must be confirmed from the API documentation and a sample response before configuring it. The service API requires credentials; never put the API key in frontend JavaScript or commit it.

## Local setup

1. Install Python 3.11+.
2. From this directory, create a virtual environment: `python -m venv .venv`, activate it, then `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and fill the official API endpoint, key, query parameters, and field mapping after verifying the API docs.
4. Run `uvicorn app.main:app --reload --port 8000`.
5. Check `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/api/facilities`.

## Environment variables

- `API_BASE_URL`: exact endpoint URL from official docs.
- `API_SERVICE_KEY`: issued key. Keep private.
- `API_KEY_PARAM`: key parameter name (defaults to `serviceKey`).
- `API_EXTRA_PARAMS`: JSON object of additional required query parameters.
- `API_FIELD_MAP`: JSON object mapping normalized field names to exact provider field names. Configure after reviewing a sample payload.

Normalized fields include facility_id, name, type, status, address, sido, sigungu, capacity, enrolled, latitude, longitude, wait_0..wait_5, wait_6_plus, wait_total, data_date.

## Security and data quality

- Request failures are sanitized before they are returned by the API; raw HTTP exceptions can contain query URLs and service keys.
- `API_FIELD_MAP` must be a JSON object mapping known normalized fields to non-empty strings.
- API credentials must stay server-side. Do not put keys in frontend code, repository files, chat, or email.
- Missing values remain null; do not treat blanks as zero wait.
- Waitlist totals are application counts and may not represent unique children across facilities.

## Tests

Run from the backend directory:

```bash
python -m unittest discover -s tests -v
```

The tests cover XML/JSON record flattening, alias mapping, numeric/null handling, age-bucket sums, field-map validation, and credential-safe HTTP error messages.

## Important

- This is a connector scaffold, not a successful live data connection.
- The API adapter does not guess endpoint paths, request parameters, or response field names.
- Verify provider terms and commercial reuse before public deployment.
- Keep existing known-good demo files intact until live data is validated.
