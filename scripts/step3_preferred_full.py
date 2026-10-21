import pandas as pd, numpy as np, statsmodels.api as sm, warnings
from linearmodels.panel import PanelOLS
warnings.filterwarnings('ignore')
p=pd.read_csv('data/processed/panel_2005_2023.csv')
p['log_ldi']=np.log(p.ldi); p['ext10_l2']=p.ext_pct_che_l2/10; p['log_ghed_l2']=np.log(p.ghed_pc_usd_l2); p['san10']=p.sanit_basic_pct/10; p['wat10']=p.water_basic_pct/10; p['uhc10']=p.uhc/10
X=['ext10_l2','log_ghed_l2','log_ldi','uhc10','san10','wat10']
L={'ext10_l2':'External share of CHE (per 10 pp, lag 2)','log_ghed_l2':'Domestic govt health spending pc (log, lag 2)','log_ldi':'Income per capita (log LDI)','uhc10':'UHC index (per 10 points)','san10':'Basic sanitation (per 10 pp)','wat10':'Basic drinking water (per 10 pp)'}
rows=[]
for outc,yv,f in [('NTDs (excl. malaria)','y_ntd',p.lmic==1),('Malaria','y_mal',(p.lmic==1)&(p.mal_endemic==1))]:
    d=p[f&p.year.between(2007,2022)].dropna(subset=X+[yv]).set_index(['iso3','year'])
    m=PanelOLS(d[yv],d[X],entity_effects=True,time_effects=True).fit(cov_type='kernel',kernel='bartlett',bandwidth=3)
    for x in X:
        b=m.params[x]; lo,hi=m.conf_int().loc[x]
        rows.append({'outcome':outc,'term':L[x],'b':b,'se':m.std_errors[x],'pct':100*(np.exp(b)-1),'pct_lo':100*(np.exp(lo)-1),'pct_hi':100*(np.exp(hi)-1),'p':m.pvalues[x],'n_obs':int(m.nobs),'N':d.index.get_level_values(0).nunique(),'r2_within':m.rsquared_within})
r=pd.DataFrame(rows); r.to_csv('results/preferred_model_full.csv',index=False); print(r.round(3).to_string())
