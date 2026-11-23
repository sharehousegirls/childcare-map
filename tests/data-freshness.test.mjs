import test from "node:test";
import assert from "node:assert/strict";
import { formatDataFreshness } from "../data-freshness.mjs";

test("shows latest source date and elapsed calendar days at collection time", () => {
  const result = formatDataFreshness({
    source_data_dates: ["2026-11-22"],
    source_data_date_latest: "2026-11-22",
    source_data_date_earliest: "2026-11-22",
    mixed_source_data_dates: false,
    collected_at: "2026-11-24T05:00:00+00:00",
  });
  assert.equal(result, "최신 기준일 2026-11-22 · 수집 당시 기준일 경과 2일");
});

test("shows a range when facilities have mixed valid source dates", () => {
  const result = formatDataFreshness({
    source_data_dates: ["2026-11-22", "2026-11-24", "2026-11-23"],
    source_data_date_latest: "2026-11-24",
    source_data_date_earliest: "2026-11-22",
    mixed_source_data_dates: true,
    collected_at: "2026-11-24T05:00:00Z",
  });
  assert.match(result, /시설별 기준일 혼재 · 2026-11-22–2026-11-24 \(3개 날짜\)/);
  assert.match(result, /수집 당시 기준일 경과 0일/);
});

test("rejects invalid calendar dates and avoids false age values", () => {
  const result = formatDataFreshness({
    source_data_dates: ["2026-02-30", "not-a-date"],
    collected_at: "2026-03-01T00:00:00Z",
  });
  assert.equal(result, "최신 기준일 확인 불가 · 유효한 날짜 없음");
});

test("flags a source date later than collection date", () => {
  const result = formatDataFreshness({
    source_data_dates: ["2026-11-25"],
    source_data_date_latest: "2026-11-25",
    mixed_source_data_dates: false,
    collected_at: "2026-11-24T23:00:00Z",
  });
  assert.match(result, /수집 시점보다 1일 미래 날짜 \(확인 필요\)/);
});

test("does not calculate elapsed days when collection timestamp is missing", () => {
  const result = formatDataFreshness({ source_data_dates: ["2026-11-24"] });
  assert.equal(result, "최신 기준일 2026-11-24");
});

test("flags inconsistent latest-date metadata", () => {
  const result = formatDataFreshness({
    source_data_dates: ["2026-11-22", "2026-11-24"],
    source_data_date_latest: "2026-11-23",
    source_data_date_earliest: "2026-11-22",
    mixed_source_data_dates: true,
    collected_at: "2026-11-24T05:00:00Z",
  });
  assert.match(result, /기준일 메타데이터 불일치 \(확인 필요\)/);
});

test("flags mixed-date metadata when only one valid date is available", () => {
  const result = formatDataFreshness({
    source_data_dates: ["2026-11-24"],
    source_data_date_latest: "2026-11-24",
    mixed_source_data_dates: true,
  });
  assert.match(result, /기준일 메타데이터 불일치 \(확인 필요\)/);
});

test("reports invalid source-date entries when some valid dates remain", () => {
  const result = formatDataFreshness({
    source_data_dates: ["2026-11-24", "2026-02-30"],
    source_data_date_latest: "2026-11-24",
    mixed_source_data_dates: true,
  });
  assert.match(result, /유효하지 않은 기준일 1개 제외/);
});
