# NTD spatial-economic study — Step 1 data inventory

Accessed 7 Oct 2026. All scripts in `scripts/` reproduce processed files from `data/raw/`.

## Sources
- **GBD 2023** (IHME) via GBD 2023 database: 21 NTD causes + malaria, 204 countries, DALYs/deaths/prevalence, 1990-2023; SDI, UHC, LDI covariates; published % change with UIs.
- **World Bank WDI** API (24 indicators, 2005-2024): GDP/GNI pc, health expenditure (CHE, domestic govt, external, OOP), ODA, population, WASH, poverty, malaria incidence.
- **Funding**: IHME FGH 2025 (Apeagyei et al., Lancet 2025, doi:10.1016/S0140-6736(25)01240-1); KFF; NPR; WHO (4 Jun 2025); USAID NTD Program country list.
- **Boundaries**: Natural Earth 1:50m admin-0.
- **WHO via UN SDG database**: SDG 3.3.5 people requiring interventions against NTDs (2010-2024, 194 countries) and 3.3.3 malaria incidence per 1000 at risk. WHO GHO API itself returned 502 errors on 7 Oct 2026.

## Files
| file | content |
|---|---|
| data/processed/analysis_country_2023.csv | 204 countries x 110 variables (main analysis file) |
| data/processed/gbd_country_burden_long.csv | long-format GBD burden (cause x measure x year) |
| data/processed/gbd_superregion_trends.csv | super-region + global annual trends 1990-2023 |
| data/processed/wb_country_year_wide.csv | WDI country-year panel 2005-2024 |
| data/processed/gbd_locations_iso3.csv | GBD location-ISO3 crosswalk |
| data/raw/funding/*.csv | funding facts + USAID NTD countries |

## Codebook (main file)
| variable | definition |
|---|---|
| `location_id` | GBD location id |
| `location_name` | GBD location name |
| `super_region_name` | GBD super-region (7) |
| `iso3` | ISO3 code |
| `daly_asr_*` | Age-standardised DALY rate per 100,000, GBD 2023 (cause suffix); _lo/_hi = 95% UI |
| `daly_n_*` | All-age DALY count, GBD 2023 |
| `daly_asr_ntd_excl_malaria` | Sum of 19 NTD cause age-std DALY rates (additive across mutually exclusive causes) |
| `deaths_*/prevalence_*` | GBD 2023 deaths / prevalence (age-std rate, count) |
| `daly_asr_<cause>_<year>` | Age-std DALY rate in 1990/2000/2010/2019 |
| `daly_asr_ntd_core14_2010/2023` | Sum of 14 NTDs with 2010 estimates (comparable change) |
| `pc_asr_ntdm_2010_2023` | GBD-published % change in age-std DALY rate (NTDs & malaria) 2010-2023 with 95% UI; _sig = direction established |
| `sdi_2023/2010` | GBD Socio-demographic Index |
| `uhc_*` | GBD UHC effective coverage index (0-100) |
| `ldi_*` | GBD lag-distributed income per capita (I$) |
| `*_latest` | World Bank WDI latest value 2019-2023 |
| `*_2010_14` | WDI mean 2010-2014 |
| `ext_pct_che` | External health expenditure, % of current health expenditure (SH.XPD.EHEX.CH.ZS) |
| `ghed_pct_che` | Domestic general government health expenditure, % CHE |
| `oop_pct_che` | Out-of-pocket, % CHE |
| `che_pc_usd` | Current health expenditure per capita, US$ |
| `oda_pc_usd` | Net ODA received per capita, US$ |
| `water_basic_pct/sanit_basic_pct/open_defec_pct` | WASH coverage (WDI/JMP) |
| `wb_income` | World Bank income group |
| `usaid_ntd_program` | 1 = country listed by USAID NTD Program (neglecteddiseases.gov) |
| `ntd_endemic_flag` | 1 = NTD (excl malaria) age-std DALY rate above 25th percentile |
| `ppl_req_ntd_interv_<yr>` / `ppl_req_ntd_pct_pop_2023` | WHO-reported people requiring NTD interventions (SDG 3.3.5), count and % of population |
