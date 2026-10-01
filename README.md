# Timerithm

### A Python time utility with slightly fewer calendar-related inconveniences.

Welcome to **Timerithm**, a lightweight Python utility for working with dates, times, durations, and calendar-aware arithmetic.

Timerithm is built on top of Python's standard `datetime` and `timedelta` modules while providing a simpler and more expressive interface for common time operations.

Timerithm provides several conveniences:

- **Readable duration constructors** for microseconds, milliseconds, seconds, minutes, hours, days, and weeks.
- **Calendar-aware month and year arithmetic** through `months()` and `years()`.
- **Automatic month-end correction** when shifting dates into shorter months.
- **Comparable `Time` objects** supporting equality and chronological comparisons.
- **Simple date construction** through `Time.at()`.
- **Current-time construction** through `Time.now()`.
- **Direct date and time component access** through properties.
- **Custom formatting syntax** with predefined layouts and readable formatting tokens.

Timerithm intentionally keeps its implementation small while making common date and time operations easier to express.

It is designed for programmers who want to work with time without repeatedly typing `datetime.timedelta(...)`.

Because apparently writing `hours(3)` was easier than writing `timedelta(hours=3)`.

---

## 1. Installation

Timerithm uses Python's standard library and does not require external dependencies.

Import the required functions and classes from the Timerithm module.

```python
from timerithm import (
    Time,
    microseconds,
    milliseconds,
    seconds,
    minutes,
    hours,
    days,
    weeks,
    months,
    years,
)
```

Replace `timerithm` with the module path used by your installation.

Timerithm is designed to work with standard Python `datetime` objects and `timedelta` values.

---

## 2. Duration Constructors

Timerithm provides helper functions for creating common time durations.

### 2.1 Fixed Durations

| Function | Description | Underlying Type |
|---|---|---|
| `microseconds(n)` | Create a duration measured in microseconds. | `timedelta` |
| `milliseconds(n)` | Create a duration measured in milliseconds. | `timedelta` |
| `seconds(n)` | Create a duration measured in seconds. | `timedelta` |
| `minutes(n)` | Create a duration measured in minutes. | `timedelta` |
| `hours(n)` | Create a duration measured in hours. | `timedelta` |
| `days(n)` | Create a duration measured in days. | `timedelta` |
| `weeks(n)` | Create a duration measured in weeks. | `timedelta` |

Each function accepts an integer amount.

Example:

```python
seconds(30)
minutes(5)
hours(2)
days(7)
weeks(3)
```

These functions return standard Python `timedelta` objects.

They can therefore be used directly with `Time` instances.

```python
now = Time.now()

later = now + hours(2)
earlier = now - days(3)
```

Fixed-duration arithmetic follows the behavior of Python's `timedelta`.

---

## 3. Calendar Durations

Timerithm provides separate duration types for months and years.

Unlike seconds or days, months and years do not have a fixed duration.

### 3.1 Months

The `months()` function creates a calendar-month duration.

```python
months(3)
```

The resulting object can be added to or subtracted from a `Time` instance.

```python
date = Time.at(2026, 1, 15)

result = date + months(3)
```

The resulting date is:

```text
2026-04-15
```

### 3.2 Years

The `years()` function creates a calendar-year duration.

```python
years(2)
```

Year arithmetic is internally implemented as twelve-month arithmetic.

```python
date = Time.at(2026, 1, 15)

result = date + years(2)
```

The resulting date is:

```text
2028-01-15
```

Calendar durations are represented internally by `_Months` and `_Years`.

These classes are implementation details and are not intended to be instantiated directly.

---

## 4. Time Class

The `Time` class provides the primary interface for working with dates and times in Timerithm.

Each `Time` instance wraps a Python `datetime` object.

```python
date = Time.at(2026, 10, 1)
```

The underlying `datetime` object is stored internally and is used for arithmetic, comparison, formatting, and component access.

---

## 5. Creating Time Objects

Timerithm provides two class methods for constructing `Time` instances.

### 5.1 Current Time

Use `Time.now()` to create a `Time` instance representing the current local date and time.

```python
current = Time.now()
```

Internally, this uses:

```python
datetime.now()
```

The returned value contains the current year, month, day, hour, minute, second, and microsecond.

### 5.2 Explicit Date and Time

Use `Time.at()` to construct a specific date and time.

```python
date = Time.at(2026, 10, 1)
```

The complete signature is:

```python
Time.at(
    year,
    month,
    day,
    hour=0,
    minute=0,
    second=0,
    microsecond=0
)
```

For example:

```python
date = Time.at(
    2026,
    10,
    1,
    14,
    30,
    45,
    123456
)
```

