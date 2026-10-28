# Cursor Handoff: Revised CB9 PDF Reconciliation and Remaining-Issues Audit

## Objective and controlling instructions
Audit the revised report against the review comments and earlier conversation, then repair the remaining discrepancies with reproducible sources and calculations. The user requested a full reconciliation this turn, superseding the earlier one-comment-at-a-time pacing for this audit. For subsequent reviewer-response work, retain individual-comment pacing unless instructed otherwise. Do not assume most issues are resolved simply because that was the user's expectation. Preserve improvements; do not revert the revised report to the older draft.

## Current authoritative artifact
- Current report: `cb9-housing-analysis.pdf`, 59 PDF pages, 111,376 extracted characters, 4,693,267 bytes.
- Older reference: `Manhattan-Community-Board-9-Housing-Analysis_-In-Depth-Data-Driven-Report-v2.pdf`.
- Older DOCX: `Manhattan-Community-Board-9-Housing-Analysis_-In-Depth-Data-Driven-Report.docx`.
- Current report is prepared by Arnav Sahai and credits Cameron Clarke as editor. Credit does not independently validate data.
- All 59 pages of the current PDF were text-extracted with pypdf during this audit. Embedded charts/maps were not visually certified. Figure presence and captions are observable, but arrow alignment, map geometry and a cumulative plotted line remain unverified.
- Page references below are PRINTED page labels, not necessarily PDF viewer page numbers. Later printed labels are generally one lower than physical PDF page numbers. Confirm before editing.

## Overall conclusion
Not all issues are resolved. Presentation improved materially; core income, project inventory, eligibility, SSI, causal inference and legal-source discrepancies remain. Several additions explain unsupported numbers rather than supplying evidence. No corrected master report was produced in this turn.

## Completed review and improvements to preserve
1. Executive overview now says alternative affordability metric rather than revised affordability metric (p4).
2. Tract reference guide and Figure 1 map have been added (pp4–7). Accuracy remains unresolved.
3. Affordability figures now appear in Part 1 (pp12–13).
4. Supportive-housing chart now appears in Part 3, with explanatory footnote (pp29–30).
5. Monthly income headers changed to Annual Income Required (Family of 3) in accessibility tables (pp14–20). Numeric interpretation remains wrong.
6. Footnote 3 defines marketed affordable housing (p10).
7. High-income city neighborhoods and high-housing-cost adjustment are now discussed (p12).
8. CB9 advisory role and negotiation-baseline framing are explicit (p32).
9. Recommendations consolidated into Part 6 (pp41–45), though recommendations and inconsistent thresholds remain elsewhere.
10. Service matrix/311 explanatory notes and narrative summaries added (pp53–58).
11. The flawed claim that not being the most burdened district disproves oversaturation was replaced with a more careful comparative statement (p30).
12. 3333 Broadway and Montefiore examples have been replaced by PS 186 and Sunrose in the current tables; replacements introduce cross-reference and arithmetic errors.

