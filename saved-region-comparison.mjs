function safeCount(value) {
  return Number.isSafeInteger(value) && value >= 0 ? value : null;
}

function safeAverage(value) {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : null;
}

function savedRegionName(value) {
  if (typeof value === "string") return value.trim();
  if (!value || typeof value !== "object" || Array.isArray(value)) return "";
  return typeof value.region === "string" ? value.region.trim() : "";
}

/** Build a safe, name-based comparison for regions saved in this browser. */
export function buildSavedRegionComparison(regions, savedRegions, { liveData = false } = {}) {
  if (!Array.isArray(regions) || !Array.isArray(savedRegions)) {
    throw new TypeError("Expected regions and saved regions to be arrays.");
  }

  const byName = new Map();
  for (const record of regions) {
    if (!record || typeof record !== "object" || Array.isArray(record)) continue;
    const name = typeof record.name === "string" ? record.name.trim() : "";
    if (!name) continue;
    if (!byName.has(name)) byName.set(name, []);
    byName.get(name).push(record);
  }

  const seen = new Set();
  const result = [];
  for (const saved of savedRegions) {
    const name = savedRegionName(saved);
    if (!name || seen.has(name)) continue;
    seen.add(name);
    const matches = byName.get(name) || [];
    if (matches.length !== 1) {
      result.push({ region: name, available: false, reason: matches.length ? "지역 이름이 중복되어 비교할 수 없습니다." : "현재 데이터에서 찾을 수 없습니다." });
      continue;
    }

    const record = matches[0];
    const facilities = safeCount(record.facilities);
    const waiting = safeCount(record.waiting);
    const average = safeAverage(record.avg);
    const zeroWaitFacilities = safeCount(record.zero);
    const knownFacilities = safeCount(record.waitingFacilities);
    const declaredMissing = safeCount(record.missingWaitlistFacilities);
    const coverageValid = facilities !== null
      && knownFacilities !== null
      && knownFacilities <= facilities
      && (declaredMissing === null || declaredMissing === facilities - knownFacilities);
    const coverage = coverageValid && facilities > 0 ? knownFacilities / facilities : null;
    const missingWaitlistFacilities = coverageValid ? facilities - knownFacilities : null;
    const totalComplete = liveData === true
      && record.waitTotalComplete === true
      && coverageValid
      && facilities > 0
      && waiting !== null
      && knownFacilities === facilities;

    result.push({
      region: name,
      available: true,
      facilities,
      waiting,
      average,
      zeroWaitFacilities: zeroWaitFacilities !== null && facilities !== null && zeroWaitFacilities <= facilities ? zeroWaitFacilities : null,
      knownFacilities: coverageValid ? knownFacilities : null,
      missingWaitlistFacilities,
      coverage,
      coverageValid,
      totalComplete,
      partial: liveData === true && coverageValid && knownFacilities < facilities,
      demo: liveData !== true,
    });
  }
  return result;
}
