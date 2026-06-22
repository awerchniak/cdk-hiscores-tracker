"""Apply historical corrections to items read from DynamoDB."""

from .correction_map import CORRECTION_ERAS


def _extract_timestamp(item):
    ts = item.get("timestamp", "")
    if "#" in ts:
        return ts.split("#", 1)[1]
    return ts


def _find_era(timestamp):
    for era in CORRECTION_ERAS:
        if era.start <= timestamp <= era.end:
            return era
    return None


def apply_corrections(items):
    result = []
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

        old_activities = item["activities"]
        new_activities = {}
        for stored_label, value in old_activities.items():
            correct_label = renames.get(stored_label, stored_label)
            new_activities[correct_label] = value

        result.append({**item, "activities": new_activities})

    return result
