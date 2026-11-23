import { test } from "node:test";
import assert from "node:assert/strict";
import { groupRegionOptions } from "../region-selector.mjs";

test("groups by parent label and sorts groups and child labels in Korean", () => {
  const groups = groupRegionOptions([
    { name: "경기도 수원시 영통구", district: "경기도" },
    { name: "대구광역시 달서구", district: "대구광역시" },
    { name: "대구광역시 수성구", district: "대구광역시" },
  ]);
  assert.deepEqual(groups.map((group) => group.parent), ["경기도", "대구광역시"]);
  assert.deepEqual(groups[1].options.map((option) => option.label), ["달서구", "수성구"]);
});

test("shortens parent-prefixed labels but preserves full option values", () => {
  const [group] = groupRegionOptions([{ name: "경기도 수원시 영통구", district: "경기도" }]);
  assert.deepEqual(group.options[0], { value: "경기도 수원시 영통구", label: "수원시 영통구" });
});

test("uses an explicit fallback parent for missing parent labels", () => {
  const groups = groupRegionOptions([{ name: "미분류 지역", district: " " }]);
  assert.equal(groups[0].parent, "상위 지역 미확인");
});

test("ignores malformed rows and blank names", () => {
  assert.deepEqual(groupRegionOptions([null, {}, { name: "   " }, "not-a-record"]), []);
});

test("deduplicates identical options within a parent group", () => {
  const groups = groupRegionOptions([
    { name: "수성구", district: "대구광역시" },
    { name: "수성구", district: "대구광역시" },
  ]);
  assert.equal(groups.length, 1);
  assert.equal(groups[0].options.length, 1);
});

test("rejects non-array input", () => {
  assert.throws(() => groupRegionOptions({}), TypeError);
});

test("does not mutate region records", () => {
  const rows = [{ name: "경기도 수원시 영통구", district: "경기도", extra: { flag: true } }];
  const before = structuredClone(rows);
  groupRegionOptions(rows);
  assert.deepEqual(rows, before);
});
