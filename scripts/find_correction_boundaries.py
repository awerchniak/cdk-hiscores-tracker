#!/usr/bin/env python3
"""Diagnostic script to find off-by-one error boundaries.

Queries a long-tenured player's full history and detects timestamps
where many activity values change simultaneously, indicating a CSV
parsing shift caused by Jagex adding new activities.

Usage:
    python scripts/find_correction_boundaries.py \
        --table TABLE_NAME --player ElderPlinius
    python scripts/find_correction_boundaries.py \
        --table TABLE_NAME --player Brec --threshold 5
"""

import argparse
import json
import sys
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


def query_all_items(table, player):
    items = []
    kwargs = {
        "KeyConditionExpression": Key("player").eq(player)
        & Key("timestamp").between("Daily#", "Daily#~"),
    }
    while True:
        response = table.query(**kwargs)
        items.extend(response["Items"])
        if "LastEvaluatedKey" not in response:
            break
        kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
    return sorted(items, key=lambda x: x["timestamp"])


def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    return obj


def detect_shift_events(items, threshold):
    events = []

    for i in range(1, len(items)):
        prev = items[i - 1]
        curr = items[i]

        prev_acts = prev.get("activities", {})
        curr_acts = curr.get("activities", {})
        prev_divisor = float(prev.get("divisor", 1))
        curr_divisor = float(curr.get("divisor", 1))

        changed = []
        all_activities = (
            set(prev_acts.keys()) | set(curr_acts.keys())
        )

        for act in sorted(all_activities):
            if act not in prev_acts or act not in curr_acts:
                reason = (
                    "appeared"
                    if act not in prev_acts
                    else "disappeared"
                )
                changed.append(
                    {
                        "activity": act,
                        "prev": _norm_act(
                            prev_acts.get(act), prev_divisor
                        ),
                        "curr": _norm_act(
                            curr_acts.get(act), curr_divisor
                        ),
                        "reason": reason,
                    }
                )
                continue

            prev_kc = (
                float(prev_acts[act].get("kc", 0)) / prev_divisor
            )
            curr_kc = (
                float(curr_acts[act].get("kc", 0)) / curr_divisor
            )

            if abs(prev_kc - curr_kc) > max(
                abs(prev_kc) * 0.5, 10
            ):
                changed.append(
                    {
                        "activity": act,
                        "prev_kc": round(prev_kc, 1),
                        "curr_kc": round(curr_kc, 1),
                        "delta": round(curr_kc - prev_kc, 1),
                    }
                )

        if len(changed) >= threshold:
            prev_ts = prev["timestamp"].split("#", 1)[-1]
            curr_ts = curr["timestamp"].split("#", 1)[-1]
            events.append(
                {
                    "between": [prev_ts, curr_ts],
                    "num_changed": len(changed),
                    "changes": changed,
                }
            )

    return events


def _norm_act(act_dict, divisor):
    if act_dict is None:
        return None
    return {
        k: round(float(v) / divisor, 1)
        for k, v in act_dict.items()
    }


def main():
    parser = argparse.ArgumentParser(
        description="Find off-by-one correction boundaries"
    )
    parser.add_argument(
        "--table", required=True, help="DynamoDB table name"
    )
    parser.add_argument(
        "--player",
        default="ElderPlinius",
        help="Player to analyze (default: ElderPlinius)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=5,
        help="Min simultaneous changes to flag (default: 5)",
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region (default: us-east-1)",
    )
    args = parser.parse_args()

    ddb = boto3.resource("dynamodb", region_name=args.region)
    table = ddb.Table(args.table)

    print(
        f"Querying Daily# aggregations for {args.player}...",
        file=sys.stderr,
    )
    items = query_all_items(table, args.player)
    print(
        f"Retrieved {len(items)} daily data points.",
        file=sys.stderr,
    )

    if len(items) < 2:
        print(
            "Not enough data points to detect shifts.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"Scanning for shift events "
        f"(threshold={args.threshold})...",
        file=sys.stderr,
    )
    events = detect_shift_events(items, args.threshold)

    print(
        f"\nFound {len(events)} potential shift events.\n",
        file=sys.stderr,
    )
    print(json.dumps(decimal_to_float(events), indent=2))


if __name__ == "__main__":
    main()
