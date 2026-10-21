"""Harmonise the external-financing coefficient across all estimators to: % change in age-standardised DALY rate per +10 pp external share."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf, geopandas as gpd, warnings
from libpysal.weights import KNN; from spreg import ML_Error
warnings.filterwarnings('ignore')
cs=pd.read_csv('data/processed/analysis_country_2023.csv')
SR=['Sub-Saharan Africa','South Asia','Southeast Asia, East Asia, and Oceania','Latin America and Caribbean','North Africa and Middle East','Central Europe, Eastern Europe, and Central Asia','High-income']
cs['sr']=pd.Categorical(cs.super_region_name,SR); cs['y_ntd']=np.log(cs.daly_asr_ntd_excl_malaria); cs['y_mal']=np.log1p(cs.daly_asr_malaria)
cs['log_ldi']=np.log(cs.ldi_2023); cs['ext10']=cs.ext_pct_che_latest/10; cs['uhc10']=cs.uhc_2023/10; cs['san10']=cs.sanit_basic_pct_latest/10; cs['wat10']=cs.water_basic_pct_latest/10
X=['ext10','log_ldi','uhc10','san10','wat10','rural_pct_latest']
rows=[]
ne=gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson'); ne['iso3']=np.where(ne.ISO_A3=='-99',ne.ADM0_A3,ne.ISO_A3)
ne.loc[ne.ADMIN=='France','iso3']='FRA'; ne.loc[ne.ADMIN=='Norway','iso3']='NOR'
cent=ne[['iso3','geometry']].dissolve('iso3').reset_index().to_crs('ESRI:54030'); cent['geometry']=cent.representative_point()
for outc,yv,flt in [('NTDs (excl. malaria)','y_ntd',cs.sr!='High-income'),('Malaria','y_mal',(cs.sr!='High-income')&(cs.daly_asr_malaria>10))]:
    d=cs[flt].dropna(subset=X+[yv]).copy(); d['sr']=d.sr.cat.remove_unused_categories()
    m=smf.ols(f"{yv} ~ {'+'.join(X)} + C(sr)",d).fit(cov_type='HC3'); b=m.params['ext10']; lo,hi=m.conf_int().loc['ext10']
    rows.append({'outcome':outc,'family':'Between-country (2023 cross-section)','model':'OLS + super-region FE','beta':b,'lo':lo,'hi':hi,'p':m.pvalues['ext10'],'n':int(m.nobs)})
    sub=d.merge(cent,on='iso3'); g=gpd.GeoDataFrame(sub,geometry='geometry'); w=KNN.from_dataframe(g,k=6); w.transform='r'
    Xm=pd.concat([sub[X],pd.get_dummies(sub.sr,drop_first=True).astype(float)],axis=1)
    me=ML_Error(sub[[yv]].values,Xm.values,w=w); b=me.betas[1,0]; se=me.std_err[1]
    rows.append({'outcome':outc,'family':'Between-country (2023 cross-section)','model':'Spatial error model','beta':b,'lo':b-1.96*se,'hi':b+1.96*se,'p':me.z_stat[1][1],'n':int(me.n)})
pm=pd.read_csv('results/panel_models_comparison.csv'); pm=pm[pm.spec=='A: share']
for _,r in pm.iterrows(): rows.append({'outcome':r.outcome,'family':'Within-country panel (2007–22)','model':r.model,'beta':r.beta,'lo':r.lo,'hi':r.hi,'p':r.p,'n':int(r.n_obs)})
sp=pd.read_csv('results/spatial_panel_models.csv')
for _,r in sp.iterrows(): rows.append({'outcome':r.outcome,'family':'Spatial panel (2007–22)','model':r.model,'beta':r.beta,'lo':r.lo,'hi':r.hi,'p':r.p,'n':int(r.n_countries*16)})
o=pd.DataFrame(rows)
for c in ['beta','lo','hi']: o[c.replace('beta','pct').replace('lo','pct_lo').replace('hi','pct_hi')]=100*(np.exp(o[c])-1)
o.to_csv('results/model_comparison_external_share.csv',index=False); print(o[['outcome','family','model','pct','pct_lo','pct_hi','p','n']].round(2).to_string())
