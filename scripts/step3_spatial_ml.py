"""Step 3b: spatial panel FE (SAR, SEM), MGWR-free GWR cross-section, and ML model comparison with
random / grouped-country / spatial-block (leave-super-region-out) / temporal cross-validation."""
import pandas as pd, numpy as np, geopandas as gpd, json, warnings
from libpysal.weights import KNN
from spreg import Panel_FE_Lag, Panel_FE_Error
from sklearn.model_selection import KFold, GroupKFold, LeaveOneGroupOut
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNetCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
import lightgbm as lgb, shap
warnings.filterwarnings('ignore'); rng=np.random.default_rng(7); OUT={}
p=pd.read_csv('data/processed/panel_2005_2023.csv')
p['log_ldi']=np.log(p.ldi); p['log_ext_pc_l2']=np.log1p(p.ext_pc_usd_l2); p['ext10_l2']=p.ext_pct_che_l2/10
p['log_ghed_l2']=np.log(p.ghed_pc_usd_l2); p['san10']=p.sanit_basic_pct/10; p['wat10']=p.water_basic_pct/10; p['uhc10']=p.uhc/10
X=['ext10_l2','log_ghed_l2','log_ldi','uhc10','san10','wat10']
# ---------- spatial panel FE (balanced LMIC panel 2007-2022) ----------
ne=gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson'); ne['iso3']=np.where(ne.ISO_A3=='-99',ne.ADM0_A3,ne.ISO_A3)
ne.loc[ne.ADMIN=='France','iso3']='FRA'; ne.loc[ne.ADMIN=='Norway','iso3']='NOR'
cent=ne[['iso3','geometry']].dissolve('iso3').reset_index().to_crs('ESRI:54030'); cent['geometry']=cent.representative_point()
cent['lon']=cent.geometry.x/1e6; cent['lat']=cent.geometry.y/1e6
sp_rows=[]
for outc,yv,flt in [('NTDs (excl. malaria)','y_ntd',p.lmic==1),('Malaria','y_mal',(p.lmic==1)&(p.mal_endemic==1))]:
    d=p[flt&p.year.between(2007,2022)].dropna(subset=X+[yv])
    cnt=d.groupby('iso3').year.nunique(); keep=cnt[cnt==16].index.intersection(cent.iso3)
    d=d[d.iso3.isin(keep)].sort_values(['iso3','year'])
    c=cent.set_index('iso3').loc[sorted(keep)].reset_index(); w=KNN.from_dataframe(c,k=6); w.transform='r'
    Y=d.pivot(index='iso3',columns='year',values=yv).loc[c.iso3].values.reshape(-1,1,order='F')   # time-major: units vary fastest
    XX=np.column_stack([d.pivot(index='iso3',columns='year',values=v).loc[c.iso3].values.reshape(-1,order='F') for v in X])
    for nm,est in [('Spatial lag FE (SAR)',Panel_FE_Lag),('Spatial error FE (SEM)',Panel_FE_Error)]:
        m=est(Y,XX,w,name_x=X,name_y=yv)
        b=m.betas.flatten(); se=np.sqrt(np.diag(m.vm)); k=0
        sp_param=float(m.rho if hasattr(m,'rho') else m.lam)
        sp_rows.append({'outcome':outc,'model':nm,'term':X[0],'beta':b[k],'se':se[k],'lo':b[k]-1.96*se[k],'hi':b[k]+1.96*se[k],
                        'p':float(2*(1-__import__('scipy').stats.norm.cdf(abs(b[k]/se[k])))),'spatial_param':sp_param,'n_countries':len(keep),'T':16,'logL':float(m.logll)})
sp=pd.DataFrame(sp_rows); sp.to_csv('results/spatial_panel_models.csv',index=False); print(sp.round(4).to_string())

