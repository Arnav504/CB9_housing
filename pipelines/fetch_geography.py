"""Save Manhattan tract, community-district, and borough boundaries for the map.

The site build reads these files and does not call the network. Geometries are
the NYC Planning layers, simplified slightly so the map stays readable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RETRIEVED, session, update_manifest

BASE = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services"
OUT = RETRIEVED / "geo"
TRACT_EPS = 0.00008
OUTLINE_EPS = 0.00015


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    client = session()
    tracts = _query(
        client,
        "NYC_Census_Tracts_for_2020_US_Census",
        "BoroCode=1",
        "GEOID,CTLabel,NTAName,CDTA2020,CDTANAME",
    )
    districts = _query(client, "NYC_Community_Districts", "BoroCD>=100 AND BoroCD<200", "BoroCD")
    borough = _query(client, "NYC_Borough_Boundary", "BoroCode=1", "BoroCode,BoroName")
    _write("manhattan_tracts_2020.geojson", tracts, TRACT_EPS)
    _write("manhattan_community_districts.geojson", districts, OUTLINE_EPS)
    _write("manhattan_borough.geojson", borough, OUTLINE_EPS)
    mn09 = [feature for feature in tracts["features"] if feature["properties"].get("CDTA2020") == "MN09"]
    if len(mn09) != 20:
        raise SystemExit(f"Expected 20 MN09 tracts, found {len(mn09)}")
    update_manifest(
        "geography",
        {
            "channel": "nyc_planning_arcgis",
            "tracts": len(tracts["features"]),
            "mn09_tracts": len(mn09),
            "community_districts": len(districts["features"]),
            "source": BASE,
        },
    )
    print(f"manhattan tracts {len(tracts['features'])}, MN09 {len(mn09)}")


def _query(client, service: str, where: str, fields: str) -> dict:
    response = client.get(
        f"{BASE}/{service}/FeatureServer/0/query",
        params={"where": where, "outFields": fields, "outSR": "4326", "f": "geojson"},
        timeout=90,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(payload["error"])
    return payload


def _write(name: str, collection: dict, epsilon: float) -> None:
    features = []
    for feature in collection["features"]:
        geometry = _simplify_geometry(feature.get("geometry"), epsilon)
        if geometry is None:
            continue
        features.append({"type": "Feature", "properties": feature.get("properties") or {}, "geometry": geometry})
    payload = {"type": "FeatureCollection", "features": features}
    (OUT / name).write_text(json.dumps(payload, separators=(",", ":")))
    print(name, (OUT / name).stat().st_size)


def _simplify_geometry(geometry: dict | None, epsilon: float) -> dict | None:
    if not geometry:
        return None
    kind = geometry["type"]
    if kind == "Polygon":
        rings = _simplify_polygon(geometry["coordinates"], epsilon)
        return {"type": "Polygon", "coordinates": rings} if rings else None
    if kind == "MultiPolygon":
        polygons = [rings for poly in geometry["coordinates"] if (rings := _simplify_polygon(poly, epsilon))]
        return {"type": "MultiPolygon", "coordinates": polygons} if polygons else None
    return None


def _simplify_polygon(rings: list, epsilon: float) -> list:
    kept = []
    for ring in rings:
        simplified = _rdp([(float(x), float(y)) for x, y in ring], epsilon)
        if len(simplified) >= 4:
            if simplified[0] != simplified[-1]:
                simplified.append(simplified[0])
            kept.append([[round(x, 6), round(y, 6)] for x, y in simplified])
    return kept


def _rdp(points: list[tuple[float, float]], epsilon: float) -> list[tuple[float, float]]:
    if len(points) < 3:
        return points
    end = len(points) - 1
    farthest = 0.0
    index = 0
    for i in range(1, end):
        distance = _distance(points[i], points[0], points[end])
        if distance > farthest:
            farthest = distance
            index = i
    if farthest > epsilon:
        return _rdp(points[: index + 1], epsilon)[:-1] + _rdp(points[index:], epsilon)
    return [points[0], points[end]]


def _distance(point, start, end) -> float:
    x, y = point
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return ((x - (x1 + t * dx)) ** 2 + (y - (y1 + t * dy)) ** 2) ** 0.5


if __name__ == "__main__":
    main()
