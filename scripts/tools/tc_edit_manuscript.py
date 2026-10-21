"""Apply tracked revisions to the manuscript (author 'Claude')."""
import sys; sys.path.insert(0, 'scripts/tools')
from tc_lib import *
from lxml import etree
P = 'manuscript/source/unpacked/word/document.xml'
tree = etree.parse(P); body = tree.find('.//w:body', ns)
ps = body.findall('w:p', ns)
def find(start):
    hits = [p for p in body.iter(q('p')) if ptext(p).startswith(start)]
    if len(hits) != 1: raise ValueError(f'{len(hits)} hits for {start!r}')
    return hits[0]
R = replace; IA = insert_after_text

# ---------------- Summary ----------------
p = find('MethodsWe conducted')
R(p, 'We assessed temporal trends and geographical inequalities across countries and regions.',
  'We assessed trends across the 21 GBD regions and 204 countries, the split between years lived with disability (YLDs) and years of life lost (YLLs), spatial clustering, and absolute and relative socioeconomic inequality in 1990, 2010 and 2023.')
R(p, 'Sensitivity analyses assessed alternative model specifications and exposure definitions.',
  'Two scenario models estimated excess DALYs under reductions in external health expenditure of the size reported for 2025; sensitivity analyses assessed alternative specifications and exposure definitions.')
p = find('FindingsIn 2023')
R(p, 'Associations between external financing and disease burden varied by disease group and model specification.',
  'Western and central sub-Saharan Africa together held 63.1% of global combined DALYs. Disability accounted for 62.4% of NTD DALYs but 4.8% of malaria DALYs. Between 1990 and 2023 the absolute socioeconomic gradient narrowed (slope index of inequality for NTDs, −1966 to −632 DALYs per 100 000), whereas relative concentration in low-SDI countries persisted (concentration index for malaria, −0.80 in both years). A 10-percentage-point higher external financing share was associated with a 13.4% (95% CI 6.4–20.0) lower NTD DALY rate between countries but not within countries over time (−0.64%, −2.39 to 1.14). Under a 19–26% cut in external health expenditure, an accounting model projected 0.41 million (95% UI 0.33–0.50) excess NTD DALYs and 1.85 million (1.51–2.21) excess malaria DALYs per year, 91% and 96% of them in sub-Saharan Africa.')
p = find('InterpretationDespite')
R(p, 'Associations with external financing should not be interpreted as causal effects.',
  'Narrowing absolute gaps have not changed the concentration of burden in the poorest and most donor-dependent countries, where projected losses from current cuts also concentrate. Within-country financing associations were weak, so the projections are conditional scenarios, not causal estimates.')

# ---------------- Research in context (new panel after Funding) ----------------
fund = find('FundingThis study'); body_tpl = find('Control of neglected tropical diseases'); head_tpl = find('Introduction')
x = new_par_after(fund, '', template=head_tpl, runs=[('Research in context', None, None)])
x = new_par_after(x, '', template=body_tpl, runs=[('Evidence before this study', True, None)])
x = new_par_after(x, 'We searched PubMed from database inception to Oct 21, 2026, with no language restrictions, using six combined strings of the terms “neglected tropical disease*”, “malaria”, “Global Burden of Disease”, “disability-adjusted life years”, “inequalit*”, “concentration index”, “spatial”, “Moran”, “development assistance for health”, “donor funding”, “USAID” and “funding cuts”, and reviewed WHO and IHME reports. Of 704 unique records, 76 studies met our inclusion criteria. Analyses of GBD 2019 and 2021 data showed that combined NTD and malaria DALYs fell by about 18% between 1990 and 2021, that burden concentrated increasingly in low-SDI countries, especially western sub-Saharan Africa, and that relative inequality widened as absolute inequality narrowed. No study had used GBD 2023 estimates for the NTD and malaria group, tested the geographical clustering of these DALYs across countries, or decomposed inequality between and within regions.', template=body_tpl)
x = new_par_after(x, 'Cross-country panel studies consistently associated development assistance with lower malaria, NTD and child mortality. The largest, of USAID funding in 133 countries and of total aid in 93 countries, projected 14 to 23 million additional deaths by 2030 from current funding cuts. These studies modelled aid volume rather than national dependence on external financing, reported mortality although NTD burden is mostly non-fatal, and did not separate between-country differences from within-country change. Other projections of the 2025 cuts addressed HIV, tuberculosis, child mortality and one year of malaria control. We found no country-level estimates of NTD DALYs under the cuts.', template=body_tpl)
x = new_par_after(x, '', template=body_tpl, runs=[('Added value of this study', True, None)])
x = new_par_after(x, 'To our knowledge, this is the first analysis of NTD and malaria burden using GBD 2023 to combine spatial clustering, absolute and relative inequality over time, and national dependence on external health financing for 204 countries and territories. Sub-Saharan Africa held 80.2% of combined DALYs, and western sub-Saharan Africa alone 49.7%. Absolute SDI-related gaps narrowed between 1990 and 2023, but relative concentration of malaria burden in low-SDI countries did not change, and most inequality lay between super-regions. Most NTD burden was disability rather than death, which mortality-based evaluations of aid omit. Thirty-four countries where high NTD burden coincides with high external financing dependence held 27.2% of global NTD DALYs and 52.3% of malaria DALYs. Across seven panel estimators, the inverse between-country association of external financing share with NTD burden was not detectable within countries over time, and the malaria association depended on the covariance estimator. We also provide country-level estimates of NTD and malaria DALYs at risk under specified funding-cut scenarios.', template=body_tpl)
x = new_par_after(x, '', template=body_tpl, runs=[('Implications of all the available evidence', True, None)])
x = new_par_after(x, 'NTD and malaria burden remains most concentrated where financing dependence is greatest, so the 2025 reductions in development assistance fall disproportionately on the most affected populations. The convergence of burden, inequality and financing evidence supports protecting continuity of services in high-burden, high-dependence countries. Aggregate external-financing shares should not, however, be read as disease-specific effects; estimating the consequences of the cuts requires programme-level disbursement data linked to coverage and disease-specific outcomes, with domestic resource mobilisation planned alongside disease priorities.', template=body_tpl)

