# Data Source Research — Verified Catalog Findings

**Research date:** 2026-11-21  
**Status:** Facility-level waitlist data is documented in an official catalog candidate; schema/sample and service-specific terms remain unverified. No live API request has been made.

## 1. Primary waitlist candidate: nationwide facility-level data

**한국사회보장정보원_어린이집별 기본정보 조회 (dataset 15101154)**  
Official catalog: https://www.data.go.kr/data/15101154/openapi.do

The official catalog describes a nationwide XML OpenAPI dataset and lists facility identity/location, capacity/enrollment, data-date, age-related facility/child counts, and facility-level waitlist fields for ages 0–5, age 6+, and total.

Catalog metadata:
- Provider: 한국사회보장정보원
- Format: XML
- Update cycle: real-time
- Cost: free
- License field: 이용허락범위 제한 없음

This is the strongest official catalog candidate for the core waitlist map. The listed fields are catalog evidence, not a tested payload. Verify the exact service URL/operation, request parameters, response nesting and field names, pagination, coordinate encoding, data-date semantics and service-specific terms from the official guide/sample before configuring the adapter or displaying data.

## 2. Existing Daegu application: basic facility data

**한국사회보장정보원_대구광역시 어린이집 정보조회 (dataset 15101186)**  
Official catalog: https://www.data.go.kr/data/15101186/openapi.do

The catalog description lists Daegu facility name, facility code, address, phone, fax, homepage and capacity; it does not list waitlist counts. Catalog metadata lists XML/LINK, real-time update and 이용허락범위 제한 없음.

The user submitted a Daegu-only development application on 2026-11-21. The application screen shows REST/XML and an endpoint URL, but no successful response or credentials have been received. Treat this as a possible facility-information source, not as the confirmed waitlist feed.

## 3. Regional aggregate comparator

**인천광역시 남동구_어린이집 입소대기현황 (dataset 15119081)**  
Official catalog: https://www.data.go.kr/data/15119081/fileData.do

The dataset lists reference month/date, facility/capacity/enrollment totals, waitlisted facility counts and child/application waitlist counts including and excluding enrolled children. It is annual CSV, district-level aggregate, not facility-level or nationwide. Catalog metadata lists free and 이용허락범위 제한 없음. Potential use: validate aggregate definitions or a regional trend feature, not facility pins.

## 4. API access and limits

Official guidance:
- API overview: https://info.childcare.go.kr/info_html5/oais/introduction/Intro.jsp
- Use policy/account process: https://info.childcare.go.kr/info_html5/oais/introduction/Policy.jsp
- Development guide: https://info.childcare.go.kr/info_html5/oais/guide/Development.jsp
- API listing: https://info.childcare.go.kr/info/oais/openapi/OpenApiInfoSl.jsp

Development account response limit: 50 rows. Operating account requires separate application/review and traffic estimate. Credentials are account/service-specific.

## 5. Reuse, commercial use, and freshness

Catalog pages for 15101154 and 15101186 list **이용허락범위 제한 없음** and real-time update metadata. This is positive evidence, but before public/commercial display record the service-specific terms, attribution requirements, caching/redistribution conditions, and any restrictions shown in the service guide/application. Do not assume general portal policy overrides service-specific terms.

A catalog real-time update designation is not a row-level freshness guarantee. Preserve the source data-date when present and record collection time separately; never fabricate dates.

## 6. Geographic and coordinate validation

Official FAQ: https://info.childcare.go.kr/info_html5/cera/community/faqboard/FaqBoardSlPL.jsp
- Portal regional type/count lookup supports city/county/district, not administrative-dong.
- Legal-dong and administrative-dong names can differ.
- FAQ identifies facility coordinates as EPSG:5181/TM. Verify exact returned fields, units and system in the sample. Convert projected coordinates to WGS84 before using a map that expects latitude/longitude.
- Dong-level summaries need validated address/coordinate-to-administrative-boundary mapping and a documented boundary source.

## 7. Data interpretation and quality rules

- Waitlist child counts and application counts are distinct; retain separately when available.
- Do not assume a child is unique across multiple facility waitlists.
- Missing waitlist values remain unknown/null, never zero.
- Do not predict admission dates.
- Validate facility IDs, duplicates, region names, coordinates, age buckets, total consistency and date semantics before public use.
- Never scrape authenticated/private child or guardian information or bypass access controls.

## Recommended next steps

1. Apply for nationwide waitlist API 15101154 development access; retain the existing Daegu 15101186 application for basic facility metadata if useful.
2. Obtain official service guide and a redacted sample response; confirm URL, parameters, error codes, pagination, 50-row cap and coordinate system.
3. Validate a small sample: stable IDs, duplicate rate, coordinate validity, null semantics, waitlist fields, age-bucket/total consistency and source dates.
4. Verify service-specific reuse/attribution/redistribution/commercial terms before public display.
5. Design normalized schema and snapshot/history tables only after schema and permissions are confirmed.
6. Connect live data only after the above gates pass.

## Current conclusion

Facility-level waitlist data is plausible and documented in official catalog 15101154; source discovery has advanced. The user's Daegu application 15101186 appears to provide basic facility fields, not waitlist counts. The nationwide waitlist API request schema, actual response, semantics, coordinate handling and service-specific reuse terms remain unvalidated. No real data is connected.
