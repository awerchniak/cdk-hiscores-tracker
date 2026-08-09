from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING, cast

import boto3
from get_and_parse_hiscores.lib.hiscores import rs_api

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aws_lambda_typing.context import Context
    from aws_lambda_typing.events import SQSEvent
    from get_and_parse_hiscores.lib.hiscores.rs_api import ProcessedHiscoresPayload
    from mypy_boto3_dynamodb.type_defs import TableAttributeValueTypeDef

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ["HISCORES_TABLE_NAME"])


def handler(event: SQSEvent, context: Context) -> ProcessedHiscoresPayload:
    """Call HiScores API, parse response, and save to Dynamo table."""

    # retrieve player username
    logger.debug(f"Received event: {event}")
    records = event["Records"]
    try:
        players = [json.loads(record["body"])["player"] for record in records]
        player = players[0]
    except (KeyError, IndexError):
        raise ValueError(f"Event did not contain player names: {event}")
    if len(players) > 1:
        logger.warn(
            f"Received records for multiple players: {players}. "
            f"Only the first player, '{player}', will be processed."
        )
    player = player.replace("-", " ")

    # retrieve HiScores for `player`
    logger.info(f"Getting HiScores for {player}")
    payload = rs_api.process_hiscores_response(
        rs_api.request_hiscores(player=player, timeout=45.0)
    )

    # write result to `table`
    logger.info(
        f"Putting payload for player '{payload['player']}', "
        f"timestamp '{payload['timestamp']}'"
    )
    logger.debug(f"Putting payload {payload}")
    table.put_item(Item=cast("Mapping[str, TableAttributeValueTypeDef]", payload))

    return payload
