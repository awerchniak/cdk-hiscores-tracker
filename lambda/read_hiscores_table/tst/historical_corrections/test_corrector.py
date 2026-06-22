from read_hiscores_table.lib.historical_corrections.corrector import (
    _extract_timestamp, _find_era, _normalize_timestamp, apply_corrections)


def test_extract_timestamp_raw():
    assert (
        _extract_timestamp({"timestamp": "2022-01-06 12:30:00"})
        == "2022-01-06 12:30:00"
    )


def test_extract_timestamp_daily():
    item = {"timestamp": "Daily#2022-01-06"}
    assert _extract_timestamp(item) == "2022-01-06"


def test_extract_timestamp_monthly():
    assert _extract_timestamp({"timestamp": "Monthly#2022-01"}) == "2022-01"


def test_extract_timestamp_missing():
    assert _extract_timestamp({}) == ""


def test_normalize_timestamp_full():
    assert _normalize_timestamp("2022-01-06 12:00:00") == "2022-01-06 12:00:00"


def test_normalize_timestamp_date():
    assert _normalize_timestamp("2022-01-06") == "2022-01-06 00:00:00"


def test_normalize_timestamp_month():
    assert _normalize_timestamp("2022-01") == "2022-01-01 00:00:00"


def test_find_era_within():
    era = _find_era("2022-01-06 12:00:00")
    assert era is not None
    assert era.start == "2022-01-05 00:00:00"


def test_find_era_date_only():
    era = _find_era("2022-01-06")
    assert era is not None


def test_find_era_outside():
    assert _find_era("2022-02-15 00:00:00") is None


def test_find_era_at_boundary():
    era = _find_era("2022-01-05 00:00:00")
    assert era is not None


def test_apply_corrections_within_era():
    items = [
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
    acts = result[0]["activities"]
    assert "Nex" in acts
    assert acts["Nex"] == {"rnk": 100, "kc": 50}
    assert "Nightmare" in acts
    assert acts["Nightmare"] == {"rnk": 200, "kc": 25}
    expected_skills = {"Attack": {"rnk": 1, "lvl": 99, "xp": 200000000}}
    assert result[0]["skills"] == expected_skills


def test_apply_corrections_outside_era():
    items = [
        {
            "timestamp": "2022-02-15 12:00:00",
            "player": "TestPlayer",
            "activities": {
                "Nightmare": {"rnk": 100, "kc": 50},
            },
        }
    ]
    result = apply_corrections(items)
    assert result[0]["activities"]["Nightmare"] == {"rnk": 100, "kc": 50}


def test_apply_corrections_no_activities():
    items = [
        {
            "timestamp": "2022-01-06 12:00:00",
            "player": "TestPlayer",
            "skills": {"Attack": {"rnk": 1, "lvl": 99, "xp": 200000000}},
        }
    ]
    result = apply_corrections(items)
    assert "activities" not in result[0]


def test_apply_corrections_daily_aggregation():
    items = [
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
    assert "Nex" in result[0]["activities"]


def test_apply_corrections_empty_list():
    assert apply_corrections([]) == []


def test_apply_corrections_multiple_items():
    items = [
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
    assert "Nex" in result[0]["activities"]
    assert "Nightmare" in result[1]["activities"]
    assert "Nex" not in result[1]["activities"]


def test_apply_corrections_preserves_unaffected_activities():
    items = [
        {
            "timestamp": "2022-01-06 12:00:00",
            "activities": {
                "LeaguePoints": {"rnk": -1, "kc": -1},
                "Nightmare": {"rnk": 100, "kc": 50},
            },
        }
    ]
    result = apply_corrections(items)
    acts = result[0]["activities"]
    assert "LeaguePoints" in acts
    assert acts["LeaguePoints"] == {"rnk": -1, "kc": -1}
