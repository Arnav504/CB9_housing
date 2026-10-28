"""Map of Western Harlem centered in Manhattan, with tract boundaries."""

from __future__ import annotations

import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Polygon
from matplotlib.path import Path

from cb9.figures import FIGURES

WATER = "#d5e3ea"
LAND = "#f4f0e8"
EDGE = "#d9d1c5"
INK = "#1c1917"
NAVY = "#1b334f"
NEIGHBORHOODS = {
    "Morningside Heights": "#1b334f",
    "Manhattanville-West Harlem": "#9a3412",
    "Hamilton Heights-Sugar Hill": "#3f6f6a",
}
CONTEXT = {
    "MN06": "Midtown",
    "MN07": "Upper West Side",
    "MN08": "Upper East Side",
    "MN10": "Central Harlem",
    "MN11": "East Harlem",
    "MN12": "Washington Heights",
}


def write_geography_map(geo_dir) -> None:
    tracts = _load(geo_dir / "manhattan_tracts_2020.geojson")
    borough = _load(geo_dir / "manhattan_borough.geojson")
    districts = _load(geo_dir / "manhattan_community_districts.geojson")
    labels: list[tuple[float, float, str]] = []
    mn09 = [feature for feature in tracts if feature["properties"].get("CDTA2020") == "MN09"]
    if len(mn09) != 20:
        raise ValueError(f"Expected 20 Western Harlem tracts, found {len(mn09)}")

    lat0 = _centroid(mn09)[1]
    west, south, east, north = _bounds(mn09, lat0)
    pad_x = (east - west) * 0.72
    pad_y = (north - south) * 0.58
    district_window = (west, south, east, north)
    window = (west - pad_x, south - pad_y, east + pad_x, north + pad_y)

    fig, ax = plt.subplots(figsize=(8.6, 9.4))
    ax.set_facecolor(WATER)
    fig.patch.set_facecolor(WATER)
    _draw(ax, borough, lat0, facecolor=LAND, edgecolor="#c8bfb2", linewidth=0.4, zorder=1)
    for feature in tracts:
        if feature["properties"].get("CDTA2020") == "MN09":
            continue
        _draw(ax, [feature], lat0, facecolor=LAND, edgecolor=EDGE, linewidth=0.35, zorder=2)
    for feature in mn09:
        color = NEIGHBORHOODS.get(feature["properties"].get("NTAName"), NAVY)
        _draw(ax, [feature], lat0, facecolor=color, edgecolor="#f6f3ee", linewidth=0.7, zorder=3)
        label_x, label_y = _project(*_centroid([feature]), lat0)
        labels.append((label_x, label_y, str(feature["properties"].get("CTLabel") or "")))
    district = [feature for feature in districts if int(feature["properties"].get("BoroCD") or 0) == 109]
    _draw(ax, district, lat0, facecolor="none", edgecolor="#1c1917", linewidth=1.15, zorder=5)
    span_x = (east - west) * 0.16
    span_y = (north - south) * 0.055
    for label_x, label_y, text in _spread(labels, span_x, span_y):
        ax.text(
            label_x,
            label_y,
            text,
            ha="center",
            va="center",
            color="white",
            fontsize=6.1,
            zorder=4,
            path_effects=[pe.withStroke(linewidth=1.6, foreground="#1c1917")],
        )
    _neighborhood_names(ax, mn09, lat0, west)
    _context_labels(ax, tracts, lat0, window, district_window)
    ax.text(
        0.02,
        0.98,
        "Western Harlem",
        transform=ax.transAxes,
        ha="left",
        va="top",
        color=NAVY,
        fontsize=16,
        fontweight="bold",
        zorder=7,
    )
    ax.set_xlim(window[0], window[2])
    ax.set_ylim(window[1], window[3])
    ax.set_aspect("equal")
    ax.axis("off")
    _legend(ax)
    _inset(fig, borough, mn09, lat0)
    ax.annotate(
        "N",
        xy=(0.97, 0.96),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color=NAVY,
        zorder=7,
    )
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "geography_map.svg", format="svg", bbox_inches="tight", facecolor=WATER)
    plt.close(fig)


def _neighborhood_names(ax, features: list[dict], lat0: float, west: float) -> None:
    grouped: dict[str, list[dict]] = {}
    for feature in features:
        grouped.setdefault(feature["properties"].get("NTAName"), []).append(feature)
    short = {
        "Morningside Heights": "Morningside Heights",
        "Manhattanville-West Harlem": "Manhattanville",
        "Hamilton Heights-Sugar Hill": "Hamilton Heights",
    }
    for name, rows in grouped.items():
        _lon, lat = _centroid(rows)
        _x, y = _project(_lon, lat, lat0)
        ax.text(
            west,
            y,
            short.get(name, name),
            ha="right",
            va="center",
            color=NEIGHBORHOODS.get(name, INK),
            fontsize=8.5,
            fontweight="bold",
            zorder=6,
        )


