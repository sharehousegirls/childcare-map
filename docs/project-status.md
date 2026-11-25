# Project status — 2026-11-25

## Current phase
**Data-source and geography validation, with frontend source-date freshness diagnostics.** Live API connection remains gated on verified official schema, credentials, quality, and service-specific reuse terms.

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
- Region selector options are grouped by the existing parent display label with native optgroups and Korean sorting; child display labels may omit a repeated parent prefix while the selected value remains the full region name. This is not an official code-backed hierarchy and does not add dong navigation.
- Saved-region comparison cards show current facility count, wait total, average per known facility, explicit zero-wait facility count and live-data coverage when valid. Demo metrics are labeled fictional; partial totals and ambiguous/stale region-name matches are not presented as complete comparisons.

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
- Saved regions are also browser-local and currently store region-name strings from the current option list; they are not canonical official IDs and may become stale after region-code/name changes. No migration or cross-device sync yet. Saved-region comparison is also name-based and reflects the current dataset only; it is not a historical snapshot or server-backed comparison.
- Saved facilities are browser-local, capped at 50 and matched by exact ID; source-ID changes can make bookmarks stale. No account or device sync.
- Storage schema has no versioned migrations, failed-run/retry recording, retention/backup policy or production concurrency/load review.
- Automated data refresh, SEO, production hardening and deployment are not ready.
- Complaint/violation/administrative-history feature remains deferred until all other scope is complete and owner review is requested.

## Next priorities
- Import the current official region-code archives only after source/layout and reuse review; preserve codes, keep administrative/legal-dong records separate, map crosswalk rows through the validator, and retain unresolved cases for manual review.
- After official region IDs are verified, replace display-name selector values with canonical IDs and a hierarchy; plan a compatibility migration for browser-local saved regions/searches.
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

## Latest bounded change (2026-11-23)
- `API_FIELD_MAP` provider-field values are trimmed and duplicate source-field assignments are rejected before a live request, reducing accidental reuse of one XML tag for multiple normalized fields. This guard does not confirm that mapped tags exist in the official schema. **PASS — GitHub Actions runs #179 and #183:** 113 backend tests, 40 frontend tests, and JavaScript syntax checks passed. Run #179 validates the code/test commit; #183 validates the final status-document commit. Local checkout tests remain NOT RUN.

## 2026-11-23 bounded milestone — strict source-date parseability diagnostics

- Added strict calendar-date diagnostics to `GET /api/facilities` metadata. Only valid `YYYY-MM-DD` values count as parseable; non-ISO and invalid calendar values remain in the raw date list and count as unparseable. Missing values remain separate.
- Added parseable/unparseable counts and earliest/latest parseable dates. This is additive metadata and does not change facility rows or the frontend.
- No stale/fresh label, SLA, or threshold is assigned because the official source-date format/meaning and update cadence remain unverified.
- **PASS — GitHub Actions run #187:** Backend 114 test methods, Frontend 40 tests, and JavaScript syntax checks succeeded after code/test commits. Run: https://github.com/sharehousegirls/childcare-map/actions/runs/45158598207
- **PASS — GitHub Actions runs #188 and #189:** freshness documentation and README commits succeeded. Run #188: https://github.com/sharehousegirls/childcare-map/actions/runs/45158630883; Run #189: https://github.com/sharehousegirls/childcare-map/actions/runs/45158643824
- **NOT RUN:** local checkout tests, live API requests, manual browser/responsive/accessibility review.
- Review: strict date parsing is bounded and non-destructive; raw values are retained, invalid dates are not silently repaired, and no new dependency or frontend behavior was introduced.
- Next priorities remain official API approval/specification and redacted sample, terms/redistribution review, schema/date/CRS validation, then nationwide ingestion and map. No live data or deployment.


