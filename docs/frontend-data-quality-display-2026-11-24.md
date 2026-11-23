# Frontend source-date quality details — 2026-11-24

## Scope
The live-data status panel now displays record-level source-date coverage and strict-date parseability after the backend returns its verified metadata fields. The values are computed from the backend's row counts, not from unique facility IDs.

## Display rules
- Demo mode explicitly states that no real source-date quality diagnostics are available.
- A non-empty live response shows dated rows / total rows, parseable dates / dated rows, unparseable rows, and missing-date rows.
- Empty responses do not show percentages.
- Missing, malformed, or inconsistent counts produce a safe fallback or warning instead of misleading percentages.
- The panel does not classify data as fresh/stale; provider date semantics and an update SLA remain unverified.

## Acceptance criteria
- [x] Demo state is not presented as real quality data.
- [x] Valid metadata displays coverage and parseability with row denominators.
- [x] Missing-date and invalid-date counts remain distinct.
- [x] Zero denominators do not create NaN/Infinity or misleading percentages.
- [x] Inconsistent counts are visibly flagged.
- [x] Diagnostics remain text-only and are announced through an accessible status region.
- [x] No dependency or live API configuration is added.

## Test evidence
The isolated Node test suite contains five cases: normal counts, all dates missing, empty facilities, inconsistent counts, and invalid/missing metadata. Direct repository checkout, full CI, and browser testing are recorded separately in the project status.

## Limitations
Ratios are row-based. Duplicate facility records can affect them; they are not unique-facility coverage. Diagnostics are not a freshness guarantee and do not validate the provider's date semantics.
