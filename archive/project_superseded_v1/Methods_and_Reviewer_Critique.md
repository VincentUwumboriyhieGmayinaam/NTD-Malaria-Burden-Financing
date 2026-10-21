# Global spatial and economic analysis of NTD burden under development-assistance cuts
## Statistical methods and anticipated reviewer critique (Step 2)

### 1. Study design
This is an ecological, multi-source, country-level study covering 204 countries and territories grouped into the 7 GBD super-regions. Its components are: (i) descriptive epidemiology; (ii) inequality and spatial analysis; (iii) regression of burden on health-system and financing determinants, allowing the associations to differ by super-region; (iv) scenario modelling of external funding cuts. The analysis follows GATHER (Guidelines for Accurate and Transparent Health Estimates Reporting) and RECORD (Reporting of studies Conducted using Observational Routinely-collected Data), as applicable to secondary analyses of modelled estimates.

### 2. Outcomes
- **NTDs excluding malaria:** the sum of the 19 GBD 2023 Level-3 NTD causes. Leishmaniasis and intestinal nematode infections are entered at Level 3, so their sub-causes are not double counted. Age-standardised rates are additive across mutually exclusive causes, because all GBD causes share the same standard population. Additivity was verified: the NTD and malaria aggregate minus the components is 0.000% for counts (audit A1).
- **Malaria:** analysed separately. Its burden is 2.7 times that of all other NTDs combined and would otherwise dominate any pooled estimate.
- **Metrics:** DALYs as age-standardised rates per 100,000 (for comparisons) and all-age counts (for magnitude), each with the 95% uncertainty intervals (UIs) published by GBD.

### 3. Exposures and covariates
- **SDI, UHC effective-coverage index and lag-distributed income (LDI):** from the GBD 2023 covariates.
- **From the World Bank WDI:** current health expenditure (CHE), its external, domestic-government and out-of-pocket shares, ODA, basic water and sanitation, and rural population share. The latest value for 2019–2023 is used, i.e. before the 2025 cuts.
- **Independent outcome:** people requiring interventions against NTDs (WHO-reported SDG indicator 3.3.5).

### 4. Analyses
1. **Descriptive analysis.** Burden by super-region and by cause, a cause × super-region concentration matrix, and the GBD-published % change for 2010–2023 with uncertainty intervals.
2. **Inequality.**
   - A population-weighted concentration index, with countries ranked by SDI and a 2,000-replicate bootstrap.
   - A population-weighted Theil T index, decomposed into between- and within-super-region components.
3. **Spatial analysis.**
   - Global Moran's I and local indicators of spatial association (LISA), using row-standardised k = 6 nearest-neighbour weights on country representative points in the Robinson projection, with 9,999 permutations.
   - LISA clusters are additionally reported after false-discovery-rate adjustment.
4. **Determinants and heterogeneity.**
   - Log-linear OLS with super-region fixed effects, standardised predictors (% change per 1 SD) and HC3 robust standard errors.
   - A maximum-likelihood spatial error model as a robustness check.
   - Super-region × external-share interactions, with a likelihood-ratio test of slope heterogeneity.
   - A linear mixed model with random intercepts and random slopes by super-region.
5. **Funding-cut scenarios (the "gains-at-risk" model).**
   - Formula: Excess DALYs_c = max(0, ASR_2010 − ASR_2023)/10⁵ × population × external share of CHE × cut fraction.
   - Cut fractions: mild 5–15%; reference 19–26%, which brackets IHME's preliminary 2024–2025 fall in development assistance for health of 22.6%; severe 40–60%.
   - Uncertainty: 2,000 Monte Carlo draws, sampling lognormally within GBD UIs and uniformly across the cut range.
   - Economic value at 1× GDP per capita per DALY, with 0.5× and 3× as sensitivity bounds.
   - Domestic financing gap: lost external funds as a percentage of domestic general-government health expenditure.

### 5. Self-critique: anticipated reviewer comments and how each is addressed