## 2026-11-23 incremental milestone — source-date coverage ratios
- Added two additive `GET /api/facilities` metadata ratios: non-empty source-date coverage across facility rows, and strict ISO-date parseability among non-empty date strings. Both are rounded to four decimals; coverage is 0.0 for a non-empty batch with no dates, parseability is null when there are no dated rows, and both are null for an empty batch.
- Existing raw source-date values, earliest/latest parseable dates, and collection timestamps are unchanged. Ratios are not freshness/SLA claims.
- Added regression coverage for fully parseable dates, mixed valid/invalid/missing dates, all-missing dates, and empty batches.
- **PASS — isolated harness:** 7 copied `build_facility_meta` unit tests passed and `py_compile` passed. This validates the helper logic only, not a repository checkout or full suite.
- **CI: NOT RUN / UNVERIFIED** — repository tests were not executed locally, and this run's GitHub Actions status could not be retrieved with the available connector.
- **NOT RUN:** direct local checkout tests, live API/schema/CRS/reuse review, and manual browser/accessibility checks.
- Review: additive metadata only; no new dependency, frontend behavior, credentials, live API calls, or deployment.


## 2026-11-23 milestone — record-level source-date ratios and verified CI

- Clarified that source-date coverage/parseability ratios are calculated per response record (row), not per unique facility ID; duplicate IDs are not deduplicated by these ratios and must be reviewed separately before interpreting them as facility coverage.
- Added a regression test with three rows, two dated rows, and a repeated facility ID: coverage 0.6667 and parseability 1.0.
- **PASS — GitHub Actions run #200:** 115 backend tests, 40 frontend tests, and JavaScript syntax checks passed for commit 5155d170. https://github.com/sharehousegirls/childcare-map/actions/runs/45176395224
- **PASS — GitHub Actions run #201:** 116 backend tests, 40 frontend tests, and JavaScript syntax checks passed for commit 406f604. https://github.com/sharehousegirls/childcare-map/actions/runs/45196215022
- **NOT RUN:** direct local repository checkout tests, manual browser/mobile/accessibility checks, live API/schema/CRS/reuse validation.
- No runtime code, dependencies, credentials, live API connections, or deployment were added.


## 2026-11-24 incremental milestone — normalized region text control-character hardening

- Hardened `backend/app/regions.py` to reject embedded C0 (U+0000–U+001F) and C1 (U+007F–U+009F) control characters in non-empty normalized region text fields: IDs, names, region types, parent IDs, source-system labels, and source codes. Existing outer-whitespace trimming remains unchanged; codes are still treated as strings with no guessed format/length.
- Added two regression tests covering each field with embedded C0 and C1 characters. A test-only failure occurred in runs #204–#207 because the initial test inputs placed control characters at the end and `str.strip()` removed them; tests were corrected to embed the characters in the middle of each value. No production logic change was needed for that test-placement issue.
- **PASS — GitHub Actions run #208:** 118 backend tests, 40 frontend tests, and JavaScript syntax checks passed on commit `36b2acd8ea77906c4635b12a1e162957626aba2d`. https://github.com/sharehousegirls/childcare-map/actions/runs/45219072602
- Documentation added in `docs/region-code-control-character-validation-2026-11-24.md`; README points to the note.
- **NOT RUN:** direct local repository checkout, official code archive import, live API/schema/CRS/reuse validation, browser/manual/responsive/accessibility review. No credentials, live API calls, map/geospatial changes, or deployment.


## Documentation CI confirmation — 2026-11-24

- **PASS — GitHub Actions run #209:** 118 backend tests, 40 frontend tests, and JavaScript syntax checks passed for documentation commit `79b63469229b01a9b3a842a247cce8947cc2b091`. https://github.com/sharehousegirls/childcare-map/actions/runs/45218756014
- **PASS — GitHub Actions run #210:** the updated project-status commit `4b0c330e976200cf7a2c7fff2a0edb3cc607543` passed the same workflow; backend log reports 118 tests and `OK`. https://github.com/sharehousegirls/childcare-map/actions/runs/45219246014


## 2026-11-24 incremental milestone — visible source-date quality diagnostics

- Added a small frontend helper to display backend source-date coverage and parseability counts with row denominators. The diagnostic text distinguishes missing dates from unparseable dates, avoids percentages for an empty facility response, and shows a warning if metadata counts are inconsistent.
- Demo mode explicitly states that real source-date diagnostics are unavailable; no fictional date quality values are shown. The live display is accessible via a polite status region and uses text-only rendering.
- **PASS — isolated Node tests:** 5/5 tests passed for valid metadata, all dates missing, empty facility response, inconsistent counts, and missing/invalid metadata; module and test syntax checks passed.
- **PASS — GitHub Actions run #212:** Backend unit-test step, JavaScript syntax-check step, and frontend test step all completed successfully for commit `0723232c7c453b441b4e95b16ea807e44125f936`. The connector exposed step conclusions but not test-count output. https://github.com/sharehousegirls/childcare-map/actions/runs/45241050402
- No dependencies, live API requests, credentials, geospatial data, or deployment were added. Ratios are response-row-based, not unique facility coverage or freshness guarantees.


