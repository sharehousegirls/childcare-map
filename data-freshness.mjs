const DATE_ONLY = /^\d{4}-\d{2}-\d{2}$/;
const TIMESTAMP_WITH_ZONE = /^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})(?::(\d{2})(?:\.\d+)?)?(Z|[+-]\d{2}:\d{2})$/;
const DAY_MS = 86_400_000;

function parseDateOnly(value) {
  if (typeof value !== "string" || !DATE_ONLY.test(value)) return null;
  const parsed = new Date(`${value}T00:00:00.000Z`);
  if (!Number.isFinite(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== value) return null;
  return parsed;
}

function parseCollectionTimestamp(value) {
  if (typeof value !== "string") return null;
  const match = TIMESTAMP_WITH_ZONE.exec(value);
  if (!match || !parseDateOnly(match[1])) return null;
  const hour = Number(match[2]);
  const minute = Number(match[3]);
  const second = match[4] == null ? 0 : Number(match[4]);
  if (hour > 23 || minute > 59 || second > 59) return null;
  const zone = match[5];
  if (zone !== "Z") {
    const [offsetHour, offsetMinute] = zone.slice(1).split(":").map(Number);
    if (offsetHour > 14 || offsetMinute > 59 || (offsetHour === 14 && offsetMinute !== 0)) return null;
  }
  const timestamp = Date.parse(value);
  return Number.isFinite(timestamp) ? timestamp : null;
}

function validUniqueDates(values) {
  return [...new Set(values.map(parseDateOnly).filter(Boolean).map((date) => date.toISOString().slice(0, 10)))].sort();
}

/**
 * Describe source-record dates without asserting a freshness SLA.
 * Elapsed calendar days are measured against the API collection timestamp only.
 */
export function formatDataFreshness(meta) {
  if (!meta || typeof meta !== "object" || Array.isArray(meta)) {
    return "최신 기준일 확인 불가 · 메타데이터 없음";
  }

  const hasDateList = Array.isArray(meta.source_data_dates);
  const rawDates = hasDateList
    ? meta.source_data_dates
    : [meta.source_data_date_earliest, meta.source_data_date_latest, meta.source_data_date].filter((value) => value != null);
  const validDates = validUniqueDates(rawDates);
  const invalidDateCount = rawDates.filter((value) => value != null && String(value).trim() && !parseDateOnly(value)).length;
  const fallbackLatest = parseDateOnly(meta.source_data_date_latest || meta.source_data_date);
  if (!validDates.length && fallbackLatest) validDates.push(fallbackLatest.toISOString().slice(0, 10));
  if (!validDates.length) return "최신 기준일 확인 불가 · 유효한 날짜 없음";

  const latest = validDates.at(-1);
  const earliest = validDates[0];
  const mixedDeclared = meta.mixed_source_data_dates === true;
  const mixed = mixedDeclared || validDates.length > 1;
  let label;
  if (mixed && validDates.length > 1) {
    label = `시설별 기준일 혼재 · ${earliest}–${latest} (${validDates.length}개 날짜)`;
  } else if (mixed) {
    label = `시설별 기준일 혼재 · 해석 가능한 최신 기준일 ${latest}`;
  } else {
    label = `최신 기준일 ${latest}`;
  }

  let metadataMismatch = false;
  const latestField = meta.source_data_date_latest;
  if (latestField != null && String(latestField).trim()) {
    const parsedLatest = parseDateOnly(latestField);
    metadataMismatch ||= !parsedLatest || parsedLatest.toISOString().slice(0, 10) !== latest;
  }
  const earliestField = meta.source_data_date_earliest;
  if (validDates.length > 1 && earliestField != null && String(earliestField).trim()) {
    const parsedEarliest = parseDateOnly(earliestField);
    metadataMismatch ||= !parsedEarliest || parsedEarliest.toISOString().slice(0, 10) !== earliest;
  }
  if (hasDateList && typeof meta.mixed_source_data_dates === "boolean") {
    metadataMismatch ||= meta.mixed_source_data_dates !== (validDates.length > 1 || invalidDateCount > 0 && rawDates.filter((value) => String(value).trim()).length > 1);
  }

  const collectedAt = parseCollectionTimestamp(meta.collected_at);
  if (Number.isFinite(collectedAt)) {
    // Source dates are Korean date-only records; compare against the collection's
    // Asia/Seoul calendar day, not the UTC day of its timestamp.
    const parts = new Intl.DateTimeFormat("en", {
      timeZone: "Asia/Seoul",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).formatToParts(new Date(collectedAt));
    const koreanDateParts = Object.fromEntries(parts
      .filter((part) => part.type !== "literal")
      .map((part) => [part.type, part.value]));
    const collectionDate = parseDateOnly(
      `${koreanDateParts.year}-${koreanDateParts.month}-${koreanDateParts.day}`,
    );
    if (collectionDate) {
      const collectionDay = collectionDate.getTime();
      const sourceDay = parseDateOnly(latest).getTime();
      const days = Math.floor((collectionDay - sourceDay) / DAY_MS);
      label += days >= 0
        ? ` · 수집 당시 기준일 경과 ${days}일`
        : ` · 수집 시점보다 ${Math.abs(days)}일 미래 날짜 (확인 필요)`;
    }
  }

  if (invalidDateCount) label += ` · 유효하지 않은 기준일 ${invalidDateCount}개 제외`;
  if (metadataMismatch) label += " · 기준일 메타데이터 불일치 (확인 필요)";
  return label;
}
