"""Build analysis-ready datasets: country cross-section (2023), country panel, super-region trends.
Inputs: data/raw/{gbd,wb,funding}; outputs: data/processed/*.csv"""
import pandas as pd, numpy as np, glob, re, os
R='data/raw'; P='data/processed'
loc=pd.read_csv(f'{P}/gbd_locations_iso3.csv')
ids=set(loc.location_id)

# ---------- GBD burden, wide by cause/measure/year ----------
recs=[]
for f in glob.glob(f'{R}/gbd/country__*__*__*.csv'):
    _,cause,meas,yr=os.path.basename(f)[:-4].split('__')
    d=pd.read_csv(f); d=d[d.location_id.isin(ids)]
    d=d[['location_id','rate_combined','rate_lower_combined','rate_upper_combined','count_combined','count_lower_combined','count_upper_combined']].copy()
    d.columns=['location_id','asr','asr_lo','asr_hi','n','n_lo','n_hi']
    d['cause']=cause; d['measure']=meas; d['year']=int(yr); recs.append(d)
burden=pd.concat(recs)
burden=burden.merge(loc,on='location_id')
burden.to_csv(f'{P}/gbd_country_burden_long.csv',index=False)

ntd_only=[c for c in burden.cause.unique() if c not in ('neglected_tropical_diseases_and_malaria','malaria')]
# NTDs excluding malaria (point estimates; age-std rates additive across mutually exclusive causes)
def agg_ntd(df):
    s=df[df.cause.isin(ntd_only)].groupby(['location_id','measure','year'])[['asr','n']].sum().reset_index()
    s['cause']='ntds_excl_malaria_sum'; return s
d23=burden[(burden.year==2023)&(burden.measure=='dalys')]
x=d23.pivot_table(index='location_id',columns='cause',values='asr'); x.columns=[f'daly_asr_{c}' for c in x.columns]
xn=d23.pivot_table(index='location_id',columns='cause',values='n'); xn.columns=[f'daly_n_{c}' for c in xn.columns]
cs=loc.set_index('location_id').join(x).join(xn)
cs['daly_asr_ntd_excl_malaria']=cs[[f'daly_asr_{c}' for c in ntd_only]].sum(1)
cs['daly_n_ntd_excl_malaria']=cs[[f'daly_n_{c}' for c in ntd_only]].sum(1)
for c in ['neglected_tropical_diseases_and_malaria']:
    u=d23[d23.cause==c].set_index('location_id')
    cs['daly_asr_ntdm_lo']=u.asr_lo; cs['daly_asr_ntdm_hi']=u.asr_hi
for meas in ['deaths','prevalence']:
    for c in ['neglected_tropical_diseases_and_malaria','malaria']:
        u=burden[(burden.year==2023)&(burden.measure==meas)&(burden.cause==c)].set_index('location_id')
        if len(u): cs[f'{meas}_asr_{c}']=u.asr; cs[f'{meas}_n_{c}']=u.n
# trends of aggregate
for c in ['neglected_tropical_diseases_and_malaria','malaria']:
    for y in [1990,2000,2010,2019]:
        u=burden[(burden.year==y)&(burden.measure=='dalys')&(burden.cause==c)].set_index('location_id')
        cs[f'daly_asr_{c}_{y}']=u.asr
# cause-specific 2010 -> NTD excl malaria 2010 (for causes available in 2010)
c10=[c for c in ntd_only if len(burden[(burden.year==2010)&(burden.cause==c)])]
u=burden[(burden.year==2010)&(burden.measure=='dalys')&(burden.cause.isin(c10))]
cs['daly_asr_ntd_core14_2010']=u.groupby('location_id').asr.sum()
cs['daly_asr_ntd_core14_2023']=cs[[f'daly_asr_{c}' for c in c10]].sum(1)
cs['n_causes_core14']=len(c10)
# GBD published % change 2010-2023 (NTD&M)
pc=pd.read_csv(f'{R}/gbd/country_pctchange__neglected_tropical_diseases_and_malaria__2010_2023.csv')
pc=pc[pc.location_id.isin(ids)].set_index('location_id')
cs['pc_asr_ntdm_2010_2023']=pc.percent_change_rate_age_std_combined
cs['pc_asr_ntdm_lo']=pc.lower_rate_age_std_combined; cs['pc_asr_ntdm_hi']=pc.upper_rate_age_std_combined
cs['pc_asr_ntdm_sig']=np.where(cs.pc_asr_ntdm_hi<0,'decline',np.where(cs.pc_asr_ntdm_lo>0,'increase','uncertain'))

# ---------- GBD covariates ----------
sdi=pd.read_csv(f'{R}/gbd/country__sdi.csv'); sdi=sdi[sdi.location_id.isin(ids)]
cs['sdi_2023']=sdi[sdi.year==2023].set_index('location_id').sdi
cs['sdi_quintile']=sdi[sdi.year==2023].set_index('location_id').sdi_quintile
cs['sdi_2010']=sdi[sdi.year==2010].set_index('location_id').sdi
for f,nm in [('country__cov_universal_health_coverage.csv','uhc'),('country__cov_ldi_i_per_capita.csv','ldi')]:
    c=pd.read_csv(f'{R}/gbd/{f}'); c=c[c.location_id.isin(ids)]
    cs[f'{nm}_2023']=c[c.year==2023].set_index('location_id').value_combined
    cs[f'{nm}_2013']=c[c.year==2013].set_index('location_id').value_combined

