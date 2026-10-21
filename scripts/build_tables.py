import json
"""Assemble APA-style tables (main + supplementary) as JSON for docx rendering."""
import pandas as pd, numpy as np, json
R='results'; T=[]
f0=lambda v: f'{v:,.0f}'; f1=lambda v: f'{v:,.1f}'; f2=lambda v: f'{v:.2f}'
def pfmt(p): return '< .001' if p<0.001 else f'{p:.3f}'.lstrip('0') if p<1 else '1.000'
def ci(a,lo,hi,d=1): return f'{a:,.{d}f} [{lo:,.{d}f}, {hi:,.{d}f}]'
SH={'Southeast Asia, East Asia, and Oceania':'Southeast Asia, East Asia, and Oceania','Central Europe, Eastern Europe, and Central Asia':'Central Europe, Eastern Europe, and Central Asia'}
# ---------- Table 1 ----------
t1=pd.read_csv(f'{R}/table1_superregion_burden.csv',index_col=0); pc=pd.read_csv('data/raw/gbd/superregion_pctchange__ntdm__dalys__2010_2023.csv').set_index('location_name')
rows=[]
for s,r in t1.iterrows():
    q=pc.loc[s]; rows.append([s,f0(r.countries),f1(r.pop_m),f'{r.dalys_ntd_m:.2f} ({r.dalys_ntd_share:.1f})',f1(r.asr_ntd_2023),f'{r.dalys_mal_m:.2f} ({r.dalys_shareal_share:.1f})',f1(r.asr_mal_2023),ci(q.pc_rate_agestd,q.pc_rate_agestd_lo,q.pc_rate_agestd_hi)])
tot=t1.sum(); q=pc.loc['Global']
rows.append(['Global',f0(tot.countries),f1(tot.pop_m),f'{tot.dalys_ntd_m:.2f} (100)','—',f'{tot.dalys_mal_m:.2f} (100)','—',ci(q.pc_rate_agestd,q.pc_rate_agestd_lo,q.pc_rate_agestd_hi)])
T.append({'id':'Table 1','title':'Burden of Neglected Tropical Diseases and Malaria by GBD Super-Region, 2023','cols':['Super-region','Countries','Population (millions)','NTD DALYs, millions (% of global)','NTD age-standardised rate','Malaria DALYs, millions (% of global)','Malaria age-standardised rate','% change in age-standardised NTD + malaria DALY rate, 2010–2023 [95% UI]'],
 'rows':rows,'widths':[2.3,0.8,1.0,1.4,1.1,1.4,1.1,1.9],'note':'NTD = neglected tropical diseases (19 GBD causes, excluding malaria); DALY = disability-adjusted life-year; UI = uncertainty interval. Rates are age-standardised DALYs per 100 000 population. Percentage changes are GBD 2023 published estimates; UIs are the 2.5th–97.5th percentiles of draw-level changes. Population from World Bank WDI (latest year). Source: GBD 2023 (IHME).','main':True})
# ---------- Table 2 ----------
K=json.load(open(f'{R}/key_numbers.json')); l=pd.read_csv(f'{R}/spatial_lisa_country.csv'); ineq=K['inequality']
rows=[]
for nm,key,col in [('NTDs (excl. malaria)','ntd','lisa_ntd_fdr'),('Malaria','mal','lisa_mal_fdr')]:
    sp=K['spatial'][key]; v=l[col].value_counts(); i=ineq['NTDs (excl. malaria)' if key=='ntd' else 'Malaria']
    rows.append([nm,f2(sp['I']),f2(sp['z']),'< .001',str(v.get('High–High',0)),str(v.get('Low–Low',0)),str(v.get('High–Low',0)+v.get('Low–High',0)),f"{i['CI']:.2f} [{i['lo']:.2f}, {i['hi']:.2f}]",f"{i['Theil']:.2f}",f"{i['between_pct']:.1f} / {i['within_pct']:.1f}"])
T.append({'id':'Table 2','title':'Spatial Autocorrelation and Socioeconomic Inequality in Age-Standardised DALY Rates, 2023','cols':['Outcome',"Global Moran's I",'z','p','High–High clusters (n)','Low–Low clusters (n)','Spatial outliers (n)','Concentration index by SDI [95% CI]','Theil T','Between / within super-region (%)'],
 'rows':rows,'widths':[1.6,0.9,0.7,0.7,0.9,0.9,0.9,1.7,0.7,1.3],'note':"Moran's I and local indicators of spatial association (LISA) computed on log(1 + rate) with row-standardised k = 6 nearest-neighbour weights and 9 999 permutations; LISA clusters reported at Benjamini–Hochberg false-discovery-rate q < .05 (n = 203 countries with geometry). Concentration index is population-weighted, ranking countries by Socio-demographic Index (SDI); negative values indicate burden concentrated in low-SDI countries; 95% CI from 2 000 bootstrap resamples. Theil T is population-weighted and decomposed into between- and within-super-region components.",'main':True})
# ---------- Table 3 ----------
mc=pd.read_csv(f'{R}/model_comparison_external_share.csv'); rows=[]; groups=[]
fams=['Between-country (2023 cross-section)','Within-country panel (2007–22)','Spatial panel (2007–22)']
for f in fams:
    rows.append({'group':f})
    for m in mc[mc.family==f].model.unique():
        a=mc[(mc.family==f)&(mc.model==m)&(mc.outcome=='NTDs (excl. malaria)')].iloc[0]; b=mc[(mc.family==f)&(mc.model==m)&(mc.outcome=='Malaria')].iloc[0]
        lab=('Two-way FE, Driscoll–Kraay SE (preferred)' if m=='Two-way FE (Driscoll–Kraay)' else m)
        rows.append([lab,ci(a.pct,a.pct_lo,a.pct_hi,2),pfmt(a.p),f0(a.n),ci(b.pct,b.pct_lo,b.pct_hi,2),pfmt(b.p),f0(b.n)])
T.append({'id':'Table 3','title':'Association Between External (Donor) Share of Health Expenditure and Age-Standardised DALY Rates Across Estimators','cols':['Estimator','NTDs: % change [95% CI]','p','n','Malaria: % change [95% CI]','p','n'],
 'rows':rows,'widths':[3.0,2.1,0.7,0.8,2.1,0.7,0.8],'note':'Estimates are percentage changes in the age-standardised DALY rate per 10-percentage-point increase in the external share of current health expenditure, adjusted for income (log LDI), UHC index, basic sanitation and drinking-water coverage, and (panel models) log domestic government health spending per capita; panel exposures lagged 2 years. NTD models: low- and middle-income countries (LMICs); malaria models: malaria-endemic LMICs. n = countries (cross-section) or country-years (panel). FE = fixed effects; CRE = correlated random effects; SAR = spatial autoregressive; SEM = spatial error model. Spatial panel models include country and year fixed effects (balanced panels; KNN k = 6 weights); SAR rows show the coefficient β, with direct, indirect and total associations in Table S12. Preferred estimator selected on the basis of Hausman and Mundlak tests (rejecting random effects) and evidence of cross-sectional dependence, serial correlation and heteroskedasticity (Table S3), for which Driscoll–Kraay standard errors are robust.','main':True})
