"""Step 3c: GWR / MGWR (2023 cross-section, LMICs) to test spatially varying associations."""
import pandas as pd, numpy as np, geopandas as gpd, json, warnings
from mgwr.gwr import GWR, MGWR
from mgwr.sel_bw import Sel_BW
import statsmodels.api as sm
warnings.filterwarnings('ignore')
p=pd.read_csv('data/processed/panel_2005_2023.csv'); d=p[(p.year==2023)&(p.lmic==1)].copy()
ext=p[(p.year.between(2019,2022))].groupby('iso3').ext_pct_che.mean(); d['ext']=d.iso3.map(ext)
d['log_ldi']=np.log(d.ldi)
ne=gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson'); ne['iso3']=np.where(ne.ISO_A3=='-99',ne.ADM0_A3,ne.ISO_A3)
ne.loc[ne.ADMIN=='France','iso3']='FRA'; ne.loc[ne.ADMIN=='Norway','iso3']='NOR'
c=ne[['iso3','geometry']].dissolve('iso3').reset_index().to_crs('ESRI:54030'); c['geometry']=c.representative_point(); c['x']=c.geometry.x/1e3; c['y']=c.geometry.y/1e3
X=['ext','uhc','log_ldi','sanit_basic_pct']
d=d.merge(c[['iso3','x','y']],on='iso3').dropna(subset=X+['y_ntd'])
Z=(d[X]-d[X].mean())/d[X].std(); yy=((d.y_ntd-d.y_ntd.mean())/d.y_ntd.std()).values.reshape(-1,1)
coords=list(zip(d.x,d.y))
ols=sm.OLS(yy,sm.add_constant(Z.values)).fit()
bw=Sel_BW(coords,yy,Z.values,kernel='bisquare',fixed=False).search(criterion='AICc'); g=GWR(coords,yy,Z.values,bw,kernel='bisquare',fixed=False).fit()
sel=Sel_BW(coords,yy,Z.values,multi=True,kernel='bisquare',fixed=False); sel.search(criterion='AICc'); mg=MGWR(coords,yy,Z.values,sel,kernel='bisquare',fixed=False).fit()
names=['Intercept']+X
out={'n':len(d),'OLS_AICc':float(ols.aic+2*(ols.df_model+2)*(ols.df_model+3)/(len(d)-ols.df_model-3)),'OLS_R2':float(ols.rsquared),
     'GWR_bw':float(bw),'GWR_AICc':float(g.aicc),'GWR_R2':float(g.R2),'MGWR_AICc':float(mg.aicc),'MGWR_R2':float(mg.R2),'MGWR_bw':dict(zip(names,map(float,sel.bw[0])))}
tv=mg.filter_tvals()   # multiple-testing corrected t-values
loc=pd.DataFrame(mg.params,columns=[f'b_{n}' for n in names]); 
for i,n in enumerate(names): loc[f'sig_{n}']=(tv[:,i]!=0).astype(int)
loc[['iso3','location_name','super_region_name']]=d[['iso3','location_name','super_region_name']].values
loc.to_csv('results/mgwr_local_coefficients.csv',index=False)
out['MGWR_coef_summary']={n:{'min':float(loc[f'b_{n}'].min()),'median':float(loc[f'b_{n}'].median()),'max':float(loc[f'b_{n}'].max()),'pct_sig':float(100*loc[f'sig_{n}'].mean())} for n in names}
json.dump(out,open('results/gwr_summary.json','w'),indent=1); print(json.dumps(out,indent=1))
