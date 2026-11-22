# Regional aggregation and waitlist coverage — 2026-11-22

## Scope

Extract frontend region aggregation into `regional-summary.mjs` and use it from `app.js`. This change addresses the risk that missing waitlist counts were displayed as a zero total.

## Behavior

- Province-first region label when both `sido` and `sigungu` are present; the previous frontend order was district-first.
- A wait count is considered known only when it is a finite, non-negative number.
- Aggregate `waiting` remains `null` when no facility in the region has a known wait count. A confirmed zero remains numeric zero.
- Partial totals sum only known facility values and are accompanied by known/missing facility counts.
- Average and zero-wait rate use only facilities with known wait counts.
- Exposes `coverage`, `missingWaitlistFacilities`, `zeroWaitRate`, and `waitTotalComplete` for future quality UI.
- Sorts region names consistently in Korean.
- Invalid wait values are not silently converted to zero.

## UI

Regional cards show confirmed wait totals, average per facility with known wait data, zero-wait count/rate, and facilities with unknown waitlist data. The summary card includes known and unknown facility counts. The zero-wait filter still requires explicit `waiting === 0`.

## Acceptance criteria

1. All-unknown region displays unknown total (—), not 0.
2. Partial totals use known values only and report missing facilities.
3. Explicit zero remains a valid total and zero-wait facility.
4. Region labels use `sido sigungu` order when both fields are present.
5. Negative, nonnumeric, and nonfinite values are counted as unknown.
6. Aggregation does not mutate input rows.
7. The pure module is covered by Node tests and included in CI syntax checks.

## Test status

- **PASS — GitHub Actions run #105:** 8 regional aggregation tests passed; the workflow also passed 45 backend tests, 9 saved-search tests, 11 saved-region tests, and JavaScript syntax checks. https://github.com/sharehousegirls/childcare-map/actions/runs/44995019954
- **NOT RUN:** manual browser interaction, mobile viewport, screen-reader/accessibility validation.

## Limitations

- The module is not a source-schema validator and does not confirm the official data source or facility-level completeness.
- Live facility IDs are not used for grouping; grouping uses normalized region labels until canonical codes are imported.
- Coverage means facility-row coverage for a waitlist value, not unique children or completeness of provider data.
- No live API configuration or real data was used in these tests.
