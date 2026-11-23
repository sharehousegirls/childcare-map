# Region selector grouping — 2026-11-24

## Scope

A small presentation-layer improvement to the region selector. Options are now grouped with native HTML `optgroup` elements by the existing `district` parent label. Region selection values remain the original region-name strings so filtering and browser-local saved-region/search records continue to work.

When a region name begins with the parent label followed by a space, the visible option label omits that prefix (for example, `경기도 수원시 영통구` displays `수원시 영통구`). The option value remains the complete original name. Groups and options are sorted with Korean locale comparison; repeated names inside the same parent group are deduplicated.

## Boundaries and risks

- Grouping is display-only; it is not an official administrative hierarchy or canonical-code implementation.
- The current `district` field is a display parent label (live regional summary currently supplies the province name; demo rows also use province labels).
- This change does not add province/city/district/dong navigation, official region IDs, or region-code imports.
- Saved-region values remain name strings. A future code-based hierarchy must include a migration/compatibility strategy for browser-local saved regions and saved searches.
- No live API, geospatial source, dependency, or deployment behavior was added.

## Acceptance criteria

- [x] All valid region options are grouped by their existing parent label.
- [x] Parent groups and option labels are sorted in Korean.
- [x] Parent-prefixed display labels are shortened without changing option values.
- [x] Blank/invalid records are ignored; missing parent labels use an explicit fallback.
- [x] Duplicate option names within a parent group are collapsed.
- [x] Region input records are not mutated.
- [x] Existing filtering and saved-region values remain name-based.

## Tests

- **PASS (isolated Node harness):** 7/7 unit tests passed; module and test syntax checks passed. This harness ran the new module/test files outside a repository checkout, not the full project suite.
- **PASS — GitHub Actions run #217:** backend unit-test, JavaScript syntax-check, and frontend test steps completed successfully; run-level conclusion is success. Exact test-count output was not exposed by the connector. https://github.com/sharehousegirls/childcare-map/actions/runs/45281684930
- **NOT RUN:** browser/manual responsive/accessibility tests.

## Next step

After official region-code archive and reuse review, replace name-based grouping/values with an ID-backed canonical hierarchy. Add dong navigation only after official hierarchy and mapping evidence is validated; keep saved-region migration explicit.