def _context_labels(
    ax,
    tracts: list[dict],
    lat0: float,
    window: tuple[float, float, float, float],
    district: tuple[float, float, float, float],
) -> None:
    grouped: dict[str, list[dict]] = {}
    for feature in tracts:
        code = feature["properties"].get("CDTA2020")
        if code in CONTEXT:
            grouped.setdefault(code, []).append(feature)
    west, south, east, north = window
    for code, rows in grouped.items():
        points = []
        for feature in rows:
            x, y = _project(*_centroid([feature]), lat0)
            if west < x < east and south < y < north:
                points.append((x, y))
        if not points:
            continue
        x = sum(point[0] for point in points) / len(points)
        y = sum(point[1] for point in points) / len(points)
        align = "center"
        if district[0] < x < district[2] and district[1] < y < district[3]:
            x = district[2] + (district[2] - district[0]) * 0.08
            align = "left"
        ax.text(x, y, CONTEXT[code], ha=align, va="center", color="#8a8175", fontsize=8, zorder=3)


def _inset(fig, borough: list[dict], mn09: list[dict], lat0: float) -> None:
    inset = fig.add_axes([0.08, 0.045, 0.15, 0.22])
    inset.set_facecolor(WATER)
    _draw(inset, borough, lat0, facecolor=LAND, edgecolor="#c8bfb2", linewidth=0.3, zorder=1)
    _draw(inset, mn09, lat0, facecolor="#9a3412", edgecolor="#9a3412", linewidth=0.2, zorder=2)
    west, south, east, north = _bounds(borough, lat0)
    pad = (north - south) * 0.04
    inset.set_xlim(west - pad, east + pad)
    inset.set_ylim(south - pad, north + pad)
    inset.set_aspect("equal")
    inset.axis("off")
    for spine in inset.spines.values():
        spine.set_visible(True)
        spine.set_color(NAVY)
        spine.set_linewidth(0.8)
    inset.text(0.5, 1.04, "Manhattan", transform=inset.transAxes, ha="center", va="bottom", fontsize=8, color=NAVY)


def _legend(ax) -> None:
    handles = [
        Polygon([[0, 0]], closed=True, facecolor=color, edgecolor="none", label=name)
        for name, color in NEIGHBORHOODS.items()
    ]
    legend = ax.legend(
        handles=handles,
        frameon=True,
        loc="lower right",
        fontsize=8,
        title="Neighborhoods",
        borderpad=0.6,
    )
    legend.get_frame().set_facecolor("#f6f3ee")
    legend.get_frame().set_edgecolor("#e7e1d8")
    legend.get_title().set_color(NAVY)


def _draw(ax, features, lat0: float, **style) -> None:
    for feature in features:
        for exterior, holes in _polygons(feature["geometry"]):
            patch = PathPatch(_path(exterior, holes, lat0), **style)
            ax.add_patch(patch)


def _path(exterior, holes, lat0: float) -> Path:
    vertices = []
    codes = []
    for ring in [exterior, *holes]:
        points = [_project(lon, lat, lat0) for lon, lat in ring]
        if len(points) < 3:
            continue
        vertices.extend(points)
        codes.append(Path.MOVETO)
        codes.extend([Path.LINETO] * (len(points) - 2))
        codes.append(Path.CLOSEPOLY)
    return Path(vertices, codes)


def _polygons(geometry: dict):
    kind = geometry["type"]
    coords = geometry["coordinates"]
    polygons = coords if kind == "MultiPolygon" else [coords]
    for rings in polygons:
        if rings:
            yield rings[0], rings[1:]


def _project(lon: float, lat: float, lat0: float) -> tuple[float, float]:
    return lon * math.cos(math.radians(lat0)), lat


def _centroid(features: list[dict]) -> tuple[float, float]:
    points = [point for feature in features for ring, _holes in _polygons(feature["geometry"]) for point in ring]
    lon = sum(point[0] for point in points) / len(points)
    lat = sum(point[1] for point in points) / len(points)
    return lon, lat


def _bounds(features: list[dict], lat0: float) -> tuple[float, float, float, float]:
    points = [point for feature in features for ring, _holes in _polygons(feature["geometry"]) for point in ring]
    xs = [_project(lon, lat, lat0)[0] for lon, lat in points]
    ys = [lat for _lon, lat in points]
    return min(xs), min(ys), max(xs), max(ys)


def _spread(labels: list[tuple[float, float, str]], min_dx: float, min_dy: float) -> list[tuple[float, float, str]]:
    placed = [[x, y, text] for x, y, text in labels]
    origins = [(x, y) for x, y, _text in labels]
    for _ in range(80):
        for i in range(len(placed)):
            for j in range(i + 1, len(placed)):
                dx = placed[j][0] - placed[i][0]
                dy = placed[j][1] - placed[i][1]
                if abs(dx) >= min_dx or abs(dy) >= min_dy:
                    continue
                shift = (min_dy - abs(dy)) / 2
                sign = 1 if dy > 0 or (dy == 0 and i % 2 == 0) else -1
                placed[i][1] -= sign * shift
                placed[j][1] += sign * shift
    for (x0, y0), point in zip(origins, placed):
        point[1] = min(y0 + min_dy * 2.2, max(y0 - min_dy * 2.2, point[1]))
    return [(x, y, text) for x, y, text in placed]


def _load(path) -> list[dict]:
    return json.loads(path.read_text())["features"]
