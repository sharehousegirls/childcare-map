export function formatDataQualityDetails(meta, recordCount) {
  if (!meta || !Number.isSafeInteger(recordCount) || recordCount < 0) {
    return "기준일 진단 정보 없음";
  }
  if (recordCount === 0) return "기준일 진단: 시설 데이터 없음";

  const counts = [
    meta.records_with_source_data_date,
    meta.records_without_source_data_date,
    meta.records_with_parseable_source_data_date,
    meta.records_with_unparseable_source_data_date,
  ];
  if (!counts.every((value) => Number.isSafeInteger(value) && value >= 0)) {
    return "기준일 진단 정보 없음";
  }

  const [dated, missing, parseable, unparseable] = counts;
  if (dated + missing !== recordCount || parseable + unparseable !== dated) {
    return "기준일 진단값 불일치 · 확인 필요";
  }

  const percent = (numerator, denominator) => (numerator / denominator * 100).toFixed(1);
  const coverage = `${dated}/${recordCount}행 (${percent(dated, recordCount)}%)`;
  const parseability = dated
    ? `${parseable}/${dated}행 (${percent(parseable, dated)}%)`
    : "— (기준일 없음)";
  return `기준일 기록 ${coverage} · 날짜 해석 ${parseability} · 해석 불가 ${unparseable}행 · 기준일 누락 ${missing}행`;
}