# ---------------- Introduction ----------------
p = find('Analyses of GBD 2021 data show')
IA(p, 'indicating that falling burden does not necessarily narrow proportional differences between countries.',
   ' Feng et al. (2025) reported the same divergence using slope and concentration indices, but neither study tested geographical clustering or decomposed inequality between and within regions.')
p = find('We examine NTD and malaria burden across 204')
R(p, 'We assess spatial clustering, socioeconomic inequality and disparities within and between super-regions,',
  'We disaggregate burden to the 21 GBD regions and to countries, separate disability from premature mortality, and assess spatial clustering and absolute and relative socioeconomic inequality from 1990 to 2023, including disparities within and between super-regions,')

# ---------------- Methods ----------------
p = find('Descriptive analyses covered 204 GBD locations')
IA(p, 'the original Theil analysis also excluded zero-rate locations.',
   ' Inequality time series used all 204 locations, with GBD population for 1990 and population implied by GBD all-age counts and crude rates for 2010 and 2023.')
p = find('GBD 2023 supplied annual all-age DALY counts')
IA(p, 'The 19 component DALY counts reproduced the 2023 NTD total.',
   ' Country-level age-standardised rates and counts for 1990 and 2010 supported the inequality time series and national comparisons. We extracted the same measures for the 21 GBD regions, including the four sub-Saharan African regions, and 2023 YLDs and YLLs for each super-region to separate non-fatal from fatal burden.')
IA(p, 'Percentage changes and their UIs were imported from GBD rather than calculated from endpoint bounds.',
   ' GBD does not publish changes for NTDs excluding malaria or country-level changes for malaria alone; we computed these from point estimates and report them without intervals.')
p = find('WHO-reported indicators provided outcomes')
IA(p, 'malaria incidence per 1000 people at risk (SDG 3.3.3) (United Nations Statistics Division, n.d.; World Health Organization, 2020).',
   ' Spearman rank correlations between these series and GBD rates in 2010 and 2023 provided external triangulation of the GBD estimates.')
p = find('We summarised 2023 all-age DALY counts')
IA(p, 'Cause-specific estimates are provided in Table S2.',
   ' Estimates for the 21 GBD regions (Table S16; Figure S2), the YLD–YLL composition (Table S17; Figure S3) and national and cause-specific rankings (Tables S18–S20) extend this description.')
R(p, 'ranking countries from lowest to highest 2023 SDI', 'ranking countries by SDI in the same year, for 1990, 2010 and 2023')
IA(p, 'using the percentile method.',
   ' Absolute inequality was measured by the slope index of inequality (SII), the population-weighted regression slope of the age-standardised rate on fractional SDI rank, which estimates the difference between the highest- and lowest-SDI ends of the distribution; the relative SII divides it by the weighted mean rate (Mackenbach & Kunst, 1997). Changes in the concentration index and relative SII from 1990 and 2010 to 2023 were estimated with paired bootstrap resampling of countries.')
