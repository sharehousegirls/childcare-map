# Real-data integration plan

## Primary official source candidate: nationwide waitlist

**한국사회보장정보원_어린이집별 기본정보 조회 (15101154)**  
https://www.data.go.kr/data/15101154/openapi.do

Official catalog lists nationwide facility identity/location, capacity/enrollment, data date, and facility-level waitlist counts by ages 0–5, 6+ and total. Metadata lists XML, real-time update, free and 이용허락범위 제한 없음. Actual response schema and service-specific terms have not been verified; no live request has been made.

## Existing Daegu application

**한국사회보장정보원_대구광역시 어린이집 정보조회 (15101186)**  
https://www.data.go.kr/data/15101186/openapi.do

User submitted a Daegu development application on 2026-11-21; review and credentials are pending. Catalog describes basic facility fields (name/code/address/contact/homepage/capacity), not waitlist counts. Keep it as a possible facility metadata source, not the waitlist feed.

## Regional aggregate comparator

**인천광역시 남동구_어린이집 입소대기현황 (15119081)**  
https://www.data.go.kr/data/15119081/fileData.do

Annual CSV with regional facility/capacity/enrollment and waitlist child/application aggregates including/excluding enrolled children. Not facility-level or nationwide; may help validate aggregate definitions or support a future regional trend view.

## Access, license, freshness and geography

- Official portal guidance: development account limited to 50 rows; operating account requires separate application/review and anticipated traffic. Credentials are account/service-specific.
- Catalog pages for 15101154 and 15101186 list real-time update metadata and unrestricted reuse. Confirm service-specific terms, attribution, caching/redistribution and commercial-use conditions before public use.
- Real-time metadata is not a row-level freshness guarantee. Use source data-date and collection timestamp separately; never fabricate either.
- Official FAQ says portal regional type/count lookup is city/county/district only, legal-dong/admin-dong may differ, and facility coordinates are EPSG:5181/TM. Validate exact fields and transform to WGS84 before map use as needed.
- Dong summaries require validated address/coordinate-to-boundary mapping with documented boundary source.

## Integration blockers

- Nationwide waitlist API development application (15101154) not yet submitted/approved by user.
- Existing Daegu development application (15101186) pending and may not contain waitlist fields.
- Exact national API endpoint, operation, query parameters, pagination, error schema, sample payload and coordinate encoding are unverified.
- Facility ID stability, null semantics, source-date meaning, and total-vs-age-bucket consistency require sample validation.
- Service-specific terms and attribution/public/commercial reuse conditions must be confirmed.

## Work completed

- FastAPI backend scaffold with configurable endpoint, server-side key handling, JSON/XML parser, normalized field mapping, health/data routes.
- Frontend prefers configured official API and otherwise clearly labels fictional demo values.
- Backend normalization tests and GitHub Actions workflow exist.
- Backend exposes `wait_total_consistent` as a nullable quality diagnostic for comparing an official total against a complete age-bucket sum; it does not alter the reported total.
- Documentation distinguishes the nationwide waitlist candidate from the submitted Daegu facility-metadata application.
- No credentials stored; live API connection is not complete.

## Next actions

1. User applies for development access to nationwide waitlist API 15101154; keep the Daegu application for metadata if useful.
2. After approval, obtain official guide and a redacted sample; confirm URL, parameters, response/error schema and development 50-row cap.
3. Test parsing and validate IDs, nulls, duplicate facilities, age buckets/total consistency, coordinates and dates.
4. Record service-specific license/terms and attribution before public display or redistribution.
5. Establish canonical facility and administrative-region IDs; document legal-dong/admin-dong mapping and coordinate transformation.
6. Design snapshot/history storage, then connect live data only after schema, quality and reuse gates pass.
7. Apply for operating access when tests and traffic estimates are ready; deploy only with user approval.

## First API test acceptance checklist
- [ ] Confirm stable facility identifiers; normalized rows flag missing IDs and duplicates within the returned batch, while preserving rows for review.

- [ ] Key only in local backend environment or approved secret storage; never in frontend or repository.
- [ ] One successful request; redacted sample saved for review.
- [ ] Provider errors and valid empty results distinguished.
- [ ] Stable facility IDs or explicit missing-ID flags.
- [ ] Waitlist values are non-negative integers; blanks remain null; age-sum derived only when all buckets are present.
- [ ] Compare waitlist total with age buckets; retain the official total and expose consistency diagnostics rather than silently overwrite.
- [ ] Coordinates and administrative fields validated; coordinate system confirmed and transformed as needed.
- [ ] Source, record date, and collection timestamp shown separately.
- [ ] Service-specific reuse terms documented before public display/redistribution.
- [ ] Unit tests run and result recorded.