## Comment reconciliation register
| Original issue | Status | Evidence / remaining work |
|---|---|---|
| Why revised? | Resolved wording | Alternative metric, p4. |
| Unclear findings 1–2 / standardized AMI testing | Partial | Methodology and footnotes added pp4,9–10, but unit-level data and valid derivation absent. |
| Tract map and findings visualizations | Partial | Figure 1 and Figures 2–8 exist; source geometry and plotted accuracy not certified. |
| Why Tract 219 / lowest income / tract-to-neighborhood comparison | Unresolved | Tract rationale added, but pp6 and18 disagree on tract income/poverty; p11/p39 still conflate tract and neighborhood. |
| Is Hamilton Heights Tract 221? | Unresolved | p6 says Tract 222 (Census Tract 221), Hamilton Heights; pp15–18 retain 221.01 in Manhattanville; p9 calls 221 Hamilton Heights. |
| Affordability-chart placement | Resolved placement | Part1 pp12–13. |
| 43.5% arrow and curve mismatch | Not verified | Caption changed p13; underlying data/annotation not visually or empirically validated. |
| Shortage underestimate / OSC-NYT scaling | Partial, not validated | New 450–500+/500-unit claims pp4,10,43; no citywide estimate, scaling formula or documented need denominator. |
| Basis for deeply affordable units needed | Unresolved | 400+,400–500,450–500+,500 coexist; 30% versus60% AMI need definitions change. |
| Meaning of marketed affordable | Resolved definition, flawed implication | Footnote p10; regional threshold is still presented as universal required income. |
| Executive-summary context | Improved | More structure, but long overview and repeated claims remain. |
| Affluent city neighborhoods affecting AMI | Addressed narratively | p12; full geography/vintage verification still required. |
| Three-person AMI vs all-household income | Unresolved | Direct comparison and $81,102/125.4% persist pp12–13; no size-matched recalculation. |
| Chart appears closer to18% | Not verified | Need original comment anchor and visual inspection/source data. |
| Chart source | Partial | Broad DHS/HPD/Comptroller footnote p29, no extract/table/version/numerator trail. |
| Supportive housing chart in section3 | Resolved placement | pp29–30. |
| Northern Manhattan district/tract reference map | Partial | CB9 map added; wider northern Manhattan geography not certified. |
| Define accessibility tables | Partial, incorrect | Notes added pp14–20; access increases with income thresholds and access/exclusion are reversed. |
| Monthly/yearly | Resolved labels | Annual headers, pp14–20. |
| Average tract median vs neighborhood median | Unresolved | $38,400 still average tract median p16, labeled median p21. |
| Why particular relevance / unclear what means | Not locatable precisely | Reviewer highlights unavailable; do not claim resolved without anchored passage. |
| Recommendations before analysis / consolidate | Partial | Dedicated Part6 added, but prescriptions remain within profiles and Part4. |
| Who recommendations are for | Largely addressed | CB9 advisory/negotiation role p32; authoritative approval/mandate language still appears elsewhere. |
| Why only one neighborhood broken into tracts | Addressed form, not data | All three have tract analyses pp15–21, but these conflict with reference guide. |
| CB9 median exceeds neighborhood figures | Unresolved | Original figures survive p21; new guide adds incompatible high incomes rather than reconciling distributions. |
| Policy recommendation basis | Partial | Rationale added pp33–35; inputs/precedents not source-verified. |
| Project selection/completeness | Unresolved | Repeated 12-project claim; nine visible inventory rows; no inclusion/exclusion protocol. |
| Project introductions | Partial | No consistent source-backed paragraph per project before comparison. |
| 1727 Amsterdam has200 apartments | Unresolved, externally contradicted | Still215/occupied2024; official Dec2025 proposal says approximately200. |
| 3333 Broadway already built | Removed example | No longer present in current extracted text; replacement rows need independent verification. |
| Policy flaw definition / sparse data | Unresolved | pp24–25 retains inference without valid eligibility/project evidence. |
| Morningside Gardens is cooperative / wrong counts | Unresolved |142 renovation units and public-housing description persist pp14,25. No project-specific preservation record. |
| Other incorrect project numbers / sources | Unresolved | No row-level citations; aggregate sums fail. |
| Omit income descriptors | Not resolved | Extreme poverty, highest-income and other labels remain and conflict. |
| Basis for tract recommendations | Partial | Narrative expanded; no validated calibration/sensitivity or legal assessment. |
| Add cumulative line | Not verified | Need inspect Figure7 directly; do not sum beds and units without a valid common metric. |
| Not-most-burdened does not disprove saturation | Addressed narrowly | p30 revised. General saturation claims still unsupported by validated capacity/need. |
| Causal vs relational | Partial | Appendix B softens wording, but p22/31/48/58 still asserts causal mechanisms and suppressed demand. |
| Incomplete/misclassified service list | Unresolved | Phone services, recreation and arts still mixed with licensed clinical providers; no complete verified directory. |
| Explain service/311 charts | Addressed presentation | Footnotes9–11 added; interpretations still exceed evidence. |
| Narrative alongside bullets | Addressed presentation | Expanded summaries and explanatory prose. |

