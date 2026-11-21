import test from "node:test";
import assert from "node:assert/strict";
import { readSavedSearches, saveSavedSearch, removeSavedSearch, SAVED_SEARCHES_KEY, MAX_SAVED_SEARCHES } from "../saved-searches.mjs";

function createStorage() {
  const values = new Map();
  return {
    getItem(key) { return values.has(key) ? values.get(key) : null; },
    setItem(key, value) { values.set(key, String(value)); },
    values
  };
}

function sample(overrides = {}) {
  return {
    id: "search-1",
    name: "대구 수성구 국공립",
    region: "대구 수성구",
    query: "",
    type: "국공립",
    zeroWait: false,
    savedAt: "2026-11-22T00:00:00.000Z",
    ...overrides
  };
}

test("save and read preserves search conditions", () => {
  const storage = createStorage();
  const result = saveSavedSearch(sample(), storage);
  assert.equal(result.ok, true);
  assert.deepEqual(readSavedSearches(storage)[0], sample());
});

test("same name and conditions cannot be saved twice", () => {
  const storage = createStorage();
  saveSavedSearch(sample(), storage);
  const duplicate = saveSavedSearch(sample({ id: "search-2" }), storage);
  assert.equal(duplicate.ok, false);
  assert.equal(duplicate.reason, "duplicate");
  assert.equal(readSavedSearches(storage).length, 1);
});

test("same conditions can be saved under a different name", () => {
  const storage = createStorage();
  saveSavedSearch(sample(), storage);
  const result = saveSavedSearch(sample({ id: "search-2", name: "같은 조건 다른 이름" }), storage);
  assert.equal(result.ok, true);
  assert.equal(readSavedSearches(storage).length, 2);
});

test("malformed stored JSON and invalid entries are safely ignored", () => {
  const storage = createStorage();
  storage.setItem(SAVED_SEARCHES_KEY, "{broken");
  assert.deepEqual(readSavedSearches(storage), []);
  storage.setItem(SAVED_SEARCHES_KEY, JSON.stringify([sample(), { id: "", name: "invalid" }]));
  assert.equal(readSavedSearches(storage).length, 1);
});

test("saved searches are capped at twenty", () => {
  const storage = createStorage();
  for (let index = 0; index < MAX_SAVED_SEARCHES; index++) {
    const result = saveSavedSearch(sample({ id: "search-" + index, name: "name-" + index }), storage);
    assert.equal(result.ok, true);
  }
  const overflow = saveSavedSearch(sample({ id: "overflow", name: "overflow" }), storage);
  assert.equal(overflow.ok, false);
  assert.equal(overflow.reason, "limit");
  assert.equal(readSavedSearches(storage).length, MAX_SAVED_SEARCHES);
});

test("invalid type and oversized name are rejected", () => {
  const storage = createStorage();
  assert.equal(saveSavedSearch(sample({ type: "unknown" }), storage).reason, "invalid");
  assert.equal(saveSavedSearch(sample({ name: "x".repeat(61) }), storage).reason, "invalid");
});

test("delete removes the selected saved search", () => {
  const storage = createStorage();
  saveSavedSearch(sample(), storage);
  const result = removeSavedSearch("search-1", storage);
  assert.equal(result.ok, true);
  assert.deepEqual(readSavedSearches(storage), []);
  assert.equal(removeSavedSearch("missing", storage).reason, "not-found");
});

test("storage access errors are handled without throwing", () => {
  const broken = {
    getItem() { throw new Error("storage blocked"); },
    setItem() { throw new Error("storage blocked"); }
  };
  assert.deepEqual(readSavedSearches(broken), []);
  assert.equal(saveSavedSearch(sample(), broken).reason, "storage-error");
  assert.equal(removeSavedSearch("search-1", broken).reason, "not-found");
  assert.deepEqual(readSavedSearches(), []);
});