# ---------- Table 4 ----------
s=pd.read_csv(f'{R}/scenario_v2_superregion.csv'); rows=[]
for sc_,lab in [('Mild','Mild (5–15% cut)'),('Reference','Reference (19–26% cut)'),('Severe','Severe (40–60% cut)')]:
    rows.append({'group':lab})
    for o in ['NTDs (excl. malaria)','Malaria']:
        a=s[(s.scenario==sc_)&(s.outcome==o)&(s.super_region=='All LMICs')].iloc[0]; ss=s[(s.scenario==sc_)&(s.outcome==o)&(s.super_region=='Sub-Saharan Africa')].iloc[0]
        rows.append([o,ci(a.A_excess/1e3,a.A_lo/1e3,a.A_hi/1e3,0),f'{a.A_pct_2023:.1f}',f'{100*ss.A_excess/a.A_excess:.0f}',ci(a.B_excess/1e3,a.B_lo/1e3,a.B_hi/1e3,0),ci(a.A_value_usd/1e9,a.A_value_lo/1e9,a.A_value_hi/1e9,2)])
T.append({'id':'Table 4','title':'Projected Excess Annual DALYs Under Development-Assistance Cut Scenarios, Low- and Middle-Income Countries','cols':['Outcome','Accounting model: excess DALYs, thousands [95% UI]','% of 2023 burden','Sub-Saharan Africa share (%)','Econometric model: excess DALYs, thousands [95% UI]','Economic value, US$ billions [95% UI]'],
 'rows':rows,'widths':[2.0,2.4,1.0,1.2,2.4,1.9],'note':'Accounting ("gains-at-risk") model: excess = reduction in all-age DALY rate 2010–2023 × 2023 population × external share of health expenditure × proportional cut; GBD uncertainty propagated through 4 000 Monte Carlo draws with rank-correlated 2010/2023 draws and cut magnitude sampled uniformly within the scenario range. Econometric model: preferred two-way FE (Driscoll–Kraay) coefficient applied to the cut-induced fall in external share. The reference range brackets the IHME preliminary 22% decline in global development assistance for health, 2024–2025. Economic value at 1 × GDP per capita per DALY (see Table S7 for 0.5× and 3×). Estimates represent the annual burden associated with reversal of donor-attributable gains, not first-year effects.','main':True})
# ================= Supplementary =================
rows=[['GBD 2023 (IHME)','Age-standardised and all-age DALY rates and counts, deaths, prevalence, 95% UIs','19 NTD causes + malaria; 204 countries; 1990–2023 (annual 2005–2023)','Outcome'],
['GBD 2023 covariates','Socio-demographic Index; UHC effective coverage index; lag-distributed income (LDI)','204 countries; 2005–2023','Covariates'],
['World Bank WDI','Current, domestic government, external and out-of-pocket health expenditure; GDP/GNI per capita; ODA; population; rural share; WASH; poverty','2005–2024','Exposure, covariates'],
['WHO via UN SDG database','SDG 3.3.5 people requiring interventions against NTDs; SDG 3.3.3 malaria incidence','194 countries; 2010–2024','Independent outcome (sensitivity)'],
['IHME Financing Global Health 2025','Development assistance for health 2021–2025, by source','Global','Scenario calibration'],
['USAID NTD Program','Programme countries (n = 32)','2006–2025','Sensitivity analysis'],
['Natural Earth','Admin-0 boundaries, 1:50 m','—','Spatial weights, maps']]
T.append({'id':'Table S1','title':'Data Sources and Variables','cols':['Source','Variables','Coverage','Role'],'rows':rows,'widths':[2.2,4.3,2.4,1.6],'note':'Accessed 7 October 2026. WHO Global Health Observatory API returned server errors on the access date; SDG-database series carry the same WHO-reported indicators.'})
cb=pd.read_csv(f'{R}/cause_by_superregion_dalys.csv',index_col=0); gl=cb.sum(1).sort_values(ascending=False)
NM={'malaria':'Malaria','other_neglected_tropical_diseases':'Other NTDs','dengue':'Dengue','schistosomiasis':'Schistosomiasis','intestinal_nematode_infections':'Soil-transmitted helminthiases','lymphatic_filariasis':'Lymphatic filariasis','cysticercosis':'Cysticercosis','leishmaniasis':'Leishmaniasis','food_borne_trematodiases':'Food-borne trematodiases','onchocerciasis':'Onchocerciasis','rabies':'Rabies','yellow_fever':'Yellow fever','chagas_disease':'Chagas disease','trachoma':'Trachoma','cystic_echinococcosis':'Cystic echinococcosis','african_trypanosomiasis':'Human African trypanosomiasis','leprosy':'Leprosy','zika_virus':'Zika virus','ebola':'Ebola','guinea_worm_disease':'Guinea worm disease'}
cols=['Sub-Saharan Africa','South Asia','Southeast Asia, East Asia, and Oceania','Latin America and Caribbean','North Africa and Middle East','Central Europe, Eastern Europe, and Central Asia','High-income']
fmtk=lambda v: f'{v/1e3:,.1f}' if v>=50 else ('< 0.1' if v<50 and v>0 else '0')
rows=[[NM[c]]+[fmtk(cb.loc[c,k]) for k in cols]+[f'{gl[c]/1e3:,.1f}'] for c in gl.index if c in NM]
T.append({'id':'Table S2','title':'DALYs (Thousands) by Cause and GBD Super-Region, 2023','cols':['Cause','Sub-Saharan Africa','South Asia','SE Asia, E Asia & Oceania','Latin America & Caribbean','N Africa & Middle East','C Europe, E Europe & C Asia','High-income','Global'],
 'rows':rows,'widths':[2.3,1.0,0.9,1.1,1.1,1.0,1.1,0.9,0.9],'note':'All-age DALY counts summed over countries, GBD 2023.'})
