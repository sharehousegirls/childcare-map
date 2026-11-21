# Real-data integration plan

## Confirmed source candidate
Official Childcare Disclosure Portal Open API: https://info.childcare.go.kr/info/oais/openapi/OpenApiInfoSl.jsp
The official portal requires signup/login, a development API application/review, and issued credentials. The development account has a 50-row response limit; production access requires a separate application/review and anticipated traffic registration. Review official use policy and restrictions before commercial reuse.

## Potential data fields
Facility code/name/type/status, address, capacity/enrollment, coordinates, age-based waitlist counts (0–6+), total waitlist count, and data date are listed in a catalog entry for the SSIS childcare-facility API. Exact official endpoint and response field names must be confirmed against official documentation/sample response before implementation.

## Integration blockers
- API credentials not yet issued.
- Exact API endpoint and request parameter names not verified.
- Official sample response not yet obtained; field mapping is unverified.
- Data reuse/redistribution and commercial-use terms require checking.

## Work completed
- Added FastAPI backend scaffold with configurable endpoint, API key kept server-side, JSON/XML parsing, normalized field mapping, and health/data routes.
- Existing demo remains available; it must not be represented as live data.

## Next actions
1. Apply for development API access at the official portal and obtain key.
2. Confirm exact API service/operation URL and query parameter names from official docs.
3. Capture a small sample response (up to development account limit) and configure mappings.
4. Test response handling and validate fields, missing values, IDs, waitlist sums, timestamps.
5. Replace demo mode only after successful source validation; then plan production account approval.


## Application and validation status (2026-11-21)
- Development API application submitted for Daegu only; review/approval pending. Credentials have not been issued.
- The application screen lists REST/XML and an API URL, but this is not yet confirmed by a successful request. Do not configure the provider or infer the response schema from the application form alone.
- The official service specification file shown on the application screen must be reviewed, along with a sample response, after access is approved.
- Before connecting, confirm: exact operation URL and required parameters; pagination and 50-row development limit; error envelope/status codes; facility ID stability; missing-value semantics; data-date semantics; terms and redistribution/commercial-use permission.

## Acceptance checklist for first API test
- [ ] Key remains only in local backend environment or approved secret storage; never in browser or repository.
- [ ] One successful request with a redacted sample response saved for mapping review.
- [ ] Provider errors and empty/error payloads are distinguished from valid empty datasets.
- [ ] Normalized records have stable IDs or are explicitly flagged when IDs are missing.
- [ ] Waitlist values are non-negative integers; blanks remain null; total is derived from age buckets only when every bucket is present.
- [ ] Coordinates and administrative region fields are validated before map display.
- [ ] Source and date are shown; date is not guessed when absent.
- [ ] Terms/reuse permission are documented before public display or redistribution.
- [ ] Unit tests run and results recorded before declaring the connection successful.


## Source finding update — 2026-11-21

### Waitlist candidate identified
Official data.go.kr catalog: **한국사회보장정보원_어린이집별 기본정보 조회 (15101154)**, https://www.data.go.kr/data/15101154/openapi.do. Catalog fields include age-based waitlist counts (0–5, 6+) and total, plus facility/location/capacity/enrollment/date. Metadata says XML, real-time, free and 이용허락범위 제한 없음. Schema and actual response remain untested.

### Existing Daegu application
**한국사회보장정보원_대구광역시 어린이집 정보조회 (15101186)**, https://www.data.go.kr/data/15101186/openapi.do. Catalog describes basic facility fields (name/code/address/contact/homepage/capacity), not waitlist counts. Application submitted by user on 2026-11-21; review/key pending. Keep this as a possible facility metadata source, not the waitlist feed.

### Regional aggregate comparator
**인천광역시 남동구_어린이집 입소대기현황 (15119081)**, https://www.data.go.kr/data/15119081/fileData.do. Annual CSV with regional facility/capacity/enrollment and child/application waitlist aggregates including/excluding enrolled children. Not facility-level or nationwide.

### Freshness, license, and spatial caveats
- 15101154/15101186 catalog metadata lists real-time updates and unrestricted reuse, but confirm service-specific terms, attribution, caching/redistribution and commercial-use conditions before public use.
- Real-time catalog cadence is not a row-level freshness guarantee; use source data-date and record collection timestamp separately.
- Official FAQ says portal regional type/count query is city/county/district only, legal-dong/admin-dong can differ, and facility coordinates are EPSG:5181/TM. Validate fields and transform coordinates to WGS84 for map use as needed.

### Required user action
Apply for development access to nationwide waitlist API 15101154. Existing Daegu-only application is not sufficient to establish waitlist fields. API credentials must remain in local backend environment or secret storage, never in chat/email/repository.
