"""Download HPD affordable-housing production rows for Manhattan Community Board 9.

The extract is every building row with community_board MN-09. Matching those
rows to the printed project names happens later, in the site build, and does
not replace the printed unit counts.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RETRIEVED, session, update_manifest, write_csv

RESOURCE = "https://data.cityofnewyork.us/resource/hg8x-zxpr.json"
COLUMNS = [
    "project_id",
    "project_name",
    "project_start_date",
    "project_completion_date",
    "building_id",
    "house_number",
    "street_name",
    "borough",
    "postcode",
    "bbl",
    "bin",
    "community_board",
    "census_tract",
    "reporting_construction_type",
    "extended_affordability_status",
    "extremely_low_income_units",
    "very_low_income_units",
    "low_income_units",
    "moderate_income_units",
    "middle_income_units",
    "other_income_units",
    "counted_rental_units",
    "counted_homeownership_units",
    "all_counted_units",
    "total_units",
    "latitude",
    "longitude",
]


def main() -> None:
    client = session()
    rows: list[dict] = []
    offset = 0
    while True:
        response = client.get(
            RESOURCE,
            params={
                "$select": ",".join(COLUMNS),
                "$where": "community_board='MN-09'",
                "$order": "project_name, building_id",
                "$limit": 1000,
                "$offset": offset,
            },
            timeout=90,
        )
        response.raise_for_status()
        page = response.json()
        rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    if not rows:
        raise SystemExit("HPD returned no MN-09 rows.")
    write_csv(RETRIEVED / "hpd_mn09.csv", rows, COLUMNS)
    update_manifest(
        "hpd",
        {"rows": len(rows), "community_board": "MN-09", "source": RESOURCE},
    )
    print(f"Wrote {len(rows)} HPD building rows")


if __name__ == "__main__":
    main()