## Priority discrepancies with exact evidence

### 1. Contradictory income and geography universes
- CB9 $64,698 pp12,21 vs $45,700 p7.
- Tract219 $20,912 and43.8% poverty p6 vs $17,584 and~62% poverty p18.
- Tract209.01 $28,015 p6 vs $22,183 p15 vs ~$56,580 p27/35.
- Tract211 $79,522 p6 vs $49,431 p15.
- Tract233 $83,232 p7 vs $51,656 p20.
- Tract225 $58,015 p6 vs $35,566 p18.
- Tract229 $59,145 p6 vs $24,806 p19.
- Tract205 $208,500 called highest-income p5; tract231.01 ~$79,713 called highest-income in CB9 p20.
- Tract222/221/221.01 not reconciled; split/unsplit IDs used interchangeably.
- Reference guide contains tracts absent from old neighborhood profile lists.
- Morningside median $56,580 but50% under$48,000; Hamilton median$62,100 but50% under$48,800. If same universe/year, inconsistent.
- Morningside summary poorest tract median$56,580 contradicts its own lower tract values.

Action: one source-controlled ACS table with GEOID, vintage, universe, estimate, MOE and neighborhood crosswalk; update all dependent text/figures. Never average medians to claim a pooled median. A household-weighted average of medians also does not recover a pooled median. Earlier assistant defense using high-income outliers was not valid evidence.

### 2. AMI table logic
- AMI benchmark does not automatically equal the minimum qualifying income. Need project-specific rent, household size, occupancy, utilities, voucher and eligibility rules.
- Morningside access18%,38%,42%,58%,14% as thresholds rise is incompatible with its own definition of share meeting or exceeding a threshold.
- Tract219 table calls94/98/99% access; footnote calls same values exclusion (p16).
- Tract221/Hamilton access also rises with threshold.
- 2024 and2025 baselines and different household sizes are mixed. p34 uses50%AMI~$47,750 family4 and60%~$57,300; p35 bases ratio on yet another baseline.
- 23% below60%AMI claim persists p10. $17,584/$87,480 is about20.1%, i.e.79.9% below, not23% below.
- 353% variance is not valid label for62,100 vs17,584: ratio~3.53, percentage increase~253%.
- $81,102 is the difference145,800−64,698, not a demonstrated average across12 projects (p4).
- Official NYCHA2025 table confirms145,800 three-person100%,87,48060%;30%=43,750 and80%=116,650 (rounded official limits), rather than43,740/116,640 obtained by simple multiplication.

### 3. Current pipeline arithmetic: DO NOT reuse older handoff totals
Current active rows (as printed, unverified project facts):
|Project|Total|Affordable|
|---|---:|---:|
|1727 Amsterdam|215|215|
|ANCP Morningside|42|42|
|PS186|79|79|
|Sunrose Tower|238|72|
|Columbia Manhattanville|230|92|
|2975 Broadway|220|88|
|Harlem Commons|165|66|

- Active seven rows sum1189 total,654 affordable,535 remaining.
- Completed two rows GeneralGrant382 and MorningsideGardens142 sum524/524.
- All nine rows sum1713 total,1178 affordable,535 remaining.
- Report aggregate remains1226/749/439deep/310workforce/477market/195supportive (p26), despite project substitutions.
- Five-project subset p23 sums804total/500affordable correctly; its215deep total not validated because exact PS186 band allocations are missing.
- Tract219 listed215+238+230=683, not595;315deep and52.9% inherited from superseded projects.
- Sunrose tract219 in p26 inventory versus tract221 p27, where included under tract219 heading.
- PS186 completed2016 p23/27 but proposed inside active2021–26 table p26; support/opposition inconsistent pp26,33,35.
- Sunrose supported p26 but opposed pp23,33–34.
- 195supportive has no unit-level derivation; only130 asserted at1727.
- Deep affordability and supportive status overlap; do not subtract supportive automatically.
- Regulated units can be above100%AMI (PS186 up to165%,Sunrose130%); >100%AMI does not imply market-rate.
- Exactly60%AMI appears in both≤60 and60–100 categories; make intervals disjoint.
- Correcting table sums does not validate underlying projects or create valid replacement policy statistics.

