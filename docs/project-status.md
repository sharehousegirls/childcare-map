# Project status — 2026-11-23

## Current phase
**Data-source and geography validation.** Live API connection remains gated on verified official schema, credentials, quality, and service-specific reuse terms.

## Completed foundation
- Responsive static prototype: region cards, facility search, type filter, explicit zero-wait filter.
- Browser-local saved searches: store, restore and delete region/search/type/zero-wait filters (up to 20, no account or server sync).
- Browser-local saved regions: store, select and delete individual region labels (up to 20; duplicate region labels prevented). Current saved values are display names, not official stable region codes.
- Browser-local saved facilities: save/load/delete by exact facility ID (up to 50). Demo IDs are fictional; records without IDs cannot be saved.
- FastAPI adapter scaffold with server-side credential configuration, XML/JSON parsing, normalized fields, health and facility endpoints.
- Provider error sanitization and field-map validation.
- Live API normalization fails closed until facility ID, name, source date and waitlist total/all age-bucket mappings are explicitly configured; live normalization no longer guesses from aliases for unmapped fields.
- Provider normalization now retains reported and age-bucket-derived waitlist totals separately, flags invalid numeric/geographic coordinate values, incomplete coordinate pairs and incomplete waitlist buckets, and propagates quality flags into SQLite snapshots. SQLite independently rejects out-of-range geographic coordinates and flags partial coordinate pairs at its ingestion boundary. This remains a disconnected scaffold, not live-data validation.
- Waitlist-total consistency diagnostic; missing/duplicate facility-ID flags (batch-level only).
- Backend unit-test evidence and CI evidence documented in the security review.
- Official source inventory and integration plan.
- Draft relational model for region hierarchy, facility identity, snapshots, ingestion-run audit, region mapping provenance, and browser-local saved features.
- File-backed SQLite snapshot-storage scaffold: facility metadata, append-only snapshots, ingestion-run summaries, and unresolved-record review table; idempotent batch handling and quality flags. Not yet wired to the API route.
- Initial normalized region validator/tree builder in `backend/app/regions.py`; supports separate administrative/legal dong types and checks duplicates, parent links, cycles and active-status contradictions. Cycle detection and deterministic tree sorting are iterative to avoid recursion-depth failures on malformed input. Synthetic fixtures only; no official code data imported.
- Versioned legal-dong → administrative-dong crosswalk validator scaffold in `backend/app/region_crosswalk.py`; supports M:N relationships, region type/reference checks, HTTPS provenance, strict effective dates and non-overlapping periods per pair/version. Synthetic rows only; no official crosswalk or spatial mapping imported.
- Region source manifest validator in `backend/app/region_manifest.py` records source/version/date/digest/attribution and reuse review; it provides separate public-redistribution and commercial-use gates. SHA-256 verification streams local files in 1 MiB chunks. The gate is not yet wired to an importer.

- Regional aggregation is extracted into `regional-summary.mjs`: missing wait counts stay null, partial totals/coverage are explicit, zero-wait counts only explicit zero, and live region labels are province-first.

## Blockers / not yet verified
- Daegu facility-metadata development API application is pending; it does not itself provide the waitlist fields.
- Nationwide waitlist dataset 15101154 application/approval is not confirmed.
- Credentials are not available; no live request has been made.
- Official API endpoint, operation, request parameters, pagination, response/error envelope, exact field names, ID stability, null semantics and row limit need the service specification and a redacted sample.
- Service-specific attribution, caching, display, redistribution, commercial and advertising conditions are not cleared.
- MOIS's website copyright policy says MOIS-owned material may be freely reused without separate permission only when marked KOGL Type 1, with source attribution; unmarked material requires prior consultation. The KOGL mark on the exact administrative-code ZIP has not been verified, so the ZIP reuse gate remains closed. Official policy: https://mois.go.kr/frt/sub/a08/copyrightPolicy/screen.do
- Current official administrative/legal-region code files have not been imported or validated.
- The Childcare Portal FAQ (Q12) confirms its regional facility-type/count query is limited to 시·군·구, not dong. This does not conclusively rule out a derived dong aggregation from facility-level rows; validated coordinates, boundaries, deduplication, and coverage are required.
- The Portal FAQ (Q13) reports EPSG:5181 TM coordinates for the childcare map data it describes; exact feed CRS and axis order still require confirmation. FAQ Q10 notes legal-dong/administrative-dong lookup mismatches.
- Reviewed geography constraints and derived-dong acceptance criteria in `docs/region-granularity-coordinate-review-2026-11-22.md`. The normalized parent contract remains simplified and unverified against full official files. The M:N legal-dong/admin-dong crosswalk validator exists as a scaffold using synthetic rows only; no official crosswalk or spatial mapping is imported. Coordinate CRS and axis order still require source validation.

