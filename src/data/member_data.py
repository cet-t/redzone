from typing import TypedDict
from enum import Enum, IntEnum


class RANK(IntEnum):
    BOSS = 0
    UNDER_BOSS = 1
    MEMBER = 8

    @classmethod
    def to_rank(cls, value: int):
        return RANK(value).name


class MemberDict(TypedDict):
    name: str  # in game
    rank: RANK
    id: int  # discord id
    roles: list[int]  # roles


# example = MemberDict(name='cet colour', rank=RANK.MEMBER, id=DISCORD_ID, roles=HAS_ROLES)
