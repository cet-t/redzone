from enum import Enum
from typing import Final, TypedDict, Optional
import discord

import utility


class LogDataDict(TypedDict):
    id: int
    datetime: str
    user_id: int
    amount: int
    note: Optional[str]
    is_cancelled: bool
    is_pending: bool
    message_id: int


class LogDict(TypedDict):
    pool: int
    logs: list[LogDataDict]


class Parameter:
    TOKEN = 'TOKEN'

    LOG_FILE_PATH = '../log/cost.json'
    COST_CHANNEL_ID: Final[dict[str, int]] = {
        'test': 1245694945323520031,
        'redzone': 1222545209578229790
    }
    ADMIN_USER_ID: Final[dict[str, int]] = {
        'boss': 421317690418790409,
        'dev': 283584931437871104
    }

    class Emoji:
        ACCEPT = ['white_check_mark']
        REJECT = ['']

    class Key:
        class LogData:
            ID = 'id'
            DATETIME = 'datetime'
            USER_ID = 'user_id'
            AMOUNT = 'amount'
            NOTE = 'note'
            IS_CANCELLED = 'is_cancelled'
            IS_PENDING = 'is_pending'
            MESSAGE_ID = 'message_id'

        class Log:
            POOL = 'pool'
            LOGS = 'logs'

    class Text:
        REDZONE = '🔥REDZONE🔥'
        AMOUNT = '金額'
        NOTE = '支払内容'
        POOL = 'チームプール'

        PENDING = 'Pending...'
        CANCEL = 'Cancel'
        RECEIPT = 'Receipt'
        ACCEPT = 'Accepted'
        REJECT = 'Reject.'

    class Embed:
        @staticmethod
        def error(description: str) -> discord.Embed:
            embed = discord.Embed(title='Error', description=description, colour=discord.Colour.red())
            embed.set_footer(text=Parameter.Text.REDZONE)
            return embed

        @staticmethod
        def warning(description: str) -> discord.Embed:
            embed = discord.Embed(title='Warning', description=description, colour=discord.Colour.pink())
            embed.set_footer(text=Parameter.Text.REDZONE)
            return embed

        @staticmethod
        def log(description: str) -> discord.Embed:
            embed = discord.Embed(title='', description=description, colour=discord.Colour(0xdfdfdf))
            embed.set_footer(text=Parameter.Text.REDZONE)
            return embed