dg=json.load(open(f'{R}/panel_assumption_tests.json')); rows=[]
for k,v in dg.items():
    if 'per-capita' in k: continue
    o=k.split(' | ')[0]
    rows+= [[o,'Hausman (FE vs RE)',f"χ²({v['Hausman_df']}) = {v['Hausman_chi2']:.1f}",pfmt(v['Hausman_p']),'Reject RE → fixed effects'],
            [o,'Mundlak (robust, clustered)',f"Wald χ²(6) = {v['Mundlak_Wald']:.1f}",pfmt(v['Mundlak_p']),'Reject RE' if v['Mundlak_p']<.05 else 'Not rejected; FE retained for consistency'],
            [o,'Breusch–Pagan LM (RE vs pooled)',f"χ²(1) = {v['BreuschPagan_LM_RE']:,.0f}",pfmt(v['BP_p']),'Country heterogeneity present → not pooled OLS'],
            [o,'Pesaran CD (cross-sectional dependence)',f"CD = {v['Pesaran_CD']:.2f}",pfmt(v['CD_p']),'Dependence → Driscoll–Kraay SE, spatial panel'],
            [o,'Wooldridge (AR(1) serial correlation)',f"F(1, {v['N']-1}) = {v['Wooldridge_AR1_F']:.1f}",pfmt(v['Wooldridge_p']),'Serial correlation → robust SE, first differences'],
            [o,'Modified Wald (groupwise heteroskedasticity)',f"χ²({v['ModWald_df']}) = {v['ModWald_hetero_chi2']:,.0f}",pfmt(v['ModWald_p']),'Heteroskedasticity → robust SE'],
            [o,'Variance inflation factor (max)',f"{max(v['VIF'].values()):.1f}",'—','Acceptable (< 10)']]
T.append({'id':'Table S3','title':'Panel-Model Specification and Assumption Tests','cols':['Outcome','Test','Statistic','p','Implication'],'rows':rows,'widths':[1.7,3.0,2.0,0.8,3.0],'note':'Tests applied to the two-way FE specification with external share (lag 2). NTD sample: 153 LMICs, 2007–2022; malaria sample: 77 malaria-endemic LMICs.'})
pf=pd.read_csv(f'{R}/preferred_model_full.csv'); rows=[]
for o in ['NTDs (excl. malaria)','Malaria']:
    rows.append({'group':f"{o}: n = {pf[pf.outcome==o].n_obs.iloc[0]:,} country-years, {pf[pf.outcome==o].N.iloc[0]} countries; within R² = {pf[pf.outcome==o].r2_within.iloc[0]:.2f}"})
    for _,r in pf[pf.outcome==o].iterrows(): rows.append([r.term,f'{r.b:.3f}',f'{r.se:.3f}',ci(r.pct,r.pct_lo,r.pct_hi,2),pfmt(r.p)])
T.append({'id':'Table S4','title':'Preferred Model: Two-Way Fixed Effects With Driscoll–Kraay Standard Errors','cols':['Covariate','b','SE','% change [95% CI]','p'],'rows':rows,'widths':[3.6,0.9,0.9,2.4,0.8],
 'note':'Outcome: log age-standardised DALY rate (malaria: log[1 + rate]); country and year fixed effects; Driscoll–Kraay SE (Bartlett kernel, bandwidth 3). The positive UHC coefficient for malaria is considered non-interpretable: the GBD UHC effective-coverage index is partly derived from GBD cause-specific outcomes, creating mechanical dependence (see audit, item 7).'})
ml=pd.read_csv(f'{R}/ml_model_comparison.csv'); rows=[[r.cv,r.model,f'{r.RMSE_log:.3f}',f'{r.MAE_log:.3f}',f'{r.R2:.3f}'] for r in ml.itertuples()]
T.append({'id':'Table S5','title':'Out-of-Sample Predictive Performance of Machine-Learning and Panel Models (NTD Outcome)','cols':['Validation scheme','Model','RMSE','MAE','R²'],'rows':rows,'widths':[3.4,3.4,0.9,0.9,0.9],
 'note':'Outcome: log age-standardised NTD DALY rate, LMICs, 2007–2023 (n = country-years). Random k-fold validation leaks information across years of the same country and is shown only to illustrate optimism; leave-country-out and spatial-block validation estimate transportability; temporal validation estimates forecasting skill. LightGBM SHAP importance ranked external financing variables lowest of 13 features.'})
gw=json.load(open(f'{R}/gwr_summary.json')); rows=[['OLS (global)','—',f"{gw['OLS_AICc']:.1f}",f"{gw['OLS_R2']:.2f}"],['GWR (single bandwidth)',f"{gw['GWR_bw']:.0f}",f"{gw['GWR_AICc']:.1f}",f"{gw['GWR_R2']:.2f}"],['Multiscale GWR','see below',f"{gw['MGWR_AICc']:.1f}",f"{gw['MGWR_R2']:.2f}"]]
T.append({'id':'Table S6a','title':'Geographically Weighted Regression: Model Fit (LMICs, 2023, n = 145)','cols':['Model','Bandwidth (nearest neighbours)','AICc','R²'],'rows':rows,'widths':[3,2.4,1.2,1.2],'note':'Adaptive bisquare kernel on projected (Robinson) country centroids; bandwidth selected by AICc.'})
NM2={'Intercept':'Intercept','ext':'External share of CHE','uhc':'UHC index','log_ldi':'Income (log LDI)','sanit_basic_pct':'Basic sanitation'}
rows=[[NM2[k],f"{gw['MGWR_bw'][k]:.0f}",f"{v['min']:.2f}",f"{v['median']:.2f}",f"{v['max']:.2f}",f"{v['pct_sig']:.0f}"] for k,v in gw['MGWR_coef_summary'].items()]
T.append({'id':'Table S6b','title':'Multiscale GWR: Covariate-Specific Bandwidths and Local Coefficients','cols':['Covariate','Bandwidth','Minimum','Median','Maximum','Countries significant (%)'],'rows':rows,'widths':[2.6,1.1,1.0,1.0,1.0,1.6],'note':'Standardised coefficients; significance uses MGWR-corrected t-values (family-wise). A bandwidth close to n (145) indicates a global (spatially stationary) relationship; small bandwidths indicate local processes.'})
se=pd.read_csv(f'{R}/sensitivity_analyses.csv'); rows=[]
for _,r in se[se.analysis.str.startswith('S1')].iterrows(): rows.append(['Spatial weights',r.outcome,r.specification,f"Moran's I = {r.estimate:.2f}",pfmt(r.p)])
for _,r in se[se.analysis.str.startswith('S2')].iterrows(): rows.append(['Cross-section specification',r.outcome,r.specification,ci(r.estimate,r.lo,r.hi,1),pfmt(r.p)])
s2=pd.read_csv(f'{R}/scenario_v2_superregion.csv'); 
for o in ['NTDs (excl. malaria)','Malaria']:
    a=s2[(s2.scenario=='Reference')&(s2.outcome==o)&(s2.super_region=='All LMICs')].iloc[0]
    rows.append(['Scenario uncertainty',o,'Independent (uncorrelated) 2010/2023 draws',ci(a.A_indep_excess/1e3,a.A_indep_lo/1e3,a.A_indep_hi/1e3,0)+' thousand','—'])
    for mult in [0.5,3]: rows.append(['Economic valuation',o,f'{mult}× GDP per capita per DALY',f'US${mult*a.A_value_usd/1e9:.2f} billion','—'])
