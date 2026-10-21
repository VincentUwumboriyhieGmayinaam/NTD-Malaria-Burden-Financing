"""Step 3: panel econometrics with assumption testing, spatial panel models, and comparison.
Primary estimand: within-country association between donor financing (external health expenditure) and
age-standardised NTD (excl. malaria) DALY rates, LMICs 2007-2022, exposures lagged 2 years."""
import pandas as pd, numpy as np, json, warnings
from linearmodels.panel import PanelOLS, RandomEffects, PooledOLS, FirstDifferenceOLS, compare
from scipy import stats
import statsmodels.api as sm
warnings.filterwarnings('ignore'); OUT={}
p=pd.read_csv('data/processed/panel_2005_2023.csv')
p['log_ldi']=np.log(p.ldi); p['log_che_l2']=np.log(p.che_pc_usd_l2); p['log_ext_pc_l2']=np.log1p(p.ext_pc_usd_l2)
p['ext10_l2']=p.ext_pct_che_l2/10      # per 10 percentage points
p['log_ghed_l2']=np.log(p.ghed_pc_usd_l2); p['san10']=p.sanit_basic_pct/10; p['wat10']=p.water_basic_pct/10; p['uhc10']=p.uhc/10
YEARS=(2007,2022)
def sample(outcome,lmic=True,endemic=False):
    d=p[(p.year>=YEARS[0])&(p.year<=YEARS[1])]
    if lmic: d=d[d.lmic==1]
    if endemic: d=d[d.mal_endemic==1]
    return d
SPEC={'A: share':['ext10_l2','log_ghed_l2','log_ldi','uhc10','san10','wat10'],
      'B: per-capita':['log_ext_pc_l2','log_ghed_l2','log_ldi','uhc10','san10','wat10']}
