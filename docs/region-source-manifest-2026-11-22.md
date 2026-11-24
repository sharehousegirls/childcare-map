# Region source manifest and import gates — 2026-11-22

## Why this exists

Before importing official administrative/legal-dong code files, preserve enough provenance to reproduce the source version and avoid publishing data before its reuse conditions are reviewed. This is metadata validation only; it is not an importer and does not establish the legal status of a dataset.

## Current official source checkpoint

As checked on 2026-11-22, the Ministry of the Interior and Safety (MOIS) notice posted 2026-11-18 describes the 2026-10-23 effective administrative-region change and lists:

- `jscode20261111.zip`
- `jscode20261111(말소코드포함).zip`
- `KiKcd_H.20261111`: administrative institution (administrative-dong) codes
- `KiKcd_B.20261111`: legal-dong codes
- `KiKmix.20261111`: administrative-dong codes with legal-dong jurisdiction mapping

The notice says the change created a Jinwon-myeon branch office in Jangseong County; legal-dong codes were unchanged for that change. This is a source-version checkpoint, not an assertion that the archive has been downloaded, parsed, or validated. Recheck the MOIS change board before each import.

- Notice: https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000052&nttId=131063
- Code-change board: https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardList.do?bbsId=BBSMSTR_000000000052

## Manifest contract

`backend/app/region_manifest.py` validates a manifest and exposes two explicit gates:

- `public_import_ready`: reuse review is marked verified, a review date is recorded, and redistribution is explicitly allowed.
- `commercial_use_ready`: public import is ready and commercial use is explicitly allowed.

A verified review with redistribution allowed but commercial use denied can pass the public-import gate; commercial use remains blocked. Pending, unknown, or denied permissions never unlock a gate. The function only validates the recorded fields; a human must verify source terms and the manifest must not be marked verified by default.

Required metadata:
- Manifest version, source system, dataset identifier, and dataset kind
- HTTPS source and terms URLs without embedded credentials
- Archive filename (basename only), SHA-256, effective date, and timezone-aware retrieval timestamp
- Attribution text, review status, redistribution/commercial permission flags, and review date when verified

`verify_file_sha256(path, expected)` streams a local file in 1 MiB chunks and compares the digest. It does not download the archive or prove the source is authentic; the caller must obtain the file from the official source and verify its hash independently.

## Example manifest (review pending; not import-ready)

```json
{
  "manifest_version": 1,
  "source_system": "MOIS",
  "dataset_id": "KiKmix.20261111",
  "dataset_kind": "admin_legal_crosswalk",
  "source_url": "https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000052&nttId=131063",
  "terms_url": "https://www.mois.go.kr/frt/sub/a08/copyrightPolicy/screen.do",
  "file_name": "jscode20261111.zip",
  "sha256": "replace-with-verified-64-character-file-digest",
  "effective_date": "2026-10-23",
  "downloaded_at": "2026-11-22T17:00:00+09:00",
  "attribution": "Source: Ministry of the Interior and Safety (MOIS)",
  "reuse_review_status": "pending",
  "license_reviewed_at": null,
  "redistribution_allowed": null,
  "commercial_use_allowed": null
}
```

## Important legal/source limitation

MOIS website copyright policy says freely reusable MOIS-owned materials are identified with the KOGL Type 1 mark and asks users to consult MOIS before using materials without that mark. A public downloadable archive is not, by itself, blanket permission for republication or commercial use. This policy page does not prove the exact archive is KOGL Type 1 or clarify the archive's terms; those remain pending.

- MOIS copyright policy: https://www.mois.go.kr/frt/sub/a08/copyrightPolicy/screen.do
- MOIS public-data opening page: https://www.mois.go.kr/frt/sub/a02/openInfo_3/screen.do

## Validation coverage

The unit tests cover:
- Pending versus verified import gates
- Separate public and commercial reuse gates
- Required fields, version and dataset-kind allowlists
- HTTPS URLs, malformed URLs, and embedded credentials
- Basename/path-traversal rejection
- SHA-256 format and local digest matching/mismatch
- Effective date format and timezone-aware retrieval time
- Permission field types

The manifest gate must be connected to a future archive importer before any official region file is loaded into public-facing data. Archive parsing, extraction safety, actual MOIS file layout, code/parent relationships, row counts, and administrative/legal-dong crosswalk validation remain separate tasks.

 
## Archive preflight — 2026-11-24

The new `evaluate_region_archive_preflight(manifest, archive_path)` helper combines the manifest's reuse-review state with a local archive check:

- The local basename must exactly match the manifest `file_name`.
- The path must be a regular file and must not be a symbolic link (to avoid unexpected path indirection).
- The check is not atomic with a later read or extraction; the future importer must stage the file safely and keep the verified archive immutable to avoid a time-of-check/time-of-use (TOCTOU) race.
- Its SHA-256 must match the manifest digest.
- Missing, unreadable, mismatched, or wrong-name files keep the combined import gates closed.
- `public_archive_import_ready` requires verified redistribution permission plus a verified local digest.
- `commercial_archive_import_ready` additionally requires explicit commercial-use permission.

This is deliberately still preflight—not an importer. It does not download the source, authenticate provenance, inspect ZIP contents, protect extraction paths, validate the official layout, or verify code/parent/crosswalk relationships. Human source and license review remains required.

**Tests:** six new preflight cases cover pending reuse with a matching digest, verified permissions, digest mismatch, filename mismatch, missing archive, and commercial permission denied.
