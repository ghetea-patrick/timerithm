# Timerithm

**Readable durations. Sensible month shifts. February still gets special treatment.**

Timerithm is a lightweight Python utility for dates, times, durations, and calendar-aware arithmetic. It builds on Python's standard `datetime` and `timedelta` functionality, adding readable duration helpers, a `Time` wrapper, and custom formatting tokens.

You can write `hours(3)` instead of `timedelta(hours=3)`, move a date forward by a calendar month, and inspect the result without repeating `datetime.timedelta(...)` boilerplate. The calendar remains complicated; your code can at least be polite about it.

[What it does](#what-it-does) · [Get started](#get-started) · [A quick example](#a-quick-example) · [How it fits together](#how-it-fits-together) · [Reference](#reference) · [Examples](#examples) · [Good to know](#good-to-know) · [Design notes](#design-notes) · [License](#license)

## What it does

- Creates fixed durations in microseconds, milliseconds, seconds, minutes, hours, days, and weeks.
- Adds or subtracts calendar months and years with `months()` and `years()`.
- Corrects the day automatically when the destination month is shorter, including leap-year handling.
- Creates explicit dates with `Time.at()` and the current local date and time with `Time.now()`.
- Supports equality and chronological comparisons, including comparisons with Python `datetime` objects.
- Exposes individual date and time components through read-only properties.
- Makes `Time` values usable in sets and dictionary keys through datetime-based hashing.
- Formats dates using preset layouts, readable tokens, fractional seconds, weekday and month names, and 12-hour or 24-hour clocks.

## Get started

> [!NOTE]
> Timerithm uses only Python's standard library and works with standard `datetime` objects and `timedelta` values. Replace `timerithm` with your installation's module path if needed.

Import the class and whichever duration helpers you need:

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

The main date/time interface is `Time`. Each instance wraps a Python `datetime`, which supplies the underlying values for arithmetic, comparison, component access, and formatting.

## A quick example

Move from January 31 to the end of February, add seven days, and format the result:

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

The month shift lands on February 28, 2026, because February has no 31st. Adding seven days then reaches March 7.

> [!IMPORTANT]
> Use **`.format(layout)`** for readable date output. The current `__str__()` and `__repr__()` methods are placeholders, so printing a `Time` object directly does not display its underlying date.

## How it fits together

### Wrap a datetime value

The `Time(date)` constructor takes the underlying datetime value. Most examples use the convenience constructors, such as:

```python
date = Time.at(2026, 10, 1)
```

The wrapped datetime remains stored internally, rather than requiring Timerithm to implement another date and time system from scratch.

### Get the current local time

Use `Time.now()` to capture the current local date and time:

```python
current = Time.now()
```

Internally, it uses:

```python
datetime.now()
```

The result includes the year, month, day, hour, minute, second, and microsecond. Timerithm does not add timezone management to this constructor.

### Construct an explicit date and time

For a date at midnight:

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

The time components default to zero. Supply them when you need a particular clock time or microsecond value:

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

This represents:

```text
2026-10-01 14:30:45.123456
```

Python's `datetime` constructor handles validation. Invalid dates therefore raise the same exceptions as the underlying datetime constructor.

### Use fixed durations for fixed amounts of time

The helpers from `microseconds()` through `weeks()` return ordinary `timedelta` values and accept an integer amount:

```python
seconds(30)
minutes(5)
hours(2)
days(7)
weeks(3)
```

Use those values directly with a `Time` instance:

```python
now = Time.now()

later = now + hours(2)
earlier = now - days(3)
```

The first operation moves two hours forward; the second moves three days backward. Fixed-duration arithmetic follows Python's `timedelta` behavior.

### Use calendar durations for months and years

Months and years have separate duration types because they do not have a fixed number of days.

Create a three-month calendar duration:

```python
months(3)
```

Add it to a date:

```python
date = Time.at(2026, 1, 15)

result = date + months(3)
```

Resulting date:

```text
2026-04-15
```

Create a two-year calendar duration:

```python
years(2)
```

Add it in the same way:

```python
date = Time.at(2026, 1, 15)

result = date + years(2)
```

Resulting date:

```text
2028-01-15
```

Internally, calendar durations are represented by `_Months` and `_Years`. These are implementation details; use `months()` and `years()` rather than instantiating those classes directly. Year arithmetic is implemented as twelve-month shifts.

> [!TIP]
> Choose `days(n)` for a fixed day count and `months(n)` for a calendar-month shift. Timerithm keeps those concepts separate instead of pretending every month has the same length.

### Add and subtract without modifying the original

Fixed durations work with `+`:

```python
date = Time.at(2026, 10, 1)

date + seconds(30)
date + minutes(15)
date + hours(2)
date + days(7)
```

Each operation returns a new `Time`; it does not modify the original. For example:

```python
date = Time.at(2026, 10, 1)

future = date + days(5)
```

The underlying dates are:

```text
date = 2026-10-01
future = 2026-10-06
```

Fixed durations also work with `-`:

```python
date = Time.at(2026, 10, 10)

previous = date - days(5)
```

Resulting date:

```text
2026-10-05
```

Both directions delegate the fixed-duration calculation to Python's datetime/timedelta behavior.

### Shift months across the calendar

Adding two months keeps the day when the destination supports it:

```python
date = Time.at(2026, 1, 15)

result = date + months(2)
```

Result:

```text
2026-03-15
```

Month shifts also cross year boundaries:

```python
date = Time.at(2026, 11, 15)

result = date + months(3)
```

Result:

```text
2027-02-15
```

Subtract months with the same operator pattern:

```python
date = Time.at(2026, 5, 15)

result = date - months(2)
```

Result:

```text
2026-03-15
```

### Let shorter months correct the day

When a destination month does not contain the original day, Timerithm selects that month's last valid day:

```python
date = Time.at(2026, 1, 31)

result = date + months(1)
```

Result:

```text
2026-02-28
```

Leap years are handled through Python's `calendar.monthrange()`:

```python
date = Time.at(2024, 1, 31)

result = date + months(1)
```

Result:

```text
2024-02-29
```

The time components are preserved during the shift:

```python
date = Time.at(2026, 1, 31, 14, 30, 45)

result = date + months(1)
```

Result:

```text
2026-02-28 14:30:45
```

The calendar may adjust the day. It does not get to rearrange the clock as well.

### Shift years using twelve-month arithmetic

Add years:

```python
date = Time.at(2026, 10, 1)

result = date + years(2)
```

Result:

```text
2028-10-01
```

Subtract years:

```python
date = Time.at(2028, 10, 1)

result = date - years(2)
```

Result:

```text
2026-10-01
```

Year calculations use the same month-end correction implemented by `_shift_months()`. That includes moving away from February 29:

```python
date = Time.at(2024, 2, 29)

result = date + years(1)
```

The destination year is not a leap year, so the result is:

```text
2025-02-28
```

## Reference

### Fixed-duration constructors

All seven helpers below take an integer amount and return a standard Python `timedelta`:

| Function | Description | Underlying Type |
|---|---|---|
| `microseconds(n)` | Create a duration measured in microseconds. | `timedelta` |
| `milliseconds(n)` | Create a duration measured in milliseconds. | `timedelta` |
| `seconds(n)` | Create a duration measured in seconds. | `timedelta` |
| `minutes(n)` | Create a duration measured in minutes. | `timedelta` |
| `hours(n)` | Create a duration measured in hours. | `timedelta` |
| `days(n)` | Create a duration measured in days. | `timedelta` |
| `weeks(n)` | Create a duration measured in weeks. | `timedelta` |

### Calendar-duration constructors

| Helper | Meaning | Internal representation |
| --- | --- | --- |
| `months(n)` | Shift by `n` calendar months. | `_Months` |
| `years(n)` | Shift by `n` calendar years, implemented through twelve-month arithmetic. | `_Years` |

Add or subtract these from `Time` values with `+` and `-`. They are distinct from the fixed-duration `timedelta` helpers.

### Comparisons

`Time` supports equality and chronological ordering:

| Operator | Description |
|---|---|
| `==` | Equal timestamps |
| `!=` | Different timestamps |
| `<` | Earlier than |
| `<=` | Earlier than or equal to |
| `>` | Later than |
| `>=` | Later than or equal to |

For example:

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

The class uses `@total_ordering` to derive the full ordering interface from `__eq__()` and `__lt__()`.

You can also compare a `Time` directly with a Python `datetime`:

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

Comparisons use the underlying `_date` value. For unsupported comparison types, the methods return `NotImplemented`, allowing Python to apply its normal comparison rules.

### Hashing

`Time.__hash__()` uses the wrapped datetime, so you can store instances in sets or use them as dictionary keys:

```python
date = Time.at(2026, 1, 1)

dates = {date}

print(date in dates)
```

Output:

```text
True
```

Two `Time` values wrapping the same datetime have equivalent hash behavior. Time can now be a dictionary key; presumably it has always wanted more responsibilities.

### Read-only date and time components

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

For a value with every component specified:

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

The `millisecond` property is derived from the microsecond value with integer division:

```python
self._date.microsecond // 1000
```

So this value:

```text
123456 microseconds
```

becomes:

```text
123 milliseconds
```

The remaining fractional precision is discarded; the property does not round it.

### Formatting interface

Call:

```python
date.format(layout)
```

The formatter accepts preset layouts and custom tokens. It supports fractional seconds, weekday and month names, 12-hour and 24-hour clocks, and uppercase or lowercase AM/PM.

For example:

```python
date = Time.at(2026, 10, 1, 14, 30, 45)

print(date.format("T"))
```

Output:

```text
2026-10-01 14:30:45
```

### Preset layouts

Each preset expands to the layout shown below before the final `strftime()` operation:

| Preset | Expansion | Example |
|---|---|---|
| `S` | `BBBB D, YYYY hh:mm` | October 1, 2026 14:30 |
| `E` | `D BBBB, YYYY hh:mm` | 1 October, 2026 14:30 |
| `L` | `YYYYMMDDhhmmss` | 20261001143045 |
| `T` | `YYYY-MM-DD hh:mm:ss` | 2026-10-01 14:30:45 |
| `C` | `AAAA, BBBB D YYYY hh:mm:ss` | Thursday, October 1 2026 14:30:45 |

Use the one-character preset as the entire layout:

```python
date = Time.at(2026, 10, 1, 14, 30, 45)

print(date.format("S"))
print(date.format("E"))
print(date.format("L"))
print(date.format("T"))
print(date.format("C"))
```

The table shows the resulting strings for the sample date of October 1, 2026, at 14:30:45.

### Formatting tokens

Timerithm converts these readable tokens into Python `strftime` directives:

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

For a weekday and month name:

```python
date = Time.at(2026, 10, 1, 14, 30, 45)

print(date.format("AAAA, BBBB D YYYY"))
```

Example output:

```text
Thursday, October 1 2026
```

For a 12-hour clock and lowercase AM/PM:

```python
print(date.format("ii:mm p"))
```

Output:

```text
02:30 pm
```

### Padded and unpadded dates

`D` is the numerical day without zero-padding; `M` is the numerical month without zero-padding. They receive special handling separately from the padded `DD` and `MM` tokens.

```python
date = Time.at(2026, 3, 5)

print(date.format("M/D/YYYY"))
```

Output:

```text
3/5/2026
```

Using the padded tokens instead:

```python
date.format("MM/DD/YYYY")
```

produces:

```text
03/05/2026
```

Choose the form that matches the representation you need.

### Fractional seconds

Repeat lowercase `f` to select how many digits of the microsecond component to include. Using this date:

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

One `f`:

```python
date.format("hh:mm:ss.f")
```

Output:

```text
14:30:45.1
```

Three `f` characters:

```python
date.format("hh:mm:ss.fff")
```

Output:

```text
14:30:45.123
```

Six `f` characters:

```python
date.format("hh:mm:ss.ffffff")
```

Output:

```text
14:30:45.123456
```

> [!IMPORTANT]
> Fractional-second formatting **truncates** the microsecond string to the requested digit count. The maximum meaningful precision is six digits because Python's `datetime` stores microseconds.

The uppercase `F` token in the token table represents microseconds; repeated lowercase `f` characters let you choose the displayed fractional precision.

### AM/PM case

For standard uppercase `AM` or `PM`, use:

```text
P
```

For lowercase `am` or `pm`, use:

```text
p
```

For example:

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

The lowercase form is implemented by replacing `AM` and `PM` after `strftime()` formats the value.

### API at a glance

#### Duration Functions

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

#### `Time` Class

```python
Time(date)
```

#### Class Methods

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

#### Arithmetic

```python
time + timedelta
time - timedelta

time + months(n)
time - months(n)

time + years(n)
time - years(n)
```

#### Comparison

```python
time == other
time != other
time < other
time <= other
time > other
time >= other
```

#### Properties

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

#### Formatting

```python
time.format(layout)
```

## Examples

### Work from construction through formatting

This combines fixed durations, calendar durations, comparisons, component access, formatting, and automatic leap-year handling:

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

Expected output:

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

The starting date is January 31, 2024. The five-hour shift keeps the same calendar date, the month shift adjusts to February 29, and the year shift reaches January 31, 2025. `next_week` also demonstrates adding seven fixed days, even though it is not printed.

The full workflow is: construct a value, calculate new values with duration helpers, compare or inspect the results, and use `.format()` when you want text output.

## Good to know

Timerithm remains a small wrapper around Python's date and time facilities. The current implementation does not provide:

- Timezone management.
- Timezone conversion.
- Daylight-saving-time utilities.
- Relative date parsing.
- Natural-language date parsing.
- Duration multiplication or division.
- Custom locale management.
- Serialization helpers.
- Custom date representations through `__str__()` or `__repr__()`.

> [!WARNING]
> `__str__()` and `__repr__()` are implementation placeholders. They do not expose a formatted date. Use `.format(layout)` for that.

`__str__()` currently returns:

```text
not implemented
```

`__repr__()` currently returns:

```text
<not implemented>
```

Dates and timestamps shown as results throughout this README describe the underlying values, or the explicitly formatted output. They are not promises about `print(time)` producing a date string.

## Design notes

Timerithm builds on `datetime` rather than replacing it. The `Time` class keeps the wrapped value internally and supplies simple construction, operator-based arithmetic, direct comparisons, component properties, and custom formatting.

Fixed and calendar durations have separate jobs: `timedelta` handles microseconds through weeks, `_Months` handles calendar-month shifts, and `_Years` expresses years through twelve-month shifts. This separation makes month-end behavior explicit instead of assuming every month contains the same number of days.

The implementation stays compact and relies on Python's standard library. The goal is to make everyday time calculations easier to express. Time has already caused enough trouble without requiring another independent date system.
