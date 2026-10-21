"""Step 6: harmonise headline outputs after the revision analyses (run after step5_* and before tables/figures).
- Mundlak CRE row in the estimator comparison = within-country component of the CRE model with year effects (step5_mundlak_between_within.py).
- 2023 inequality metrics = GBD-population, all-country estimates (step5_revisions.py), the primary inequality specification."""
import pandas as pd, json
mc=pd.read_csv('results/model_comparison_external_share.csv'); bw=pd.read_csv('results/rev_between_within.csv')
for o in ['NTDs (excl. malaria)','Malaria']:
    w=bw[(bw.outcome==o)&(bw.exposure=='Share (per 10 pp)')&(bw.component=='Within-country')].iloc[0]
    i=(mc.outcome==o)&mc.model.str.startswith('Mundlak CRE')
    mc.loc[i,['beta','lo','hi','p','pct','pct_lo','pct_hi']]=[w.beta,w.beta-1.96*w.se,w.beta+1.96*w.se,w.p,w.pct,w.lo,w.hi]; mc.loc[i,'model']='Mundlak CRE (within)'
mc.to_csv('results/model_comparison_external_share.csv',index=False)
iq=pd.read_csv('results/rev_inequality_over_time.csv'); iq=iq[iq.year==2023].set_index('outcome')
im=pd.read_csv('results/inequality_metrics.csv',index_col=0); K=json.load(open('results/key_numbers.json'))
for o in im.index:
    r=iq.loc[o]; v=dict(CI=r.CI,lo=r.CI_lo,hi=r.CI_hi,Theil=r.Theil,between_pct=r.between_pct,within_pct=r.within_pct)
    for k,x in v.items(): im.loc[o,k]=x
    K['inequality'][o].update({k:float(x) for k,x in v.items()})
im.to_csv('results/inequality_metrics.csv'); json.dump(K,open('results/key_numbers.json','w'),indent=1); print('harmonised')
