"""Tracked revision of the manuscript to a Lancet-length article (~4500 words main text).
Whole-paragraph rewrites are tracked as deletion + insertion (author 'Claude'); material removed from the
main text is carried in the appendix."""
import sys, re; sys.path.insert(0, '/home/claude/ntd/scripts')
from tc_lib import *
from lxml import etree
P = '/home/claude/ntd/manuscript/tc/un/word/document.xml'
tree = etree.parse(P); body = tree.find('.//w:body', ns)
def dtext(p): return ''.join(t.text or '' for r in p if r.tag == q('r') for t in r.findall('w:t', ns))
def find(start, contains=None):
    hits = [p for p in body.iter(q('p')) if dtext(p).startswith(start) and (contains is None or contains in dtext(p))]
    if len(hits) != 1: raise ValueError(f'{len(hits)} hits for {start!r}')
    return hits[0]
def rewrite(p, new, keep_prefix=''):
    full = dtext(p); old = full[len(keep_prefix):]
    replace(p, old, new) if old else None
def drop(*starts):
    for s in starts: delete_par(find(s))
TPL_BODY = find('Control of neglected tropical diseases'); TPL_H1 = find('Introduction'); TPL_H2 = find('Study design')
def rename(start, new): p = find(start); replace(p, dtext(p), new)

# =========================== SUMMARY (≤300 words) ===========================
rewrite(find('BackgroundNeglected'), 'Neglected tropical diseases (NTDs) and malaria are concentrated in countries that depend heavily on external health financing, which fell by about a fifth in 2025. We quantified how this burden is distributed, how socioeconomic inequality in it changed, and the health losses that financing cuts could cause.', 'Background')
rewrite(find('MethodsWe conducted'), 'We analysed Global Burden of Disease (GBD) 2023 disability-adjusted life-years (DALYs) for 204 countries and territories, 1990–2023, by super-region, region and country. We measured spatial clustering, absolute and relative inequality by Socio-demographic Index (SDI) and Theil decomposition. Panel models for 153 low- and middle-income countries, 2007–2022, related external financing share to DALY rates; two scenario models projected excess DALYs under 5–60% cuts.', 'Methods')
rewrite(find('FindingsIn 2023'), 'In 2023, NTDs and malaria caused 70.8 million DALYs (51.6 million from malaria). Sub-Saharan Africa had 15.1% of the world population but 80.2% of these DALYs; western and central sub-Saharan Africa alone had 63.1%. Age-standardised rates fell 21.6% (95% UI 7.8–36.3) from 2010. The absolute SDI gap narrowed (NTD slope index of inequality −1966 to −632 DALYs per 100 000, 1990–2023), but relative concentration in low-SDI countries persisted (malaria concentration index −0.80 in both years). Disability accounted for 62.4% of NTD DALYs. A 10-percentage-point higher external share was associated with a 13.4% (95% CI 6.4–20.0) lower NTD rate between countries but not within countries (−0.64%, −2.39 to 1.14). A 19–26% cut projected 0.41 million (95% UI 0.33–0.50) excess NTD and 1.85 million (1.51–2.21) excess malaria DALYs a year, over 90% in sub-Saharan Africa.', 'Findings')
rewrite(find('InterpretationDespite'), 'Falling averages have not moved burden away from the poorest, most donor-dependent countries, where projected losses also concentrate. Protecting service continuity there is a priority; the projections are conditional scenarios, not causal estimates.', 'Interpretation')

# =========================== RESEARCH IN CONTEXT ===========================
fund = find('FundingThis study')
x = new_par_after(fund, '', template=TPL_H1, runs=[('Research in context', None, None)])
x = new_par_after(x, '', template=TPL_BODY, runs=[('Evidence before this study', True, None)])
x = new_par_after(x, 'We searched PubMed from inception to Oct 21, 2026, without language restrictions, for studies of NTD or malaria burden, inequality, spatial analysis, development assistance for health and funding cuts, and reviewed WHO and IHME reports; 76 of 704 unique records were eligible (appendix). GBD 2019 and 2021 analyses showed combined NTD and malaria DALYs falling by about 18% between 1990 and 2021, with burden concentrating in low-SDI countries and relative inequality widening as absolute inequality narrowed. None used GBD 2023, tested geographical clustering, or decomposed inequality between and within regions. Cross-country panels associated aid volume with lower malaria, NTD and child mortality and projected 14–23 million additional deaths by 2030 from current cuts, but none separated between-country from within-country associations, examined dependence on external financing, or estimated NTD DALYs under the cuts.', template=TPL_BODY)
x = new_par_after(x, '', template=TPL_BODY, runs=[('Added value of this study', True, None)])
x = new_par_after(x, 'Using GBD 2023, we show that 63.1% of global NTD and malaria DALYs occur in western and central sub-Saharan Africa, that burden hot spots were unchanged between 2010 and 2023, and that the absolute socioeconomic gap narrowed while relative concentration in the poorest countries did not. Most NTD burden is disability, which mortality-based evaluations omit. Thirty-four countries combining high NTD burden and high donor dependence hold over half of malaria DALYs. The association of external financing with NTD burden seen between countries was absent within countries over time. We provide country-level estimates of NTD and malaria DALYs at risk under specified cuts.', template=TPL_BODY)
x = new_par_after(x, '', template=TPL_BODY, runs=[('Implications of all the available evidence', True, None)])
x = new_par_after(x, 'The 2025 reductions in development assistance fall where NTD and malaria burden and financing dependence are greatest, which supports protecting service continuity in those countries. Aggregate financing shares should not be read as disease-specific effects; estimating the consequences of the cuts needs programme disbursement data linked to coverage and outcomes.', template=TPL_BODY)

