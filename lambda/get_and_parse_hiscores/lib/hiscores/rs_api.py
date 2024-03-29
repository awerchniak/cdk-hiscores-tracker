"""Module for interacting with OSRS APIs."""
import logging
from datetime import datetime, timedelta
from typing import List
from urllib.parse import urlparse

import requests

from .constants import (
    HISCORE_RESPONSE_ACTIVITY_COLS,
    HISCORES_RESPONSE_ACTIVITIES,
    HISCORES_RESPONSE_SKILL_COLS,
    HISCORES_RESPONSE_SKILLS,
)

logger = logging.getLogger()

HISCORES_API = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws"
HISCORES_IRONMAN_API = (
    "https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws"
)

__all__ = [
    "InvalidSchemaError",
    "request_hiscores",
    "sanitize_hiscores_stats",
    "process_hiscores_response",
]


class InvalidSchemaError(Exception):
    """Indicates the schema for parsing an RS API response line is invalid."""


class HiscoresDownError(Exception):
    """Indicates an error connecting with the OSRS HiScores API."""


def get_hiscores_api(player: str) -> str:
    if "iron" in player.lower():
        return HISCORES_IRONMAN_API
    return HISCORES_API


def _parse_hiscores_response_line(line: str, schema: List[str]) -> dict:
    """Parse a single line of a hiscores API response."""
    split_line = line.split(",")
    if len(schema) != len(split_line):
        raise InvalidSchemaError(
            f"Schema '{schema}' is invalid for line '{line}': must be same length."
        )
    return dict(zip(schema, map(int, split_line)))


def _parse_skill_line(line: str) -> dict:
    """Parse a CSV skill line from a hiscores response."""
    return _parse_hiscores_response_line(line, HISCORES_RESPONSE_SKILL_COLS)


def _parse_activity_line(line: str) -> dict:
    """Parse a CSV activity line from a hiscores response."""
    return _parse_hiscores_response_line(line, HISCORE_RESPONSE_ACTIVITY_COLS)


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


def sanitize_hiscores_stats(text: str) -> dict:
    """Sanitize hiscore_oldscool API result text.

    API documentation:
    https://runescape.wiki/w/Application_programming_interface#Hiscores_Lite_2

    """

    # split string by line
    lines = text.strip().split("\n")

    if len(lines) != len(HISCORES_RESPONSE_SKILLS) + len(HISCORES_RESPONSE_ACTIVITIES):
        logger.warning(
            "HiScores response contains unexpected number of lines. Have the set of "
            "skills or activities returned by the HiScores API changed recently? "
            "Check https://runescape.wiki/w/Application_programming_interface#Old_School_Hiscores."  # noqa: E501
        )

    # skills are returned first
    skill_lines = lines[: len(HISCORES_RESPONSE_SKILLS)]
    # parse and label elements
    try:
        skill_dict = dict(
            zip(HISCORES_RESPONSE_SKILLS, map(_parse_skill_line, skill_lines))
        )
    except InvalidSchemaError as e:
        raise ValueError("Expected skill line of API result is malformatted.") from e

    # activities are returned second
    activity_lines = lines[len(HISCORES_RESPONSE_SKILLS) :]
    # parse and label elements
    try:
        activity_dict = dict(
            zip(
                HISCORES_RESPONSE_ACTIVITIES,
                map(_parse_activity_line, activity_lines),
            )
        )
    except InvalidSchemaError as e:
        raise ValueError("Expected activity line of API result is malformatted.") from e

    # return all information
    return dict(skills=skill_dict, activities=activity_dict)


def process_hiscores_response(response: requests.models.Response) -> dict:
    """Read hiscores API response into human-readable format."""
    # parse and label API response text
    result: dict = sanitize_hiscores_stats(response.text)

    # Add player name
    query = urlparse(response.request.url).query.split("=")
    if len(query) != 2 or query[0] != "player":
        raise ValueError(f"Received invalid query in API result: {'='.join(query)}")
    result["player"] = query[1].replace("+", " ")

    # Add timestamp
    result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return result
