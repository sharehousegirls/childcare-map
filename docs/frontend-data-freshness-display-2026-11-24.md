# Frontend source-date freshness display — 2026-11-24

## Scope
- Display the newest parseable source-record date separately from API collection time.
- Show a valid date range when multiple source-record dates are present.
- Compute elapsed calendar days only relative to the API collection timestamp.
- Flag future source dates, invalid date values, and inconsistent date metadata.
- Keep demo mode explicit; no real freshness data is invented.

## Semantics
The display is descriptive and is not a freshness SLA or stale/fresh classification. The source-date meaning, provider update cadence, and acceptable age threshold remain unverified until the official API schema and a redacted response are reviewed. A source date later than the collection date is shown as a warning, not corrected automatically.

Date values are accepted only as valid calendar dates in `YYYY-MM-DD`. Collection timestamps must include a timezone. The helper derives a range from the unique valid source-date list; malformed values are excluded and counted. Metadata range/latest mismatches are flagged instead of silently trusted.

## Acceptance criteria
- [x] One valid date is shown without a freshness threshold.
- [x] Multiple valid dates produce a range and mixed-date label.
- [x] Invalid calendar dates are excluded from date math.
- [x] Elapsed days use the collection timestamp's UTC calendar date.
- [x] Future source dates are flagged.
- [x] Missing/invalid collection timestamps do not produce a computed age.
- [x] Invalid collection calendar dates, clock values, and timezone offsets are rejected.
- [x] Latest-date and mixed-date metadata inconsistencies are flagged.
- [x] Demo mode states that real freshness is unavailable.
- [x] No dependency, live API request, credential, or deployment added.

## Tests
- 10 Node unit tests added to `tests/data-freshness.test.mjs`.
- PASS — GitHub Actions run #212 passed the initial 8-test implementation. Follow-up timestamp validation and its 2 added assertions are pending CI
- Direct local repository tests: NOT RUN (no local checkout in this execution environment).