# =========================== INTRODUCTION ===========================
rewrite(find('Control of neglected tropical diseases'), 'NTDs and malaria remain central to Sustainable Development Goal 3.3. In 2023, 1.495 billion people required NTD interventions, and in 2024 malaria caused an estimated 282 million cases and 610 000 deaths (World Health Organization [WHO], 2025a, 2025b). Combined DALYs fell by about 18% between 1990 and 2021, to 71.6 million (Zheng et al., 2025), and successive GBD rounds show burden concentrating in low-SDI countries and western sub-Saharan Africa (GBD 2023 Causes of Death Collaborators, 2025; Lin et al., 2022; Murray et al., 2014). Between-country inequality narrowed in absolute terms but widened in relative terms (Emadi et al., 2021; Feng et al., 2025; He et al., 2025; Lin et al., 2025; Stolk et al., 2016), and NTD treatment coverage remains uneven within countries (Khaki et al., 2025; Lo et al., 2019). None of these studies used GBD 2023, tested whether burden clusters geographically, or decomposed inequality between and within regions.')
rewrite(find('Analyses of GBD 2021 data show'), 'External financing underpinned much of this progress. Cross-national panels associate development assistance for health with lower malaria and child mortality (Akachi & Atun, 2011; Bendavid & Bhattacharya, 2014; Hsiao & Emdin, 2014; Mishra & Newhouse, 2009; Yan et al., 2015), and evaluations attribute large gains to the US President’s Malaria Initiative and insecticide-treated nets (Bhatt et al., 2015; Jakubowski et al., 2017). Development assistance for health fell by an estimated 22% between 2024 and 2025 (Apeagyei et al., 2025). Recent studies project 14–23 million additional deaths by 2030 from USAID and broader aid cuts (Cavalcanti et al., 2025; A. F. da Silva et al., 2026), and models address HIV, tuberculosis and malaria (Hallett et al., 2025; Stover et al., 2025; Symons et al., 2025). These analyses model aid volume and mortality. Yet most NTD burden is non-fatal, and because aid flows towards high-burden countries (Namubiru, 2025; Sempungu et al., 2023), between-country associations can differ from within-country change. WHO already reports disruption of NTD programmes (World Health Organization Regional Office for Africa, 2025). No study has estimated NTD DALYs at risk from the cuts.')
rewrite(find('We examine NTD and malaria burden across 204'), 'We analysed NTD and malaria burden in 204 countries and territories using GBD 2023, at super-region, regional and national level. We quantified spatial clustering, absolute and relative socioeconomic inequality from 1990 to 2023, and the fatal and non-fatal composition of burden; compared between-country and within-country associations of external financing dependence with burden; and projected excess DALYs under specified financing cuts.')
drop('External financing has supported the expansion', 'Recent studies already estimate the consequences')

# =========================== METHODS ===========================
rename('Study design', 'Study design and data')
rewrite(find('We conducted an ecological panel study'), 'We conducted an ecological study of 204 countries and territories in seven GBD super-regions and 21 regions, reported according to GATHER and STROBE (appendix section 1) (Stevens et al., 2016; von Elm et al., 2007). We linked GBD 2023 estimates of DALYs, years lived with disability (YLDs) and years of life lost (YLLs), World Bank World Development Indicators (WDI), WHO indicators from the UN SDG database, IHME Financing Global Health estimates and Natural Earth boundaries (Table S1; Figure 1) (Apeagyei et al., 2025; GBD 2023 Disease and Injury and Risk Factor Collaborators, 2025; World Bank, n.d.). Outcomes were age-standardised DALY rates per 100 000 for NTDs excluding malaria (the GBD NTD-and-malaria aggregate minus malaria; 19 causes) and for malaria; counts were all-age. Percentage changes with uncertainty intervals (UIs) were taken from GBD. GBD does not publish changes for NTDs excluding malaria or country-level changes for malaria alone; we computed these from point estimates, without intervals.')
drop('Data sources and linkage', 'We linked five public sources', 'Study populations', 'Descriptive analyses covered 204', 'Burden outcomes', 'GBD 2023 supplied annual all-age')
rename('Financing exposures', 'Financing exposure and covariates')
rewrite(find('The primary exposure was external health expenditure'), 'The primary exposure was external health expenditure as a share of current health expenditure, per 10 percentage points, which measures dependence; the secondary exposure was log(1 + external health expenditure per capita), which measures volume (World Bank, n.d.). Both were lagged by 2 years. Models adjusted for log domestic government health expenditure per capita (lagged 2 years), log lag-distributed income per capita, universal health coverage (UHC) effective coverage, and basic sanitation and drinking-water coverage, selected a priori (Bendavid & Bhattacharya, 2014; Mishra & Newhouse, 2009; WHO, 2020).')
drop('Additional sources and data quality', 'WHO-reported indicators provided outcomes')
rewrite(find('GBD outcomes and the GBD covariates'), 'GBD outcomes and covariates were complete. Gaps in WDI series (15.1% for lagged external share) were linearly interpolated within countries, with last observations carried forward for up to 2 years; remaining incomplete records were excluded. The analysis samples comprised 153 countries (2287 country-years) for NTDs and 77 malaria-endemic countries (1187 country-years) for malaria, 2007–2022. Complete-case, balanced-panel and multiple-imputation analyses assessed sensitivity (Tables S10a–b).')
drop('Fourteen locations had no usable', 'We assessed associations between incomplete', 'Within each country, interior WDI gaps', 'Missing-data sensitivity analyses used', 'The supplied multiple-imputation implementation', 'Cross-sectional exposures used the latest', 'Scenario analyses used 2022 population', 'Model specification', 'NTD rates were natural-log transformed')
rewrite(find('We summarised 2023 all-age DALY counts'), 'We summarised burden by super-region, region and country, ranked countries by count and rate, and identified countries whose rates rose between 2010 and 2023. Socioeconomic inequality was measured in 1990, 2010 and 2023, ranking countries by SDI of the same year and weighting by population. Relative inequality was measured by the concentration index and absolute inequality by the slope index of inequality (SII), the modelled difference in rate between the highest-SDI and lowest-SDI ends of the distribution (Kakwani et al., 1997; Mackenbach & Kunst, 1997; Wagstaff et al., 1991). Country bootstrap resampling (2000 replicates) gave 95% CIs, with paired resampling for changes over time. Theil T was decomposed into components between super-regions, between regions within super-regions and within regions (Shorrocks, 1980; Theil, 1967). GBD rates were compared with WHO-reported people requiring NTD interventions and malaria incidence by Spearman correlation.')
drop('We calculated the population-weighted Theil T index')
rewrite(find('Spatial dependence was assessed before'), 'Global Moran’s I and local indicators of spatial association were computed on log(1 + rate) with six-nearest-neighbour weights and 9999 permutations; local clusters were reported at a Benjamini–Hochberg false-discovery rate below 5% (Anselin, 1995; Benjamini & Hochberg, 1995; Moran, 1950). Analyses were repeated for 1990 and 2010 and with alternative weights (Table S7).')
rename('Panel econometric models', 'Financing models')
rewrite(find('The primary analysis used within-country variation'), 'The primary analysis estimated within-country associations with two-way (country and year) fixed effects and Driscoll–Kraay standard errors, which allow for the heteroskedasticity, serial correlation and cross-sectional dependence found in diagnostic tests (Table S3) (Driscoll & Kraay, 1998; Hoechle, 2007; Wooldridge, 2010). NTD rates were log-transformed and malaria rates log(1 + rate)-transformed. We compared this model with a 2023 cross-section of 145 countries, pooled, random-effects, first-difference and country-trend models, spatial panel models, and a correlated random-effects (Mundlak) model that separates between-country from within-country associations in one sample (Bell & Jones, 2015; Mundlak, 1978). Estimates are percentage differences per 10-percentage-point higher external share, interpreted as conditional associations rather than causal effects (Imai & Kim, 2021). Malaria mortality was an alternative outcome. Geographically weighted regression and machine-learning prediction, which assessed spatial heterogeneity and predictive performance, are described in the appendix.')
drop('Diagnostics comprised the Breusch', 'Additional spatial and predictive analyses', 'Models used row-standardised six-nearest', 'Geographically weighted regression', 'GWR and MGWR examined', 'Predictive modelling', 'We compared elastic net')
p = find('Spatial panel models', contains=None) if False else [p for p in body.iter(q('p')) if dtext(p) == 'Spatial panel models'][0]; delete_par(p)
rename('Scenario modelling of development-assistance cuts', 'Scenarios of financing cuts')
rewrite(find('The original analysis used two conditional'), 'Two models projected annual excess DALYs if each country’s external health expenditure fell by 5–15% (mild), 19–26% (reference, bracketing the 22% fall in development assistance for health in 2025) or 40–60% (severe) in 153 low- and middle-income countries (Apeagyei et al., 2025). The accounting model assumed that the fall in each country’s all-age DALY rate between 2010 and 2023, summed over the 19 NTD causes or for malaria, was attributable to external financing in proportion to its share of health expenditure and would reverse in proportion to the cut. The econometric model applied the preferred fixed-effects coefficient to the cut-induced fall in external share; for malaria, the change was computed on the (1 + rate) scale and converted to the implied change in rate. Uncertainty was propagated through 4000 Monte Carlo draws of GBD estimates, cut size and coefficients (Briggs et al., 2012). DALYs were valued at one times GDP per capita (0.5 and 3 times in sensitivity analyses), and the rise in domestic government health expenditure needed to replace lost external funds was calculated by super-region.')
drop('The accounting script summed', 'Uncertainty was propagated through 4000', 'Sensitivity analyses examined alternative')
p = [p for p in body.iter(q('p')) if dtext(p) == 'Sensitivity analyses'][0]; delete_par(p)
rewrite(find('Analyses used Python'), 'Analyses used Python (pandas, statsmodels, linearmodels, PySAL, scikit-learn and LightGBM) (Rey & Anselin, 2007). Code, data and execution instructions are in the appendix and the project GitHub repository [URL to be added]. Tests were two-sided at α = .05.')

