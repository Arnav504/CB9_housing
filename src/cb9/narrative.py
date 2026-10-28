"""Markdown fragments computed from the published tables and, when present, snapshots."""

from __future__ import annotations

import json

import pandas as pd

from cb9.affordability import affordability_gap, income_ratio, share_of_threshold, times_as_dense
from cb9.formatutil import dollars, md_table, number, percent
from cb9.inventory import summarize_projects
from cb9.load import (
    accessibility,
    aggregates,
    benchmarks,
    district_rates,
    income_distribution,
    income_pairs,
    income_statements,
    projects,
    requests_311,
    requests_311_tracts,
    service_matrix,
    ssi_policy,
    tract_guide,
)
from cb9.match import acs_tract_label, hpd_tract_label, match_projects
from cb9.paths import RETRIEVED
from cb9.ssi import appendix_ssi, band_for, main_ssi, weighted_terms


def guide_group(neighborhood: str) -> str:
    text = neighborhood.lower()
    if text.startswith("morningside"):
        return "Morningside Heights"
    if text.startswith("manhattanville"):
        return "Manhattanville"
    if text.startswith("hamilton"):
        return "Hamilton Heights"
    return "Other"


def tract_guide_md() -> str:
    guide = tract_guide().copy()
    guide["group"] = guide["neighborhood_as_printed"].map(guide_group)
    sections = []
    for group in ["Morningside Heights", "Manhattanville", "Hamilton Heights"]:
        rows = []
        for record in guide[guide["group"].eq(group)].itertuples(index=False):
            rows.append(
                [
                    record.tract_id,
                    record.neighborhood_as_printed,
                    dollars(record.median_income),
                    number(record.population),
                    percent(record.poverty_rate_pct, 1),
                    percent(record.homeownership_pct, 1),
                    dollars(record.median_rent),
                    str(record.printed_page),
                ]
            )
        sections.append(
            f"### {group}\n\n"
            + md_table(
                ["Tract", "Neighborhood as printed", "Median income", "Population", "Poverty", "Homeownership", "Median rent", "Page"],
                rows,
            )
        )
    role_rows = [
        [record.tract_id, record.role, str(record.printed_page)]
        for record in guide.itertuples(index=False)
    ]
    sections.append("### Role assigned in the guide\n\n" + md_table(["Tract", "Role as printed", "Page"], role_rows))
    return "\n".join(sections)


def gap_md() -> str:
    values = benchmarks()
    gap = affordability_gap(values["ami_100_hh3"], values["cb9_median_gap"])
    lines = [
        "The report subtracts the CB9 median from the family-of-three 100 percent AMI limit.",
        "",
        md_table(
            ["Step", "Value"],
            [
                ["100% AMI, family of 3", dollars(values["ami_100_hh3"])],
                ["CB9 median used in the gap", dollars(values["cb9_median_gap"])],
                ["Difference", dollars(gap["gap_dollars"])],
                ["Difference as a percent of the median", percent(gap["gap_percent_of_median"], 1)],
                ["Printed dollar gap", dollars(values["gap_dollars_printed"])],
                ["Printed percent gap", percent(values["gap_percent_printed"], 1)],
            ],
        ),
        "",
        (
            f"The difference is {dollars(gap['gap_dollars'])}. "
            f"Divided by the median, that is {percent(gap['gap_percent_of_median'], 1)}, "
            f"which rounds to the printed {percent(values['gap_percent_printed'], 1)}."
        ),
        "",
        (
            "The two inputs are a regional income limit for a three-person household and a district median "
            "that is not restricted to three-person households. The report treats the difference as the "
            "affordability gap."
        ),
    ]
    return "\n".join(lines) + "\n"


def distribution_md() -> str:
    rows = []
    for record in income_distribution().itertuples(index=False):
        relation = "Under" if record.relation == "under" else "Over"
        rows.append([relation, dollars(record.ceiling_dollars), percent(record.share_pct, 1), str(record.printed_page)])
    return md_table(["Relation", "Income", "Share of CB9 households", "Page"], rows)


def access_md() -> str:
    frame = accessibility()
    blocks = []
    for area, group in frame.groupby("area", sort=False):
        rows = [
            [f"{int(record.ami_pct)}% AMI", dollars(record.income_required), record.access_text, str(record.printed_page)]
            for record in group.itertuples(index=False)
        ]
        blocks.append(f"### {area}\n\n" + md_table(["Threshold", "Annual income, family of 3", "Printed share", "Page"], rows))
    return "\n".join(blocks)


