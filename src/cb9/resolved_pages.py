"""Markdown for the resolved tract, project, and request tables."""

from __future__ import annotations

import pandas as pd

from cb9.formatutil import dollars, md_table, number, percent
from cb9.income_brackets import BRACKETS, limit_ranges, tract_ranges
from cb9.resolve import ami_limits, omitted_projects, project_totals, projects, requests, tract_crosswalk, tracts
from cb9.services import sites, supportive_sites, tract_site_counts


def tracts_md() -> str:
    rows = []
    for record in tracts().itertuples(index=False):
        income = "Suppressed" if _blank(record.median_income) else dollars(float(record.median_income))
        moe = "" if _blank(record.median_income_moe) else dollars(float(record.median_income_moe))
        poverty = "" if _blank(record.poverty_rate_pct) else percent(float(record.poverty_rate_pct), 1)
        rent = "" if _blank(record.median_rent) else dollars(float(record.median_rent))
        rows.append(
            [
                record.tract_label,
                record.nta_name,
                income,
                moe,
                poverty,
                number(float(record.population)),
                rent,
            ]
        )
    return md_table(
        ["Tract", "Neighborhood tabulation area", "Median income", "Margin of error", "Poverty rate", "Population", "Median rent"],
        rows,
    )


def crosswalk_md() -> str:
    rows = [
        [record.report_id, record.where_printed, record.census_2020_id or "—", record.relationship]
        for record in tract_crosswalk().itertuples(index=False)
    ]
    return md_table(["Printed id", "Where the PDF uses it", "2020 tract", "Relationship"], rows)


def ami_md() -> str:
    rows = [
        [f"{int(record.ami_pct)}% of AMI", dollars(int(record.income_limit))]
        for record in ami_limits().itertuples(index=False)
    ]
    return md_table(["Limit for a family of 3, 2025", "Income"], rows)


def projects_md() -> str:
    totals = project_totals()
    register = projects()
    rows = []
    notes = []
    for record in register.itertuples(index=False):
        total = f"about {number(float(record.total_units))}" if record.total_is_approximate else number(float(record.total_units))
        affordable = "" if _blank(record.affordable_units) else number(float(record.affordable_units))
        counted = "Yes" if record.include_in_total else "No"
        rows.append(
            [
                record.display_name,
                _kind_label(record.kind),
                record.address,
                "—" if _blank(record.tract_label) else record.tract_label,
                record.status,
                str(record.record_date),
                total,
                affordable,
                counted,
            ]
        )
        if record.kind == "existing" and not _blank(record.notes):
            notes.append(f"**{record.display_name}.** {record.notes}")
    omitted = [
        [record.printed_project, record.reason]
        for record in omitted_projects().itertuples(index=False)
    ]
    intro = (
        f"The production total uses the two HPD buildings only: {number(totals['total_units'])} total units "
        f"and {number(totals['affordable_units'])} counted affordable units. "
        "1727 Amsterdam stays out of that sum because its unit count is approximate and its affordable split is not recorded here. "
        "General Grant Houses and Morningside Gardens are existing buildings with their own source counts. They are listed and kept out of the production total.\n\n"
    )
    return (
        intro
        + md_table(
            ["Project", "Kind", "Address", "Tract", "Status", "Record date", "Total units", "Counted affordable", "In the production total"],
            rows,
        )
        + "\n"
        + "\n\n".join(notes)
        + "\n\nNamed projects that still have no MN09 unit count:\n\n"
        + md_table(["Project", "Reason"], omitted)
    )


def income_md() -> str:
    ranges = limit_ranges(ami_limits())
    labels = {column: label for column, label, _low, _high in BRACKETS}
    deep = ranges[ranges["ami_pct"].eq(30)].iloc[0]
    rows = [
        [
            f"{int(record.ami_pct)}% of AMI",
            dollars(int(record.income_limit)),
            number(int(record.households_below)),
            percent(float(record.share_below), 1),
            number(int(record.households_through)),
            percent(float(record.share_through), 1),
            labels[record.containing_column],
        ]
        for record in ranges.itertuples(index=False)
    ]
    tract_rows = []
    for record in tract_ranges(int(deep.income_limit)).itertuples(index=False):
        households = int(record.households)
        tract_rows.append(
            [
                record.tract_label,
                number(households),
                number(int(record.households_below)),
                "—" if households == 0 else percent(float(record.share_below), 1),
                number(int(record.households_through)),
                "—" if households == 0 else percent(float(record.share_through), 1),
            ]
        )
    intro = (
        f"The 20 tracts contain {number(int(deep.households))} households in ACS table B19001, the 2023 five-year household income brackets. "
        "A three-person limit that falls inside a bracket is not split. "
        "The lower count is households in brackets that end below the limit. "
        "The upper count also includes every household in the bracket that contains the limit. "
        "Neither figure is the share of residents who qualify. "
        "This table does not split households by size, so it cannot say who would pass an eligibility test.\n\n"
    )
    return (
        intro
        + md_table(
            [
                "Three-person limit",
                "Dollar line",
                "Households below the bracket",
                "Share",
                "Households through the containing bracket",
                "Share",
                "Bracket that contains the line",
            ],
            rows,
        )
        + f"\nThe next table uses the 30 percent line, {dollars(int(deep.income_limit))} for a family of three, in each tract. "
        + _empty_household_note(tract_rows)
        + "\n\n"
        + md_table(
            [
                "Tract",
                "Households",
                f"Brackets ending below {dollars(int(deep.income_limit))}",
                "Share",
                "Through the containing bracket",
                "Share",
            ],
            tract_rows,
        )
    )


