"""Historical correction map for CSV-era off-by-one errors.

Between Dec 2021 and Feb 2026, the service parsed the OSRS HiScores CSV API
using hardcoded positional constants. When Jagex added new activities, all
activities from the insertion point onward were stored under the wrong label.

Each CorrectionEra defines a period where labels are wrong, along with the
deployed (incorrect) and correct activity orderings needed to compute renames.

ERA_0 is the baseline activity ordering; each subsequent ERA_N is derived from
ERA_{N-1} by applying the same insertions/reorderings Jagex's API underwent,
verified against git history at each fix commit.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class CorrectionEra:
    start: str
    end: str
    deployed: Tuple[str, ...]
    correct: Tuple[str, ...]

    @cached_property
    def renames(self) -> Dict[str, str]:
        result = {}
        for i, deployed_name in enumerate(self.deployed):
            if i < len(self.correct) and deployed_name != self.correct[i]:
                result[deployed_name] = self.correct[i]
        return result


# --- Activity lists verified from git history at each fix commit ---

# After 80fadb9 (2021-12-06) — baseline when data collection began.
ERA_0 = (
    "LeaguePoints",
    "BountyHunter_Hunter",
    "BountyHunter_Rogue",
    "ClueScrolls_all",
    "ClueScrolls_beginner",
    "ClueScrolls_easy",
    "ClueScrolls_medium",
    "ClueScrolls_hard",
    "ClueScrolls_elite",
    "ClueScrolls_master",
    "LMS_Rank",
    "SoulWars_Zeal",
    "AbyssalSire",
    "AlchemicalHydra",
    "BarrowsChests",
    "Bryophyta",
    "Callisto",
    "Cerberus",
    "ChambersofXeric",
    "ChambersofXeric_ChallengeMode",
    "ChaosElemental",
    "ChaosFanatic",
    "CommanderZilyana",
    "CorporealBeast",
    "CrazyArchaeologist",
    "DagannothPrime",
    "DagannothRex",
    "DagannothSupreme",
    "DerangedArchaeologist",
    "GeneralGraardor",
    "GiantMole",
    "GrotesqueGuardians",
    "Hespori",
    "KalphiteQueen",
    "KingBlackDragon",
    "Kraken",
    "KreeArra",
    "KrilTsutsaroth",
    "Mimic",
    "Nightmare",
    "PhosanisNightmare",
    "Obor",
    "Sarachnis",
    "Scorpia",
    "Skotizo",
    "Tempoross",
    "TheGauntlet",
    "TheCorruptedGauntlet",
    "TheatreofBlood",
    "TheatreofBlood_HardMode",
    "ThermonuclearSmokeDevil",
    "TzKalZuk",
    "TzTokJad",
    "Venenatis",
    "Vettion",
    "Vorkath",
    "Wintertodt",
    "Zalcano",
    "Zulrah",
)

# After 06fcf25 (2022-01-08) — Nex added, Skotizo/Scorpia swapped.
ERA_1 = ERA_0[:39] + ("Nex",) + ERA_0[39:43] + ("Skotizo", "Scorpia") + ERA_0[45:]

# After 0dcb8a0 (2022-04-14) — GuardiansOfTheRift added.
ERA_2 = ERA_1[:12] + ("GuardiansOfTheRift",) + ERA_1[12:]

# After 6edbd59 (2022-07-13) — PvPArena added (initially wrong position).
ERA_3 = ERA_2[:13] + ("PvPArena",) + ERA_2[13:]

# After d089fa4 (2022-07-14) — PvPArena reordered, Scorpia/Skotizo back.
ERA_4 = (
    ERA_3[:11]
    + ("PvPArena",)
    + ERA_3[11:13]
    + ERA_3[14:46]
    + ("Scorpia", "Skotizo")
    + ERA_3[48:]
)

# After 7fe6bcc (2022-08-24) — TombsOfAmascut + TombsOfAmascutExpert added.
ERA_5 = ERA_4[:54] + ("TombsOfAmascut", "TombsOfAmascutExpert") + ERA_4[54:]

# After 7a496c3 (2023-01-12) — PhantomMuspah added.
ERA_6 = ERA_5[:45] + ("PhantomMuspah",) + ERA_5[45:]

# After df822ad (2023-04-12) — Artio, Calvarion, Spindel added.
ERA_7 = (
    ERA_6[:16]
    + ("Artio",)
    + ERA_6[16:19]
    + ("Calvarion",)
    + ERA_6[19:49]
    + ("Spindel",)
    + ERA_6[49:]
)

# After 6a73186 (2023-05-24) — BountyHunter Legacy columns added.
ERA_8 = (
    ERA_7[:3] + ("BountyHunter_Hunter_Legacy", "BountyHunter_Rogue_Legacy") + ERA_7[3:]
)

# After a8333a3 (2023-07-30) — DT2 bosses added.
ERA_9 = (
    ERA_8[:35]
    + ("DukeSucellus",)
    + ERA_8[35:57]
    + ("TheLeviathan", "TheWhisperer")
    + ERA_8[57:64]
    + ("Vardorvis",)
    + ERA_8[64:]
)

# After 6c3e818 (2023-08-24) — DeadmanPoints added.
ERA_10 = ERA_9[:1] + ("DeadmanPoints",) + ERA_9[1:]

# After bc8728c (2024-01-24) — Scurrius added.
ERA_11 = ERA_10[:54] + ("Scurrius",) + ERA_10[54:]

# After 3534002 (2024-03-21) — Varlamore activities added.
ERA_12 = (
    ERA_11[:17]
    + ("ColosseumGlory",)
    + ERA_11[17:46]
    + ("LunarChests",)
    + ERA_11[46:56]
    + ("SolHeredit",)
    + ERA_11[56:]
)

# After d69bc68 (2024-08-28) — Araxxor added.
ERA_13 = ERA_12[:20] + ("Araxxor",) + ERA_12[20:]

# After 3d08b84 (2024-09-25) — Amoxliatl + TheHueycoatl added.
ERA_14 = ERA_13[:20] + ("Amoxliatl",) + ERA_13[20:64] + ("TheHueycoatl",) + ERA_13[64:]

# After 9fbff73 (2025-02-06) — CollectionsLogged + TheRoyalTitans added.
ERA_15 = (
    ERA_14[:18]
    + ("CollectionsLogged",)
    + ERA_14[18:67]
    + ("TheRoyalTitans",)
    + ERA_14[67:]
)

# After cee0569 (2025-05-20) — Yama added.
ERA_16 = ERA_15[:82] + ("Yama",) + ERA_15[82:]

# After 5956194 (2025-07-24) — DoomOfMokhaiotl added.
ERA_17 = ERA_16[:40] + ("DoomOfMokhaiotl",) + ERA_16[40:]

# After 12091a5 (2025-10-15) — GridPoints added.
ERA_18 = ("GridPoints",) + ERA_17

# After adfb564 (2025-11-07) — ShellbaneGryphon added.
ERA_19 = ERA_18[:62] + ("ShellbaneGryphon",) + ERA_18[62:]

# After b2e29c5 (2026-02-25) — Brutus added. Final CSV-era list.
ERA_20 = ERA_19[:26] + ("Brutus",) + ERA_19[26:]

# --- Correction eras ---
# deployed=constants the parser was using, correct=what API served.
# Dates marked "confirmed" were verified from production data via
# find_correction_boundaries.py on ElderPlinius. Others are estimates.

CORRECTION_ERAS: List[CorrectionEra] = [
    CorrectionEra(
        start="2022-01-05 00:00:00",  # estimated (Nex release)
        end="2022-01-08 20:14:04",
        deployed=ERA_0,
        correct=ERA_1,
    ),
    CorrectionEra(
        start="2022-04-13 00:00:00",  # confirmed
        end="2022-04-14 23:21:42",
        deployed=ERA_1,
        correct=ERA_2,
    ),
    CorrectionEra(
        start="2022-05-25 00:00:00",  # estimated
        end="2022-07-13 11:12:13",
        deployed=ERA_2,
        correct=ERA_3,
    ),
    CorrectionEra(
        start="2022-07-13 11:12:13",
        end="2022-07-14 20:19:41",
        deployed=ERA_3,
        correct=ERA_4,
    ),
    CorrectionEra(
        start="2022-08-24 00:00:00",  # estimated (ToA release)
        end="2022-08-24 12:12:32",
        deployed=ERA_4,
        correct=ERA_5,
    ),
    CorrectionEra(
        start="2023-01-04 00:00:00",  # estimated
        end="2023-01-12 21:43:43",
        deployed=ERA_5,
        correct=ERA_6,
    ),
    CorrectionEra(
        start="2023-03-29 00:00:00",  # estimated
        end="2023-04-12 13:03:10",
        deployed=ERA_6,
        correct=ERA_7,
    ),
    CorrectionEra(
        start="2023-05-24 00:00:00",  # confirmed
        end="2023-05-24 19:27:20",
        deployed=ERA_7,
        correct=ERA_8,
    ),
    CorrectionEra(
        start="2023-07-26 00:00:00",  # confirmed
        end="2023-07-30 20:52:38",
        deployed=ERA_8,
        correct=ERA_9,
    ),
    CorrectionEra(
        start="2023-08-23 00:00:00",  # confirmed
        end="2023-08-24 18:29:49",
        deployed=ERA_9,
        correct=ERA_10,
    ),
    CorrectionEra(
        start="2024-01-10 00:00:00",  # estimated
        end="2024-01-24 11:18:09",
        deployed=ERA_10,
        correct=ERA_11,
    ),
    CorrectionEra(
        start="2024-03-20 00:00:00",  # confirmed
        end="2024-03-21 13:01:54",
        deployed=ERA_11,
        correct=ERA_12,
    ),
    CorrectionEra(
        start="2024-07-24 00:00:00",  # estimated
        end="2024-08-28 08:16:03",
        deployed=ERA_12,
        correct=ERA_13,
    ),
    CorrectionEra(
        start="2024-09-25 00:00:00",  # estimated
        end="2024-09-25 08:25:31",
        deployed=ERA_13,
        correct=ERA_14,
    ),
    CorrectionEra(
        start="2025-01-29 00:00:00",  # confirmed
        end="2025-02-06 17:31:03",
        deployed=ERA_14,
        correct=ERA_15,
    ),
    CorrectionEra(
        start="2025-05-14 00:00:00",  # estimated
        end="2025-05-20 08:57:28",
        deployed=ERA_15,
        correct=ERA_16,
    ),
    CorrectionEra(
        start="2025-07-23 00:00:00",  # confirmed
        end="2025-07-24 18:04:07",
        deployed=ERA_16,
        correct=ERA_17,
    ),
    CorrectionEra(
        start="2025-10-15 00:00:00",  # confirmed
        end="2025-10-15 18:24:17",
        deployed=ERA_17,
        correct=ERA_18,
    ),
    CorrectionEra(
        start="2025-11-05 00:00:00",  # confirmed
        end="2025-11-07 18:13:48",
        deployed=ERA_18,
        correct=ERA_19,
    ),
    # Sailing (skill, 2025-11-19): parse failures, no data.
    CorrectionEra(
        start="2026-02-25 00:00:00",  # estimated
        end="2026-02-25 09:03:45",
        deployed=ERA_19,
        correct=ERA_20,
    ),
]
