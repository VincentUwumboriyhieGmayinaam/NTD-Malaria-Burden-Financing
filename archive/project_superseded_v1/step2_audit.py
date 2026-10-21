"""Methodological audit: tests for flaws a reviewer could raise. Output results/audit_checks.csv
A1 additivity of cause-specific age-standardised rates (no double counting of parent/child causes)
A2 OLS residual spatial autocorrelation (justifies spatial error model)
A3 heterogeneity LR test robust to small super-regions (exclude n<10 and high-income)
A4 measurement uncertainty: inverse-variance weighted regression using GBD 95% UIs
A5 multicollinearity (VIF)
A6 scenario: correlation between 2010 and 2023 GBD draws (independence assumption inflates UI only)
A7 influence: leave-one-super-region-out for the external-dependence coefficient
"""
import pandas as pd, numpy as np, geopandas as gpd, warnings
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy.stats import chi2
from libpysal.weights import KNN
from esda.moran import Moran
warnings.filterwarnings('ignore'); rng=np.random.default_rng(7)
P='data/processed'; out=[]
cs=pd.read_csv(f'{P}/analysis_country_2023.csv')
SR=['Sub-Saharan Africa','South Asia','Southeast Asia, East Asia, and Oceania','Latin America and Caribbean','North Africa and Middle East','Central Europe, Eastern Europe, and Central Asia','High-income']
cs['sr']=pd.Categorical(cs.super_region_name,SR)
# A1
a=cs.daly_n_neglected_tropical_diseases_and_malaria.sum(); b=cs.daly_n_malaria.sum()+cs.daly_n_ntd_excl_malaria.sum()
out.append({'check':'A1 Cause additivity (counts): NTD&M total minus (malaria + 19 NTD causes), % of total','value':100*(a-b)/a,'verdict':'pass' if abs(a-b)/a<0.001 else 'FAIL'})
r=cs.daly_asr_neglected_tropical_diseases_and_malaria-(cs.daly_asr_malaria+cs.daly_asr_ntd_excl_malaria)
out.append({'check':'A1 Cause additivity (age-standardised rates): max absolute discrepancy per 100 000','value':float(r.abs().max()),'verdict':'pass' if r.abs().max()<0.5 else 'FAIL'})
# data prep
d=cs.copy(); d['y']=np.log(d.daly_asr_ntd_excl_malaria); d['log_ldi']=np.log(d.ldi_2023)
X=['log_ldi','uhc_2023','sanit_basic_pct_latest','water_basic_pct_latest','rural_pct_latest','ext_pct_che_latest']
d=d.dropna(subset=X+['y']).copy()
for x in X: d[x+'_z']=(d[x]-d[x].mean())/d[x].std()
Z=[x+'_z' for x in X]; f=f"y ~ {'+'.join(Z)} + C(sr)"
m=smf.ols(f,d).fit(cov_type='HC3')
# A2 residual Moran
ne=gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson'); ne['iso3']=np.where(ne.ISO_A3=='-99',ne.ADM0_A3,ne.ISO_A3)
ne.loc[ne.ADMIN=='France','iso3']='FRA'; ne.loc[ne.ADMIN=='Norway','iso3']='NOR'
g=ne[['iso3','geometry']].dissolve('iso3').reset_index().to_crs('ESRI:54030'); g['geometry']=g.representative_point()
dd=d.merge(g,on='iso3'); gg=gpd.GeoDataFrame(dd,geometry='geometry',crs=g.crs)
w=KNN.from_dataframe(gg,k=6); w.transform='r'
mr=smf.ols(f,dd).fit(); mi=Moran(mr.resid.values,w,permutations=999)
out.append({'check':"A2 Moran's I of OLS residuals (k=6) — if significant, spatial error model required",'value':mi.I,'verdict':f'p={mi.p_sim:.3f}; spatial error model reported'})
# A3 heterogeneity robustness
def lr(df):
    m0=smf.ols(f,df).fit(); m1=smf.ols(f+' + C(sr):ext_pct_che_latest_z',df).fit()
    L=2*(m1.llf-m0.llf); k=m1.df_model-m0.df_model; return L,k,chi2.sf(L,k)
