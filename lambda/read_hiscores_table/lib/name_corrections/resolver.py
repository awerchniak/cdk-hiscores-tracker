"""Resolve a queried player name to its canonical name and all known aliases."""

from .name_map import NAME_CHANGES


def _canonical(name: str, name_map: dict[str, str]) -> str:
    """Follow the rename chain forward to the final (canonical) name."""
    seen: set[str] = set()
    while name in name_map:
        if name in seen:
            raise ValueError(f"Cycle detected in name map starting at '{name}'")
        seen.add(name)
        name = name_map[name]
    return name


def resolve_aliases(
    player: str, name_map: dict[str, str] = NAME_CHANGES
) -> tuple[str, set[str]]:
    """Resolve `player` to its canonical name and the set of all known aliases.

    Handles rename chains in either direction: querying any name in a chain
    A -> B -> C returns canonical "C" and aliases {A, B, C}. Untracked names
    (the common case) resolve to themselves with a single-element alias set.
    """
    canonical = _canonical(player, name_map)
    aliases = {canonical, player}
    for name in name_map:
        if _canonical(name, name_map) == canonical:
            aliases.add(name)
    return canonical, aliases
