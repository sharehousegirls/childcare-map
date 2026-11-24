# Freshness calendar comparison — Korean date boundary fix (2026-11-24)

## Change
The frontend freshness label compares a provider's date-only source date with the collection timestamp's **Asia/Seoul calendar date**, instead of the UTC calendar date.

This prevents an off-by-one-day label near UTC midnight. For example, `2026-11-23T15:00:00Z` is `2026-11-24 00:00` in Korea; if the source date is `2026-11-24`, the displayed elapsed calendar days should be 0, not a future-date warning.

## Scope
- `data-freshness.mjs`: convert the validated collection instant to date parts in `Asia/Seoul` before calendar-day comparison.
- `tests/data-freshness.test.mjs`: update the future-date fixture to a timestamp that is still on the previous Korean calendar day and add boundary regressions on both sides of Korean midnight.

## Acceptance criteria
- Collection timestamp validation remains offset-aware and rejects invalid dates/times/offsets.
- Source date and collection date are compared as calendar days in Korea, not elapsed 24-hour intervals.
- UTC timestamps crossing Korean midnight produce the expected Korean date.
- A source date that is still future before Korean midnight remains flagged.
- Missing/invalid collection timestamps do not produce an elapsed-day label.

## Validation

- **FAIL — GitHub Actions #252 (intermediate code-only commit):** the old UTC-based future-date fixture failed after the code switched to Korea-local dates; the test fixture was corrected in #253 and the full test workflow passed. This was an expected compatibility break between the separate code and test commits, not left unresolved.
- **PASS — GitHub Actions #253:** backend, JavaScript syntax, and frontend test steps completed successfully for commit `a38b2d7a09e9fb4cc59d50539998d98b486d58db`. Exact frontend test-count output was not available through the connector.
- **PASS — isolated local harness:** 11 data-freshness tests passed using copied module/test content; this is not a direct repository checkout test.
- **NOT RUN:** full local repository test suite, browser/manual review, live API or data import.

## Limitations
This is a calendar-day diagnostic, not a freshness SLA. It does not prove the provider's data is current or that source-date semantics have been verified.
