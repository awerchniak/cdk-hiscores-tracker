import json
import logging
import os

import boto3
from boto3.dynamodb.conditions import Key
from read_hiscores_table.lib.aggregation_queryer.legacy import (
    format_legacy_response, parse_query_str)
from read_hiscores_table.lib.aggregation_queryer.util import (
    DATE_FMT, MONTH_FMT, TIMESTAMP_FMT, CustomEncoder, get_query_boundaries,
    infer_aggregation_level, lint_items, valid_datetime)
from read_hiscores_table.lib.historical_corrections import apply_corrections

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ["HISCORES_TABLE_NAME"])


def run_table_query(player, start_time, end_time, skills=None, category=None):
    """Query HiScores table for a player, start time, and end time."""

    try:
        aggregation_level = infer_aggregation_level(start_time, end_time)
        query_boundaries = get_query_boundaries(start_time, end_time, aggregation_level)
    except TypeError:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "status": 400,
                    "body": "'startTime' and 'endTime' parameter formats must match.",
                }
            ),
        }

    logger.info(
        f"Retrieving HiScores data for player '{player}' between "
        f"{query_boundaries[0]} and {query_boundaries[1]}"
    )
    if skills and category:
        logger.info(f"Limiting query to category '{category}' and skills {skills}")
        response = table.query(
            KeyConditionExpression=Key("player").eq(player)
            & Key("timestamp").between(*query_boundaries),
            ProjectionExpression=",".join(
                ["player", "#t", "divisor"]
                + [f"skills.{skill}.{category}" for skill in skills]
            ),
            ExpressionAttributeNames={"#t": "timestamp"},
        )
    else:
        response = table.query(
            KeyConditionExpression=Key("player").eq(player)
            & Key("timestamp").between(*query_boundaries),
        )

    items = response["Items"]
    logger.info(f"Received items: {items}")

    linted_items = lint_items(items, aggregation_level)
    logger.info(f"Linted items: {linted_items}")

    corrected_items = apply_corrections(linted_items)
    return corrected_items


def handle_v0(event, context):
    """Handle a v0 API request."""

    params = event["queryStringParameters"]
    if not isinstance(params, dict):
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps(
                {
                    "status": 400,
                    "message": (
                        "API requires 'player', 'startTime', and 'endTime' params."
                    ),
                }
            ),
        }

    if "player" not in params:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": "API requires 'player' param.",
        }
    player = params["player"]

    if "startTime" not in params or not any(
        [
            valid_datetime(params["startTime"], TIMESTAMP_FMT),
            valid_datetime(params["startTime"], DATE_FMT),
            valid_datetime(params["startTime"], MONTH_FMT),
        ]
    ):
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps(
                {
                    "status": 400,
                    "body": (
                        "API requires 'startTime' param with shape "
                        "'YYYY-mm[-dd [HH:MM:SS]]'"
                    ),
                }
            ),
        }
    start_time = params["startTime"]

    if "endTime" not in params or not any(
        [
            valid_datetime(params["endTime"], TIMESTAMP_FMT),
            valid_datetime(params["endTime"], DATE_FMT),
            valid_datetime(params["endTime"], MONTH_FMT),
        ]
    ):
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps(
                {
                    "status": 400,
                    "body": (
                        "API requires 'endTime' param with shape "
                        "'YYYY-mm[-dd [HH:MM:SS]]'"
                    ),
                }
            ),
        }
    end_time = params["endTime"]

    query_response = run_table_query(player, start_time, end_time)

    return {
        "statusCode": 200,
        "headers": CORS_HEADERS,
        "body": json.dumps(query_response, cls=CustomEncoder),
    }


def handle_legacy(event, context):
    """Handle a legacy API request."""
    params = event["queryStringParameters"]
    if not isinstance(params, dict) or "sql" not in params:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "status": 400,
                    "message": "API requires 'sql' param.",
                }
            ),
        }

    original_sql = params["sql"]
    logger.info(f"Original SQL: '{original_sql}'")

    parsed_fields = parse_query_str(original_sql)
    logger.info(f"Parsed fields: {parsed_fields}")

    query_result = run_table_query(
        parsed_fields["player"],
        parsed_fields["start_time"],
        parsed_fields["end_time"],
        category=parsed_fields["category"],
        skills=parsed_fields["skills"],
    )

    logger.info(f"Received query result: {query_result}")
    formatted_query_result = format_legacy_response(
        query_result, parsed_fields["skills"], parsed_fields["category"]
    )

    logger.info(f"Formatted query result: '{formatted_query_result}'")
    return {
        "statusCode": 200,
        "body": json.dumps(formatted_query_result, cls=CustomEncoder),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
    }


def handler(event, context):
    """Handle a GET request.

    The endpoint has two possible paths:
    1. `/v0` takes a request with player/startDate/endDate and responds with all
       data for that player between those dates.
    2. `/legacy` takes a MySQL statement intended for the legacy RDS database,
       parses its parameters, and responds with data for the given player and
       skill category between the specified dates.

    """
    method = event["httpMethod"]
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}
    if method != "GET":
        return {
            "statusCode": 501,
            "headers": CORS_HEADERS,
            "body": json.dumps({"status": 501, "message": "We only accept GET /"}),
        }

    path = event["path"].strip("/")
    logger.info(f"Received '{path}' invocation.")
    if path == "legacy":
        return handle_legacy(event, context)
    elif path == "v0":
        return handle_v0(event, context)
    else:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "status": 400,
                    "body": (
                        f"Unsupported path: {event['path']}." "Choose from: [legacy|v0]"
                    ),
                }
            ),
        }