T.append({'id':'Table S7','title':'Sensitivity Analyses','cols':['Domain','Outcome','Specification','Estimate','p'],'rows':rows,'widths':[1.8,1.8,4.0,2.4,0.7],'note':'Cross-section estimates are % change per 1 SD of external share. The WHO-reported independent outcome (people requiring NTD interventions) shows no association, consistent with the null within-country panel estimates.'})
c=pd.read_csv(f'{R}/scenario_v2_country.csv'); r=c[(c.scenario=='Reference')&(c.outcome=='NTDs (excl. malaria)')].copy(); m=c[(c.scenario=='Reference')&(c.outcome=='Malaria')].set_index('iso3')
r['rate']=r.excess_A/r.pop2023*1e5; r=r.nlargest(25,'excess_A')
rows=[[x.location_name,x.sr,f'{100*x.ext_share:.1f}',ci(x.excess_A,x.A_lo,x.A_hi,0),f'{x.rate:.1f}',f"{m.loc[x.iso3,'excess_A']:,.0f}"] for x in r.itertuples()]
T.append({'id':'Table S8','title':'Countries With the Largest Projected Excess NTD DALYs, Reference Scenario','cols':['Country','Super-region','External share of CHE (%)','Excess NTD DALYs/year [95% UI]','Per 100 000','Excess malaria DALYs/year'],'rows':rows,'widths':[2.2,2.4,1.2,2.4,1.0,1.6],'note':'Accounting model, reference scenario (19–26% cut). Ranked by absolute excess NTD DALYs.'})
ex=pd.read_csv(f'{R}/excluded_countries_regression.csv'); ms=pd.read_csv(f'{R}/sensitivity_missingness.csv',index_col=0)
rows=[[i,f'{ms.loc[i].iloc[0]:,.1f}',f'{ms.loc[i].iloc[1]:,.1f}'] for i in ms.index]
T.append({'id':'Table S9','title':'Comparison of Countries Included and Excluded From Cross-Sectional Regression (Complete-Case)','cols':['Characteristic','Included','Excluded'],'rows':rows,'widths':[4,1.6,1.6],'note':'Excluded countries ('+', '.join(ex.location_name.tolist())+') are predominantly small island and high-income states that together account for under 2% of global NTD DALYs.'})

# ---------- Tables S10a/S10b: missing data ----------
mp=pd.read_csv(f'{R}/missing_profile.csv'); ms=json.load(open(f'{R}/missing_summary.json'))
rows=[[r.variable,f1(r.missing_raw_pct),f1(r.filled_by_rule_pct),f1(r.missing_after_pct),f0(r.countries_never_observed)] for r in mp.itertuples()]
T.append({'id':'Table S10a','title':'Extent and Pattern of Missing Data in the Panel Modelling Frame (LMICs, 2007–2022)','cols':['Variable','Missing as reported (%)','Filled by within-country rule (%)','Missing after rule (%)','Countries never observed (n)'],'rows':rows,'widths':[3.6,1.4,1.6,1.4,1.4],
 'note':f"Frame: {ms['countries']} LMICs × 16 years = {ms['country_years']:,} country-years. Rule: within-country linear interpolation of interior gaps and last observation carried forward for at most 2 years; no backward extrapolation, no cross-country borrowing, outcomes never imputed. Complete-case rows for the NTD model: {ms['complete_case_rows']:,} ({ms['complete_case_pct']}%) from {ms['countries_in_model']} countries, of which {ms['imputed_rows_in_model']} ({ms['imputed_rows_pct']}%) contain ≥1 filled value. Incompleteness was associated with lower burden (OR 0.33 per log unit, 95% CI 0.12–0.91) and earlier years (OR 0.94 per year), not with SDI (logistic model, country-clustered SE), consistent with missingness at random conditional on observed covariates. The 14 territories never reporting external health expenditure hold 0.77% of LMIC NTD DALYs."})
mss=pd.read_csv(f'{R}/missing_sensitivity.csv'); rows=[]
for o in ['NTDs (excl. malaria)','Malaria']:
    rows.append({'group':o})
    for r in mss[mss.outcome==o].itertuples():
        rows.append([r.strategy,ci(r.pct,r.lo,r.hi,2),pfmt(r.p),f0(r.n),f0(r.countries),(r.note if isinstance(r.note,str) else '—')])
T.append({'id':'Table S10b','title':'Sensitivity of the Preferred Estimate to the Missing-Data Strategy','cols':['Strategy','% change per 10 pp external share [95% CI]','p','Country-years','Countries','FMI'],'rows':rows,'widths':[3.4,2.6,0.7,1.1,1.0,1.0],
 'note':'Preferred two-way fixed-effects model (country and year fixed effects) with Driscoll–Kraay SE. MICE: chained equations with Bayesian ridge regression and posterior predictive draws, 15 iterations, m = 20, auxiliary variables (country means of observed values, SDI, LDI, UHC, year, outcome as predictor only); estimates pooled with Rubin\'s rules. FMI = fraction of missing information.'})