### 4. SSI formulas fail to reproduce scores
Main formula pp36–37:
SSI_i=(0.4*(MH_i/MH_bar)+0.4*(SH_i/SH_bar)+0.2*(FP_i/FP_bar))*100
Appendix p54 formula:
(MH+2*SH+FP)/(CB9 counterpart)*100
R7 pp42–43 instead invokes income,tax revenue and citywide reference.
Using printed matrix MHbar4.4,SHbar9.7,FPbar1.0:
|Tract|Reported|Main formula|Appendix formula|
|---|---:|---:|---:|
|219|137|179.25|188.71|
|221|42|44.18|15.73|
|209|58|92.29|73.79|
|231|35|44.88|28.23|
Not a rounding issue. Need one metric, validated raw sites/capacity and denominator; distinguish above-average density from measured overload. District SH18.62 p29 conflicts with9.7 matrix CB9 average if intended same universe/date. p37 says>100 over-saturation but table100–120 balanced.137 leads both conditional opposition and outright oppose. Executive conditional support conflicts with de-facto moratorium p41.

### 5. Audit/legal claims: new consequential discrepancies
Authoritative audit MD22-101A defines BTP as BEDS-TO-POPULATION, not Below the Poverty Line.
Revised report pp30–31,44–45,48 repeatedly misdefines BTP and builds unsupported specific claims on it.
Actual audit:
- Scope FY2018–2022.
-74% of230 sitings not independently reviewed (170Article9 vs60ULURP/Section195).
-40% of170Article9 sitings in high-BTP districts.
-28 detailed statements sampled;18 sitings in high-BTP districts; ManhattanCD9 included among several districts.
-2015 BTP baseline, not2016 vulnerability index.
-Does not support report's claimed73%below-median-income placement,38%197-a bypass,6CB9 instances,94:1wealth disparity or top-five CB9 poverty-facility rank as presented.
-94%fewer is not94:1.
-Audit distinguishes ULURP/Section197-c,Section195 andArticle9; report's197-a60-day entitlement should not be repeated without primary legal verification.
-Do not turn unequal density or this audit into automatic tract-specific illegality/moratorium power.
-Check new cost/CBA precedents ($150/unit,$500–1000/unit) against actual documents; prose explanations without citations are not validation.

### 6. Other arithmetic and inference
-18.62/1.24=15.02, not53times CB8 (p30).18.62/1.63=11.42 forCB7; footnote roughly11times both districts imprecise.
-350%of average is250%above, not350%above.
-12mental-health sites in population5400 would be2.22/1000, not8.2; investigate site-universe mismatch.
-130supportive units in tract population5400 already imply24.07/1000 if located there, exceeding18.6 asserted tract rate.
-SSI/needs claims confuse service presence with harm, capacity, utilization and unmet demand.
-311 footnote p58 says CB9 has four census tracts, contradicting reference guide; four counts94+54+59+40=247 cover full district total without a documented complete geography filter.
-311 service scarcity as cause of low requests is untested, not established hidden demand.
-Claims of partnerships, retention85%vs60%,waitlists,850monthly callers,34%housing referrals,287annual outcomes need primary data.

