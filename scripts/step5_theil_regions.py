"""Nested Theil T decomposition: between super-regions, between GBD regions within super-regions, within regions."""
import sys; sys.path.insert(0,'scripts'); from gbd_regions import ISO2REG
import pandas as pd, numpy as np
c=pd.read_csv('results/rev_country_1990_2010_2023.csv'); c['reg']=c.iso3.map(ISO2REG)
def T_of(d):
    s=d.w/d.w.sum(); mu=(s*d.y).sum(); return (s*(d.y/mu)*np.log(d.y/mu)).sum(), mu
rows=[]
for yr in [1990,2010,2023]:
  for o,nm in [('ntd','NTDs (excl. malaria)'),('mal','Malaria')]:
    d=c[c.year==yr][[o,'pop','super_region_name','reg']].rename(columns={o:'y','pop':'w'}).dropna(); d=d[d.y>0]
    T,mu=T_of(d); W=d.w.sum()
    g1=d.groupby('super_region_name').apply(lambda x: pd.Series({'s':x.w.sum()/W,'mu':(x.w*x.y).sum()/x.w.sum()}))
    Tb1=(g1.s*(g1.mu/mu)*np.log(g1.mu/mu)).sum()
    g2=d.groupby('reg').apply(lambda x: pd.Series({'s':x.w.sum()/W,'mu':(x.w*x.y).sum()/x.w.sum()}))
    Tb12=(g2.s*(g2.mu/mu)*np.log(g2.mu/mu)).sum()
    rows.append(dict(outcome=nm,year=yr,n=len(d),Theil=T,between_superregion_pct=100*Tb1/T,between_region_within_sr_pct=100*(Tb12-Tb1)/T,within_region_pct=100*(T-Tb12)/T))
o=pd.DataFrame(rows); o.to_csv('results/rev_theil_nested.csv',index=False); print(o.round(2).to_string())
