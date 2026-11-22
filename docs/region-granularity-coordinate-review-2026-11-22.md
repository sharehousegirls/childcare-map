# Region granularity and coordinate review — 2026-11-22

## Scope and official FAQ findings

Reviewed the Childcare Information Disclosure Portal FAQ on 2026-11-22:

- FAQ 12 says nationwide facility type/count queries cannot be requested at dong level; the portal query supports city/county/district (시·군·구) granularity. This statement is specifically about the FAQ's regional facility-type/count query; it is **not evidence that dong-level waitlist totals are directly provided by the API**.
- FAQ 13 reports childcare facility coordinates as EPSG:5181, a Transverse Mercator (TM) projected coordinate system, for the Kakao/Daum map data it describes.
- FAQ 10 warns that lookup can fail when a legal-dong (법정동) address is used for a facility registered under an administrative-dong (행정동), and advises using the administrative dong.

Official source: https://info.childcare.go.kr/info_html5/cera/community/faqboard/FaqBoardSlPL.jsp

## Product and data implications

1. Do not present dong-level waitlist totals as a directly queried official API field or result.
2. The portal FAQ does not rule out a derived dong aggregation from facility-level rows. Such an aggregate is only eligible after a source and boundary review, coordinate validation, and successful spatial mapping.
3. Use official, versioned administrative-region identifiers for navigation. Display names alone are not stable identifiers.
4. Keep administrative dong and legal dong as separate entities; model their crosswalk as a versioned many-to-many mapping where the source supports it.
5. If facility coordinates are confirmed to be EPSG:5181, transform them to the map's expected CRS (typically WGS 84 / EPSG:4326) before rendering. Do not treat projected x/y values as latitude/longitude. Confirm CRS and axis order for the exact response before processing.
6. Record the boundary dataset/version, CRS, transformation method, mapping result and review provenance.
7. Preserve unmapped or ambiguous facilities as unresolved; do not silently assign them to a dong.
8. Show coverage beside derived dong metrics: mapped facilities / facilities with eligible waitlist values / total facilities. Unknown wait counts remain unknown, not zero.
9. Avoid summing facilities or records that are duplicated across region assignments. Validate facility identity and region membership before aggregation.

## Recommended implementation sequence

- Import and validate the current official region-code archive only after source metadata and reuse terms are reviewed.
- Build a stable region tree for province/city → district → administrative dong; retain legal-dong records separately.
- Add a versioned administrative-dong/legal-dong crosswalk and unresolved mapping review.
- Validate facility coordinates and CRS against a redacted API sample.
- Only then compute dong-level waitlist aggregates from uniquely identified facility rows and validated boundary joins.
- Until those acceptance checks pass, support verified direct city/county/district statistics and label dong-level metrics unavailable rather than fabricated.

## Acceptance criteria for dong aggregation

- [ ] Boundary source, version, terms, attribution and CRS documented.
- [ ] Coordinate source and CRS confirmed for the exact facility feed.
- [ ] Transform tested against known control points or official examples.
- [ ] Facility IDs are stable and deduplicated within a snapshot.
- [ ] Spatial assignment is deterministic and handles boundary/ambiguous points.
- [ ] Unmapped facilities are retained and surfaced with coverage.
- [ ] Waitlist missingness remains null; no implicit zero.
- [ ] Derived totals and coverage have unit tests.
- [ ] UI explicitly distinguishes derived dong aggregation from direct provider query.
- [ ] No admission-date prediction or unique-child interpretation is introduced.

## Source

Childcare Information Disclosure Portal, FAQ (reviewed 2026-11-22):
https://info.childcare.go.kr/info_html5/cera/community/faqboard/FaqBoardSlPL.jsp
