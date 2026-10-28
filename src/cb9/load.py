"""Load the transcribed report tables."""

from __future__ import annotations

import pandas as pd

from cb9.paths import PUBLISHED


def _csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PUBLISHED / name)


def benchmarks() -> dict[str, float]:
    frame = _csv("ami_benchmarks.csv")
    return dict(zip(frame["benchmark_id"], frame["value"].astype(float), strict=True))


def tract_guide() -> pd.DataFrame:
    return pd.read_csv(PUBLISHED / "tract_guide.csv", dtype={"tract_id": str})


def projects() -> pd.DataFrame:
    frame = pd.read_csv(PUBLISHED / "projects.csv", dtype={"tract": str, "project_id": str})
    frame["total_units"] = frame["total_units"].astype(int)
    frame["affordable_units"] = frame["affordable_units"].astype(int)
    return frame


def aggregates() -> pd.DataFrame:
    return _csv("published_aggregates.csv")


def service_matrix() -> pd.DataFrame:
    frame = _csv("service_matrix.csv")
    frame["is_district_average"] = frame["is_district_average"].astype(str).str.lower().eq("true")
    return frame


def income_statements() -> pd.DataFrame:
    return _csv("income_statements.csv")


def income_pairs() -> pd.DataFrame:
    return _csv("income_pairs.csv")


def accessibility() -> pd.DataFrame:
    return _csv("accessibility.csv")


def income_distribution() -> pd.DataFrame:
    return _csv("income_distribution.csv")


def district_rates() -> pd.DataFrame:
    return _csv("district_rates.csv")


def ssi_policy() -> pd.DataFrame:
    return _csv("ssi_policy.csv")


def requests_311() -> pd.DataFrame:
    return _csv("requests_311.csv")


def requests_311_tracts() -> pd.DataFrame:
    return _csv("requests_311_tracts.csv")
