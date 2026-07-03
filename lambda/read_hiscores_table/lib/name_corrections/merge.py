"""Merge aggregate rows that collide after alias resolution.

A rename that happens mid-day/mid-month leaves the aggregator's Daily#/
Monthly# rollups split across two partial-period rows -- one per alias --
since each rollup is keyed by whatever literal player name was on the raw
stream record at write time. This module recombines those rows at read time.
"""

from decimal import Decimal
from typing import cast


class _SchemaMismatch(ValueError):
    """Nested item schemas don't match; can't be safely summed."""


def _sum_nested(a: dict[str, object], b: dict[str, object]) -> dict[str, object]:
    """Elementwise-sum two same-shaped nested dicts (mirrors aggregator's merge)."""
    result: dict[str, object] = {}
    for key, a_val in a.items():
        if key not in b:
            raise _SchemaMismatch(f"Key '{key}' missing from second item.")
        b_val = b[key]
        if isinstance(a_val, dict) != isinstance(b_val, dict):
            raise _SchemaMismatch(f"Key '{key}' type mismatch.")
        if isinstance(a_val, dict) and isinstance(b_val, dict):
            result[key] = _sum_nested(a_val, b_val)
        else:
            # Real (DynamoDB-sourced) leaves are always Decimal; this cast
            # doesn't affect runtime behavior, which works for any numeric
            # type via normal Python duck typing.
            result[key] = cast(Decimal, a_val) + cast(Decimal, b_val)
    return result


def merge_period_collisions(items: list[dict[str, object]]) -> list[dict[str, object]]:
    """Merge items that share a timestamp (a rename fell inside one aggregate period).

    Only DAILY/MONTHLY rows carry a "divisor" and can collide this way; raw
    (NONE-level) items have full HH:MM:SS timestamps and pass through untouched.
    Sums skills/activities/divisor so the later lint_items() division produces
    one correctly-weighted average instead of two partial-period rows. If the
    two colliding items' schemas don't match (e.g. a correction-era boundary
    landed on the exact same day), both rows are kept unmerged rather than
    raising or dropping data.
    """
    by_timestamp: dict[object, list[dict[str, object]]] = {}
    order: list[object] = []
    for item in items:
        ts = item["timestamp"]
        if ts not in by_timestamp:
            by_timestamp[ts] = [item]
            order.append(ts)
            continue
        by_timestamp[ts].append(item)

    result: list[dict[str, object]] = []
    for ts in order:
        group = by_timestamp[ts]
        if len(group) == 1 or "divisor" not in group[0]:
            result.extend(group)
            continue
        merged = group[0]
        for other in group[1:]:
            try:
                for field in ("skills", "activities"):
                    if field in merged and field in other:
                        merged_field = merged[field]
                        other_field = other[field]
                        assert isinstance(merged_field, dict)
                        assert isinstance(other_field, dict)
                        merged[field] = _sum_nested(merged_field, other_field)
                merged["divisor"] = cast(Decimal, merged["divisor"]) + cast(
                    Decimal, other["divisor"]
                )
            except _SchemaMismatch:
                result.append(other)
                continue
        result.append(merged)
    return result