## 2026-11-24 incremental milestone — frontend source-date freshness display
- Added a separate UI line showing the latest valid source-record date, date range/mixed-date status, and calendar-day difference measured at API collection time.
- Invalid date strings are excluded from date calculations and counted in the display; future source dates and inconsistent metadata are flagged for review.
- No stale threshold, SLA, or provider update cadence is inferred. Source-date meaning still requires official schema/sample verification.
- Added 8 Node unit tests in the initial implementation covering valid age, mixed-date range, invalid dates, future dates, missing collection timestamp, inconsistent latest-date metadata, mixed-flag mismatch, and invalid entries alongside valid dates.
- **PASS — GitHub Actions run #212:** backend, JavaScript syntax, and frontend test steps completed successfully for the initial implementation; the run did not expose test-count output. https://github.com/sharehousegirls/childcare-map/actions/runs/45261444098
- No local repository checkout is available in this run.



## 2026-11-24 follow-up — collection timestamp validation
- Tightened elapsed-day calculation to require a calendar-valid collection date, valid clock fields, and a timezone offset no greater than ±14:00.
- Added a regression test for invalid collection dates, clock values, and timezone offsets.
- Added one regression test covering invalid calendar date, clock, and offset variants.
- **PASS — GitHub Actions run #215:** backend, JavaScript syntax, and frontend test steps succeeded for commit `92552ff6d5bc732c7cab6845be6386cc4a384b65`. The repository test files contain 118 backend test methods and 54 frontend test cases; CI output exposed step conclusions but not counts. https://github.com/sharehousegirls/childcare-map/actions/runs/45261706107
- Direct local repository checkout tests: NOT RUN.


## 2026-11-24 incremental milestone — grouped region selector
- Grouped the existing region selector by its parent display label using native optgroups; child labels are shortened only when the parent prefix is present, while option values preserve the full region name.
- Added 7 unit tests for Korean sorting, parent grouping, display/value separation, fallback parent, malformed rows, same-group duplicates, and input immutability.
- **PASS (isolated Node harness):** 7/7 tests and syntax checks. This was not a full repository checkout.
- **PASS — GitHub Actions run #217:** backend unit-test, JavaScript syntax-check, and frontend test steps completed successfully; run-level conclusion is success. Exact test-count output was not exposed by the connector. https://github.com/sharehousegirls/childcare-map/actions/runs/45281684930
- **NOT RUN:** browser interaction, mobile viewport, and screen-reader checks.
- No official region codes, live API data, mapping, external dependency, or deployment were added. Grouping is presentation-only; canonical code-based hierarchy and dong navigation remain blocked on official source review/import.


## 2026-11-24 incremental milestone — saved-region comparison
- Added a comparison helper and UI cards for regions already saved in browser-local storage. Cards show facility count, wait total, average per known facility, explicit zero-wait facility count, and live-data coverage when valid.
- Demo values retain example labels; facility-level coverage remains unknown in demo mode. Live totals are marked partial unless completeness metadata and full known-facility coverage confirm every facility; missing values remain unknown rather than zero.
- Stale or ambiguous name matches are reported as unavailable instead of selecting an arbitrary region. Comparison rendering uses DOM text nodes and does not interpolate saved names into HTML.
- **PASS — isolated Node tests:** 10/10 tests passed for demo ordering/labels, complete and partial live coverage, unknown totals, missing/ambiguous regions, malformed/duplicate saved entries, invalid metrics, empty regions, and input validation. Module and test syntax checks passed.
- GitHub CI verification pending after implementation commit; browser/manual mobile and accessibility testing remains **NOT RUN**.
- No official data, map coordinates, API credentials, dependencies, or deployment were added. Comparison is current-data only; historical snapshots and canonical region IDs remain future work.


