"""Step 2 analysis: descriptives, inequality, spatial autocorrelation, regression heterogeneity,
funding-cut scenarios. Outputs -> results/*.csv and results/key_numbers.json"""
import pandas as pd, numpy as np, json, warnings, geopandas as gpd
import statsmodels.formula.api as smf, statsmodels.api as sm
from libpysal.weights import KNN
from esda.moran import Moran, Moran_Local
warnings.filterwarnings('ignore'); rng=np.random.default_rng(20261007)
P='data/processed'; K={}
cs=pd.read_csv(f'{P}/analysis_country_2023.csv')
SR_ORDER=['Sub-Saharan Africa','South Asia','Southeast Asia, East Asia, and Oceania','Latin America and Caribbean',
          'North Africa and Middle East','Central Europe, Eastern Europe, and Central Asia','High-income']
cs['sr']=pd.Categorical(cs.super_region_name,SR_ORDER)
cs['ntd']=cs.daly_asr_ntd_excl_malaria; cs['mal']=cs.daly_asr_malaria
cs['pop']=cs.pop_latest

# ---------------- A. descriptives ----------------
g=cs.groupby('sr',observed=True)
tab=pd.DataFrame({'countries':g.size(),
  'dalys_ntdm_m':g.daly_n_neglected_tropical_diseases_and_malaria.sum()/1e6,
  'dalys_ntd_m':g.daly_n_ntd_excl_malaria.sum()/1e6,'dalys_mal_m':g.daly_n_malaria.sum()/1e6,
  'pop_m':g['pop'].sum()/1e6})
for c in ['dalys_ntdm_m','dalys_ntd_m','dalys_mal_m','pop_m']: tab[c.replace('_m','_share')]=100*tab[c]/tab[c].sum()
tr=pd.read_csv(f'{P}/gbd_superregion_trends.csv')
def asr(cause,meas,yr):
    t=tr[(tr.cause_name==cause)&(tr.measure==meas)&(tr.year==yr)].set_index('location_name'); return t.rate_age_std_combined
tab['asr_ntdm_2023']=asr('Neglected tropical diseases and malaria','dalys',2023)
tab['asr_mal_2023']=asr('Malaria','dalys',2023); tab['asr_ntd_2023']=tab.asr_ntdm_2023-tab.asr_mal_2023
tab.to_csv('results/table1_superregion_burden.csv'); print(tab.round(2).to_string())
glob_=tr[(tr.location_name=='Global')&(tr.measure=='dalys')]
K['global_dalys_ntdm_2023']=float(glob_[(glob_.year==2023)&(glob_.cause_name.str.startswith('Negl'))].count_combined.iloc[0])
K['global_dalys_ntdm_2023_ui']=[float(glob_[(glob_.year==2023)&(glob_.cause_name.str.startswith('Negl'))][c].iloc[0]) for c in ['count_lower_combined','count_upper_combined']]
K['global_dalys_mal_2023']=float(glob_[(glob_.year==2023)&(glob_.cause_name=='Malaria')].count_combined.iloc[0])
K['ssa_share_ntdm']=float(tab.loc['Sub-Saharan Africa','dalys_ntdm_share']); K['ssa_share_ntd']=float(tab.loc['Sub-Saharan Africa','dalys_ntd_share'])
K['ssa_share_pop']=float(tab.loc['Sub-Saharan Africa','pop_share'])

# cause x super-region (counts -> all-age rate per 100k; share of global by cause)
causes=[c[len('daly_n_'):] for c in cs.columns if c.startswith('daly_n_') and c not in('daly_n_neglected_tropical_diseases_and_malaria','daly_n_ntd_excl_malaria')]
cm=g[[f'daly_n_{c}' for c in causes]].sum(); cm.columns=causes
cm.T.to_csv('results/cause_by_superregion_dalys.csv')
(100*cm/cm.sum()).T.to_csv('results/cause_by_superregion_share_of_global.csv')
(cm.div(tab.pop_m*1e6,axis=0)*1e5).T.to_csv('results/cause_by_superregion_rate_per100k.csv')
gt=cm.sum().sort_values(ascending=False); gt.to_csv('results/cause_global_dalys_2023.csv')

