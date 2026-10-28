"""Match printed project names to HPD building rows. A hit is a retrieval result."""

from __future__ import annotations

import pandas as pd

# Each rule is applied to the MN-09 production extract. Address rules require both
# a house number and a street fragment. Name rules match the project name.
RULES: list[dict[str, str]] = [
    {"project_id": "1727_amsterdam", "house": "1727", "street": "AMSTERDAM"},
    {"project_id": "ps186", "house": "525", "street": "145"},
    {"project_id": "sunrose", "house": "620", "street": "153"},
    {"project_id": "2975_broadway", "house": "2975", "street": "BROADWAY"},
    {"project_id": "ancp", "name": "ANCP"},
    {"project_id": "general_grant", "name": "GRANT HOUSE"},
    {"project_id": "morningside_gardens", "name": "MORNINGSIDE GARDENS"},
    {"project_id": "harlem_commons", "name": "HARLEM COMMONS"},
    {"project_id": "columbia", "name": "MANHATTANVILLE"},
    {"project_id": "columbia", "name": "MANHANTANVILLE"},
]


def hpd_tract_label(value: object) -> str:
    """Normalize an HPD census-tract code such as 23501 to 235.01."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return ""
    if "." in text:
        return text
    if not text.isdigit():
        return text
    if len(text) <= 3:
        return str(int(text))
    if len(text) == 5:
        return f"{int(text[:3])}.{text[3:]}"
    if len(text) == 6:
        base = str(int(text[:4]))
        suffix = text[4:]
        return base if suffix == "00" else f"{base}.{suffix}"
    return text


def acs_tract_label(value: object) -> str:
    """Normalize a 6-digit ACS tract code such as 020901 to 209.01."""
    text = str(value).strip().split(".")[0]
    if not text.isdigit():
        return text
    return hpd_tract_label(text.zfill(6) if len(text) < 6 else text)


def match_projects(hpd: pd.DataFrame) -> pd.DataFrame:
    """Return HPD rows that meet one of the printed-project rules."""
    if hpd.empty:
        return hpd
    frame = hpd.copy()
    names = frame.get("project_name", pd.Series("", index=frame.index)).fillna("").str.upper()
    houses = frame.get("house_number", pd.Series("", index=frame.index)).fillna("").astype(str).str.strip()
    streets = frame.get("street_name", pd.Series("", index=frame.index)).fillna("").str.upper()
    hits = []
    for rule in RULES:
        mask = pd.Series(True, index=frame.index)
        if "house" in rule:
            mask &= houses.eq(rule["house"]) & streets.str.contains(rule["street"], regex=False)
        if "name" in rule:
            mask &= names.str.contains(rule["name"], regex=False)
        matched = frame.loc[mask].copy()
        if matched.empty:
            continue
        matched["matched_project_id"] = rule["project_id"]
        hits.append(matched)
    if not hits:
        return frame.iloc[0:0].assign(matched_project_id=pd.Series(dtype=str))
    return pd.concat(hits, ignore_index=True)
