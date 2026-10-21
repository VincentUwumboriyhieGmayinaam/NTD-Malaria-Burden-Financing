"""Headline between- vs within-country decomposition (Mundlak CRE, with year effects)."""
import pandas as pd, numpy as np, warnings, statsmodels.api as sm
from linearmodels.panel import RandomEffects, BetweenOLS
warnings.filterwarnings('ignore')
p=pd.read_csv('data/processed/panel_2005_2023.csv')
p['log_ldi']=np.log(p.ldi); p['log_ext_pc_l2']=np.log1p(p.ext_pc_usd_l2); p['ext10_l2']=p.ext_pct_che_l2/10
p['log_ghed_l2']=np.log(p.ghed_pc_usd_l2); p['san10']=p.sanit_basic_pct/10; p['wat10']=p.water_basic_pct/10; p['uhc10']=p.uhc/10
p=p[(p.year>=2007)&(p.year<=2022)&(p.lmic==1)]
rows=[]
for outc,yv,end in [('NTDs (excl. malaria)','y_ntd',False),('Malaria','y_mal',True)]:
  for spec,x in [('Share (per 10 pp)','ext10_l2'),('Per capita (log)','log_ext_pc_l2')]:
    X=[x,'log_ghed_l2','log_ldi','uhc10','san10','wat10']
    d=p[p.mal_endemic==1] if end else p
    d=d.dropna(subset=X+[yv]).set_index(['iso3','year'])
    mu=d.groupby(level=0)[X].transform('mean').add_suffix('_bar')
    yr=pd.get_dummies(d.index.get_level_values(1),prefix='y',drop_first=True,dtype=float); yr.index=d.index
    Xm=sm.add_constant(pd.concat([d[X],mu,yr],axis=1))
    m=RandomEffects(d[yv],Xm).fit(cov_type='clustered',cluster_entity=True)
    b_w=m.params[x]; b_c=m.params[x+'_bar']; V=m.cov
    b_b=b_w+b_c; se_b=np.sqrt(V.loc[x,x]+V.loc[x+'_bar',x+'_bar']+2*V.loc[x,x+'_bar'])
    for comp,b,se in [('Within-country',b_w,m.std_errors[x]),('Between-country',b_b,se_b),('Difference (contextual)',b_c,m.std_errors[x+'_bar'])]:
      from scipy.stats import norm
      rows.append(dict(outcome=outc,exposure=spec,component=comp,beta=b,se=se,pct=100*(np.exp(b)-1),lo=100*(np.exp(b-1.96*se)-1),hi=100*(np.exp(b+1.96*se)-1),p=2*norm.sf(abs(b/se)),n=len(d),countries=d.index.get_level_values(0).nunique()))
out=pd.DataFrame(rows); out.to_csv('results/rev_between_within.csv',index=False); print(out.round(3).to_string())