# inequality: concentration index (pop-weighted, ranked by SDI) and Theil decomposition
def conc_index(y,rankvar,w):
    d=pd.DataFrame({'y':y,'r':rankvar,'w':w}).dropna().sort_values('r')
    d['wf']=d.w/d.w.sum(); d['R']=d.wf.cumsum()-d.wf/2; mu=(d.y*d.wf).sum()
    ci=2*(d.wf*(d.y-mu)*(d.R-(d.wf*d.R).sum())).sum()/mu
    d['cum_pop']=d.wf.cumsum(); d['cum_y']=(d.y*d.wf).cumsum()/(d.y*d.wf).sum(); return ci,d
ineq={}; curves=[]
for nm,col in [('NTDs (excl. malaria)','ntd'),('Malaria','mal')]:
    ci,d=conc_index(cs[col],cs.sdi_2023,cs['pop'])
    bs=[]
    for _ in range(2000):
        i=rng.integers(0,len(d),len(d)); bs.append(conc_index(d.y.values[i],d.r.values[i],d.w.values[i])[0])
    ineq[nm]={'CI':ci,'lo':np.percentile(bs,2.5),'hi':np.percentile(bs,97.5)}
    curves.append(d.assign(measure=nm)[['measure','cum_pop','cum_y','r']])
pd.concat(curves).to_csv('results/concentration_curves.csv',index=False)
def theil(y,w,grp):
    d=pd.DataFrame({'y':y,'w':w,'g':grp}).dropna(); d=d[d.y>0]; s=d.w/d.w.sum(); mu=(s*d.y).sum()
    T=(s*(d.y/mu)*np.log(d.y/mu)).sum(); gg=d.assign(s=s).groupby('g',observed=True)
    sg=gg.s.sum(); mug=gg.apply(lambda x:(x.s*x.y).sum()/x.s.sum())
    Tb=(sg*(mug/mu)*np.log(mug/mu)).sum(); return T,Tb,T-Tb
for nm,col in [('NTDs (excl. malaria)','ntd'),('Malaria','mal')]:
    T,Tb,Tw=theil(cs[col],cs['pop'],cs.sr); ineq[nm].update({'Theil':T,'between_pct':100*Tb/T,'within_pct':100*Tw/T})
pd.DataFrame(ineq).T.to_csv('results/inequality_metrics.csv'); K['inequality']=ineq; print(pd.DataFrame(ineq).T.round(3))

# ---------------- B. spatial autocorrelation ----------------
ne=gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson')
ne['iso3']=np.where(ne.ISO_A3=='-99',ne.ADM0_A3,ne.ISO_A3)
ne.loc[ne.ADMIN=='France','iso3']='FRA'; ne.loc[ne.ADMIN=='Norway','iso3']='NOR'; ne.loc[ne.ADMIN=='Kosovo','iso3']='XKX'
geo=ne[['iso3','geometry']].dissolve('iso3').reset_index().merge(cs,on='iso3',how='inner').to_crs('ESRI:54030')
pts=geo.copy(); pts['geometry']=geo.representative_point()
w=KNN.from_dataframe(pts,k=6); w.transform='r'
sp={}
for nm,col in [('ntd','ntd'),('mal','mal')]:
    y=np.log1p(geo[col].values)
    mi=Moran(y,w,permutations=9999); lisa=Moran_Local(y,w,permutations=9999,seed=1)
    sp[nm]={'I':mi.I,'p_sim':mi.p_sim,'z':mi.z_sim}
    q=pd.Series(lisa.q).map({1:'High–High',2:'Low–High',3:'Low–Low',4:'High–Low'})
    sig=lisa.p_sim<0.05
    from statsmodels.stats.multitest import multipletests
    fdr=multipletests(lisa.p_sim,method='fdr_bh')[0]
    geo[f'lisa_{nm}']=np.where(sig,q,'Not significant'); geo[f'lisa_{nm}_fdr']=np.where(fdr,q,'Not significant')
    geo[f'lisa_{nm}_p']=lisa.p_sim; geo[f'lag_{nm}']=w.sparse@y; geo[f'z_{nm}']=y
    sp[nm]['n_HH']=int((geo[f'lisa_{nm}']=='High–High').sum()); sp[nm]['HH_countries']=geo.loc[geo[f'lisa_{nm}']=='High–High','location_name'].tolist()
K['spatial']=sp; print({k:{kk:(round(v,3) if isinstance(v,float) else v) for kk,v in d.items() if kk!='HH_countries'} for k,d in sp.items()})
geo.drop(columns='geometry').to_csv('results/spatial_lisa_country.csv',index=False)
geo[['iso3','location_name','super_region_name','lisa_ntd','lisa_mal','lisa_ntd_fdr','lisa_mal_fdr','geometry']].to_file('results/lisa.gpkg',driver='GPKG')