# ---------- Table S11: variable definitions ----------
rows=[['NTD DALY rate','GBD 2023','—','Age-standardised DALYs per 100 000, 19 causes','log','—','Outcome'],
['Malaria DALY rate','GBD 2023','—','Age-standardised DALYs per 100 000','log(1 + x)','—','Outcome'],
['External share of CHE','WDI/GHED','SH.XPD.EHEX.CH.ZS','External health expenditure, % of current health expenditure','per 10 pp','2 years','Primary exposure'],
['External health expenditure per capita','WDI/GHED','SH.XPD.EHEX.PC.CD','Current US$ per person','log(1 + x)','2 years','Secondary exposure; financing gap'],
['Domestic government health expenditure per capita','WDI/GHED','SH.XPD.GHED.PC.CD','Current US$ per person','log','2 years','Covariate; financing gap'],
['Current health expenditure per capita','WDI/GHED','SH.XPD.CHEX.PC.CD','Current US$ per person','—','—','Descriptive'],
['Out-of-pocket expenditure','WDI/GHED','SH.XPD.OOPC.CH.ZS','% of current health expenditure','none','—','Machine-learning feature'],
['Lag-distributed income (LDI)','GBD 2023','—','Per capita, international $','log','—','Covariate'],
['UHC effective-coverage index','GBD 2023','—','Index, 0–100','per 10 points','—','Covariate'],
['Socio-demographic Index (SDI)','GBD 2023','—','Composite of income, education and fertility, 0–1','none','—','Inequality ranking; sensitivity covariate'],
['Basic sanitation','WDI/JMP','SH.STA.BASS.ZS','% population with at least basic sanitation','per 10 pp','—','Covariate'],
['Basic drinking water','WDI/JMP','SH.H2O.BASW.ZS','% population with at least basic drinking water','per 10 pp','—','Covariate'],
['Rural population','WDI','SP.RUR.TOTL.ZS','% of total population','none','—','Machine-learning feature'],
['GDP per capita (PPP)','WDI','NY.GDP.PCAP.PP.KD','Constant international $','log','—','Descriptive'],
['GDP per capita (current US$)','WDI','NY.GDP.PCAP.CD','Current US$','none','—','Economic valuation'],
['Population','WDI','SP.POP.TOTL','Persons','none','—','Weights; scenario counts'],
['Net ODA received per capita','WDI','DT.ODA.ODAT.PC.ZS','Current US$ per person','none','—','Descriptive']]
T.append({'id':'Table S11','title':'Variable Definitions, Sources, Units, Transformations and Lags','cols':['Variable','Source','Indicator code','Definition and unit','Transformation','Lag','Role'],'rows':rows,'widths':[2.6,1.1,1.7,3.0,1.2,0.7,1.9],
 'note':'CHE = current health expenditure; GHED = WHO Global Health Expenditure Database; JMP = WHO/UNICEF Joint Monitoring Programme; ODA = official development assistance; PPP = purchasing power parity; pp = percentage points. Dashes in the Indicator code column denote GBD covariates, which have no WDI code.'})
# ---------- Table S12: spatial panel two-way FE ----------
sp2=pd.read_csv(f'{R}/spatial_panel_twoway.csv'); rows=[]
for o in ['NTDs (excl. malaria)','Malaria']:
    rows.append({'group':o})
    for r in sp2[sp2.outcome==o].itertuples():
        rows.append([r.model.replace(' two-way FE',''),r.effect.capitalize(),ci(r.pct,r.lo,r.hi,2),pfmt(r.p),f2(r.spatial_param),f0(r.n_countries)])
T.append({'id':'Table S12','title':'Spatial Panel Models With Country and Year Fixed Effects: Spatial Parameters and Direct, Indirect and Total Associations','cols':['Model','Quantity','% change per 10 pp [95% CI]','p','ρ or λ','Countries'],'rows':rows,'widths':[2.6,1.4,2.6,0.7,0.9,1.0],
 'note':'Balanced panels 2007–2022 (16 years). KNN (k = 6) row-standardised weights. Country effects by within transformation, year effects by cross-sectional demeaning. SAR effects follow LeSage and Pace: direct = mean diagonal of (I − ρW)⁻¹β, total = β/(1 − ρ), indirect = total − direct; 95% intervals from 2 000 draws of (β, ρ).'})
# ---------- Table S13: threats to validity ----------
rows=[['Spatial clustering is an artefact of the neighbour definition','KNN k = 4 and 8; 2 500 km distance band','Table S7'],
['Clustering reflects only high-income versus other countries','Moran\'s I within LMICs and within malaria-endemic countries','Results'],
['Between-country confounding','Two-way FE, first differences, FE with country trends and Mundlak CRE; 2010–14 exposure; exclusion of sub-Saharan Africa or high-income countries','Table 3, Table S7'],
['Circularity of GBD covariates','SDI replaces UHC and LDI; WHO-reported independent outcome (SDG 3.3.5)','Table S7'],
['Choice of exposure metric','External expenditure per capita (specification B)','Results'],
['Time-varying confounding within countries','FE with country-specific linear trends; first differences','Table 3'],
['Cross-border dependence','Two-way FE SAR and SEM; direct, indirect and total effects','Table 3, Table S12'],
['Missing data','Complete case; exclusion of filled rows; balanced panel; MICE (m = 20)','Table S10b'],
['Selection into complete-case cross-section','Included versus excluded countries','Table S9'],
['Scenario: temporal correlation of GBD uncertainty','Independent rather than comonotonic draws','Table S7'],
['Scenario: attribution share','≥80% donor attribution in 32 USAID NTD-programme countries','Results'],
['Scenario: monetary valuation','0.5× and 3× GDP per capita per DALY','Table S7']]
T.append({'id':'Table S13','title':'Threats to Validity and the Sensitivity Analyses That Address Them','cols':['Threat','Sensitivity analysis','Reported in'],'rows':rows,'widths':[3.4,4.6,1.6],'note':'All sensitivity analyses were prespecified.'})

# ---------- Table S14: domestic financing gap ----------
fg=pd.read_csv(f'{R}/scenario_financing_gap.csv'); rows=[]
order=['Sub-Saharan Africa','South Asia','North Africa and Middle East','Latin America and Caribbean','Central Europe, Eastern Europe, and Central Asia','Southeast Asia, East Asia, and Oceania']
for sc_,lab in [('Mild','Mild (5–15% cut)'),('Reference','Reference (19–26% cut)'),('Severe','Severe (40–60% cut)')]:
    rows.append({'group':lab})
    for sr in order:
        r=fg[(fg.scenario==sc_)&(fg.sr==sr)].iloc[0]
        rows.append([sr,f2(r.lost_ext_usd/1e9),f'{r.ghed_total_usd/1e9:,.1f}',f2(r.domestic_increase_needed_pct)])
T.append({'id':'Table S14','title':'Increase in Domestic Government Health Expenditure Required to Replace Lost External Funds, by Super-Region and Scenario','cols':['Super-region','Lost external funds, US$ billions','Domestic government health expenditure, US$ billions','Increase required (%)'],'rows':rows,'widths':[3.6,2.0,2.4,1.6],
 'note':'Lost external funds = midpoint of the scenario cut × external health expenditure per capita × population, summed over countries. Baseline spending is the latest available value, 2019–2023. Low- and middle-income countries with financing data (n = 153).'})

