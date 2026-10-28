"""Build the tract, project, and 311 tables used by the resolved site pages."""

from __future__ import annotations

import pandas as pd

from cb9.income_brackets import assert_brackets
from cb9.match import hpd_tract_label
from cb9.paths import RETRIEVED, SOURCES
from cb9.services import assert_services

# Identifiers printed in the PDF. A blank census id means this repository does
# not assign that printed label to a 2020 tract.
REPORT_TRACT_IDS: list[tuple[str, str]] = [
    ("197.01", "Morningside Heights profile"),
    ("199", "Tract guide"),
    ("201.01", "Tract guide"),
    ("203", "Tract guide"),
    ("205", "Tract guide"),
    ("207.01", "Tract guide"),
    ("209", "Service matrix"),
    ("209.01", "Tract guide and Morningside profile"),
    ("211", "Tract guide and Morningside profile"),
    ("213.01", "Manhattanville profile"),
    ("213.03", "Tract guide"),
    ("217.01", "Manhattanville profile"),
    ("219", "Tract guide, profiles, and service matrix"),
    ("221", "Profiles and service matrix"),
    ("221.01", "Manhattanville profile and project table"),
    ("222", "Tract guide, also labeled Census Tract 221"),
    ("223", "Project table for Harlem Commons"),
    ("223.01", "Tract guide"),
    ("225", "Tract guide and Manhattanville profile"),
    ("227", "Tract guide"),
    ("227.01", "Manhattanville profile"),
    ("229", "Tract guide and Manhattanville profile"),
    ("231", "Tract guide and service matrix"),
    ("231.01", "Hamilton Heights profile"),
    ("233", "Tract guide and Hamilton Heights profile"),
    ("235.01", "Tract guide"),
    ("237", "Tract guide"),
]

HPD_BUILDINGS: list[dict[str, str]] = [
    {
        "project_id": "ps186",
        "display_name": "PS 186",
        "project_name_contains": "PS 186",
        "house_number": "525",
        "street_contains": "145",
    },
    {
        "project_id": "sunrose",
        "display_name": "Sunrose",
        "project_name_contains": "620 WEST 153",
        "house_number": "620",
        "street_contains": "153",
    },
]

OMITTED_FROM_PDF: list[tuple[str, str]] = [
    (
        "ANCP Morningside",
        "Habitat for Humanity NYC and Westchester describes 35 residential units now and 36 after rehabilitation, at Manhattan Avenue, West 115th Street, and West 116th Street. PLUTO places 494 Manhattan Avenue (9 residential units) and 357 West 115 Street (18 residential units) in community district 110, not MN09. 321 West 116 Street has no PLUTO row under that address. HPD's Morningside Cluster row at 494 Manhattan Avenue is community board MN-10. The cluster is not added to the MN09 total.",
    ),
    (
        "Columbia Manhattanville, 125 Amsterdam Avenue",
        "No HPD row matches this address. It is not the Manhattanville phase rows at 3595 Broadway, and no unit count is recorded here.",
    ),
    ("2975 Broadway", "No HPD row matches this address, so no unit count is recorded here."),
    ("Harlem Commons", "No HPD row matches this name, so no unit count is recorded here."),
]

REQUEST_TYPES = ("Homeless Person Assistance", "Encampment")


def ami_limits() -> pd.DataFrame:
    frame = pd.read_csv(SOURCES / "ami_limits.csv")
    frame["income_limit"] = frame["income_limit"].astype(int)
    frame["ami_pct"] = frame["ami_pct"].astype(int)
    return frame


def tracts() -> pd.DataFrame:
    frame = pd.read_csv(RETRIEVED / "acs_2023_tracts.csv", dtype=str)
    frame["tract_label"] = frame["tract_label"].str.strip()
    if frame["tract_label"].duplicated().any():
        raise ValueError("Resolved tract labels must be unique")
    return frame.sort_values("tract_label", key=lambda series: series.map(_tract_sort)).reset_index(drop=True)


def tract_crosswalk() -> pd.DataFrame:
    official = set(tracts()["tract_label"])
    rows = []
    for report_id, where in REPORT_TRACT_IDS:
        if report_id in official:
            rows.append(
                {
                    "report_id": report_id,
                    "where_printed": where,
                    "census_2020_id": report_id,
                    "relationship": "Same 2020 tract id in MN09",
                }
            )
        else:
            rows.append(
                {
                    "report_id": report_id,
                    "where_printed": where,
                    "census_2020_id": "",
                    "relationship": "Printed in the PDF and not a 2020 MN09 tract id",
                }
            )
    return pd.DataFrame(rows)


