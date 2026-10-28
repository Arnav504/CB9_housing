"""Site counts from the community district 109 facilities snapshot.

Mental-health and food rows become sites per address. Supportive-housing rows
stay sites: the file's capacity field is not a unit count, so it is not used
as the supportive-housing numerator.
"""

from __future__ import annotations

import re

import pandas as pd

from cb9.match import acs_tract_label
from cb9.paths import RETRIEVED

EXCLUDED_TYPES = {
    "SUMMER ONLY FEEDING SITE",
    "FEEDING SITE",
    "HOUSING SUPPORT",
    "COMMUNITY SERVICES; FAMILY SUPPORT; HOUSING SUPPORT; IMMIGRANT SERVICES",
}
_FLOOR = re.compile(r"\b\d+(ST|ND|RD|TH)\s+FLOOR\b")
_TRAILING_SUFFIX = re.compile(r"\s+(AVENUE|AVE|STREET|ST|BOULEVARD|BLVD|PLACE|PL|ROAD|RD|DRIVE|DR|LANE|LN)$")


def address_key(value: object) -> str:
    text = "" if value is None or (isinstance(value, float) and pd.isna(value)) else str(value)
    text = text.upper().replace(".", " ").replace(",", " ").replace("-", " ")
    text = _FLOOR.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    while _TRAILING_SUFFIX.search(text):
        text = _TRAILING_SUFFIX.sub("", text).strip()
    return text


def roles_for(factype: object) -> set[str]:
    text = " ".join(str(factype).upper().split())
    if text in EXCLUDED_TYPES:
        return set()
    found = set()
    if "MENTAL" in text or "PSYCHOSOCIAL CLUB" in text or "ON-SITE REHABILITATION" in text:
        found.add("mental_health")
    if text in {"FOOD PANTRY", "SOUP KITCHEN"}:
        found.add("food")
    if "SUPPORTED HOUSING" in text or "SUPPORTED SRO" in text or "NY NY III SUPPORTED" in text:
        found.add("supportive_site")
    if not found:
        raise ValueError(f"Unclassified facility type: {factype}")
    return found


def facilities() -> pd.DataFrame:
    frame = pd.read_csv(RETRIEVED / "facilities_cd109.csv", dtype=str).fillna("")
    frame["roles"] = frame["factype"].map(lambda value: "|".join(sorted(roles_for(value))))
    frame["address_key"] = frame["address"].map(address_key)
    frame["tract_label"] = frame["ct2020"].map(acs_tract_label)
    return frame


def sites() -> pd.DataFrame:
    """One row per address and role, using the tract with the most source rows."""
    frame = facilities()
    counted = frame[frame["roles"].ne("")].copy()
    if counted["address_key"].eq("").any():
        raise AssertionError("A counted facility row has no address")
    rows = []
    for key, group in counted.groupby("address_key", sort=True):
        tract = _majority(group["tract_label"])
        if not tract:
            raise AssertionError(f"{key} has no majority tract")
        role_set = set()
        for value in group["roles"]:
            role_set.update(part for part in value.split("|") if part)
        types = sorted(set(group["factype"]))
        names = [name for name in group["opname"] if str(name).strip()]
        for role in sorted(role_set):
            role_rows = group[group["roles"].str.contains(role, regex=False)]
            role_types = sorted(set(role_rows["factype"])) if not role_rows.empty else types
            rows.append(
                {
                    "address_key": key,
                    "address": _display_address(group),
                    "tract_label": tract,
                    "role": role,
                    "facility_types": "; ".join(role_types),
                    "operator": names[0] if names else str(group["facname"].iloc[0]),
                    "source_rows": int(len(group)),
                    "tracts_in_source": ", ".join(sorted(set(group["tract_label"]))),
                }
            )
    return pd.DataFrame(rows)


def tract_site_counts(population: pd.DataFrame) -> pd.DataFrame:
    counted = sites()
    base = population[["tract_label", "population"]].copy()
    base["population"] = base["population"].map(lambda value: int(value) if str(value).strip() not in {"", "nan"} else pd.NA)
    rows = []
    for record in base.itertuples(index=False):
        here = counted[counted["tract_label"].eq(record.tract_label)]
        mental = int(here["role"].eq("mental_health").sum())
        food = int(here["role"].eq("food").sum())
        supportive = int(here["role"].eq("supportive_site").sum())
        people = record.population
        rows.append(
            {
                "tract_label": record.tract_label,
                "mental_health_sites": mental,
                "food_sites": food,
                "supportive_sites": supportive,
                "population": people,
                "mental_health_per_1000": _rate(mental, people),
                "food_per_1000": _rate(food, people),
            }
        )
    return pd.DataFrame(rows)


def supportive_sites() -> pd.DataFrame:
    frame = sites()
    kept = frame[frame["role"].eq("supportive_site")].copy()
    return kept.sort_values(["tract_label", "address_key"]).reset_index(drop=True)


def assert_services(population: pd.DataFrame) -> None:
    frame = facilities()
    if not set(frame["cd"]).issubset({"109"}):
        raise AssertionError("Facility snapshot is not limited to community district 109")
    counted = frame[frame["roles"].ne("")]
    capacities = counted["capacity"].map(lambda value: str(value).strip())
    if not set(capacities).issubset({"0", "0.0"}):
        raise AssertionError("A counted facility row has a capacity other than 0")
    inventory = sites()
    known = set(population["tract_label"])
    if not set(inventory["tract_label"]).issubset(known):
        raise AssertionError("A facility site fell outside the MN09 tract list")
    counts = tract_site_counts(population)
    if int(counts["mental_health_sites"].sum()) != 5:
        raise AssertionError("Mental-health site count changed")
    if int(counts["food_sites"].sum()) != 10:
        raise AssertionError("Food site count changed")
    if int(counts["supportive_sites"].sum()) != 6:
        raise AssertionError("Supportive-housing site count changed")
    amsterdam = inventory[inventory["address_key"].eq("1727 AMSTERDAM")]
    if set(amsterdam["tract_label"]) != {"231"}:
        raise AssertionError("1727 Amsterdam should be counted once, in tract 231")
    hospital = inventory[inventory["address_key"].eq("1090 AMSTERDAM")]
    if set(hospital["tract_label"]) != {"197.01"}:
        raise AssertionError("1090 Amsterdam should be counted once, in tract 197.01")


def _display_address(group: pd.DataFrame) -> str:
    addresses = group["address"].astype(str).str.strip()
    preferred = addresses[addresses.str.contains(r"\b(?:AVENUE|STREET|BOULEVARD)\b")]
    chosen = preferred if not preferred.empty else addresses
    return _majority(chosen) or str(chosen.iloc[0])


def _majority(values: pd.Series) -> str:
    cleaned = values.astype(str).str.strip()
    cleaned = cleaned[~cleaned.isin({"", "nan"})]
    if cleaned.empty:
        return ""
    counts = cleaned.value_counts()
    top = counts[counts.eq(counts.max())]
    if len(top) != 1:
        return ""
    return str(top.index[0])


def _rate(count: int, population: object) -> float:
    if population is pd.NA or population is None:
        return float("nan")
    people = int(population)
    if people <= 0:
        return float("nan")
    return count / people * 1000
