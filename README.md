# CB9 housing analysis

Methods companion for the Manhattan Community Board 9 housing analysis. The policy document is [`report/cb9-housing-analysis.pdf`](report/cb9-housing-analysis.pdf). The site's tract, project, and 311 tables are built from the 2023 Census estimates, HPD building records, the borough president's recommendation for 1727 Amsterdam, and two 311 complaint types. The saturation formula is stated and is not scored. The reproducibility page records where the PDF prints a different figure.

Prepared by Arnav Sahai. Cameron Clarke edited the policy report.

## Read it in order

1. Geography — the 2023 estimates for the current MN09 tracts, and a crosswalk of printed tract ids.
2. Pipelines — census, housing production, services, and 311.
3. Analysis — three-person AMI reference lines and the verified project register.
4. Saturation index — the weighted formula, with no score.
5. The report — the PDF, and where its findings differ from the source tables.
6. Reproducibility — published, recomputed, and retrieved figures.

## Repository

| Path | Contents |
| --- | --- |
| `report/` | The housing analysis PDF |
| `data/published/` | Tables transcribed from the PDF, with printed page numbers |
| `data/retrieved/` | ACS, HPD, and 311 snapshots written by the pipeline scripts |
| `data/sources/` | Cited AMI limits and the 1727 Amsterdam source record |
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
python3 pipelines/fetch_hpd.py
python3 pipelines/fetch_311.py
python3 scripts/build_site_data.py
```

`CENSUS_API_KEY` is optional. With a key, the census script uses the Census API. Without one, it reads the Bureau's 2023 5-year summary files and keeps the MN09 rows. The 311 query is aggregated by complaint type for community board `09 MANHATTAN` in 2023 and 2024.

## Publish on GitHub Pages

`.github/workflows/pages.yml` installs Quarto, rebuilds the computed pages from the committed tables, and publishes `site/_site`. Enable GitHub Pages with the GitHub Actions source on the repository. The first publication needs a public remote; create the repository and turn Pages on when the name and visibility are settled.

## Scope

The PDF is the policy end product. This site does not revise it. The resolved unit total is the two HPD buildings only. 1727 Amsterdam is listed and left out of that sum. The saturation index stays unscored until a service-site list exists.
