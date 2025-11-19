import datetime
import inspect
from unittest import mock

import get_and_parse_hiscores.lib.hiscores.rs_api as rs_api
import pytest
import requests


class MockRequestsGet(object):
    """Mock for `requests` module."""

    def __init__(self, text, status_code, elapsed, reason):
        self._text = text
        self._status_code = status_code
        self._elapsed = datetime.timedelta(seconds=elapsed)
        self._reason = reason

    def __call__(self, api, params, *args, **kwargs):
        response = requests.Response()
        response._content = self._text.encode()
        response.status_code = self._status_code
        response.elapsed = self._elapsed
        response.reason = self._reason

        response.request = requests.Request()
        response.request.url = api + "?player=" + params["player"]

        return response


def successful_response_text():
    return inspect.cleandoc(
        """
        417625,1775,51739960
        536659,85,3273304
        620289,80,2054713
        653510,90,5403638
        599986,91,6262073
        642452,88,4644869
        487677,74,1113801
        516330,90,5719009
        1038967,70,751496
        817948,70,790087
        787621,70,754410
        738328,71,814511
        855431,70,745340
        574399,71,834875
        469361,72,900892
        279024,80,1986418
        411567,71,872644
        388560,73,1077529
        469001,70,797108
        428416,82,2596132
        177812,93,7560975
        303083,66,525955
        366373,73,1043046
        394233,75,1217135
        -1,1,0
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        420501,42
        1099732,1
        643745,4
        636404,5
        337647,29
        313798,3
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        238864,132
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        126798,37
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        278341,6
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        -1,-1
        34195,177
        232831,51
        """
    )


@pytest.fixture
def player_name():
    return "PlayerName"


def successful_parsed_response(player_name):
    return {
        "activities": {
            "AbyssalSire": {"kc": -1, "rnk": -1},
            "AlchemicalHydra": {"kc": -1, "rnk": -1},
            "Amoxliatl": {"kc": -1, "rnk": -1},
            "Araxxor": {"kc": -1, "rnk": -1},
            "Artio": {"kc": -1, "rnk": -1},
            "BarrowsChests": {"kc": 132, "rnk": 238864},
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
@mock.patch(
    f"{rs_api.__name__}.requests.get",
    side_effect=MockRequestsGet(
        text=successful_response_text(),
        status_code=200,
        elapsed=5,
        reason="OK",
    ),
)
def test_get_parse_hiscores_valid(mock_get, player, api):
    response = rs_api.request_hiscores(player)
    mock_get.assert_called_once_with(api, params=dict(player=player), timeout=mock.ANY)

    payload = rs_api.process_hiscores_response(response)
    timestamp = payload.pop("timestamp")
    assert payload == successful_parsed_response(player_name=player)
    assert timestamp is not None


def test_process_hiscores_response_invalid_query(mocker, player_name):
    mock_response = mocker.Mock()
    mock_request = mocker.Mock()
    mock_response.request = mock_request
    mock_request.url = rs_api.HISCORES_API + "?username=" + player_name

    mocker.patch(f"{rs_api.__name__}.sanitize_hiscores_stats")
    with pytest.raises(ValueError):
        rs_api.process_hiscores_response(mock_response)


def test_sanitize_hiscores_stats_invalid_skill_line():
    invalid_skill_line_schema = successful_response_text().replace(
        "417625,1775,51739960", "-1,-1"
    )
    with pytest.raises(ValueError):
        rs_api.sanitize_hiscores_stats(invalid_skill_line_schema)


def test_sanitize_hiscores_stats_invalid_activities_line():
    invalid_activity_line_schema = successful_response_text().replace(
        "-1,-1", "417625,1775,51739960"
    )
    with pytest.raises(ValueError):
        rs_api.sanitize_hiscores_stats(invalid_activity_line_schema)


@mock.patch(
    f"{rs_api.__name__}.requests.get",
    side_effect=requests.exceptions.ReadTimeout,
)
def test_request_hiscores_read_timeout(mock_get, player_name):
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
def test_request_hiscores_down(mock_get, player_name):
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
def test_request_hiscores_error(mock_get, player_name):
    with pytest.raises(ValueError):
        rs_api.request_hiscores(player_name)
    mock_get.assert_called_once()
