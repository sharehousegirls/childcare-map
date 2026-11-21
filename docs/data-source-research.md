# Data Source Research — Initial Findings

**Research date:** 2026-11-21  
**Status:** Initial investigation; no live API integration performed.

## Findings

### 1. Childcare Disclosure Portal API
- Official portal provides childcare disclosure data via file downloads and REST/SOAP APIs.
- API use requires application and issued key.
- Developer account responses are limited to 50 rows.
- Production account requires a separate review/application and anticipated traffic information; approval is required.
- API use may be restricted for commercial use depending on API policy. Verify the specific endpoint's terms before use.

Official references:
- API overview: https://info.childcare.go.kr/info_html5/oais/introduction/Intro.jsp
- API use policy / account process: https://info.childcare.go.kr/info_html5/oais/introduction/Policy.jsp
- Open API listing: https://info.childcare.go.kr/info/oais/openapi/OpenApiInfoSl.jsp

### 2. Geographic granularity risk
- The portal FAQ states that its Open API can query childcare facility types/counts by city/county/district, but not by administrative dong.
- The FAQ also warns that legal-dong and administrative-dong naming can differ, causing search/matching issues.
- Dong-level analysis therefore needs an additional validated address/geocoding and administrative-boundary mapping strategy; it cannot be assumed from the portal API alone.

Official reference:
- FAQ: https://info.childcare.go.kr/info_html5/cera/community/faqboard/FaqBoardSlPL.jsp

### 3. Waitlist data availability
- The initial research confirms public childcare facility disclosure APIs, but does **not** yet confirm an openly reusable endpoint that provides facility-level, current waitlist counts and age-specific waitlist counts nationwide.
- This is the critical data-source blocker to validate next. Do not substitute facility counts, enrollment, or capacity for waitlist counts.

### 4. General annual statistics
- Ministry of Health and Welfare annual childcare facility data exists through the Public Data Portal, with annual update cadence and reuse terms listed on the dataset page.
- This can be a baseline source for facility-level/region-level context, but it is not a substitute for live waitlist data.

Reference:
- https://www.data.go.kr/data/15128034/fileData.do

## Recommended next steps
1. Inspect API documentation and available fields for facility IDs, location, coordinates, type, capacity/enrollment, and freshness.
2. Determine whether facility-level waitlist and age-specific counts are available from an official public source and whether reuse/redistribution is permitted.
3. If waitlist data is not public or not reusable, stop before scraping authenticated/private child or guardian data; assess lawful alternative public aggregates.
4. Validate data on a small geographic sample, including legal-dong vs administrative-dong mapping.
5. Only after schema, licensing, and source freshness are verified, design ingestion and snapshot tables.

## Current conclusion
Nationwide facility mapping is technically feasible. Nationwide dong-level waitlist analytics remain **unverified** because the public API's documented granularity and available waitlist fields have not yet been confirmed. No real data has been connected and no API credentials have been requested or stored.


## Verified catalog update — 2026-11-21

### Nationwide facility waitlist candidate
**한국사회보장정보원_어린이집별 기본정보 조회 (15101154)** — official catalog: https://www.data.go.kr/data/15101154/openapi.do
The official catalog lists facility identity/location, capacity/enrollment, data-date, age-based waitlist fields for ages 0–5 and 6+, and waitlist total. Metadata: XML, real-time update, free, and 이용허락범위 제한 없음. This is the strongest official catalog candidate for facility-level waitlist mapping. These are catalog-listed fields, not a tested API payload; exact endpoint, operation, request parameters, response nesting, coordinate encoding, and service-specific reuse terms still need the official guide/sample.

### Existing Daegu application is a different dataset
**한국사회보장정보원_대구광역시 어린이집 정보조회 (15101186)** — https://www.data.go.kr/data/15101186/openapi.do
Catalog description lists facility name/code/address/phone/fax/homepage/capacity, but does not list waitlist fields. User submitted a Daegu development application on 2026-11-21; the application screen showed REST/XML but no successful response or credentials yet. Treat it as facility metadata, not the waitlist feed.

### Regional aggregate comparator
**인천광역시 남동구_어린이집 입소대기현황 (15119081)** — https://www.data.go.kr/data/15119081/fileData.do
CSV with reference date, facility/capacity/enrollment totals, waitlisted facility counts and child/application counts including/excluding enrolled children. Annual update; district aggregate only, not facility-level or nationwide. Catalog lists free and 이용허락범위 제한 없음.

### Reuse and freshness caveats
Catalog pages for 15101154 and 15101186 list unrestricted reuse and real-time metadata, but service-specific terms, attribution, caching/redistribution and commercial-use conditions must still be recorded before publication. A real-time update label is not proof every facility record is current; preserve the API data-date when available.

### Geographic validation
Official FAQ: https://info.childcare.go.kr/info_html5/cera/community/faqboard/FaqBoardSlPL.jsp
- Portal regional type/count lookup is city/county/district level, not administrative-dong.
- Legal-dong and administrative-dong names can differ.
- FAQ identifies facility coordinates as EPSG:5181/TM; verify the exact returned coordinate fields and convert to WGS84 before using a map that expects latitude/longitude.

### Updated conclusion and action
Waitlist data is now a plausible official catalog source (15101154), so initial source discovery is advanced. The Daegu application (15101186) appears to be basic facility metadata and cannot be assumed to supply waitlist counts. The user should separately apply for nationwide API 15101154 development access. Do not configure live ingestion until its official guide/sample and service terms are verified. No live API connection exists.