# =========================== RESULTS ===========================
rename('Global and super-regional burden in 2023', 'Global, regional and national burden')
rewrite(find('The supplied GBD global aggregate reports'), 'In 2023, NTDs and malaria caused 70.83 million DALYs (95% UI 41.3–113.8 million); country estimates attributed 51.56 million to malaria and 19.24 million to NTDs (Table 1). Sub-Saharan Africa had 15.1% of the population but 80.2% of combined DALYs, 95.1% of malaria DALYs and 40.3% of NTD DALYs. Western sub-Saharan Africa alone accounted for 49.7% of global combined DALYs and central sub-Saharan Africa for 13.4%, with age-standardised rates of 5556.5 and 5006.5 per 100 000, against 314.2 in southern sub-Saharan Africa; malaria contributed 4828.5 and 4104.3 of those rates (Table S16; Figure S2). Outside Africa, Oceania had the highest rate (1694.8 per 100 000). For NTDs, South Asia held the largest regional share of DALYs (25.0%), followed by western (20.7%) and eastern sub-Saharan Africa (12.3%; Figure 2).')
rewrite(find('Sub-Saharan Africa accounted for 15.1% of the population'), 'Three countries, India (4.00 million DALYs), Nigeria (2.10 million) and China (1.30 million), accounted for 38.5% of NTD DALYs, and Nigeria (16.63 million) and the Democratic Republic of the Congo (6.46 million) for 44.8% of malaria DALYs (Table S18). Rates were highest in South Sudan for NTDs (2227.1 per 100 000) and Sierra Leone for malaria (8237.2). Among the 19 NTDs, other NTDs (5.14 million DALYs), dengue (3.01 million) and schistosomiasis (2.07 million) contributed most (Figure 3; Table S2). Single countries held most of the burden of several causes: India 53.3% of lymphatic filariasis DALYs, China 75.6% of food-borne trematodiasis, Brazil 58.2% of Chagas disease and the Democratic Republic of the Congo 42.3% of onchocerciasis (Table S20).')
rewrite(find('The highest country-level NTD and malaria rates'), 'Disability accounted for 62.4% of NTD DALYs (12.01 million YLDs), from 54.6% in sub-Saharan Africa to 94.5% in Central Europe, Eastern Europe and Central Asia, whereas premature death accounted for 95.2% of malaria DALYs (Table S17; Figure S3). GBD country rates correlated closely with WHO-reported people requiring NTD interventions (Spearman ρ = 0.81) and malaria incidence (ρ = 0.94; Table S21).')
drop('The largest global NTD burdens were other NTDs')
rewrite(find('The global age-standardised NTD and malaria DALY rate declined'), 'The global age-standardised rate fell from 1714.0 per 100 000 in 1990 to 1290.8 in 2010 and 1012.5 in 2023, a fall of 21.6% (95% UI 7.8–36.3) since 2010 (Table 1; Figure 4). Since 2010, rates fell most in South Asia (43.8%, 29.2–52.9) and Southeast Asia, East Asia and Oceania (38.2%, 7.1–56.3), and by 34.1–39.9% in each of the four sub-Saharan African regions; sub-Saharan Africa’s rate fell from 5.7 to 3.8 times the global rate between 1990 and 2023. Malaria rates rose only in North Africa and the Middle East (26.3%, 0.1–46.4) and fell to zero in Central Asia, Southern Latin America and Western Europe (Table S16). Nationally, 78 of 204 countries had a significant decline in the combined rate and four a significant increase: Nicaragua (105.0%, 46.2–178.8), Fiji (92.5%, 62.7–132.2), Monaco (88.8%, 16.9–242.3) and American Samoa (56.2%, 20.4–91.4). Malaria rates were higher in 2023 than in 2010 in 13 countries, including Burundi, Madagascar, Zambia and Kenya (Table S19).')
rewrite(find('Global Moran’s I was 0.71'), 'Burden clustered geographically: Moran’s I was 0.71 for NTDs and 0.79 for malaria (both p < .001; Table 2), and 0.66–0.82 across alternative weights (Table S7). High–high clusters (48 countries for NTDs and 42 for malaria) lay almost entirely in sub-Saharan Africa (Figure 5) and were stable: all 47 NTD high–high countries of 2010 remained so in 2023, with Somalia added, and Comoros and Somalia joined the malaria cluster (Table S21; Figure S4).')
rewrite(find('After false-discovery-rate adjustment, NTD burden'), 'Burden was concentrated in low-SDI countries, and relative concentration changed little over time. The malaria concentration index was −0.80 in 1990 (95% CI −0.88 to −0.63) and in 2023 (−0.88 to −0.65); the NTD index moved from −0.51 (−0.64 to −0.36) to −0.43 (−0.54 to −0.27), a change distinguishable from zero only for 2010–2023 (0.05, 0.02 to 0.08). Absolute inequality narrowed: the SII fell from −1966 (−3053 to −1198) to −632 (−877 to −412) DALYs per 100 000 for NTDs and from −3806 (−6754 to −1974) to −2484 (−4271 to −1131) for malaria (Table S15a; Figure S1). Most inequality lay between super-regions (79.3% for malaria and 64.0% for NTDs in 2023), but the share of NTD inequality between countries within the same region rose from 12.6% in 1990 to 21.1% in 2023 (Table S15b).')
rename('Burden and dependence on external financing', 'Financing dependence and burden')
rewrite(find('Among 153 locations with financing data'), 'Median external expenditure share was 23.0% in sub-Saharan Africa, 11.5% in Southeast Asia, East Asia and Oceania and 6.4% in South Asia. Thirty-four countries, 31 in sub-Saharan Africa, were in the highest tertiles of both NTD burden and external share; they held 27.2% of NTD DALYs and 52.3% of malaria DALYs (Figure 6). Seventeen high-burden countries, including Brazil, Peru and Indonesia, had low or intermediate external shares.')
drop('Associations between financing and burden')
rewrite(find('In the 2023 cross-section of 145 locations'), 'Between countries, a 10-percentage-point higher external share was associated with a 13.4% (95% CI 6.4–20.0) lower NTD rate in the 2023 cross-section (Table 3). Within countries, the association was −0.64% (−2.39 to 1.14) in the preferred model and ranged from −1.48% to 0.17% across within-country estimators, all intervals including zero (Figure 7A). In the correlated random-effects model, the between-country association was −4.99% (−11.25 to 1.71) and the within-country association −0.64% (Table S23). For malaria, the preferred within-country estimate was −6.32% in (1 + rate) (−10.85 to −1.56), but intervals included zero with country-clustered errors (−17.14 to 5.91) and in other within-country estimators, and the between-country association was positive (18.25%, −13.46 to 61.58). Malaria mortality gave a similar within-country estimate (−6.30%, −10.96 to −1.38; Table S24), as did alternative missing-data strategies and extension to 2023 (Tables S10b and S22). Higher UHC, sanitation and drinking-water coverage were each associated with lower NTD burden (Table S4). Local external-share coefficients from multiscale geographically weighted regression were significant in 36 of 145 countries, none in sub-Saharan Africa (Figure 7C; Table S6b).')
drop('In the preferred NTD model, a 10-percentage-point', 'Robustness to missing data handling', 'Excluding filled model inputs gave', 'MGWR fitted the 2023 NTD cross-section')
p = [p for p in body.iter(q('p')) if dtext(p) == 'Spatial panel models'][0]; delete_par(p)
rewrite(find('The econometric model projected 25 000'), 'Under the reference scenario, the accounting model projected 406 600 excess NTD DALYs a year (95% UI 334 500–501 800) and 1.85 million excess malaria DALYs (1.51–2.21 million), 2.2% and 3.6% of 2023 burden; severe cuts projected 908 700 (708 000–1 140 400) and 4.10 million (3.25–5.07 million; Table 4; Figure 8A–B). The econometric model projected 24 500 excess NTD DALYs (−42 100 to 90 300) and 1.22 million malaria DALYs (0.27–2.29 million). Sub-Saharan Africa accounted for 91% of excess NTD and 96% of excess malaria DALYs in the reference accounting scenario. The largest NTD projections were for the Democratic Republic of the Congo (109 900; 83 600–145 100), Ethiopia (34 700) and Tanzania (32 000), and the largest per-capita projections for South Sudan (246 per 100 000) and the Democratic Republic of the Congo (104; Table S8; Figure 8C). Reference-scenario losses were valued at US$0.55 billion (0.45–0.72) for NTDs and US$2.11 billion (1.65–2.55) for malaria a year. Replacing lost external funds would require domestic government health expenditure to rise by 8.7% in sub-Saharan Africa (US$3.44 billion; 3.9–19.4% across scenarios), 1.8% in South Asia and 0.5% in North Africa and the Middle East (Table S14; Figure 8D). Independent burden draws widened intervals without materially changing medians (Table S7).')
drop('Sub-Saharan Africa accounted for 94% of projected', 'Scenario sensitivity analyses', 'The original independent-draw sensitivity')

