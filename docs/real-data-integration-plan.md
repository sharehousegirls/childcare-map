# Real-data integration plan

## Primary official source candidate: nationwide waitlist

**한국사회보장정보원_어린이집별 기본정보 조회 (15101154)**  
https://www.data.go.kr/data/15101154/openapi.do

The official catalog lists nationwide facility identity/location, capacity/enrollment, record date, and age waitlist counts 0–5, 6+ and total. Catalog metadata says XML, real-time update, free, and reuse scope unrestricted. This is catalog metadata, not a verified response sample or blanket permission for every use: confirm service-specific API conditions, attribution, caching, public redistribution and commercial/advertising use before service launch or monetization. Reviewed 2026-11-22.

## Existing Daegu application

**한국사회보장정보원_대구광역시 어린이집 정보조회 (15101186)**  
https://www.data.go.kr/data/15101186/openapi.do

User submitted a Daegu development application on 2026-11-21; review and credentials are pending. Catalog describes facility metadata (name/code/address/contact/homepage/capacity), not waitlist counts. Keep it as a possible facility metadata source, not the waitlist feed.

## Regional aggregate comparator

**인천광역시 남동구_어린이집 입소대기현황 (15119081)**  
https://www.data.go.kr/data/15119081/fileData.do

Annual CSV with regional facility/capacity/enrollment and waitlist child/application aggregates including/excluding enrolled children. Not facility-level or nationwide; may help validate aggregate definitions or support a future regional trend view.

## Access, license, freshness and geography

- Official API portal policy: development account is limited to 50 returned rows; operation/account credentials are issued after application and approval. Operating account is separately reviewed, requires expected traffic, is limited to 12 months, and must be renewed. See https://info.childcare.go.kr/info_html5/oais/introduction/Policy.jsp.
- Catalog metadata for 15101154 lists “이용허락범위 제한 없음.” This is catalog-level metadata and does not replace the exact API service specification, terms, attribution and redistribution/commercial-use review. Portal policy explicitly says commercial use of APIs for which commercial use is not allowed may result in restrictions. Commercial/advertising use is **not cleared**.
- The API development guide says the service specification, downloadable from the API detail page, includes service URL, operations, request/response messages and examples. Obtain that official document after access; do not guess endpoints or fields. https://info.childcare.go.kr/info_html5/oais/guide/Development.jsp
- “Real-time” update metadata is not a row-level freshness guarantee. Preserve source data date and actual collection timestamp separately; never fabricate either.
- Existing source FAQ notes regional lookup granularity may be city/county/district and legal-dong/admin-dong can differ; facility coordinates may use EPSG:5181/TM. Confirm exact fields, coordinate system and axis order before mapping or conversion.
- Dong-level summaries require validated address/coordinate-to-boundary mapping with a documented boundary source, version and reuse terms.

## Integration blockers

- Nationwide waitlist API (15101154) development application has not been confirmed as submitted/approved.
- Existing Daegu development application (15101186) is pending and may not contain waitlist fields.
- Exact endpoint, operation, request parameters, response/error schema, pagination, sample payload and null semantics remain unverified.
- Facility ID stability, data-date meaning, total-vs-age-bucket consistency and CRS require sample validation.
- Service-specific terms, attribution, caching, public display/redistribution and commercial/advertising use remain to be confirmed.

## Work completed

- FastAPI backend scaffold with configurable endpoint, server-side key handling, JSON/XML parser, normalized field mapping, health/data routes.
- Frontend prefers configured official API and otherwise clearly labels fictional demo values.
- Backend normalization tests and GitHub Actions workflow exist.
- Backend exposes wait_total_consistent as a nullable quality diagnostic for comparing an official total against a complete age-bucket sum; it does not alter the reported total.
- Facility ID normalization and response-batch duplicate/missing-ID diagnostics; rows are retained for review.
- Documentation distinguishes the nationwide waitlist candidate from the submitted Daegu facility-metadata application.
- Draft relational data model and snapshot/region mapping rules added at docs/data-model-draft.md.
- No credentials stored; live API connection is not complete.

## Next actions

1. User applies for development access to nationwide waitlist API 15101154; keep Daegu application for metadata if useful.
2. After approval, obtain official guide and a redacted sample; confirm URL, parameters, response/error schema and development 50-row cap.
3. Test parsing and validate IDs, nulls, duplicate facilities, age buckets/total consistency, coordinates and dates.
4. Record service-specific reuse terms and attribution before public display/redistribution or commercial use.
5. Establish canonical facility and administrative-region IDs; document legal-dong/admin-dong mapping and coordinate transformation.
6. Implement snapshot/history storage and idempotent ingestion; connect live data only after schema, quality and rights gates pass.
7. Nationwide ingestion, quality checks, map and regional/facility views.
8. Saved regions/facilities/filters/comparisons and historical trends.
9. SEO, accessibility, security, backup and deploy-readiness review (no deployment without user approval).

## First API test acceptance checklist

- [ ] Confirm stable facility identifiers; normalized rows flag missing IDs and duplicates within returned batch, while preserving rows for review.
- [ ] Key only in local backend environment or approved secret storage; never in frontend or repository.
- [ ] One successful request; redacted sample saved for review.
- [ ] Provider errors and valid empty results distinguished.
- [ ] Stable facility IDs or explicit missing-ID flags.
- [ ] Waitlist values are non-negative integers; blanks remain null; age sum derived only when all buckets are present.
- [ ] Compare waitlist total with age buckets; retain official total and expose consistency diagnostics rather than silently overwrite.
- [ ] Coordinates and administrative fields validated; CRS confirmed and transformed as needed.
- [ ] Source, record date, and collection timestamp shown separately.
- [ ] Service-specific reuse terms documented before public display/redistribution/commercial use.
- [ ] Unit tests run and result recorded.
