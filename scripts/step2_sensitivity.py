"""Reviewer-driven sensitivity analyses. Outputs results/sensitivity_*.csv"""
import pandas as pd, numpy as np, geopandas as gpd, warnings, json
import statsmodels.formula.api as smf
from libpysal.weights import KNN, DistanceBand
from esda.moran import Moran
warnings.filterwarnings('ignore')
P='data/processed'; out=[]
cs=pd.read_csv(f'{P}/analysis_country_2023.csv')
SR=['Sub-Saharan Africa','South Asia','Southeast Asia, East Asia, and Oceania','Latin America and Caribbean','North Africa and Middle East','Central Europe, Eastern Europe, and Central Asia','High-income']
cs['sr']=pd.Categorical(cs.super_region_name,SR)
lisa=pd.read_csv('results/spatial_lisa_country.csv')
# R1. Spatial weights specification
ne=gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson'); ne['iso3']=np.where(ne.ISO_A3=='-99',ne.ADM0_A3,ne.ISO_A3)
ne.loc[ne.ADMIN=='France','iso3']='FRA'; ne.loc[ne.ADMIN=='Norway','iso3']='NOR'
geo=ne[['iso3','geometry']].dissolve('iso3').reset_index().merge(cs,on='iso3').to_crs('ESRI:54030'); pts=geo.copy(); pts['geometry']=geo.representative_point()
for nm,col in [('NTDs (excl. malaria)','daly_asr_ntd_excl_malaria'),('Malaria','daly_asr_malaria')]:
    y=np.log1p(geo[col].values)
    for spec,w in [('KNN k=4',KNN.from_dataframe(pts,k=4)),('KNN k=6 (main)',KNN.from_dataframe(pts,k=6)),('KNN k=8',KNN.from_dataframe(pts,k=8)),
                   ('Distance band 2,500 km',DistanceBand.from_dataframe(pts,threshold=2.5e6,binary=False,alpha=-1,silence_warnings=True))]:
        w.transform='r'; m=Moran(y,w,permutations=999)
        out.append({'analysis':'S1 Spatial weights','outcome':nm,'specification':spec,'estimate':m.I,'lo':np.nan,'hi':np.nan,'p':m.p_sim,'n':len(y)})
# R2. Regression robustness: lagged exposure, excluding SSA, SDI instead of LDI/UHC, independent WHO outcome
d=cs.copy(); d['y']=np.log(d.daly_asr_ntd_excl_malaria); d['log_ldi']=np.log(d.ldi_2023)
d['y_who']=np.log1p(d.ppl_req_ntd_pct_pop_2023)
base=['log_ldi','uhc_2023','sanit_basic_pct_latest','water_basic_pct_latest','rural_pct_latest']
def fit(df,yv,xs,ext,lab):
    df=df.dropna(subset=xs+[ext,yv]).copy()
    for x in xs+[ext]: df[x+'_z']=(df[x]-df[x].mean())/df[x].std()
    f=f"{yv} ~ {'+'.join(x+'_z' for x in xs)} + {ext}_z" + (" + C(sr)" if df.sr.nunique()>1 else "")
    m=smf.ols(f,df).fit(cov_type='HC3'); b=m.params[ext+'_z']; lo,hi=m.conf_int().loc[ext+'_z']
    out.append({'analysis':'S2 External-dependence association','outcome':'NTDs (excl. malaria)' if yv=='y' else 'WHO: people requiring NTD interventions (% pop)','specification':lab,
                'estimate':100*(np.exp(b)-1),'lo':100*(np.exp(lo)-1),'hi':100*(np.exp(hi)-1),'p':m.pvalues[ext+'_z'],'n':int(m.nobs)})
fit(d,'y',base,'ext_pct_che_latest','Main model (2019–23 exposure)')
fit(d,'y',base,'ext_pct_che_2010_14','Lagged exposure (2010–14 mean)')
fit(d[d.sr!='Sub-Saharan Africa'],'y',base,'ext_pct_che_latest','Excluding sub-Saharan Africa')
fit(d[d.sr!='High-income'],'y',base,'ext_pct_che_latest','Excluding high-income')
fit(d.assign(sdi=d.sdi_2023),'y',['sdi','sanit_basic_pct_latest','water_basic_pct_latest','rural_pct_latest'],'ext_pct_che_latest','SDI replaces income and UHC (GBD-covariate circularity check)')
fit(d,'y_who',base,'ext_pct_che_latest','Independent outcome: WHO-reported need (SDG 3.3.5)')
# R3. Missing-data comparison (complete-case vs excluded)
need=base+['ext_pct_che_latest','daly_asr_ntd_excl_malaria']
cc=d.dropna(subset=need); ex=d[~d.index.isin(cc.index)]
miss=pd.DataFrame({'Included (complete case)':[len(cc),cc.daly_asr_ntd_excl_malaria.median(),cc.daly_n_ntd_excl_malaria.sum()/d.daly_n_ntd_excl_malaria.sum()*100],
                   'Excluded':[len(ex),ex.daly_asr_ntd_excl_malaria.median(),ex.daly_n_ntd_excl_malaria.sum()/d.daly_n_ntd_excl_malaria.sum()*100]},
                  index=['Countries','Median NTD age-standardised DALY rate','% of global NTD DALYs'])
miss.to_csv('results/sensitivity_missingness.csv'); excl=ex[['location_name','super_region_name']]; excl.to_csv('results/excluded_countries_regression.csv',index=False)
# R4. Scenario attribution assumptions (NTDs): programme-dependence upper bound & DALY valuation
sc=pd.read_csv('results/scenario_excess_dalys_country.csv')
r=sc[(sc.scenario=='Reference')]
for outc in ['NTDs (excl. malaria)','Malaria']:
    t=r[r.outcome==outc]
    main=t.excess_dalys.sum()
    us=pd.read_csv('data/raw/funding/usaid_ntd_program_countries.csv').iso3
    ub=(t.excess_dalys/t.ext_share.clip(1e-6)*np.where(t.iso3.isin(us),np.maximum(t.ext_share,0.8),t.ext_share)).sum()
    out.append({'analysis':'S4 Scenario attribution','outcome':outc,'specification':'Main: gains attributable in proportion to external share of health spending','estimate':main,'lo':t.lo.sum(),'hi':t.hi.sum(),'p':np.nan,'n':len(t)})
    if outc.startswith('NTD'): out.append({'analysis':'S4 Scenario attribution','outcome':outc,'specification':'Programme-dependence upper bound: ≥80% donor attribution in USAID NTD-programme countries','estimate':ub,'lo':np.nan,'hi':np.nan,'p':np.nan,'n':len(t)})
    for mult in [0.5,1,3]:
        out.append({'analysis':'S5 Economic valuation (US$ billion)','outcome':outc,'specification':f'{mult}× GDP per capita per DALY','estimate':mult*t.value_usd_1gdp.sum()/1e9,'lo':np.nan,'hi':np.nan,'p':np.nan,'n':len(t)})
res=pd.DataFrame(out); res.to_csv('results/sensitivity_analyses.csv',index=False)
pd.set_option('display.width',250); print(res.round(3).to_string()); print(miss.round(1))
