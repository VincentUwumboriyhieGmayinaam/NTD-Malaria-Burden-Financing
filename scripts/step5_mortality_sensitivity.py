"""Sensitivity outcome: age-standardised malaria death rate (GBD 2023), preferred two-way FE (Driscoll-Kraay)."""
import pandas as pd, numpy as np, warnings, statsmodels.api as sm
from linearmodels.panel import PanelOLS
warnings.filterwarnings('ignore')
p=pd.read_csv('data/processed/panel_2005_2023.csv')
p['log_ldi']=np.log(p.ldi); p['log_ext_pc_l2']=np.log1p(p.ext_pc_usd_l2); p['ext10_l2']=p.ext_pct_che_l2/10
p['log_ghed_l2']=np.log(p.ghed_pc_usd_l2); p['san10']=p.sanit_basic_pct/10; p['wat10']=p.water_basic_pct/10; p['uhc10']=p.uhc/10
dth=pd.read_csv('data/raw/gbd/country_trend__malaria__deaths_asr__2007_2022.csv')[['location_id','year','rate_combined']]
loc=pd.read_csv('data/processed/gbd_locations_iso3.csv')[['location_id','iso3']]
dth=dth.merge(loc,on='location_id'); p=p.merge(dth[['iso3','year','rate_combined']],on=['iso3','year'],how='left')
p['y_mal_death']=np.log1p(p.rate_combined)
d0=p[(p.year>=2007)&(p.year<=2022)&(p.lmic==1)&(p.mal_endemic==1)]
rows=[]
for spec,x in [('Share (per 10 pp)','ext10_l2'),('Per capita (log)','log_ext_pc_l2')]:
    X=[x,'log_ghed_l2','log_ldi','uhc10','san10','wat10']
    for yv,lab in [('y_mal_death','Malaria deaths, log(1 + ASR)'),('y_mal','Malaria DALYs, log(1 + ASR)')]:
        d=d0.dropna(subset=X+[yv]).set_index(['iso3','year'])
        m=PanelOLS(d[yv],sm.add_constant(d[X]),entity_effects=True,time_effects=True,drop_absorbed=True).fit(cov_type='kernel',kernel='bartlett',bandwidth=3)
        mc=PanelOLS(d[yv],sm.add_constant(d[X]),entity_effects=True,time_effects=True,drop_absorbed=True).fit(cov_type='clustered',cluster_entity=True)
        b=m.params[x]; ci=m.conf_int().loc[x]; cc=mc.conf_int().loc[x]
        rows.append(dict(outcome=lab,exposure=spec,pct=100*(np.exp(b)-1),lo=100*(np.exp(ci.lower)-1),hi=100*(np.exp(ci.upper)-1),p=m.pvalues[x],
                         lo_cl=100*(np.exp(cc.lower)-1),hi_cl=100*(np.exp(cc.upper)-1),p_cl=mc.pvalues[x],n=len(d),countries=d.index.get_level_values(0).nunique()))
o=pd.DataFrame(rows); o.to_csv('results/rev_mortality_sensitivity.csv',index=False); print(o.round(3).to_string())