## 2026-11-24 follow-up — saved-region comparison consistency guard
- The comparison display now labels partial totals only when facility coverage metadata reconciles; otherwise it reports that coverage and the total require verification.
- Added a regression case for inconsistent known/missing facility counts. **PASS — isolated Node: 11/11 saved-region comparison tests.** GitHub CI follow-up pending.


## 2026-11-24 follow-up — coverage metadata hardening
- Coverage validation now treats a present but invalid missing-facility count as invalid metadata, rather than silently treating it as absent. Added a regression test for negative counts. **PASS — isolated Node: 12/12 saved-region comparison tests.** GitHub CI follow-up pending.


## 2026-11-24 official catalog/API-policy recheck
- Directly re-opened the nationwide waitlist dataset 15101154 catalog. Its description lists facility identity/location and waitlist fields for ages 0–5, 6+, and total; catalog metadata remains XML/LINK, free, real-time, and unrestricted reuse.
- Reconfirmed the official API guide points to a downloadable service specification with operations, request/response schemas, and examples. The public page still does not expose enough to verify the exact endpoint, field mapping, pagination, coordinate encoding, or null semantics.
- Reconfirmed development access is capped at 50 rows, has no expiration, and keys are issued after approval. Operating access is separately reviewed, requires traffic estimates, and is valid for 12 months. Commercial-use restrictions can apply by API; catalog-level unrestricted reuse is not treated as blanket redistribution/commercial clearance.
- Evidence is documented in `docs/official-api-catalog-recheck-2026-11-24.md`; no credentials or live calls were used.

## 2026-11-24 saved-region comparison verification
- **PASS — isolated Node:** final helper/test files ran with 12/12 tests. `node --check` passed for helper and test.
- **PASS — GitHub Actions #219:** full workflow success for the comparison implementation; **#220:** full workflow success for coverage wording; **#221:** full workflow success for invalid coverage metadata guard. Run-level conclusions were success; connector job step summaries confirm backend tests, frontend syntax checks, and frontend tests succeeded.
- **NOT RUN:** browser interaction, mobile layout, keyboard-only, and screen-reader testing.


## 2026-11-24 run closeout — verified code and documentation CI
- Saved-region comparison implementation and two coverage-hardening follow-ups are on `main`; the final isolated Node helper/test harness ran **12/12 PASS**. Browser interaction testing remains NOT RUN.
- **PASS — GitHub Actions #221:** final coverage-metadata guard code, backend tests, JavaScript syntax, and frontend tests all succeeded. https://github.com/sharehousegirls/childcare-map/actions/runs/45299222870
- **PASS — GitHub Actions #222:** official API catalog/policy recheck documentation and README/status updates; full workflow succeeded. https://github.com/sharehousegirls/childcare-map/actions/runs/45299364256
- Official source recheck confirmed catalog field descriptions and account policy only; exact service schema and service-specific reuse terms remain blocked by development access, technical document, sample, and approval.

 
## 2026-11-24 archive preflight CI closeout

- Added `evaluate_region_archive_preflight` to combine reuse gates with local archive basename, regular-file, and SHA-256 checks. Public and commercial archive gates require integrity verification; the commercial gate additionally requires explicit commercial-use permission.
- Review caught two failed commits (`49ece9d`, `ffbb436`) where test placement/syntax was malformed. The final correction `8618fb6` rebuilds the test file from the previously verified baseline and places six preflight tests correctly inside `RegionManifestTests`. These intermediate failures are retained as development history and are not counted as passing evidence.
- **PASS — GitHub Actions #226:** 124 backend tests, frontend syntax checks, and 73 frontend tests all passed.
- **NOT RUN:** local checkout/test execution and browser/manual accessibility testing. GitHub CI is the verified execution environment.
- No official region archive was downloaded or imported. The helper does not authenticate provenance, safely extract ZIP contents, validate official layouts, or replace human reuse review.


## 2026-11-24 incremental milestone — reject symlinked region archives

