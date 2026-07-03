"""Apply historical corrections to items read from DynamoDB."""

from .correction_map import CORRECTION_ERAS, CorrectionEra

_DAILY_TS_LEN = len("YYYY-MM-DD")
_MONTHLY_TS_LEN = len("YYYY-MM")


def _extract_timestamp(item: dict[str, object]) -> str:
    ts = item.get("timestamp", "")
    assert isinstance(ts, str)
    if "#" in ts:
        return ts.split("#", 1)[1]
    return ts


def _normalize_timestamp(ts: str) -> str:
    if len(ts) == _MONTHLY_TS_LEN:
        return ts + "-01 00:00:00"
    if len(ts) == _DAILY_TS_LEN:
        return ts + " 00:00:00"
    return ts


def _find_era(timestamp: str) -> CorrectionEra | None:
    if len(timestamp) == _MONTHLY_TS_LEN:
        # Monthly aggregates span a full calendar month; match any era that
        # overlaps the month, not just eras that contain the first of the month.
        for era in CORRECTION_ERAS:
            start_mo = era.start[:_MONTHLY_TS_LEN]
            end_mo = era.end[:_MONTHLY_TS_LEN]
            if start_mo <= timestamp <= end_mo:
                return era
        return None
    normalized = _normalize_timestamp(timestamp)
    for era in CORRECTION_ERAS:
        if era.start <= normalized <= era.end:
            return era
    return None


def _is_boundary(ts: str, era: CorrectionEra) -> bool:
    """True for aggregated timestamps that straddle an era boundary.

    Daily/monthly aggregates on the start or end day of an error era mix
    correct and mislabeled raw data in unknown proportions, so they cannot
    be reliably corrected and are omitted from the response instead.
    Raw timestamps (point-in-time) are never considered boundary items.
    """
    if len(ts) == _DAILY_TS_LEN:
        return ts == era.start[:_DAILY_TS_LEN] or ts == era.end[:_DAILY_TS_LEN]
    if len(ts) == _MONTHLY_TS_LEN:
        return ts == era.start[:_MONTHLY_TS_LEN] or ts == era.end[:_MONTHLY_TS_LEN]
    return False


def apply_corrections(items: list[dict[str, object]]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for item in items:
        ts = _extract_timestamp(item)
        era = _find_era(ts)

        if era is None or "activities" not in item:
            result.append(item)
            continue

        renames = era.renames
        if not renames:
            result.append(item)
            continue

        if _is_boundary(ts, era):
            continue

        old_activities_obj = item["activities"]
        assert isinstance(old_activities_obj, dict)
        old_activities: dict[str, object] = old_activities_obj
        new_activities: dict[str, object] = {}
        for stored_label, value in old_activities.items():
            correct_label = renames.get(stored_label, stored_label)
            new_activities[correct_label] = value

        result.append({**item, "activities": new_activities})

    return result