| # | Likely reviewer comment | How addressed | Where |
|---|---|---|---|
| R1 | "Ecological fallacy; associations are not causal." | All regression results are framed as associations. A first-difference panel model (2010–2023) was also estimated. It gave a null, imprecise elasticity, so causal elasticities were **not** used to project effects. | Table 2 note; Table S11 |
| R2 | "GBD outcomes are modelled partly *from* income and SDI covariates, so regressing them on LDI or SDI is circular." | Re-estimated with SDI in place of LDI and UHC. Repeated with an independent WHO-reported outcome (SDG 3.3.5, people requiring NTD interventions). | Table S7 (S2 rows) |
| R3 | "Countries are spatially dependent; OLS standard errors are wrong." | Moran's I of the OLS residuals was tested. A spatial error model gave the same direction and size of effect. | Table 2; audit A2 |
| R4 | "Results depend on the choice of spatial weights." | Moran's I was recomputed with k = 4, 6 and 8 neighbours and with 2,500 km inverse-distance bands. I ranged from 0.66 to 0.74 for NTDs and from 0.73 to 0.82 for malaria, all with p < .001. | Table S5 |
| R5 | "Multiple testing in LISA." | Reported FDR-adjusted classifications alongside the unadjusted ones. | Data file; Table S12 note |
| R6 | "Heterogeneity is driven by South Asia (n = 5) and high-income outliers." | The likelihood-ratio test was repeated excluding South Asia, and excluding both South Asia and high-income. A leave-one-super-region-out analysis was also run. A mixed model shrinks the small-group slopes. | Audit A3, A7; Table S6 |
| R7 | "GBD estimates carry uncertainty that the regressions ignore." | Fitted an inverse-variance-weighted regression using the GBD UIs. | Audit A4 |
| R8 | "Collinearity between income, UHC, WASH and spending." | Computed variance inflation factors (VIFs). Standardised coefficients are interpreted jointly, and SDI was used as an alternative specification. | Audit A5 |
| R9 | "The scenario assumes gains are proportional to the donor share of total health spending. Mass drug administration is far more donor-dependent than that." | This makes the main estimate conservative. An upper-bound scenario sets donor attribution to at least 80% in the 32 US NTD Program countries. | Table S7 (S4 rows) |
| R10 | "Monte Carlo draws for 2010 and 2023 are treated as independent." | Independent draws only widen the UI; the median is unchanged. Re-run with draw correlation ρ = 0.8. | Audit A6 |
| R11 | "Valuing a DALY at GDP per capita is contested." | Reported 0.5×, 1× and 3× GDP per capita, and also reported the DALYs themselves without valuation. | Table S7 (S5 rows) |
| R12 | "Missing data: are complete cases representative?" | 169 of 204 countries were analysed. They hold 98.3% of global NTD DALYs. The excluded countries are listed. | Table S13 |
| R13 | "Timing: the scenario implies an instant rebound." | Results are labelled as steady-state annual DALYs once gains erode, not first-year effects. Resurgence dynamics are named as a limitation and a priority for transmission modelling. | Table 3 note; Limitations |
| R14 | "Unmeasured donor targeting: aid flows to high-burden settings, which biases associations." | The external-share association is consistently *negative* (more donor share, lower conditional burden). This holds with exposure lagged to 2010–2014, excluding sub-Saharan Africa, and excluding high-income countries. Because aid is targeted towards *higher*-burden settings, targeting would push the coefficient towards zero, so it cannot produce a negative association on its own. | Table S7 |
| R15 | "No NTD-specific donor funding by country." | Acknowledged. External share of CHE is a proxy. The IHME DAH database (NTD programme area) can replace it when available. | Limitations |
| R16 | "WHO GHO data not used directly." | The GHO API was unavailable (HTTP 502) on the access date. The same WHO indicators were taken from the UN SDG database. | Table S1 note |

### 6. Limitations to state in the Discussion
Ecological design. GBD estimates are modelled, and their covariate dependence is checked only partly. NTD-specific DAH at country level was unavailable, so external share of CHE is a proxy. The scenario model is an accounting attribution, not a transmission-dynamic model. There is no explicit time path to resurgence. CHE in current US$ is affected by exchange rates. Small-n super-regions limit precision.
