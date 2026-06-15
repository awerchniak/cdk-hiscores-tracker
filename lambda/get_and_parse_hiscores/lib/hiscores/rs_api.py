"""Module for interacting with OSRS APIs."""

import json
import logging
import re
from datetime import datetime, timedelta

import requests

from .constants import LEGACY_ACTIVITY_MAP, LEGACY_SKILL_MAP

logger = logging.getLogger()

HISCORES_API = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.json"
HISCORES_IRONMAN_API = (
    "https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.json"
)

__all__ = [
    "InvalidSchemaError",
    "request_hiscores",
    "process_hiscores_response",
]


class InvalidSchemaError(Exception):
    """Indicates the schema for parsing an RS API response line is invalid."""


class HiscoresDownError(Exception):
    """Indicates an error connecting with the OSRS HiScores API."""


def _safe_dynamodb_string(key: str) -> str:
    """
    Strip any disallowed characters for DynamoDB attribute names.
    Allowed: a-z, A-Z, 0-9, underscore (_), dot (.), and hyphen (-).
    """

    # Replace any character NOT in the allowed set with an underscore
    safe_key = re.sub(r"[^a-zA-Z0-9._-]", "_", key)

    # DynamoDB attribute names must be between 1 and 255 characters
    return safe_key[:255]


def _safe_skill_name(skill_name: str) -> str:
    """Translate a skill name to a safe value for our DDB table."""
    candidate = LEGACY_SKILL_MAP.get(skill_name, skill_name)
    return _safe_dynamodb_string(candidate)


def _safe_activity_name(activity_name: str) -> str:
    """Translate an activity name to a safe value for our DDB table."""
    candidate = LEGACY_ACTIVITY_MAP.get(activity_name, activity_name)
    return _safe_dynamodb_string(candidate)


def get_hiscores_api(player: str) -> str:
    if "iron" in player.lower():
        return HISCORES_IRONMAN_API
    return HISCORES_API


def request_hiscores(
    player: str, warn_secs: int = 10, timeout: float = 60.0, **kwargs
) -> requests.models.Response:
    """Call hiscore_oldscool API to request stats for a given player."""
    try:
        response = requests.get(
            get_hiscores_api(player=player),
            params={"player": player},
            timeout=timeout,
            **kwargs,
        )
    except requests.exceptions.ReadTimeout as e:
        raise HiscoresDownError(
            f"Timed out calling Hiscores API after {timeout} seconds."
        ) from e

    if response.elapsed > timedelta(seconds=warn_secs):
        logger.warning(
            f"Longer than expected response time from Hiscores API: "
            f"{response.elapsed.seconds}s."
        )

    if "<!doctype html>" in response.text:
        raise HiscoresDownError(f"Hiscores API returned HTML response: {response.text}")

    if response.status_code != 200:
        raise ValueError(
            f"Received status code {response.status_code} with reason "
            f"'{response.reason}' for request '{response.request.url}'"
        )
    return response


def process_hiscores_response(response: requests.models.Response) -> dict:
    """Read hiscores API response into human-readable format.

    Unfortunately, `RANK`, `LEVEL`, and `COUNT` are all reserved words in DynamoDB:
    https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ReservedWords.html

    This is why we use rnk, lvl, xp, kc.

    TODO: create pydantic models instead of these typeless dicts
    """

    try:
        payload = response.json()
    except json.decoder.JSONDecodeError:
        raise HiscoresDownError(f"Hiscores API returned invalid JSON: {response.text}")

    try:
        processed_payload = dict()
        processed_payload["player"] = payload["name"]

        processed_payload["skills"] = dict()
        for skill in payload["skills"]:
            processed_payload["skills"][_safe_skill_name(skill["name"])] = dict(
                rnk=skill["rank"],
                lvl=skill["level"],
                xp=skill["xp"],
            )

        processed_payload["activities"] = dict()
        for activity in payload["activities"]:
            processed_payload["activities"][_safe_activity_name(activity["name"])] = (
                dict(
                    rnk=activity["rank"],
                    kc=activity["score"],
                )
            )
    except (AttributeError, KeyError, TypeError):
        raise HiscoresDownError(
            f"Hiscores API returned unexpected JSON format: {response.text}"
        )

    processed_payload["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return processed_payload
