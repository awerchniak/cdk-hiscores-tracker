import datetime
import json
from collections.abc import Mapping
from typing import TypedDict
from unittest import mock
from unittest.mock import MagicMock

import get_and_parse_hiscores.lib.hiscores.rs_api as rs_api
import pytest
import requests
from get_and_parse_hiscores.lib.hiscores.rs_api import ActivityStats, SkillStats


class MockRequestsGet(object):
    """Mock for `requests` module."""

    def __init__(self, text: str, status_code: int, elapsed: float, reason: str):
        self._text = text
        self._status_code = status_code
        self._elapsed = datetime.timedelta(seconds=elapsed)
        self._reason = reason

    def __call__(
        self, api: str, params: Mapping[str, str], *args: object, **kwargs: object
    ) -> requests.Response:
        response = requests.Response()
        response._content = self._text.encode("utf-8")
        response.status_code = self._status_code
        response.elapsed = self._elapsed
        response.reason = self._reason
        response.encoding = "utf-8"
        response.headers["Content-Type"] = "application/json"
        response.request = requests.PreparedRequest()
        response.request.url = api + "?player=" + params["player"]

        return response


def successful_response_text(player_name: str) -> str:
    return json.dumps(
        {
            "name": player_name,
            "skills": [
                {
                    "id": 0,
                    "name": "Overall",
                    "rank": 417625,
                    "level": 1775,
                    "xp": 51739960,
                },
                {"id": 1, "name": "Attack", "rank": 536659, "level": 85, "xp": 3273304},
                {
                    "id": 2,
                    "name": "Defence",
                    "rank": 620289,
                    "level": 80,
                    "xp": 2054713,
                },
                {
                    "id": 3,
                    "name": "Strength",
                    "rank": 653510,
                    "level": 90,
                    "xp": 5403638,
                },
                {
                    "id": 4,
                    "name": "Hitpoints",
                    "rank": 599986,
                    "level": 91,
                    "xp": 6262073,
                },
                {"id": 5, "name": "Ranged", "rank": 642452, "level": 88, "xp": 4644869},
                {"id": 6, "name": "Prayer", "rank": 487677, "level": 74, "xp": 1113801},
                {"id": 7, "name": "Magic", "rank": 516330, "level": 90, "xp": 5719009},
                {
                    "id": 8,
                    "name": "Cooking",
                    "rank": 1038967,
                    "level": 70,
                    "xp": 751496,
                },
                {
                    "id": 9,
                    "name": "Woodcutting",
                    "rank": 817948,
                    "level": 70,
                    "xp": 790087,
                },
                {
                    "id": 10,
                    "name": "Fletching",
                    "rank": 787621,
                    "level": 70,
                    "xp": 754410,
                },
                {
                    "id": 11,
                    "name": "Fishing",
                    "rank": 738328,
                    "level": 71,
                    "xp": 814511,
                },
                {
                    "id": 12,
                    "name": "Firemaking",
                    "rank": 855431,
                    "level": 70,
                    "xp": 745340,
                },
                {
                    "id": 13,
                    "name": "Crafting",
                    "rank": 574399,
                    "level": 71,
                    "xp": 834875,
                },
                {
                    "id": 14,
                    "name": "Smithing",
                    "rank": 469361,
                    "level": 72,
                    "xp": 900892,
                },
                {
                    "id": 15,
                    "name": "Mining",
                    "rank": 279024,
                    "level": 80,
                    "xp": 1986418,
                },
                {
                    "id": 16,
                    "name": "Herblore",
                    "rank": 411567,
                    "level": 71,
                    "xp": 872644,
                },
                {
                    "id": 17,
                    "name": "Agility",
                    "rank": 388560,
                    "level": 73,
                    "xp": 1077529,
                },
                {
                    "id": 18,
                    "name": "Thieving",
                    "rank": 469001,
                    "level": 70,
                    "xp": 797108,
                },
                {
                    "id": 19,
                    "name": "Slayer",
                    "rank": 428416,
                    "level": 82,
                    "xp": 2596132,
                },
                {
                    "id": 20,
                    "name": "Farming",
                    "rank": 177812,
                    "level": 93,
                    "xp": 7560975,
                },
                {
                    "id": 21,
                    "name": "Runecrafting",
                    "rank": 303083,
                    "level": 66,
                    "xp": 525955,
                },
                {
                    "id": 22,
                    "name": "Hunter",
                    "rank": 366373,
                    "level": 73,
                    "xp": 1043046,
                },
                {
                    "id": 23,
                    "name": "Construction",
                    "rank": 394233,
                    "level": 75,
                    "xp": 1217135,
                },
                {"id": 24, "name": "Sailing", "rank": -1, "level": 1, "xp": 0},
            ],
            "activities": [
                {"id": 0, "name": "Grid Points", "rank": -1, "score": -1},
                {"id": 1, "name": "League Points", "rank": -1, "score": -1},
                {"id": 2, "name": "Deadman Points", "rank": -1, "score": -1},
                {"id": 3, "name": "Bounty Hunter - Hunter", "rank": -1, "score": -1},
                {"id": 4, "name": "Bounty Hunter - Rogue", "rank": -1, "score": -1},
                {
                    "id": 5,
                    "name": "Bounty Hunter (Legacy) - Hunter",
                    "rank": -1,
                    "score": -1,
                },
                {
                    "id": 6,
                    "name": "Bounty Hunter (Legacy) - Rogue",
                    "rank": -1,
                    "score": -1,
                },
                {"id": 7, "name": "Clue Scrolls (all)", "rank": 420501, "score": 42},
                {
                    "id": 8,
                    "name": "Clue Scrolls (beginner)",
                    "rank": 1099732,
                    "score": 1,
                },
                {"id": 9, "name": "Clue Scrolls (easy)", "rank": 643745, "score": 4},
                {"id": 10, "name": "Clue Scrolls (medium)", "rank": 636404, "score": 5},
                {"id": 11, "name": "Clue Scrolls (hard)", "rank": 337647, "score": 29},
                {"id": 12, "name": "Clue Scrolls (elite)", "rank": 313798, "score": 3},
                {"id": 13, "name": "Clue Scrolls (master)", "rank": -1, "score": -1},
                {"id": 14, "name": "LMS - Rank", "rank": -1, "score": -1},
                {"id": 15, "name": "PvP Arena - Rank", "rank": -1, "score": -1},
                {"id": 16, "name": "Soul Wars Zeal", "rank": -1, "score": -1},
                {"id": 17, "name": "Rifts closed", "rank": -1, "score": -1},
                {"id": 18, "name": "Colosseum Glory", "rank": -1, "score": -1},
                {"id": 19, "name": "Collections Logged", "rank": -1, "score": -1},
                {"id": 20, "name": "Abyssal Sire", "rank": -1, "score": -1},
                {"id": 21, "name": "Alchemical Hydra", "rank": -1, "score": -1},
                {"id": 22, "name": "Amoxliatl", "rank": -1, "score": -1},
                {"id": 23, "name": "Araxxor", "rank": -1, "score": -1},
                {"id": 24, "name": "Artio", "rank": -1, "score": -1},
                {"id": 25, "name": "Barrows Chests", "rank": 238864, "score": 132},
                {"id": 26, "name": "Brutus", "rank": -1, "score": -1},
                {"id": 27, "name": "Bryophyta", "rank": -1, "score": -1},
                {"id": 28, "name": "Callisto", "rank": -1, "score": -1},
                {"id": 29, "name": "Calvar'ion", "rank": -1, "score": -1},
                {"id": 30, "name": "Cerberus", "rank": -1, "score": -1},
                {"id": 31, "name": "Chambers of Xeric", "rank": -1, "score": -1},
                {
                    "id": 32,
                    "name": "Chambers of Xeric: Challenge Mode",
                    "rank": -1,
                    "score": -1,
                },
                {"id": 33, "name": "Chaos Elemental", "rank": -1, "score": -1},
                {"id": 34, "name": "Chaos Fanatic", "rank": -1, "score": -1},
                {"id": 35, "name": "Commander Zilyana", "rank": -1, "score": -1},
                {"id": 36, "name": "Corporeal Beast", "rank": -1, "score": -1},
                {"id": 37, "name": "Crazy Archaeologist", "rank": -1, "score": -1},
                {"id": 38, "name": "Dagannoth Prime", "rank": -1, "score": -1},
                {"id": 39, "name": "Dagannoth Rex", "rank": -1, "score": -1},
                {"id": 40, "name": "Dagannoth Supreme", "rank": -1, "score": -1},
                {"id": 41, "name": "Deranged Archaeologist", "rank": -1, "score": -1},
                {"id": 42, "name": "Doom of Mokhaiotl", "rank": -1, "score": -1},
                {"id": 43, "name": "Duke Sucellus", "rank": -1, "score": -1},
                {"id": 44, "name": "General Graardor", "rank": -1, "score": -1},
                {"id": 45, "name": "Giant Mole", "rank": -1, "score": -1},
                {"id": 46, "name": "Grotesque Guardians", "rank": -1, "score": -1},
                {"id": 47, "name": "Hespori", "rank": 126798, "score": 37},
                {"id": 48, "name": "Kalphite Queen", "rank": -1, "score": -1},
                {"id": 49, "name": "King Black Dragon", "rank": -1, "score": -1},
                {"id": 50, "name": "Kraken", "rank": -1, "score": -1},
                {"id": 51, "name": "Kree'Arra", "rank": -1, "score": -1},
                {"id": 52, "name": "K'ril Tsutsaroth", "rank": -1, "score": -1},
                {"id": 53, "name": "Lunar Chests", "rank": -1, "score": -1},
                {"id": 54, "name": "Mimic", "rank": -1, "score": -1},
                {"id": 55, "name": "Nex", "rank": -1, "score": -1},
                {"id": 56, "name": "Nightmare", "rank": -1, "score": -1},
                {"id": 57, "name": "Phosani's Nightmare", "rank": -1, "score": -1},
                {"id": 58, "name": "Obor", "rank": -1, "score": -1},
                {"id": 59, "name": "Phantom Muspah", "rank": -1, "score": -1},
                {"id": 60, "name": "Sarachnis", "rank": -1, "score": -1},
                {"id": 61, "name": "Scorpia", "rank": -1, "score": -1},
                {"id": 62, "name": "Scurrius", "rank": -1, "score": -1},
                {"id": 63, "name": "Shellbane Gryphon", "rank": -1, "score": -1},
                {"id": 64, "name": "Skotizo", "rank": 278341, "score": 6},
                {"id": 65, "name": "Sol Heredit", "rank": -1, "score": -1},
                {"id": 66, "name": "Spindel", "rank": -1, "score": -1},
                {"id": 67, "name": "Tempoross", "rank": -1, "score": -1},
                {"id": 68, "name": "The Gauntlet", "rank": -1, "score": -1},
                {"id": 69, "name": "The Corrupted Gauntlet", "rank": -1, "score": -1},
                {"id": 70, "name": "The Hueycoatl", "rank": -1, "score": -1},
                {"id": 71, "name": "The Leviathan", "rank": -1, "score": -1},
                {"id": 72, "name": "The Royal Titans", "rank": -1, "score": -1},
                {"id": 73, "name": "The Whisperer", "rank": -1, "score": -1},
                {"id": 74, "name": "Theatre of Blood", "rank": -1, "score": -1},
                {
                    "id": 75,
                    "name": "Theatre of Blood: Hard Mode",
                    "rank": -1,
                    "score": -1,
                },
                {
                    "id": 76,
                    "name": "Thermonuclear Smoke Devil",
                    "rank": -1,
                    "score": -1,
                },
                {"id": 77, "name": "Tombs of Amascut", "rank": -1, "score": -1},
                {
                    "id": 78,
                    "name": "Tombs of Amascut: Expert Mode",
                    "rank": -1,
                    "score": -1,
                },
                {"id": 79, "name": "TzKal-Zuk", "rank": -1, "score": -1},
                {"id": 80, "name": "TzTok-Jad", "rank": -1, "score": -1},
                {"id": 81, "name": "Vardorvis", "rank": -1, "score": -1},
                {"id": 82, "name": "Venenatis", "rank": -1, "score": -1},
                {"id": 83, "name": "Vet'ion", "rank": -1, "score": -1},
                {"id": 84, "name": "Vorkath", "rank": -1, "score": -1},
                {"id": 85, "name": "Wintertodt", "rank": -1, "score": -1},
                {"id": 86, "name": "Yama", "rank": -1, "score": -1},
                {"id": 87, "name": "Zalcano", "rank": 34195, "score": 177},
                {"id": 88, "name": "Zulrah", "rank": 232831, "score": 51},
            ],
        }
    )