## Known limitations
- Demo values are fictional and must not be interpreted as current real waitlist data.
- No actual nationwide facility/waitlist ingestion.
- No official canonical region hierarchy imported or dong-level mapping implemented. Dong-level waitlist statistics must be derived only from uniquely identified facility rows and verified spatial mapping; the portal FAQ does not document a direct dong-level query for its regional facility-type/count query. Region and crosswalk validators are not wired into API/UI. Crosswalk validation does not prove geographic relationships.
- SQLite snapshot storage exists as an isolated scaffold, but it is not integrated with API ingestion or exposed through routes; no region hierarchy, real map, facility detail page, persistent saved facilities, server-backed comparisons or trend UI yet.
- Saved searches are browser-local only; up to 20. They do not sync across devices/accounts, and browser storage can be cleared or unavailable.
- Saved regions are also browser-local and currently store region-name strings from the current option list; they are not canonical official IDs and may become stale after region-code/name changes. No migration or cross-device sync yet.
- Saved facilities are browser-local, capped at 50 and matched by exact ID; source-ID changes can make bookmarks stale. No account or device sync.
- Storage schema has no versioned migrations, failed-run/retry recording, retention/backup policy or production concurrency/load review.
- Automated data refresh, SEO, production hardening and deployment are not ready.
- Complaint/violation/administrative-history feature remains deferred until all other scope is complete and owner review is requested.

## Next priorities
- Import the current official region-code archives only after source/layout and reuse review; preserve codes, keep administrative/legal-dong records separate, map crosswalk rows through the validator, and retain unresolved cases for manual review.
- Validate facility coordinates and EPSG:5181 transformation using a redacted official sample before map rendering.
- Prototype derived dong aggregation with deduplication, mapping coverage, null handling, and explicit UI labeling; do not claim a direct official dong query.

## Verification
- **PASS — GitHub Actions run #167 (coordinate validation follow-up):** 108 backend tests, 40 frontend tests, and JavaScript syntax checks passed after the provider and storage coordinate-pair validation changes. https://github.com/sharehousegirls/childcare-map/actions/runs/45112984412
- **PASS — GitHub Actions run #136 (CI action runtime update):** 91 backend tests, 40 frontend tests, and JavaScript syntax checks passed on commit `a2b04f88a10a93ddc7ae79886282d449c97af72a`; all three action majors were upgraded to v7. No Node 20 deprecation warning appeared in this run. https://github.com/sharehousegirls/childcare-map/actions/runs/45056638594

