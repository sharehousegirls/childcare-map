import { test } from "node:test";
import assert from "node:assert/strict";
import { buildSavedRegionComparison } from "../saved-region-comparison.mjs";

const saved = (region) => ({ id: `saved-${region}`, region });

test("keeps saved order and exposes valid demo metrics without claiming coverage", () => {
  const rows = buildSavedRegionComparison([
    { name: "안성시", facilities: 42, waiting: 318, avg: 7.6, zero: 11 },
    { name: "대구 수성구", facilities: 56, waiting: 426, avg: 8.1, zero: 14 },
  ], [saved("대구 수성구"), saved("안성시")]);
  assert.deepEqual(rows.map((row) => row.region), ["대구 수성구", "안성시"]);
  assert.equal(rows[0].waiting, 426);
  assert.equal(rows[0].coverage, null);
  assert.equal(rows[0].demo, true);
});

test("marks a live total complete only when all facilities have confirmed counts", () => {
  const [row] = buildSavedRegionComparison([
    { name: "지역 A", facilities: 3, waiting: 8, avg: 2.67, zero: 1, waitingFacilities: 3, missingWaitlistFacilities: 0, waitTotalComplete: true },
  ], [saved("지역 A")], { liveData: true });
  assert.equal(row.coverage, 1);
  assert.equal(row.missingWaitlistFacilities, 0);
  assert.equal(row.totalComplete, true);
  assert.equal(row.partial, false);
});

test("marks partial live totals and derives coverage from known facility rows", () => {
  const [row] = buildSavedRegionComparison([
    { name: "지역 A", facilities: 4, waiting: 7, avg: 3.5, zero: 1, waitingFacilities: 2, missingWaitlistFacilities: 2, waitTotalComplete: false },
  ], [saved("지역 A")], { liveData: true });
  assert.equal(row.coverage, 0.5);
  assert.equal(row.missingWaitlistFacilities, 2);
  assert.equal(row.totalComplete, false);
  assert.equal(row.partial, true);
});

test("keeps an unknown wait total as null instead of zero", () => {
  const [row] = buildSavedRegionComparison([
    { name: "지역 A", facilities: 2, waiting: null, avg: null, zero: 0, waitingFacilities: 0, missingWaitlistFacilities: 2, waitTotalComplete: false },
  ], [saved("지역 A")], { liveData: true });
  assert.equal(row.waiting, null);
  assert.equal(row.average, null);
  assert.equal(row.coverage, 0);
  assert.equal(row.totalComplete, false);
});

test("reports a saved region missing from the current data", () => {
  const [row] = buildSavedRegionComparison([], [saved("삭제된 지역")]);
  assert.equal(row.available, false);
  assert.match(row.reason, /현재 데이터/);
});

test("reports ambiguous duplicate region names instead of choosing one", () => {
  const [row] = buildSavedRegionComparison([
    { name: "지역 A", facilities: 1, waiting: 2, avg: 2, zero: 0 },
    { name: "지역 A", facilities: 2, waiting: 3, avg: 1.5, zero: 1 },
  ], [saved("지역 A")]);
  assert.equal(row.available, false);
  assert.match(row.reason, /중복/);
});

test("ignores malformed saved entries and duplicate saved region names", () => {
  const rows = buildSavedRegionComparison(
    [{ name: "지역 A", facilities: 1, waiting: 2, avg: 2, zero: 0 }],
    [null, {}, saved(" "), saved("지역 A"), saved("지역 A")],
  );
  assert.equal(rows.length, 1);
});

test("rejects non-array inputs", () => {
  assert.throws(() => buildSavedRegionComparison({}, []), TypeError);
  assert.throws(() => buildSavedRegionComparison([], {}), TypeError);
});

test("invalid metrics stay unknown and impossible zero-wait counts are rejected", () => {
  const [row] = buildSavedRegionComparison([
    { name: "지역 A", facilities: -1, waiting: Infinity, avg: -2, zero: 8, waitingFacilities: 5, missingWaitlistFacilities: 0 },
  ], [saved("지역 A")], { liveData: true });
  assert.equal(row.facilities, null);
  assert.equal(row.waiting, null);
  assert.equal(row.average, null);
  assert.equal(row.zeroWaitFacilities, null);
  assert.equal(row.coverage, null);
});

test("zero-facility regions do not show a coverage percentage", () => {
  const [row] = buildSavedRegionComparison([
    { name: "지역 A", facilities: 0, waiting: 0, avg: null, zero: 0, waitingFacilities: 0, missingWaitlistFacilities: 0, waitTotalComplete: true },
  ], [saved("지역 A")], { liveData: true });
  assert.equal(row.coverage, null);
  assert.equal(row.totalComplete, false);
});


test("rejects coverage metadata whose known and missing counts do not reconcile", () => {
  const [row] = buildSavedRegionComparison([
    { name: "지역 A", facilities: 4, waiting: 7, avg: 3.5, zero: 1, waitingFacilities: 2, missingWaitlistFacilities: 1, waitTotalComplete: false },
  ], [saved("지역 A")], { liveData: true });
  assert.equal(row.coverage, null);
  assert.equal(row.knownFacilities, null);
  assert.equal(row.missingWaitlistFacilities, null);
  assert.equal(row.totalComplete, false);
  assert.equal(row.partial, false);
});


test("rejects negative declared missing-facility counts", () => {
  const [row] = buildSavedRegionComparison([
    { name: "지역 A", facilities: 3, waiting: 5, avg: 2.5, zero: 0, waitingFacilities: 2, missingWaitlistFacilities: -1 },
  ], [saved("지역 A")], { liveData: true });
  assert.equal(row.coverage, null);
  assert.equal(row.totalComplete, false);
});