# =========================== DISCUSSION ===========================
rewrite(find('Sub-Saharan Africa carried 80.2%'), 'NTDs and malaria caused 70.8 million DALYs in 2023, 63.1% of them in western and central sub-Saharan Africa. Since 1990 the absolute socioeconomic gap narrowed by about two-thirds for NTDs and one-third for malaria, but burden remained as concentrated in low-SDI countries as before and hot spots did not move. Thirty-four countries combining high NTD burden with high donor dependence held over half of malaria DALYs. The inverse association between external financing and NTD burden seen across countries was not detectable within countries over time, and the malaria association depended on the estimator. These findings locate where need and financing vulnerability coincide; they do not establish the size of losses attributable to withdrawal.')
rewrite(find('The continuing concentration of burden in sub-Saharan Africa'), 'Our 2023 total is close to the 71.6 million DALYs reported for 2021 from GBD 2021 (Zheng et al., 2025); because each GBD round re-estimates the full series, the difference does not measure change. The regional pattern agrees with GBD 2019 and 2021 analyses identifying western sub-Saharan Africa as the highest-burden region (Feng et al., 2025; Lin et al., 2025), and stable high–high clusters extend malaria-only geospatial evidence (Namubiru, 2025) to NTDs. National concentration matters for planning: three countries held 38.5% of NTD DALYs and two held 44.8% of malaria DALYs, and single countries held most of the burden of lymphatic filariasis, food-borne trematodiasis and Chagas disease, which aggregate rankings conceal. The post-2015 plateau in malaria incidence in Africa (Weiss et al., 2025) and higher malaria rates in 13 countries in 2023 than in 2010 show that recent progress has been neither uniform nor secure.')
rewrite(find('Spatial clustering and socioeconomic concentration described'), 'Absolute and relative inequality moved differently. Narrowing absolute gaps reflect falling rates in low-SDI countries, but unchanged concentration indices show that these countries still carry the same disproportionate share of burden; GBD 2021 analyses found relative inequality widening to 2021 (Feng et al., 2025; Lin et al., 2025), and our estimates to 2023 show at most stabilisation. Targets framed in absolute terms can therefore be met while the relative disadvantage of the poorest countries persists (Mackenbach & Kunst, 1997). The rising within-region share of NTD inequality suggests that residual NTD burden increasingly reflects differences between neighbouring countries, consistent with uneven subnational treatment coverage (Khaki et al., 2025; Lo et al., 2019), whereas malaria inequality remains largely between super-regions. Associations of NTD burden with sanitation and water coverage are consistent with evidence on water, housing and cash transfers (Ahmed et al., 2022; Grimes et al., 2014; Tusting et al., 2017), but do not identify intervention effects.')
rewrite(find('The NTD financing association changed from'), 'The NTD financing association attenuated from 13.4% between countries to 0.64% within countries, and the Mundlak model reproduced this contrast in one sample. Earlier panels associated aid volume with lower malaria and child mortality (Akachi & Atun, 2011; Bendavid & Bhattacharya, 2014; Hsiao & Emdin, 2014; Yan et al., 2015), and recent analyses associated USAID and total aid with lower NTD and malaria mortality (Cavalcanti et al., 2025; A. F. da Silva et al., 2026). Our exposure measures dependence rather than volume, and our outcome includes disability, which makes up 62.4% of NTD DALYs and which mortality analyses cannot capture. For malaria, within-country associations with DALYs and deaths were negative, in the direction of programme evaluations (Bhatt et al., 2015; Jakubowski et al., 2017), whereas the between-country association was positive, consistent with aid allocation to high-burden countries (Namubiru, 2025; Sempungu et al., 2023). This contrast is why between-country coefficients should not be converted into projected losses. The weak NTD association may reflect an exposure that does not isolate NTD funding, which received 0.6% of health aid in 2003–2007 (Liese & Schubert, 2009), aggregation of diseases with different response times (Borlase et al., 2022), and a fixed 2-year lag; these are hypotheses that this study cannot test.')
rewrite(find('The scenario analyses address a different question'), 'The scenario models bracket structural uncertainty. The accounting model assumes that donor-financed spending produced a matching share of health gains; the econometric model transfers a weak historical association; their NTD projections differ 17-fold. Neither represents the nonlinear rebound that follows interrupted mass drug administration (Borlase et al., 2022) or the resurgence that followed weakened control in 68 of 75 malaria resurgence events (Cohen et al., 2012), and the programme-specific malaria projections of Symons et al. (2025) address a different counterfactual. Replacing lost funds would require an 8.7% rise in domestic government health spending in sub-Saharan Africa. Reductions in health aid have not historically been offset by domestic spending (Dieleman & Hanlon, 2014), aid has had no significant effect on overall domestic public health spending (Patenaude, 2021), poorly prepared donor transitions disrupt services (Huffstetler et al., 2022), and higher tax revenue is the main route to greater public health spending (Reeves et al., 2015).')
rewrite(find('The study brings together burden distributions'), 'This ecological study cannot establish individual-level effects or locate underserved communities within countries (Morgenstern, 1995). GBD outcomes are modelled; close agreement with WHO series supports the ordering of countries, not absolute levels. Financing samples were smaller than the descriptive sample, missing WDI values were interpolated, and fixed effects do not remove time-varying confounding. Country-level changes for NTDs excluding malaria and for malaria alone lack uncertainty intervals, and the spatial-panel and machine-learning analyses remain provisional (appendix).')
rewrite(find('The evidence supports prioritising continuity'), 'NTD and malaria burden remains concentrated where poverty and donor dependence are greatest, and the 2025 cuts fall on those countries. These data support protecting service continuity there, with priorities adapted to each disease’s geography. Measuring the burden attributable to the cuts requires linking programme disbursements to coverage and disease-specific outcomes.')
drop('The 21.6% global reduction in the combined', 'The inverse associations of NTD burden with sanitation', 'The 34 countries in the highest tertiles', 'Several features could contribute to the weak', 'For malaria, a 10-percentage-point increase', 'Published disruption models provide relevant', 'Replacing the reference-scenario financing loss')

