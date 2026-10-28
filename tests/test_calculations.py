"""Checks for the formulas and the transcribed tables."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cb9.affordability import affordability_gap, income_ratio, share_of_threshold, times_as_dense
from cb9.inventory import summarize_projects
from cb9.load import aggregates, benchmarks, projects, service_matrix
from cb9.match import acs_tract_label, hpd_tract_label
from cb9.resolve import assert_consistent, project_totals, requests, tract_crosswalk, tracts
from cb9.ssi import appendix_ssi, main_ssi


class FormulaTests(unittest.TestCase):
    def test_main_formula_on_printed_matrix(self) -> None:
        bars = (4.4, 9.7, 1.0)
        expected = {
            (8.2, 18.6, 1.4): 179.25,
            (3.1, 0.0, 0.8): 44.18,
            (4.7, 6.2, 1.2): 92.29,
            (2.8, 1.8, 0.6): 44.88,
        }
        for rates, score in expected.items():
            self.assertAlmostEqual(main_ssi(*rates, *bars), score, places=2)

    def test_appendix_formula_on_printed_matrix(self) -> None:
        bars = (4.4, 9.7, 1.0)
        expected = {
            (8.2, 18.6, 1.4): 188.71,
            (3.1, 0.0, 0.8): 15.73,
            (4.7, 6.2, 1.2): 73.79,
            (2.8, 1.8, 0.6): 28.23,
        }
        for rates, score in expected.items():
            self.assertAlmostEqual(appendix_ssi(*rates, *bars), score, places=2)

    def test_printed_scores_differ_from_both_formulas(self) -> None:
        matrix = service_matrix()
        district = matrix[matrix["is_district_average"]].iloc[0]
        bars = (district.mh_per_1000, district.sh_per_1000, district.fp_per_1000)
        for record in matrix[~matrix["is_district_average"]].itertuples(index=False):
            rates = (record.mh_per_1000, record.sh_per_1000, record.fp_per_1000)
            printed = float(record.ssi_printed)
            self.assertNotAlmostEqual(main_ssi(*rates, *bars), printed, places=0)
            self.assertNotAlmostEqual(appendix_ssi(*rates, *bars), printed, places=0)

    def test_gap_matches_printed_dollars(self) -> None:
        values = benchmarks()
        gap = affordability_gap(values["ami_100_hh3"], values["cb9_median_gap"])
        self.assertEqual(gap["gap_dollars"], values["gap_dollars_printed"])
        self.assertAlmostEqual(gap["gap_percent_of_median"], values["gap_percent_printed"], places=1)

    def test_income_descriptions(self) -> None:
        values = benchmarks()
        ratio = income_ratio(values["tract_231_body_high"], values["tract_219_body"])
        self.assertAlmostEqual(ratio["ratio"], 3.53, places=2)
        self.assertAlmostEqual(share_of_threshold(values["tract_219_body"], values["ami_60_hh3"]), 20.1, places=1)
        self.assertAlmostEqual(times_as_dense(18.62, 5.34), 3.49, places=2)
        self.assertAlmostEqual(times_as_dense(18.62, 1.24), 15.02, places=2)

    def test_inventory_sums(self) -> None:
        frame = projects()
        five = summarize_projects(frame[frame["inventory"].eq("five_project")])
        expanded = summarize_projects(frame[frame["inventory"].eq("expanded")])
        published = aggregates().set_index("aggregate_id")
        self.assertEqual(five["total_units"], published.loc["five_project", "total_units"])
        self.assertEqual(five["affordable_units"], published.loc["five_project", "affordable_units"])
        self.assertEqual(expanded["total_units"], 1713)
        self.assertEqual(expanded["affordable_units"], 1178)
        self.assertEqual(int(published.loc["expanded_pipeline", "total_units"]), 1226)
        self.assertEqual(int(published.loc["expanded_pipeline", "affordable_units"]), 749)

    def test_tract_labels(self) -> None:
        self.assertEqual(acs_tract_label("020901"), "209.01")
        self.assertEqual(acs_tract_label("019900"), "199")
        self.assertEqual(hpd_tract_label("23501"), "235.01")
        self.assertEqual(hpd_tract_label("229"), "229")

    def test_resolved_tables_stay_tied_to_their_sources(self) -> None:
        assert_consistent()
        frame = tracts()
        self.assertEqual(len(frame), 20)
        suppressed = frame[frame["tract_label"].eq("217.03")].iloc[0]
        income = suppressed["median_income"]
        self.assertTrue(income != income or str(income).strip() == "")
        self.assertEqual(project_totals(), {"buildings": 2, "total_units": 317, "affordable_units": 151})
        self.assertEqual(set(requests()["complaint_type"]), {"Homeless Person Assistance", "Encampment"})
        unresolved = tract_crosswalk()[tract_crosswalk()["census_2020_id"].eq("")]
        self.assertIn("221", set(unresolved["report_id"]))
        self.assertIn("222", set(unresolved["report_id"]))


if __name__ == "__main__":
    unittest.main()
