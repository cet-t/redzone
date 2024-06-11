from typing import TypedDict, Optional


class Log(TypedDict):
    id: int
    datetime: str
    user_id: int
    amount: int
    note: Optional[str]
    is_cancelled: bool


class Format(TypedDict):
    pool: int
    logs: list[Log]