@pytest.fixture
def player_name() -> str:
    return "PlayerName"


class _ExpectedPayload(TypedDict):
    player: str
    skills: dict[str, SkillStats]
    activities: dict[str, ActivityStats]


def successful_parsed_response(player_name: str) -> _ExpectedPayload:
    return {
        "activities": {
            "AbyssalSire": {"kc": -1, "rnk": -1},
            "AlchemicalHydra": {"kc": -1, "rnk": -1},
            "Amoxliatl": {"kc": -1, "rnk": -1},
            "Araxxor": {"kc": -1, "rnk": -1},
            "Artio": {"kc": -1, "rnk": -1},
            "BarrowsChests": {"kc": 132, "rnk": 238864},
            "Brutus": {"kc": -1, "rnk": -1},
            "BountyHunter_Hunter": {"kc": -1, "rnk": -1},
            "BountyHunter_Rogue": {"kc": -1, "rnk": -1},
            "BountyHunter_Hunter_Legacy": {"kc": -1, "rnk": -1},
            "BountyHunter_Rogue_Legacy": {"kc": -1, "rnk": -1},
            "Bryophyta": {"kc": -1, "rnk": -1},
            "Callisto": {"kc": -1, "rnk": -1},
            "Calvarion": {"kc": -1, "rnk": -1},
            "Cerberus": {"kc": -1, "rnk": -1},
            "ChambersofXeric": {"kc": -1, "rnk": -1},
            "ChambersofXeric_ChallengeMode": {"kc": -1, "rnk": -1},
            "ChaosElemental": {"kc": -1, "rnk": -1},
            "ChaosFanatic": {"kc": -1, "rnk": -1},
            "ClueScrolls_all": {"kc": 42, "rnk": 420501},
            "ClueScrolls_beginner": {"kc": 1, "rnk": 1099732},
            "ClueScrolls_easy": {"kc": 4, "rnk": 643745},
            "ClueScrolls_elite": {"kc": 3, "rnk": 313798},
            "ClueScrolls_hard": {"kc": 29, "rnk": 337647},
            "ClueScrolls_master": {"kc": -1, "rnk": -1},
            "ClueScrolls_medium": {"kc": 5, "rnk": 636404},
            "ColosseumGlory": {"kc": -1, "rnk": -1},
            "CollectionsLogged": {"kc": -1, "rnk": -1},
            "CommanderZilyana": {"kc": -1, "rnk": -1},
            "CorporealBeast": {"kc": -1, "rnk": -1},
            "CrazyArchaeologist": {"kc": -1, "rnk": -1},
            "DagannothPrime": {"kc": -1, "rnk": -1},
            "DagannothRex": {"kc": -1, "rnk": -1},
            "DagannothSupreme": {"kc": -1, "rnk": -1},
            "DeadmanPoints": {"kc": -1, "rnk": -1},
            "DerangedArchaeologist": {"kc": -1, "rnk": -1},
            "DoomOfMokhaiotl": {"kc": -1, "rnk": -1},
            "DukeSucellus": {"kc": -1, "rnk": -1},
            "GeneralGraardor": {"kc": -1, "rnk": -1},
            "GiantMole": {"kc": -1, "rnk": -1},
            "GridPoints": {"kc": -1, "rnk": -1},
            "GrotesqueGuardians": {"kc": -1, "rnk": -1},
            "GuardiansOfTheRift": {"kc": -1, "rnk": -1},
            "Hespori": {"kc": 37, "rnk": 126798},
            "KalphiteQueen": {"kc": -1, "rnk": -1},
            "KingBlackDragon": {"kc": -1, "rnk": -1},
            "Kraken": {"kc": -1, "rnk": -1},
            "KreeArra": {"kc": -1, "rnk": -1},
            "KrilTsutsaroth": {"kc": -1, "rnk": -1},
            "LMS_Rank": {"kc": -1, "rnk": -1},
            "LeaguePoints": {"kc": -1, "rnk": -1},
            "LunarChests": {"kc": -1, "rnk": -1},
            "Mimic": {"kc": -1, "rnk": -1},
            "Nex": {"kc": -1, "rnk": -1},
            "Nightmare": {"kc": -1, "rnk": -1},
            "Obor": {"kc": -1, "rnk": -1},
            "PhosanisNightmare": {"kc": -1, "rnk": -1},
            "PvPArena": {"kc": -1, "rnk": -1},
            "PhantomMuspah": {"kc": -1, "rnk": -1},
            "Sarachnis": {"kc": -1, "rnk": -1},
            "Scorpia": {"kc": -1, "rnk": -1},
            "Scurrius": {"kc": -1, "rnk": -1},
            "ShellbaneGryphon": {"kc": -1, "rnk": -1},
            "Skotizo": {"kc": 6, "rnk": 278341},
            "Spindel": {"kc": -1, "rnk": -1},
            "SolHeredit": {"kc": -1, "rnk": -1},
            "SoulWars_Zeal": {"kc": -1, "rnk": -1},
            "Tempoross": {"kc": -1, "rnk": -1},
            "TheCorruptedGauntlet": {"kc": -1, "rnk": -1},
            "TheHueycoatl": {"kc": -1, "rnk": -1},
            "TheLeviathan": {"kc": -1, "rnk": -1},
            "TheRoyalTitans": {"kc": -1, "rnk": -1},
            "TheWhisperer": {"kc": -1, "rnk": -1},
            "TheGauntlet": {"kc": -1, "rnk": -1},
            "TheatreofBlood": {"kc": -1, "rnk": -1},
            "TheatreofBlood_HardMode": {"kc": -1, "rnk": -1},
            "ThermonuclearSmokeDevil": {"kc": -1, "rnk": -1},
            "TombsOfAmascut": {"kc": -1, "rnk": -1},
            "TombsOfAmascutExpert": {"kc": -1, "rnk": -1},
            "TzKalZuk": {"kc": -1, "rnk": -1},
            "TzTokJad": {"kc": -1, "rnk": -1},
            "Vardorvis": {"kc": -1, "rnk": -1},
            "Venenatis": {"kc": -1, "rnk": -1},
            "Vettion": {"kc": -1, "rnk": -1},
            "Vorkath": {"kc": -1, "rnk": -1},
            "Wintertodt": {"kc": -1, "rnk": -1},
            "Yama": {"kc": -1, "rnk": -1},
            "Zalcano": {"kc": 177, "rnk": 34195},
            "Zulrah": {"kc": 51, "rnk": 232831},
        },
        "skills": {
            "Agility": {"lvl": 73, "rnk": 388560, "xp": 1077529},
            "Attack": {"lvl": 85, "rnk": 536659, "xp": 3273304},
            "Construction": {"lvl": 75, "rnk": 394233, "xp": 1217135},
            "Cooking": {"lvl": 70, "rnk": 1038967, "xp": 751496},
            "Crafting": {"lvl": 71, "rnk": 574399, "xp": 834875},
            "Defence": {"lvl": 80, "rnk": 620289, "xp": 2054713},
            "Farming": {"lvl": 93, "rnk": 177812, "xp": 7560975},
            "Firemaking": {"lvl": 70, "rnk": 855431, "xp": 745340},
            "Fishing": {"lvl": 71, "rnk": 738328, "xp": 814511},
            "Fletching": {"lvl": 70, "rnk": 787621, "xp": 754410},
            "Herblore": {"lvl": 71, "rnk": 411567, "xp": 872644},
            "Hitpoints": {"lvl": 91, "rnk": 599986, "xp": 6262073},
            "Hunter": {"lvl": 73, "rnk": 366373, "xp": 1043046},
            "Magic": {"lvl": 90, "rnk": 516330, "xp": 5719009},
            "Mining": {"lvl": 80, "rnk": 279024, "xp": 1986418},
            "Overall": {"lvl": 1775, "rnk": 417625, "xp": 51739960},
            "Prayer": {"lvl": 74, "rnk": 487677, "xp": 1113801},
            "Ranged": {"lvl": 88, "rnk": 642452, "xp": 4644869},
            "Runecrafting": {"lvl": 66, "rnk": 303083, "xp": 525955},
            "Sailing": {"lvl": 1, "rnk": -1, "xp": 0},
            "Slayer": {"lvl": 82, "rnk": 428416, "xp": 2596132},
            "Smithing": {"lvl": 72, "rnk": 469361, "xp": 900892},
            "Strength": {"lvl": 90, "rnk": 653510, "xp": 5403638},
            "Thieving": {"lvl": 70, "rnk": 469001, "xp": 797108},
            "Woodcutting": {"lvl": 70, "rnk": 817948, "xp": 790087},
        },
        "player": player_name,
    }