p = find('We calculated the population-weighted Theil T index')
IA(p, '(Shorrocks, 1980; Theil, 1967).', ' The decomposition was repeated for 1990 and 2010 (Table S15; Figure S1).')
p = find('Spatial dependence was assessed before regression')
IA(p, 'Cluster maps are shown in Figure 5.',
   ' Global and local Moran statistics were repeated for 1990 and 2010 to assess the persistence of clusters (Table S21; Figure S4).')
p = find('The primary analysis used within-country variation')
R(p, '(Table S15)', '(Table S22)')
p = find('The original analysis used two conditional scenarios')
R(p, 'The original analysis used two', 'We used two')
R(p, 'Scenario estimates retained below, in Table 4 and in Figure 8 are provisional: the available data do not support the stated 19-cause NTD accounting calculation, and the malaria econometric conversion requires correction. ', '')
p = find('The accounting script summed')
R(p, 'The accounting script summed', 'The accounting model summed')
R(p, 'Five 2010 NTD cause baselines were absent from the supplied extracts: other NTDs, yellow fever, Ebola, Guinea worm disease and Zika. The script replaced these missing values with near-zero counts. That substitution is unsupported, and the resulting NTD projections cannot be treated as validated estimates.',
  'All 19 NTD causes, including other NTDs, yellow fever, Ebola, Guinea worm disease and Zika, had GBD 2023 baselines for 2010.')
R(p, 'The econometric script recalculated', 'The econometric model recalculated')
R(p, 'For malaria, the outcome is log(1 + rate), so this proportional count conversion is only an approximation and must be replaced by an explicitly defined rate-scale calculation.',
  'For malaria, whose outcome is log(1 + rate), the change was applied on the (1 + rate) scale, converted to the implied proportional change in each country’s age-standardised rate, and applied to baseline all-age DALYs.')
p = find('Analyses used Python')
R(p, 'cand be found on this GitHub repository', 'can be found in the project GitHub repository [URL to be added]')

# ---------------- Results ----------------
p = find('The supplied GBD global aggregate reports')
IA(p, 'is not a sum of country bounds.',
   ' GBD country rates agreed closely with WHO surveillance series in 2023: Spearman ρ was 0.81 (n = 170) between NTD DALY rates and people requiring NTD interventions per capita, and 0.94 (n = 79) between malaria DALY rates and WHO malaria incidence (both p < .001; Table S21).')
