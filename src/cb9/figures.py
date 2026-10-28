"""Static figures drawn from the transcribed tables and the formulas."""

from __future__ import annotations

import os

# Set before pyplot is imported. The home matplotlib cache is not always writable.
os.environ.setdefault("MPLCONFIGDIR", str((__import__("pathlib").Path(__file__).resolve().parents[2] / ".mplconfig")))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from cb9.paths import FIGURES
from cb9.ssi import weighted_terms

INK = "#1c1917"
NAVY = "#1b334f"
RUST = "#9a3412"
TEAL = "#3f6f6a"
SAND = "#c4b49a"
GRID = "#e7e1d8"


def _style(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#d6d0c6")
    ax.spines["bottom"].set_color("#d6d0c6")
    ax.tick_params(colors=INK, labelsize=10)
    ax.yaxis.grid(True, color=GRID, zorder=0)
    ax.set_axisbelow(True)


def _save(fig: plt.Figure, name: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / name, format="svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def tract_income_chart(tract_frame: pd.DataFrame, limits: pd.DataFrame) -> None:
    """ACS tract medians with the 2025 three-person AMI limits as reference lines."""
    frame = tract_frame[tract_frame["median_income"].fillna("").astype(str).str.strip().ne("")].copy()
    frame["income"] = frame["median_income"].astype(float)
    frame = frame.sort_values("income")
    fig, ax = plt.subplots(figsize=(8.2, 7.2))
    ax.barh(frame["tract_label"], frame["income"], color=NAVY, zorder=2)
    styles = {30: (SAND, "30% AMI"), 60: (RUST, "60% AMI"), 100: ("#44403c", "100% AMI")}
    for record in limits.itertuples(index=False):
        if int(record.ami_pct) not in styles:
            continue
        color, label = styles[int(record.ami_pct)]
        ax.axvline(record.income_limit, color=color, linewidth=1.2, linestyle="--", label=label, zorder=3)
    ax.set_xlabel("Median household income, 2023 dollars")
    ax.legend(frameon=False, loc="lower right")
    _style(ax)
    _save(fig, "tract_medians.svg")


def verified_projects_chart(register: pd.DataFrame) -> None:
    included = register[register["include_in_total"]].copy()
    included["total_units"] = included["total_units"].astype(float)
    included["affordable_units"] = included["affordable_units"].astype(float)
    import numpy as np

    labels = ["PS 186", "Sunrose"]
    order = ["ps186", "sunrose"]
    included = included.set_index("project_id").loc[order]
    x = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    total_bars = ax.bar(x - width / 2, included["total_units"], width=width, label="Total units", color=NAVY, zorder=2)
    aff_bars = ax.bar(x + width / 2, included["affordable_units"], width=width, label="HPD counted affordable", color=RUST, zorder=2)
    for bar in (*total_bars, *aff_bars):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 4,
            f"{bar.get_height():.0f}",
            ha="center",
            va="bottom",
            color=INK,
            fontsize=10,
        )
    ax.set_xticks(x, labels)
    ax.set_ylabel("Units")
    ax.set_ylim(0, included["total_units"].max() * 1.2)
    ax.legend(frameon=False)
    _style(ax)
    _save(fig, "verified_projects.svg")


def ami_gap_chart(median: float, ami_limit: float) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    labels = ["CB9 median\nhousehold income", "100% AMI\nfamily of 3"]
    values = [median, ami_limit]
    bars = ax.bar(labels, values, color=[NAVY, RUST], width=0.62, zorder=2)
    ax.set_ylabel("Dollars")
    ax.set_ylim(0, ami_limit * 1.18)
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + ami_limit * 0.03,
            f"${value:,.0f}",
            ha="center",
            va="bottom",
            color=INK,
            fontsize=11,
        )
    _style(ax)
    _save(fig, "ami_gap.svg")


def service_rates_chart(matrix: pd.DataFrame) -> None:
    order = ["219", "221", "209", "231", "CB9"]
    frame = matrix.set_index(matrix["tract_id"].astype(str)).loc[order]
    labels = ["Tract 219", "Tract 221", "Tract 209", "Tract 231", "CB9 average"]
    metrics = [
        ("mh_per_1000", "Mental health sites", NAVY),
        ("sh_per_1000", "Supportive housing units", RUST),
        ("fp_per_1000", "Food pantries", TEAL),
    ]
    import numpy as np

    x = np.arange(len(labels))
    width = 0.24
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    for i, (column, label, color) in enumerate(metrics):
        offset = (i - 1) * width
        ax.bar(x + offset, frame[column].astype(float), width=width, label=label, color=color, zorder=2)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Per 1,000 residents")
    ax.legend(frameon=False, ncols=3, loc="upper right")
    _style(ax)
    _save(fig, "service_rates.svg")


def inventory_chart(row_total: float, row_affordable: float, published_total: float, published_affordable: float) -> None:
    import numpy as np

    labels = ["Total units", "Affordable units"]
    x = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    row_bars = ax.bar(x - width / 2, [row_total, row_affordable], width=width, label="Sum of nine printed rows", color=NAVY, zorder=2)
    pub_bars = ax.bar(
        x + width / 2,
        [published_total, published_affordable],
        width=width,
        label="Published pipeline total",
        color=RUST,
        zorder=2,
    )
    for bar in (*row_bars, *pub_bars):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 30,
            f"{bar.get_height():,.0f}",
            ha="center",
            va="bottom",
            color=INK,
            fontsize=10,
        )
    ax.set_xticks(x, labels)
    ax.set_ylabel("Units")
    ax.set_ylim(0, max(row_total, published_total) * 1.18)
    ax.legend(frameon=False)
    _style(ax)
    _save(fig, "inventory_comparison.svg")


def ssi_components_chart(mh: float, sh: float, fp: float, mh_bar: float, sh_bar: float, fp_bar: float, printed: float) -> None:
    terms = weighted_terms(mh, sh, fp, mh_bar, sh_bar, fp_bar)
    labels = ["Mental health\n0.4 × ratio", "Supportive housing\n0.4 × ratio", "Food pantries\n0.2 × ratio"]
    values = [terms["mh_points"], terms["sh_points"], terms["fp_points"]]
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    bars = ax.bar(labels, values, color=[NAVY, RUST, TEAL], width=0.62, zorder=2)
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 2,
            f"{value:.1f}",
            ha="center",
            va="bottom",
            color=INK,
            fontsize=11,
        )
    ax.axhline(printed, color=SAND, linewidth=1.5, linestyle="--", zorder=1)
    ax.text(2.45, printed + 3, f"Printed index {printed:.0f}", color="#6b6256", fontsize=9, ha="right")
    ax.set_ylabel("Index points")
    ax.set_ylim(0, max(max(values), printed) * 1.22)
    _style(ax)
    _save(fig, "ssi_components.svg")
