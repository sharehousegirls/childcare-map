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

## Next steps

1. Obtain development access and the service-specific technical document.
2. Export a redacted sample response (remove credentials and any personal information).
3. Confirm exact fields, response envelope, paging, errors, source-date semantics, ID stability, and coordinate system.
4. Review service-specific commercial/redistribution and attribution conditions.
5. Only then configure a mapping and run a bounded validation batch. Keep live ingestion disabled until the mapping and terms review pass.