# =================== Revision tables S15–S21 ===================
SRS={'Sub-Saharan Africa':'Sub-Saharan Africa','South Asia':'South Asia','Southeast Asia, East Asia, and Oceania':'SE Asia, E Asia & Oceania','Latin America and Caribbean':'Latin America & Caribbean','North Africa and Middle East':'N Africa & Middle East','Central Europe, Eastern Europe, and Central Asia':'C Europe, E Europe & C Asia','High-income':'High-income'}
def n0(x): return f'{x:,.0f}'
# S15 inequality over time
iq=pd.read_csv(f'{R}/rev_inequality_over_time.csv'); ch=pd.read_csv(f'{R}/rev_inequality_change.csv'); rows=[]
for o in ['NTDs (excl. malaria)','Malaria']:
    rows.append({'group':o})
    for _,r in iq[iq.outcome==o].iterrows():
        rows.append([str(int(r.year)),n0(r.pop_weighted_mean),ci(r.CI,r.CI_lo,r.CI_hi,2),ci(r.SII,r.SII_lo,r.SII_hi,0),ci(r.rSII,r.rSII_lo,r.rSII_hi,2),f'{r.Theil:.2f}',f'{r.between_pct:.1f} / {r.within_pct:.1f}'])
    for _,r in ch[ch.outcome==o].iterrows():
        rows.append([f'Change {r.period}','—',ci(r.dCI,r.dCI_lo,r.dCI_hi,2),'—',ci(r.drSII,r.drSII_lo,r.drSII_hi,2),'—','—'])
T.append({'id':'Table S15a','title':'Socioeconomic Inequality in Age-Standardised DALY Rates by Socio-demographic Index, 1990, 2010 and 2023','cols':['Year','Population-weighted mean rate (per 100 000)','Concentration index [95% CI]','Slope index of inequality, per 100 000 [95% CI]','Relative SII [95% CI]','Theil T','Between / within super-region (%)'],'rows':rows,'widths':[1.5,1.6,1.9,2.3,1.8,0.9,1.6],
 'note':'All 204 countries and territories, weighted by GBD population (1990) or population implied by GBD all-age counts and crude rates (2010, 2023), ranked by SDI of the same year. Concentration index ranges from −1 to 1; negative values indicate burden concentrated in low-SDI countries. The slope index of inequality (SII) is the population-weighted regression slope of the age-standardised rate on the fractional SDI rank (ridit), that is, the modelled difference between the highest- and lowest-SDI ends of the distribution; relative SII = SII ÷ population-weighted mean. 95% CI from 2 000 bootstrap resamples of countries; changes use paired resampling, so a change is distinguishable from zero when its interval excludes zero. NTD rates are NTDs and malaria minus malaria. 2023 values can differ from Table 2 in the second decimal because Table 2 weights by World Bank population and excludes zero rates from Theil T.'})
# S15b nested Theil
tn=pd.read_csv(f'{R}/rev_theil_nested.csv'); rows=[]
for o in ['NTDs (excl. malaria)','Malaria']:
    rows.append({'group':o})
    for _,r in tn[tn.outcome==o].iterrows():
        rows.append([str(int(r.year)),str(int(r.n)),f'{r.Theil:.2f}',f'{r.between_superregion_pct:.1f}',f'{r.between_region_within_sr_pct:.1f}',f'{r.within_region_pct:.1f}'])
T.append({'id':'Table S15b','title':'Nested Theil T Decomposition of Inequality in Age-Standardised DALY Rates Across Super-Regions, GBD Regions and Countries, 1990, 2010 and 2023','cols':['Year','Countries (n)','Theil T','Between super-regions (%)','Between regions within super-regions (%)','Within regions, between countries (%)'],'rows':rows,'widths':[1.2,1.2,1.0,1.8,2.4,2.4],
 'note':'Population-weighted Theil T over countries with a positive rate, decomposed into three additive components using the GBD hierarchy of 7 super-regions and 21 regions. Malaria country counts fall over time as countries reach zero burden.'})
# S16 21 regions
rg=pd.read_csv(f'{R}/rev_region21.csv'); rows=[]
g=rg[rg.region=='Global'].iloc[0]
def pcs(r,p): return '—' if pd.isna(r[p]) else ci(r[p],r[p+'_lo'],r[p+'_hi'],1)
rows.append(['Global',ci(g.ntdm_n/1e6,g.ntdm_n_lo/1e6,g.ntdm_n_hi/1e6,2),f'{g.ntdm_asr:,.1f}',f'{g.mal_asr:,.1f}',f'{g.ntd_asr:,.1f}','100.0','100.0',pcs(g,'pc_ntdm'),pcs(g,'pc_mal')])
for sr in SRS:
    rows.append({'group':sr})
    for _,r in rg[rg.super_region==sr].sort_values('ntdm_asr',ascending=False).iterrows():
        rows.append([r.region,ci(r.ntdm_n/1e6,r.ntdm_n_lo/1e6,r.ntdm_n_hi/1e6,2),f'{r.ntdm_asr:,.1f}',f'{r.mal_asr:,.1f}',f'{r.ntd_asr:,.1f}',f'{r.share_global_ntdm:.1f}',f'{r.share_global_ntd:.1f}',pcs(r,'pc_ntdm'),pcs(r,'pc_mal')])
T.append({'id':'Table S16','title':'Burden of NTDs and Malaria in the 21 GBD Regions, 2023, and Change in Age-Standardised DALY Rates, 2010–2023','cols':['Region','DALYs, millions [95% UI]','ASR, NTDs and malaria','ASR, malaria','ASR, NTDs (excl. malaria)','Share of global NTD-and-malaria DALYs (%)','Share of global NTD DALYs (%)','% change ASR 2010–2023, NTDs and malaria [95% UI]','% change ASR 2010–2023, malaria [95% UI]'],'rows':rows,'widths':[2.3,1.8,1.0,0.9,1.0,1.2,1.1,1.9,1.9],
 'note':'ASR = age-standardised DALY rate per 100 000. Counts, rates and percent changes with 95% uncertainty intervals are GBD 2023 estimates; NTD (excluding malaria) values are the NTD-and-malaria aggregate minus malaria and carry no interval. A change is statistically distinguishable from zero when its interval excludes zero. — = malaria burden zero in both years.'})
# S17 YLD/YLL
yy=pd.read_csv(f'{R}/rev_yld_yll.csv'); rows=[]
for c in ['NTDs (excl. malaria)','Malaria','NTDs and malaria']:
    rows.append({'group':c})
    for loc in ['Global']+list(SRS):
        r=yy[(yy.cause==c)&(yy.location==loc)].iloc[0]; tot=r.yld+r.yll
        if tot<1000: rows.append([SRS.get(loc,loc),'< 0.001','< 0.001','—']); continue
        yld=ci(r.yld/1e6,r.yld_lo/1e6,r.yld_hi/1e6,2) if pd.notna(r.get('yld_lo')) else f'{r.yld/1e6:.2f}'
        yll=ci(r.yll/1e6,r.yll_lo/1e6,r.yll_hi/1e6,2) if pd.notna(r.get('yll_lo')) else f'{r.yll/1e6:.2f}'
        rows.append([SRS.get(loc,loc),yld,yll,f'{r.yld_share_pct:.1f}'])
