from read_hiscores_table.lib.historical_corrections.corrector import (
    _extract_timestamp,
    _find_era,
    _is_boundary,
    _normalize_timestamp,
    apply_corrections,
)


def _activities(row: dict[str, object]) -> dict[str, object]:
    acts = row["activities"]
    assert isinstance(acts, dict)
    return acts


def test_extract_timestamp_raw() -> None:
    assert (
        _extract_timestamp({"timestamp": "2022-01-06 12:30:00"})
        == "2022-01-06 12:30:00"
    )


def test_extract_timestamp_daily() -> None:
    item: dict[str, object] = {"timestamp": "Daily#2022-01-06"}
    assert _extract_timestamp(item) == "2022-01-06"


def test_extract_timestamp_monthly() -> None:
    assert _extract_timestamp({"timestamp": "Monthly#2022-01"}) == "2022-01"


def test_extract_timestamp_missing() -> None:
    assert _extract_timestamp({}) == ""


def test_normalize_timestamp_full() -> None:
    assert _normalize_timestamp("2022-01-06 12:00:00") == "2022-01-06 12:00:00"


def test_normalize_timestamp_date() -> None:
    assert _normalize_timestamp("2022-01-06") == "2022-01-06 00:00:00"


def test_normalize_timestamp_month() -> None:
    assert _normalize_timestamp("2022-01") == "2022-01-01 00:00:00"


def test_find_era_within() -> None:
    era = _find_era("2022-01-06 12:00:00")
    assert era is not None
    assert era.start == "2022-01-05 00:00:00"


def test_find_era_date_only() -> None:
    era = _find_era("2022-01-06")
    assert era is not None


def test_find_era_outside() -> None:
    assert _find_era("2022-02-15 00:00:00") is None


def test_find_era_at_boundary() -> None:
    era = _find_era("2022-01-05 00:00:00")
    assert era is not None


def test_apply_corrections_within_era() -> None:
    items: list[dict[str, object]] = [
        {
            "timestamp": "2022-01-06 12:00:00",
            "player": "TestPlayer",
            "skills": {"Attack": {"rnk": 1, "lvl": 99, "xp": 200000000}},
            "activities": {
                "Nightmare": {"rnk": 100, "kc": 50},
                "PhosanisNightmare": {"rnk": 200, "kc": 25},
                "LeaguePoints": {"rnk": -1, "kc": -1},
            },
        }
    ]
    result = apply_corrections(items)
    assert len(result) == 1
    acts = _activities(result[0])
    assert "Nex" in acts
    assert acts["Nex"] == {"rnk": 100, "kc": 50}
    assert "Nightmare" in acts
    assert acts["Nightmare"] == {"rnk": 200, "kc": 25}
    expected_skills = {"Attack": {"rnk": 1, "lvl": 99, "xp": 200000000}}
    assert result[0]["skills"] == expected_skills


def test_apply_corrections_outside_era() -> None:
    items: list[dict[str, object]] = [
        {
            "timestamp": "2022-02-15 12:00:00",
            "player": "TestPlayer",
            "activities": {
                "Nightmare": {"rnk": 100, "kc": 50},
            },
        }
    ]
    result = apply_corrections(items)
    assert _activities(result[0])["Nightmare"] == {"rnk": 100, "kc": 50}


def test_apply_corrections_no_activities() -> None:
    items: list[dict[str, object]] = [
        {
            "timestamp": "2022-01-06 12:00:00",
            "player": "TestPlayer",
            "skills": {"Attack": {"rnk": 1, "lvl": 99, "xp": 200000000}},
        }
    ]
    result = apply_corrections(items)
    assert "activities" not in result[0]


def test_apply_corrections_daily_aggregation() -> None:
    items: list[dict[str, object]] = [
        {
            "timestamp": "2022-01-06",
            "player": "TestPlayer",
            "activities": {
                "Nightmare": {"rnk": 100, "kc": 50},
            },
            "aggregationLevel": "AggregationLevel.DAILY",
        }
    ]
    result = apply_corrections(items)
    assert "Nex" in _activities(result[0])


def test_apply_corrections_empty_list() -> None:
    assert apply_corrections([]) == []


def test_apply_corrections_multiple_items() -> None:
    items: list[dict[str, object]] = [
        {
            "timestamp": "2022-01-06 12:00:00",
            "activities": {"Nightmare": {"rnk": 1, "kc": 1}},
        },
        {
            "timestamp": "2022-02-15 12:00:00",
            "activities": {"Nightmare": {"rnk": 2, "kc": 2}},
        },
    ]
    result = apply_corrections(items)
    assert "Nex" in _activities(result[0])
    assert "Nightmare" in _activities(result[1])
    assert "Nex" not in _activities(result[1])


