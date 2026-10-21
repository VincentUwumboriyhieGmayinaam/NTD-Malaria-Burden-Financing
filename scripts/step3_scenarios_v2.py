"""Scenario model v2 (corrects v1):
 (1) uses ALL-AGE counts and population (crude rates), not age-standardised rates x population;
 (2) all 19 NTD causes have 2010 baselines;
 (3) GBD uncertainty propagated with comonotonic (rank-correlated) draws for 2010 and 2023 (sensitivity: independent);
 (4) two complementary estimators: A) 'gains-at-risk' accounting model; B) econometric model using the preferred
     two-way FE (Driscoll-Kraay) within-country estimate."""
import pandas as pd, numpy as np, json
rng=np.random.default_rng(20261007); NS=4000
P='data/processed'; R='data/raw'
cs=pd.read_csv(f'{P}/analysis_country_2023.csv'); BL=pd.read_csv(f'{P}/gbd_country_burden_long.csv'); BL=BL[BL.measure=='dalys']
wb=pd.read_csv(f'{P}/wb_country_year_wide.csv'); pop=wb.pivot(index='iso3',columns='year',values='pop')
SR=['Sub-Saharan Africa','South Asia','Southeast Asia, East Asia, and Oceania','Latin America and Caribbean','North Africa and Middle East','Central Europe, Eastern Europe, and Central Asia']
sc=cs[cs.super_region_name.isin(SR)].dropna(subset=['ext_pct_che_latest']).reset_index(drop=True)
sc=sc[sc.iso3.isin(pop.index)].reset_index(drop=True)
p10=pop.loc[sc.iso3,2010].values; p23=pop.loc[sc.iso3,2023].fillna(pop.loc[sc.iso3,2022]).values
NTD=sorted(set(BL.cause)-{'neglected_tropical_diseases_and_malaria','malaria'})
def cdraw(cause,yr,Zc):
    t=BL[(BL.cause==cause)&(BL.year==yr)].set_index('location_id').reindex(sc.location_id)
    mu=t.n.fillna(0).clip(lower=1e-6).values; lo=t.n_lo.fillna(0).clip(lower=1e-6).values; hi=t.n_hi.fillna(0).clip(lower=1e-6).values
    sd=((np.log(hi)-np.log(lo))/3.92); sd=np.nan_to_num(sd)
    return np.exp(np.log(mu)[None,:]+sd[None,:]*Zc)
def gains(causes,comonotonic=True):
    G=np.zeros((NS,len(sc)))
    for c in causes:
        Z1=rng.standard_normal((NS,len(sc))); Z2=Z1 if comonotonic else rng.standard_normal((NS,len(sc)))
        r10=cdraw(c,2010,Z1)/p10[None,:]; r23=cdraw(c,2023,Z2)/p23[None,:]
        G+= (r10-r23)       # change in crude (all-age) rate, per person
    return G
G={'NTDs (excl. malaria)':gains(NTD),'Malaria':gains(['malaria'])}
Gind={'NTDs (excl. malaria)':gains(NTD,False),'Malaria':gains(['malaria'],False)}
ext=sc.ext_pct_che_latest.values/100; gdp=sc.gdppc_usd_latest.fillna(sc.gdppc_usd_latest.median()).values
SCEN={'Mild':(0.05,0.15),'Reference':(0.19,0.26),'Severe':(0.40,0.60)}
# econometric: preferred two-way FE (Driscoll-Kraay), share spec; beta per +10 pp external share (log outcome)
pm=pd.read_csv('results/panel_models_comparison.csv')
def beta(outc):
    r=pm[(pm.outcome==outc)&(pm.spec=='A: share')&(pm.model=='Two-way FE (Driscoll–Kraay)')].iloc[0]; return r.beta,r.se
rows=[]; cty=[]
for nm,(a,b) in SCEN.items():
    cut=rng.uniform(a,b,(NS,1))
    for outc in G:
        base=sc['daly_n_ntd_excl_malaria' if outc.startswith('NTD') else 'daly_n_malaria'].values
        exA=np.clip(G[outc],0,None)*p23[None,:]*ext[None,:]*cut
        exI=np.clip(Gind[outc],0,None)*p23[None,:]*ext[None,:]*cut
        bm,bs=beta(outc); bd=rng.normal(bm,bs,(NS,1))
        new_share=ext[None,:]*(1-cut)/(1-cut*ext[None,:]); dpp10=(new_share-ext[None,:])*100/10   # negative
        if outc.startswith('NTD'):
            exB=base[None,:]*(np.exp(bd*dpp10)-1)          # log(rate) model: proportional change in rate
        else:                                               # log(1+rate) model: convert on the (1+rate) scale
            asr=sc['daly_asr_malaria'].values[None,:]
            new_asr=(1+asr)*np.exp(bd*dpp10)-1
            ratio=np.where(asr>0,new_asr/np.where(asr>0,asr,1),1.0)
            exB=base[None,:]*(ratio-1)
        cty.append(pd.DataFrame({'iso3':sc.iso3,'location_name':sc.location_name,'sr':sc.super_region_name,'scenario':nm,'outcome':outc,
             'excess_A':np.median(exA,0),'A_lo':np.percentile(exA,2.5,0),'A_hi':np.percentile(exA,97.5,0),'excess_B':np.median(exB,0),
             'pop2023':p23,'ext_share':ext,'value_A_usd':np.median(exA,0)*gdp,
             'lost_ext_usd':(a+b)/2*sc.ext_pc_usd_latest.values*p23,'ghed_total_usd':sc.ghed_pc_usd_latest.values*p23}))
        for s in SR+['All LMICs']:
            m=(sc.super_region_name==s).values if s in SR else np.ones(len(sc),bool)
            tA=exA[:,m].sum(1); tI=exI[:,m].sum(1); tB=exB[:,m].sum(1); vA=(exA[:,m]*gdp[m][None,:]).sum(1); bse=base[m].sum()
            rows.append({'scenario':nm,'outcome':outc,'super_region':s,
              'A_excess':np.median(tA),'A_lo':np.percentile(tA,2.5),'A_hi':np.percentile(tA,97.5),
              'A_indep_excess':np.median(tI),'A_indep_lo':np.percentile(tI,2.5),'A_indep_hi':np.percentile(tI,97.5),
              'B_excess':np.median(tB),'B_lo':np.percentile(tB,2.5),'B_hi':np.percentile(tB,97.5),
              'A_value_usd':np.median(vA),'A_value_lo':np.percentile(vA,2.5),'A_value_hi':np.percentile(vA,97.5),
              'A_pct_2023':100*np.median(tA)/bse if bse>1000 else np.nan,'baseline_2023':bse})
s=pd.DataFrame(rows); s.to_csv('results/scenario_v2_superregion.csv',index=False)
c=pd.concat(cty); c.to_csv('results/scenario_v2_country.csv',index=False)
g=c[c.outcome=='Malaria'].groupby(['scenario','sr'])[['lost_ext_usd','ghed_total_usd']].sum().reset_index(); g['domestic_increase_needed_pct']=100*g.lost_ext_usd/g.ghed_total_usd
g.to_csv('results/scenario_financing_gap.csv',index=False)
pd.set_option('display.width',260)
print(s[s.super_region.isin(['All LMICs','Sub-Saharan Africa'])][['scenario','outcome','super_region','A_excess','A_lo','A_hi','A_indep_lo','A_indep_hi','B_excess','B_lo','B_hi','A_pct_2023']].round(0).to_string())
print('countries',len(sc))