T.append({'id':'Table S17','title':'Years Lived With Disability and Years of Life Lost From NTDs and Malaria by Super-Region, 2023','cols':['Location','YLDs, millions [95% UI]','YLLs, millions [95% UI]','YLDs as % of DALYs'],'rows':rows,'widths':[3.2,2.6,2.6,1.4],
 'note':'GBD 2023 all-age counts. NTD (excluding malaria) values are derived by subtraction and carry no interval.'})
# S18 national rankings
MUI=pd.read_csv('data/raw/gbd/country__malaria__dalys__2023.csv').set_index('location_id')
na=pd.read_csv(f'{R}/rev_national.csv'); rows=[]
for lab,col,c10,chg in [('Highest age-standardised NTD (excl. malaria) DALY rate','ntd_2023','ntd_2010','chg_ntd_asr_pct'),('Highest age-standardised malaria DALY rate','mal_2023','mal_2010','chg_mal_asr_pct')]:
    rows.append({'group':lab})
    for i,(_,r) in enumerate(na.nlargest(10,col).iterrows(),1):
        v=f'{r[col]:,.1f}'
        if col=='mal_2023':
            u=MUI.loc[r.location_id]; v=ci(r[col],u.rate_lower_combined,u.rate_upper_combined,1)
        rows.append([f'{i}. {r.location_name}',SRS[r.super_region_name],v,f'{r[c10]:,.1f}',f'{r[chg]:+.1f}',f'{r.sdi_2023:.3f}'])
for lab,col,tot in [('Largest absolute NTD (excl. malaria) DALYs','n_ntd_2023',na.n_ntd_2023.sum()),('Largest absolute malaria DALYs','n_mal_2023',na.n_mal_2023.sum())]:
    rows.append({'group':lab+' (DALYs, thousands; share of global, %)'})
    cum=0
    for i,(_,r) in enumerate(na.nlargest(10,col).iterrows(),1):
        cum+=r[col]; rows.append([f'{i}. {r.location_name}',SRS[r.super_region_name],f'{r[col]/1e3:,.0f}',f'{100*r[col]/tot:.1f}',f'cumulative {100*cum/tot:.1f}',f'{r.sdi_2023:.3f}'])
T.append({'id':'Table S18','title':'National Rankings of NTD and Malaria Burden, 2023, With Comparison to 2010','cols':['Country','Super-region','Rate 2023 [95% UI] / DALYs (thousands)','Rate 2010 / share of global (%)','Change in rate 2010–2023 (%)','SDI 2023'],'rows':rows,'widths':[3.0,2.4,1.5,1.6,1.6,0.9],
 'note':'Rates are age-standardised DALYs per 100 000. Changes for NTDs excluding malaria and for malaria are computed from GBD point estimates and have no interval; GBD-published changes with intervals for the NTD-and-malaria aggregate are in Table S19.'})
# S19 countries with significant change + rising point estimates
rows=[]; vc=na.pc_ntdm_sig.value_counts()
rows.append({'group':f'NTDs and malaria, GBD-published change in ASR 2010–2023: decrease n = {vc.get("decrease",0)}, uncertain n = {vc.get("uncertain",0)}, increase n = {vc.get("increase",0)}'})
for _,r in na[na.pc_ntdm_sig=='increase'].sort_values('pc_ntdm',ascending=False).iterrows():
    rows.append([r.location_name,SRS[r.super_region_name],'NTDs and malaria',f'{r.ntdm_2010:,.1f}',f'{r.ntdm_2023:,.1f}',ci(r.pc_ntdm,r.pc_ntdm_lo,r.pc_ntdm_hi,1)])
rows.append({'group':'NTDs (excl. malaria): countries with a higher point-estimate rate in 2023 than 2010'})
for _,r in na[na.chg_ntd_asr_pct>0].sort_values('chg_ntd_asr_pct',ascending=False).iterrows():
    rows.append([r.location_name,SRS[r.super_region_name],'NTDs (excl. malaria)',f'{r.ntd_2010:,.1f}',f'{r.ntd_2023:,.1f}',f'{r.chg_ntd_asr_pct:+.1f}'])
rows.append({'group':'Malaria: countries with a higher point-estimate rate in 2023 than 2010 (2010 rate > 1 per 100 000)'})
for _,r in na[(na.chg_mal_asr_pct>0)&(na.mal_2010>1)].sort_values('chg_mal_asr_pct',ascending=False).iterrows():
    rows.append([r.location_name,SRS[r.super_region_name],'Malaria',f'{r.mal_2010:,.1f}',f'{r.mal_2023:,.1f}',f'{r.chg_mal_asr_pct:+.1f}'])
T.append({'id':'Table S19','title':'Countries in Which Age-Standardised NTD or Malaria DALY Rates Rose Between 2010 and 2023','cols':['Country','Super-region','Outcome','ASR 2010','ASR 2023','Change (%) [95% UI where published]'],'rows':rows,'widths':[2.6,2.4,1.8,1.1,1.1,2.0],
 'note':'ASR = age-standardised DALY rate per 100 000. Only the NTD-and-malaria aggregate has GBD-published country-level percent changes with uncertainty intervals; changes for the two components are computed from point estimates and should be read as descriptive.'})
# S20 cause leaders
cl=pd.read_csv(f'{R}/rev_cause_leaders.csv'); rows=[]
for _,r in cl[cl.global_dalys>=1000].iterrows():
    rows.append([r.cause,f'{r.global_dalys/1e3:,.1f}',f'{r.top_count_country} ({r.top_count_share:.1f})',r.top3_count_countries.replace('Democratic Republic of the Congo','DR Congo').replace('Venezuela (Bolivarian Republic of)','Venezuela'),f'{r.top3_count_share:.1f}',f'{r.top_rate_country.replace("Democratic Republic of the Congo","DR Congo").replace("Lao People\'s Democratic Republic","Lao PDR").replace("Bolivia (Plurinational State of)","Bolivia")} ({r.top_rate:,.1f})'])
T.append({'id':'Table S20','title':'Cause-Specific National Leaders: Countries Contributing the Most NTD DALYs and Countries With the Highest Rates, 2023','cols':['Cause','Global DALYs (thousands)','Largest contributor (% of global)','Three largest contributors','Share of three largest (%)','Highest age-standardised rate (per 100 000)'],'rows':rows,'widths':[2.4,1.2,2.2,3.2,1.1,2.2],
 'note':'Sum of 204 country-level GBD 2023 all-age counts. Causes with fewer than 1 000 global DALYs (Ebola, Guinea worm disease, Zika virus) omitted. "Other NTDs" is the GBD residual category.'})