rows=[]; diag={}
for outc,yv,endem in [('NTDs (excl. malaria)','y_ntd',False),('Malaria','y_mal',True)]:
  for spec,X in SPEC.items():
    d=sample(yv,endemic=endem).dropna(subset=X+[yv]).set_index(['iso3','year'])
    y=d[yv]; Xc=sm.add_constant(d[X])
    mods={}
    mods['Pooled OLS']=PooledOLS(y,Xc).fit(cov_type='clustered',cluster_entity=True)
    mods['Random effects']=RandomEffects(y,Xc).fit(cov_type='clustered',cluster_entity=True)
    mods['Two-way FE (cluster)']=PanelOLS(y,Xc,entity_effects=True,time_effects=True,drop_absorbed=True).fit(cov_type='clustered',cluster_entity=True)
    mods['Two-way FE (Driscoll–Kraay)']=PanelOLS(y,Xc,entity_effects=True,time_effects=True,drop_absorbed=True).fit(cov_type='kernel',kernel='bartlett',bandwidth=3)
    mods['First difference']=FirstDifferenceOLS(y,d[X]).fit(cov_type='clustered',cluster_entity=True)
    # FE + country-specific linear trends (Frisch-Waugh: residualise on unit intercept+trend)
    dd=d.reset_index(); cols=[yv]+X
    def detrend(g):
        t=g.year.values-g.year.mean(); A=np.c_[np.ones(len(g)),t]
        return pd.DataFrame(g[cols].values-A@np.linalg.lstsq(A,g[cols].values,rcond=None)[0],columns=cols,index=g.index)
    rt=dd.groupby('iso3',group_keys=False).apply(detrend); rt[['iso3','year']]=dd[['iso3','year']]; rt=rt.set_index(['iso3','year'])
    mods['FE + country trends']=PanelOLS(rt[yv],rt[X],time_effects=True).fit(cov_type='clustered',cluster_entity=True)
    # Mundlak / correlated random effects
    mu=d.groupby(level=0)[X].transform('mean').add_suffix('_bar'); Xm=sm.add_constant(pd.concat([d[X],mu],axis=1))
    cre=RandomEffects(y,Xm).fit(cov_type='clustered',cluster_entity=True); mods['Mundlak CRE']=cre
    W=cre.wald_test(formula=' = '.join([])  if False else ', '.join(f'{c}_bar = 0' for c in X))
    for nm,m in mods.items():
        k=X[0]
        rows.append({'outcome':outc,'spec':spec,'model':nm,'term':k,'beta':m.params[k],'se':m.std_errors[k],'lo':m.conf_int().loc[k,'lower'],'hi':m.conf_int().loc[k,'upper'],
                     'p':m.pvalues[k],'n_obs':int(m.nobs),'n_countries':int(d.index.get_level_values(0).nunique()),'r2_within':getattr(m,'rsquared_within',np.nan)})
    # ---- assumption diagnostics on two-way FE ----
    fe=PanelOLS(y,Xc,entity_effects=True,time_effects=True,drop_absorbed=True).fit()
    e=fe.resids.unstack(level=1)     # countries x years
    # Pesaran CD
    E=e.values; N,T=E.shape; corr=[]
    for i in range(N):
        for j in range(i+1,N):
            m_=~np.isnan(E[i])&~np.isnan(E[j])
            if m_.sum()>=5: corr.append((m_.sum(),np.corrcoef(E[i,m_],E[j,m_])[0,1]))
    Tij=np.array([c[0] for c in corr]); rho=np.array([c[1] for c in corr]); CD=np.sqrt(2/(N*(N-1)))*np.nansum(np.sqrt(Tij)*rho)
    # Wooldridge serial-correlation test (FD residuals, H0 coef=-0.5)
    fd=FirstDifferenceOLS(y,d[X]).fit(); r=fd.resids.rename('r').reset_index().sort_values(['iso3','year']); r['rl']=r.groupby('iso3').r.shift(1); r=r.dropna()
    wm=sm.OLS(r.r,r.rl).fit(cov_type='cluster',cov_kwds={'groups':pd.factorize(r.iso3)[0]}); F_w=((wm.params.iloc[0]+0.5)/wm.bse.iloc[0])**2
    # Modified Wald groupwise heteroskedasticity
    s2=e.var(axis=1,ddof=1); s2_all=np.nanvar(E); Tw=e.notna().sum(1); Vi=(1/(Tw*(Tw-1)))*((e.sub(e.mean(1),axis=0)**2).sub(s2,axis=0)**2).sum(1)
    Wh=float(((s2-s2_all)**2/Vi).replace([np.inf],np.nan).dropna().sum())
    # Hausman (classical) & Mundlak robust
    fe1=PanelOLS(y,Xc,entity_effects=True,drop_absorbed=True).fit(); re1=RandomEffects(y,Xc).fit()
    b=fe1.params[X]-re1.params[X]; V=fe1.cov.loc[X,X]-re1.cov.loc[X,X]
    try: H=float(b@np.linalg.pinv(V)@b)
    except: H=np.nan
    # Breusch-Pagan LM for random effects (pooled residuals)
    po=PooledOLS(y,Xc).fit(); u=po.resids.unstack(1); n=u.shape[0]; t=u.notna().sum(1).mean()
    LM=(n*t/(2*(t-1)))*((u.sum(1)**2).sum()/(u**2).sum().sum()-1)**2
    # VIF
    from statsmodels.stats.outliers_influence import variance_inflation_factor as vif
    Z=sm.add_constant(d[X]).values; vifs={X[i]:float(vif(Z,i+1)) for i in range(len(X))}
    diag[f'{outc} | {spec}']={'Hausman_chi2':H,'Hausman_df':len(X),'Hausman_p':float(stats.chi2.sf(H,len(X))),
        'Mundlak_Wald':float(W.stat),'Mundlak_p':float(W.pval),'BreuschPagan_LM_RE':float(LM),'BP_p':float(stats.chi2.sf(LM,1)),
        'Pesaran_CD':float(CD),'CD_p':float(2*stats.norm.sf(abs(CD))),'Wooldridge_AR1_F':float(F_w),'Wooldridge_p':float(stats.f.sf(F_w,1,r.iso3.nunique()-1)),
        'ModWald_hetero_chi2':Wh,'ModWald_df':int(N),'ModWald_p':float(stats.chi2.sf(Wh,N)),'VIF':vifs,'N':int(N),'T_max':int(T)}
res=pd.DataFrame(rows); res.to_csv('results/panel_models_comparison.csv',index=False)
json.dump(diag,open('results/panel_assumption_tests.json','w'),indent=1)
pd.set_option('display.width',250)
print(res.round(4).to_string())
for k,v in diag.items(): print(k,{kk:(round(vv,3) if isinstance(vv,float) else vv) for kk,vv in v.items() if kk!='VIF'}, {a:round(b,1) for a,b in v['VIF'].items()})
