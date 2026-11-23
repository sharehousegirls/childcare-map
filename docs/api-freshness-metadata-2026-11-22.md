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

## Strict source-date diagnostics — 2026-11-23

The metadata helper now adds:
- `records_with_parseable_source_data_date`: non-empty provider date strings that match the strict `YYYY-MM-DD` format and are valid calendar dates.
- `records_with_unparseable_source_data_date`: non-empty strings not accepted by that strict parser (including other formats and invalid calendar dates).
- `source_data_date_earliest` and `source_data_date_latest`: minimum/maximum among parseable dates only; null when no valid ISO date exists.

Raw non-empty values remain in `source_data_dates` for audit. Missing values continue to be counted separately and are not classified as unparseable.

These fields are parseability diagnostics only. Because the provider's source-date format/semantics and update cadence remain unverified, the API does not label records fresh or stale and does not apply an age threshold. No date is synthesized from collection time.

## Acceptance additions

- Strict ISO date diagnostics do not rewrite raw source-date strings.
- Invalid calendar dates and non-ISO strings count as unparseable, not as missing.
- Earliest/latest values use parseable calendar dates only.
- No freshness SLA or stale/fresh label is inferred.

Test cases cover mixed valid, non-ISO, invalid-calendar, and missing date values. GitHub Actions result is recorded in project status after the run completes.


## Source-date coverage ratios — 2026-11-23

Added two additive diagnostics to `GET /api/facilities` metadata:
- `source_data_date_coverage_ratio`: non-empty provider source-date records divided by all facility records. Invalid-but-present date strings count as present; missing/blank dates do not. Rounded to four decimals; null for an empty record set.
- `source_data_date_parseability_ratio`: strict valid `YYYY-MM-DD` dates divided by non-empty source-date records. Invalid formats/calendar dates count against parseability; missing values are excluded from this denominator. Rounded to four decimals; null when no non-empty source date exists.

These ratios are coverage/format diagnostics, not freshness indicators. They do not establish how recent a facility record is, the provider update SLA, or the semantic correctness of the date field. No stale/fresh threshold is applied.

Acceptance:
- all valid dated records yield 1.0 for both ratios;
- invalid and missing dates affect the appropriate denominator only;
- empty batches return null for both ratios, avoiding a misleading zero-percent claim;
- raw dates and existing metadata remain unchanged.


## Validation note — 2026-11-23

- **PASS (isolated harness):** 7 metadata-helper tests and Python compilation passed against a temporary copy of the helper/module and test cases. This is not a full repository checkout or backend-suite run.
- **NOT RUN:** repository checkout test suite. GitHub commit status queries returned no status entries, so CI is unverified for this change.


## Ratio unit and duplicate records — 2026-11-23

The source-date coverage and parseability ratios are calculated per normalized response record (row), not per unique facility ID. They do not deduplicate records. If a batch contains duplicate facility IDs with different or missing dates, those rows each contribute to the denominator; the ratio can therefore differ from unique-facility coverage. Provider duplicate-ID diagnostics are separate, and duplicates should be resolved or explicitly reviewed before interpreting these ratios as facility coverage.

Acceptance: a batch with three rows, two dated rows, and a repeated facility ID yields record-level coverage '0.6667' and parseability '1.0' when both dated rows have valid ISO dates. A regression test now locks this behavior.