# ---------- World Bank ----------
wb=pd.read_csv(f'{R}/wb/wdi_long_2005_2024.csv')
short={'NY.GDP.PCAP.CD':'gdppc_usd','NY.GDP.PCAP.PP.KD':'gdppc_ppp','NY.GNP.PCAP.CD':'gnipc_usd','SH.XPD.CHEX.PC.CD':'che_pc_usd',
'SH.XPD.CHEX.GD.ZS':'che_pct_gdp','SH.XPD.GHED.PC.CD':'ghed_pc_usd','SH.XPD.GHED.CH.ZS':'ghed_pct_che','SH.XPD.GHED.GE.ZS':'ghed_pct_gge',
'SH.XPD.EHEX.CH.ZS':'ext_pct_che','SH.XPD.EHEX.PC.CD':'ext_pc_usd','SH.XPD.OOPC.CH.ZS':'oop_pct_che','DT.ODA.ODAT.PC.ZS':'oda_pc_usd',
'DT.ODA.ODAT.GN.ZS':'oda_pct_gni','DT.ODA.ODAT.CD':'oda_usd','SP.POP.TOTL':'pop','SP.RUR.TOTL.ZS':'rural_pct','SI.POV.DDAY':'poverty_pct',
'SH.H2O.BASW.ZS':'water_basic_pct','SH.STA.BASS.ZS':'sanit_basic_pct','SH.STA.ODFC.ZS':'open_defec_pct','SH.MLR.INCD.P3':'malaria_inc_per1000',
'SH.MLR.NETS.ZS':'itn_u5_pct','SH.STA.STNT.ZS':'stunting_pct','SP.POP.0014.TO.ZS':'pop0014_pct'}
wb['var']=wb.indicator.map(short)
wbp=wb.pivot_table(index=['iso3','year'],columns='var',values='value').reset_index()
wbp.to_csv(f'{P}/wb_country_year_wide.csv',index=False)
# latest value 2019-2023 (pre-cut baseline), and 2010-2014 mean
def latest(df,lo,hi):
    s=df[(df.year>=lo)&(df.year<=hi)].sort_values('year').groupby(['iso3','var']).value.last().unstack()
    return s
lat=latest(wb,2019,2023).add_suffix('_latest'); early=wb[(wb.year>=2010)&(wb.year<=2014)].groupby(['iso3','var']).value.mean().unstack().add_suffix('_2010_14')
meta=pd.read_csv(f'{R}/wb/wb_country_metadata.csv').set_index('iso3')[['income','lending','region']].add_prefix('wb_')
cs=cs.reset_index().merge(lat,left_on='iso3',right_index=True,how='left').merge(early[['ext_pct_che_2010_14','oda_pc_usd_2010_14','che_pc_usd_2010_14']],left_on='iso3',right_index=True,how='left').merge(meta,left_on='iso3',right_index=True,how='left')

# ---------- funding exposure ----------
us=pd.read_csv(f'{R}/funding/usaid_ntd_program_countries.csv')
cs['usaid_ntd_program']=cs.iso3.isin(us.iso3).astype(int)
cs['ntd_endemic_flag']=(cs.daly_asr_ntd_excl_malaria>cs.daly_asr_ntd_excl_malaria.quantile(0.25)).astype(int)
cs.to_csv(f'{P}/analysis_country_2023.csv',index=False)

# ---------- super-region trends ----------
tr=[]
for f in glob.glob(f'{R}/gbd/superregion_trend__*.csv'):
    d=pd.read_csv(f); tr.append(d[['location_name','location_id','year','cause_name','measure','count_combined','count_lower_combined','count_upper_combined','rate_combined','rate_age_std_combined']])
pd.concat(tr).to_csv(f'{P}/gbd_superregion_trends.csv',index=False)
print('cross-section',cs.shape); print(cs.isna().mean().sort_values(ascending=False).head(12).round(2))

# ---------- UN SDG (WHO-sourced) series ----------
sdg=pd.read_csv(f'{R}/who/un_sdg_ntd_malaria_series.csv')
for s,nm in [('SDG_SH_TRP_INTVN','ppl_req_ntd_interv'),('SDG_SH_STA_MALR','malaria_inc_per1000_risk')]:
    u=sdg[sdg.series==s]
    for y in [2010,2019,2023]:
        v=u[u.year==y].set_index('iso3').value; cs[f'{nm}_{y}']=cs.iso3.map(v)
cs['ppl_req_ntd_pct_pop_2023']=100*cs.ppl_req_ntd_interv_2023/cs.pop_latest
cs.to_csv(f'{P}/analysis_country_2023.csv',index=False)
print('with SDG',cs.shape, cs.ppl_req_ntd_interv_2023.notna().sum())
