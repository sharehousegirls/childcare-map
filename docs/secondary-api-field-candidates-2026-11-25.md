# Secondary API field-name candidates — 2026-11-25

## Purpose and evidence boundary

The official catalog for dataset **15101154 (한국사회보장정보원_어린이집별 기본정보 조회)** was re-opened. It confirms the *conceptual* facility identity, location, facility/date metadata, and waitlist categories (ages 0–5, 6+, and total), but does not expose a verified service-specific XML field map in the accessible catalog view.

Two secondary API-index pages surfaced candidate element names. These are discovery hints only; neither replaces the official technical document or a redacted successful payload.

- Official catalog: https://www.data.go.kr/data/15101154/openapi.do
- Secondary field-name listing: https://infosnake.net/services/opendata/?id=15101154
- Secondary catalog listing: https://gongapi.kr/d/15101154

## Candidate names from secondary listings (UNVERIFIED)

| Normalized field | Candidate provider tag |
|---|---|
| facility_id | `stcode` |
| name | `crname` |
| type | `crtypename` |
| status | `crstatusname` |
| address | `craddr` |
| capacity | `crcapat` |
| enrolled | `Crchcnt` |
| latitude | `La` |
| longitude | `Lo` |
| data_date | `datastdrdt` |
| wait_0 … wait_5 | `ew_cnt_00` … `ew_cnt_05` |
| wait_6_plus | `ew_cnt_m6` |
| wait_total | `ew_cnt_tot` |

Do not treat these spellings, case, nesting, or semantics as verified. Secondary listings can be stale, incomplete, or mismatched to a specific API revision.

## Mapping and safety rules

- Do not add these candidate tags to automatic aliases or configure `API_FIELD_MAP` from this table.
- Live normalization must continue to use explicit mappings only and fail closed until the required identity, source date, and waitlist fields are configured.
- Confirm exact XML tag casing, response envelope, operation, paging, row limits, errors, blank/null values, stable ID semantics, and total-vs-age-bucket meaning from the official technical document and a redacted payload.
- `La`/`Lo` are only coordinate-name candidates. Confirm units, CRS, axis order, and whether they are actual geographic coordinates before map placement.
- Keep missing waitlist counts unknown/null. Do not convert blanks to zero.
- Preserve provider-reported total separately from age-derived totals and compare only when all age buckets are present.
- Review commercial display, caching, attribution, and redistribution conditions separately; catalog-level reuse wording is not blanket service-specific clearance.

## Regression guard

Added `test_secondary_schema_candidates_are_not_accepted_without_explicit_mapping` in `backend/tests/test_provider.py`. A fixture containing the secondary candidate names is normalized with no field map and `allow_aliases=False`; identity, source date, and waitlist values remain unknown. This test is a fail-closed guard, not proof that the candidates are correct.

## Next verification gate

1. Obtain the official service-specific technical document and a redacted response.
2. Compare the response tags and nesting with these candidates; correct or discard every mismatch.
3. Verify paging and provider ID uniqueness across the full batch.
4. Validate waitlist counts, total semantics, source dates, coordinate CRS/axis order, and null conventions.
5. Review reuse terms and approved access before a bounded offline mapping-validation batch.
6. Keep live requests, ingestion, public data display, and raw-response redistribution disabled until these gates are satisfied.
