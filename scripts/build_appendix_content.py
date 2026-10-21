"""Assemble the supplementary appendix content (methods text, GATHER checklist, evidence map, tables, figures) -> results/appendix.json"""
import json, re
O = json.load(open('manuscript/source/original_methods_paragraphs.json'))
T = json.load(open('results/tables.json'))
def fix(s, pairs):
    for a, b in pairs:
        if a not in s: raise ValueError('missing: ' + a[:60])
        s = s.replace(a, b)
    return s

M = []  # list of (heading, [paragraphs])
M.append(('3.1 Data sources, linkage and study populations', [
  O[1], O[3],
  O[7] + ' Inequality time series used all 204 locations, weighted by GBD population for 1990 and by population implied by GBD all-age counts divided by crude rates for 2010 and 2023.',
  'Countries were assigned to the 21 GBD regions using the GBD location hierarchy. Summed country DALY counts reproduced published regional totals to within 0.2% in 17 regions and within 1.5–4.2% in the Caribbean, Central Europe, Western Europe and Oceania, where GBD regional aggregates include locations without separate country estimates. In the linkage file, Finland carried the Natural Earth code for the Åland Islands (ALA); it was reassigned to Western Europe for regional analyses and to the Finland polygon for supplementary maps.',
  fix(O[13], [('These were retrieved through the UN SDG database after the WHO API returned server errors. ', 'These were retrieved through the UN SDG database. ')])]))
M.append(('3.2 Burden outcomes', [
  O[9],
  'For regional analyses we extracted, for each of the 21 GBD regions, 2023 all-age DALY counts with 95% UIs, all-age and age-standardised rates, and GBD-published percentage changes in age-standardised rates between 2010 and 2023, with UIs, for the NTD-and-malaria aggregate and for malaria. For the fatal and non-fatal composition, we extracted 2023 all-age YLDs and YLLs with UIs for each super-region and globally. NTD values excluding malaria were obtained by subtraction and carry no interval because GBD does not publish draws for that difference. Country-level age-standardised rates and counts for 1990 and 2010 supported the inequality time series and the national comparisons. GBD publishes country-level percentage changes with UIs only for the NTD-and-malaria aggregate; changes for NTDs excluding malaria and for malaria alone were computed from point estimates and are reported without intervals.']))
M.append(('3.3 Financing exposures and covariates', [O[11], O[24]]))
M.append(('3.4 Missing data', [O[15], O[16], O[17], O[18], O[19],
  fix(O[20], [('The supplied multiple-imputation implementation', 'The multiple-imputation implementation')]), O[21], O[22]]))
M.append(('3.5 Descriptive, regional and national analyses', [
  'We summarised 2023 all-age DALY counts, shares of global burden and age-standardised rates by super-region (Table 1), cause (Table S2), GBD region (Table S16) and country. Countries were ranked by age-standardised rate and by absolute count for NTDs excluding malaria and for malaria (Table S18), and for each of the 19 NTD causes we identified the country with the largest share of global DALYs, the three largest contributors and the country with the highest age-standardised rate (Table S20). Countries whose rates rose between 2010 and 2023 were identified in two ways: from GBD-published percentage changes with UIs for the NTD-and-malaria aggregate (classified as a significant increase or decrease when the UI excluded zero) and from point estimates for NTDs excluding malaria and for malaria, restricting malaria to countries with a 2010 rate above 1 per 100 000 (Table S19).']))
M.append(('3.6 Socioeconomic inequality', [
  fix(O[26], [('ranking countries from lowest to highest 2023 SDI', 'ranking countries from lowest to highest SDI in the same year (1990, 2010 and 2023)')]),
  'Absolute inequality was measured with the slope index of inequality (SII). Countries were ordered by SDI and each was assigned the midpoint of its cumulative population share (its fractional rank, from 0 to 1). The SII is the slope of a population-weighted linear regression of the age-standardised rate on this rank, which estimates the difference in rate between the hypothetical highest-SDI and lowest-SDI ends of the distribution; negative values indicate higher rates in low-SDI countries. The relative SII divides the SII by the population-weighted mean rate (Mackenbach & Kunst, 1997). The concentration index, the SII and the relative SII were estimated for 1990, 2010 and 2023. CIs used 2000 bootstrap resamples of countries. Changes between years were estimated by resampling countries jointly across years (paired bootstrap), so that each replicate compares the same set of countries; a change was considered distinguishable from zero when its 95% CI excluded zero (Table S15a; Figure S1).',
  O[27],
  'A nested Theil T decomposition used the GBD hierarchy to split total inequality into three additive parts: between the seven super-regions, between the 21 regions within super-regions, and between countries within regions. It was computed for 1990, 2010 and 2023 among countries with positive rates (Table S15b).']))
