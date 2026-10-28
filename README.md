# CB9 housing analysis

Methods companion for the Manhattan Community Board 9 housing analysis. The policy document is [`report/cb9-housing-analysis.pdf`](report/cb9-housing-analysis.pdf). The site's tract, project, and 311 tables are built from the 2023 Census estimates, including household income brackets, HPD building records, the NYCHA data book, PLUTO, the borough president's recommendation for 1727 Amsterdam, and two 311 complaint types. Mental-health and food sites come from the NYC Facilities Database. The saturation formula is stated. It is not scored, because that file does not contain supportive-housing unit counts. Geography draws Western Harlem in Manhattan from the 2020 tract boundaries.

Prepared by Arnav Sahai.

## Read it in order

1. Geography — Western Harlem in Manhattan, with tract boundaries and the 2023 estimates.
2. Sources — the datasets and how each one is retrieved.
3. Analysis — tract incomes and household brackets against three-person AMI limits, and the project register.
4. Saturation index — the weighted formula, the site counts, and how a score is read.
5. Recommendations — the actions in the housing analysis report, and the PDF.

## Repository

| Path | Contents |
| --- | --- |
| `report/` | The housing analysis PDF |
| `data/published/` | Tables transcribed from the PDF, with printed page numbers |
| `data/retrieved/` | ACS, HPD, 311, facilities, NYCHA, and PLUTO snapshots written by the pipeline scripts |
| `data/sources/` | Cited AMI limits, the 1727 Amsterdam record, and the existing-building register |
| `data/resolved/` | Tract, project, and 311 tables written by the site build |
| `src/cb9/` | Affordability gap, inventory sums, both saturation-index formulas, and the resolver |
| `pipelines/` | Retrieval scripts and the manual source log |
| `site/` | Quarto website |
| `scripts/build_site_data.py` | Regenerates figures, computed pages, and the PDF copy inside the site |

## Rebuild the computed pages

The site reads local files. Rendering does not download data.

```bash
python3 -m unittest tests/test_calculations.py
python3 scripts/build_site_data.py
quarto render site
```

Open `site/_site/index.html`.

## Refresh the public snapshots

```bash
python3 pipelines/fetch_acs.py
python3 pipelines/fetch_income_brackets.py
python3 pipelines/fetch_hpd.py
python3 pipelines/fetch_311.py
python3 pipelines/fetch_facilities.py
python3 pipelines/fetch_stock.py
python3 scripts/build_site_data.py
```

`CENSUS_API_KEY` is optional. With a key, the census script uses the Census API for the median, poverty, rent, and population tables. Without one, it reads the Bureau's 2023 5-year summary files and keeps the MN09 rows. Household income brackets always come from summary-file table B19001. The 311 query is aggregated by complaint type for community board `09 MANHATTAN` in 2023 and 2024.

## Publish on GitHub Pages

`.github/workflows/pages.yml` installs Quarto, rebuilds the computed pages from the committed tables, and publishes `site/_site`. Enable GitHub Pages with the GitHub Actions source on the repository. The first publication needs a public remote; create the repository and turn Pages on when the name and visibility are settled.

## Scope

The PDF is the policy end product. This site does not revise it. The production total is the two HPD buildings only. Grant Houses and Morningside Gardens are existing buildings and stay out of that sum. 1727 Amsterdam is listed and left out as well. The saturation index stays unscored until supportive-housing unit counts exist. The facility file supplies sites, and its capacity field is 0.
