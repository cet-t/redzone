from enum import Enum
from typing import TypedDict, Optional


class LogDataDict(TypedDict):
    id: int
    datetime: str
    user_id: int
    amount: int
    note: Optional[str]
    is_cancelled: bool
    is_pending: bool


class LogDataKey:
    ID = 'id'
    DATETIME = 'datetime'
    USER_ID = 'user_id'
    AMOUNT = 'amount'
    NOTE = 'note'
    IS_CANCELLED = 'is_cancelled'
    IS_PENDING = 'is_pending'


class LogDict(TypedDict):
    pool: int
    logs: list[LogDataDict]


class LogKey:
    POOL = 'pool'
    LOGS = 'logs'


class PendingLog(TypedDict):
    id: list[int]