## Verified external evidence and URLs
1. Comptroller official full audit (read during audit):
https://comptroller.nyc.gov/reports/audit-report-on-new-york-citys-compliance-with-fair-share/
Confirms BTP meaning and above actual findings; November9,2023,MD22-101A. Search metadata update dates are not original publication dates.
2. Manhattan Borough President announcement December11,2025:
https://www.manhattanbp.nyc.gov/manhattan-bp-recommends-the-approval-of-1727-amsterdam-avenue-an-affordable-and-supportive-housing-project/
Approximately200units; proposed project, inconsistent with215occupied2024.
3. Official BP recommendation December10,2025:
https://www.manhattanbp.nyc.gov/wp-content/uploads/2025/12/MBP-Levine-Recommendation-1727-Amsterdam-2025-12-10.pdf
C260071HAM; approximately200units; site Block2060Lot1.
4. Operator project page (search evidence):
https://www.brc.org/hilltopapartments
Approximately200apartments plus superintendent; proposed redevelopment. Need verify whether published200includes superintendent before fixing exact master count.
5. Official NYCHA2025 income table (read):
https://home4.nyc.gov/site/nycha/residents/pay-rent.page
Household-size-specific limits as above. Do not replace historical2025limits with2026 just because live HPD page updated.
6. HPD AMI page:
https://www.nyc.gov/site/hpd/services-and-information/area-median-income.page
7. HUD methodology/data:
https://www.huduser.gov/portal/datasets/il.html

Report-listed sources NOT validated for all individual figures:
https://censusreporter.org/profiles/79500US3604109/
https://datacommons.org/
https://furmancenter.org/neighborhoods/view/morningside-heights-hamilton
https://data.cityofnewyork.us/Housing-Development/Affordable-Housing-Production-by-Building/hg8x-zxpr
https://www.nyhc.org/tracker/
https://communityprofiles.planning.nyc.gov/manhattan/9
https://mentalhealth.cityofnewyork.us/dashboard/
https://a816-health.nyc.gov/hdi/profiles/
https://data.cityofnewyork.us/api/views/erm2-nwe9/

## Files generated in this audit
- cb9_cursor_handoff_audit.md: this handoff.
- cb9_pipeline_transcription_audit.csv: seven current active rows, exactly as printed, not validated project facts.
- cb9_ssi_recalculation_audit.csv: both SSI formulations evaluated on printed matrix.
No original PDF was modified. No updated DOCX/source design file supplied for59pagePDF.

## Technical implementation
Python pypdf and pandas used. Extraction:
```python
from pypdf import PdfReader
r = PdfReader('cb9-housing-analysis.pdf')
texts = [p.extract_text() or '' for p in r.pages]
```
pypdf emitted `Ignoring wrong pointing object 303 0 (offset 0)` but all59pages extracted. No chart geometry validation performed. No repository, app architecture or pinned dependencies established. Earlier image-generator maps are not GIS evidence.

## Exact next action for Cursor
Create a source-controlled audit workbook BEFORE revising prose:
1. Extract all59pages into page-indexed text and visually inspect Figures1–8.
2. Create issues.csv with issue_id,printed_page,quote,status,evidence,dependency,proposed_fix.
3. First remove/correct the BTP misdefinition and unsupported audit-specific claims, using actual MD22-101A text; label policies as proposals, not adopted CB9 positions unless resolutions supplied.
4. Build verified tract_income.csv (GEOID,vintage,universe,estimate,MOE,source) and projects.csv (ID,BBL,address,geography,status,date,new/preserved,total,regulated,AMI-band counts,supportive count,source).
5. Mark all unresolved headline numbers provisional. Do not choose between conflicting values without evidence.
6. Regenerate aggregates,accessibility outputs,SSI and figures from those tables; no hard-coded summary totals.
7. Propagate updates into executive summary,body,appendix,policy thresholds and conclusion; run consistency checks.
8. Return a comment-by-comment resolution register plus proposed corrected text for remaining issues.

## Acceptance criteria
- Each numerical claim has a retrievable source and explicit universe/date.
- All repeated values consistent or explicitly different with rationale.
- Project totals equal included rows; completed/preserved/proposed separated.
- SSI exactly reproduces displayed scores and sensitivity is disclosed.
- Eligibility not inferred from meeting/exceeding AMI ceiling.
- No unsupported causal/legal claims or fabricated CBA precedents.
- Map boundaries and identifiers reconciled; all plots visually inspected.
- Unknown reviewer highlights remain not verified rather than incorrectly closed.
