"""Build analysis panel 2005-2023: GBD burden (annual) + GBD covariates (SDI, UHC, LDI) + World Bank WDI.
WDI gaps: within-country linear interpolation only (no extrapolation beyond observed range except last-observation-carried-forward <=2 years, flagged)."""
import pandas as pd, numpy as np
P='data/processed'; R='data/raw'
g=pd.read_csv(f'{P}/gbd_country_panel_2005_2023.csv'); loc=pd.read_csv(f'{P}/gbd_locations_iso3.csv')
g=g.merge(loc[['location_id','iso3','super_region_name']],on='location_id')
sdi=pd.read_csv(f'{R}/gbd/country__sdi.csv')[['location_id','year','sdi']].drop_duplicates(['location_id','year'])
cov=[]
for f,nm in [('country__cov_universal_health_coverage.csv','uhc'),('country__cov_ldi_i_per_capita.csv','ldi')]:
    c=pd.read_csv(f'{R}/gbd/{f}')[['location_id','year','value_combined']].drop_duplicates(['location_id','year']).rename(columns={'value_combined':nm}); cov.append(c)
p=g.merge(sdi,on=['location_id','year'],how='left').merge(cov[0],on=['location_id','year'],how='left').merge(cov[1],on=['location_id','year'],how='left')
wb=pd.read_csv(f'{P}/wb_country_year_wide.csv')
keep=['ext_pct_che','ext_pc_usd','che_pc_usd','ghed_pc_usd','ghed_pct_che','oop_pct_che','gdppc_ppp','sanit_basic_pct','water_basic_pct','rural_pct','pop','oda_pc_usd']
wb=wb[['iso3','year']+keep]
full=pd.MultiIndex.from_product([wb.iso3.unique(),range(2003,2024)],names=['iso3','year'])
wb=wb.set_index(['iso3','year']).reindex(full).sort_index()
flag=wb.isna()
wb=wb.groupby(level=0).transform(lambda s: s.interpolate(limit_area='inside').ffill(limit=2))
wb['imputed_any']=(flag & wb.notna()).any(axis=1).astype(int)
wb=wb.reset_index()
p=p.merge(wb,on=['iso3','year'],how='left')
# lags (2-year) of time-varying exposures to reduce simultaneity
p=p.sort_values(['iso3','year'])
for v in ['ext_pct_che','ext_pc_usd','che_pc_usd','ghed_pc_usd','uhc','ldi','sanit_basic_pct','water_basic_pct']:
    p[f'{v}_l2']=p.groupby('iso3')[v].shift(2)
p['lmic']=(p.super_region_name!='High-income').astype(int)
p['y_ntd']=np.log(p.asr_ntd.clip(lower=0.01)); p['y_mal']=np.log1p(p.asr_malaria)
mx=p.groupby('iso3').asr_malaria.max(); p['mal_endemic']=p.iso3.map(mx>10).astype(int)
p.to_csv(f'{P}/panel_2005_2023.csv',index=False)
print(p.shape, p.iso3.nunique()); print(p[['ext_pct_che','ext_pc_usd_l2','uhc','ldi','sanit_basic_pct']].notna().mean().round(3).to_dict())
print('malaria-endemic countries:',p[p.mal_endemic==1].iso3.nunique())