This creates a `Time` object representing:

```text
2026-10-01 14:30:45.123456
```

Date validation is handled by Python's `datetime` constructor.

Invalid dates therefore raise the same exceptions produced by `datetime`.

---

## 6. Time Arithmetic

Timerithm overloads the `+` and `-` operators to support intuitive time calculations.

### 6.1 Adding Fixed Durations

```python
date = Time.at(2026, 10, 1)

date + seconds(30)
date + minutes(15)
date + hours(2)
date + days(7)
```

Each operation returns a new `Time` object.

The original object is not modified.

For example:

```python
date = Time.at(2026, 10, 1)

future = date + days(5)
```

The values are:

```text
date = 2026-10-01
future = 2026-10-06
```

### 6.2 Subtracting Fixed Durations

Fixed durations can also be subtracted.

```python
date = Time.at(2026, 10, 10)

previous = date - days(5)
```

The resulting date is:

```text
2026-10-05
```

Timerithm delegates fixed-duration arithmetic to Python's `timedelta`.

---

## 7. Calendar-Aware Month Arithmetic

Month arithmetic is handled separately from `timedelta` arithmetic.

This is necessary because months do not contain a fixed number of days.

### 7.1 Adding Months

```python
date = Time.at(2026, 1, 15)

result = date + months(2)
```

Result:

```text
2026-03-15
```

Month arithmetic correctly handles changes in year.

```python
date = Time.at(2026, 11, 15)

result = date + months(3)
```

Result:

```text
2027-02-15
```

### 7.2 Subtracting Months

Months can also be subtracted.

```python
date = Time.at(2026, 5, 15)

result = date - months(2)
```

Result:

```text
2026-03-15
```

### 7.3 Month-End Correction

When shifting a date into a month that does not contain the original day, Timerithm automatically uses the last valid day of the destination month.

For example:

```python
date = Time.at(2026, 1, 31)

result = date + months(1)
```

February does not contain a 31st day.

Timerithm therefore produces:

```text
2026-02-28
```

Leap years are handled through Python's `calendar.monthrange()`.

```python
date = Time.at(2024, 1, 31)

result = date + months(1)
```

Result:

```text
2024-02-29
```

The time components are preserved during month arithmetic.

```python
date = Time.at(2026, 1, 31, 14, 30, 45)

result = date + months(1)
```

Result:

```text
2026-02-28 14:30:45
```

The calendar may change the day.

It does not get to mess with the clock.

---

## 8. Year Arithmetic

Year arithmetic is implemented using month arithmetic.

One year corresponds to twelve calendar months.

### Adding Years

```python
date = Time.at(2026, 10, 1)

result = date + years(2)
```

Result:

```text
2028-10-01
```

### Subtracting Years

```python
date = Time.at(2028, 10, 1)

result = date - years(2)
```

Result:

```text
2026-10-01
```

Year calculations also inherit the month-end handling behavior of `_shift_months()`.

For example:

```python
date = Time.at(2024, 2, 29)

result = date + years(1)
```

The destination year does not contain February 29.

Timerithm therefore adjusts the result to the final valid day:

```text
2025-02-28
```

---

## 9. Time Comparison

`Time` objects support equality and chronological comparisons.

The class uses Python's `@total_ordering` decorator to provide the complete set of ordering operations from `__eq__()` and `__lt__()`.

### Supported Comparisons

| Operator | Description |
|---|---|
| `==` | Equal timestamps |
| `!=` | Different timestamps |
| `<` | Earlier than |
| `<=` | Earlier than or equal to |
| `>` | Later than |
| `>=` | Later than or equal to |

### Example

```python
first = Time.at(2026, 1, 1)
second = Time.at(2026, 6, 1)

print(first < second)
print(first == second)
print(second > first)
```

Output:

```text
True
False
True
```

### Comparing with `datetime`

`Time` objects can also be compared directly with Python `datetime` objects.

```python
from datetime import datetime

timerithm_time = Time.at(2026, 1, 1)
python_time = datetime(2026, 1, 1)

print(timerithm_time == python_time)
```

Output:

```text
True
```

The comparison is performed against the underlying `_date` value.

Unsupported comparison types return `NotImplemented`, allowing Python to handle the operation according to its normal comparison rules.

---

## 10. Hashing

`Time` implements `__hash__()` using the wrapped `datetime`.

This allows `Time` instances to be used in hash-based collections such as sets and dictionaries.

Example:

```python
date = Time.at(2026, 1, 1)

dates = {date}

print(date in dates)
```

Output:

```text
True
```

Two `Time` instances representing the same underlying `datetime` produce equivalent hash behavior.