- **PASS — GitHub Actions run #109:** 68 backend tests (including 23 region-source-manifest tests), 28 frontend tests (8 regional summary, 11 saved-region, 9 saved-search), and all JavaScript syntax checks succeeded. https://github.com/sharehousegirls/childcare-map/actions/runs/45004001134
- **PASS (isolated harness):** 23 region-source-manifest tests and `py_compile` passed. Exact GitHub checkout was not available locally; repository CI run #109 is the source-checkout evidence.
- **PASS — GitHub Actions run #105:** 45 backend tests, 28 frontend tests (8 regional summary, 11 saved-region, 9 saved-search), and all four JavaScript syntax checks passed for commit `437384c3f430a7498f7ba7f091a993dd52a0d8bc`. https://github.com/sharehousegirls/childcare-map/actions/runs/44995019954
- **PASS (reported/evidence documented):** 15 backend unit tests in an isolated harness using source/test blob hashes verified against the repository; GitHub Actions passed for commit ec14fb6a938820cb1181ada6e3e26101fa3201e4. See docs/backend-security-review-2026-11-21.md.
- **PASS (isolated local copy):** 11 SQLite storage unit tests and Python compileall; local tests were not run against a repository checkout.
- **PASS — GitHub Actions run #48:** 26 repository tests passed against the repository checkout for commit 396e30762bb3776eadeddd1715b0574bf0049ce4 (workflow: https://github.com/sharehousegirls/childcare-map/actions/runs/44947857967).
- **NOT RUN:** direct local repository checkout test run in this environment.
- **PASS — GitHub Actions run #57:** backend unit-test step and frontend saved-search test step both succeeded for commit e3dd6039132e545e2512f4a4162f41d7a2ad277a (https://github.com/sharehousegirls/childcare-map/actions/runs/44957889342; saved-search suite at that point had 8 tests).
- **PASS (isolated local harness):** 9 saved-search module tests passed after adding read-error protection; direct repository checkout was unavailable.
- **PASS — GitHub Actions run #58:** backend unit tests, app.js/saved-searches.mjs syntax checks, and frontend saved-search test steps succeeded for commit 79339ad982c108143eae8623cc97b3ac05a54e0e (https://github.com/sharehousegirls/childcare-map/actions/runs/44958036482).
- **PASS — GitHub Actions run #82:** 45 backend tests passed; frontend JavaScript syntax checks and 9 saved-search tests also succeeded. The new 1,500-node malformed-cycle test passed. https://github.com/sharehousegirls/childcare-map/actions/runs/44976683017
- **PASS (isolated local Node harness):** 11 saved-region module tests and `node --check saved-regions.mjs`.
- **PASS — GitHub Actions run #98:** 45 backend tests, JavaScript syntax checks, 9 saved-search tests, and 11 saved-region tests passed for code commit `1d8825a5560e9100774494d0234bf53bbacd6657`. https://github.com/sharehousegirls/childcare-map/actions/runs/44985738434
- **NOT RUN:** direct browser interaction, mobile viewport, screen-reader check.
- **FAIL — Runs #80/#81:** iterative cycle-detection refactor exposed a tree-sort queue bug (`dict.sort`); corrected in commit `647460e9fe2c0d17adc9c9a379f5960b32678b54` and verified by run #82.
- **FAIL — Run #73:** a temporary malformed test-file edit caused a Python syntax error; corrected in commit `eb116b5555b6ef70192302c54b8609eddfa0b658`, verified by run #74.
- **NOT RUN:** browser interaction, accessibility, responsive manual test.
- **BLOCKED:** live API validation, nationwide data completeness, real map/geospatial validation, end-to-end integration.
- **WARN:** GitHub Actions reports Node 20 deprecation notices for checkout/setup-python actions; run is successful, but workflow action maintenance should be scheduled.
- **NOT RUN:** deployment; requires owner approval.


## Next priorities
1. Obtain nationwide waitlist API access, official specification, redacted response, and complete reuse/attribution review.
2. Download/version the current MOIS administrative and legal-dong code files, validate status/parent fields, and confirm the simplified region rules against the full official data; do not import unverified codes.
3. Implement a separate versioned M:N administrative-dong/legal-dong crosswalk using boundary/jurisdiction evidence; never join by name alone.
4. Add schema versioning/migrations and ingestion failure/retry audit; connect the snapshot-storage scaffold only after API/schema/rights gates pass.
5. Add real map, facility detail, region comparison and filtering against validated data.
6. Saved regions, searches and facilities are browser-local; extend to canonical region IDs after official code import. Continue with comparisons, snapshot history and trends.
7. Add automated refresh/recovery, SEO, accessibility, operational/security review.
8. Conduct deploy-readiness review; deploy only with owner approval.

## Acceptance rules
- Missing is not zero; zero-wait requires explicit zero.
- Waitlist application counts are not necessarily unique children.
- No admission-date prediction.
- Show source, record date, collection time, coverage and quality flags.
- Keep demo and live states unmistakably distinct.
- Never commit credentials or expose them in logs/errors.
- Verify source terms before public redistribution or commercial use.