# ---------------- C. regression ----------------
d=cs.copy()
d['y_ntd']=np.log(d.ntd); d['y_mal']=np.log1p(d.mal)
d['log_ldi']=np.log(d.ldi_2023); d['log_che']=np.log(d.che_pc_usd_latest)
X=['log_ldi','uhc_2023','sanit_basic_pct_latest','water_basic_pct_latest','rural_pct_latest','ext_pct_che_latest']
labels={'log_ldi':'Income per capita (log LDI)','uhc_2023':'UHC effective coverage index','sanit_basic_pct_latest':'Basic sanitation coverage',
 'water_basic_pct_latest':'Basic drinking-water coverage','rural_pct_latest':'Rural population share','ext_pct_che_latest':'External share of health spending'}
dm=d.dropna(subset=X+['y_ntd']).copy()
for x in X: dm[x+'_z']=(dm[x]-dm[x].mean())/dm[x].std()
Z=[x+'_z' for x in X]; K['n_regression']=len(dm)
res=[]
for yv,lab in [('y_ntd','NTDs (excl. malaria)'),('y_mal','Malaria')]:
    m=smf.ols(f"{yv} ~ {'+'.join(Z)} + C(sr)",dm).fit(cov_type='HC3')
    for x in Z:
        b,(lo,hi)=m.params[x],m.conf_int().loc[x]
        res.append({'outcome':lab,'model':'Pooled OLS + super-region FE','term':labels[x[:-2]],'pct':100*(np.exp(b)-1),'lo':100*(np.exp(lo)-1),'hi':100*(np.exp(hi)-1),'p':m.pvalues[x],'n':int(m.nobs),'r2':m.rsquared})
    # spatial error robustness
    from spreg import ML_Error
    sub=dm.merge(geo[['iso3']].reset_index(),on='iso3')
    gg=geo.set_index('iso3').loc[sub.iso3]; p2=gg.copy(); p2['geometry']=gg.representative_point()
    w2=KNN.from_dataframe(p2,k=6); w2.transform='r'
    Xm=pd.concat([sub[Z],pd.get_dummies(sub.sr,drop_first=True).astype(float)],axis=1)
    me=ML_Error(sub[[yv]].values,Xm.values,w=w2,name_x=list(Xm.columns))
    for i,x in enumerate(Z):
        b=me.betas[i+1,0]; se=me.std_err[i+1]
        res.append({'outcome':lab,'model':'Spatial error model (ML)','term':labels[x[:-2]],'pct':100*(np.exp(b)-1),'lo':100*(np.exp(b-1.96*se)-1),'hi':100*(np.exp(b+1.96*se)-1),'p':me.z_stat[i+1][1],'n':int(me.n),'r2':np.nan})
    K[f'lambda_{yv}']=float(me.lam)
    # residual Moran of OLS
    K[f'resid_moran_{yv}']=float(Moran(m.resid.loc[sub.index if False else m.resid.index].values[:len(sub)],w2,permutations=999).I) if len(sub)==len(m.resid) else None
reg=pd.DataFrame(res); reg.to_csv('results/regression_determinants.csv',index=False)
# heterogeneity: region-specific slope of external dependence (interaction) + LR test
het=[]
for yv,lab in [('y_ntd','NTDs (excl. malaria)'),('y_mal','Malaria')]:
    base=f"{yv} ~ {'+'.join(Z)} + C(sr)"
    m0=smf.ols(base,dm).fit(); m1=smf.ols(base+" + C(sr):ext_pct_che_latest_z",dm).fit()
    lr=2*(m1.llf-m0.llf); dfd=m1.df_model-m0.df_model
    from scipy.stats import chi2
    K[f'het_LR_{yv}']={'LR':lr,'df':dfd,'p':float(chi2.sf(lr,dfd))}
    m1r=smf.ols(f"{yv} ~ {'+'.join([z for z in Z if z!='ext_pct_che_latest_z'])} + C(sr) + C(sr):ext_pct_che_latest_z",dm).fit(cov_type='HC3')
    for s in SR_ORDER:
        t=f'C(sr)[{s}]:ext_pct_che_latest_z'
        if t in m1r.params and dm[dm.sr==s].shape[0]>=5:
            b,(lo,hi)=m1r.params[t],m1r.conf_int().loc[t]
            het.append({'outcome':lab,'super_region':s,'n':int((dm.sr==s).sum()),'pct':100*(np.exp(b)-1),'lo':100*(np.exp(lo)-1),'hi':100*(np.exp(hi)-1)})
    # mixed model random slope
    try:
        mm=smf.mixedlm(f"{yv} ~ {'+'.join(Z)}",dm,groups=dm.sr.astype(str),re_formula='~ext_pct_che_latest_z').fit(reml=True)
        K[f'mixed_{yv}']={'fixed_ext':float(mm.params['ext_pct_che_latest_z']),'re_var_slope':float(mm.cov_re.iloc[1,1]),'re_var_int':float(mm.cov_re.iloc[0,0])}
    except Exception as e: K[f'mixed_{yv}']=str(e)