def _project_rows(frame: pd.DataFrame) -> list[list[str]]:
    rows = []
    for record in frame.itertuples(index=False):
        tract = "" if pd.isna(record.tract) else str(record.tract)
        status = "" if pd.isna(record.status) else str(record.status)
        label = "" if pd.isna(record.report_label) else str(record.report_label)
        rows.append(
            [
                record.project_name,
                "" if pd.isna(record.address) else str(record.address),
                number(record.total_units),
                number(record.affordable_units),
                str(record.ami_range),
                tract,
                status,
                label,
                str(record.printed_page),
            ]
        )
    return rows


def projects_md(inventory: str, heading: str) -> str:
    frame = projects()
    frame = frame[frame["inventory"].eq(inventory)]
    summary = summarize_projects(frame)
    table = md_table(
        ["Project", "Address", "Total", "Affordable", "AMI range", "Tract", "Status", "Report label", "Page"],
        _project_rows(frame),
    )
    totals = (
        f"Sum of these rows: {number(summary['rows'], 0)} projects, "
        f"{number(summary['total_units'])} total units, "
        f"{number(summary['affordable_units'])} affordable units, "
        f"{number(summary['remaining_units'])} units above the printed affordable count."
    )
    return f"### {heading}\n\n{table}\n{totals}\n"


def inventory_checks_md() -> str:
    frame = projects()
    published = aggregates().set_index("aggregate_id")
    five = summarize_projects(frame[frame["inventory"].eq("five_project")])
    expanded = summarize_projects(frame[frame["inventory"].eq("expanded")])
    completed = summarize_projects(frame[frame["inventory"].eq("expanded") & frame["status"].eq("Complete")])
    active = summarize_projects(frame[frame["inventory"].eq("expanded") & frame["status"].ne("Complete")])
    headline = published.loc["expanded_pipeline"]
    five_pub = published.loc["five_project"]
    deep = float(headline["deep_units"])
    workforce = float(headline["workforce_units"])
    market = float(headline["market_units"])
    supportive = float(headline["supportive_units"])
    require = float(headline["require_60_plus"])
    affordable = float(headline["affordable_units"])
    total = float(headline["total_units"])
    rows = [
        ["Five printed projects", number(five["total_units"]), number(five["affordable_units"]), number(five_pub["total_units"]), number(five_pub["affordable_units"])],
        ["Nine printed rows", number(expanded["total_units"]), number(expanded["affordable_units"]), number(total), number(affordable)],
        ["Completed rows inside the nine", number(completed["total_units"]), number(completed["affordable_units"]), "—", "—"],
        ["Other rows inside the nine", number(active["total_units"]), number(active["affordable_units"]), "—", "—"],
    ]
    identity = md_table(
        ["Published piece", "Value", "Check"],
        [
            ["Deep + workforce", number(deep + workforce), f"Printed affordable total is {number(affordable)}"],
            ["Affordable + market", number(affordable + market), f"Printed pipeline total is {number(total)}"],
            ["Deep + workforce + market", number(deep + workforce + market), f"Printed pipeline total is {number(total)}"],
            ["Workforce + market", number(workforce + market), f"Printed count of units at 60% AMI or above is {number(require)}"],
            ["Deep + units at 60% AMI or above", number(deep + require), f"Printed pipeline total is {number(total)}"],
            ["Supportive units / affordable units", percent(supportive / affordable * 100, 1), "Printed share of affordable units is 26.0%"],
            ["Deep / pipeline total", percent(deep / total * 100, 1), "Printed share is 35.8%"],
        ],
    )
    return (
        md_table(
            ["Set", "Row-sum total", "Row-sum affordable", "Published total", "Published affordable"],
            rows,
        )
        + "\n"
        + identity
    )