# =========================== TABLES IN MANUSCRIPT ===========================
p = [p for p in body.iter(q('p')) if 'Provisional annual DALY projections under development-assistance cuts' in dtext(p)][0]
replace(p, 'Provisional annual DALY projections under development-assistance cuts', 'Projected Excess Annual DALYs Under Development-Assistance Cut Scenarios, Low- and Middle-Income Countries')
p = find('Note. The accounting model multiplies')
replace(p, 'All values are retained original outputs, not validated revised projections. Missing NTD baselines and the malaria outcome transformation require correction before finalisation.', 'NTD baselines cover all 19 causes; malaria projections are computed on the (1 + rate) scale of the fitted model.')
p = find("Note. Moran's I and local indicators"); replace(p, 'Table S15 gives', 'Table S22 gives')
tbl = body.findall('.//w:tbl', ns)[3]; rows = tbl.findall('w:tr', ns)
CH = {2: {1: '182 [94, 277]', 2: '1.0', 3: '91', 5: '0.25 [0.13, 0.39]'}, 3: {4: '490 [107, 1,116]'},
      5: {1: '407 [335, 502]', 2: '2.2', 3: '91', 5: '0.55 [0.45, 0.72]'}, 6: {4: '1,222 [270, 2,288]'},
      8: {1: '909 [708, 1,140]', 2: '4.8', 3: '91', 5: '1.24 [0.95, 1.62]'}, 9: {4: '3,060 [701, 5,972]'}}
for ri, cells in CH.items():
    tcs = rows[ri].findall('w:tc', ns)
    for ci_, val in cells.items():
        cp = tcs[ci_].find('w:p', ns); replace(cp, dtext(cp), val)