def projects() -> pd.DataFrame:
    hpd = pd.read_csv(RETRIEVED / "hpd_mn09.csv", dtype=str)
    rows = [_hpd_row(hpd, rule) for rule in HPD_BUILDINGS]
    external = pd.read_csv(SOURCES / "external_projects.csv", dtype=str)
    rows.extend(external.to_dict(orient="records"))
    rows.extend(_stock_rows())
    frame = pd.DataFrame(rows)
    frame["include_in_total"] = frame["include_in_total"].map(_as_bool)
    frame["total_is_approximate"] = frame["total_is_approximate"].map(_as_bool)
    return frame


def project_totals(frame: pd.DataFrame | None = None) -> dict[str, int]:
    frame = projects() if frame is None else frame
    included = frame[frame["include_in_total"]]
    return {
        "buildings": int(len(included)),
        "total_units": int(included["total_units"].astype(int).sum()),
        "affordable_units": int(included["affordable_units"].astype(int).sum()),
    }


def omitted_projects() -> pd.DataFrame:
    return pd.DataFrame(OMITTED_FROM_PDF, columns=["printed_project", "reason"])


def requests() -> pd.DataFrame:
    raw = pd.read_csv(RETRIEVED / "requests_311_by_type.csv", dtype=str)
    raw["requests"] = raw["requests"].astype(int)
    raw["year"] = raw["year"].astype(int)
    kept = raw[raw["complaint_type"].isin(REQUEST_TYPES)].copy()
    if set(kept["complaint_type"]) - set(REQUEST_TYPES):
        raise ValueError("311 extract includes a type outside the resolved list")
    return kept.sort_values(["year", "complaint_type"]).reset_index(drop=True)


def assert_consistent() -> None:
    tract_frame = tracts()
    acs = pd.read_csv(RETRIEVED / "acs_2023_tracts.csv", dtype=str)
    merged = tract_frame.merge(acs, on="geoid", suffixes=("", "_acs"))
    if len(merged) != len(tract_frame):
        raise AssertionError("Every resolved tract must come from the ACS snapshot")
    mismatch = merged[merged["median_income"].fillna("") != merged["median_income_acs"].fillna("")]
    if not mismatch.empty:
        raise AssertionError("Resolved incomes differ from the ACS snapshot")
    if tract_frame["tract_label"].duplicated().any():
        raise AssertionError("Duplicate tract labels")
    register = projects()
    totals = project_totals(register)
    if totals != {"buildings": 2, "total_units": 317, "affordable_units": 151}:
        raise AssertionError(f"Verified project total changed: {totals}")
    proposal = register[register["project_id"].eq("1727_amsterdam")]
    if proposal.empty or bool(proposal.iloc[0]["include_in_total"]):
        raise AssertionError("1727 Amsterdam must stay outside the unit total")
    types = set(requests()["complaint_type"])
    if not types <= set(REQUEST_TYPES):
        raise AssertionError(f"Unexpected 311 types: {types}")
    cross = tract_crosswalk()
    if cross["report_id"].duplicated().any():
        raise AssertionError("Duplicate report tract ids")
    _assert_stock(register)
    assert_brackets()
    assert_services(tract_frame)


def _hpd_row(hpd: pd.DataFrame, rule: dict[str, str]) -> dict[str, str]:
    names = hpd["project_name"].fillna("").str.upper()
    houses = hpd["house_number"].fillna("").str.strip()
    streets = hpd["street_name"].fillna("").str.upper()
    mask = (
        names.str.contains(rule["project_name_contains"], regex=False)
        & houses.eq(rule["house_number"])
        & streets.str.contains(rule["street_contains"], regex=False)
    )
    hits = hpd.loc[mask]
    if len(hits) != 1:
        raise ValueError(f"{rule['project_id']} matched {len(hits)} HPD rows")
    hit = hits.iloc[0]
    completed = str(hit["project_completion_date"]).split("T")[0]
    return {
        "project_id": rule["project_id"],
        "display_name": rule["display_name"],
        "project_name": hit["project_name"],
        "address": f"{hit['house_number']} {hit['street_name']}".title(),
        "bbl": hit["bbl"],
        "status": "Completed",
        "record_date": completed,
        "total_units": str(int(hit["total_units"])),
        "total_is_approximate": "false",
        "affordable_units": str(int(hit["all_counted_units"])),
        "tract_label": hpd_tract_label(hit["census_tract"]),
        "source": "HPD Affordable Housing Production by Building",
        "source_url": "https://data.cityofnewyork.us/Housing-Development/Affordable-Housing-Production-by-Building/hg8x-zxpr",
        "include_in_total": "true",
        "kind": "production",
        "notes": f"HPD counted units are the agency affordable-unit field. Construction type: {hit['reporting_construction_type']}.",
    }