def ssi_worked_example_md() -> str:
    matrix = service_matrix()
    tract = matrix[matrix["tract_id"].astype(str).eq("219")].iloc[0]
    district = matrix[matrix["is_district_average"]].iloc[0]
    terms = weighted_terms(
        tract.mh_per_1000, tract.sh_per_1000, tract.fp_per_1000,
        district.mh_per_1000, district.sh_per_1000, district.fp_per_1000,
    )
    main = main_ssi(
        tract.mh_per_1000, tract.sh_per_1000, tract.fp_per_1000,
        district.mh_per_1000, district.sh_per_1000, district.fp_per_1000,
    )
    appendix = appendix_ssi(
        tract.mh_per_1000, tract.sh_per_1000, tract.fp_per_1000,
        district.mh_per_1000, district.sh_per_1000, district.fp_per_1000,
    )
    rows = [
        ["Mental health sites", number(tract.mh_per_1000, 1), number(district.mh_per_1000, 1), number(terms["mh_ratio"], 3), "0.4", number(terms["mh_points"], 2)],
        ["Supportive housing units", number(tract.sh_per_1000, 1), number(district.sh_per_1000, 1), number(terms["sh_ratio"], 3), "0.4", number(terms["sh_points"], 2)],
        ["Food pantries", number(tract.fp_per_1000, 1), number(district.fp_per_1000, 1), number(terms["fp_ratio"], 3), "0.2", number(terms["fp_points"], 2)],
    ]
    return (
        "Tract 219 and the CB9 average, from the printed service matrix.\n\n"
        + md_table(["Component per 1,000 residents", "Tract 219", "CB9 average", "Ratio", "Weight", "Points"], rows)
        + "\n"
        + f"Main formula: {number(terms['mh_points'], 2)} + {number(terms['sh_points'], 2)} + {number(terms['fp_points'], 2)} = {number(main, 2)}.\n\n"
        + f"Appendix formula: (8.2 + 2×18.6 + 1.4) / (4.4 + 2×9.7 + 1.0) × 100 = {number(appendix, 2)}.\n\n"
        + f"The report prints {number(tract.ssi_printed, 0)} for Tract 219 and uses that score for the policy call.\n"
    )


def ssi_comparison_md() -> str:
    matrix = service_matrix()
    district = matrix[matrix["is_district_average"]].iloc[0]
    policy = ssi_policy().set_index(ssi_policy()["tract_id"].astype(str))
    rows = []
    for record in matrix[~matrix["is_district_average"]].itertuples(index=False):
        main = main_ssi(record.mh_per_1000, record.sh_per_1000, record.fp_per_1000, district.mh_per_1000, district.sh_per_1000, district.fp_per_1000)
        appendix = appendix_ssi(record.mh_per_1000, record.sh_per_1000, record.fp_per_1000, district.mh_per_1000, district.sh_per_1000, district.fp_per_1000)
        printed = float(record.ssi_printed)
        call = policy.loc[str(record.tract_id), "policy_as_printed"] if str(record.tract_id) in policy.index else ""
        rows.append(
            [
                str(record.tract_id),
                number(printed, 0),
                number(main, 2),
                band_for(main),
                number(appendix, 2),
                number(main - printed, 2),
                call,
            ]
        )
    return md_table(
        ["Tract", "Printed index", "Main formula", "Band from main formula", "Appendix formula", "Main minus printed", "Printed policy call"],
        rows,
    )


def income_conflicts_md() -> str:
    statements = income_statements().set_index("statement_id")
    rows = []
    for pair in income_pairs().itertuples(index=False):
        left = statements.loc[pair.statement_a]
        right = statements.loc[pair.statement_b]
        rows.append(
            [
                left.subject if left.subject == right.subject else f"{left.subject} / {right.subject}",
                _statement_cell(left),
                _statement_cell(right),
                pair.issue,
            ]
        )
    ratio = income_ratio(benchmarks()["tract_231_body_high"], benchmarks()["tract_219_body"])
    below = share_of_threshold(benchmarks()["tract_219_body"], benchmarks()["ami_60_hh3"])
    extra = (
        "\n\n"
        + md_table(
            ["Printed description", "Recomputed from the printed inputs"],
            [
                [
                    "Income range from $17,584 to $62,100 is a 353% variance (printed page 11)",
                    f"Ratio {number(ratio['ratio'], 2)}; percent increase from the lower figure {percent(ratio['percent_increase'], 1)}",
                ],
                [
                    "Tract 219 at $17,584 is 23% below the 60% AMI threshold (printed page 10)",
                    f"$17,584 is {percent(below, 1)} of the printed 60% AMI limit of $87,480",
                ],
            ],
        )
    )
    return md_table(["Subject", "One printed figure", "Another printed figure", "What differs"], rows) + extra


def _statement_cell(row: pd.Series) -> str:
    if "poverty" in str(row.measure):
        shown = percent(float(row.value), 1)
    else:
        shown = dollars(float(row.value))
    return f"{shown} (p. {int(row.printed_page)})"


