from calendar import monthrange
from datetime import datetime, timedelta
from functools import total_ordering
from re import findall
from types import NotImplementedType
from typing import Any, Union


def microseconds(amount: int) -> timedelta:
    amount = abs(amount)
    return timedelta(microseconds=amount)


def milliseconds(amount: int) -> timedelta:
    amount = abs(amount)
    return timedelta(milliseconds=amount)


def seconds(amount: int) -> timedelta:
    amount = abs(amount)
    return timedelta(seconds=amount)


def minutes(amount: int) -> timedelta:
    amount = abs(amount)
    return timedelta(minutes=amount)


def hours(amount: int) -> timedelta:
    amount = abs(amount)
    return timedelta(hours=amount)


def days(amount: int) -> timedelta:
    amount = abs(amount)
    return timedelta(days=amount)


def weeks(amount: int) -> timedelta:
    amount = abs(amount)
    return timedelta(weeks=amount)


def months(amount: int) -> "_Months":
    amount = abs(amount)
    return _Months(amount)


def years(amount: int) -> "_Years":
    amount = abs(amount)
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
        return self._date.isoformat()

    def __str__(self) -> str:
        return self._date.strftime("%Y-%m-%d %H:%M:%S.%f")

    def __hash__(self) -> int:
        return hash(self._date)

    def __eq__(
        self,
        other: Any,
    ) -> Union[NotImplementedType, bool]:
        if isinstance(other, Time):
            return self._date == other._date
        if isinstance(other, datetime):
            return self._date == other
        return NotImplemented

    def __lt__(
        self,
        other: Union[datetime, "Time"],
    ) -> Union[NotImplementedType, bool]:
        if isinstance(other, Time):
            return self._date < other._date
        if isinstance(other, datetime):
            return self._date < other
        return NotImplemented

    def __add__(
        self,
        other: Union[timedelta, "_Months", "_Years"],
    ) -> Union[NotImplementedType, "Time"]:
        if isinstance(other, timedelta):
            return Time(self._date + other)
        if isinstance(other, _Months):
            return Time(self._shift_months(other.amount))
        if isinstance(other, _Years):
            return Time(self._shift_months(other.amount * 12))
        return NotImplemented

    def __sub__(
        self,
        other: Union[timedelta, "_Months", "_Years"],
    ) -> Union[NotImplementedType, "Time"]:
        if isinstance(other, timedelta):
            return Time(self._date - other)
        if isinstance(other, _Months):
            return Time(self._shift_months(-other.amount))
        if isinstance(other, _Years):
            return Time(self._shift_months(-other.amount * 12))
        return NotImplemented

    def _shift_months(self, moves: int) -> datetime:
        total_months = self._date.month + moves - 1

        new_year = self._date.year + (total_months // 12)
        new_month = (total_months % 12) + 1

        max_days = monthrange(new_year, new_month)[1]
        new_day = min(self._date.day, max_days)

        return self._date.replace(
            year=new_year,
            month=new_month,
            day=new_day,
        )

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
    def at(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
    ) -> "Time":
        return cls(
            datetime(
                year,
                month,
                day,
                hour,
                minute,
                second,
                microsecond,
            )
        )

    def format(self, layout: str) -> str:
        presets = {
            "T": "YYYY-MM-DD hh:mm:ss.F",
            "L": "YYYY-MM-DD hh-mm-ss.fff",
            "C": "AAAA, BBBB D YYYY hh:mm:ss",
            "S": "BBBB D, YYYY hh:mm",
            "E": "D BBBB YYYY hh:mm"
        }

        mapping = {
            "AAAA": "%A",
            "AAA": "%a",
            "BBBB": "%B",
            "BBB": "%b",
            "YYYY": "%Y",
            "YY": "%y",
            "MM": "%m",
            "DD": "%d",
            "hh": "%H",
            "ii": "%I",
            "mm": "%M",
            "ss": "%S",
            "F": "%f",
            "P": "%p",
            "p": "%p",
            "J": "%j",
            "U": "%U",
            "W": "%W",
        }

        for preset, expanded in presets.items():
            layout = layout.replace(preset, expanded)

        microseconds_as_string = self._date.strftime("%f")
        matches = findall(r"f+", layout)

        formatted = layout

        for match in matches:
            precision = len(match)
            sliced = microseconds_as_string[: min(precision, 6)]
            formatted = formatted.replace(match, sliced)

        for token, directive in mapping.items():
            formatted = formatted.replace(token, directive)

        result = self._date.strftime(formatted)

        if "p" in layout and "P" not in layout:
            result = result.replace("AM", "am")
            result = result.replace("PM", "pm")

        if "D" in layout:
            result = result.replace("D", str(self._date.day))
        if "M" in layout:
            result = result.replace("M", str(self._date.month))

        return result