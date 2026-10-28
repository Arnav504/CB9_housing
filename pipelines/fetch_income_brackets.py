"""Save ACS 2023 5-year household income brackets for MN09 tracts.

Table B19001 counts households in income brackets. It does not say how many
people are eligible for a housing program. The summary file does not require
a Census API key. Only the MN09 rows are written.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RETRIEVED, session, update_manifest, write_csv
from fetch_acs import SUMMARY, _clean, _load_crosswalk, _stream_table

FILENAME = "acsdt5y2023-b19001.dat"
COLUMNS = [f"B19001_E{i:03d}" for i in range(1, 18)]
FIELDS = ["geoid", "tract", "tract_label", "nta_name", "vintage", *COLUMNS]


def main() -> None:
    client = session()
    tracts = _load_crosswalk(client)
    wanted = {source["geoid"] for source in tracts}
    table = _stream_table(client, FILENAME, wanted)
    rows = []
    for source in tracts:
        record = table.get(source["geoid"], {})
        rows.append(
            {
                "geoid": source["geoid"],
                "tract": source["ct2020"],
                "tract_label": source["ctlabel"],
                "nta_name": source["ntaname"],
                "vintage": "ACS 2023 5-year",
                **{column: _clean(record.get(column)) for column in COLUMNS},
            }
        )
    missing = [row["tract_label"] for row in rows if row["B19001_E001"] == ""]
    write_csv(RETRIEVED / "acs_2023_b19001.csv", rows, FIELDS)
    update_manifest(
        "acs_b19001",
        {
            "rows": len(rows),
            "vintage": "2023 5-year",
            "table": "B19001",
            "universe": "Households",
            "geography": "Manhattan CDTA MN09",
            "file": FILENAME,
            "blank_household_count": missing,
        },
    )
    print(f"Wrote {len(rows)} B19001 rows")
    if missing:
        print(f"Blank household count: {', '.join(missing)}")


if __name__ == "__main__":
    main()
