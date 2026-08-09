import re
from typing import TypedDict

QUERY_REGEX = (
    "SELECT timestamp,(?P<skills>.*) FROM skills.(?P<category>.*) "
    "WHERE player='(?P<player>.*)' AND timestamp > '(?P<startTime>.*)' "
    "AND timestamp < '(?P<endTime>.*)' ORDER BY timestamp ASC"
)
CATEGORY_MAP = {
    "experience": "xp",
    "level": "lvl",
    "rank": "rnk",
}


class ParsedQuery(TypedDict):
    skills: list[str]
    category: str
    player: str
    start_time: str
    end_time: str


def parse_query_str(query_str: str) -> ParsedQuery:
    """Parse skills, category, player, and date range from a legacy query. # noqa: E501

    Examples:
    >>> example = (
    ...     "SELECT timestamp,a,b,c "
    ...     "FROM skills.experience WHERE player='ElderPlinius' "
    ...     "AND timestamp > '2021-12-21 00:00:00' "
    ...     "AND timestamp < '2021-12-28 23:59:59' "
    ...     "ORDER BY timestamp ASC"
    ... )
    >>> parse_query_str(example)
    {'skills': ['a', 'b', 'c'], 'category': 'xp', 'player': 'ElderPlinius', 'start_time': '2021-12-21 00:00:00', 'end_time': '2021-12-28 23:59:59'}

    """
    m = re.search(QUERY_REGEX, query_str)
    if not m:
        raise ValueError(
            f"Query string '{QUERY_REGEX}' does not match regex '{QUERY_REGEX}'"
        )
    return {
        "skills": m.group("skills").split(","),
        "category": CATEGORY_MAP[m.group("category")],
        "player": m.group("player"),
        "start_time": m.group("startTime"),
        "end_time": m.group("endTime"),
    }


def format_legacy_response(
    response: list[dict[str, object]], skills: list[str], category: str
) -> list[list[object]]:
    """Format responses appropriately for legacy API.  # noqa: E501

    Examples:
    >>> skills = ["Strength", "Hitpoints", "Ranged", "Magic", "Slayer", "Farming"]
    >>> category = "xp"
    >>> response = [
    ...     {
    ...         'skills': {
    ...             'Farming': {'xp': 8109782},
    ...             'Hitpoints': {'xp': 6262476},
    ...             'Magic': {'xp': 5720554},
    ...             'Ranged': {'xp': 4644881},
    ...             'Slayer': {'xp': 2596132},
    ...             'Strength': {'xp': 5403638},
    ...         },
    ...         'player': 'ElderPlinius',
    ...         'timestamp': '2021-12-23',
    ...         'aggregationLevel': 'AggregationLevel.DAILY',
    ...     },
    ...     {
    ...         'skills': {
    ...             'Farming': {'xp': 8234596},
    ...             'Hitpoints': {'xp': 6262585},
    ...             'Magic': {'xp': 5720557},
    ...             'Ranged': {'xp': 4644884},
    ...             'Slayer': {'xp': 2596132},
    ...             'Strength': {'xp': 5403768},
    ...         },
    ...         'player': 'ElderPlinius',
    ...         'timestamp': '2021-12-24',
    ...         'aggregationLevel': 'AggregationLevel.DAILY',
    ...     },
    ... ]
    >>> format_legacy_response(response, skills, category)
    [['2021-12-23', 5403638, 6262476, 4644881, 5720554, 2596132, 8109782], ['2021-12-24', 5403768, 6262585, 4644884, 5720557, 2596132, 8234596]]
    """

    def format_item(item: dict[str, object]) -> list[object]:
        skills_dict = item["skills"]
        assert isinstance(skills_dict, dict)
        return [item["timestamp"]] + [skills_dict[skill][category] for skill in skills]

    return [format_item(item) for item in response]
