import test from "node:test";
import assert from "node:assert/strict";
import { readSavedRegions, saveSavedRegion, removeSavedRegion, SAVED_REGIONS_KEY, MAX_SAVED_REGIONS } from "../saved-regions.mjs";

function createStorage() {
  const values = new Map();
  return {
    getItem(key) { return values.has(key) ? values.get(key) : null; },
    setItem(key, value) { values.set(key, String(value)); },
    values
  };
}
function sample(overrides = {}) {
  return { id: "region-1", region: "대구 수성구", savedAt: "2026-11-22T00:00:00.000Z", ...overrides };
}

test("save and read preserves a selected region", () => {
  const storage = createStorage();
  assert.equal(saveSavedRegion(sample(), storage).ok, true);
  assert.deepEqual(readSavedRegions(storage), [sample()]);
});
test("same region cannot be saved twice", () => {
  const storage = createStorage();
  saveSavedRegion(sample(), storage);
  const duplicate = saveSavedRegion(sample({ id: "region-2" }), storage);
  assert.equal(duplicate.ok, false);
  assert.equal(duplicate.reason, "duplicate");
  assert.equal(readSavedRegions(storage).length, 1);
});
test("duplicate IDs cannot be reused for different regions", () => {
  const storage = createStorage();
  saveSavedRegion(sample(), storage);
  const duplicateId = saveSavedRegion(sample({ region: "대구 동구" }), storage);
  assert.equal(duplicateId.ok, false);
  assert.equal(duplicateId.reason, "duplicate-id");
  assert.equal(readSavedRegions(storage).length, 1);
});
test("saved regions are capped at twenty", () => {
  const storage = createStorage();
  for (let index = 0; index < MAX_SAVED_REGIONS; index++) {
    assert.equal(saveSavedRegion(sample({ id: `region-${index}`, region: `지역 ${index}` }), storage).ok, true);
  }
  const overflow = saveSavedRegion(sample({ id: "overflow", region: "overflow" }), storage);
  assert.equal(overflow.reason, "limit");
  assert.equal(readSavedRegions(storage).length, MAX_SAVED_REGIONS);
});
test("all regions and malformed region values are rejected", () => {
  const storage = createStorage();
  assert.equal(saveSavedRegion(sample({ region: "all" }), storage).reason, "invalid");
  assert.equal(saveSavedRegion(sample({ region: " " }), storage).reason, "invalid");
  assert.equal(saveSavedRegion(sample({ id: "" }), storage).reason, "invalid");
});
test("malformed JSON and invalid entries are safely ignored", () => {
  const storage = createStorage();
  storage.setItem(SAVED_REGIONS_KEY, "{broken");
  assert.deepEqual(readSavedRegions(storage), []);
  storage.setItem(SAVED_REGIONS_KEY, JSON.stringify([sample(), { id: "", region: "invalid" }]));
  assert.equal(readSavedRegions(storage).length, 1);
});
test("duplicate stored regions are normalized and deduplicated", () => {
  const storage = createStorage();
  storage.setItem(SAVED_REGIONS_KEY, JSON.stringify([sample(), sample({ id: "region-2" }), sample({ id: "region-1", region: "대구 중구" }), sample({ id: "region-3", region: "대구 동구" })]));
  const items = readSavedRegions(storage);
  assert.equal(items.length, 2);
  assert.equal(items[0].region, "대구 수성구");
  assert.equal(items[1].region, "대구 동구");
});
test("delete removes the selected region and missing IDs are reported", () => {
  const storage = createStorage();
  saveSavedRegion(sample(), storage);
  assert.equal(removeSavedRegion("region-1", storage).ok, true);
  assert.deepEqual(readSavedRegions(storage), []);
  assert.equal(removeSavedRegion("missing", storage).reason, "not-found");
});
test("storage access errors are handled without throwing", () => {
  const broken = { getItem() { throw new Error("blocked"); }, setItem() { throw new Error("blocked"); } };
  assert.deepEqual(readSavedRegions(broken), []);
  assert.equal(saveSavedRegion(sample(), broken).reason, "storage-error");
  assert.equal(removeSavedRegion("region-1", broken).reason, "storage-error");
});
test("read failure does not write over stored regions", () => {
  let writes = 0;
  const brokenRead = { getItem() { throw new Error("read blocked"); }, setItem() { writes++; } };
  assert.equal(saveSavedRegion(sample(), brokenRead).reason, "storage-error");
  assert.equal(removeSavedRegion("region-1", brokenRead).reason, "storage-error");
  assert.equal(writes, 0);
});
test("invalid saved timestamp is replaced with a safe epoch value", () => {
  const storage = createStorage();
  saveSavedRegion(sample({ savedAt: "not-a-date" }), storage);
  assert.equal(readSavedRegions(storage)[0].savedAt, new Date(0).toISOString());
});
