from enum import Enum
from typing import TypedDict, Final


class TYPE(str, Enum):
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
    name: TYPE
    members: int
    cops: int


heists: Final[list[HeistDict]] = [
    HeistDict(name=TYPE.STORE, members=1, cops=3),
    HeistDict(name=TYPE.FREECA, members=1, cops=4),
    HeistDict(name=TYPE.JEWELRY, members=1, cops=5),
    HeistDict(name=TYPE.YACHT, members=6, cops=6),
    HeistDict(name=TYPE.THERMITE, members=6, cops=6),
    HeistDict(name=TYPE.OILRIG, members=7, cops=7),
    HeistDict(name=TYPE.PACIFIC, members=8, cops=8),
    HeistDict(name=TYPE.UNION, members=8, cops=8),
]


class HeistRecordDict(TypedDict):
    date: str  # int datetime.datetime
    members_reward: dict[int, int]  # [id, reward_amount]
    total_amount: int
