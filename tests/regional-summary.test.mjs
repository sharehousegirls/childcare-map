import { test } from "node:test";
import assert from "node:assert/strict";
import { buildRegions } from "../regional-summary.mjs";

test("live region labels are province-first and group correctly", () => {
  const groups = buildRegions([{ sido: "대구광역시", sigungu: "수성구", waiting: 2 }]);
  assert.equal(groups[0].name, "대구광역시 수성구");
  assert.equal(groups[0].district, "대구광역시");
});

test("all unknown wait counts remain null instead of becoming zero", () => {
  const groups = buildRegions([
    { region: "미분류", waiting: null },
    { region: "미분류", waiting: undefined },
  ]);
  assert.equal(groups[0].waiting, null);
  assert.equal(groups[0].zero, 0);
  assert.equal(groups[0].avg, null);
  assert.equal(groups[0].missingWaitlistFacilities, 2);
  assert.equal(groups[0].coverage, 0);
  assert.equal(groups[0].waitTotalComplete, false);
});

test("partial totals and averages only use confirmed wait counts", () => {
  const groups = buildRegions([
    { region: "A", waiting: 3 },
    { region: "A", waiting: 0 },
    { region: "A", waiting: null },
  ]);
  const group = groups[0];
  assert.equal(group.waiting, 3);
  assert.equal(group.waitingFacilities, 2);
  assert.equal(group.missingWaitlistFacilities, 1);
  assert.equal(group.avg, 1.5);
  assert.equal(group.zero, 1);
  assert.equal(group.zeroWaitRate, 0.5);
  assert.equal(group.coverage, 2 / 3);
  assert.equal(group.waitTotalComplete, false);
});

test("confirmed zero values are valid and preserve zero total", () => {
  const group = buildRegions([{ region: "A", waiting: 0 }, { region: "A", waiting: 0 }])[0];
  assert.equal(group.waiting, 0);
  assert.equal(group.zero, 2);
  assert.equal(group.avg, 0);
  assert.equal(group.zeroWaitRate, 1);
  assert.equal(group.waitTotalComplete, true);
});

test("negative, nonnumeric and nonfinite wait values count as unknown", () => {
  const group = buildRegions([
    { region: "A", waiting: -1 },
    { region: "A", waiting: "0" },
    { region: "A", waiting: Number.NaN },
  ])[0];
  assert.equal(group.waiting, null);
  assert.equal(group.waitingFacilities, 0);
  assert.equal(group.missingWaitlistFacilities, 3);
});

test("fallback region labels are grouped and results are sorted", () => {
  const groups = buildRegions([
    { region: "대구 수성구", waiting: 1 },
    { region: "경기도 성남시", waiting: 2 },
    { region: "대구 수성구", waiting: 4 },
  ]);
  assert.deepEqual(groups.map(group => group.name), ["경기도 성남시", "대구 수성구"]);
  assert.equal(groups[1].waiting, 5);
});

test("aggregation does not mutate input records", () => {
  const rows = [{ sido: "대구광역시", sigungu: "수성구", waiting: 0, extra: { value: 1 } }];
  const before = structuredClone(rows);
  buildRegions(rows);
  assert.deepEqual(rows, before);
});

test("non-array input is rejected", () => {
  assert.throws(() => buildRegions({}), TypeError);
});
