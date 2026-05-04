"""
Datetime utility helpers (stdlib only, no external dependencies)
"""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")


def now_jst() -> datetime:
    return datetime.now(tz=JST)


def format_date(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    return dt.strftime(fmt)


def days_between(d1: date, d2: date) -> int:
    return abs((d2 - d1).days)


def is_business_day(dt: date) -> bool:
    return dt.weekday() < 5  # Monday=0 … Friday=4


def next_business_day(dt: date) -> date:
    dt = dt + timedelta(days=1)
    while not is_business_day(dt):
        dt += timedelta(days=1)
    return dt


if __name__ == "__main__":
    now = now_jst()
    print("Now (JST):", format_date(now))
    print("Date only:", format_date(now, "%Y/%m/%d"))

    d1 = date(2025, 1, 1)
    d2 = date(2025, 12, 31)
    print(f"Days between {d1} and {d2}: {days_between(d1, d2)}")

    today = date.today()
    print(f"Today ({today.strftime('%A')}) is business day: {is_business_day(today)}")
    print(f"Next business day: {next_business_day(today)}")