M.append(('3.7 Spatial autocorrelation', [O[29],
  'To assess persistence of clusters, global Moran’s I and local indicators were recomputed for 1990, 2010 and 2023 with the same weights and false-discovery-rate control, and countries entering or leaving high–high clusters between 2010 and 2023 were listed (Table S21; Figure S4).']))
M.append(('3.8 Panel econometric models', [O[31], O[32],
  'To present between-country and within-country associations side by side in the same sample, we fitted a correlated random-effects (Mundlak) model containing the time-varying exposure, its country mean, the five covariates and their country means, and year indicators, with country-clustered standard errors. The coefficient on the time-varying exposure is the within-country association; the sum of that coefficient and the coefficient on the country mean is the between-country association; the coefficient on the country mean tests whether the two differ (Table S23) (Bell & Jones, 2015; Mundlak, 1978).',
  'Because recent evaluations of development assistance report mortality, the preferred two-way fixed-effects model was re-estimated with the GBD 2023 age-standardised malaria death rate, on the log(1 + rate) scale, as outcome for the 77 malaria-endemic countries, with Driscoll–Kraay and country-clustered standard errors (Table S24).']))
M.append(('3.9 Spatial panel models', [O[35]]))
M.append(('3.10 Geographically weighted regression', [O[37]]))
M.append(('3.11 Predictive modelling', [O[39]]))
M.append(('3.12 Scenario models of development-assistance cuts', [
  fix(O[41], [('The original analysis used two conditional scenarios', 'We used two conditional scenarios'),
              ('Scenario estimates retained below, in Table 4 and in Figure 8 are provisional: the available data do not support the stated 19-cause NTD accounting calculation, and the malaria econometric conversion requires correction. ', '')]),
  fix(O[42], [('The accounting script summed', 'The accounting model summed'),
              ('Five 2010 NTD cause baselines were absent from the supplied extracts: other NTDs, yellow fever, Ebola, Guinea worm disease and Zika. The script replaced these missing values with near-zero counts. That substitution is unsupported, and the resulting NTD projections cannot be treated as validated estimates.',
               'All 19 NTD causes, including other NTDs, yellow fever, Ebola, Guinea worm disease and Zika, had GBD 2023 baselines for 2010; the 2010 sum of the 19 causes was 21.76 million DALYs.'),
              ('The econometric script recalculated', 'The econometric model recalculated'),
              ('For malaria, the outcome is log(1 + rate), so this proportional count conversion is only an approximation and must be replaced by an explicitly defined rate-scale calculation.',
               'For malaria, whose outcome is log(1 + rate), each draw computed the new value of (1 + age-standardised rate) by multiplying the baseline (1 + rate) by the exponentiated coefficient–exposure product, subtracted 1 to obtain the new rate, and applied the ratio of the new to the baseline rate to baseline all-age DALYs.')]),
  fix(O[43], [('The scenario code treated', 'We treated')])]))
M.append(('3.13 External triangulation with WHO surveillance series', [
  'GBD country estimates were compared with two WHO series obtained from the UN SDG database: the number of people requiring interventions against NTDs (SDG 3.3.5), expressed per 100 000 population, and malaria incidence per 1000 population at risk (SDG 3.3.3). Spearman rank correlations with GBD age-standardised DALY rates were computed for 2010 and 2023, for NTDs excluding malaria across all reporting countries and for malaria across endemic countries with non-zero values (Table S21). The comparison assesses agreement in the ordering of countries, not in absolute levels, because the measures differ in construct.']))