def services_md() -> str:
    counts = tract_site_counts(tracts())
    inventory = sites()
    mental = int(counts["mental_health_sites"].sum())
    food = int(counts["food_sites"].sum())
    supportive = int(counts["supportive_sites"].sum())
    people = int(counts["population"].sum())
    mental_rate = mental / people * 1000
    food_rate = food / people * 1000
    rows = [
        [
            record.tract_label,
            number(int(record.mental_health_sites)),
            number(int(record.food_sites)),
            number(int(record.supportive_sites)),
            number(int(record.population)),
            number(float(record.mental_health_per_1000), 2),
            number(float(record.food_per_1000), 2),
        ]
        for record in counts.itertuples(index=False)
    ]
    supportive_rows = [
        [_name(record.operator), record.address.title(), record.tract_label, record.facility_types, "—"]
        for record in supportive_sites().itertuples(index=False)
    ]
    split_notes = []
    seen = set()
    for record in inventory.itertuples(index=False):
        tracts_named = [part for part in str(record.tracts_in_source).split(", ") if part]
        if len(tracts_named) < 2 or record.address_key in seen:
            continue
        seen.add(record.address_key)
        others = ", ".join(part for part in tracts_named if part != record.tract_label)
        split_notes.append(
            f"{record.address.title()} is also coded to tract {others}; it is counted once, in tract {record.tract_label}."
        )
    intro = (
        f"After addresses for the same building are combined, community district 109 has {mental} mental-health sites "
        f"and {food} food sites. The file also lists {supportive} supportive-housing sites. "
        "Capacity is 0 on every counted row, so those supportive-housing rows stay sites and are not turned into units. "
        f"The district rates divide {mental} and {food} sites by the district population of {number(people)}: "
        f"{number(mental_rate, 2)} mental-health sites and {number(food_rate, 2)} food sites per 1,000 residents. "
        "Those are pooled rates, total sites divided by total population, not an average of the tract rates. "
        "Summer-only feeding sites, the other feeding site, and rows labeled only as housing support are in the download and are not counted.\n\n"
    )
    split = (" ".join(split_notes) + "\n\n") if split_notes else ""
    return (
        intro
        + split
        + md_table(
            ["Tract", "Mental-health sites", "Food sites", "Supportive-housing sites", "Population", "Mental-health sites per 1,000", "Food sites per 1,000"],
            rows,
        )
        + "\nSupportive-housing sites. The units column is blank because the file does not contain a unit count:\n\n"
        + md_table(["Operator", "Address", "Tract", "Facility type", "Units"], supportive_rows)
    )


def requests_md() -> str:
    rows = [
        [str(int(record.year)), record.complaint_type, number(int(record.requests))]
        for record in requests().itertuples(index=False)
    ]
    return md_table(["Year", "311 complaint type", "Requests in CB9"], rows)


def _empty_household_note(rows: list[list[str]]) -> str:
    empty = [row[0] for row in rows if row[1] == "0"]
    if not empty:
        return ""
    names = ", ".join(f"tract {label}" for label in empty)
    verb = "has" if len(empty) == 1 else "have"
    return f"{names[:1].upper() + names[1:]} {verb} no households in this table, so there is no share."


def _name(value: object) -> str:
    text = str(value).strip()
    return text.title() if text.isupper() else text


def _kind_label(kind: object) -> str:
    labels = {
        "production": "HPD production",
        "proposal": "Proposal",
        "existing": "Existing building",
    }
    return labels.get(str(kind), str(kind))


def _blank(value: object) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return True
    return str(value).strip() in {"", "nan", "None"}
