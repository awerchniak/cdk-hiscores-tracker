"""Player rename map for players.txt name-change history.

When a tracked player renames their OSRS account, `players.txt` is updated
to poll the new name going forward (see e.g. commit 7b29dc0). Historical
DynamoDB data remains under the old name's partition key ("player" is the
table's literal partition key with no secondary index), so the read API
resolves aliases through this map at query time to stitch history together.

Unlike historical_corrections/correction_map.py, these mappings are NOT
time-boundaries -- once a player is renamed, the orchestrator only polls the
new name forever after, so the old name can never be "recycled" by this
tracker. A flat, unconditional alias map is therefore safe.

NAME_CHANGES maps old_name -> new_name for a single rename hop. Chains
(e.g. a player renamed twice) are represented as two entries and resolved
transitively by resolver.resolve_aliases.
"""

from typing import Dict

NAME_CHANGES: Dict[str, str] = {
    # commit efc6ab9 (2024-10-05) / 0dbf6e5 (2024-11-03)
    "State Lad": "sstate",
    "sstate": "state 0",
    # commit 0fc0acc (2025-04-19)
    "GI Pliny": "Plinybis",
    # commit 7b29dc0 (2025-05-03)
    "GI Jobra": "DrPlingo0",
}