- Archive preflight now rejects a path that is a symbolic link, even if its basename and target digest match the manifest. This avoids accepting unexpected path indirection before a future importer.
- Added one regression test using a matching-content symlink; unsupported symlink creation is skipped explicitly by the test rather than treated as a pass.
- Updated the archive preflight notes to state the restriction and the remaining time-of-check/time-of-use risk. The importer must stage the file safely and keep the verified archive immutable through extraction; this preflight alone is not race-proof.
- **PASS — GitHub Actions #228:** code-only commit passed backend tests, JavaScript syntax and frontend tests. **PASS — #229:** regression-test commit passed the same full workflow. **PASS — #230:** documentation commit passed the same full workflow. Run-level and all step conclusions were successful.
- Backend test file now contains 125 test methods; the #229/#230 backend steps completed successfully. Frontend test files contain 73 tests; syntax and frontend test steps also completed successfully.
- **NOT RUN:** direct local checkout, browser/manual responsive and accessibility tests. GitHub CI is the executed test environment.
- No official region archive was downloaded or imported, no API/credentials were connected, and no deployment occurred.


## 2026-11-24 incremental milestone — descriptor-based archive hashing
- Hardened `verify_file_sha256`: opens with `O_NOFOLLOW` where available and non-blocking mode, checks the opened descriptor is a regular file with `fstat`, and on platforms without `O_NOFOLLOW` compares the pre-open `lstat` device/inode to the opened descriptor.
- Added direct verifier regressions for symlink and non-regular paths; unsafe file errors are surfaced as `archive_file_unsafe` by preflight. The preflight remains fail-closed.
- This narrows path-based symlink races but does not prevent in-place file mutation or guarantee that a future importer extracts the exact verified bytes. Safe immutable staging, ZIP entry/path/size limits, and extraction validation remain required.
- **PASS — isolated verifier harness:** regular-file digest match/mismatch and rejection of directory/symlink paths.
- **PASS — GitHub Actions #237:** backend unit tests, JavaScript syntax checks, and frontend tests succeeded; the backend test file now contains 128 tests (125 baseline + 3 regressions), and frontend tests remain 73. **#236 failed** because a newly added test had a malformed assertion; it was corrected in #237 before counting the run as passing. https://github.com/sharehousegirls/childcare-map/actions/runs/45342054704
- **NOT RUN:** direct local repository checkout, browser/manual responsive and accessibility tests. No official archive download/import, live API request, or deployment.


## 2026-11-24 follow-up — archive verifier regression closure
- Added regression tests for direct symlink rejection, non-regular files, and fail-closed handling of unsafe hash-open errors.
- **PASS — GitHub Actions #237:** backend tests, JavaScript syntax and frontend tests all completed successfully. Backend test file: 128 tests; frontend: 73. **FAIL — #236:** a malformed test assertion caused the backend step to fail; corrected in #237 and not counted as passing.
- **PASS — isolated verifier harness:** regular-file digest match/mismatch and directory/symlink rejection. This is not a direct repository checkout run.
- **NOT RUN:** direct checkout tests in this environment, browser/manual responsive and accessibility checks. No archive download/import, live API, or deployment.


## 2026-11-24 incremental milestone — keyboard focus visibility

- Added a shared `:focus-visible` outline rule covering links, buttons, inputs, selects, and textareas; existing more-specific control styles remain intact.
- Added a Node static CSS regression test checking selector coverage and the 3px outline / 2px offset declarations.
- **CI PENDING:** CSS, test, and docs commits are pushed; verify the current workflow run before calling this PASS.
- **NOT RUN:** manual keyboard-only browser review, mobile viewport, contrast audit, screen-reader checks.
- No API, data, dependencies, or deployment behavior changed.

## 2026-11-24 incremental milestone — keyboard focus visibility (CI closeout)

- Shared CSS `:focus-visible` rule covers links, buttons, inputs, selects, and textareas with a 3px outline and 2px offset.
- Added `tests/accessibility-focus.test.mjs` static CSS regression check.
- **PASS — GitHub Actions #243:** backend unit tests, JS syntax checks, and frontend tests succeeded. The new static focus test is part of the frontend suite. https://github.com/sharehousegirls/childcare-map/actions/runs/45357878490
- **NOT RUN:** direct local repository checkout, manual keyboard-only browser review, mobile viewport, contrast audit, and screen-reader checks.
- No API, data, dependency, or deployment changes.


