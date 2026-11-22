# Data model draft — 2026-11-22

Status: **partially implemented**. SQLite facility/snapshot/ingestion-run/unresolved-record storage exists in `backend/app/storage.py`; a normalized region validator/tree builder exists in `backend/app/regions.py`. Official region-code rows, canonical region hierarchy, M:N dong crosswalk, user features, migrations and API integration remain unimplemented. The waitlist API response, stable identifiers and service-specific reuse terms remain unverified.

## Design goals
- Preserve provider values and provenance; keep derived calculations separate.
- Treat facilities as canonical identities and store dated snapshots instead of overwriting history.
- Unknown/missing values stay null; never convert missing waitlist values to zero.
- Keep provider-reported totals separate from age-bucket sums and quality diagnostics.
- Version region mapping explicitly.
- Support free-first return-value features (saved regions, facilities, comparisons, filters, history) without requiring accounts in the first prototype.
- Never predict admission dates.

## Implemented subset (2026-11-22)

- `facility`: provider facility ID is currently the primary key; latest metadata is upserted.
- `facility_snapshot`: stores dated counts, reported/derived total and consistency diagnostic; unique per facility/run.
- `ingestion_run`: stores source, batch fingerprint and received/stored/flagged/unresolved counts.
- `unresolved_record`: keeps normalized rows with missing IDs or later duplicate IDs for review; raw provider payload is not saved.
- Same run ID + same fingerprint is idempotent; same run ID + different content is rejected.
- Snapshot updates are blocked by an append-only trigger. Deletes remain possible for a future verified retention policy.
- `backend/app/regions.py` validates normalized region records and builds deterministic trees; test data is synthetic only. It does not import official codes or perform an administrative/legal-dong crosswalk.
- **PASS:** 11 storage tests and `compileall` in an isolated local copy.
- **PASS:** GitHub Actions run #48 passed 26 repository tests for commit `396e30762bb3776eadeddd1715b0574bf0049ce4`.
- **PASS — GitHub Actions run #62:** 41 backend tests passed; frontend syntax and 9 saved-search tests also succeeded. https://github.com/sharehousegirls/childcare-map/actions/runs/44967776618
- **NOT RUN:** direct local repository checkout test run.

Not implemented: official canonical region hierarchy/code import, administrative/legal-dong crosswalk, internal facility IDs, source dataset registry, versioned region assignment, database migrations, failed-run/retry auditing, retention/backup, integration with provider/API routes, and production concurrency/load review.

## Proposed entities

### 1. region — canonical hierarchy
| Field | Purpose |
|---|---|
| region_id | Internal stable ID |
| source_region_code | Official code only after source verification; nullable |
| region_name | Official sourced name |
| region_type | sido, sigungu, admin_dong, legal_dong, eup, myeon, or ri |
| parent_region_id | Parent link; null for top-level |
| boundary_source / boundary_version | Boundary provenance, if available |
| valid_from / valid_to | Effective dates, when known |

Acceptance: no guessed region codes; hierarchy validated against current official files; legal/admin dong distinction preserved; names alone are not unique IDs. The validator currently applies a conservative parent-type contract that has not been checked against the full official dataset.

### Administrative-dong/legal-dong crosswalk (separate from the region tree)

Administrative-dong and legal-dong names/codes are not a reliable 1:1 relationship. Maintain a separate versioned crosswalk with explicit source/boundary provenance, mapping method, confidence/review status and valid dates. Do not join facilities or aggregate dong data by matching names alone. See `docs/region-code-validation-2026-11-22.md`.

### 2. facility — identity and attributes
| Field | Purpose |
|---|---|
| facility_id | Internal canonical ID |
| provider_facility_id | Provider code, normalized but retained as sourced |
| name / type / status | Provider-sourced identity attributes |
| address | Provider-sourced address |
| region_id | Verified canonical region association, nullable until resolved |
| latitude / longitude | Converted map coordinates only after CRS is verified |
| source_dataset_id / source_record_key | Provenance reference |

Acceptance: missing or duplicated provider IDs are flagged and preserved for review; records are not silently merged or discarded.