for lab,df in [('all super-regions',d),('excluding super-regions with n<10 (South Asia)',d[d.sr!='South Asia']),('excluding South Asia and high-income',d[~d.sr.isin(['South Asia','High-income'])])]:
    df=df.copy(); df['sr']=df.sr.cat.remove_unused_categories(); L,k,p=lr(df)
    out.append({'check':f'A3 Heterogeneity of external-dependence slope, LR test ({lab})','value':L,'verdict':f'df={k:.0f}, p={p:.4f}'})
# A4 inverse-variance weights from GBD UI (log scale)
se=(np.log(d.daly_asr_ntdm_hi)-np.log(d.daly_asr_ntdm_lo))/3.92
mw=smf.wls(f,d,weights=1/se.clip(0.02)**2).fit(cov_type='HC3')
b=mw.params['ext_pct_che_latest_z']; lo,hi=mw.conf_int().loc['ext_pct_che_latest_z']
out.append({'check':'A4 Inverse-variance weighted (GBD UI) estimate: % change in NTD DALY rate per SD external share','value':100*(np.exp(b)-1),'verdict':f'95% CI {100*(np.exp(lo)-1):.1f} to {100*(np.exp(hi)-1):.1f} (unweighted {100*(np.exp(m.params["ext_pct_che_latest_z"])-1):.1f})'})
# A5 VIF
Xm=d[Z].assign(const=1.0)
for i,z in enumerate(Z):
    v=variance_inflation_factor(Xm.values,i); out.append({'check':f'A5 VIF {z[:-2]}','value':v,'verdict':'acceptable (<5)' if v<5 else ('moderate (5-10)' if v<10 else 'HIGH (>10)')})
# A6 correlated draws in scenario
BL=pd.read_csv(f'{P}/gbd_country_burden_long.csv'); BL=BL[BL.measure=='dalys']
core=sorted(set(BL[BL.year==2010].cause)-{'neglected_tropical_diseases_and_malaria','malaria'})
sc=cs.dropna(subset=['ext_pct_che_latest','pop_latest']); sc=sc[sc.super_region_name!='High-income']
def tot(rho,NS=2000):
    z0=rng.standard_normal((NS,len(sc))); res=np.zeros((NS,len(sc)))
    for c in core:
        z1=rho*z0+np.sqrt(1-rho**2)*rng.standard_normal((NS,len(sc)))
        g={}
        for yr,zz in [(2010,z0),(2023,z1)]:
            t=BL[(BL.cause==c)&(BL.year==yr)].set_index('location_id').reindex(sc.location_id)
            mu=np.log(t.asr.clip(1e-9).values); s=((np.log(t.asr_hi.clip(1e-9))-np.log(t.asr_lo.clip(1e-9)))/3.92).fillna(0).values
            g[yr]=np.exp(mu+s*zz)
        res+=g[2010]-g[2023]
    ex=np.clip(res,0,None)/1e5*sc.pop_latest.values*sc.ext_pct_che_latest.values/100*rng.uniform(0.19,0.26,(NS,1))
    T=ex.sum(1); return np.median(T),np.percentile(T,2.5),np.percentile(T,97.5)
for rho in [0.0,0.8]:
    mdn,lo,hi=tot(rho); out.append({'check':f'A6 Reference scenario NTD excess DALYs, draw correlation rho={rho}','value':mdn,'verdict':f'95% UI {lo:,.0f}–{hi:,.0f}'})
# A7 leave-one-super-region-out
for s in SR:
    df=d[d.sr!=s].copy(); df['sr']=df.sr.cat.remove_unused_categories()
    mm=smf.ols(f,df).fit(cov_type='HC3'); b=mm.params['ext_pct_che_latest_z']; lo,hi=mm.conf_int().loc['ext_pct_che_latest_z']
    out.append({'check':f'A7 Leave out {s}: % change per SD external share','value':100*(np.exp(b)-1),'verdict':f'95% CI {100*(np.exp(lo)-1):.1f} to {100*(np.exp(hi)-1):.1f}; n={int(mm.nobs)}'})
res=pd.DataFrame(out); res.to_csv('results/audit_checks.csv',index=False)
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',120); print(res.to_string())
