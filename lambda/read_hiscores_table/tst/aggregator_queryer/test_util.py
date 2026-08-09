import decimal
import json

import pytest
import read_hiscores_table.lib.aggregation_queryer.util as util


def test_custom_encoder() -> None:
    d = {"decimal": decimal.Decimal("10"), "level": util.AggregationLevel.NONE}
    json.dumps(d, cls=util.CustomEncoder)


def daily_items() -> list[dict[str, object]]:
    return [
        {
            "timestamp": util.DAILY_SENTINEL + "2021-12-17",
            "divisor": 3,
            "skills": {
                "Overall": {
                    "lvl": 1800,
                    "rnk": 300000,
                    "xp": 3e7,
                },
            },
            "activities": {
                "TheatreofBlood_HardMode": {
                    "kc": -3,
                    "rnk": -3,
                }
            },
        },
        {
            "timestamp": util.DAILY_SENTINEL + "2021-12-18",
            "divisor": 3,
            "skills": {
                "Overall": {
                    "lvl": 2100,
                    "rnk": 270000,
                    "xp": 6e7,
                },
            },
            "activities": {
                "TheatreofBlood_HardMode": {
                    "kc": 12,
                    "rnk": 300000,
                }
            },
        },
    ]


def linted_daily_items() -> list[dict[str, object]]:
    return [
        {
            "timestamp": "2021-12-17",
            "skills": {
                "Overall": {
                    "lvl": 600,
                    "rnk": 100000,
                    "xp": 1e7,
                }
            },
            "activities": {
                "TheatreofBlood_HardMode": {
                    "kc": -1,
                    "rnk": -1,
                }
            },
            "aggregationLevel": util.AggregationLevel.DAILY,
        },
        {
            "timestamp": "2021-12-18",
            "skills": {
                "Overall": {
                    "lvl": 700,
                    "rnk": 90000,
                    "xp": 2e7,
                }
            },
            "activities": {
                "TheatreofBlood_HardMode": {
                    "kc": 4,
                    "rnk": 100000,
                }
            },
            "aggregationLevel": util.AggregationLevel.DAILY,
        },
    ]


@pytest.mark.parametrize(
    "items,aggregation_level,expected",
    [
        (daily_items(), util.AggregationLevel.DAILY, linted_daily_items()),
        (
            [{}],
            util.AggregationLevel.NONE,
            [{"aggregationLevel": util.AggregationLevel.NONE}],
        ),
    ],
)
def test_lint_items(
    items: list[dict[str, object]],
    aggregation_level: util.AggregationLevel,
    expected: list[dict[str, object]],
) -> None:
    assert util.lint_items(items, aggregation_level) == expected


def test_lint_items_invalid() -> None:
    with pytest.raises(ValueError):
        util.lint_items([{}], 3)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "start_time,end_time,expected",
    [
        ("2021-12-18 00:00:00", "2021-12-18 18:30:00", util.AggregationLevel.NONE),
        ("2021-12-17", "2021-12-18", util.AggregationLevel.DAILY),
        ("2021-12-10 00:00:00", "2021-12-18 18:30:00", util.AggregationLevel.DAILY),
        ("2020-12", "2021-01", util.AggregationLevel.MONTHLY),
        ("2020-12-01 00:00:00", "2021-12-01 00:00:00", util.AggregationLevel.MONTHLY),
    ],
)
def test_infer_aggregation_level(
    start_time: str, end_time: str, expected: util.AggregationLevel
) -> None:
    assert util.infer_aggregation_level(start_time, end_time) == expected


@pytest.mark.parametrize(
    "start_time,end_time,aggregation_level",
    [
        ("2021-12-18 00:00:00", "2021-12-18 18:30:00", util.AggregationLevel.NONE),
        ("2021-12-17", "2021-12-18", util.AggregationLevel.DAILY),
        ("2020-12-17 00:00:00", "2021-12-17 00:00:00", util.AggregationLevel.MONTHLY),
    ],
)
def test_get_query_boundaries(
    start_time: str, end_time: str, aggregation_level: util.AggregationLevel
) -> None:
    result = util.get_query_boundaries(start_time, end_time, aggregation_level)
    assert len(result) == 2
    if aggregation_level == util.AggregationLevel.NONE:
        assert result == (start_time, end_time)
    elif aggregation_level == util.AggregationLevel.DAILY:
        assert all([dt.startswith(util.DAILY_SENTINEL) for dt in result])
        assert all(
            [util.valid_datetime(dt.split("#")[1], util.DATE_FMT) for dt in result]
        )
    elif aggregation_level == util.AggregationLevel.MONTHLY:
        assert all([dt.startswith(util.MONTHLY_SENTINEL) for dt in result])
        assert all(
            [util.valid_datetime(dt.split("#")[1], util.MONTH_FMT) for dt in result]
        )


def test_get_query_boundaries_invalid() -> None:
    with pytest.raises(ValueError):
        util.get_query_boundaries("", "", 3)  # type: ignore[arg-type]


def test_convert_timestamp_invalid() -> None:
    with pytest.raises(ValueError):
        util.convert_timestamp("", [])
