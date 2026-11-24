# Saved-region comparison — 2026-11-24

## Scope
Added a current-data comparison panel for regions users have already saved in browser-local storage. This is a Lock-in First improvement that does not depend on official data or geographic sources.

## Metrics
- Facility count
- Wait total (demo example or live verified/partial sum)
- Average wait per facility with known waitlist values
- Explicit zero-wait facility count
- Live waitlist coverage (known facilities / total facilities) when valid

## Safety and data semantics
- Demo totals and averages are visibly labeled as examples and never treated as current facts.
- Live totals are labeled complete only when metadata says complete, all facilities have known counts, and the total itself is valid. Otherwise they are identified as partial or unknown.
- Missing waitlist values are not converted to zero.
- Coverage is unknown in demo mode because the demo region summaries do not contain facility-level waitlist coverage.
- The UI notes that waitlists at multiple facilities may overlap; totals are not a count of unique children.
- A saved name that no longer matches current data is marked unavailable. Duplicate names in the current dataset are treated as ambiguous, not arbitrarily selected.
- Rendering uses DOM text nodes, avoiding HTML interpolation of saved names.

## Acceptance criteria
- [x] Comparison follows the saved-region order.
- [x] Metrics are null-safe and nonnegative; invalid counts are not displayed as valid values.
- [x] Partial live totals are clearly marked.
- [x] Demo data and coverage limitations are clearly labeled.
- [x] Missing and ambiguous name matches are surfaced as unavailable.
- [x] Comparison refreshes after saved-region changes and after data mode changes.
- [x] No API, dependency, coordinate, or deployment changes.

## Tests
- **PASS (isolated Node):** 11/11 unit tests; module/test syntax checks passed. A follow-up regression case rejects inconsistent known/missing coverage counts.
- **PASS — GitHub Actions run #219:** backend unit-test, JavaScript syntax-check, and frontend test steps succeeded for commit `142c1005c83fd1068d2a17f06c1e12e5a749a255`. https://github.com/sharehousegirls/childcare-map/actions/runs/45299016823
- Follow-up UI wording now distinguishes a valid partial total from unverified coverage.
- **NOT RUN:** Browser, mobile viewport, keyboard, and screen-reader interaction tests.

## Limitations
- Comparison is based on region-name matching and the current dataset, not official region IDs.
- Historical snapshots, trend charts, account sync, and server-side saved comparisons are not implemented.