# =========================== REFERENCES ===========================
NEW = {
 'Akachi': ('Ahmed, A.,', 'Akachi, Y., & Atun, R. (2011). Effect of investment in malaria control on child mortality in sub-Saharan Africa in 2002–2008. ', 'PLoS ONE, 6', '(6), Article e21309. https://doi.org/10.1371/journal.pone.0021309'),
 'Emadi': ('Elhorst, J. P.', 'Emadi, M., Delavari, S., & Bayati, M. (2021). Global socioeconomic inequality in the burden of communicable and non-communicable diseases and injuries: An analysis on Global Burden of Disease Study 2019. ', 'BMC Public Health, 21', '(1), Article 1771. https://doi.org/10.1186/s12889-021-11793-7'),
 'Feng': ('Emadi, M.', 'Feng, L., Mo, G., Liu, Z., & Liu, Q. (2025). Global, regional, national burden, trends and health inequality of neglected tropical diseases and malaria from 1990 to 2021. ', 'BMC Infectious Diseases, 25', '(1), Article 1649. https://doi.org/10.1186/s12879-025-12068-x'),
 'GBDCoD': ('GBD 2019 Universal', 'GBD 2023 Causes of Death Collaborators. (2025). Global burden of 292 causes of death in 204 countries and territories and 660 subnational locations, 1990–2023: A systematic analysis for the Global Burden of Disease Study 2023. ', 'The Lancet, 406', '(10513), 1811–1872. https://doi.org/10.1016/S0140-6736(25)01917-8'),
 'Hallett': ('Grimes, J. E. T.', 'Hallett, T. B., Menzies, N. A., Resch, S., Pretorius, C., Stover, J., Su, J. S., Winskill, P., Gordon, M., Grahn, R., Mahmood, F., Smit, M., Hosseini, M., & Hunger, J. (2025). The case for optimal investment in combating HIV, tuberculosis, and malaria: A global modelling study. ', 'The Lancet, 406', '(10500), 261–270. https://doi.org/10.1016/S0140-6736(25)00831-1'),
 'Hsiao': ('Honaker, J.', 'Hsiao, A. J., & Emdin, C. A. (2014). The association between development assistance for health and malaria, HIV and tuberculosis mortality: A cross-national analysis. ', 'Journal of Epidemiology and Global Health, 5', '(1), 41–48. https://doi.org/10.1016/j.jegh.2014.10.001'),
 'Khaki': ('Ke, G.', 'Khaki, J. J., Minnery, M., & Giorgi, E. (2025). Using ESPEN data for evidence-based control of neglected tropical diseases in sub-Saharan Africa: A comprehensive model-based geostatistical analysis of soil-transmitted helminths. ', 'PLoS Neglected Tropical Diseases, 19', '(1), Article e0012782. https://doi.org/10.1371/journal.pntd.0012782'),
 'Liese': ('LeSage, J.', 'Liese, B. H., & Schubert, L. (2009). Official development assistance for health—how neglected are neglected tropical diseases? An analysis of health financing. ', 'International Health, 1', '(2), 141–147. https://doi.org/10.1016/j.inhe.2009.08.004'),
 'Lin2022': ('Liese, B. H.', 'Lin, Y., Fang, K., Zheng, Y., Wang, H. L., & Wu, J. (2022). Global burden and trends of neglected tropical diseases from 1990 to 2019. ', 'Journal of Travel Medicine, 29', '(3), Article taac031. https://doi.org/10.1093/jtm/taac031'),
 'Lo': ('Lin, Y., Long, Q.', 'Lo, N. C., Heft-Neal, S., Coulibaly, J. T., Leonard, L., Bendavid, E., & Addiss, D. G. (2019). State of deworming coverage and equity in low-income and middle-income countries using household health surveys: A spatiotemporal cross-sectional study. ', 'The Lancet Global Health, 7', '(11), e1511–e1520. https://doi.org/10.1016/S2214-109X(19)30413-9'),
 'Mackenbach': ('Lundberg, S. M.', 'Mackenbach, J. P., & Kunst, A. E. (1997). Measuring the magnitude of socio-economic inequalities in health: An overview of available measures illustrated with two examples from Europe. ', 'Social Science & Medicine, 44', '(6), 757–771. https://doi.org/10.1016/S0277-9536(96)00073-1'),
 'Murray': ('Mundlak, Y.', 'Murray, C. J. L., Ortblad, K. F., Guinovart, C., Lim, S. S., Wolock, T. M., Roberts, D. A., Dansereau, E. A., Graetz, N., Barber, R. M., Brown, J. C., Wang, H., Duber, H. C., Naghavi, M., Dicker, D., Dandona, L., Salomon, J. A., Heuton, K. R., Foreman, K., Phillips, D. E., … Vos, T. (2014). Global, regional, and national incidence and mortality for HIV, tuberculosis, and malaria during 1990–2013: A systematic analysis for the Global Burden of Disease Study 2013. ', 'The Lancet, 384', '(9947), 1005–1070. https://doi.org/10.1016/S0140-6736(14)60844-8'),
 'Namubiru': ('Murray, C. J. L.', 'Namubiru, C. (2025). Institutional quality, aid flows, and malaria burden: A geospatial analysis of sub-Saharan Africa. ', 'Malaria Journal, 24', '(1), Article 332. https://doi.org/10.1186/s12936-025-05592-3'),
 'Patenaude': ('Oshan, T. M.', 'Patenaude, B. N. (2021). The relationship between development assistance for health and public health financing in 134 countries between 2000 and 2015. ', 'Health Policy and Planning, 36', '(4), 369–383. https://doi.org/10.1093/heapol/czab004'),
 'Sempungu': ('Rubin, D. B.', 'Sempungu, J. K., Choi, M., Lee, E. H., & Lee, Y. H. (2023). The burden of malaria in sub-Saharan Africa and its association with development assistance for health and governance: An exploration of the GBD 2019 study. ', 'Global Public Health, 18', '(1), Article 2229892. https://doi.org/10.1080/17441692.2023.2229892'),
 'Stolk': ('Stevens, G. A.', 'Stolk, W. A., Kulik, M. C., le Rutte, E. A., Jacobson, J., Richardus, J. H., de Vlas, S. J., & Houweling, T. A. J. (2016). Between-country inequalities in the neglected tropical disease burden in 1990 and 2010, with projections for 2020. ', 'PLoS Neglected Tropical Diseases, 10', '(5), Article e0004560. https://doi.org/10.1371/journal.pntd.0004560'),
 'Stover': ('Stolk, W. A.', 'Stover, J., Sonneveldt, E., Tam, Y., Horton, K. C., Phillips, A. N., Smith, J., Martin-Hughes, R., Ten Brink, D., Citron, D. T., Kim, H. Y., Akullian, A., Mudimu, E., Pickles, M., Bershteyn, A., Williamson, J., Meyer-Rath, G., Jamieson, L., Sully, E. A., White, J. N., … Kaftan, D. (2025). Effects of reductions in US foreign assistance on HIV, tuberculosis, family planning, and maternal and child health: A modelling study. ', 'The Lancet Global Health, 13', '(10), e1669–e1680. https://doi.org/10.1016/S2214-109X(25)00281-5'),
 'Yan': ('World Health Organization Regional Office', 'Yan, I., Korenromp, E., & Bendavid, E. (2015). Mortality changes after grants from the Global Fund to Fight AIDS, Tuberculosis and Malaria: An econometric analysis from 1995 to 2010. ', 'BMC Public Health, 15', ', Article 977. https://doi.org/10.1186/s12889-015-2305-1'),
 'Zheng': ('Yan, I.', 'Zheng, J.-X., Liu, Y., Guan, S.-Y., Guo, Z.-Y., Duan, L., Lv, S., Zhang, S.-X., Li, S.-Z., Zhou, X.-N., & Feng, X.-Y. (2025). Global, regional, and national burden of neglected tropical diseases and malaria in the general population, 1990–2021: Systematic analysis of the Global Burden of Disease Study 2021. ', 'Journal of Advanced Research, 79', ', 769–781. https://doi.org/10.1016/j.jare.2025.04.004'),
}
ref_pars = []
for key, (anchor, a, it, b) in NEW.items():
    hits = [p for p in body.iter(q('p')) if dtext(p).startswith(anchor) or (ptext(p).startswith(anchor) and len(ptext(p)) > 40)]
    anc = hits[-1]
    new_par_after(anc, '', template=anc, runs=[(a, False, False), (it, False, True), (b, False, False)])

tree.write(P, xml_declaration=True, encoding='UTF-8', standalone=True)
print('ok')

# =========================== DECLARATIONS AND DATA SHARING (author-supplied text) ===========================
from lxml import etree as _et
from tc_lib import _mark
tree = _et.parse(P); body = tree.find('.//w:body', ns)
REPO = 'https://github.com/VincentUwumboriyhieGmayinaam/NTD-Malaria-Burden-Financing'
def del_runs(elem):
    for r in list(elem.iter(q('r'))):
        if r.getparent().tag in (q('del'), q('ins')): continue
        d = _mark('del'); r.addprevious(d); r.getparent().remove(r); d.append(r)
        for t_ in r.findall('w:t', ns): t_.tag = q('delText')
    for p_ in elem.iter(q('p')):
        ppr = p_.find('w:pPr', ns)
        if ppr is None: ppr = _et.Element(q('pPr')); p_.insert(0, ppr)
        rp = ppr.find('w:rPr', ns)
        if rp is None: rp = _et.SubElement(ppr, q('rPr'))
        if rp.find('w:del', ns) is None: rp.insert(0, _mark('del'))