@pytest.mark.parametrize(
    "player,api",
    [
        ("ElderPlinius", rs_api.HISCORES_API),
        ("IronPlinius", rs_api.HISCORES_IRONMAN_API),
    ],
)
@mock.patch(f"{rs_api.__name__}.requests.get")
def test_get_parse_hiscores_valid(mock_get: MagicMock, player: str, api: str) -> None:
    mock_get.side_effect = MockRequestsGet(
        text=successful_response_text(player),
        status_code=200,
        elapsed=5,
        reason="OK",
    )

    response = rs_api.request_hiscores(player)
    mock_get.assert_called_once_with(api, params=dict(player=player), timeout=mock.ANY)

    payload = dict(rs_api.process_hiscores_response(response))
    timestamp = payload.pop("timestamp")
    assert payload == successful_parsed_response(player_name=player)
    assert timestamp is not None


@mock.patch(
    f"{rs_api.__name__}.requests.get",
    side_effect=requests.exceptions.ReadTimeout,
)
def test_request_hiscores_read_timeout(mock_get: MagicMock, player_name: str) -> None:
    with pytest.raises(rs_api.HiscoresDownError):
        rs_api.request_hiscores(player_name)
    mock_get.assert_called_once()


@mock.patch(
    f"{rs_api.__name__}.requests.get",
    side_effect=MockRequestsGet(
        text="<!doctype html> <body> API DOWN </body>",
        status_code=500,
        elapsed=1,
        reason="Internal Server Error",
    ),
)
def test_request_hiscores_down(mock_get: MagicMock, player_name: str) -> None:
    with pytest.raises(rs_api.HiscoresDownError):
        rs_api.request_hiscores(player_name)
    mock_get.assert_called_once()


