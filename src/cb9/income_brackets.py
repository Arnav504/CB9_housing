"""Household counts by income bracket, and how they sit against a dollar limit.

ACS table B19001 counts households. A three-person income limit that falls
inside a bracket is not split, and the resulting share is not an eligibility rate.
"""

from __future__ import annotations

import pandas as pd

from cb9.paths import RETRIEVED

BRACKETS: list[tuple[str, str, int, int | None]] = [
    ("B19001_E002", "Less than $10,000", 0, 9999),
    ("B19001_E003", "$10,000 to $14,999", 10000, 14999),
    ("B19001_E004", "$15,000 to $19,999", 15000, 19999),
    ("B19001_E005", "$20,000 to $24,999", 20000, 24999),
    ("B19001_E006", "$25,000 to $29,999", 25000, 29999),
    ("B19001_E007", "$30,000 to $34,999", 30000, 34999),
    ("B19001_E008", "$35,000 to $39,999", 35000, 39999),
    ("B19001_E009", "$40,000 to $44,999", 40000, 44999),
    ("B19001_E010", "$45,000 to $49,999", 45000, 49999),
    ("B19001_E011", "$50,000 to $59,999", 50000, 59999),
    ("B19001_E012", "$60,000 to $74,999", 60000, 74999),
    ("B19001_E013", "$75,000 to $99,999", 75000, 99999),
    ("B19001_E014", "$100,000 to $124,999", 100000, 124999),
    ("B19001_E015", "$125,000 to $149,999", 125000, 149999),
    ("B19001_E016", "$150,000 to $199,999", 150000, 199999),
    ("B19001_E017", "$200,000 or more", 200000, None),
]
TOTAL = "B19001_E001"


def brackets() -> pd.DataFrame:
    frame = pd.read_csv(RETRIEVED / "acs_2023_b19001.csv", dtype=str)
    frame["tract_label"] = frame["tract_label"].str.strip()
    for column in [TOTAL, *[item[0] for item in BRACKETS]]:
        frame[column] = frame[column].map(_count)
    return frame.sort_values("tract_label", key=lambda series: series.map(_tract_sort)).reset_index(drop=True)


def bracket_span(limit: int) -> tuple[list[str], str]:
    """Columns entirely below the limit, and the one column that contains it."""
    below: list[str] = []
    containing = ""
    for column, _label, low, high in BRACKETS:
        if high is not None and high < limit:
            below.append(column)
        elif low <= limit and (high is None or limit <= high):
            containing = column
    if not below or not containing:
        raise ValueError(f"No B19001 span for {limit}")
    return below, containing


def district_brackets() -> pd.DataFrame:
    frame = brackets()
    _require_complete(frame)
    rows = []
    for column, label, low, high in BRACKETS:
        rows.append({"column": column, "label": label, "low": low, "high": high, "households": int(frame[column].sum())})
    return pd.DataFrame(rows)


def limit_ranges(limits: pd.DataFrame) -> pd.DataFrame:
    frame = brackets()
    _require_complete(frame)
    total = int(frame[TOTAL].sum())
    rows = []
    for record in limits.sort_values("ami_pct").itertuples(index=False):
        below, containing = bracket_span(int(record.income_limit))
        lower = int(frame[below].sum().sum())
        upper = lower + int(frame[containing].sum())
        rows.append(
            {
                "ami_pct": int(record.ami_pct),
                "income_limit": int(record.income_limit),
                "households_below": lower,
                "share_below": lower / total * 100,
                "households_through": upper,
                "share_through": upper / total * 100,
                "households": total,
                "containing_column": containing,
            }
        )
    return pd.DataFrame(rows)


def tract_ranges(limit: int) -> pd.DataFrame:
    frame = brackets()
    _require_complete(frame)
    below, containing = bracket_span(limit)
    lower = frame[below].sum(axis=1)
    upper = lower + frame[containing]
    out = pd.DataFrame(
        {
            "tract_label": frame["tract_label"],
            "households": frame[TOTAL].astype(int),
            "households_below": lower.astype(int),
            "share_below": lower / frame[TOTAL] * 100,
            "households_through": upper.astype(int),
            "share_through": upper / frame[TOTAL] * 100,
        }
    )
    return out.reset_index(drop=True)


def assert_brackets() -> None:
    frame = brackets()
    if len(frame) != 20:
        raise AssertionError(f"Expected 20 B19001 tracts, found {len(frame)}")
    _require_complete(frame)
    detail = [item[0] for item in BRACKETS]
    mismatch = frame[frame[detail].sum(axis=1) != frame[TOTAL]]
    if not mismatch.empty:
        raise AssertionError(f"Bracket counts do not add up for {mismatch['tract_label'].tolist()}")
    below, containing = bracket_span(43750)
    if containing != "B19001_E009" or below[-1] != "B19001_E008":
        raise AssertionError("The $43,750 limit should fall in the $40,000 to $44,999 bracket")


def _require_complete(frame: pd.DataFrame) -> None:
    columns = [TOTAL, *[item[0] for item in BRACKETS]]
    if frame[columns].isna().any().any():
        raise AssertionError("A household bracket is blank")


def _count(value: object) -> int:
    text = "" if value is None else str(value).strip()
    if text in {"", "nan", "None"}:
        return pd.NA
    return int(text)


def _tract_sort(value: str) -> tuple[int, int]:
    text = str(value)
    if "." in text:
        base, suffix = text.split(".", 1)
        return int(base), int(suffix)
    return int(text), 0