## 2026-11-24 incremental milestone — verified catalog field inventory
- Re-opened the public dataset 15101154 catalog and documented field groups, normalized mapping candidates, and pre-ingestion acceptance criteria in `docs/official-api-catalog-recheck-2026-11-24.md`. Catalog-level names are explicitly marked unverified as XML element names; no `API_FIELD_MAP`, API request, or live ingestion was configured.
- Clarified the data-minimization scope (representative/staff details are not needed for the waitlist map), and added whole-pagination facility-ID deduplication, source-date coverage, waitlist total-vs-age-bucket checks, and CRS/axis-order validation gates.
- Reconfirmed the coordinate risk: catalog labels latitude/longitude, while portal FAQ reports EPSG:5181 TM for its childcare map. Actual field values, units and axis order must be checked in a redacted response before mapping.
- Official catalog page was re-opened on 2026-11-24. It lists the dataset as XML/LINK, free, real-time catalog metadata, and unrestricted reuse; this remains a catalog statement, not blanket commercial/cache/redistribution clearance. API access still requires a reviewed account; development results are limited to 50 rows and operating access is separately reviewed.
- **PASS (documentation review):** catalog field inventory and mapping gates are grounded in the public catalog and official API policy/guide/FAQ pages.
- **NOT RUN:** repository tests (docs-only change), direct checkout, browser, live API, archive import, and deployment. The GitHub combined-status query returned no check entries for the docs commits; no CI execution is claimed.
- **Next:** obtain service specification + redacted sample; verify operation/response envelope/paging/row limit/date/ID/CRS/terms, then run only a bounded offline mapping-validation batch before considering live access.
## CI verification update — 2026-11-24

The documentation commits following the official catalog review were subsequently verified by the full GitHub Actions workflow. The earlier catalog-review note's "NOT RUN" is historical and has been superseded for those commits.

- **PASS — GitHub Actions #249** (commit `6c54c44092c0faab788421f676df118dfd052b2f`): backend **128 tests**, frontend **74 tests**, JavaScript syntax check all passed; job conclusion success.
- Evidence: https://github.com/sharehousegirls/childcare-map/actions/runs/45376815885
- **NOT RUN:** direct local checkout, browser/manual responsive and keyboard/screen-reader checks, live API, official-region archive import, and deployment.
- This workflow result does not change the official API schema, credentials, reuse-term, or coordinate-system blockers.

## 2026-11-24 incremental milestone — Korean calendar freshness comparison

- **FAIL — GitHub Actions #252 (intermediate code-only commit):** the old UTC-based future-date fixture failed after the code switched to Korea-local dates; the test fixture was corrected in #253 and the full test workflow passed. This was an expected compatibility break between the separate code and test commits, not left unresolved.
- **PASS — GitHub Actions #254:** documentation update workflow completed successfully. https://github.com/sharehousegirls/childcare-map/actions/runs/45416727857

- Corrected the freshness diagnostic to compare date-only source dates with the collection timestamp's **Asia/Seoul calendar date** rather than UTC. This avoids false future/staleness day labels around UTC midnight for Korean data.
- Added two boundary regressions: collection timestamp crossing into Korea's next day, and a source date still future just before Korean midnight.
- **PASS — GitHub Actions #253:** backend, JavaScript syntax and frontend test steps succeeded for the code/test commits. Exact frontend test-count output was not available via the connector. https://github.com/sharehousegirls/childcare-map/actions/runs/45416448050
- **PASS — isolated local harness:** 11 freshness tests passed from copied current module/test content; this is not a full local repository checkout.
- **NOT RUN:** full local repository suite, browser/manual timezone display review, live API, official region archive import, deployment.
- No live-data, API credentials, external dependencies, or deployment behavior changed.


## 2026-11-25 incremental milestone — secondary API tag candidates and Pages evidence

- Re-opened official catalog dataset 15101154. Catalog-level field groups remain verified, but the exact service-specific XML schema is still not confirmed.
- Secondary index pages surfaced candidate tags (for example `stcode`, `crname`, `datastdrdt`, and `ew_cnt_00`…`ew_cnt_tot`). These are explicitly marked UNVERIFIED and recorded in `docs/secondary-api-field-candidates-2026-11-25.md`; no automatic alias or live field map was configured.
- Added a fail-closed regression test that supplies those secondary candidates without an explicit map and verifies normalized identity/date/waitlist values remain unknown.
- **PASS — GitHub Actions #258:** 129 backend tests, 76 frontend tests, and JavaScript syntax checks succeeded. https://github.com/sharehousegirls/childcare-map/actions/runs/45439607037
- **PASS — GitHub Pages workflow #1:** build, deploy, and status-report jobs succeeded after Pages was enabled by the user. Expected URL is `https://sharehousegirls.github.io/childcare-map/`. The external web viewer returned an internal error; the published page has not been manually verified in a browser/device.
- **NOT RUN:** direct local full-suite checkout, live API call, official archive import, manual browser/mobile/keyboard/screen-reader checks. No live-data mapping, credentials, or deployment was initiated by this automation.
- **Next:** obtain the official technical document and redacted payload, verify schema/paging/date/ID/CRS/null semantics and service-specific reuse terms, then run a bounded offline mapping-validation batch.