Because time apparently needed to become hashable too.

---

## 11. Date and Time Properties

Timerithm exposes individual components of the underlying datetime through read-only properties.

| Property | Description |
|---|---|
| `microsecond` | Microsecond component. |
| `millisecond` | Millisecond component. |
| `second` | Second component. |
| `minute` | Minute component. |
| `hour` | Hour component. |
| `day` | Day of the month. |
| `month` | Month number. |
| `year` | Year number. |

### Example

```python
date = Time.at(
    2026,
    10,
    1,
    14,
    30,
    45,
    123456
)

print(date.year)
print(date.month)
print(date.day)

print(date.hour)
print(date.minute)
print(date.second)

print(date.millisecond)
print(date.microsecond)
```

Output:

```text
2026
10
1
14
30
45
123
123456
```

### Milliseconds

The `millisecond` property is derived from the underlying microsecond value:

```python
self._date.microsecond // 1000
```

Therefore:

```text
123456 microseconds
```

becomes:

```text
123 milliseconds
```

The remaining fractional precision is discarded.

---

## 12. Formatting

Timerithm provides custom date and time formatting through the `format()` method.

```python
date.format(layout)
```

The formatter supports:

- Predefined layouts.
- Custom formatting tokens.
- Fractional seconds.
- 12-hour and 24-hour clocks.
- Weekday names.
- Month names.
- AM/PM formatting.

Example:

```python
date = Time.at(2026, 10, 1, 14, 30, 45)

print(date.format("T"))
```

Output:

```text
2026-10-01 14:30:45
```

---

## 13. Predefined Formatting Layouts

Timerithm provides several predefined layout shortcuts.

| Preset | Expansion | Example |
|---|---|---|
| `S` | `BBBB D, YYYY hh:mm` | October 1, 2026 14:30 |
| `E` | `D BBBB, YYYY hh:mm` | 1 October, 2026 14:30 |
| `L` | `YYYYMMDDhhmmss` | 20261001143045 |
| `T` | `YYYY-MM-DD hh:mm:ss` | 2026-10-01 14:30:45 |
| `C` | `AAAA, BBBB D YYYY hh:mm:ss` | Thursday, October 1 2026 14:30:45 |

### Example

```python
date = Time.at(2026, 10, 1, 14, 30, 45)

print(date.format("S"))
print(date.format("E"))
print(date.format("L"))
print(date.format("T"))
print(date.format("C"))
```

The preset is expanded before the final `strftime()` operation.

---

## 14. Formatting Tokens

Timerithm supports readable formatting tokens that are converted into Python `strftime` directives.

| Token | Description |
|---|---|
| `AAAA` | Full weekday name |
| `AAA` | Abbreviated weekday name |
| `BBBB` | Full month name |
| `BBB` | Abbreviated month name |
| `YYYY` | Four-digit year |
| `YY` | Two-digit year |
| `MM` | Zero-padded month |
| `DD` | Zero-padded day |
| `hh` | 24-hour clock hour |
| `ii` | 12-hour clock hour |
| `mm` | Minute |
| `ss` | Second |
| `F` | Microseconds |
| `J` | Day of the year |
| `U` | ISO weekday number |
| `W` | Weekday number |
| `P` | AM/PM |
| `p` | Lowercase AM/PM |

### Example

```python
date = Time.at(2026, 10, 1, 14, 30, 45)

print(date.format("AAAA, BBBB D YYYY"))
```

Example output:

```text
Thursday, October 1 2026
```

Another example:

```python
print(date.format("ii:mm p"))
```

Output:

```text
02:30 pm
```

---

## 15. Unpadded Day and Month

Timerithm provides special handling for `D` and `M`.

The `D` token represents the numerical day of the month without zero-padding.

The `M` token represents the numerical month without zero-padding.

For example:

```python
date = Time.at(2026, 3, 5)

print(date.format("M/D/YYYY"))
```

Output:

```text
3/5/2026
```

This differs from:

```python
date.format("MM/DD/YYYY")
```

which produces:

```text
03/05/2026
```

This distinction allows both padded and unpadded calendar representations.

---

## 16. Fractional Seconds

Timerithm supports repeated `f` characters for formatting fractional seconds.

The number of `f` characters determines how many digits of the microsecond component are included.

```python
date = Time.at(
    2026,
    10,
    1,
    14,
    30,
    45,
    123456
)
```

### Examples

```python
date.format("hh:mm:ss.f")
```

Output:

```text
14:30:45.1
```

```python
date.format("hh:mm:ss.fff")
```

Output:

```text
14:30:45.123
```

```python
date.format("hh:mm:ss.ffffff")
```

Output:

```text
14:30:45.123456
```