def rate_checks_md() -> str:
    rates = district_rates().set_index("district")
    cb9 = float(rates.loc["CB9 (West Harlem)", "supportive_units_per_1000"])
    city = float(rates.loc["Citywide average", "supportive_units_per_1000"])
    cb7 = float(rates.loc["CB7 (Upper West Side)", "supportive_units_per_1000"])
    cb8 = float(rates.loc["CB8 (Upper East Side)", "supportive_units_per_1000"])
    cb8_shelter = float(rates.loc["CB8 (Upper East Side)", "shelter_beds_per_1000"])
    cb9_shelter = float(rates.loc["CB9 (West Harlem)", "shelter_beds_per_1000"])
    cb11_shelter = float(rates.loc["CB11 (East Harlem)", "shelter_beds_per_1000"])
    matrix_avg = float(service_matrix().loc[service_matrix()["is_district_average"], "sh_per_1000"].iloc[0])
    tract_219 = float(service_matrix().loc[service_matrix()["tract_id"].astype(str).eq("219"), "sh_per_1000"].iloc[0])
    rows = [
        ["CB9 supportive units / citywide", number(times_as_dense(cb9, city), 2), "Printed text says 3.5 times (p. 29)"],
        ["CB9 supportive units / CB7", number(times_as_dense(cb9, cb7), 2), "Printed text says roughly 11 times CB7 and CB8 (p. 29)"],
        ["CB9 supportive units / CB8", number(times_as_dense(cb9, cb8), 2), "Printed text also says CB8 has 53 times less supportive housing (p. 30)"],
        ["CB9 supportive units / CB8 shelter beds", number(times_as_dense(cb9, cb8_shelter), 2), "This divides a supportive-unit rate by a shelter-bed rate"],
        ["CB11 shelter beds / CB9 shelter beds", number(times_as_dense(cb11_shelter, cb9_shelter), 2), "Printed text says roughly 2.5 times (p. 29)"],
        ["District table, CB9 supportive units", number(cb9, 2), "Printed service-matrix CB9 average is " + number(matrix_avg, 1) + "; Tract 219 in that matrix is " + number(tract_219, 1)],
    ]
    return md_table(["Comparison", "Quotient of the printed rates", "Printed claim beside it"], rows)


def retrieval_md() -> str:
    parts = [census_md(), hpd_md(), requests_md()]
    manifest = RETRIEVED / "manifest.json"
    if manifest.exists():
        meta = json.loads(manifest.read_text())
        bits = [f"{key} on {value.get('retrieved_on', 'unknown date')}" for key, value in meta.items()]
        parts.insert(0, "Snapshots on disk: " + "; ".join(bits) + ".\n")
    else:
        parts.insert(0, "No retrieval snapshots are on disk yet. Run the three scripts in `pipelines/` and rebuild.\n")
    return "\n".join(parts)


def census_md() -> str:
    path = RETRIEVED / "acs_2023_tracts.csv"
    cross = RETRIEVED / "cb9_tracts.csv"
    if not path.exists() or not cross.exists():
        return "### Census\n\nThe ACS snapshot is not on disk.\n"
    acs = pd.read_csv(path, dtype=str)
    official = pd.read_csv(cross, dtype=str)
    if "tract_label" in acs.columns:
        acs["tract_id"] = acs["tract_label"].map(lambda value: str(value).strip())
    else:
        acs["tract_id"] = acs["tract"].map(acs_tract_label)
    official["tract_id"] = official["ctlabel"].astype(str)
    guide = tract_guide().copy()
    guide["tract_id"] = guide["tract_id"].astype(str)
    merged = guide.merge(
        acs[["tract_id", "median_income", "median_income_moe", "poverty_rate_pct", "population"]],
        on="tract_id",
        how="outer",
        indicator="join_status",
    )
    rows = []
    for record in merged.sort_values("tract_id", key=lambda s: s.map(_tract_sort)).itertuples(index=False):
        if record.join_status == "left_only":
            status = "In the guide only"
        elif record.join_status == "right_only":
            status = "In MN09 only"
        else:
            status = "In both"
        guide_income = "" if _blank(record.median_income_x) else dollars(float(record.median_income_x))
        if not _blank(record.median_income_y):
            acs_income = dollars(float(record.median_income_y))
        elif not _blank(getattr(record, "population_y", None)):
            acs_income = "Suppressed"
        else:
            acs_income = ""
        moe = "" if _blank(record.median_income_moe) else dollars(float(record.median_income_moe))
        rows.append([str(record.tract_id), status, guide_income, acs_income, moe])
    note = (
        f"City Planning assigns {len(official)} 2020 census tracts to Manhattan CDTA MN09. "
        "The ACS columns are 2023 5-year estimates for those tract IDs. "
        "A guide tract that uses a different ID does not join.\n\n"
    )
    return "### Census\n\n" + note + md_table(
        ["Tract", "Where it appears", "Guide median", "ACS 2023 median", "ACS margin of error"],
        rows,
    )