### 3. facility_snapshot — point-in-time values
| Field | Purpose |
|---|---|
| snapshot_id / facility_id | Snapshot and canonical facility relation |
| source_dataset_id / source_data_date | Source identity and provider's record date |
| collected_at | Actual retrieval timestamp, separate from source date |
| capacity / enrolled | Provider counts, nullable |
| wait_0 through wait_5 / wait_6_plus | Age buckets, individually nullable |
| wait_total_reported | Provider-reported total, nullable |
| wait_total_derived | Sum only when every bucket is present; otherwise null |
| quality_flags | Missing/duplicate ID, invalid count, total mismatch, stale/unknown date, CRS uncertainty, etc. |

Acceptance: snapshot is immutable after ingestion; provider total is never overwritten by derived total; explicit zero and unknown remain distinct.

### 4. ingestion_run — update audit
Track run ID, source/dataset, start/end, status, rows received/accepted/flagged, retry count and sanitized error summary. Never store service keys, request URLs containing keys, or raw exception strings that may expose secrets.

Acceptance: distinguish successful empty results from failed requests; safe diagnostics; retries do not create duplicate snapshots.

### 5. facility_region_assignment — mapping provenance
Track facility-to-region mapping, level (sido/sigungu/admin-dong/legal-dong), method (provider field/address/boundary spatial join), source/version, confidence/status and effective dates.

Acceptance: district-level fields are not presented as dong-level data. Dong assignment requires validated address or coordinate mapping and a documented boundary source/version.

### 6. user return-value features — MVP browser storage
- saved_region: canonical region ID, fallback label, saved timestamp.
- saved_facility: canonical facility ID, saved timestamp.
- saved_filter: query, type, zero-wait flag, selected region and timestamps.
- comparison: selected canonical region IDs and saved timestamp.

Use browser-local storage for the account-free prototype only. Explain that saved items are device/browser-local and may be cleared; do not claim cross-device sync. Version the storage format for migration. Do not store sensitive child/family information.

Acceptance: save/unsave, reload persistence, stale-ID handling, version migration and clear/reset control. Account/cloud sync is out of MVP and requires separate privacy/security design.

## Aggregation rules
- Aggregate total facility count separately from facilities with known waitlist values.
- Sum only known waitlist totals; label coverage (known waitlist facilities / all facilities).
- Average only facilities with known wait values; label the denominator and disclose incomplete coverage.
- Count zero-wait facilities only when the value is explicitly numeric zero.
- Keep provider record date and actual collection time separate; show missing/stale dates clearly.
- Regional comparisons use the same snapshot date or disclose mixed dates.
- Trend views must disclose incomplete coverage and avoid misleading changes from facility additions/removals or missing data.

## Geographic constraints
- Catalog field descriptions are not proof of the response schema. Verify exact fields from the official service spec and a redacted response.
- Validate coordinate reference system and axis order before map rendering/spatial joins. Existing notes suggest EPSG:5181/TM; verify against the exact API field before conversion.
- API regional granularity may be city/county/district. Legal dong and administrative dong differ; do not infer dong from a district name.
- Use boundary data only after source, license and redistribution conditions are reviewed and the boundary version recorded.

## Implementation gates
1. Schema gate: operation, parameters, response envelope, pagination, ID stability and null semantics confirmed.
2. Rights gate: API-specific terms, attribution, caching, public display, redistribution and commercial/advertising use confirmed.
3. Quality gate: sample validates IDs, numeric ranges, age buckets/total, dates, geography and CRS.
4. Storage gate: versioned migrations, indexes, retention/backup and idempotent snapshot ingestion tested. Current scaffold covers batch/idempotency only; migrations, retention, backup and API integration remain open.
5. UI gate: source/date labels, coverage, unknown values and stale state verified.
6. Release gate: accessibility, responsive layout, security, tests and deploy-readiness review completed; deployment requires owner approval.

## Next bounded work
Validate the initial region model against the current official MOIS code archives, then implement the canonical region loader/selector and separate versioned M:N dong crosswalk; do not hardcode an unverified code list. In parallel, obtain and validate the official API spec/sample and terms. Add schema migrations and ingestion failure/retry audit, then connect the snapshot-storage scaffold only after all API gates pass.
