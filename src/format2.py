from typing import TypedDict, Optional


class Log(TypedDict):
    datetime: str
    user_id: int
    amount: int
    note: Optional[str]


class Format(TypedDict):
    pool: int
    logs: list[Log]