M.append(('3.14 Sensitivity analyses', [O[45] + ' Post-review analyses extended the panel to 2023, omitted UHC, excluded observations without matching UHC or income records and retained zero rates in the Theil decomposition (Table S22).']))
M.append(('3.15 Statistical software and reproducibility', [fix(O[47], [('The reproducible code cand be found on this GitHub repository.', 'Code is in the project GitHub repository [URL to be added].')]) +
  ' Revision analyses are in scripts step5_revisions.py (inequality over time, regions, YLD–YLL, national rankings, cause leaders, LISA over time, WHO triangulation), step5_theil_regions.py, step5_mundlak_between_within.py, step5_mortality_sensitivity.py and step3_scenarios_v2.py.']))

GATHER = [
 ('1', 'Define the indicators, populations and time periods for which estimates were made.', 'Main text, Methods; appendix 3.1–3.2'),
 ('2', 'List the funding sources for the work.', 'Main text, Funding'),
 ('3', 'Describe how the data were identified and accessed.', 'Main text, Methods; appendix 3.1; Table S1'),
 ('4', 'Specify the inclusion and exclusion criteria; identify all ad-hoc exclusions.', 'Appendix 3.1 and 3.4; Table S9'),
 ('5', 'Provide information on all included data sources and their main characteristics.', 'Table S1; Table S11'),
 ('6', 'Identify and describe any categories of input data that have potentially important biases.', 'Appendix 3.4; Tables S9–S10b'),
 ('7', 'Describe and give sources for any other data inputs.', 'Appendix 3.1, 3.3 and 3.13; Table S11'),
 ('8', 'Provide all data inputs in a file format from which data can be efficiently extracted.', 'Project repository (data/raw, data/processed)'),
 ('9', 'Provide a conceptual overview of the data analysis method.', 'Main text, Figure 1'),
 ('10', 'Provide a detailed description of all steps of the analysis, including mathematical formulae.', 'Appendix 3.1–3.15 (described in words)'),
 ('11', 'Describe how candidate models were evaluated and how the final model(s) were selected.', 'Appendix 3.8 and 3.11; Tables S3, S5'),
 ('12', 'Provide the results of an evaluation of model performance, if done, as well as sensitivity analyses.', 'Tables S5, S7, S10b, S12, S22–S24'),
 ('13', 'Describe methods for calculating uncertainty of the estimates.', 'Appendix 3.6, 3.8 and 3.12'),
 ('14', 'State how analytical or statistical source code can be accessed.', 'Appendix 3.15'),
 ('15', 'Provide published estimates in a file format from which data can be efficiently extracted.', 'Project repository (results)'),
 ('16', 'Report a quantitative measure of the uncertainty of the estimates.', 'Main text and Tables 1–4, S15–S24'),
 ('17', 'Interpret results in light of existing evidence; if updating previous estimates, explain changes.', 'Main text, Discussion'),
 ('18', 'Discuss limitations of the estimates, including changes in methods or data sources.', 'Main text, Discussion; Table S13'),
]

# Evidence map from the screening file
ev = open('literature/Evidence_table_full_screening.md').read()
rows = []
theme = {'A': 'A. Burden and trends', 'B': 'B. Inequality and spatial analyses', 'C': 'C. Financing and outcomes', 'D': 'D. Projections of funding cuts', 'E': 'E. Domestic financing, displacement and donor transition'}
cur = None
for line in ev.splitlines():
    if line.startswith('| ') and not line.startswith('| Theme') and not line.startswith('|---'):
        c = [x.strip() for x in line.split('|')][1:-1]
        th = c[0].split('/')[0].strip()
        if th != cur: rows.append({'group': theme[th]}); cur = th
        rows.append([re.sub(r'\*\*\[landmark national\]\*\*', '(national)', c[1]) + ', ' + c[2], c[3] + '; ' + c[4], c[5], c[6], c[8]])
EV = {'id': 'Table E1', 'title': 'Evidence Map: 44 Studies Prioritised From 76 Eligible Records, by Theme', 'cols': ['Study, journal', 'Design, data and scope', 'Key quantitative findings', 'Limitation relative to this study', 'DOI'],
      'rows': rows, 'widths': [2.0, 2.6, 3.6, 2.6, 1.8],
      'note': 'PubMed searched from inception to Oct 21, 2026 (six search strings; 767 records, 704 unique, 698 screened by title, 96 abstracts assessed, 76 eligible). Themes may overlap; studies are listed under their first theme. Values are as reported in each abstract.'}
