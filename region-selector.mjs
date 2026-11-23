/** Group selectable region labels by their existing parent label.
 * This is presentation-only grouping, not a canonical administrative hierarchy.
 */
export function groupRegionOptions(regions) {
  if (!Array.isArray(regions)) throw new TypeError("Expected region records to be an array.");

  const groups = new Map();
  for (const region of regions) {
    if (!region || typeof region !== "object" || Array.isArray(region)) continue;
    const name = typeof region.name === "string" ? region.name.trim() : "";
    if (!name) continue;
    const parent = typeof region.district === "string" && region.district.trim()
      ? region.district.trim()
      : "상위 지역 미확인";
    const label = name.startsWith(`${parent} `) ? name.slice(parent.length + 1).trim() : name;
    if (!groups.has(parent)) groups.set(parent, new Map());
    const options = groups.get(parent);
    if (!options.has(name)) options.set(name, { value: name, label });
  }

  return [...groups.entries()]
    .sort(([a], [b]) => a.localeCompare(b, "ko"))
    .map(([parent, options]) => ({
      parent,
      options: [...options.values()].sort((a, b) =>
        a.label.localeCompare(b.label, "ko") || a.value.localeCompare(b.value, "ko")),
    }));
}
