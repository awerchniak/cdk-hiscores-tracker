import decimal
import enum
import json
from datetime import datetime

DAILY_SENTINEL = "Daily#"
MONTHLY_SENTINEL = "Monthly#"
TIMESTAMP_FMT = "%Y-%m-%d %H:%M:%S"
DATE_FMT = "%Y-%m-%d"
MONTH_FMT = MONTH = "%Y-%m"


class AggregationLevel(enum.Enum):
    NONE = 0
    DAILY = 1
    MONTHLY = 2


class CustomEncoder(json.JSONEncoder):
    """JSON encode Decimal objects."""

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o)
        if isinstance(o, AggregationLevel):
            return str(o)
        return super(CustomEncoder, self).default(o)


def valid_datetime(date_string, format):
    """Check if a string is a valid datetime."""
    try:
        return datetime.strptime(date_string, format)
    except ValueError:
        return None


def convert_timestamp(timestamp, fmts):
    """Convert a timestamp to an aggregation boundary."""
    for fmt in fmts:
        dt = valid_datetime(timestamp, fmt)
        if dt is not None:
            return dt.strftime(fmts[-1])
    raise ValueError(f"Timestamp {timestamp} must be one of {fmts}")


def timestamp_to_date(timestamp):
    """Parse a date from a timestamp."""
    return convert_timestamp(timestamp, [TIMESTAMP_FMT, DATE_FMT])


def timestamp_to_month(timestamp):
    """Parse a month from a timestamp."""
    return convert_timestamp(timestamp, [TIMESTAMP_FMT, DATE_FMT, MONTH_FMT])


def infer_aggregation_level(start_time, end_time):
    """Infer an aggregation level from startTime and endTime parameters"""
    # If dates aren't specified, use MONTHLY aggregation
    if valid_datetime(start_time, MONTH_FMT) and valid_datetime(end_time, MONTH_FMT):
        return AggregationLevel.MONTHLY

    # If times aren't specified, use DAILY aggregation
    if valid_datetime(start_time, DATE_FMT) and valid_datetime(end_time, DATE_FMT):
        return AggregationLevel.DAILY

    # If times are > 6 months apart, use MONTHLY aggregation
    start_dt = valid_datetime(start_time, TIMESTAMP_FMT)
    end_dt = valid_datetime(end_time, TIMESTAMP_FMT)
    if (end_dt - start_dt).days >= 180:
        return AggregationLevel.MONTHLY

    # If times are > 1 week apart, use DAILY aggregation
    if (end_dt - start_dt).days >= 7:
        return AggregationLevel.DAILY

    # else, use NONE aggregation
    return AggregationLevel.NONE


def get_query_boundaries(start_time, end_time, aggregation_level=AggregationLevel.NONE):
    """Get start and end sort keys for table query."""

    if aggregation_level == AggregationLevel.NONE:
        return start_time, end_time
    elif aggregation_level == AggregationLevel.DAILY:
        return (
            f"{DAILY_SENTINEL}{timestamp_to_date(start_time)}",
            f"{DAILY_SENTINEL}{timestamp_to_date(end_time)}",
        )
    elif aggregation_level == AggregationLevel.MONTHLY:
        return (
            f"{MONTHLY_SENTINEL}{timestamp_to_month(start_time)}",
            f"{MONTHLY_SENTINEL}{timestamp_to_month(end_time)}",
        )
    else:
        raise ValueError(f"Unsupported aggregation_level '{aggregation_level}.")


def normalize_nested_dict(d, denom):
    """Normalize values in a nested dict by a given denominator.

    Examples:
    >>> d = {"one": 1.0, "two": {"three": 3.0, "four": 4.0}}
    >>> normalize_nested_dict(d, 2.0)
    {'one': 0.5, 'two': {'three': 1.5, 'four': 2.0}}

    """
    result = dict()
    for key, value in d.items():
        if isinstance(value, dict):
            result[key] = normalize_nested_dict(value, denom)
        else:
            result[key] = value / denom
    return result


def lint_items(items, aggregation_level):
    """Lint items returned from HiScores Table Query."""
    result = list()
    for item in items:
        if aggregation_level == AggregationLevel.NONE:
            # If no aggregation, no action needed
            pass
        elif aggregation_level in [AggregationLevel.DAILY, AggregationLevel.MONTHLY]:
            item["timestamp"] = item["timestamp"].split("#")[1]
            divisor = item.pop("divisor")
            if "skills" in item:
                item["skills"] = normalize_nested_dict(item["skills"], divisor)
            if "activities" in item:
                item["activities"] = normalize_nested_dict(item["activities"], divisor)
        else:
            raise ValueError(f"Unsupported aggregation_level '{aggregation_level}.")

        item["aggregationLevel"] = aggregation_level
        result.append(item)

    return result