cap3 = find('Figure  SEQ Figure \\* ARABIC 3') if False else [p for p in body.iter(q('p')) if ptext(p).startswith('Figure') and 'Cause-specific burden by GBD super-region' in ptext(p)][0]
sub_tpl = find('Global and super-regional burden in 2023')
x = new_par_after(cap3, '', template=sub_tpl, runs=[('Regional and national burden and its fatal and non-fatal composition', None, None)])
x = new_par_after(x, 'Western sub-Saharan Africa accounted for 49.7% of global combined DALYs (35.17 million; 95% UI 16.61–60.58 million), eastern sub-Saharan Africa for 16.7% and central sub-Saharan Africa for 13.4%, compared with 0.4% for southern sub-Saharan Africa (Table S16; Figure S2). Age-standardised rates were 5556.5 per 100 000 in western, 5006.5 in central, 2190.8 in eastern and 314.2 in southern sub-Saharan Africa; malaria contributed 4828.5, 4104.3, 1640.6 and 54.0 of these rates, respectively. Outside Africa, Oceania had the highest combined rate (1694.8), of which malaria contributed 1217.7. For NTDs excluding malaria, South Asia held the largest regional share of global DALYs (25.0%), followed by western (20.7%) and eastern sub-Saharan Africa (12.3%).', template=body_tpl)
x = new_par_after(x, 'Burden was concentrated in few countries. India (4.00 million DALYs), Nigeria (2.10 million) and China (1.30 million) contributed 38.5% of NTD DALYs, and the ten largest contributors 62.4%. Nigeria (16.63 million) and the Democratic Republic of the Congo (6.46 million) contributed 44.8% of malaria DALYs, and the ten largest contributors, all in sub-Saharan Africa, 71.8%. The highest age-standardised NTD rates were in South Sudan (2227.1 per 100 000), the Central African Republic (2207.7) and Afghanistan (1450.5); the highest malaria rates were in Sierra Leone (8237.2), Niger (5902.2) and Liberia (5502.5; Table S18). By cause, India accounted for 53.3% of global lymphatic filariasis DALYs and 42.5% of dengue DALYs, China for 75.6% of food-borne trematodiasis DALYs, Brazil for 58.2% of Chagas disease DALYs, the Democratic Republic of the Congo for 42.3% of onchocerciasis DALYs and Afghanistan for 26.8% of leishmaniasis DALYs (Table S20).', template=body_tpl)
x = new_par_after(x, 'Disability accounted for 62.4% of NTD DALYs globally (12.01 million YLDs and 7.24 million YLLs), ranging from 54.6% in sub-Saharan Africa to 94.5% in Central Europe, Eastern Europe and Central Asia. Premature death accounted for 95.2% of malaria DALYs (49.10 million YLLs; Table S17; Figure S3).', template=body_tpl)
p = find('The global age-standardised NTD and malaria DALY rate declined from')
x = new_par_after(p, 'All four sub-Saharan African regions had declines in the combined rate between 2010 and 2023, from 34.1% (95% UI 20.5–51.9) in western to 39.9% (31.4–47.8) in southern sub-Saharan Africa. Among the 21 regions, the malaria rate rose only in North Africa and the Middle East (26.3%, 0.1–46.4) and fell to zero in Central Asia, Southern Latin America and Western Europe (Table S16). Of 204 countries, 78 had a significant decline in the combined rate, 122 had changes whose UIs included zero, and four had significant increases: Nicaragua (105.0%, 46.2–178.8), Fiji (92.5%, 62.7–132.2), Monaco (88.8%, 16.9–242.3) and American Samoa (56.2%, 20.4–91.4). Point estimates of the malaria rate were higher in 2023 than in 2010 in 13 countries, including Burundi (4685.9 to 5229.5 per 100 000), Madagascar (1679.6 to 1941.9), Zambia (1864.2 to 1973.1) and Kenya (380.1 to 475.3; Table S19).', template=body_tpl)
p = find('After false-discovery-rate adjustment, NTD burden')
IA(p, 'Central Europe, Eastern Europe and Central Asia.',
   ' Clusters were stable over time: all 47 NTD high–high locations of 2010 remained so in 2023, with Somalia added; for malaria, Comoros and Somalia joined the high–high cluster and none left (Table S21; Figure S4).')
IA(p, 'and −0.80 (−0.88 to −0.65) for malaria.',
   ' Relative concentration changed little over time: in 1990 the indices were −0.51 (−0.64 to −0.36) for NTDs and −0.80 (−0.88 to −0.63) for malaria. The NTD index rose by 0.05 (0.02 to 0.08) between 2010 and 2023, whereas its change from 1990 (0.08, −0.04 to 0.18) and all malaria changes had intervals including zero. Absolute inequality narrowed: the NTD slope index of inequality fell from −1966 (−3053 to −1198) DALYs per 100 000 in 1990 to −632 (−877 to −412) in 2023, and the malaria index from −3806 (−6754 to −1974) to −2484 (−4271 to −1131; Table S15; Figure S1).')
IA(p, 'within-super-region differences accounted for 36.6% and 21.1%.',
   ' On a common 204-location basis, NTD Theil T fell from 0.64 in 1990 to 0.43 in 2023 and its between-super-region share from 75.3% to 64.0%; malaria Theil T fell from 1.62 to 1.34, with a stable between-super-region share (80.3% and 79.3%).')
R(p, '(Table S15)', '(Table S22)')
p = find('Excluding filled model inputs gave')
R(p, 'Tables S10b and S15', 'Tables S10b and S22')
p = find('The econometric model projected 25 000')
R(p, ''.join(t.text or '' for r in p if r.tag==q('r') for t in r.findall('w:t', ns)), 'Under the reference scenario (19–26% cut), the accounting model projected 406 600 excess NTD DALYs per year (95% UI 334 500–501 800) and 1.85 million excess malaria DALYs (1.51–2.21 million), equivalent to 2.2% and 3.6% of 2023 burden. Mild cuts projected 182 400 (93 900–276 700) NTD and 825 100 (433 500–1 244 100) malaria DALYs; severe cuts projected 908 700 (708 000–1 140 400) and 4.10 million (3.25–5.07 million), or 4.8% and 8.0% of 2023 burden (Table 4; Figure 8A–B). The econometric model gave smaller projections: 24 500 excess NTD DALYs (−42 100 to 90 300) and 1.22 million malaria DALYs (0.27–2.29 million) in the reference scenario.')
p = find('Sub-Saharan Africa accounted for 94% of projected')
R(p, 'accounted for 94% of projected', 'accounted for 91% of projected')
R(p, 'the Democratic Republic of the Congo (95 800; 95% UI 70 400–129 200), South Sudan (23 800), Uganda (21 300), Tanzania (20 800) and Ethiopia (15 000; Table S8)',
  'the Democratic Republic of the Congo (109 900; 95% UI 83 600–145 100), Ethiopia (34 700), Tanzania (32 000), Uganda (31 000) and South Sudan (28 300; Table S8)')
