# Project status — 2026-11-22

## Current phase
**Pre-live validation and storage foundation.** Live API connection remains gated on verified official schema, credentials, quality, and service-specific reuse terms.

## Completed foundation
- Responsive static prototype: region cards, facility search, type filter, explicit zero-wait filter.
- FastAPI adapter scaffold with server-side credential configuration, XML/JSON parsing, normalized fields, health and facility endpoints.
- Provider error sanitization and field-map validation.
- Waitlist-total consistency diagnostic; missing/duplicate facility-ID flags (batch-level only).
- Backend unit-test evidence and CI evidence documented in the security review.
- Official source inventory and integration plan.
- Draft relational model for region hierarchy, facility identity, snapshots, ingestion-run audit, region mapping provenance, and browser-local saved features.
- File-backed SQLite snapshot-storage scaffold: facility metadata, append-only snapshots, ingestion-run summaries, and unresolved-record review table; idempotent batch handling and quality flags. Not yet wired to the API route

## Blockers / not yet verified
- Daegu facility-metadata development API application is pending; it does not itself provide the waitlist fields.
- Nationwide waitlist dataset 15101154 application/approval is not confirmed.
- Credentials are not available; no live request has been made.
- Official API endpoint, operation, request parameters, pagination, response/error envelope, exact field names, ID stability, null semantics and row limit need the service specification and a redacted sample.
- Service-specific attribution, caching, display, redistribution, commercial and advertising conditions are not cleared.
- Region codes/boundaries, legal-dong vs administrative-dong mapping, coordinate CRS and axis order require source validation.

## Known limitations
- Demo values are fictional and must not be interpreted as current real waitlist data.
- No actual nationwide facility/waitlist ingestion.
- No implemented canonical region hierarchy or dong-level mapping.
- SQLite snapshot storage exists as an isolated scaffold, but it is not integrated with API ingestion or exposed through routes; no region hierarchy, real map, facility detail page, persistent saved features, comparisons or trend UI yet.
- Storage schema has no versioned migrations, failed-run/retry recording, retention/backup policy or production concurrency/load review.
- Automated data refresh, SEO, production hardening and deployment are not ready.
- Complaint/violation/administrative-history feature remains deferred until all other scope is complete and owner review is requested.

## Verification
- **PASS (reported/evidence documented):** 15 backend unit tests in an isolated harness using source/test blob hashes verified against the repository; GitHub Actions passed for commit ec14fb6a938820cb1185ada6e3e26101fa3201e4. See docs/backend-security-review-2026-11-21.md.
- **PASS (isolated local copy):** 11 SQLite storage unit tests and Python `compileall`; this did not run against a direct repository checkout. GitHub Actions run #48 passed for commit `396e30762bb3776eadeddd1715b0574bf0049ce4` (26 tests).
- **PASS — GitHub Actions run #48:** 26 repository tests passed for commit `396e30762bb3776eadeddd1715b0574bf0049ce4` (workflow: https://github.com/sharehousegirls/childcare-map/actions/runs/44947857967).
- **NOT RUN:** direct local repository checkout test run in this environment.
- **NOT RUN:** browser interaction, accessibility, responsive manual test, frontend unit tests.
- **BLOCKED:** live API validation, nationwide data completeness, real map/geospatial validation, end-to-end integration.
- **WARN:** GitHub Actions reports Node 20 deprecation notices for checkout/setup-python actions; run is successful, but workflow action maintenance should be scheduled.
- **NOT RUN:** deployment; requires owner approval.

## Next priorities
1. Obtain nationwide waitlist API access, official specification, redacted response, and complete reuse/attribution review.
2. Implement canonical province/district region hierarchy using verified codes; do not guess codes or claim dong-level coverage.
3. Add schema versioning/migrations and ingestion failure/retry audit; connect the tested snapshot-storage scaffold only after API/schema/rights gates pass.
4. Add real map, facility detail, region comparison and filtering against validated data.
5. Add saved regions/facilities/searches, comparisons, snapshot history and trends.
6. Add automated refresh/recovery, SEO, accessibility, operational/security review.
7. Conduct deploy-readiness review; deploy only with owner approval.

## Acceptance rules
- Missing is not zero; zero-wait requires explicit zero.
- Waitlist application counts are not necessarily unique children across facilities.
- No admission-date prediction.
- Show source, record date, collection time, coverage and quality flags.
- Keep demo and live states unmistakably distinct.
- Never commit credentials or expose them in logs/errors.
- Verify source terms before public redistribution or commercial use.
