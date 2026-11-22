# Project status — 2026-11-22

## Current phase
**Prototype feature expansion.** Live API connection remains gated on verified official schema, credentials, quality, and service-specific reuse terms.

## Completed foundation
- Responsive static prototype: region cards, facility search, type filter, explicit zero-wait filter.
- Browser-local saved searches: store, restore and delete region/search/type/zero-wait filters (up to 20, no account or server sync).
- Browser-local saved regions: store, select and delete individual region labels (up to 20; duplicate region labels prevented). Current saved values are display names, not official stable region codes.
- Browser-local saved facilities: save/load/delete by exact facility ID (up to 50). Demo IDs are fictional; records without IDs cannot be saved.
- FastAPI adapter scaffold with server-side credential configuration, XML/JSON parsing, normalized fields, health and facility endpoints.
- Provider error sanitization and field-map validation.
- Waitlist-total consistency diagnostic; missing/duplicate facility-ID flags (batch-level only).
- Backend unit-test evidence and CI evidence documented in the security review.
- Official source inventory and integration plan.
- Draft relational model for region hierarchy, facility identity, snapshots, ingestion-run audit, region mapping provenance, and browser-local saved features.
- File-backed SQLite snapshot-storage scaffold: facility metadata, append-only snapshots, ingestion-run summaries, and unresolved-record review table; idempotent batch handling and quality flags. Not yet wired to the API route.
- Initial normalized region validator/tree builder in `backend/app/regions.py`; supports separate administrative/legal dong types and checks duplicates, parent links, cycles and active-status contradictions. Cycle detection and deterministic tree sorting are iterative to avoid recursion-depth failures on malformed input. Synthetic fixtures only; no official code data imported.
- Region source manifest validator in `backend/app/region_manifest.py` records source/version/date/digest/attribution and reuse review; it provides separate public-redistribution and commercial-use gates. SHA-256 verification streams local files in 1 MiB chunks. The gate is not yet wired to an importer.

- Regional aggregation is extracted into `regional-summary.mjs`: missing wait counts stay null, partial totals/coverage are explicit, zero-wait counts only explicit zero, and live region labels are province-first.

## Blockers / not yet verified
- Daegu facility-metadata development API application is pending; it does not itself provide the waitlist fields.
- Nationwide waitlist dataset 15101154 application/approval is not confirmed.
- Credentials are not available; no live request has been made.
- Official API endpoint, operation, request parameters, pagination, response/error envelope, exact field names, ID stability, null semantics and row limit need the service specification and a redacted sample.
- Service-specific attribution, caching, display, redistribution, commercial and advertising conditions are not cleared.
- Current official administrative/legal-region code files have not been imported or validated. The normalized validator uses a deliberately simplified parent contract; administrative-dong/legal-dong crosswalk is M:N and not implemented. Coordinate CRS and axis order require source validation.

## Known limitations
- Demo values are fictional and must not be interpreted as current real waitlist data.
- No actual nationwide facility/waitlist ingestion.
- No official canonical region hierarchy imported or dong-level mapping implemented. The initial validator is not wired into the API or UI and its simplified parent rules must be checked against current source files.
- SQLite snapshot storage exists as an isolated scaffold, but it is not integrated with API ingestion or exposed through routes; no region hierarchy, real map, facility detail page, persistent saved facilities, server-backed comparisons or trend UI yet.
- Saved searches are browser-local only; up to 20. They do not sync across devices/accounts, and browser storage can be cleared or unavailable.
- Saved regions are also browser-local and currently store region-name strings from the current option list; they are not canonical official IDs and may become stale after region-code/name changes. No migration or cross-device sync yet.
- Saved facilities are browser-local, capped at 50 and matched by exact ID; source-ID changes can make bookmarks stale. No account or device sync.
- Storage schema has no versioned migrations, failed-run/retry recording, retention/backup policy or production concurrency/load review.
- Automated data refresh, SEO, production hardening and deployment are not ready.
- Complaint/violation/administrative-history feature remains deferred until all other scope is complete and owner review is requested.

## Verification
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
- **NOT RUN in this automation run:** direct checkout tests and manual browser/mobile/accessibility checks. New unit tests were committed; GitHub Actions status must be checked after the final commit before reporting pass/fail.
- No provider freshness SLA is inferred from collection time. Source date format and semantics remain pending official API schema/sample.
- Implementation note: `docs/api-freshness-metadata-2026-11-22.md`.