kids = list(body)
def heading(text):
    return [c for c in kids if c.tag == q('p') and ''.join(c.itertext()).strip() == text][0]
body_tpl = [p for p in body.iter(q('p')) if ''.join(t.text or '' for t in p.iter(q('t'))).startswith('NTD and malaria burden remains concentrated where poverty')]
body_tpl = body_tpl[0] if body_tpl else None
# Declaration of interests
h = heading('DECLARATION OF INTERESTS (Required)'); tpl = h.getnext()
del_runs(tpl)
replace(h, 'DECLARATION OF INTERESTS (Required)', 'DECLARATION OF INTERESTS')
new_par_after(tpl, 'All other authors declare no competing interests.', template=body_tpl)
# Data sharing
h = heading('DATA SHARING (Required)'); tpl = h.getnext()
while tpl is not None and tpl.tag == q('p') and not ''.join(tpl.itertext()).strip(): tpl = tpl.getnext()
if tpl.tag == q('sdt'): del_runs(tpl)
replace(h, 'DATA SHARING (Required)', 'DATA SHARING')
new_par_after(tpl, "All data analysed in this study were obtained from publicly accessible secondary data repositories. Disease burden, sociodemographic, and universal health coverage estimates were retrieved from the Global Burden of Disease (GBD) 2023 study through the Institute for Health Metrics and Evaluation (IHME) (https://vizhub.healthdata.org/gbd-results/). Economic and health-system indicators were obtained from the World Bank's World Development Indicators database (https://databank.worldbank.org/source/world-development-indicators). Sustainable Development Goal indicators were obtained from the United Nations SDG Global Database, incorporating data reported by the World Health Organization (https://unstats.un.org/sdgs/dataportal). Development assistance for health estimates were obtained from IHME's Financing Global Health database (https://www.healthdata.org/data-tools-practices/data-sources), and geographical boundary data were sourced from Natural Earth (https://www.naturalearthdata.com/). The analytical dataset was constructed by harmonising and linking these sources using country identifiers and calendar years. All original datasets are accessible through their respective repositories, subject to applicable data-use conditions. The harmonised analytical dataset and analytical code are held in the study GitHub repository (" + REPO + "), which will be made publicly available on publication.", template=body_tpl)
# GitHub link in Methods
p = [p for p in body.iter(q('p')) if 'project GitHub repository [URL to be added]' in ''.join(t.text or '' for t in p.iter(q('t')))][0]
for ins in p.findall('w:ins', ns):
    for t_ in ins.iter(q('t')):
        if '[URL to be added]' in (t_.text or ''): t_.text = t_.text.replace('the project GitHub repository [URL to be added]', 'the study GitHub repository (' + REPO + ')')

# Ethics (author-supplied)
p = [p for p in body.iter(q('p')) if 'requires author confirmation' in ''.join(t.text or '' for t in p.iter(q('t')))][0]
old = ''.join(t.text or '' for r in p.findall('w:r', ns) for t in r.findall('w:t', ns))
replace(p, old, "This study was based exclusively on secondary analyses of publicly available, aggregated data obtained from the Global Burden of Disease 2023 study, the World Bank's World Development Indicators, the World Health Organization through the United Nations Sustainable Development Goals database, the Institute for Health Metrics and Evaluation's Financing Global Health database, and Natural Earth. All data were available at the country or geographical level and contained no individual-level identifiable information. The study involved no direct recruitment of human participants, collection of primary data, or access to identifiable personal health records. Consequently, formal ethical approval and individual informed consent were not required for this secondary analysis, subject to applicable institutional requirements.")
tree.write(P, xml_declaration=True, encoding='UTF-8', standalone=True)
print('declarations ok')

# =========================== FINAL CHECKLIST / LANCET REVISIONS ===========================
tree = _et.parse(P); body = tree.find('.//w:body', ns)
def _direct(p): return ''.join(t.text or '' for r in p.findall('w:r', ns) for t in r.findall('w:t', ns))
def edit(key, old, new):
    """Tracked replace in original text; direct text change inside Claude's own earlier insertions."""
    ps=[p for p in body.iter(q('p')) if key in ptext(p) and old in ptext(p)] or [p for p in body.iter(q('p')) if key in ptext(p)]
    if not ps: raise ValueError('para not found: '+key)
    p=ps[0]
    if old in _direct(p): replace(p, old, new); return
    for ins in p.iter(q('ins')):
        for t_ in ins.iter(q('t')):
            if old in (t_.text or ''): t_.text=t_.text.replace(old,new,1); return
    raise ValueError('text not found: '+old[:70]+' || DIRECT: '+_direct(p)[-400:])