def test_apply_corrections_preserves_unaffected_activities() -> None:
    items: list[dict[str, object]] = [
        {
            "timestamp": "2022-01-06 12:00:00",
            "activities": {
                "LeaguePoints": {"rnk": -1, "kc": -1},
                "Nightmare": {"rnk": 100, "kc": 50},
            },
        }
    ]
    result = apply_corrections(items)
    acts = _activities(result[0])
    assert "LeaguePoints" in acts
    assert acts["LeaguePoints"] == {"rnk": -1, "kc": -1}


# --- _is_boundary tests ---


def test_is_boundary_start_day() -> None:
    era = _find_era("2022-01-05 00:00:00")
    assert era is not None
    assert _is_boundary("2022-01-05", era)


def test_is_boundary_end_day() -> None:
    era = _find_era("2022-01-08 12:00:00")
    assert era is not None
    assert _is_boundary("2022-01-08", era)


def test_is_boundary_interior_day() -> None:
    era = _find_era("2022-01-06 12:00:00")
    assert era is not None
    assert not _is_boundary("2022-01-06", era)


def test_is_boundary_raw_timestamp_never_boundary() -> None:
    era = _find_era("2022-01-05 00:00:00")
    assert era is not None
    assert not _is_boundary("2022-01-05 00:00:00", era)


def test_is_boundary_start_month() -> None:
    # ShellbaneGryphon era: start=2025-11-05, end=2025-11-07 — both in 2025-11
    era = _find_era("2025-11-06 12:00:00")
    assert era is not None
    assert _is_boundary("2025-11-", era) is False  # wrong length, not matched
    assert _is_boundary("2025-11", era)


# --- boundary omission in apply_corrections ---


def test_boundary_start_day_omitted() -> None:
    # Nex era start boundary: 2022-01-05 — daily aggregate is dropped
    items: list[dict[str, object]] = [
        {
            "timestamp": "2022-01-05",
            "activities": {"Nightmare": {"rnk": 1, "kc": 100}},
        }
    ]
    assert apply_corrections(items) == []


def test_boundary_end_day_omitted() -> None:
    # Nex era end boundary: 2022-01-08 — daily aggregate is dropped
    items: list[dict[str, object]] = [
        {
            "timestamp": "2022-01-08",
            "activities": {"Nightmare": {"rnk": 1, "kc": 100}},
        }
    ]
    assert apply_corrections(items) == []


def test_interior_day_corrected_not_dropped() -> None:
    # 2022-01-06 is interior to the Nex era — should be corrected and returned
    items: list[dict[str, object]] = [
        {
            "timestamp": "2022-01-06",
            "activities": {"Nightmare": {"rnk": 1, "kc": 100}},
        }
    ]
    result = apply_corrections(items)
    assert len(result) == 1
    assert "Nex" in _activities(result[0])


def test_boundary_month_omitted() -> None:
    # ShellbaneGryphon era start and end both fall in 2025-11
    items: list[dict[str, object]] = [
        {
            "timestamp": "2025-11",
            "activities": {"LeaguePoints": {"rnk": -1, "kc": -1}},
        }
    ]
    assert apply_corrections(items) == []


def test_raw_timestamp_on_boundary_day_corrected_not_dropped() -> None:
    # A raw point-in-time on the start day is in the era and gets corrected,
    # not omitted — only aggregated timestamps are considered boundary items
    items: list[dict[str, object]] = [
        {
            "timestamp": "2022-01-05 06:00:00",
            "activities": {"Nightmare": {"rnk": 1, "kc": 100}},
        }
    ]
    result = apply_corrections(items)
    assert len(result) == 1
    assert "Nex" in _activities(result[0])


def test_boundary_day_mix_in_query_result() -> None:
    # Simulates a November 2025 daily query: boundary days dropped, interior corrected
    items: list[dict[str, object]] = [
        {
            "timestamp": "2025-11-05",
            "activities": {"LeaguePoints": {"rnk": -1, "kc": -1}},
        },
        {
            "timestamp": "2025-11-06",
            "activities": {"LeaguePoints": {"rnk": -1, "kc": -1}},
        },
        {
            "timestamp": "2025-11-07",
            "activities": {"LeaguePoints": {"rnk": -1, "kc": -1}},
        },
    ]
    result = apply_corrections(items)
    timestamps = [r["timestamp"] for r in result]
    assert "2025-11-05" not in timestamps
    assert "2025-11-07" not in timestamps
    assert "2025-11-06" in timestamps