## Saved facilities — 2026-11-22
- **PASS — commit `f0a12d30`, GitHub Actions run #114:** 68 backend tests, 40 frontend tests (8 regional summary, 11 saved regions, 9 saved searches, 12 saved facilities), and 5 JavaScript syntax checks succeeded. https://github.com/sharehousegirls/childcare-map/actions/runs/45013742067
- **PASS — documentation commit `8760f731`, run #115:** project README/status/feature documentation changes also passed the same CI workflow. https://github.com/sharehousegirls/childcare-map/actions/runs/45013812845
- **PASS — isolated Node 22 harness:** 12 saved-facility unit tests also ran independently before commit.
- **NOT RUN:** manual browser interaction, responsive viewport and screen-reader checks.
- Facility card buttons save by dataset ID, load by exact ID (no name-only fallback), and delete. Browser-local only, 50-item cap.


## API freshness metadata — 2026-11-22
- Added additive `meta` to `GET /api/facilities`: timezone-aware UTC collection time, distinct provider record dates, single-date value only for unambiguous dates, mixed-date flag and dated/undated record counts.
- Frontend displays source date and browser-local collection time separately; exact UTC collection timestamp is available in the status title. It rejects a mismatched API count and falls back to the labeled demo.
- **PASS — GitHub Actions run #123:** 73 backend tests (68 existing + 5 freshness-metadata tests), 40 frontend tests, and JavaScript syntax checks passed on the repository checkout. https://github.com/sharehousegirls/childcare-map/actions/runs/45023627178. Runs #121–#123 also passed for the documentation commits.
- **NOT RUN:** direct local checkout test run, manual browser interaction, mobile viewport, and screen-reader checks. The dynamic data-status element now uses `role=status` and `aria-live=polite`; manual assistive-technology verification is still pending.
- No provider freshness SLA is inferred from collection time. Source date format and semantics remain pending official API schema/sample.
- Implementation note: `docs/api-freshness-metadata-2026-11-22.md`.


## 2026-11-23 incremental milestone — CI action runtime modernization
- Updated `actions/checkout`, `actions/setup-python`, and `actions/setup-node` from v4/v5 to v7; the run completed without the previous Node 20 runtime deprecation warning.
- **PASS — GitHub Actions run #136:** 91 backend tests, 40 frontend tests, and JavaScript syntax checks passed. https://github.com/sharehousegirls/childcare-map/actions/runs/45056638594

## 2026-11-23 incremental milestone — crosswalk validation scaffold

- Added a backend-only normalized crosswalk validator for legal-dong → administrative-dong M:N links.
- Enforces source/target region types and IDs, provenance URL, version label, strict inclusive dates, and non-overlapping intervals for each pair/version.
- Added synthetic unit tests covering M:N, missing/invalid references, dates, overlaps, URL credentials, immutability, and deterministic sorting.
- No official region-code data was downloaded or imported. No live API, map, spatial crosswalk, or deployment was connected.
- **PASS — GitHub Actions run #134:** 91 backend tests, 40 frontend tests, and JavaScript syntax checks passed. A code-review correction made overlap issues retain original input row indexes and missing fields use explicit required-field errors; the fix was verified in the same run.


## 2026-11-23 incremental milestone — crosswalk open-ended interval regression
- Added a regression test ensuring a null valid_to (open-ended) interval overlaps and rejects any later interval for the same legal/admin pair and version.
- **PASS — GitHub Actions run #138:** 92 backend tests, 40 frontend tests, JavaScript syntax checks passed. https://github.com/sharehousegirls/childcare-map/actions/runs/45067435394
- **PASS — GitHub Actions run #139:** README verification-note update also passed the full CI workflow. https://github.com/sharehousegirls/childcare-map/actions/runs/45067529233
- **NOT RUN:** direct local repository checkout tests; manual browser and assistive-technology review remain outstanding.


## 2026-11-23 incremental milestone — crosswalk provenance URL hardening
- Tightened the HTTPS provenance validator to reject hostnames containing whitespace/backslashes and malformed or out-of-range ports, in addition to credentials and non-HTTPS schemes.
- Added two regression tests for whitespace in hostnames and port 99999.
- **PASS — GitHub Actions run #141:** validator change passed the existing suite. https://github.com/sharehousegirls/childcare-map/actions/runs/45079211694
- **PASS — GitHub Actions run #142:** 94 backend tests, 40 frontend tests, and JavaScript syntax checks passed with the new regression tests. https://github.com/sharehousegirls/childcare-map/actions/runs/45079217801
- Direct local checkout tests and manual browser/accessibility checks remain **NOT RUN**.