R(p, 'South Sudan (207), the Democratic Republic of the Congo (91), Uganda (44), Tanzania (31), Liberia (30) and Mozambique (29; Figure 8C)',
  'South Sudan (246), the Democratic Republic of the Congo (104), Uganda (64), Somalia (56), Liberia (53) and Zambia (49; Figure 8C)')
R(p, 'US$0.32 billion annually for NTDs (95% UI 0.24–0.47)', 'US$0.55 billion annually for NTDs (95% UI 0.45–0.72)')
R(p, 'US$0.16–0.95 billion for NTDs', 'US$0.28–1.66 billion for NTDs')
p = find('The original independent-draw sensitivity')
R(p, ''.join(t.text or '' for r in p if r.tag==q('r') for t in r.findall('w:t', ns)), 'With independent rather than correlated 2010 and 2023 burden draws, reference-scenario projections were 410 000 excess NTD DALYs (95% UI 320 000–534 000) and 2.00 million excess malaria DALYs (1.29–2.92 million): the intervals widened but the medians changed little (Table S7).')

# ---------------- Discussion ----------------
p = find('Sub-Saharan Africa carried 80.2%')
IA(p, 'since 2010.', ' Western and central sub-Saharan Africa alone held 63.1% of global combined DALYs.')
p = find('The continuing concentration of burden in sub-Saharan Africa')
IA(p, 'despite declining global age-standardised rates (He et al., 2025; Lin et al., 2025).',
   ' Our 2023 global total of 70.8 million DALYs is close to the 71.6 million reported for 2021 from GBD 2021 (Zheng et al., 2025); because each GBD round re-estimates the full series, the two figures do not measure change between 2021 and 2023.')
IA(p, 'within a broader commitment to geographical equity (WHO, 2020).',
   ' National concentration sharpens this point: three countries held 38.5% of NTD DALYs and two held 44.8% of malaria DALYs, so trends in India, Nigeria, China and the Democratic Republic of the Congo will largely shape global totals.')
p = find('Spatial clustering and socioeconomic concentration described')
IA(p, 'located burden disproportionately among lower-SDI populations.',
   ' The time series adds a distinction that single-year analyses cannot make: between 1990 and 2023 the absolute SDI gradient narrowed by about two-thirds for NTDs and one-third for malaria, while relative concentration of malaria in low-SDI countries did not change and that of NTDs eased only after 2010. This is consistent with the narrowing absolute but not relative inequality reported from GBD 2021 (Feng et al., 2025; Lin et al., 2025), and indicates that falling averages have not shifted burden away from the poorest countries. Stable high–high clusters across 2010–2023 point the same way.')
p = find('The NTD financing association changed from')
IA(p, 'are not interchangeable outcomes or exposures (Cavalcanti et al., 2025; A. F. da Silva et al., 2026).',
   ' The distinction is substantive: 62.4% of NTD DALYs in 2023 were years lived with disability, which mortality-based evaluations of aid do not capture, whereas 95.2% of malaria DALYs were years of life lost.')
p = find('The scenario analyses address a different question')
R(p, 'Their numerical health-loss estimates remain provisional because the accounting analysis lacks five historical NTD cause baselines and the malaria econometric calculation requires a corrected conversion from log-transformed rates. Consequently, the retained projections cannot yet establish the magnitude of excess DALYs.',
  'Under the reference cut, the accounting model projected 0.41 million excess NTD DALYs and 1.85 million excess malaria DALYs per year, whereas the econometric model projected 0.02 million and 1.22 million. The 17-fold difference for NTDs follows from the weak within-country association and marks the range of structural uncertainty rather than a precise estimate.')
