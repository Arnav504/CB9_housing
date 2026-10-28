"""Markdown for the resolved tract, project, and request tables."""

from __future__ import annotations

import pandas as pd

from cb9.formatutil import dollars, md_table, number, percent
from cb9.resolve import ami_limits, omitted_projects, project_totals, projects, requests, tract_crosswalk, tracts


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
    rows = []
    for record in projects().itertuples(index=False):
        total = f"about {number(float(record.total_units))}" if record.total_is_approximate else number(float(record.total_units))
        affordable = "" if _blank(record.affordable_units) else number(float(record.affordable_units))
        counted = "Yes" if record.include_in_total else "No"
        rows.append(
            [
                record.display_name,
                record.address,
                "—" if _blank(record.tract_label) else record.tract_label,
                record.status,
                str(record.record_date),
                total,
                affordable,
                counted,
            ]
        )
    omitted = [
        [record.printed_project, record.reason]
        for record in omitted_projects().itertuples(index=False)
    ]
    intro = (
        f"The unit total uses the two HPD buildings only: {number(totals['total_units'])} total units "
        f"and {number(totals['affordable_units'])} counted affordable units. "
        "1727 Amsterdam stays out of that sum because its unit count is approximate and its affordable split is not recorded here.\n\n"
    )
    return (
        intro
        + md_table(
            ["Project", "Address", "Tract", "Status", "Record date", "Total units", "Counted affordable", "In the total"],
            rows,
        )
        + "\nPrinted projects left out of the total:\n\n"
        + md_table(["Printed project", "Reason"], omitted)
    )


def requests_md() -> str:
    rows = [
        [str(int(record.year)), record.complaint_type, number(int(record.requests))]
        for record in requests().itertuples(index=False)
    ]
    return md_table(["Year", "311 complaint type", "Requests in CB9"], rows)


def _blank(value: object) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return True
    return str(value).strip() in {"", "nan", "None"}
