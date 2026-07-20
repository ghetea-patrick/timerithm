from calendar import monthrange
from datetime import datetime, timedelta
from functools import total_ordering
from re import findall
from types import NotImplementedType


def microseconds(amount: int) -> timedelta:
    return timedelta(microseconds=amount)


def milliseconds(amount: int) -> timedelta:
    return timedelta(milliseconds=amount)


def seconds(amount: int) -> timedelta:
    return timedelta(seconds=amount)


def minutes(amount: int) -> timedelta:
    return timedelta(minutes=amount)


def hours(amount: int) -> timedelta:
    return timedelta(hours=amount)


def days(amount: int) -> timedelta:
    return timedelta(days=amount)


def weeks(amount: int) -> timedelta:
    return timedelta(weeks=amount)


def months(amount: int) -> "_Months":
    return _Months(amount)


def years(amount: int) -> "_Years":
    return _Years(amount)


class _Months:
    def __init__(self, amount: int) -> None:
        self.amount = amount


class _Years:
    def __init__(self, amount: int) -> None:
        self.amount = amount


@total_ordering
class Time:
    def __init__(self, date: datetime) -> None:
        self._date = date

    def __repr__(self) -> str:
        return f"<not implemented>"

    def __str__(self) -> str:
        return f"not implemented"

    def __hash__(self) -> int:
        return hash(self._date)
    
    def __eq__(self, other: object) -> bool | NotImplementedType:
        if isinstance(other, Time):
            return self._date == other._date
        if isinstance(other, datetime):
            return self._date == other
        return NotImplemented
    
    def __lt__(self, other: object) -> bool | NotImplementedType:
        if isinstance(other, Time):
            return self._date < other._date
        if isinstance(other, datetime):
            return self._date < other
        return NotImplemented
    
    def __add__(self, other: object) -> "Time | NotImplementedType":
        if isinstance(other, timedelta):
            return Time(self._date + other)
        if isinstance(other, _Months):
            return Time(self._shift_months(other.amount))
        if isinstance(other, _Years):
            return Time(self._shift_months(other.amount * 12))
        return NotImplemented

    def __sub__(self, other: object) -> "Time | NotImplementedType":
        if isinstance(other, timedelta):
            return Time(self._date - other)
        if isinstance(other, _Months):
            return Time(self._shift_months(-other.amount))
        if isinstance(other, _Years):
            return Time(self._shift_months(-other.amount * 12))
        return NotImplemented

    def _shift_months(self, amount: int) -> datetime:
        total = self._date.month + amount - 1

        new_year = (total // 12) + self._date.year
        new_month = (total % 12) + 1

        max_day = monthrange(new_year, new_month)[1] 
        new_day = min(self._date.day, max_day)

        return self._date.replace(year=new_year, month=new_month, day=new_day)

    @property
    def microsecond(self) -> int:
        return self._date.microsecond

    @property
    def millisecond(self) -> int:
        return self._date.microsecond // 1000

    @property
    def second(self) -> int:
        return self._date.second

    @property
    def minute(self) -> int:
        return self._date.minute

    @property
    def hour(self) -> int:
        return self._date.hour

    @property
    def day(self) -> int:
        return self._date.day

    @property
    def month(self) -> int:
        return self._date.month

    @property
    def year(self) -> int:
        return self._date.year

    @classmethod
    def now(cls) -> "Time":
        return cls(datetime.now())

    @classmethod
    def at(cls, year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0) -> "Time":
        return cls(datetime(year, month, day, hour, minute, second, microsecond))
    
    def format(self, layout: str) -> str:
        presets = {
            "S": "BBBB D, YYYY hh:mm",
            "E": "D BBBB, YYYY hh:mm",
            "L": "YYYYMMDDhhmmss",
            "T": "YYYY-MM-DD hh:mm:ss",
            "C": "AAAA, BBBB D YYYY hh:mm:ss",
        }

        mapping = {
            "AAAA": "%A", "AAA": "%a", "BBBB": "%B", "BBB": "%b",
            "YYYY": "%Y", "YY": "%y", "MM": "%m", "DD": "%d",
            "hh": "%H", "ii": "%I", "mm": "%M", "ss": "%S",
            "F": "%f", "J": "%j", "U": "%u", "W": "%w",
            "P": "%p", "p": "%p"
        }

        if "f" in layout:
            microsecond = self._date.strftime("%f")

            for match in findall(r"f+", layout):
                sliced = microsecond[:min(len(match), 6)]
                layout = layout.replace(match, sliced)

        for preset, expansion in presets.items():
            layout = layout.replace(preset, expansion)

        if "D" in layout:
            layout = layout.replace("D", str(self._date.day))
        if "M" in layout:
            layout = layout.replace("M", str(self._date.month))
    
        result = self._date.strftime(layout)

        if "p" in layout:
            result = result.replace("AM", "am")
            result = result.replace("PM", "pm")

        return result