pd.DataFrame(het).to_csv('results/regression_heterogeneity_external.csv',index=False)
print(reg[reg.model.str.startswith('Pooled')].round(3).to_string()); print(pd.DataFrame(het).round(2).to_string())

# ---------------- D. elasticity (first differences 2010->2023) & scenarios ----------------
wb=pd.read_csv(f'{P}/wb_country_year_wide.csv')
def avg(var,lo,hi): return wb[(wb.year>=lo)&(wb.year<=hi)].groupby('iso3')[var].mean()
fd=cs[['iso3','sr','daly_asr_ntd_core14_2010','daly_asr_ntd_core14_2023','daly_asr_malaria_2010','mal','ldi_2013','ldi_2023']].copy()
for v in ['che_pc_usd','sanit_basic_pct','gdppc_ppp']:
    fd[v+'_0']=fd.iso3.map(avg(v,2009,2011)); fd[v+'_1']=fd.iso3.map(avg(v,2021,2023))
fd['dy_ntd']=np.log(fd.daly_asr_ntd_core14_2023)-np.log(fd.daly_asr_ntd_core14_2010)
fd['dy_mal']=np.log1p(fd.mal)-np.log1p(fd.daly_asr_malaria_2010)
fd['dche']=np.log(fd.che_pc_usd_1)-np.log(fd.che_pc_usd_0); fd['dgdp']=np.log(fd.gdppc_ppp_1)-np.log(fd.gdppc_ppp_0)
fd['dsan']=(fd.sanit_basic_pct_1-fd.sanit_basic_pct_0)/10
fd=fd[(fd.sr!='High-income')].dropna(subset=['dy_ntd','dche','dgdp','dsan'])
fd=fd[fd.daly_asr_ntd_core14_2010>10]   # endemic settings
el={}
for yv in ['dy_ntd','dy_mal']:
    f=f"{yv} ~ dche + dgdp + dsan + C(sr)"
    m=smf.ols(f,fd).fit(cov_type='HC3'); bs=[]
    for _ in range(2000):
        s=fd.sample(len(fd),replace=True,random_state=int(rng.integers(1e9)))
        try: bs.append(smf.ols(f,s).fit().params['dche'])
        except: pass
    el[yv]={'beta':m.params['dche'],'lo':m.conf_int().loc['dche',0],'hi':m.conf_int().loc['dche',1],'p':m.pvalues['dche'],'n':int(m.nobs),'boot':np.array(bs)}
    print(yv,'elasticity',round(m.params['dche'],3),m.conf_int().loc['dche'].round(3).tolist(),'n',int(m.nobs))
K['elasticity']={k:{kk:float(vv) for kk,vv in v.items() if kk!='boot'} for k,v in el.items()}

# ---- Scenario model: "gains at risk" (donor-attributable share of 2010-2023 burden reductions) ----
# Excess annual DALYs_c = max(0, ASR2010 - ASR2023)/1e5 * Pop * ext_share * cut   (Monte Carlo over GBD UIs and cut range)
SCEN={'Mild':(0.05,0.15),'Reference':(0.19,0.26),'Severe':(0.40,0.60)}
SCEN_LAB={'Mild':'Mild (5–15% cut)','Reference':'Reference (19–26% cut; IHME 2025)','Severe':'Severe (40–60% cut)'}
BLc=pd.read_csv(f'{P}/gbd_country_burden_long.csv')
core=sorted(set(BLc[(BLc.year==2010)&(BLc.measure=='dalys')].cause)-{'neglected_tropical_diseases_and_malaria','malaria'})
K['core_ntds_2010']=core
def load(cause,yr):
    t=pd.read_csv(f'{P}/gbd_country_burden_long.csv') if 'BL' not in globals() else BL
    return t
