# Nationwide waitlist API schema verification — 2026-11-23

## Status

The public catalog for SSIS dataset **15101154 (한국사회보장정보원_어린이집별 기본정보 조회)** confirms that the nationwide facility record includes waitlist counts by age and a total. This is catalog evidence only. The exact API service specification, XML tag names, response envelope, pagination, null conventions, coordinate fields/CRS and date semantics have **not** been verified from an authenticated service specification or a redacted response sample. No live request was made.

Official catalog: https://www.data.go.kr/data/15101154/openapi.do

Catalog metadata reviewed:
- Provider: 한국사회보장정보원
- Format: XML; delivery type is LINK
- Catalog update date: 2025-08-20
- Catalog update cycle: real-time
- Catalog reuse field: 이용허락범위 제한 없음
- Fee: free

The catalog's update-cycle label is not a freshness SLA for individual facility records. Preserve a provider record date when present and the server collection timestamp separately. Do not synthesize dates.

## Additional catalog-described facility fields

A fresh catalog page review on 2026-11-23 also confirms a broader facility-detail inventory beyond waitlist totals. These are catalog descriptions, not verified response tags or definitions:

- Facility profile: facility code/name/type/status, postal code and address, phone/fax/homepage, room count and room area, playground count, CCTV total, childcare staff count, capacity, enrolled children, latitude/longitude, approval date, temporary suspension start/end, abolition date, data date, and offered services.
- Class counts: age 0–5, mixed infant class (0–2), mixed toddler class (3–5), special-disability class, and total.
- Child counts: age 0–5, mixed infant (0–2), mixed toddler (3–5), special-disability, and total.
- Staff tenure buckets: under 1 year, 1–2 years, 2–4 years, 4–6 years, and 6+ years.
- Staff role counts: director, childcare teacher, special-education teacher, therapy teacher, nutritionist, nurse, nurse assistant, cook, office staff, and total.
- Waitlist: age 0–5, 6+, and total.

Do not add together mixed-class, special-disability, age-bucket, enrollment, or staffing counts unless the official schema definitions prove they are mutually exclusive and comparable. The exact response tags, semantics, null conventions, and update dates for these fields remain unverified.

Official catalog reviewed: https://www.data.go.kr/data/15101154/openapi.do

## Secondary field-name hints (unverified)

A third-party API index was reviewed only as a discovery aid; it is not an official specification and must not be used to configure live field mapping. It lists candidate tags such as `sidoname`, `sigunguname`, `stcode`, `crname`, `crtypename`, `crstatusname`, `craddr`, `Crcapat`, `Crchcnt`, `La`, `Lo`, `datastdrdt`, and waitlist tags `ew_cnt_00`–`ew_cnt_05`, `ew_cnt_m6`, `ew_cnt_tot`.

These names are **unverified** against the provider's service specification or a response sample. Do not add them to `FIELD_ALIASES` or `API_FIELD_MAP` until official evidence confirms each mapping, especially coordinates, totals, and date semantics.

Discovery-only reference: https://infosnake.net/services/opendata/?id=15101154

## Candidate normalized fields (not a confirmed XML schema)

| Normalized field | Catalog-described item | Schema status |
|---|---|---|
| facility_id | 어린이집코드 | Candidate; XML tag unverified |
| name | 어린이집명 | Candidate; XML tag unverified |
| type | 어린이집유형 | Candidate; XML tag unverified |
| status | 운영현황 | Candidate; XML tag unverified |
| sido / sigungu | 시도명 / 시군구명 | Candidate; XML tags unverified |
| address / postal code | 상세주소 / 우편번호 | Candidate; XML tags unverified |
| capacity / enrolled | 정원 / 현원 | Candidate; XML tags unverified |
| latitude / longitude | 시설 위도·경도 | Candidate; exact fields, CRS and axis order unverified |
| data_date | 데이터기준일자 | Candidate; format and meaning unverified |
| wait_0…wait_5 | 입소대기아동수 0세…5세 | Candidate; XML tags and null semantics unverified |
| wait_6_plus | 입소대기아동수 6세 이상 | Candidate; XML tag unverified |
| wait_total | 입소대기아동수-총계 | Candidate; XML tag and definition unverified |

Do not configure API_FIELD_MAP based on Korean catalog labels alone. The provider's actual XML response and specification are the source of truth. Keep missing wait counts as null, never zero; retain the provider-reported total separately from an age-bucket-derived sum; and do not interpret application counts as unique children across facilities.

## Official service specification is the next required artifact

The Childcare Information Disclosure API guide says the service specification is downloadable from the API detail page's technical-document section. It provides the service URL, operations, request/response message definitions and examples.

Official guide: https://info.childcare.go.kr/info_html5/oais/guide/Development.jsp

After the API account is approved, obtain and review the specification and a redacted sample. Verify:
1. exact base URL and operation;
2. required parameters and key parameter name;
3. pagination and result-count behavior;
4. XML envelope, record path and tag names;
5. service-level errors and empty-result semantics;
6. stable facility identifier and duplicates across pages;
7. date format, timezone and meaning;
8. coordinate field names, CRS and axis order;
9. null, blank, sentinel and numeric-range semantics;
10. API service terms, attribution, caching, redistribution and commercial/advertising restrictions.

## Account and traffic constraints

The official API policy states:
- Development accounts are for testing and are limited to 50 returned rows; no usage-period limit is listed.
- Operating accounts require a separate application/review, an expected traffic estimate and a separate issued key.
- Operating accounts are limited to 12 months and need renewal.
- Commercial use of an API that disallows commercial use and traffic excess can trigger usage restrictions.

Official policy: https://info.childcare.go.kr/info_html5/oais/introduction/Policy.jsp

The 50-row development limit is not enough to claim nationwide coverage or validate full pagination/deduplication. Treat development results as sample data only.

## Acceptance gate before live integration

- [ ] Development API account approval and key are available (key stays server-side; never commit it).
- [ ] Service specification and a redacted response sample have been reviewed.
- [ ] Exact request, pagination and response schema are confirmed.
- [ ] Field mapping is tested against the sample, including missing values and numeric parsing.
- [ ] Facility IDs and cross-page duplicate handling are verified.
- [ ] Data-date and collection-time metadata are separate.
- [ ] CRS and axis order are confirmed before map placement.
- [ ] Service-specific reuse, display, caching, attribution, redistribution and commercial terms are reviewed.
- [ ] Quality diagnostics and unmapped rows are retained and reported.
- [ ] No admissions-date prediction is shown.

## Evidence links

- Catalog: https://www.data.go.kr/data/15101154/openapi.do
- Service-spec download instructions: https://info.childcare.go.kr/info_html5/oais/guide/Development.jsp
- API access policy: https://info.childcare.go.kr/info_html5/oais/introduction/Policy.jsp
- Geographic FAQ: https://info.childcare.go.kr/info_html5/cera/community/faqboard/FaqBoardSlPL.jsp
