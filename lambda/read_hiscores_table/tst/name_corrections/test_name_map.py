from read_hiscores_table.lib.name_corrections.name_map import NAME_CHANGES


def test_no_self_mapping():
    for old, new in NAME_CHANGES.items():
        assert old != new, f"'{old}' maps to itself"


def test_no_cycles():
    for name in NAME_CHANGES:
        seen = set()
        current = name
        while current in NAME_CHANGES:
            assert current not in seen, f"Cycle detected starting at '{name}'"
            seen.add(current)
            current = NAME_CHANGES[current]


def test_known_renames_present():
    assert NAME_CHANGES["GI Jobra"] == "DrPlingo0"
    assert NAME_CHANGES["GI Pliny"] == "Plinybis"
    assert NAME_CHANGES["State Lad"] == "sstate"
    assert NAME_CHANGES["sstate"] == "state 0"
