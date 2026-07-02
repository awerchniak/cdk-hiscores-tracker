import pytest
from read_hiscores_table.lib.name_corrections.resolver import (
    _canonical,
    resolve_aliases,
)


def test_untracked_player_is_noop():
    canonical, aliases = resolve_aliases("ElderPlinius")
    assert canonical == "ElderPlinius"
    assert aliases == {"ElderPlinius"}


def test_resolve_old_name_to_canonical():
    canonical, aliases = resolve_aliases("GI Jobra")
    assert canonical == "DrPlingo0"
    assert aliases == {"GI Jobra", "DrPlingo0"}


def test_resolve_new_name_still_returns_full_alias_set():
    canonical, aliases = resolve_aliases("DrPlingo0")
    assert canonical == "DrPlingo0"
    assert aliases == {"GI Jobra", "DrPlingo0"}


def test_multi_hop_chain_from_original_name():
    # Real chain: State Lad -> sstate -> state 0
    canonical, aliases = resolve_aliases("State Lad")
    assert canonical == "state 0"
    assert aliases == {"State Lad", "sstate", "state 0"}


def test_multi_hop_chain_from_middle_name():
    canonical, aliases = resolve_aliases("sstate")
    assert canonical == "state 0"
    assert aliases == {"State Lad", "sstate", "state 0"}


def test_multi_hop_chain_from_canonical_name():
    canonical, aliases = resolve_aliases("state 0")
    assert canonical == "state 0"
    assert aliases == {"State Lad", "sstate", "state 0"}


def test_independent_rename_pairs_do_not_cross_contaminate():
    _, aliases = resolve_aliases("GI Pliny")
    assert "GI Jobra" not in aliases
    assert "DrPlingo0" not in aliases


def test_synthetic_two_hop_chain_with_injected_map():
    name_map = {"A": "B", "B": "C"}
    canonical, aliases = resolve_aliases("A", name_map=name_map)
    assert canonical == "C"
    assert aliases == {"A", "B", "C"}


def test_cycle_detection_raises():
    name_map = {"A": "B", "B": "A"}
    with pytest.raises(ValueError):
        resolve_aliases("A", name_map=name_map)


def test_canonical_helper_directly():
    name_map = {"X": "Y"}
    assert _canonical("X", name_map) == "Y"
    assert _canonical("Y", name_map) == "Y"
    assert _canonical("Z", name_map) == "Z"
