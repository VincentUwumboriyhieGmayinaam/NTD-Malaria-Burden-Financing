"""Two-way FE spatial panel (country FE via spreg within-transformation + year FE via cross-sectional demeaning of the balanced panel),
with LeSage-Pace direct/indirect/total effects for the SAR model (simulated CIs from the asymptotic distribution of (beta, rho))."""
import pandas as pd, numpy as np, geopandas as gpd, warnings
from libpysal.weights import KNN
from spreg import Panel_FE_Lag, Panel_FE_Error
from scipy import stats
warnings.filterwarnings('ignore'); rng=np.random.default_rng(7)
p=pd.read_csv('data/processed/panel_2005_2023.csv')
p['log_ldi']=np.log(p.ldi); p['ext10_l2']=p.ext_pct_che_l2/10; p['log_ghed_l2']=np.log(p.ghed_pc_usd_l2)
p['san10']=p.sanit_basic_pct/10; p['wat10']=p.water_basic_pct/10; p['uhc10']=p.uhc/10
X=['ext10_l2','log_ghed_l2','log_ldi','uhc10','san10','wat10']
ne=gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson'); ne['iso3']=np.where(ne.ISO_A3=='-99',ne.ADM0_A3,ne.ISO_A3)
ne.loc[ne.ADMIN=='France','iso3']='FRA'; ne.loc[ne.ADMIN=='Norway','iso3']='NOR'
cent=ne[['iso3','geometry']].dissolve('iso3').reset_index().to_crs('ESRI:54030'); cent['geometry']=cent.representative_point()
rows=[]
for outc,yv,flt in [('NTDs (excl. malaria)','y_ntd',p.lmic==1),('Malaria','y_mal',(p.lmic==1)&(p.mal_endemic==1))]:
    d=p[flt&p.year.between(2007,2022)].dropna(subset=X+[yv])
    cnt=d.groupby('iso3').year.nunique(); keep=cnt[cnt==16].index.intersection(cent.iso3)
    d=d[d.iso3.isin(keep)].sort_values(['iso3','year']).copy()
    for v in X+[yv]: d[v]=d[v]-d.groupby('year')[v].transform('mean')   # year FE (balanced panel)
    c=cent.set_index('iso3').loc[sorted(keep)].reset_index(); w=KNN.from_dataframe(c,k=6); w.transform='r'
    Y=d.pivot(index='iso3',columns='year',values=yv).loc[c.iso3].values.reshape(-1,1,order='F')
    XX=np.column_stack([d.pivot(index='iso3',columns='year',values=v).loc[c.iso3].values.reshape(-1,order='F') for v in X])
    W=w.full()[0]; n=len(keep)
    for nm,est in [('Spatial lag two-way FE (SAR)',Panel_FE_Lag),('Spatial error two-way FE (SEM)',Panel_FE_Error)]:
        m=est(Y,XX,w,name_x=X,name_y=yv); b=m.betas.flatten(); vm=m.vm; se=np.sqrt(np.diag(vm))
        sp=float(m.rho if hasattr(m,'rho') else m.lam)
        pc=lambda x:(np.exp(x)-1)*100
        r=dict(outcome=outc,model=nm,effect='coefficient',beta=b[0],se=se[0],pct=pc(b[0]),lo=pc(b[0]-1.96*se[0]),hi=pc(b[0]+1.96*se[0]),
               p=2*(1-stats.norm.cdf(abs(b[0]/se[0]))),spatial_param=sp,n_countries=n,T=16)
        rows.append(r)
        if 'SAR' in nm:   # effects: S = (I - rho W)^-1 beta ; direct = mean diag, total = mean row sum
            # draws of (beta_ext, rho): vm order follows betas (X..., rho last)
            idx=[0,len(b)-1]; mu=b[idx]; V=vm[np.ix_(idx,idx)]
            dr=rng.multivariate_normal(mu,V,2000); ev=np.linalg.eigvals(W).real
            eff={'direct':[],'indirect':[],'total':[]}
            for be,rh in dr:
                dg=np.mean(1/(1-rh*ev))   # mean diag of (I-rhoW)^-1 via eigenvalues
                tot=1/(1-rh); eff['direct'].append(be*dg); eff['total'].append(be*tot); eff['indirect'].append(be*(tot-dg))
            for k,v in eff.items():
                v=np.array(v); rows.append(dict(outcome=outc,model=nm,effect=k,beta=np.median(v),se=v.std(),pct=pc(np.median(v)),
                    lo=pc(np.percentile(v,2.5)),hi=pc(np.percentile(v,97.5)),p=2*min((v>0).mean(),(v<0).mean()),spatial_param=sp,n_countries=n,T=16))
out=pd.DataFrame(rows); out.to_csv('results/spatial_panel_twoway.csv',index=False); print(out.round(3).to_string())