## 2026-11-23 incremental milestone — manifest URL hardening and official API schema evidence
- Hardened the region-source manifest HTTPS URL validator: reject host whitespace/backslashes and malformed or out-of-range ports, while preserving existing HTTPS, hostname, and credential checks.
- Added two regression tests for a whitespace hostname and an out-of-range terms URL port.
- **PASS — GitHub Actions run #147:** URL-hardening code commit passed.
- **PASS — GitHub Actions run #148:** 96 backend tests, 40 frontend tests, and JavaScript syntax checks passed with the regression tests included. https://github.com/sharehousegirls/childcare-map/actions/runs/45090277903
- Reviewed the official data.gov catalog for nationwide dataset 15101154. Its catalog lists age waitlist fields (0–5, 6+, total), facility metadata and a data date, with XML, LINK, real-time update metadata, unrestricted catalog reuse, and catalog last-modified date 2025-08-20. This confirms catalog-described fields only; exact XML tags and payload schema remain unverified.
- Official Childcare API guide confirms that service specifications on API detail pages contain service URLs, operations, request/response definitions and examples. Policy confirms the development-account result cap is 50 rows and operating accounts require separate approval, expected traffic, and renewal after 12 months.
- Added \`docs/api-schema-verification-2026-11-23.md\` with a candidate field mapping and acceptance checklist. No API request, credentials, live data, or deployment was added.
- **NOT RUN:** direct local checkout tests and browser/accessibility checks remain outstanding.


## 2026-11-23 incremental milestone — provider normalization quality

- Invalid numeric values are nullified and flagged; blank/sentinel values remain unknown.
- Latitude/longitude outside geographic ranges are nullified and flagged. This is only a bounds check; CRS/axis order remains unverified and projected values must not be mapped as geographic coordinates.
- Provider-reported and age-derived waitlist totals are retained separately; existing effective-total behavior remains backward-compatible. Mismatch/incomplete-age and facility-ID quality flags are surfaced and persisted.
- **FAIL — GitHub Actions runs #156/#157:** an intermediate SQL schema typo caused test setup errors; corrected before final verification.
- **PASS — GitHub Actions run #158:** 103 backend tests, 40 frontend tests and JavaScript syntax checks passed. https://github.com/sharehousegirls/childcare-map/actions/runs/45101632033
- **NOT RUN:** direct local repository tests (GitHub DNS prevented clone), live API/schema/CRS/license checks, browser/manual responsive/accessibility checks.
- Implementation notes: [provider data-quality safeguards](provider-data-quality-2026-11-23.md).


## 2026-11-23 incremental milestone — live field-mapping fail-closed gate

- Added a pre-request mapping gate requiring explicit facility ID, name, and provider data date, plus either the reported waitlist total or all seven age buckets.
- Live normalization uses only explicitly mapped fields; candidate aliases remain available only in compatibility/unit-normalization paths and are not treated as official schema evidence.
- This prevents accidental field guessing but cannot prove configured tags are correct. Official service specification and a redacted sample are still required.
- **NOT RUN:** no live API request, schema sample, CRS, or redistribution/commercial review was performed.
- New regression tests cover missing mapping, valid total/complete age mapping, and alias fallback disabled for live normalization.


## 2026-11-23 incremental milestone — fail-closed live field mapping verification

- **FAIL — GitHub Actions run #175:** the first commit of the mapping gate reached 111 backend tests but five errors were caused by test imports missing the new helper/constants. Frontend steps were skipped because the backend step failed. Failure evidence: https://github.com/sharehousegirls/childcare-map/actions/runs/45125173484
- Corrected the test imports in follow-up commit `eae2687e05170edf9a21fb42bd85c56738803ff8`.
- **PASS — GitHub Actions run #176:** 111 backend tests, 40 frontend tests and JavaScript syntax checks passed on the corrected test commit. https://github.com/sharehousegirls/childcare-map/actions/runs/45125220339
- **NOT RUN:** local checkout tests, live API requests, official schema/CRS/reuse review, and manual browser/responsive/accessibility checks.
