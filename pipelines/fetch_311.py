"""Download 311 complaint counts for Manhattan Community Board 9, 2023 and 2024.

The query is aggregated on NYC Open Data. It does not download the citywide
service-request file. Counts are by calendar year and complaint type.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RETRIEVED, session, update_manifest, write_csv

RESOURCE = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
YEARS = (2023, 2024)


def _year_query(year: int) -> str:
    start = f"{year}-01-01T00:00:00"
    end = f"{year + 1}-01-01T00:00:00"
    return (
        "SELECT complaint_type, count(*) AS requests "
        f"WHERE community_board = '09 MANHATTAN' "
        f"AND created_date >= '{start}' AND created_date < '{end}' "
        "GROUP BY complaint_type ORDER BY requests DESC LIMIT 5000"
    )


def main() -> None:
    client = session()
    rows: list[dict] = []
    for year in YEARS:
        response = client.get(RESOURCE, params={"$query": _year_query(year)}, timeout=180)
        response.raise_for_status()
        page = response.json()
        if not page:
            raise SystemExit(f"311 aggregation returned no complaint types for {year}.")
        for row in page:
            rows.append({"year": year, "complaint_type": row["complaint_type"], "requests": row["requests"]})
    write_csv(RETRIEVED / "requests_311_by_type.csv", rows, ["year", "complaint_type", "requests"])
    update_manifest(
        "requests_311",
        {
            "rows": len(rows),
            "community_board": "09 MANHATTAN",
            "years": "2023-2024",
            "source": RESOURCE,
        },
    )
    print(f"Wrote {len(rows)} complaint-type rows")


if __name__ == "__main__":
    main()