# ---------- ML comparison (NTDs, LMIC, 2007-2023) ----------
d=p[(p.lmic==1)&p.year.between(2007,2023)].merge(cent[['iso3','lon','lat']],on='iso3',how='left')
F=['ext10_l2','log_ext_pc_l2','log_ghed_l2','log_ldi','uhc10','san10','wat10','rural_pct','oop_pct_che','sdi','year','lon','lat']
d=d.dropna(subset=F+['y_ntd']).reset_index(drop=True); y=d.y_ntd.values; Xf=d[F].values
models={'Elastic net':lambda: make_pipeline(StandardScaler(),ElasticNetCV(l1_ratio=[.1,.5,.9],cv=5)),
        'Random forest':lambda: RandomForestRegressor(n_estimators=500,min_samples_leaf=5,max_features=0.5,n_jobs=-1,random_state=1),
        'LightGBM':lambda: lgb.LGBMRegressor(n_estimators=600,learning_rate=0.03,num_leaves=15,min_child_samples=20,subsample=0.8,subsample_freq=1,colsample_bytree=0.8,verbose=-1,random_state=1)}
schemes={'Random 5-fold (optimistic)':list(KFold(5,shuffle=True,random_state=1).split(Xf)),
         'Leave-country-out (grouped 5-fold)':list(GroupKFold(5).split(Xf,y,d.iso3)),
         'Spatial block: leave-one-super-region-out':list(LeaveOneGroupOut().split(Xf,y,d.super_region_name)),
         'Temporal: train ≤2017, test 2018–2023':[(np.where(d.year<=2017)[0],np.where(d.year>=2018)[0])]}
res=[]
for sname,folds in schemes.items():
    for mname,mk in models.items():
        pred=np.full(len(y),np.nan)
        for tr,te in folds: m=mk(); m.fit(Xf[tr],y[tr]); pred[te]=m.predict(Xf[te])
        ok=~np.isnan(pred); r=y[ok]-pred[ok]
        res.append({'cv':sname,'model':mname,'RMSE_log':float(np.sqrt(np.mean(r**2))),'MAE_log':float(np.mean(abs(r))),'R2':float(1-np.sum(r**2)/np.sum((y[ok]-y[ok].mean())**2))})
    if sname.startswith('Temporal'):   # FE linear benchmark can forecast within known countries
        tr,te=folds[0]; dd=d.copy(); Xl=['ext10_l2','log_ghed_l2','log_ldi','uhc10','san10','wat10']
        import statsmodels.formula.api as smf
        fm=smf.ols('y_ntd ~ '+'+'.join(Xl)+' + C(iso3) + year',dd.iloc[tr]).fit()
        te_=dd.iloc[te]; te_=te_[te_.iso3.isin(dd.iloc[tr].iso3)]; pr=fm.predict(te_); r=te_.y_ntd-pr
        res.append({'cv':sname,'model':'Two-way FE linear (country FE + linear year)','RMSE_log':float(np.sqrt(np.mean(r**2))),'MAE_log':float(np.mean(abs(r))),'R2':float(1-np.sum(r**2)/np.sum((te_.y_ntd-te_.y_ntd.mean())**2))})
ml=pd.DataFrame(res); ml.to_csv('results/ml_model_comparison.csv',index=False); print(ml.round(3).to_string())
# interpretation: LightGBM SHAP on full data + permutation importance under grouped CV
m=models['LightGBM'](); m.fit(Xf,y)
sv=shap.TreeExplainer(m).shap_values(Xf)
imp=pd.DataFrame({'feature':F,'mean_abs_shap':np.abs(sv).mean(0)}).sort_values('mean_abs_shap',ascending=False); imp.to_csv('results/ml_shap_importance.csv',index=False)
pd.DataFrame({'ext_pct_che_l2':d.ext10_l2*10,'shap_ext':sv[:,0],'super_region':d.super_region_name}).to_csv('results/ml_shap_external_share.csv',index=False)
print(imp.round(3).to_string())
