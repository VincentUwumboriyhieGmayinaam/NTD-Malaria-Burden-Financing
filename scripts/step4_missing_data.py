"""Step 4: missing-data audit and sensitivity of the preferred panel model to the missing-data strategy.
Outputs results/missing_profile.csv, results/missing_predictors.csv, results/missing_sensitivity.csv"""
import pandas as pd, numpy as np, warnings, json
import statsmodels.api as sm, statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge
warnings.filterwarnings('ignore')
P='data/processed'
p=pd.read_csv(f'{P}/panel_2005_2023.csv')
raw=pd.read_csv(f'{P}/wb_country_year_wide.csv')
VARS=['ext_pct_che','ghed_pc_usd','sanit_basic_pct','water_basic_pct']
raw=raw[['iso3','year']+VARS].rename(columns={v:v+'_raw' for v in VARS})
p=p.merge(raw,on='iso3 year'.split(),how='left')
p=p.sort_values(['iso3','year'])
for v in ['ext_pct_che','ghed_pc_usd']:
    p[v+'_raw_l2']=p.groupby('iso3')[v+'_raw'].shift(2)
lm=p[(p.lmic==1)&(p.year.between(2007,2022))].copy()
# ---------- 1. profile ----------
prof=[]
spec={'External share of CHE (lag 2)':('ext_pct_che_raw_l2','ext_pct_che_l2'),
      'Domestic govt health spending pc (lag 2)':('ghed_pc_usd_raw_l2','ghed_pc_usd_l2'),
      'Basic sanitation':('sanit_basic_pct_raw','sanit_basic_pct'),
      'Basic drinking water':('water_basic_pct_raw','water_basic_pct'),
      'UHC index (GBD)':('uhc','uhc'),'LDI (GBD)':('ldi','ldi'),
      'NTD age-standardised DALY rate (GBD)':('asr_ntd','asr_ntd'),
      'Malaria age-standardised DALY rate (GBD)':('asr_malaria','asr_malaria')}
N=len(lm)
for k,(r,f) in spec.items():
    miss_raw=lm[r].isna().mean()*100; miss_fin=lm[f].isna().mean()*100
    nocov=(lm.groupby('iso3')[f].apply(lambda s:s.notna().sum())==0).sum()
    prof.append(dict(variable=k,country_years=N,missing_raw_pct=round(miss_raw,1),filled_by_rule_pct=round(miss_raw-miss_fin,1),
                     missing_after_pct=round(miss_fin,1),countries_never_observed=int(nocov)))
prof=pd.DataFrame(prof)
X=['ext_pct_che_l2','ghed_pc_usd_l2','ldi','uhc','sanit_basic_pct','water_basic_pct','asr_ntd']
cc=lm[X].notna().all(axis=1)
ann=dict(country_years=N,countries=lm.iso3.nunique(),complete_case_rows=int(cc.sum()),complete_case_pct=round(cc.mean()*100,1),
         countries_in_model=int(lm[cc].iso3.nunique()),imputed_rows_in_model=int(lm[cc].imputed_any.sum()),
         imputed_rows_pct=round(lm[cc].imputed_any.mean()*100,1))
prof.to_csv('results/missing_profile.csv',index=False)
# ---------- 2. predictors of incompleteness (MAR plausibility) ----------
lm['incomplete']=(~cc).astype(int)
lm['log_ntd']=np.log(lm.asr_ntd.clip(lower=.01)); lm['sdi10']=lm.sdi*10
m=smf.logit('incomplete ~ log_ntd + sdi10 + C(super_region_name) + I(year-2007)',data=lm).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pd.factorize(lm.iso3)[0]})
pr=pd.DataFrame({'OR':np.exp(m.params),'lo':np.exp(m.conf_int()[0]),'hi':np.exp(m.conf_int()[1]),'p':m.pvalues}).round(3)
pr.to_csv('results/missing_predictors.csv')
# ---------- 3. sensitivity of preferred model ----------
def fit(d,yv='y_ntd',ext='ext_pct_che_l2',ghed='ghed_pc_usd_l2',san='sanit_basic_pct',wat='water_basic_pct'):
    d=d.copy(); d['ext10']=d[ext]/10; d['lg']=np.log(d[ghed]); d['log_ldi']=np.log(d.ldi); d['uhc10']=d.uhc/10
    d['san10']=d[san]/10; d['wat10']=d[wat]/10
    XX=['ext10','lg','log_ldi','uhc10','san10','wat10']
    d=d.dropna(subset=XX+[yv]).set_index(['iso3','year'])
    r=PanelOLS(d[yv],sm.add_constant(d[XX]),entity_effects=True,time_effects=True,drop_absorbed=True).fit(cov_type='kernel',kernel='bartlett',bandwidth=3)
    return r.params['ext10'],r.std_errors['ext10'],len(d),d.index.get_level_values(0).nunique()
