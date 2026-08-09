from read_hiscores_table.lib.historical_corrections.correction_map import (
    CORRECTION_ERAS,
    ERA_0,
    ERA_1,
    ERA_20,
    CorrectionEra,
)


def test_eras_have_valid_timestamps() -> None:
    for era in CORRECTION_ERAS:
        assert (
            era.start < era.end
        ), f"Era {era.start}-{era.end}: start must be before end"


def test_eras_do_not_overlap() -> None:
    sorted_eras = sorted(CORRECTION_ERAS, key=lambda e: e.start)
    for i in range(1, len(sorted_eras)):
        prev = sorted_eras[i - 1]
        curr = sorted_eras[i]
        assert (
            prev.end <= curr.start
        ), f"Eras overlap: {prev.start}-{prev.end} and {curr.start}-{curr.end}"


def test_deployed_and_correct_differ() -> None:
    for era in CORRECTION_ERAS:
        assert (
            era.deployed != era.correct
        ), f"Era {era.start}: deployed and correct are identical"


def test_correct_has_more_or_different_activities() -> None:
    for era in CORRECTION_ERAS:
        assert len(era.correct) >= len(
            era.deployed
        ), f"Era {era.start}: correct should be >= deployed"


def test_renames_are_nonempty() -> None:
    for era in CORRECTION_ERAS:
        assert (
            len(era.renames) > 0
        ), f"Era {era.start}-{era.end}: renames should not be empty"


def test_era_0_baseline_count() -> None:
    assert len(ERA_0) == 59


def test_era_1_nex_added() -> None:
    assert len(ERA_1) == 60
    assert "Nex" in ERA_1
    assert "Nex" not in ERA_0


def test_era_20_final_count() -> None:
    assert len(ERA_20) == 89


def test_nex_era_renames() -> None:
    era = CORRECTION_ERAS[0]
    renames = era.renames
    assert renames["Nightmare"] == "Nex"
    assert renames["PhosanisNightmare"] == "Nightmare"
    assert "LeaguePoints" not in renames


def test_correction_era_cached_property() -> None:
    era = CorrectionEra(
        start="2020-01-01 00:00:00",
        end="2020-01-02 00:00:00",
        deployed=("A", "B", "C"),
        correct=("A", "X", "B", "C"),
    )
    assert era.renames == {"B": "X", "C": "B"}
    assert era.renames is era.renames