def hpd_md() -> str:
    path = RETRIEVED / "hpd_mn09.csv"
    if not path.exists():
        return "### Housing production\n\nThe HPD snapshot is not on disk.\n"
    hpd = pd.read_csv(path, dtype=str)
    hits = match_projects(hpd)
    printed = projects()
    printed = printed[printed["inventory"].eq("expanded")]
    rows = []
    for record in printed.itertuples(index=False):
        matched = hits[hits["matched_project_id"].eq(record.project_id)] if not hits.empty else hits
        if matched.empty:
            rows.append([record.project_name, number(record.total_units), number(record.affordable_units), "No building row matched the rule", ""])
            continue
        for hit in matched.itertuples(index=False):
            address = f"{getattr(hit, 'house_number', '')} {getattr(hit, 'street_name', '')}".strip()
            units = getattr(hit, "total_units", "")
            counted = getattr(hit, "all_counted_units", "")
            tract = hpd_tract_label(getattr(hit, "census_tract", ""))
            rows.append(
                [
                    record.project_name,
                    number(record.total_units),
                    number(record.affordable_units),
                    f"{getattr(hit, 'project_name', '')}; {address}",
                    f"{units} total, {counted} counted, tract {tract}",
                ]
            )
    return (
        "### Housing production\n\n"
        f"The HPD extract has {len(hpd)} building rows in community board MN-09. "
        "A row is listed when its address or project name meets the rule for that printed project. "
        "Counted units are HPD's affordable-unit field. They sit beside the printed counts and are not substituted for them. "
        "An address that differs from the printed address means the name rule hit a different building.\n\n"
        + md_table(
            ["Printed project", "Printed total", "Printed affordable", "HPD building", "HPD units"],
            rows,
        )
    )


def requests_md() -> str:
    path = RETRIEVED / "requests_311_by_type.csv"
    if not path.exists():
        return "### 311 requests\n\nThe 311 snapshot is not on disk.\n"
    raw = pd.read_csv(path, dtype=str)
    raw["requests"] = raw["requests"].astype(int)
    raw["year"] = raw["year"].astype(int)
    published = requests_311()
    pub_rows = [
        [record.request_type, str(int(record.year)), number(record.requests)]
        for record in published.itertuples(index=False)
    ]
    tagged = raw.copy()
    tagged["tag"] = tagged["complaint_type"].map(_request_tag)
    focus = tagged[tagged["tag"].ne("")]
    focus_rows = [
        [str(int(record.year)), record.complaint_type, record.tag, number(record.requests)]
        for record in focus.sort_values(["year", "requests"], ascending=[True, False]).itertuples(index=False)
    ]
    if not focus_rows:
        focus_rows = [["—", "No complaint type contains mental, homeless, or shelter", "", "0"]]
    tract_sum = int(requests_311_tracts()["mental_health_requests"].sum())
    return (
        "### 311 requests\n\n"
        "The snapshot is every complaint type for community board `09 MANHATTAN` in calendar years 2023 and 2024, aggregated on the open-data server. "
        "The report's category names are kept as printed. A retrieved type is listed below when its name contains mental or homeless, or when the type is an encampment complaint.\n\n"
        + md_table(["Printed category", "Year", "Printed requests"], pub_rows)
        + "\n"
        + md_table(["Year", "311 complaint type", "Name contains", "Requests"], focus_rows)
        + "\n"
        + f"The four printed tract counts of mental-health requests sum to {number(tract_sum)}, which is the printed 2024 district total. "
        + "The snapshot is not assigned to tracts, because the report does not document the tract filter.\n"
    )


def _request_tag(name: object) -> str:
    text = str(name).lower()
    if "mental" in text:
        return "mental"
    if "homeless" in text:
        return "homeless"
    if "encampment" in text:
        return "encampment"
    return ""


def _blank(value: object) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return True
    return str(value).strip() in {"", "nan", "None"}


def _tract_sort(value: str) -> tuple[int, int]:
    text = str(value)
    if "." in text:
        base, suffix = text.split(".", 1)
        return int(base), int(suffix)
    if text.isdigit():
        return int(text), 0
    return 10_000, 0
