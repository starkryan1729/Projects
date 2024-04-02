from datetime import datetime, timezone
from pytz import timezone as pytz_timezone
from enum import Enum

def to_time_ns(dt) -> int:
    return int(dt.astimezone(tz=timezone.utc).timestamp() * 1e9)

def get_time_now(tz: str):
    return datetime.now(pytz_timezone(tz))

class Frequency(Enum):
    DAILY = 1
    WEEKLY = 2
    BIWEEKLY = 3
    MONTHLY = 4
    YEARLY = 5