# S21 LISA over time + WHO triangulation
li=pd.read_csv(f'{R}/rev_lisa_over_time.csv'); rows=[{'group':'A. Spatial autocorrelation of log(1 + age-standardised DALY rate)'}]
for _,r in li.iterrows():
    o,y=r.series.split('_'); rows.append([('NTDs (excl. malaria)' if o=='ntd' else 'Malaria')+f', {y}',f'{r.moran_I:.2f}',f'{r.z:.1f}','< .001',str(r.HH),str(r.LL),str(r.outliers)])
tri=pd.read_csv(f'{R}/rev_who_triangulation.csv'); rows.append({'group':'B. Agreement between GBD and WHO/UN SDG country series (Spearman rank correlation)'})
for _,r in tri.iterrows(): rows.append([f'{r.pair}, {int(r.year)}',f'ρ = {r.rho:.2f}','—',pfmt(r.p),f'n = {int(r.n)}','—','—'])
T.append({'id':'Table S21','title':'Stability of Spatial Clustering, 1990–2023, and External Validation Against WHO Surveillance Series','cols':['Series',"Moran's I / ρ",'z','p','High–High (n)','Low–Low (n)','Spatial outliers (n)'],'rows':rows,'widths':[4.4,1.1,0.7,0.8,1.1,1.0,1.1],
 'note':"Panel A: row-standardised k = 6 nearest-neighbour weights, 9 999 permutations, LISA clusters at Benjamini–Hochberg q < .05 (n = 203 countries with geometry). Panel B: WHO-reported people requiring interventions against NTDs (SDG 3.3.5) expressed per 100 000 population; WHO malaria incidence per 1 000 population at risk (SDG 3.3.3), endemic countries only."})

# S22 post-review sensitivity analyses (values from the authors' post-review re-estimation reported in the manuscript)
rows=[{'group':'A. Preferred two-way fixed-effects estimate, % difference per 10-percentage-point external share [95% CI] (observations)'},
 ['Primary specification (2007–2022)','−0.64 [−2.39, 1.14] (2,287)','−6.32 [−10.84, −1.57] (1,187)'],
 ['Panel extended through 2023','−0.32 [−2.13, 1.53] (2,429)','−6.97 [−11.28, −2.45] (1,262)'],
 ['Excluding observations without matching raw UHC or LDI records','−0.45 [−2.17, 1.29] (2,101)','No observations affected'],
 ['Omitting UHC effective coverage','−0.78 [−2.44, 0.91]','−6.59 [−11.62, −1.28]'],
 ['Country-clustered rather than Driscoll–Kraay standard errors','CI includes zero','−6.32 [−17.14, 5.91]'],
 {'group':'B. Theil T decomposition, 2023'},
 ['Positive rates only (primary; NTDs n = 199, malaria n = 86)','0.43; between 63.4%','1.34; between 78.9%'],
 ['Zero rates retained (n = 199)','0.43; between 63.4% (unchanged)','1.88; between 83.7%']]
T.append({'id':'Table S22','title':'Post-Review Sensitivity Analyses of the Financing Association and the Theil Decomposition','cols':['Analysis','NTDs (excl. malaria)','Malaria'],'rows':rows,'widths':[4.6,2.8,2.8],
 'note':'Malaria estimates are percentage differences in (1 + age-standardised DALY rate). UHC = universal health coverage effective-coverage index; LDI = lag-distributed income per capita. In the Theil T with zero rates, the limiting term 0 × log(0) is set to zero.'})

# S23 between vs within (Mundlak)
bw=pd.read_csv(f'{R}/rev_between_within.csv'); rows=[]
for o in ['NTDs (excl. malaria)','Malaria']:
    rows.append({'group':o})
    for e in ['Share (per 10 pp)','Per capita (log)']:
        for _,r in bw[(bw.outcome==o)&(bw.exposure==e)].iterrows():
            f=np.log(2) if e.startswith('Per') else 1
            pc=100*(np.exp(r.beta*f)-1); lo=100*(np.exp((r.beta-1.96*r.se)*f)-1); hi=100*(np.exp((r.beta+1.96*r.se)*f)-1)
            rows.append([('External share, per 10 percentage points' if f==1 else 'External expenditure per capita, per doubling')+' — '+r.component.lower(),ci(pc,lo,hi,2),pfmt(r.p),f'{int(r.n):,}',str(int(r.countries))])
T.append({'id':'Table S23','title':'Between-Country and Within-Country Associations of External Health Financing With Age-Standardised DALY Rates (Correlated Random-Effects Decomposition)','cols':['Exposure — component','% difference [95% CI]','p','Observations','Countries'],'rows':rows,'widths':[5.0,2.2,0.8,1.2,1.0],
 'note':'Correlated random-effects (Mundlak) model with year effects, the five covariates of the preferred model and their country means; country-clustered standard errors. The within-country component is the coefficient on the time-varying exposure; the between-country component adds the coefficient on its country mean; the difference tests whether the two are equal. Malaria estimates refer to (1 + rate). Per-capita exposure is log(1 + external health expenditure per capita), so a doubling refers to expenditure plus US$1.'})
# S24 mortality outcome
mo=pd.read_csv(f'{R}/rev_mortality_sensitivity.csv'); rows=[]
for _,r in mo.iterrows():
    f=np.log(2) if r.exposure.startswith('Per') else 1
    tr=lambda v: 100*(np.exp(np.log1p(v/100)*f)-1)
    rows.append([r.outcome,'Per 10 percentage points' if f==1 else 'Per doubling of expenditure + US$1',ci(tr(r.pct),tr(r.lo),tr(r.hi),2),pfmt(r.p),ci(tr(r.pct),tr(r.lo_cl),tr(r.hi_cl),2),pfmt(r.p_cl),f'{int(r.n):,}'])
T.append({'id':'Table S24','title':'Malaria Mortality as an Alternative Outcome: Two-Way Fixed-Effects Associations With External Health Financing, Malaria-Endemic Countries, 2007–2022','cols':['Outcome','Exposure','% difference, Driscoll–Kraay [95% CI]','p','% difference, country-clustered [95% CI]','p','Observations'],'rows':rows,'widths':[2.6,2.2,2.2,0.7,2.2,0.7,1.1],
 'note':'Preferred specification (country and year fixed effects; covariates as in Table S4) with the GBD 2023 age-standardised malaria death rate as outcome, 77 malaria-endemic low- and middle-income countries. Exposures lagged 2 years. The DALY rows repeat the primary outcome on the same countries for comparison.'})

json.dump(T,open('results/tables.json','w'),indent=1,ensure_ascii=False); print(len(T),'tables')
