# Versioned legal-dong / administrative-dong crosswalk validator — 2026-11-23

## Scope and safety boundary

The new backend validator accepts normalized legal-dong → administrative-dong relationship rows and validates region references, types, provenance, version identifiers, and inclusive effective-date intervals. It supports many-to-many (M:N) relationships.

This is a **validation scaffold only**. It does not download/import official files, prove a jurisdictional or spatial relationship, calculate boundary overlap, assign facilities, create a geometric crosswalk, or authorize public/commercial reuse. No official region-code records are embedded in this change; tests use fictional IDs.

## Normalized row contract

- legal_region_id: existing validated region whose region_type is legal_dong
- admin_region_id: existing validated region whose region_type is admin_dong
- crosswalk_version: non-empty source/import version label
- valid_from: strict ISO date (YYYY-MM-DD), inclusive
- valid_to: strict ISO date or null (inclusive; null means open-ended)
- source_system: non-empty source name
- source_reference: HTTPS provenance URL without embedded credentials

Source region records are passed through the existing region validator. Codes and identifiers must be treated as strings to preserve leading zeroes. The validator does not join regions by display names.

## Validation behavior

- Aggregates malformed row and reference issues.
- Rejects missing IDs, unknown IDs, and incorrect source/target region types.
- Rejects malformed dates and end dates earlier than start dates.
- Rejects non-HTTPS provenance URLs and URLs containing credentials.
- Permits multiple legal regions to map to one administrative region and one legal region to map to multiple administrative regions.
- Within a crosswalk version, the same legal/admin pair cannot have overlapping inclusive effective periods; non-overlapping intervals are allowed.
- Returns normalized rows in deterministic order and does not mutate input.

## Acceptance criteria

- [x] M:N relationships represented without flattening or name-based joins.
- [x] Source and target IDs resolve to validated legal_dong/admin_dong records.
- [x] Date periods are strict, inclusive, and non-overlapping per pair/version.
- [x] Source provenance is required.
- [x] Output ordering is deterministic.
- [x] Tests run in repository CI after commit (#134).
- [ ] Official current code archives and crosswalk rows imported only after source-layout and reuse review.
- [ ] Spatial/area mapping and unresolved-case review remain separate future work.

## Test status

**PASS — GitHub Actions run #134:** 91 backend tests, 40 frontend tests, and JavaScript syntax checks passed for commit 2ee71fb4772b1082ecc38258ac5de156d123eac8. Direct local repository checkout tests were not run in this environment. https://github.com/sharehousegirls/childcare-map/actions/runs/45045057756

Code review found and corrected an issue where overlap diagnostics could report a normalized row index rather than the original input row index. Missing fields now emit explicit required-field issue codes; both fixes are covered by the CI run.

## Next steps

1. Recheck the current MOIS code-change board and obtain the current official archives/layout.
2. Confirm exact source-to-target field semantics for any official crosswalk file; do not infer them from filename.
3. Review attribution, redistribution and commercial-use terms for the exact archive.
4. Map official rows into this normalized contract and validate; retain unresolved cases.
5. Separately validate geographic boundaries, facility coordinate CRS/axis order, spatial assignment and coverage before dong-level waitlist aggregation.
