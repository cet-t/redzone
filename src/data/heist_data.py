from dataclasses import dataclass
from enum import Enum
from typing import TypedDict, Final


class HEIST_TYPE(str, Enum):
    CUSTOM = "custom"
    STORE = "store"
    FREECA = "freeca"
    JEWELRY = "jewelry"
    YACHT = "yacht"
    THERMITE = "thermite"
    OILRIG = "oilrig"
    PACIFIC = "pacific"
    UNION = "union"
    TREASURE = "treasure"


class HeistDict(TypedDict):
    name: HEIST_TYPE
    members: int
    cops: int


heists: Final[list[HeistDict]] = [
    HeistDict(name=HEIST_TYPE.STORE, members=1, cops=3),
    HeistDict(name=HEIST_TYPE.FREECA, members=1, cops=4),
    HeistDict(name=HEIST_TYPE.JEWELRY, members=1, cops=5),
    HeistDict(name=HEIST_TYPE.YACHT, members=6, cops=6),
    HeistDict(name=HEIST_TYPE.THERMITE, members=6, cops=6),
    HeistDict(name=HEIST_TYPE.OILRIG, members=7, cops=7),
    HeistDict(name=HEIST_TYPE.PACIFIC, members=8, cops=8),
    HeistDict(name=HEIST_TYPE.UNION, members=8, cops=8),
]


class HeistRecordDict(TypedDict):
    date: str  # int datetime.datetime
    members_reward: dict[int, int]  # [id, reward_amount]
    total_amount: int