# Summary
edit('two scenario models projected excess', 'We analysed Global Burden of Disease', 'In this ecological study, we analysed Global Burden of Disease')
edit('relative concentration in low-SDI countries persisted', 'malaria concentration index −0.80 in both years', 'malaria concentration index −0.79 in 1990 and −0.81 in 2023')
# Methods
edit('Gaps in WDI series', 'The analysis samples comprised 153 countries', 'The analysis samples, restricted to countries outside the GBD high-income super-region (hereafter low- and middle-income countries), comprised 153 countries')
edit('Gaps in WDI series', 'Complete-case, balanced-panel and multiple-imputation analyses assessed sensitivity (Tables S10a–b).', 'Sample derivation and characteristics are in Tables S25–S26; complete-case, balanced-panel and multiple-imputation analyses assessed sensitivity (Tables S10a–b).')
edit('Geographically weighted regression and machine-learning prediction', 'Geographically weighted regression and machine-learning prediction, which assessed spatial heterogeneity and predictive performance, are described in the appendix.', 'Geographically weighted regression and machine-learning prediction are described in the appendix.')
edit('Tests were two-sided', 'Tests were two-sided at α = .05.', 'Tests were two-sided at α=0.05.')
# Results
edit('Sub-Saharan Africa had 15.1% of the population', 'Sub-Saharan Africa had 15.1% of the population but 80.2% of combined DALYs, 95.1% of malaria DALYs and 40.3% of NTD DALYs.', 'Sub-Saharan Africa had 15.1% of the population (1208.6 million) but 80.2% of combined DALYs (56.78 million), 95.1% of malaria DALYs (49.03 million) and 40.3% of NTD DALYs (7.75 million).')
edit('Western sub-Saharan Africa alone accounted', 'Western sub-Saharan Africa alone accounted for 49.7% of global combined DALYs and central sub-Saharan Africa for 13.4%', 'Western sub-Saharan Africa alone accounted for 49.7% of global combined DALYs (35.17 million) and central sub-Saharan Africa for 13.4% (9.49 million)')
edit('Moran’s I was 0.71', '(both p < .001; Table 2)', '(both p<0.0001; Table 2)')
edit('relative concentration changed little over time', 'The malaria concentration index was −0.80 in 1990 (95% CI −0.88 to −0.63) and in 2023 (−0.88 to −0.65)', 'The malaria concentration index was −0.79 in 1990 (95% CI −0.88 to −0.63) and −0.81 in 2023 (−0.89 to −0.65)')
edit('relative concentration changed little over time', 'to −0.43 (−0.54 to −0.27)', 'to −0.43 (−0.54 to −0.28)')
edit('Median external expenditure share', 'Median external expenditure share was 23.0% in sub-Saharan Africa, 11.5% in Southeast Asia, East Asia and Oceania and 6.4% in South Asia.', 'Median external expenditure share was 23.0% (IQR 14.6–39.1) in sub-Saharan Africa, 11.5% (1.2–18.4) in Southeast Asia, East Asia and Oceania and 6.4% (3.5–6.9) in South Asia.')
edit('Median external expenditure share', 'they held 27.2% of NTD DALYs and 52.3% of malaria DALYs', 'they held 27.2% of NTD DALYs (5.24 million) and 52.3% of malaria DALYs (26.95 million)')
edit('In the correlated random-effects model', 'the within-country association −0.64% (Table S23)', 'the within-country association −0.64% (Table 3; Table S23)')
# Discussion
edit('This ecological study cannot establish', 'and the spatial-panel and machine-learning analyses remain provisional (appendix).', 'and spatial-panel models used balanced subsets of 130 and 71 countries (appendix).')
# Funding role
fp=[p for p in body.iter(q('p')) if 'subject to applicable institutional requirements' in ptext(p)][0]
new_par_after(fp, 'This study was self-funded by the authors. No funder had any role in study design, data collection, data analysis, data interpretation or writing of the report.', template=fp)
# Figure legends: map projection
edit('Hatched = no data.', 'Hatched = no data.', 'Hatched = no data. Equal Earth projection.')
edit("LISA clusters (FDR q < .05)", "LISA clusters (FDR q < .05)", "LISA clusters (FDR q<0.05; Equal Earth projection)")
edit('Bivariate tertile map', 'Bivariate tertile map of', 'Bivariate tertile map (Equal Earth projection) of')
edit('Multiscale GWR local coefficients for external share', 'Multiscale GWR local coefficients for external share', 'Multiscale GWR local coefficients for external share (Equal Earth projection)')
# Table notes
edit('Theil T is population-weighted', 'The reported Theil estimates exclude zero rates and require population data (NTDs: n = 199; malaria: n = 86); ', 'Theil T uses GBD populations and countries with a non-zero rate (NTDs: n = 204; malaria: n = 86); Table S15b gives the three-level decomposition and ')
edit('Theil T is population-weighted', ' the zero-inclusive sensitivity.', ' the sensitivity to population source and zero rates.')
edit('Spatial-panel rows remain provisional', 'Spatial-panel rows remain provisional because the main and supplementary tables read different model outputs.', 'Mundlak rows are the within-country and between-country components of one correlated random-effects model with year effects (Table S23). p values are given to two significant figures.')
# Table cells (Tables 2 and 3): tracked cell replacements to match regenerated estimates
import json
TJ={t['id']:t for t in json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'..','results','tables.json')))}
tbls=body.findall('.//w:tbl', ns)
def cell_paras(tr): return [tc.find('w:p', ns) for tc in tr.findall('w:tc', ns)]
def set_cell(p, new):
    old=_direct(p)
    if old==new or not old: return
    replace(p, old, new)
def sync_table(tbl, tid, labelmap=lambda s: s):
    want={r[0]:r for r in TJ[tid]['rows'] if isinstance(r, list)}
    for tr in tbl.findall('w:tr', ns)[1:]:
        ps=cell_paras(tr); lab=labelmap(ptext(ps[0]))
        if len(ps)>1 and lab in want:
            for p_, v in zip(ps[1:], want[lab][1:]): set_cell(p_, v.replace('−','-'))
import json
sync_table(tbls[1], 'Table 2')
t3=tbls[2]
# Mundlak: relabel row as within component, add tracked row for between component
mr=[tr for tr in t3.findall('w:tr', ns) if ptext(cell_paras(tr)[0])=='Mundlak CRE'][0]
newrow=copy.deepcopy(mr); mr.addnext(newrow)
replace(cell_paras(mr)[0], 'Mundlak CRE', 'Mundlak CRE, within-country component')
trpr=newrow.find('w:trPr', ns)
if trpr is None: trpr=_et.Element(q('trPr')); newrow.insert(0, trpr)
trpr.append(_mark('ins'))
bw=[r for r in TJ['Table 3']['rows'] if isinstance(r, list) and r[0]=='Mundlak CRE, between-country component'][0]
for p_, v in zip(cell_paras(newrow), bw):
    for r_ in list(p_.findall('w:r', ns)):
        rpr=r_.find('w:rPr', ns); p_.remove(r_)
    ins=_mark('ins'); r_=_et.SubElement(ins, q('r'))
    if rpr is not None: r_.append(copy.deepcopy(rpr))
    t_=_et.SubElement(r_, q('t')); t_.text=v.replace('−','-'); t_.set('{http://www.w3.org/XML/1998/namespace}space','preserve'); p_.append(ins)
for tr in t3.findall('w:tr', ns):
    p0=cell_paras(tr)[0]
    if ptext(p0)=='Spatial panel 2007–2022 — provisional':
        replace(p0, 'Spatial panel 2007–2022 — provisional', 'Spatial panel (2007–22)')
        ref=[tr2 for tr2 in t3.findall('w:tr', ns) if ptext(cell_paras(tr2)[0])=='Within-country panel (2007–22)'][0]
        rp=cell_paras(ref)[0].find('.//w:r/w:rPr', ns); ins_r=p0.find('w:ins/w:r', ns)
        if rp is not None and ins_r is not None:
            old_rp=ins_r.find('w:rPr', ns)
            if old_rp is not None: ins_r.remove(old_rp)
            ins_r.insert(0, copy.deepcopy(rp))
        rpp=cell_paras(ref)[0].find('w:pPr', ns); opp=p0.find('w:pPr', ns)
        if rpp is not None:
            if opp is not None: p0.remove(opp)
            p0.insert(0, copy.deepcopy(rpp))
sync_table(t3, 'Table 3', labelmap=lambda s: {'Mundlak CRE, within-country component':'Mundlak CRE, within-country component'}.get(s, s))
tree.write(P, xml_declaration=True, encoding='UTF-8', standalone=True)
print('final revisions ok')
# word-limit trim (main text ≤3500 words)
tree = _et.parse(P); body = tree.find('.//w:body', ns)
edit('Reductions in health aid have not historically', 'Replacing lost funds would require an 8.7% rise in domestic government health spending in sub-Saharan Africa. Reductions', 'Domestic replacement is uncertain. Reductions')
tree.write(P, xml_declaration=True, encoding='UTF-8', standalone=True); print('trim ok')