R(p, 'but narrower simulation intervals cannot compensate for an unsupported baseline or an incorrect outcome conversion (Briggs et al., 2012)',
  'because simulation intervals reflect parameter uncertainty within each model, not the choice between models (Briggs et al., 2012)')
p = find('Published disruption models provide relevant comparators')
R(p, 'without validating these provisional magnitudes', 'without validating these magnitudes')
p = find('The study brings together burden distributions')
IA(p, 'analyses using related GBD releases are therefore not independent validation datasets (GBD 2023 Disease and Injury and Risk Factor Collaborators, 2025).',
   ' Close rank agreement with WHO surveillance series (ρ = 0.81 for NTDs and 0.94 for malaria) supports the between-country ordering, not the absolute levels. Country-level changes for NTDs excluding malaria and for malaria alone were computed from point estimates without uncertainty.')
R(p, 'The provisional spatial-panel, prediction and scenario outputs', 'The provisional spatial-panel and prediction outputs')
p = find('The evidence supports prioritising continuity')
R(p, 'requires corrected calculations and more direct measurement', 'requires more direct measurement')

# ---------------- References ----------------
def ref_after(anchor_start, runs):
    a = find(anchor_start); new_par_after(a, '', template=a, runs=runs)
ref_after('Elhorst, J. P. (2014)', [('Feng, L., Mo, G., Liu, Z., & Liu, Q. (2025). Global, regional, national burden, trends and health inequality of neglected tropical diseases and malaria from 1990 to 2021. ', False, False), ('BMC Infectious Diseases, 25', False, True), (', Article 1649. https://doi.org/10.1186/s12879-025-12068-x', False, False)])
ref_after('Lundberg, S. M., & Lee', [('Mackenbach, J. P., & Kunst, A. E. (1997). Measuring the magnitude of socio-economic inequalities in health: An overview of available measures illustrated with two examples from Europe. ', False, False), ('Social Science & Medicine, 44', False, True), ('(6), 757–771. https://doi.org/10.1016/S0277-9536(96)00073-1', False, False)])
ref_after('World Health Organization Regional Office for Africa. (2025)', [('Zheng, J.-X., Liu, Y., Guan, S.-Y., Guo, Z.-Y., Duan, L., Lv, S., Zhang, S.-X., Li, S.-Z., Zhou, X.-N., & Feng, X.-Y. (2025). Global, regional, and national burden of neglected tropical diseases and malaria in the general population, 1990–2021: Systematic analysis of the global burden of disease study 2021. ', False, False), ('Journal of Advanced Research, 79', False, True), (', 769–781. https://doi.org/10.1016/j.jare.2025.04.004', False, False)])

# ---------------- Tables in manuscript ----------------
p = [p for p in body.iter(q('p')) if 'Provisional annual DALY projections under development-assistance cuts' in ptext(p)][0]
R(p, 'Provisional annual DALY projections under development-assistance cuts', 'Projected Excess Annual DALYs Under Development-Assistance Cut Scenarios, Low- and Middle-Income Countries')
p = find('Note. The accounting model multiplies')
R(p, 'All values are retained original outputs, not validated revised projections. Missing NTD baselines and the malaria outcome transformation require correction before finalisation.',
  'NTD baselines cover all 19 causes; malaria projections are computed on the (1 + rate) scale of the fitted model.')
p = find("Note. Moran's I and local indicators")
R(p, 'Table S15 gives', 'Table S22 gives')
tbl = body.findall('.//w:tbl', ns)[3]
CH = {2: {1: '182 [94, 277]', 2: '1.0', 3: '91', 5: '0.25 [0.13, 0.39]'}, 3: {4: '490 [107, 1,116]'},
      5: {1: '407 [335, 502]', 2: '2.2', 3: '91', 5: '0.55 [0.45, 0.72]'}, 6: {4: '1,222 [270, 2,288]'},
      8: {1: '909 [708, 1,140]', 2: '4.8', 3: '91', 5: '1.24 [0.95, 1.62]'}, 9: {4: '3,060 [701, 5,972]'}}
rows = tbl.findall('w:tr', ns)
for ri, cells in CH.items():
    tcs = rows[ri].findall('w:tc', ns)
    for ci, val in cells.items():
        cp = tcs[ci].find('w:p', ns); R(cp, ''.join(t.text or '' for r in cp if r.tag==q('r') for t in r.findall('w:t', ns)), val)
tree.write(P, xml_declaration=True, encoding='UTF-8', standalone=True)
print('done')
