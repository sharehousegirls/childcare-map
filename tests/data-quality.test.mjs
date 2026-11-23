import test from "node:test";
import assert from "node:assert/strict";
import { formatDataQualityDetails } from "../data-quality.mjs";

const meta = (overrides = {}) => ({
  records_with_source_data_date: 3,
  records_without_source_data_date: 1,
  records_with_parseable_source_data_date: 2,
  records_with_unparseable_source_data_date: 1,
  ...overrides,
});

test("formats coverage and parseability from row counts", () => {
  const result = formatDataQualityDetails(meta(), 4);
  assert.match(result, /기준일 기록 3\/4행 \(75\.0%\)/);
  assert.match(result, /날짜 해석 2\/3행 \(66\.7%\)/);
  assert.match(result, /해석 불가 1행 · 기준일 누락 1행/);
});

test("all-missing dates show zero coverage and no parseability denominator", () => {
  const result = formatDataQualityDetails(meta({
    records_with_source_data_date: 0,
    records_without_source_data_date: 4,
    records_with_parseable_source_data_date: 0,
    records_with_unparseable_source_data_date: 0,
  }), 4);
  assert.match(result, /기준일 기록 0\/4행 \(0\.0%\)/);
  assert.match(result, /날짜 해석 — \(기준일 없음\)/);
});

test("empty facility response does not show a percentage", () => {
  assert.equal(formatDataQualityDetails(meta(), 0), "기준일 진단: 시설 데이터 없음");
});

test("inconsistent metadata counts are not converted to misleading ratios", () => {
  assert.equal(formatDataQualityDetails(meta({ records_without_source_data_date: 9 }), 4), "기준일 진단값 불일치 · 확인 필요");
});

test("missing or invalid counts return a safe fallback", () => {
  assert.equal(formatDataQualityDetails(null, 4), "기준일 진단 정보 없음");
  assert.equal(formatDataQualityDetails(meta({ records_with_source_data_date: -1 }), 4), "기준일 진단 정보 없음");
  assert.equal(formatDataQualityDetails(meta(), NaN), "기준일 진단 정보 없음");
});