Timerithm truncates the microsecond string to the requested number of digits.

The maximum meaningful precision is six digits because Python's `datetime` stores microseconds.

---

## 17. AM/PM Formatting

The formatter supports both uppercase and lowercase AM/PM output.

Using:

```text
P
```

produces the standard `AM` or `PM` representation.

Using:

```text
p
```

produces lowercase `am` or `pm`.

Example:

```python
date = Time.at(2026, 10, 1, 14, 30)

print(date.format("ii:mm P"))
print(date.format("ii:mm p"))
```

Output:

```text
02:30 PM
02:30 pm
```

The lowercase form is implemented by replacing `AM` and `PM` after `strftime()` formatting.

---

## 18. Complete Example

The following example demonstrates the primary features of Timerithm.

```python
from timerithm import (
    Time,
    hours,
    days,
    months,
    years,
)

# Create a starting date

start = Time.at(
    2024,
    1,
    31,
    12,
    30,
    45
)

# Perform fixed-duration arithmetic

later = start + hours(5)
next_week = start + days(7)

# Perform calendar arithmetic

next_month = start + months(1)
next_year = start + years(1)

# Compare dates

print(next_month > start)

# Inspect components

print(next_month.year)
print(next_month.month)
print(next_month.day)

# Format results

print(start.format("C"))
print(later.format("T"))
print(next_month.format("YYYY-MM-DD"))
print(next_year.format("S"))
```

### Expected Output

```text
True
2024
2
29
Wednesday, January 31 2024 12:30:45
2024-01-31 17:30:45
2024-02-29
January 31, 2025 12:30
```

The example demonstrates:

1. Explicit time construction.
2. Fixed-duration arithmetic.
3. Calendar-aware month arithmetic.
4. Calendar-aware year arithmetic.
5. Date comparison.
6. Component inspection.
7. Custom formatting.
8. Automatic leap-year handling.

---

## 19. Design Philosophy

Timerithm is designed as a lightweight abstraction over Python's existing date and time functionality.

Rather than replacing `datetime`, it builds on top of it.

The library separates fixed durations from calendar durations:

- `timedelta` handles microseconds through weeks.
- `_Months` handles calendar-month arithmetic.
- `_Years` represents calendar years through twelve-month shifts.

This distinction allows Timerithm to provide intuitive month and year arithmetic without pretending that every month contains the same number of days.

The `Time` class keeps the underlying `datetime` available internally while providing:

- Simple construction.
- Operator-based arithmetic.
- Direct comparison.
- Component properties.
- Custom formatting.

Timerithm is intentionally compact and relies heavily on Python's standard library rather than implementing another independent date/time system.

The goal is not to reinvent time.

Time has already done enough damage.

---

## 20. API Summary

### Duration Functions

```python
microseconds(amount)
milliseconds(amount)
seconds(amount)
minutes(amount)
hours(amount)
days(amount)
weeks(amount)
months(amount)
years(amount)
```

### `Time` Class

```python
Time(date)
```

### Class Methods

```python
Time.now()
Time.at(
    year,
    month,
    day,
    hour=0,
    minute=0,
    second=0,
    microsecond=0
)
```

### Arithmetic

```python
time + timedelta
time - timedelta

time + months(n)
time - months(n)

time + years(n)
time - years(n)
```

### Comparison

```python
time == other
time != other
time < other
time <= other
time > other
time >= other
```

### Properties

```python
time.microsecond
time.millisecond
time.second
time.minute
time.hour
time.day
time.month
time.year
```

### Formatting

```python
time.format(layout)
```

---

## 21. Limitations

Timerithm intentionally remains a small wrapper around Python's standard date/time facilities.

The current implementation does not provide:

- Time zone management.
- Time zone conversion.
- Daylight-saving-time utilities.
- Relative date parsing.
- Natural-language date parsing.
- Duration multiplication or division.
- Custom locale management.
- Serialization helpers.
- A custom `__str__()` or `__repr__()` representation.

The current `__str__()` and `__repr__()` methods are placeholders and return:

```text
not implemented
```

and:

```text
<not implemented>
```

respectively.

These are implementation placeholders rather than formatted representations of the underlying date.

---

## 22. License

Timerithm is distributed according to the license included with the project.

See the project's license file for the applicable terms.

---

## 23. Final Example

A compact Timerithm program can therefore look like this:

```python
from timerithm import Time, months, days

date = Time.at(2026, 1, 31)

future = date + months(1) + days(7)

print(future.format("C"))
```

Output:

```text
Saturday, March 7 2026 00:00:00
```

A small interface for doing the things calendars have spent centuries making unnecessarily complicated.
