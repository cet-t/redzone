from enum import Enum
from random import randint
from typing import Final, TypeVar, Optional

import discord

T = TypeVar('T')

# region discord


class Discord:

    class Mention(Enum):
        USER = 0
        CHANNEL = 1

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
            case Discord.Mention.USER: return f'<@{id}>'
            case Discord.Mention.CHANNEL: return f'<#{id}>'


# endregion discord

# region string

class String:
    empty: Final[str] = ''

    @staticmethod
    def is_null_or_empty(source: str) -> bool:
        return source is None or source == String.empty

# endregion


class Random:
    @staticmethod
    def choice(list: list[T]) -> int:
        return randint(0, len(list)-1)

    @staticmethod
    def choice_item(list: list[T]) -> T:
        return list[Random.choice(list)]


class FileMode:
    READ = 'r'
    CREATE_WRITE = 'x'
