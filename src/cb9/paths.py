"""Repository paths. The site build reads local files and does not call the network."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHED = ROOT / "data" / "published"
RETRIEVED = ROOT / "data" / "retrieved"
SOURCES = ROOT / "data" / "sources"
RESOLVED = ROOT / "data" / "resolved"
FIGURES = ROOT / "site" / "figures"
GENERATED = ROOT / "site" / "_generated"
SITE_FILES = ROOT / "site" / "files"
REPORT_PDF = ROOT / "report" / "cb9-housing-analysis.pdf"
