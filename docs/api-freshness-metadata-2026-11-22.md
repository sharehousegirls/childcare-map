# API freshness metadata — 2026-11-22

## Change
The `GET /api/facilities` envelope now includes a `meta` object. It records the backend collection timestamp in UTC and the distinct provider record dates found in normalized facility rows.

Fields:
- `collected_at`: backend retrieval timestamp, timezone-aware ISO 8601 normalized to UTC.
- `source_data_date`: one date only when every dated record resolves to the same non-empty value; null for mixed or missing dates.
- `source_data_dates`: sorted distinct non-empty provider date strings. These are preserved as supplied; their format/meaning still requires source-spec verification.
- `mixed_source_data_dates`: true when more than one distinct date appears.
- `records_with_source_data_date` / `records_without_source_data_date`: coverage counts.

The frontend checks the API envelope record count, displays source-date status and the collection timestamp in browser-local time, and retains the exact UTC timestamp in the status tooltip. If metadata is absent, it falls back to facility-level dates without claiming a collection time.

## Acceptance criteria
- Collection time is separate from provider source dates.
- Collection time is timezone-aware and emitted in UTC.
- Mixed source dates never collapse to one date.
- Missing dates remain missing and are counted.
- An API response whose `count` does not match `facilities.length` is rejected by the frontend and falls back to the clearly labeled demo.
- Existing API consumers can continue reading `source`, `count`, and `facilities`; metadata is additive.

## Validation
- Unit tests added for single date, mixed dates, missing dates, UTC normalization, and rejecting naive timestamps.
- GitHub Actions is the authoritative repository test run; record its result after the code commits.
- Manual browser and responsive testing are not performed in this change.

## Limitation
This is a collection-time indicator, not a freshness SLA. No provider freshness threshold is assigned until the official API's date semantics and update frequency are confirmed.
