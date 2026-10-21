# Global, regional and national inequalities in NTD and malaria burden and the consequences of development-assistance cuts

Spatial, inequality and panel-econometric analysis of GBD 2023 disability-adjusted life-years (DALYs) for neglected tropical diseases (NTDs) and malaria in 204 countries and territories, 1990–2023, with scenario projections of the 2025 cuts in development assistance for health.

Authors: Gmayinaam VU, Nortey AN, Dzissem PE, Immurana M, Manyeh AK. Centre for Neglected Tropical Diseases, University of Health and Allied Sciences, Ho, Ghana.

> Status: manuscript in preparation (version 2, 21 Oct 2026). Do not cite the results until the paper is published.

## Repository layout

| Folder | Contents |
|---|---|
| `manuscript/` | `Manuscript_V2_tracked_changes.docx` (revisions as tracked changes), `Manuscript_V2_clean.docx/.pdf` (changes accepted), `Supplementary_Appendix.docx/.pdf`, `Tables_Main_APA.docx`, `Tables_Supplementary_APA.docx`, `Methods_Audit_and_Reviewer_Responses.docx`, original V1 manuscript |
| `manuscript/source/` | inputs used to assemble the appendix and the tracked revision |
| `figures/main/` | Figures 1–8 (PDF and SVG vector; PNG and TIFF at 600 dpi; 180 mm width) |
| `figures/supplementary/` | Figures S1–S4 |
| `results/` | every numeric output (CSV/JSON); `tables.json` feeds all APA tables; `rev_*` files are the revision analyses |
| `scripts/` | analysis pipeline (run from the repository root) |
| `scripts/tools/` | helpers for tracked-change editing of the Word manuscript |
| `data/raw/` | source extracts: GBD 2023, World Bank WDI, WHO/UN SDG, funding facts, Natural Earth boundaries |
| `data/processed/` | analysis datasets built from `data/raw/` |
| `literature/` | evidence review: search strategy, screening counts, 44-study evidence table, references |
| `archive/` | superseded outputs kept for audit only; do not cite |

## Data sources
GBD 2023 (IHME); World Bank World Development Indicators (external, domestic and current health expenditure; WASH; population); WHO indicators via the UN SDG database (SDG 3.3.5 people requiring NTD interventions; SDG 3.3.3 malaria incidence); IHME Financing Global Health 2025; Natural Earth 1:50m boundaries. Access dates and codebook: see `data/README_DATA.md`.

## Running the analysis (from repository root)
1. Data assembly: `harvest_gbd.py`, `harvest_wb.py`, `harvest_panel.py`, `gbd_iso3.py`, `build_analysis_dataset.py`
2. Descriptives, inequality, spatial autocorrelation: `step2_analysis.py`, `step2_sensitivity.py`
3. Panel models: `step3_build_panel.py`, `step3_panel_models.py`, `step3_spatial_ml.py`, `step3_gwr.py`, `step3_combine_models.py`, `step3_preferred_full.py`
4. Missing data and spatial panels: `step4_missing_data.py`, `step4_spatial_panel_twoway.py`
5. Scenarios of funding cuts: `step3_scenarios_v2.py`
6. Revision analyses: `step5_revisions.py` (inequality 1990/2010/2023, 21 regions, YLD/YLL, national rankings, cause leaders, LISA over time, WHO triangulation), `step5_theil_regions.py`, `step5_mundlak_between_within.py`, `step5_mortality_sensitivity.py`
7. Figures: `fig1_workflow.py` … `fig8_scenarios.py`, `figS_revisions.py` (shared style in `vizstyle.py`)
8. Tables and appendix: `build_tables.py` → `render_tables.js`; `build_appendix_content.py` → `render_appendix.js`; `build_audit.py` → `render_audit.js`

Requirements: Python ≥3.11 (`requirements.txt`) and Node.js with `docx` 9.x for the Word outputs. Random seeds are fixed in each script.

## Key results (v2)
- 70.8 million NTD and malaria DALYs in 2023; 80.2% in sub-Saharan Africa and 63.1% in western and central sub-Saharan Africa.
- 1990–2023: absolute SDI gradient narrowed (NTD slope index −1966 to −632 DALYs per 100 000); relative concentration persisted (malaria concentration index −0.80 in 1990 and 2023).
- External financing share: −13.4% NTD rate per 10 percentage points between countries, −0.64% (95% CI −2.39 to 1.14) within countries.
- Reference 19–26% cut: 0.41 million excess NTD DALYs and 1.85 million excess malaria DALYs a year (accounting model).

## Licence and data attribution
- **Code** (`scripts/`): MIT License — see `LICENSE`.
- **Manuscript text, figures, tables and derived results** (`manuscript/`, `figures/`, `results/`): Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/. Please cite the article once published.
- **Third-party data** (`data/raw/`) are not covered by these licences and remain under their providers' terms:
  - Global Burden of Disease Study 2023 — Institute for Health Metrics and Evaluation (IHME), Seattle, WA. Used under the IHME Free-of-Charge Non-commercial User Agreement; cite: GBD 2023 Disease and Injury and Risk Factor Collaborators, *Lancet* 2025.
  - World Bank World Development Indicators — CC BY 4.0.
  - WHO indicators via the UN Global SDG Indicators Database — WHO / United Nations terms of use.
  - IHME Financing Global Health 2025 — Apeagyei et al., *Lancet* 2025 (IHME terms).
  - Natural Earth boundaries — public domain.
- Check the providers' terms before redistributing raw data; the repository is private until publication.