BL=pd.read_csv(f'{P}/gbd_country_burden_long.csv'); BL=BL[BL.measure=='dalys']
sc=cs.dropna(subset=['ext_pct_che_latest','pop_latest']).copy(); sc=sc[sc.sr!='High-income'].reset_index(drop=True)
NS=2000
def draws(cause,yr):
    t=BL[(BL.cause==cause)&(BL.year==yr)].set_index('location_id').reindex(sc.location_id)
    mu=t.asr.values.clip(1e-9); sd=((np.log(t.asr_hi.clip(1e-9))-np.log(t.asr_lo.clip(1e-9)))/3.92).fillna(0).values
    return np.exp(np.log(mu)[None,:]+sd[None,:]*rng.standard_normal((NS,len(sc))))
gain={}
gain['NTDs (excl. malaria)']=sum(draws(c,2010) for c in core)-sum(draws(c,2023) for c in core)
gain['Malaria']=draws('malaria',2010)-draws('malaria',2023)
ext=sc.ext_pct_che_latest.values/100; popn=sc.pop_latest.values; gdp=sc.gdppc_usd_latest.fillna(sc.gdppc_usd_latest.median()).values
rows=[]; cty=[]
for nm,(a,b) in SCEN.items():
    cut=rng.uniform(a,b,(NS,1))
    for outc,G in gain.items():
        ex=np.clip(G,0,None)/1e5*popn[None,:]*ext[None,:]*cut          # draws x country
        cty.append(pd.DataFrame({'iso3':sc.iso3,'location_name':sc.location_name,'sr':sc.sr,'scenario':nm,'outcome':outc,
            'excess_dalys':np.median(ex,0),'lo':np.percentile(ex,2.5,0),'hi':np.percentile(ex,97.5,0),
            'gain_asr_median':np.median(G,0),'ext_share':ext,'value_usd_1gdp':np.median(ex,0)*gdp,
            'lost_ext_usd':(a+b)/2*sc.ext_pc_usd_latest.values*popn,'ghed_total_usd':sc.ghed_pc_usd_latest.values*popn}))
        for s in SR_ORDER[:-1]+['All endemic (LMIC) countries']:
            m=(sc.sr==s).values if s in SR_ORDER else np.ones(len(sc),bool)
            tot=ex[:,m].sum(1); val=(ex[:,m]*gdp[m][None,:]).sum(1)
            base=sc.loc[m,'daly_n_ntd_excl_malaria' if outc.startswith('NTD') else 'daly_n_malaria'].sum()
            rows.append({'scenario':nm,'scenario_label':SCEN_LAB[nm],'outcome':outc,'super_region':s,'excess_dalys':np.median(tot),'lo':np.percentile(tot,2.5),'hi':np.percentile(tot,97.5),
                'value_usd_1gdp':np.median(val),'value_lo':np.percentile(val,2.5),'value_hi':np.percentile(val,97.5),'pct_of_2023_burden':(100*np.median(tot)/base) if base>=1000 else np.nan})
scen=pd.DataFrame(rows); scen.to_csv('results/scenario_excess_dalys_superregion.csv',index=False)
ctyd=pd.concat(cty); ctyd.to_csv('results/scenario_excess_dalys_country.csv',index=False)
gap=ctyd[ctyd.outcome=='Malaria'].groupby(['scenario','sr'],observed=True)[['lost_ext_usd','ghed_total_usd']].sum().reset_index()
gap['domestic_increase_needed_pct']=100*gap.lost_ext_usd/gap.ghed_total_usd; gap.to_csv('results/scenario_financing_gap.csv',index=False)
K['scenario_global']=scen[scen.super_region.str.startswith('All')].to_dict('records')
print(scen[scen.super_region.isin(['All endemic (LMIC) countries','Sub-Saharan Africa'])][['scenario','outcome','super_region','excess_dalys','lo','hi','value_usd_1gdp','pct_of_2023_burden']].round(1).to_string())
print(gap[gap.scenario=='Reference'].round(1).to_string())
json.dump(K,open('results/key_numbers.json','w'),indent=1,default=lambda o: float(o) if hasattr(o,'__float__') else str(o))