other = ev[ev.find('The other 32 eligible'):]
m = re.search(r'Other eligible studies[^\n]*\n+([^\n#]+)', ev)
OTHER = None
for para in ev.split('\n\n'):
    if para.count('(') > 15 and re.search(r'\(\d{8}\)', para): OTHER = para.strip()
SEARCH = 'We searched PubMed from inception to Oct 21, 2026, without language restrictions, using six strings: (S1) NTD or malaria burden with Global Burden of Disease or DALYs; (S2) NTD or malaria with inequality, concentration index or slope index; (S3) NTD or malaria with spatial analysis, Moran’s I or hotspots; (S4) USAID, funding cuts or donor funding with NTDs, malaria or mortality, January 2024–October 2026; (S5) development assistance for health or official development assistance with NTD, malaria or child mortality; and (S6) domestic health financing, displacement or donor transition. The searches identified 767 records (S1 206; S2 29; S3 163; S4 99; S5 176; S6 94); after removal of 63 duplicates, 704 were unique and 698 could be retrieved and screened by title. We excluded 602 on title and 20 on abstract (commentaries without data, superseded analyses, out-of-scope designs), leaving 76 eligible studies. The 44 most relevant and recent, prioritised within five themes, are summarised in Table E1; two landmark national studies are flagged. WHO and IHME reports were reviewed for current indicator values. Supplementary targeted searches of Lancet journals for 2025–26 comment on the aid cuts identified commentaries and letters without primary data.'

FIGS = [
 ('Figure S1', 'FigureS1_inequality_over_time.png', 'Socioeconomic inequality in age-standardised DALY rates by SDI, 1990, 2010 and 2023', '(A) Concentration index with 95% bootstrap CI; negative values indicate concentration in low-SDI countries. (B) Slope index of inequality (SII), the modelled difference in DALYs per 100 000 between the highest-SDI and lowest-SDI ends of the distribution, with 95% CI. (C) Theil T; labels give the percentage of inequality between super-regions. Countries weighted by population and ranked by SDI of the same year (n = 204). Absolute gaps narrowed while relative concentration of malaria was unchanged.'),
 ('Figure S2', 'FigureS2_gbd_regions.png', 'Burden and change in the 21 GBD regions', '(A) Age-standardised DALY rate per 100 000 in 2023 for NTDs excluding malaria and for malaria (log scale; regions grouped by super-region; sub-Saharan African regions in bold). (B) Share of global combined NTD-and-malaria DALYs. (C) GBD-published percentage change in age-standardised rate, 2010–2023, with 95% UI, for the NTD-and-malaria aggregate and for malaria; × marks regions where malaria burden fell to zero.'),
 ('Figure S3', 'FigureS3_yld_yll.png', 'Years lived with disability and years of life lost as shares of DALYs, 2023', 'Coloured segments show the YLD share of DALYs for (A) NTDs excluding malaria and (B) malaria, by super-region; grey segments show YLLs. Totals are all-age DALYs. Most NTD burden is disability, whereas malaria burden is almost entirely premature death.'),
 ('Figure S4', 'FigureS4_lisa_2010_2023.png', 'Local spatial clusters of age-standardised DALY rates, 2010 and 2023', 'Local indicators of spatial association on log(1 + rate) with six-nearest-neighbour weights, 9999 permutations and Benjamini–Hochberg false-discovery rate below 5%. Black outlines mark countries that entered a high–high cluster between 2010 and 2023.'),
]
json.dump({'methods': M, 'gather': GATHER, 'evidence': EV, 'search': SEARCH, 'other': OTHER,
           'tables': [t for t in T if not t.get('main')], 'figures': FIGS}, open('results/appendix.json', 'w'), ensure_ascii=False, indent=1)
print('methods words', sum(len(p.split()) for _, ps in M for p in ps), 'tables', len([t for t in T if not t.get('main')]), 'evidence rows', len(rows), 'other found', OTHER is not None)
