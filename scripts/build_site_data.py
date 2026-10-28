"""Write the computed markdown, figures, and PDF that the Quarto site includes."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cb9.geography_map import write_geography_map
from cb9.figures import (
    ami_gap_chart,
    inventory_chart,
    service_rates_chart,
    ssi_components_chart,
    tract_income_chart,
    verified_projects_chart,
)
from cb9.inventory import summarize_projects
from cb9.load import aggregates, benchmarks, projects, service_matrix
from cb9.narrative import (
    access_md,
    census_md,
    distribution_md,
    gap_md,
    hpd_md,
    income_conflicts_md,
    inventory_checks_md,
    projects_md,
    rate_checks_md,
    requests_md,
    retrieval_md,
    ssi_comparison_md,
    ssi_worked_example_md,
    tract_guide_md,
)
from cb9.paths import GENERATED, REPORT_PDF, RESOLVED, RETRIEVED, SITE_FILES
from cb9.resolve import ami_limits, assert_consistent, projects as resolved_projects
from cb9.resolve import requests as resolved_requests
from cb9.resolve import tract_crosswalk, tracts as resolved_tracts
from cb9.resolved_pages import ami_md, crosswalk_md, projects_md as resolved_projects_md
from cb9.resolved_pages import requests_md as resolved_requests_md
from cb9.resolved_pages import tracts_md


def _write(name: str, text: str) -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / name).write_text(text if text.endswith("\n") else text + "\n")


def main() -> None:
    values = benchmarks()
    matrix = service_matrix()
    district = matrix[matrix["is_district_average"]].iloc[0]
    tract = matrix[matrix["tract_id"].astype(str).eq("219")].iloc[0]
    expanded = summarize_projects(projects()[projects()["inventory"].eq("expanded")])
    headline = aggregates().set_index("aggregate_id").loc["expanded_pipeline"]

    _write("tract_guide.md", tract_guide_md())
    _write("gap_arithmetic.md", gap_md())
    _write("income_distribution.md", distribution_md())
    _write("access_tables.md", access_md())
    _write("projects_five.md", projects_md("five_project", "Five projects, 2016–2026"))
    _write("projects_expanded.md", projects_md("expanded", "Nine-row inventory, 2014–2026"))
    _write("inventory_checks.md", inventory_checks_md())
    _write("ssi_worked_example.md", ssi_worked_example_md())
    _write("ssi_comparison.md", ssi_comparison_md())
    _write("income_conflicts.md", income_conflicts_md())
    _write("rate_checks.md", rate_checks_md())
    _write("retrieval.md", retrieval_md())
    # Keep the section files used above available if a page includes them alone.
    _write("census_retrieval.md", census_md())
    _write("hpd_retrieval.md", hpd_md())
    _write("requests_retrieval.md", requests_md())

    assert_consistent()
    RESOLVED.mkdir(parents=True, exist_ok=True)
    resolved_tracts().to_csv(RESOLVED / "tracts.csv", index=False)
    tract_crosswalk().to_csv(RESOLVED / "tract_crosswalk.csv", index=False)
    resolved_projects().to_csv(RESOLVED / "projects.csv", index=False)
    resolved_requests().to_csv(RESOLVED / "requests_311.csv", index=False)
    ami_limits().to_csv(RESOLVED / "ami_limits.csv", index=False)
    _write("resolved_tracts.md", tracts_md())
    _write("tract_crosswalk.md", crosswalk_md())
    _write("resolved_projects.md", resolved_projects_md())
    _write("resolved_requests.md", resolved_requests_md())
    _write("resolved_ami.md", ami_md())

    write_geography_map(RETRIEVED / "geo")
    tract_income_chart(resolved_tracts(), ami_limits())
    verified_projects_chart(resolved_projects())
    ami_gap_chart(values["cb9_median_gap"], values["ami_100_hh3"])
    service_rates_chart(matrix)
    inventory_chart(
        expanded["total_units"],
        expanded["affordable_units"],
        float(headline["total_units"]),
        float(headline["affordable_units"]),
    )
    ssi_components_chart(
        float(tract.mh_per_1000),
        float(tract.sh_per_1000),
        float(tract.fp_per_1000),
        float(district.mh_per_1000),
        float(district.sh_per_1000),
        float(district.fp_per_1000),
        float(tract.ssi_printed),
    )

    if not REPORT_PDF.exists():
        raise FileNotFoundError(f"Missing policy report: {REPORT_PDF}")
    SITE_FILES.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPORT_PDF, SITE_FILES / "cb9-housing-analysis.pdf")


if __name__ == "__main__":
    main()
