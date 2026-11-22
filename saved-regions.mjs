export const SAVED_REGIONS_KEY = "childcare-map:saved-regions:v1";
export const MAX_SAVED_REGIONS = 20;

function resolveStorage(storage) {
  if (storage !== undefined) return storage;
  try {
    return globalThis.localStorage || null;
  } catch {
    return null;
  }
}

function normalizeSavedRegion(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const id = typeof value.id === "string" ? value.id.trim() : "";
  const region = typeof value.region === "string" ? value.region.trim() : "";
  if (!id || id.length > 100 || !region || region === "all" || region.length > 100) return null;
  const savedAt = typeof value.savedAt === "string" && Number.isFinite(Date.parse(value.savedAt))
    ? value.savedAt
    : new Date(0).toISOString();
  return { id, region, savedAt };
}

function readStoredItems(target) {
  try {
    const raw = target.getItem(SAVED_REGIONS_KEY);
    if (!raw) return { ok: true, items: [] };
    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch {
      return { ok: true, items: [] };
    }
    if (!Array.isArray(parsed)) return { ok: true, items: [] };
    const seenRegions = new Set();
    const seenIds = new Set();
    const items = [];
    for (const entry of parsed) {
      const item = normalizeSavedRegion(entry);
      if (!item || seenRegions.has(item.region) || seenIds.has(item.id)) continue;
      seenRegions.add(item.region);
      seenIds.add(item.id);
      items.push(item);
      if (items.length >= MAX_SAVED_REGIONS) break;
    }
    return { ok: true, items };
  } catch {
    return { ok: false, items: [] };
  }
}

export function readSavedRegions(storage) {
  const target = resolveStorage(storage);
  return target ? readStoredItems(target).items : [];
}

export function saveSavedRegion(value, storage) {
  const target = resolveStorage(storage);
  if (!target) return { ok: false, reason: "storage-unavailable", items: [] };
  const item = normalizeSavedRegion(value);
  if (!item) return { ok: false, reason: "invalid", items: readSavedRegions(target) };
  const stored = readStoredItems(target);
  if (!stored.ok) return { ok: false, reason: "storage-error", items: [] };
  const current = stored.items;
  if (current.some(existing => existing.region === item.region)) {
    return { ok: false, reason: "duplicate", items: current };
  }
  if (current.some(existing => existing.id === item.id)) {
    return { ok: false, reason: "duplicate-id", items: current };
  }
  if (current.length >= MAX_SAVED_REGIONS) return { ok: false, reason: "limit", items: current };
  const items = [item, ...current];
  try {
    target.setItem(SAVED_REGIONS_KEY, JSON.stringify(items));
    return { ok: true, items };
  } catch {
    return { ok: false, reason: "storage-error", items: current };
  }
}

export function removeSavedRegion(id, storage) {
  const target = resolveStorage(storage);
  if (!target) return { ok: false, reason: "storage-unavailable", items: [] };
  const stored = readStoredItems(target);
  if (!stored.ok) return { ok: false, reason: "storage-error", items: [] };
  const current = stored.items;
  const items = current.filter(item => item.id !== id);
  if (items.length === current.length) return { ok: false, reason: "not-found", items: current };
  try {
    target.setItem(SAVED_REGIONS_KEY, JSON.stringify(items));
    return { ok: true, items };
  } catch {
    return { ok: false, reason: "storage-error", items: current };
  }
}