## 2026-11-25 incremental milestone — official API account and specification workflow recheck

- Re-opened the public dataset 15101154 catalog and the official Childcare Portal Open API list, development guide, and use policy.
- Confirmed the official portal workflow: signup/login, development-account application/review and key issuance, service-spec-based development/test, then separate operating-account application/review and key issuance. Development account results are limited to 50 rows; operating account requires expected-traffic entry, is valid for 12 months, and must be renewed for continued use.
- The portal guide describes the service technical document as containing service URL, operations, request/response definitions, and examples. The exact portal operation-to-dataset-15101154 mapping and schema remain unverified; no API request or credentials were used.
- Added `docs/official-api-account-and-spec-gate-2026-11-25.md` and a README link. Updated portal guide/policy links to the currently verified paths.
- Existing user-action email about the API approval blocker is already in Sent; no duplicate email was sent.
- **PASS (documentation/source review):** the public official pages opened and the workflow/limits were recorded with scope boundaries.
- **NOT RUN:** local test suite (documentation-only change); live API request, schema verification, exact-service reuse clearance, and browser manual checks.
- **Next:** obtain the exact service technical document and redacted response, confirm dataset/service correspondence and service-specific reuse terms, then perform bounded offline schema mapping validation. Live ingestion remains gated.


## 2026-11-25 — provider payload traversal hardening

- Replaced recursive provider response flattening with an iterative depth-first traversal. Common response envelope keys retain priority; insertion order is retained within priority/fallback groups.
- Added cycle detection for arbitrary in-memory payload structures and avoided recursion-depth failures on deeply nested envelopes.
- Added tests for 1,500-level nesting and cyclic input.
- Acceptance: existing JSON/XML envelope behavior and key priority preserved; deep payload returns a row without RecursionError; cyclic payload without records terminates with an empty list.
- **NOT RUN locally:** this connector-only session cannot execute the repository checkout directly. GitHub Actions is the authoritative test run for this commit.
- **Next:** verify CI; then continue official schema/source/license checks and region-code provenance. No live API call, deployment, or credential use was performed.


## 2026-11-25 crosswalk metadata validation follow-up
- Extended legal-dong/admin-dong crosswalk text and date validation to reject embedded C1 controls (U+007F–U+009F), alongside C0 controls (U+0000–U+001F). Text fields and `valid_from`/`valid_to` retain field-specific issue codes.
- Added two regression tests: five text fields and two effective-date fields are probed with U+0085 (NEL) at an interior position, preserving input length.
- **PASS — GitHub Actions run #283:** 133 backend tests, 76 frontend tests, and JavaScript syntax checks succeeded on commit `f81caa9bcf627daa7447f0368ec817374c5d0e64`. https://github.com/sharehousegirls/childcare-map/actions/runs/45519664581
- **PASS — run #281:** the code/test commit also passed CI (133 backend tests, 76 frontend tests). https://github.com/sharehousegirls/childcare-map/actions/runs/45519621808
- **Initial test FAIL — run #280:** three subcases failed because U+0085 was placed at the end of short values and Python `strip()` removed it; the probes were corrected to keep the character interior. The implementation was not changed for this test-fixture correction. https://github.com/sharehousegirls/childcare-map/actions/runs/45519593914
- Local execution is **NOT RUN**: a shallow clone attempt failed because the container could not resolve `github.com`. CI is the actual source-checkout test evidence.
- This remains structural input validation only. No official code archive, API payload, or live data was imported. No merge to `main` or deployment was performed.
- Details: `docs/crosswalk-control-character-validation-2026-11-25.md`.
