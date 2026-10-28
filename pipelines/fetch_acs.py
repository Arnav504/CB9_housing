"""Download ACS 2023 5-year estimates for the tracts City Planning assigns to MN09.

The tract list is the NYC Open Data 2020 tract-to-CDTA crosswalk (cdtacode MN09).
When CENSUS_API_KEY is set, estimates come from the Census Bureau API. Otherwise
they are read from the Bureau's 2023 5-year table-based summary files, which do
not require a key. Only the MN09 rows are saved. Vintage, universe, estimate,
and margin of error are stored on every row.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RETRIEVED, session, update_manifest, write_csv

CROSSWALK = "https://data.cityofnewyork.us/resource/hm78-6dwm.json"
CENSUS_API = "https://api.census.gov/data/2023/acs/acs5"
SUMMARY = "https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/5YRData/"
TABLES = {
    "b19013": "acsdt5y2023-b19013.dat",
    "b17001": "acsdt5y2023-b17001.dat",
    "b25064": "acsdt5y2023-b25064.dat",
    "b01003": "acsdt5y2023-b01003.dat",
}
FIELDS = [
    "geoid",
    "tract",
    "tract_label",
    "nta_name",
    "median_income",
    "median_income_moe",
    "poverty_universe",
    "poverty_count",
    "poverty_rate_pct",
    "median_rent",
    "median_rent_moe",
    "population",
    "population_moe",
    "vintage",
    "income_universe",
    "poverty_universe_label",
    "rent_universe",
    "source",
]


def _clean(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text in {"", ".", "null", "-"}:
        return ""
    try:
        number = float(text)
    except ValueError:
        return ""
    if number < 0:
        return ""
    if number.is_integer():
        return str(int(number))
    return str(number)


def _rate(count: str, universe: str) -> str:
    if not count or not universe or float(universe) == 0:
        return ""
    return f"{float(count) / float(universe) * 100:.4f}"


def _load_crosswalk(client):
    response = client.get(CROSSWALK, params={"cdtacode": "MN09", "$limit": 100}, timeout=60)
    response.raise_for_status()
    tracts = response.json()
    if not tracts:
        raise SystemExit("The CDTA crosswalk returned no MN09 tracts.")
    write_csv(
        RETRIEVED / "cb9_tracts.csv",
        tracts,
        ["geoid", "boroct2020", "ct2020", "ctlabel", "ntaname", "cdtacode", "cdtaname"],
    )
    return tracts


def _from_api(client, tracts: list[dict]) -> list[dict]:
    variables = [
        "NAME",
        "B19013_001E",
        "B19013_001M",
        "B17001_001E",
        "B17001_002E",
        "B25064_001E",
        "B25064_001M",
        "B01003_001E",
        "B01003_001M",
    ]
    params = {"get": ",".join(variables), "for": "tract:*", "in": "state:36 county:061", "key": os.environ["CENSUS_API_KEY"]}
    response = client.get(CENSUS_API, params=params, timeout=90)
    response.raise_for_status()
    table = response.json()
    header, *records = table
    by_tract = {row[header.index("tract")]: dict(zip(header, row, strict=True)) for row in records}
    rows = []
    for source in tracts:
        values = by_tract.get(source["ct2020"])
        if values is None:
            continue
        universe = _clean(values["B17001_001E"])
        poor = _clean(values["B17001_002E"])
        rows.append(_row(source, {
            "median_income": _clean(values["B19013_001E"]),
            "median_income_moe": _clean(values["B19013_001M"]),
            "poverty_universe": universe,
            "poverty_count": poor,
            "poverty_rate_pct": _rate(poor, universe),
            "median_rent": _clean(values["B25064_001E"]),
            "median_rent_moe": _clean(values["B25064_001M"]),
            "population": _clean(values["B01003_001E"]),
            "population_moe": _clean(values["B01003_001M"]),
            "source": CENSUS_API,
        }))
    return rows


def _stream_table(client, filename: str, wanted: set[str]) -> dict[str, dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    response = client.get(SUMMARY + filename, stream=True, timeout=180)
    response.raise_for_status()
    header: list[str] | None = None
    for raw in response.iter_lines(decode_unicode=True):
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        if not raw:
            continue
        parts = raw.split("|")
        if header is None:
            header = parts
            continue
        geoid = parts[0][-11:]
        if geoid in wanted and len(parts) == len(header):
            found[geoid] = dict(zip(header, parts, strict=True))
        if len(found) == len(wanted) and parts[0].startswith("1400000US") and geoid > max(wanted):
            break
    response.close()
    return found


def _from_summary(client, tracts: list[dict]) -> list[dict]:
    wanted = {source["geoid"] for source in tracts}
    income = _stream_table(client, TABLES["b19013"], wanted)
    poverty = _stream_table(client, TABLES["b17001"], wanted)
    rent = _stream_table(client, TABLES["b25064"], wanted)
    population = _stream_table(client, TABLES["b01003"], wanted)
    rows = []
    for source in tracts:
        geoid = source["geoid"]
        universe = _clean(poverty.get(geoid, {}).get("B17001_E001"))
        poor = _clean(poverty.get(geoid, {}).get("B17001_E002"))
        rows.append(_row(source, {
            "median_income": _clean(income.get(geoid, {}).get("B19013_E001")),
            "median_income_moe": _clean(income.get(geoid, {}).get("B19013_M001")),
            "poverty_universe": universe,
            "poverty_count": poor,
            "poverty_rate_pct": _rate(poor, universe),
            "median_rent": _clean(rent.get(geoid, {}).get("B25064_E001")),
            "median_rent_moe": _clean(rent.get(geoid, {}).get("B25064_M001")),
            "population": _clean(population.get(geoid, {}).get("B01003_E001")),
            "population_moe": _clean(population.get(geoid, {}).get("B01003_M001")),
            "source": SUMMARY,
        }))
    return rows


def _row(source: dict, values: dict) -> dict:
    return {
        "geoid": source["geoid"],
        "tract": source["ct2020"],
        "tract_label": source["ctlabel"],
        "nta_name": source["ntaname"],
        "vintage": "ACS 2023 5-year",
        "income_universe": "Households",
        "poverty_universe_label": "Population for whom poverty status is determined",
        "rent_universe": "Renter-occupied units paying cash rent",
        **values,
    }


def main() -> None:
    client = session()
    tracts = _load_crosswalk(client)
    if os.environ.get("CENSUS_API_KEY"):
        rows = _from_api(client, tracts)
        channel = "census_api"
    else:
        rows = _from_summary(client, tracts)
        channel = "census_summary_file"
    absent = [row["tract_label"] for row in rows if row["population"] == "" and row["median_income"] == ""]
    if len(rows) != len(tracts) or absent:
        raise SystemExit(f"ACS rows missing from the summary files: {absent or 'row count mismatch'}")
    suppressed = [row["tract_label"] for row in rows if row["median_income"] == ""]
    write_csv(RETRIEVED / "acs_2023_tracts.csv", rows, FIELDS)
    update_manifest(
        "acs",
        {
            "rows": len(rows),
            "vintage": "2023 5-year",
            "geography": "Manhattan CDTA MN09",
            "channel": channel,
            "suppressed_median_income": suppressed,
        },
    )
    print(f"Wrote {len(rows)} ACS tract rows via {channel}")
    if suppressed:
        print(f"Suppressed median income: {', '.join(suppressed)}")


if __name__ == "__main__":
    main()
