"""Sums of the housing rows transcribed from the report."""

from __future__ import annotations

import pandas as pd


def summarize_projects(projects: pd.DataFrame) -> dict[str, float]:
    total = float(projects["total_units"].sum())
    affordable = float(projects["affordable_units"].sum())
    return {
        "rows": float(len(projects)),
        "total_units": total,
        "affordable_units": affordable,
        "remaining_units": total - affordable,
    }
