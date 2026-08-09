import pytest
from read_hiscores_table.lib.name_corrections.merge import (
    _SchemaMismatch,
    _sum_nested,
    merge_period_collisions,
)


def _nested(row: dict[str, object], *keys: str) -> object:
    value: object = row
    for key in keys:
        assert isinstance(value, dict)
        value = value[key]
    return value


def test_no_collisions_pass_through_unchanged() -> None:
    items: list[dict[str, object]] = [
        {"timestamp": "Daily#2025-05-01", "divisor": 3, "skills": {}, "activities": {}},
        {"timestamp": "Daily#2025-05-02", "divisor": 3, "skills": {}, "activities": {}},
    ]
    assert merge_period_collisions(items) == items


def test_two_colliding_daily_items_are_summed() -> None:
    old_alias: dict[str, object] = {
        "player": "DrPlingo0",
        "timestamp": "Daily#2025-05-03",
        "divisor": 3,
        "skills": {"Overall": {"lvl": 1800, "rnk": 300000, "xp": 3e7}},
        "activities": {"TheatreofBlood_HardMode": {"kc": -3, "rnk": -3}},
    }
    new_alias: dict[str, object] = {
        "player": "DrPlingo0",
        "timestamp": "Daily#2025-05-03",
        "divisor": 2,
        "skills": {"Overall": {"lvl": 1200, "rnk": 200000, "xp": 2e7}},
        "activities": {"TheatreofBlood_HardMode": {"kc": 2, "rnk": 300000}},
    }
    result = merge_period_collisions([old_alias, new_alias])
    assert len(result) == 1
    merged = result[0]
    assert merged["divisor"] == 5
    assert _nested(merged, "skills", "Overall") == {
        "lvl": 3000,
        "rnk": 500000,
        "xp": 5e7,
    }
    assert _nested(merged, "activities", "TheatreofBlood_HardMode") == {
        "kc": -1,
        "rnk": 299997,
    }


def test_three_way_collision_sums_across_all() -> None:
    def item(divisor: int, lvl: int) -> dict[str, object]:
        return {
            "timestamp": "Daily#2025-05-03",
            "divisor": divisor,
            "skills": {"Overall": {"lvl": lvl}},
            "activities": {},
        }

    result = merge_period_collisions([item(1, 100), item(1, 200), item(1, 300)])
    assert len(result) == 1
    assert result[0]["divisor"] == 3
    assert _nested(result[0], "skills", "Overall", "lvl") == 600


def test_colliding_items_missing_divisor_left_unmerged() -> None:
    items: list[dict[str, object]] = [
        {"timestamp": "2025-05-03 12:00:00", "skills": {}, "activities": {}},
        {"timestamp": "2025-05-03 12:00:00", "skills": {}, "activities": {}},
    ]
    assert merge_period_collisions(items) == items


def test_non_colliding_raw_items_untouched() -> None:
    items: list[dict[str, object]] = [
        {"timestamp": "2025-05-03 12:00:00", "skills": {}, "activities": {}},
        {"timestamp": "2025-05-03 12:30:00", "skills": {}, "activities": {}},
    ]
    assert merge_period_collisions(items) == items


def test_mismatched_schema_kept_unmerged() -> None:
    old_alias: dict[str, object] = {
        "timestamp": "Daily#2025-05-03",
        "divisor": 1,
        "skills": {},
        "activities": {"Zulrah": {"kc": 5, "rnk": 100}},
    }
    new_alias: dict[str, object] = {
        "timestamp": "Daily#2025-05-03",
        "divisor": 1,
        "skills": {},
        "activities": {"Vorkath": {"kc": 3, "rnk": 50}},
    }
    result = merge_period_collisions([old_alias, new_alias])
    assert len(result) == 2
    assert old_alias in result
    assert new_alias in result


def test_sum_nested_type_mismatch_raises() -> None:
    with pytest.raises(_SchemaMismatch):
        _sum_nested({"Overall": {"lvl": 100}}, {"Overall": 100})
