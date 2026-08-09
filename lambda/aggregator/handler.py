from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, cast

import boto3
from aggregator.lib.dynamo_aggregator.util import (
    aggregate_hiscores_rows,
    lint_query_response,
    parse_image,
    unroll_image,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aggregator.lib.dynamo_aggregator.util import ScalarTree
    from aws_lambda_typing.context import Context
    from aws_lambda_typing.events import DynamoDBStreamEvent
    from mypy_boto3_dynamodb.type_defs import TableAttributeValueTypeDef

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ["HISCORES_TABLE_NAME"])

DAILY_SENTINEL = "Daily#"
MONTHLY_SENTINEL = "Monthly#"
TIMESTAMP = "%Y-%m-%d %H:%M:%S"
DATE = "%Y-%m-%d"
MONTH = "%Y-%m"


def _timestamp_to_date(timestamp: str) -> str:
    """Parse a date from a timestamp."""
    return datetime.strptime(timestamp, TIMESTAMP).strftime(DATE)


def _timestamp_to_month(timestamp: str) -> str:
    """Parse a month from a timestamp."""
    return datetime.strptime(timestamp, TIMESTAMP).strftime(MONTH)


def aggregate(
    image: Mapping[str, object], interval: str = "daily"
) -> dict[str, object]:
    player_id, timestamp = parse_image(image)

    if interval == "daily":
        timestamp = f"{DAILY_SENTINEL}{_timestamp_to_date(timestamp)}"
        logger.info(f"Processing daily aggregation for {player_id}:{timestamp}.")
    elif interval == "monthly":
        timestamp = f"{MONTHLY_SENTINEL}{_timestamp_to_month(timestamp)}"
        logger.info(f"Processing monthly aggregation for {player_id}:{timestamp}.")
    else:
        raise ValueError(f"Unsupported aggregation interval: {interval}")

    unrolled_new_image = unroll_image(image)
    unrolled_new_image["timestamp"] = timestamp
    unrolled_new_image["divisor"] = 1
    logger.info(f"Formatted incoming row: {unrolled_new_image}")

    key = {"player": player_id, "timestamp": timestamp}
    logger.info(f"Querying table for {key}")
    resp = table.get_item(Key=key)
    logger.info(f"Received response {resp}")

    linted_resp = lint_query_response(cast("ScalarTree | None", resp.get("Item")))
    logger.info(f"Linted response: {linted_resp}")

    new_item = aggregate_hiscores_rows(
        cast("dict[str, object] | None", linted_resp), unrolled_new_image
    )
    logger.info(f"Produced aggregation {new_item}")

    table.put_item(Item=cast("Mapping[str, TableAttributeValueTypeDef]", new_item))

    return new_item


def handler(
    event: DynamoDBStreamEvent, context: Context
) -> tuple[dict[str, object], dict[str, object]] | None:
    event_name = event["Records"][0]["eventName"]
    event_source = event["Records"][0]["eventSource"]
    logger.info(f"Processing Event '{event_name}' from source '{event_source}'.")

    if event_name == "INSERT":
        new_image = event["Records"][0]["dynamodb"]["NewImage"]
        _, timestamp = parse_image(new_image)
        if timestamp.startswith(DAILY_SENTINEL):
            logger.info("Ignoring event from daily aggregation write.")
            return None
        if timestamp.startswith(MONTHLY_SENTINEL):
            logger.info("Ignoring event from monthly aggregation write.")
            return None

        logger.info(f"Received image: {new_image}")

        # aggregate daily
        daily = aggregate(new_image, interval="daily")

        # aggregate monthly
        monthly = aggregate(new_image, interval="monthly")

        return daily, monthly
    else:
        logger.info("Ignoring non-insert event.")
        return None