@mock.patch(
    f"{rs_api.__name__}.requests.get",
    side_effect=MockRequestsGet(
        text="Resource not found",
        status_code=404,
        elapsed=1,
        reason="Resource not found",
    ),
)
def test_request_hiscores_error(mock_get: MagicMock, player_name: str) -> None:
    with pytest.raises(ValueError):
        rs_api.request_hiscores(player_name)
    mock_get.assert_called_once()


@mock.patch(f"{rs_api.__name__}.requests.get")
def test_process_hiscores_response_invalid_json(
    mock_get: MagicMock, player_name: str
) -> None:
    invalid_text = "The Highscores are currently undergoing maintenance."
    mock_get.side_effect = MockRequestsGet(
        text=invalid_text,
        status_code=200,
        elapsed=1,
        reason="OK",
    )

    response = rs_api.request_hiscores(player_name)

    with pytest.raises(rs_api.HiscoresDownError) as excinfo:
        rs_api.process_hiscores_response(response)

    assert invalid_text in str(excinfo.value)
    assert "invalid JSON" in str(excinfo.value)


@mock.patch(f"{rs_api.__name__}.requests.get")
def test_process_hiscores_response_empty_json(
    mock_get: MagicMock, player_name: str
) -> None:
    unexpected_text = "{}"
    mock_get.side_effect = MockRequestsGet(
        text=unexpected_text,  # valid json but not what we expect
        status_code=200,
        elapsed=1,
        reason="OK",
    )

    response = rs_api.request_hiscores(player_name)

    with pytest.raises(rs_api.HiscoresDownError) as excinfo:
        rs_api.process_hiscores_response(response)

    assert unexpected_text in str(excinfo.value)
    assert "unexpected JSON" in str(excinfo.value)
