"""Save the NYCHA and PLUTO rows behind the existing-building register.

General Grant Houses comes from the NYCHA Development Data Book. Morningside
Gardens and the ANCP addresses come from PLUTO, which carries the current
residential-unit count and the community district.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RETRIEVED, session, update_manifest, write_csv

NYCHA = "https://data.cityofnewyork.us/resource/evjd-dqpz.json"
PLUTO = "https://data.cityofnewyork.us/resource/64uk-42ks.json"
NYCHA_FIELDS = [
    "development",
    "borough",
    "community_distirct",
    "total_number_of_apartments",
    "number_of_current_apartments",
    "data_as_of",
    "completion_date",
    "hud_amp_",
    "number_of_residential_bldgs",
    "population_public_housing",
    "location_street_a",
    "location_street_b",
    "location_street_c",
    "location_street_d",
]
PLUTO_FIELDS = ["address", "bldgclass", "unitsres", "unitstotal", "cd", "ownername", "bbl", "yearbuilt"]
PLUTO_ADDRESSES = [
    "80 LA SALLE STREET",
    "494 MANHATTAN AVENUE",
    "357 WEST 115 STREET",
]


def main() -> None:
    client = session()
    grant = client.get(
        NYCHA,
        params={"$where": "development='GRANT' AND borough='MANHATTAN'", "$limit": 5},
        timeout=60,
    )
    grant.raise_for_status()
    grant_rows = grant.json()
    if len(grant_rows) != 1:
        raise SystemExit(f"Expected one Manhattan GRANT row, found {len(grant_rows)}")
    write_csv(RETRIEVED / "nycha_grant.csv", grant_rows, NYCHA_FIELDS)

    pluto_rows = []
    for address in PLUTO_ADDRESSES:
        response = client.get(
            PLUTO,
            params={
                "$select": ",".join(PLUTO_FIELDS),
                "$where": f"address='{address}' AND borough='MN'",
                "$limit": 3,
            },
            timeout=60,
        )
        response.raise_for_status()
        found = response.json()
        if len(found) != 1:
            raise SystemExit(f"{address} matched {len(found)} PLUTO rows")
        pluto_rows.extend(found)
    write_csv(RETRIEVED / "pluto_examined.csv", pluto_rows, PLUTO_FIELDS)
    update_manifest(
        "stock",
        {
            "nycha_rows": 1,
            "pluto_rows": len(pluto_rows),
            "nycha_dataset": "evjd-dqpz",
            "pluto_dataset": "64uk-42ks",
            "pluto_address_without_a_row": "321 WEST 116 STREET",
        },
    )
    print("Wrote the NYCHA GRANT row and the examined PLUTO rows")


if __name__ == "__main__":
    main()
