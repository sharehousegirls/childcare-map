export const SAVED_SEARCHES_KEY = "childcare-map:saved-searches:v1";
export const MAX_SAVED_SEARCHES = 20;

const VALID_TYPES = new Set(["all", "국공립", "민간", "가정", "직장"]);

function resolveStorage(storage) {
  if (storage !== undefined) return storage;
  try {
    return globalThis.localStorage || null;
  } catch {
    return null;
  }
}

function normalizeSavedSearch(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const id = typeof value.id === "string" ? value.id.trim() : "";
  const name = typeof value.name === "string" ? value.name.trim() : "";
  const region = typeof value.region === "string" && value.region.trim() ? value.region.trim() : "all";
  const query = typeof value.query === "string" ? value.query.trim() : "";
  const type = value.type == null ? "all" : value.type;
  if (!VALID_TYPES.has(type)) return null;
  if (!id || id.length > 100 || !name || name.length > 60 || region.length > 100 || query.length > 100) return null;
  const savedAt = typeof value.savedAt === "string" && Number.isFinite(Date.parse(value.savedAt))
    ? value.savedAt
    : new Date(0).toISOString();
  return { id, name, region, query, type, zeroWait: value.zeroWait === true, savedAt };
}

function readStoredItems(target) {
  try {
    const raw = target.getItem(SAVED_SEARCHES_KEY);
    if (!raw) return { ok: true, items: [] };
    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch {
      return { ok: true, items: [] };
    }
    if (!Array.isArray(parsed)) return { ok: true, items: [] };
    return { ok: true, items: parsed.map(normalizeSavedSearch).filter(Boolean).slice(0, MAX_SAVED_SEARCHES) };
  } catch {
    return { ok: false, items: [] };
  }
}

export function readSavedSearches(storage) {
  const target = resolveStorage(storage);
  return target ? readStoredItems(target).items : [];
}

function sameFilters(left, right) {
  return left.region === right.region && left.query === right.query && left.type === right.type && left.zeroWait === right.zeroWait;
}

export function saveSavedSearch(value, storage) {
  const target = resolveStorage(storage);
  if (!target) return { ok: false, reason: "storage-unavailable", items: [] };
  const item = normalizeSavedSearch(value);
  if (!item) return { ok: false, reason: "invalid", items: readSavedSearches(target) };
  const stored = readStoredItems(target);
  if (!stored.ok) return { ok: false, reason: "storage-error", items: [] };
  const current = stored.items;
  if (current.some(existing => existing.name === item.name && sameFilters(existing, item))) {
    return { ok: false, reason: "duplicate", items: current };
  }
  if (current.length >= MAX_SAVED_SEARCHES) return { ok: false, reason: "limit", items: current };
  const items = [item, ...current];
  try {
    target.setItem(SAVED_SEARCHES_KEY, JSON.stringify(items));
    return { ok: true, items };
  } catch {
    return { ok: false, reason: "storage-error", items: current };
  }
}

export function removeSavedSearch(id, storage) {
  const target = resolveStorage(storage);
  if (!target) return { ok: false, reason: "storage-unavailable", items: [] };
  const stored = readStoredItems(target);
  if (!stored.ok) return { ok: false, reason: "storage-error", items: [] };
  const current = stored.items;
  const items = current.filter(item => item.id !== id);
  if (items.length === current.length) return { ok: false, reason: "not-found", items: current };
  try {
    target.setItem(SAVED_SEARCHES_KEY, JSON.stringify(items));
    return { ok: true, items };
  } catch {
    return { ok: false, reason: "storage-error", items: current };
  }
}