def _stock_rows() -> list[dict[str, str]]:
    spec = pd.read_csv(SOURCES / "stock_buildings.csv", dtype=str)
    grant = pd.read_csv(RETRIEVED / "nycha_grant.csv", dtype=str)
    pluto = pd.read_csv(RETRIEVED / "pluto_examined.csv", dtype=str)
    if len(grant) != 1:
        raise ValueError("Expected one NYCHA GRANT row")
    grant_row = grant.iloc[0]
    morningside = pluto[pluto["address"].eq("80 LA SALLE STREET")]
    if len(morningside) != 1:
        raise ValueError("Expected one PLUTO row for 80 La Salle Street")
    lot = morningside.iloc[0]
    total = _plain_int(grant_row["total_number_of_apartments"])
    current = _plain_int(grant_row["number_of_current_apartments"])
    units = _plain_int(lot["unitsres"])
    details = {
        "grant_houses": {
            "bbl": "",
            "status": "Existing",
            "record_date": _mdy(grant_row["data_as_of"]),
            "total_units": str(total),
            "notes": (
                f"Existing public housing. The NYCHA data book, as of {grant_row['data_as_of']}, "
                f"lists {total:,} total apartments and {current:,} current apartments "
                f"in Manhattan community district {grant_row['community_distirct']}. "
                f"HUD AMP {grant_row['hud_amp_']}. Completed {str(grant_row['completion_date']).split('T')[0]}. "
                "Not an HPD production project, so these apartments are not in the production total. "
                "The data book does not use HPD's counted-units field, so the affordable count is blank."
            ),
        },
        "morningside_gardens": {
            "bbl": _bbl(lot["bbl"]),
            "status": "Existing",
            "record_date": str(lot["yearbuilt"]),
            "total_units": str(units),
            "notes": (
                f"PLUTO lists {units:,} residential units at this tax lot in community district {lot['cd']}. "
                "The cooperative's history page says the six buildings were home to 980 families by 1958. "
                "The register uses the PLUTO residential-unit count. "
                "Existing cooperative housing, not an HPD production project, so these units are not in the production total. "
                "No affordable-unit count is recorded here."
            ),
        },
    }
    rows = []
    for record in spec.to_dict(orient="records"):
        extra = details.get(record["project_id"])
        if extra is None:
            raise ValueError(f"No snapshot for {record['project_id']}")
        rows.append(
            {
                **record,
                **extra,
                "total_is_approximate": "false",
                "affordable_units": "",
                "tract_label": "",
                "include_in_total": "false",
            }
        )
    return rows


def _assert_stock(register: pd.DataFrame) -> None:
    grant = register[register["project_id"].eq("grant_houses")]
    gardens = register[register["project_id"].eq("morningside_gardens")]
    if len(grant) != 1 or len(gardens) != 1:
        raise AssertionError("Grant Houses and Morningside Gardens must both be on the register")
    if int(grant.iloc[0]["total_units"]) != 1940 or bool(grant.iloc[0]["include_in_total"]):
        raise AssertionError("Grant Houses must stay at 1,940 apartments and outside the production total")
    if int(gardens.iloc[0]["total_units"]) != 982 or bool(gardens.iloc[0]["include_in_total"]):
        raise AssertionError("Morningside Gardens must stay at 982 residential units and outside the production total")
    if set(register["kind"]) != {"production", "proposal", "existing"}:
        raise AssertionError(f"Unexpected project kinds: {set(register['kind'])}")
    pluto = pd.read_csv(RETRIEVED / "pluto_examined.csv", dtype=str)
    outside = pluto[pluto["address"].isin(["494 MANHATTAN AVENUE", "357 WEST 115 STREET"])]
    if set(outside["cd"]) != {"110"}:
        raise AssertionError("The examined ANCP buildings should be community district 110")
    names = set(omitted_projects()["printed_project"])
    if "ANCP Morningside" not in names or "General Grant Houses renovation" in names:
        raise AssertionError("The omitted-project list is out of date")


def _as_bool(value: object) -> bool:
    return str(value).strip().lower() == "true"


def _tract_sort(value: str) -> tuple[int, int]:
    text = str(value)
    if "." in text:
        base, suffix = text.split(".", 1)
        return int(base), int(suffix)
    return int(text), 0


def _plain_int(value: object) -> int:
    return int(str(value).replace(",", "").split(".", 1)[0])


def _bbl(value: object) -> str:
    text = str(value).strip()
    if "." in text:
        return text.split(".", 1)[0]
    return text


def _mdy(value: object) -> str:
    month, day, year = str(value).split("/")
    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
