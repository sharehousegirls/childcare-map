# Official API catalog and policy recheck — 2026-11-24

## Nationwide waitlist candidate

**Dataset:** 한국사회보장정보원_어린이집별 기본정보 조회 (15101154)  
**Official catalog:** https://www.data.go.kr/data/15101154/openapi.do

Direct catalog page re-opened on 2026-11-24. The catalog description lists facility name/code, address, coordinates, capacity/enrollment, data-date, and age-specific facility/child counts, including waitlist counts for ages 0–5, age 6+, and total. It describes the feed as XML, LINK, free, real-time update metadata, and `이용허락범위 제한 없음`.

These are catalog claims, not a tested XML payload. Do not configure live field mappings based on catalog wording alone. Exact request/response nesting, operation, pagination, errors, row limits, null semantics, stable facility ID, coordinate fields/CRS/axis order, and source-date behavior remain unverified.

## Official service specification

The development guide says the service specification is available from the API detail page's Technical Documents area. It includes:
- service overview and provider details
- service URL
- operation list
- operation request/response messages
- request/response examples

Guide: https://info.childcare.go.kr/info_html5/oais/guide/Development.jsp

The public guide itself does not identify the exact service operation/schema for the dataset in a way that replaces the service-specific technical document and a redacted successful response.

## Access policy recheck

Official policy page: https://info.childcare.go.kr/info_html5/oais/introduction/Policy.jsp

- Development account: first testing stage, result limited to 50 rows, no stated expiration.
- Operating account: separately applied/reviewed; expected traffic must be registered.
- Operating account validity: 12 months; renewal is required when continued use is needed.
- Keys are issued per service account after approval.
- API use can be restricted for commercial use where commercial permission is not granted, traffic overload, or improper use.

## Reuse interpretation

The catalog's unrestricted-reuse field is encouraging but not treated as blanket permission for commercial display, caching, bulk redistribution, or republishing the raw response. The exact service-specific conditions, attribution, caching and redistribution policy must still be reviewed and documented before launch.

## Evidence

- Catalog: https://www.data.go.kr/data/15101154/openapi.do
- Development guide: https://info.childcare.go.kr/info_html5/oais/guide/Development.jsp
- API policy: https://info.childcare.go.kr/info_html5/oais/introduction/Policy.jsp

## Catalog field inventory (verified 2026-11-24)

The public catalog page's field description was re-opened on 2026-11-24. This inventory is a **catalog-level list only**; it does not establish XML element names, nesting, operation parameters, paging, null/blank conventions, or a verified field map.

Source: https://www.data.go.kr/data/15101154/openapi.do

### Relevant field groups

| Group | Catalog-described fields | Intended use |
|---|---|---|
| Identity / location | 시도명, 시군구명, 어린이집코드, 어린이집명, 어린이집유형, 운영현황, 우편번호, 상세주소, 시설 위도/경도, 데이터기준일자 | Facility identity, filters, source date and location |
| Facility summary | 정원, 현원, 보육실수/면적, 놀이터수, CCTV 설치수, 보육교직원수, 통학차량운영여부, 인가/휴지/폐지일자, 제공서비스 | Optional context only; collect/display only fields needed for the product |
| Classes | 반수 by ages 0–5, mixed infant (0–2), mixed preschool (3–5), special-needs, total | Context; not a waitlist count |
| Enrolled children | 아동수 by ages 0–5, mixed infant/preschool, special-needs, total | Context; do not mix with waitlist fields |
| Staff | Staff-tenure buckets, role counts and total | Out of initial waitlist-map scope unless a later feature justifies it |
| Waitlist | 입소대기아동수 0세–5세, 6세 이상, 총계 | Primary metrics; blanks remain unknown, not zero |

Representative-name and other nonessential fields are not required by the waitlist map; avoid collecting them by default (data minimization).

### Normalized mapping candidates (all UNVERIFIED)

| Normalized field | Catalog meaning | Required evidence before mapping |
|---|---|---|
| facility_id | 어린이집코드 | Exact response field, stability and duplicate behavior |
| name | 어린이집명 | Exact response field |
| type / status | 어린이집유형 / 운영현황 | Exact field and category values |
| sido / sigungu / address | 시도명 / 시군구명 / 상세주소 | Exact fields and code/label semantics |
| data_date | 데이터기준일자 | Format, whether facility-level and update meaning |
| latitude / longitude | 시설 위도/경도 | Exact field names, units, CRS and axis order |
| capacity / enrolled | 정원 / 현원 | Exact field names, missing-value behavior |
| wait_0 … wait_5 / wait_6_plus / wait_total | Age buckets and total | Exact fields, null semantics, total definition and consistency |

Do not configure `API_FIELD_MAP` from this table. The portal FAQ currently describes EPSG:5181 TM coordinates for the childcare map, while the catalog labels facility coordinate fields as latitude/longitude. Confirm the actual feed's coordinate values and CRS before transforming or assigning normalized latitude/longitude; range checks alone do not establish a correct map pin.

### Import validation acceptance criteria

- A redacted response and service specification confirm operation, response envelope, exact field names, pagination, request limit, and errors.
- Facility IDs are nonblank and stable; duplicates are checked across the entire paginated batch, not just individual pages.
- Waitlist values are nonnegative integers; blank/unknown values are never zero-filled.
- Reported total and age-bucket sum are kept distinct; compare only when all seven age buckets are present.
- Source data date and collection timestamp are preserved separately; mixed dates and date coverage are reported.
- Coordinates are transformed only after CRS/axis order is verified; incomplete or invalid pairs remain unmapped and counted.
- Unknown facility/region mappings are retained for review, not silently assigned.
- No API call, ingestion, caching, or public redistribution until access and terms are reviewed.

## Next steps

1. Obtain development access and the service-specific technical document.
2. Export a redacted sample response (remove credentials and any personal information).
3. Confirm exact fields, response envelope, paging, errors, source-date semantics, ID stability, and coordinate system.
4. Review service-specific commercial/redistribution and attribution conditions.
5. Only then configure a mapping and run a bounded validation batch. Keep live ingestion disabled until the mapping and terms review pass.
