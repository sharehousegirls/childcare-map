export function buildRegions(rows) {
  if (!Array.isArray(rows)) throw new TypeError("Expected facility rows to be an array.");
  const groups = new Map();
  for (const facility of rows) {
    if (!facility || typeof facility !== "object" || Array.isArray(facility)) continue;
    const sido = typeof facility.sido === "string" ? facility.sido.trim() : "";
    const sigungu = typeof facility.sigungu === "string" ? facility.sigungu.trim() : "";
    const fallbackRegion = typeof facility.region === "string" ? facility.region.trim() : "";
    const name = sido && sigungu ? `${sido} ${sigungu}` : (fallbackRegion || "지역 미분류");
    if (!groups.has(name)) {
      groups.set(name, {
        name,
        district: sido,
        facilities: 0,
        waiting: null,
        waitingFacilities: 0,
        missingWaitlistFacilities: 0,
        zero: 0,
        waitSum: 0,
        avg: null,
        coverage: 0,
        zeroWaitRate: null,
        waitTotalComplete: false,
      });
    }
    const group = groups.get(name);
    group.facilities += 1;
    const wait = facility.waiting;
    if (typeof wait === "number" && Number.isFinite(wait) && wait >= 0) {
      group.waiting = (group.waiting ?? 0) + wait;
      group.waitingFacilities += 1;
      group.waitSum += wait;
      if (wait === 0) group.zero += 1;
    }
  }
  return [...groups.values()].map(group => {
    const missing = group.facilities - group.waitingFacilities;
    const avg = group.waitingFacilities ? group.waitSum / group.waitingFacilities : null;
    return {
      ...group,
      missingWaitlistFacilities: missing,
      avg,
      coverage: group.facilities ? group.waitingFacilities / group.facilities : 0,
      zeroWaitRate: group.waitingFacilities ? group.zero / group.waitingFacilities : null,
      waitTotalComplete: missing === 0,
    };
  }).sort((a, b) => a.name.localeCompare(b.name, "ko"));
}