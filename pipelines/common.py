"""Shared helpers for the public-data snapshots."""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RETRIEVED = ROOT / "data" / "retrieved"
USER_AGENT = "cb9-housing-methods/0.1 (public data snapshot for a methods site)"


def session() -> requests.Session:
    client = requests.Session()
    client.headers["User-Agent"] = USER_AGENT
    return client


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "" if row.get(key) is None else row.get(key) for key in fieldnames})


def update_manifest(key: str, payload: dict) -> None:
    path = RETRIEVED / "manifest.json"
    current = {}
    if path.exists():
        current = json.loads(path.read_text())
    current[key] = {"retrieved_on": date.today().isoformat(), **payload}
    path.write_text(json.dumps(current, indent=2) + "\n")
