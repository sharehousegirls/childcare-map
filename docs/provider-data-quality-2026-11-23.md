# Provider normalization data-quality safeguards — 2026-11-23

## Scope

A bounded improvement to the unconnected API normalization/storage scaffold. No API request, live data, credentials, schema assumption, or deployment was added.

## Changes

- Invalid non-missing numeric input is normalized to null and reported as `invalid_numeric:<field>`. Blank, `-`, and `--` remain unknown and are not treated as malformed.
- Geographic latitude and longitude values outside the standard geographic ranges are nullified and flagged as `coordinate_out_of_range:latitude` or `coordinate_out_of_range:longitude`. This check is enforced by both provider normalization and the SQLite storage boundary, so records passed directly to storage receive the same guard. A one-sided coordinate pair is flagged as `coordinate_pair_incomplete`; two absent coordinates remain unknown without an incomplete-pair flag. These checks are only valid when values are actual geographic coordinates; they do **not** validate CRS, axis order, accuracy, or address alignment. Do not map projected EPSG:5181 x/y values directly to latitude/longitude.
- Incomplete age buckets remain unknown; `wait_age_buckets_incomplete` is retained in row-level quality flags instead of filling missing buckets with zero.
- Provider-reported `wait_total_reported` and age-bucket-derived `wait_total_derived` are now separately exposed. Existing `wait_total` behavior is preserved for display/aggregation: use the reported total if present, otherwise the complete age-bucket sum. `wait_total_consistent` remains null when comparison is impossible and flags a mismatch when both totals exist but disagree.
- Missing/duplicate facility-ID diagnostics are also included in the row-level `quality_flags` array.
- SQLite storage preserves a provider-reported total as reported (null remains null) and retains provider diagnostic flags, while computing its own age-bucket derived total and consistency state.

## Acceptance criteria

- Missing/sentinel values stay null and do not become zero.
- Invalid numeric counts are not silently treated as missing; they receive a field-specific quality flag.
- Coordinates outside geographic bounds are not retained as normalized latitude/longitude, even when normalized rows are passed directly into SQLite storage.
- A partial latitude/longitude pair is flagged at both normalization and storage boundaries; two missing coordinates remain unflagged.
- Reported and derived waitlist totals are not conflated in snapshots.
- Quality flags survive the provider-to-storage boundary.

## Verification

- **PASS — GitHub Actions run #158:** 103 backend tests, 40 frontend tests, and frontend JavaScript syntax checks succeeded on commit `fcea52b602f5ced3fbd9254bcb77da4fd0d6ad20`. https://github.com/sharehousegirls/childcare-map/actions/runs/45101632033
- **PASS — GitHub Actions run #167 (coordinate validation follow-up):** 108 backend tests, 40 frontend tests, and frontend JavaScript syntax checks completed successfully. https://github.com/sharehousegirls/childcare-map/actions/runs/45112984412
- **NOT RUN:** direct local checkout tests. GitHub DNS resolution failed when attempting `git clone`; CI is the source-checkout test evidence.
- **NOT RUN:** live API/schema, CRS, license/redistribution, browser, responsive, and assistive-technology checks.

## Review notes

The normalized total remains backward-compatible for consumers. The additional provenance fields and flags are additive. The coordinate guard is a basic geographic-range check only and must not be used as evidence that coordinates are accurate or in the correct CRS.
