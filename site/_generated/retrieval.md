Snapshots on disk: hpd on 2026-10-27; requests_311 on 2026-10-27; acs on 2026-10-27.

### Census

City Planning assigns 20 2020 census tracts to Manhattan CDTA MN09. The ACS columns are 2023 5-year estimates for those tract IDs. A guide tract that uses a different ID does not join.

| Tract | Where it appears | Guide median | ACS 2023 median | ACS margin of error |
| --- | --- | --- | --- | --- |
| 197.01 | In MN09 only |  | $60,398 | $15,243 |
| 199 | In both | $103,636 | $103,636 | $39,571 |
| 201.01 | In both | $153,826 | $153,826 | $19,340 |
| 203 | In both | $65,806 | $65,806 | $11,263 |
| 205 | In both | $208,500 | $208,500 | $36,515 |
| 207.01 | In both | $82,778 | $82,778 | $26,623 |
| 209.01 | In both | $28,015 | $28,015 | $13,773 |
| 211 | In both | $79,522 | $79,522 | $21,977 |
| 213.03 | In both | $55,466 | $55,466 | $9,830 |
| 217.03 | In MN09 only |  | Suppressed |  |
| 219 | In both | $20,912 | $20,912 | $4,972 |
| 222 | In the guide only | $82,438 |  |  |
| 223.01 | In both | $49,410 | $49,410 | $8,827 |
| 223.02 | In MN09 only |  | $39,004 | $16,059 |
| 225 | In both | $58,015 | $58,015 | $22,454 |
| 227 | In both | $70,120 | $70,120 | $21,458 |
| 229 | In both | $59,145 | $59,145 | $14,803 |
| 231 | In both | $67,175 | $67,175 | $30,917 |
| 233 | In both | $83,232 | $83,232 | $12,799 |
| 235.01 | In both | $80,337 | $80,337 | $15,747 |
| 237 | In both | $60,116 | $60,116 | $22,011 |

### Housing production

The HPD extract has 162 building rows in community board MN-09. A row is listed when its address or project name meets the rule for that printed project. Counted units are HPD's affordable-unit field. They sit beside the printed counts and are not substituted for them. An address that differs from the printed address means the name rule hit a different building.

| Printed project | Printed total | Printed affordable | HPD building | HPD units |
| --- | --- | --- | --- | --- |
| General Grant Houses (renovation) | 382 | 382 | No building row matched the rule |  |
| Morningside Gardens (renovation) | 142 | 142 | No building row matched the rule |  |
| 1727 Amsterdam Ave | 215 | 215 | No building row matched the rule |  |
| ANCP Morningside | 42 | 42 | No building row matched the rule |  |
| PS 186 / Residences at PS 186 | 79 | 79 | PS 186 AKA BGCH (BOYS AND GIRLS CLUB OF HARLEM); 525 WEST 145 STREET | 79 total, 79 counted, tract 229 |
| Sunrose Tower | 238 | 72 | 620 WEST 153 STREET; 620 WEST 153 STREET | 238 total, 72 counted, tract 237 |
| Columbia Manhattanville | 230 | 92 | MANHATTANVILLE PHASE I; 3595 BROADWAY | 43 total, 20 counted, tract 233 |
| Columbia Manhattanville | 230 | 92 | MANHATTANVILLE (PHASE III); 3595 BROADWAY | 43 total, 16 counted, tract 233 |
| Columbia Manhattanville | 230 | 92 | MANHANTANVILLE (PHASE II); 3595 BROADWAY | 43 total, 7 counted, tract 233 |
| 2975 Broadway | 220 | 88 | No building row matched the rule |  |
| Harlem Commons | 165 | 66 | No building row matched the rule |  |

### 311 requests

The snapshot is every complaint type for community board `09 MANHATTAN` in calendar years 2023 and 2024, aggregated on the open-data server. The report's category names are kept as printed. A retrieved type is listed below when its name contains mental or homeless, or when the type is an encampment complaint.

| Printed category | Year | Printed requests |
| --- | --- | --- |
| Mental health crisis | 2023 | 209 |
| Mental health crisis | 2024 | 247 |
| Homelessness/shelter requests | 2023 | 139 |
| Homelessness/shelter requests | 2024 | 156 |
| Housing assistance requests | 2023 | 97 |
| Housing assistance requests | 2024 | 89 |

| Year | 311 complaint type | Name contains | Requests |
| --- | --- | --- | --- |
| 2023 | Encampment | encampment | 454 |
| 2023 | Homeless Person Assistance | homeless | 388 |
| 2024 | Encampment | encampment | 494 |
| 2024 | Homeless Person Assistance | homeless | 317 |

The four printed tract counts of mental-health requests sum to 247, which is the printed 2024 district total. The snapshot is not assigned to tracts, because the report does not document the tract filter.