def row(lbl,outc,b,se,n,k,extra=''):
    pc=lambda x:(np.exp(x)-1)*100
    from scipy import stats
    return dict(strategy=lbl,outcome=outc,pct=round(pc(b),2),lo=round(pc(b-1.96*se),2),hi=round(pc(b+1.96*se),2),
                p=round(2*(1-stats.norm.cdf(abs(b/se))),3),n=n,countries=k,note=extra)
out=[]
for outc,yv,sub in [('NTDs (excl. malaria)','y_ntd',lm),('Malaria','y_mal',lm[lm.mal_endemic==1])]:
    out.append(row('Main: interpolation + LOCF ≤2 y',outc,*fit(sub,yv)))
    out.append(row('Complete case, no imputation',outc,*fit(sub,yv,ext='ext_pct_che_raw_l2',ghed='ghed_pc_usd_raw_l2',san='sanit_basic_pct_raw',wat='water_basic_pct_raw')))
    out.append(row('Excluding any imputed country-year',outc,*fit(sub[sub.imputed_any==0],yv)))
    # balanced: countries with complete data all 16 years
    s2=sub.copy(); ok=s2.groupby('iso3').apply(lambda g:g[['ext_pct_che_l2','ghed_pc_usd_l2','ldi','uhc','sanit_basic_pct','water_basic_pct',yv]].notna().all(axis=1).all())
    out.append(row('Balanced panel only',outc,*fit(s2[s2.iso3.isin(ok[ok].index)],yv)))
    # multiple imputation by chained equations (m = 20), Rubin's rules
    cols=['ext_pct_che_raw_l2','ghed_pc_usd_raw_l2','sanit_basic_pct_raw','water_basic_pct_raw','ldi','uhc','sdi',yv,'year']
    base=sub.copy(); base['ghed_pc_usd_raw_l2']=np.log(base['ghed_pc_usd_raw_l2']); base['ldi']=np.log(base.ldi)
    # country means of observed values as auxiliary variables (retain between-country structure)
    for c in cols[:4]: base[c+'_cm']=base.groupby('iso3')[c].transform('mean')
    aux=[c+'_cm' for c in cols[:4]]
    B=[];V=[]
    for mi in range(20):
        imp=IterativeImputer(estimator=BayesianRidge(),sample_posterior=True,max_iter=15,random_state=mi)
        Z=base[cols+aux].copy(); Z[aux]=Z[aux].fillna(Z[aux].median())
        arr=imp.fit_transform(Z); d=base.copy(); d[cols+aux]=arr
        d['ghed_pc_usd_raw_l2']=np.exp(d['ghed_pc_usd_raw_l2']); d['ldi']=np.exp(d.ldi)
        d[yv]=sub[yv].values   # outcome never imputed
        b,se,n,k=fit(d,yv,ext='ext_pct_che_raw_l2',ghed='ghed_pc_usd_raw_l2',san='sanit_basic_pct_raw',wat='water_basic_pct_raw')
        B.append(b);V.append(se**2)
    B=np.array(B);V=np.array(V); qb=B.mean(); W=V.mean(); Bv=B.var(ddof=1); T=W+(1+1/20)*Bv
    out.append(row('Multiple imputation (MICE, m = 20)',outc,qb,np.sqrt(T),n,k,f'FMI={((1+1/20)*Bv/T):.2f}'))
res=pd.DataFrame(out); res.to_csv('results/missing_sensitivity.csv',index=False)
json.dump(ann,open('results/missing_summary.json','w'),indent=1)
print(prof.to_string()); print(ann); print(pr.to_string()); print(res.to_string())
