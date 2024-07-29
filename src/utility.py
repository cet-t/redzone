from enum import Enum
from random import randint
from typing import Final, TypeVar

import discord

T = TypeVar('T')

# region discord


class Discord:

    class Mention(Enum):
        none = 0
        user = 1
        channel = 2

    @staticmethod
    def code_block(text: str) -> str:
        return f'```{text}```'

    @staticmethod
    def inline_code_block(text: str) -> str:
        return f'`{text}`'

    @staticmethod
    def mention(id: int | None, mention_type: Mention) -> str:
        if type(id) is None:
            return String.empty

        match mention_type:
            case Discord.Mention.user:
                return f'<@{id}>'
            case Discord.Mention.channel:
                return f'<#{id}>'
            case _:
                return String.empty


# endregion discord

# region string

class String:
    empty: Final[str] = ''

    @staticmethod
    def is_none_or_empty(source: str | None) -> bool:
        return source is None or source == String.empty

# endregion


class Random:
    @staticmethod
    def choice(list: list[T]) -> int:
        return randint(0, len(list)-1)

    @staticmethod
    def choice_item(list: list[T]) -> T:
        return list[Random.choice(list)]
