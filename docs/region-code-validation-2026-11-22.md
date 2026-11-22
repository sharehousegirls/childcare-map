# Region-code validation scaffold — 2026-11-22

## Scope

`backend/app/regions.py` is a **normalized-record validator and tree builder**, not an official-code downloader/importer. It deliberately makes no assumption about code length or numeric format. Official code strings (including leading zeroes) must be preserved.

## Official sources checked

- **Ministry of the Interior and Safety (MOIS), 2026-10-23 effective administrative/legal-dong change notice**, posted 2026-11-18: the notice identifies a new Jinwon-myeon branch office in Jangseong County and says the legal-dong codes are unchanged for that change. It lists `jscode20261111.zip`, the version with abolished codes, and a layout file. Use the notice and its official files as the starting point for the next code-data review; do not assume they remain the latest without checking the MOIS/code-change board first. https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000052&nttId=131063
- **MOIS standardized legal-dong code API, data catalog 15077871**: `region_cd`, `sido_cd`, `sgg_cd`, `umd_cd`, `ri_cd`, `locatadd_nm`, `locathigh_cd`, and related fields are documented. It is a legal-dong code source; do not treat it as an administrative-dong dataset. Catalog says free and unrestricted reuse, but check service-level conditions before deployment. https://www.data.go.kr/data/15077871/openapi.do
- **Statistics Korea/SIGIS administrative-region classification guide (2021-12-28)**: administrative-dong and legal-dong are not a reliable 1:1 name/code crosswalk; most relationships are M:N, and matching names do not guarantee matching boundaries. Keep an explicit crosswalk with provenance and valid dates rather than joining by name. https://sgis.mods.go.kr/html/attachFiles/%ED%95%9C%EA%B5%AD%ED%96%89%EC%A0%95%EA%B5%AC%EC%97%AD%EB%B6%84%EB%A5%98%20%ED%95%B4%EC%84%A4%EC%84%9C%282021.12.28.%29.pdf
- MOIS code-change board: https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardList.do?bbsId=BBSMSTR_000000000052

## Normalized validator contract

Each record accepts:

- `region_id`, `name`, `region_type` (required strings)
- `parent_region_id` (nullable)
- `source_system` and `source_code` (both present or both null; code is a string)
- `is_active` (true/false/null; null means status is unknown)

Initial supported types and parent rules:

- `sido`: root only
- `sigungu`: parent `sido`
- `admin_dong`, `legal_dong`, `eup`, `myeon`: parent `sigungu`
- `ri`: parent `eup` or `myeon`

These parent rules are intentionally conservative and are **not yet verified against the full current official files**. If the official dataset contains a legitimate exception, inspect and revise the normalized model instead of weakening validation or silently forcing the row into this tree.

`validate_region_records(records)` aggregates structural issues and returns normalized rows only when valid. It checks required strings, type allowlist, ID/code duplicates, parent existence/type, root rules, cycles and active-child/inactive-parent contradictions. Source codes are unique within `source_system`; their format and length are not guessed.

`build_region_tree(records)` returns deterministic nested `children` arrays sorted by region type, name and ID. It does not create legal-dong/admin-dong crosswalks.

## Crosswalk and geometry gate

Before dong-level facility assignment or map aggregation:

1. Download and archive the official current code file and layout with version/effective date.
2. Parse and validate code strings, status/abolition fields and parent codes; keep deleted rows in a separate historical table.
3. Confirm administrative and legal-dong versions independently.
4. Build a versioned M:N crosswalk using official jurisdiction/boundary evidence; do not join on names alone.
5. Verify boundary source/license, coordinate reference system, axis order and address/coordinate assignment.
6. Preserve source region code, internal ID, crosswalk version and valid-from/to dates on each mapping.
7. Require manual review for unresolved or many-to-many cases before marking coverage complete.

## Acceptance criteria

- Valid synthetic hierarchy validates and tree output is deterministic.
- Duplicate IDs/codes, missing parents, invalid parent types, root errors, cycles and active/inactive contradictions are rejected.
- Leading zeroes in source codes survive normalization.
- Input records are not mutated.
- No official code rows are imported or represented as verified in this change.

## Test status

- **PASS (isolated local harness):** 18 region-validator tests and `py_compile`.
- **PASS — GitHub Actions run #74:** 44 backend tests, frontend syntax checks and 9 saved-search tests succeeded. https://github.com/sharehousegirls/childcare-map/actions/runs/44968035073
- **FAIL — Run #73:** a temporary test-file edit contained literal escaped newlines and caused a Python syntax error; corrected in commit `eb116b5555b6ef70192302c54b8609eddfa0b658`, verified by run #74.
- No official file parsing, full coverage or dong crosswalk test yet.
- **NOT RUN:** browser/manual UI validation; validator is not wired to a route or selector.
