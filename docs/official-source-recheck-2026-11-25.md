# Official source recheck — 2026-11-25

## Nationwide childcare waitlist candidate

**Dataset:** 한국사회보장정보원_어린이집별 기본정보 조회 (15101154)  
**Catalog:** https://www.data.go.kr/data/15101154/openapi.do

The official catalog was re-opened on 2026-11-25. It describes a nationwide facility-level XML/LINK OpenAPI source with facility identifiers, names, region/address, coordinates, capacity/enrollment, source data date, and age-specific waitlist fields (0–5, age 6+, and total). Catalog metadata states free access, real-time update metadata, and `이용허락범위 제한 없음`; the page lists its last modification date as 2025-08-20.

**Interpretation and remaining gate:** The unrestricted-reuse catalog field is positive evidence, but this is catalog metadata, not a successful response or service-specific legal/technical review. It does not establish actual row freshness, the exact operation/endpoint, response envelope or field names, pagination, null/blank semantics, ID stability/uniqueness, coordinate CRS/axis order, request limits, error behavior, caching/display requirements, or a blanket commercial/redistribution clearance. No live request was made and no field map was changed.

## Latest MOIS region-code notice found in this recheck

**Notice:** 2026-10-23 effective administrative/legal-dong change, posted 2026-11-18.  
**Official notice:** https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000052&nttId=131063

The notice identifies a new administrative-dong branch office in Jangseong County (Jinwon-myeon). It states that the administrative-dong code is newly created and legal-dong/ri codes are unchanged for this change. Listed attachments include:

- `jscode20261111.zip`
- `jscode20261111(말소코드포함).zip`
- `행정기관(행정동) 및 관할구역(법정동) 코드 Layout.hwpx`

This is the latest change notice found during the 2026-11-25 recheck, not a guarantee that no newer notice exists. The archive was not downloaded or parsed. Its exact attachment reuse/redistribution terms and KOGL mark were not checked, so the region-code import gate remains closed.

## Next steps

1. Obtain the API service technical document and an approved, redacted response sample.
2. Validate actual XML envelope, operation, fields, paging, date/null semantics and facility identifiers offline.
3. Check the exact archive's reuse mark/terms and any service-specific display/cache/commercial conditions.
4. Download the official region archive only after terms are verified; preserve source version, effective date, digest and attribution.
5. Validate hierarchy and crosswalk independently; do not join legal/admin regions by name or infer dong-level statistics without verified boundary/coordinate assignment.

## Evidence links

- Nationwide waitlist catalog: https://www.data.go.kr/data/15101154/openapi.do
- MOIS 2026-10-23 effective change notice: https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000052&nttId=131063
- Statistics Korea/SIGIS administrative-region classification notes: https://sgis.mods.go.kr/html/attachFiles/%ED%95%9C%EA%B5%AD%ED%96%89%EC%A0%95%EA%B5%AC%EC%97%AD%EB%B6%84%EB%A5%98%20%ED%95%B4%EC%84%A4%EC%84%9C%282021.12.28.%29.pdf

