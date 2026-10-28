"""Save community district 109 facility rows used for the service inventory.

The extract is the NYC Facilities Database. It is filtered to mental-health,
food, and housing-support facility types. Classification happens later, in
the site build, so this file stays a snapshot of the source rows.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RETRIEVED, session, update_manifest, write_csv

ENDPOINT = "https://data.cityofnewyork.us/resource/ji82-xba5.json"
WHERE = """
cd='109' AND (
  upper(factype) like '%MENTAL%'
  OR upper(factype) like '%FOOD PANTRY%'
  OR upper(factype) like '%SOUP KITCHEN%'
  OR upper(factype) like '%FEEDING%'
  OR upper(factype) like '%SUPPORTED HOUSING%'
  OR upper(factype) like '%SUPPORTED SRO%'
  OR upper(factype) like '%HOUSING SUPPORT%'
  OR upper(factype) like '%NY NY III%'
)
"""
FIELDS = [
    "uid",
    "facname",
    "factype",
    "address",
    "bbl",
    "bin",
    "cd",
    "ct2020",
    "capacity",
    "opname",
    "latitude",
    "longitude",
    "datasource",
]


def main() -> None:
    client = session()
    response = client.get(
        ENDPOINT,
        params={"$where": " ".join(WHERE.split()), "$limit": 5000, "$order": "uid"},
        timeout=90,
    )
    response.raise_for_status()
    rows = response.json()
    if not rows:
        raise SystemExit("Facilities query returned no community district 109 rows.")
    write_csv(RETRIEVED / "facilities_cd109.csv", rows, FIELDS)
    update_manifest(
        "facilities",
        {
            "rows": len(rows),
            "dataset": "ji82-xba5",
            "community_district": "109",
            "filter": "mental health, food, feeding, and housing-support facility types",
        },
    )
    print(f"Wrote {len(rows)} facility rows")


if __name__ == "__main__":
    main()
