"""Figure 6. Does donor financing track NTD/malaria burden? Estimator comparison (A), out-of-sample model performance (B),
and spatially varying association from MGWR (C)."""
import pandas as pd, numpy as np, geopandas as gpd, matplotlib.pyplot as plt, json, warnings
from matplotlib.lines import Line2D
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap
import vizstyle as V; warnings.filterwarnings('ignore'); V.setup()
mc=pd.read_csv('results/model_comparison_external_share.csv'); ml=pd.read_csv('results/ml_model_comparison.csv'); gw=json.load(open('results/gwr_summary.json'))
loc=pd.read_csv('results/mgwr_local_coefficients.csv')
fig=plt.figure(figsize=(V.W2,V.W2*0.95))
gs=fig.add_gridspec(2,2,height_ratios=[1.05,0.9],width_ratios=[1.2,1],hspace=0.42,wspace=0.42,left=0.25,right=0.985,top=0.91,bottom=0.04)
# ---- A forest
ax=fig.add_subplot(gs[0,0])
order=[('Between-country (2023 cross-section)','OLS + super-region FE'),('Between-country (2023 cross-section)','Spatial error model'),
       ('Within-country panel (2007–22)','Pooled OLS'),('Within-country panel (2007–22)','Random effects'),('Within-country panel (2007–22)','Mundlak CRE'),
       ('Within-country panel (2007–22)','Two-way FE (cluster)'),('Within-country panel (2007–22)','Two-way FE (Driscoll–Kraay)'),('Within-country panel (2007–22)','First difference'),
       ('Within-country panel (2007–22)','FE + country trends'),('Spatial panel (2007–22)','Spatial lag FE (SAR)'),('Spatial panel (2007–22)','Spatial error FE (SEM)')]
ypos=[]; y=0; heads=[]
for i,(f,m) in enumerate(order):
    if i==0 or order[i-1][0]!=f: y-=0.9; heads.append((y,f)); y-=1
    else: y-=1
    ypos.append(y)
for (f,m),yy in zip(order,ypos):
    for outc,c,off in [('NTDs (excl. malaria)',V.BLUE,0.17),('Malaria',V.ORANGE,-0.17)]:
        r=mc[(mc.outcome==outc)&(mc.family==f)&(mc.model==m)].iloc[0]
        pref=m=='Two-way FE (Driscoll–Kraay)'
        ax.plot([max(r.pct_lo,-45),min(r.pct_hi,45)],[yy+off]*2,color=c,lw=1.6 if pref else 1.1)
        ax.scatter(r.pct,yy+off,s=26 if pref else 16,color=c if pref else 'white',edgecolor=c,linewidth=1.1,zorder=3,marker='D' if pref else 'o')
        if r.pct_hi>45: ax.annotate('',xy=(45,yy+off),xytext=(40,yy+off),arrowprops=dict(arrowstyle='->',color=c,lw=0.9))
    ax.text(-47.5,yy,m+('  (preferred)' if m=='Two-way FE (Driscoll–Kraay)' else ''),ha='right',va='center',fontsize=6.1,fontweight='bold' if m=='Two-way FE (Driscoll–Kraay)' else 'normal',color=V.INK)
for yy,f in heads: ax.text(-47.5,yy,f,ha='right',va='center',fontsize=6.2,fontweight='bold',color=V.INK2,style='italic')
ax.axvline(0,color=V.INK2,lw=0.7); ax.set_xlim(-45,45); ax.set_yticks([]); ax.spines['left'].set_visible(False)
ax.xaxis.grid(True); ax.set_axisbelow(True); ax.set_ylim(min(ypos)-0.7,0.2)
ax.set_xlabel('% change in age-standardised DALY rate per +10 percentage-point external share\n(95% CI; exposure lagged 2 years in panel models)',fontsize=6.2)
ax.legend([Line2D([],[],color=V.BLUE,marker='o',markerfacecolor='white',lw=1.1,markersize=4),Line2D([],[],color=V.ORANGE,marker='o',markerfacecolor='white',lw=1.1,markersize=4),
           Line2D([],[],color=V.INK2,marker='D',lw=1.6,markersize=4)],['NTDs excl. malaria (LMICs)','Malaria (endemic LMICs)','Preferred estimator'],loc='lower left',bbox_to_anchor=(-0.62,1.07),ncol=3,fontsize=6)
V.panel(ax,'A','Association with donor financing: between vs within countries',x=-0.62,y=1.02)
# ---- B ML performance
bx=fig.add_subplot(gs[0,1])
CV=['Random 5-fold (optimistic)','Leave-country-out (grouped 5-fold)','Spatial block: leave-one-super-region-out','Temporal: train ≤2017, test 2018–2023']
CVL=['Random 5-fold\n(leaks country)','Leave-country-out','Spatial block\n(super-region out)','Temporal\n(≤2017 → 2018–23)']
MS=[('Elastic net','s',V.INK2),('Random forest','^',V.AQUA),('LightGBM','o',V.BLUE),('Two-way FE linear (country FE + linear year)','D',V.ORANGE)]
for i,cv in enumerate(CV):
    for j,(m,mk,c) in enumerate(MS):
        r=ml[(ml.cv==cv)&(ml.model==m)]
        if len(r): bx.scatter(r.RMSE_log,len(CV)-1-i+(j-1.5)*0.14,marker=mk,s=22,color=c,edgecolor='white',linewidth=0.6,zorder=3)
bx.set_yticks(range(len(CV))); bx.set_yticklabels(CVL[::-1],fontsize=6.1); bx.tick_params(axis='y',length=0); bx.spines['left'].set_visible(False)
bx.set_xlim(0,0.75); bx.xaxis.grid(True); bx.set_axisbelow(True); bx.set_xlabel('Out-of-sample RMSE, log NTD DALY rate (lower = better)',fontsize=6.2)
bx.legend([Line2D([],[],ls='',marker=mk,color=c,markersize=4) for _,mk,c in MS],['Elastic net','Random forest','LightGBM','Two-way FE\n(temporal only)'],loc='lower left',bbox_to_anchor=(-0.05,1.07),ncol=4,fontsize=5.8,handletextpad=0.2,columnspacing=0.8)
V.panel(bx,'B','Predictive validation of ML vs panel models',x=-0.42,y=1.02)
# ---- C MGWR map
cx=fig.add_subplot(gs[1,:]); cx.set_axis_off()
ne=gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson'); ne['iso3']=np.where(ne.ISO_A3=='-99',ne.ADM0_A3,ne.ISO_A3)
ne.loc[ne.ADMIN=='France','iso3']='FRA'; ne.loc[ne.ADMIN=='Norway','iso3']='NOR'; ne=ne[ne.ADMIN!='Antarctica'].to_crs('ESRI:54030')
w=ne[['iso3','geometry']].dissolve('iso3').reset_index().merge(loc,on='iso3',how='left')
w[w.b_ext.isna()].plot(ax=cx,color='white',edgecolor=V.AXIS,linewidth=0.2)
cmap=LinearSegmentedColormap.from_list('d',[V.BLUE_RAMP[5],V.BLUE_RAMP[2],V.NEUTRAL,V.ORANGE_RAMP[2],V.ORANGE_RAMP[5]])
norm=TwoSlopeNorm(0,-0.4,0.55)
w[w.b_ext.notna()&(w.sig_ext==0)].plot(ax=cx,color=V.NEUTRAL,edgecolor='white',linewidth=0.15)
w[w.sig_ext==1].plot(ax=cx,column='b_ext',cmap=cmap,norm=norm,edgecolor='white',linewidth=0.15)
cx.set_xlim(-1.15e7,1.62e7); cx.set_ylim(-4.5e6,6.2e6); cx.set_position([0.25,0.03,0.74,0.40])
cax=fig.add_axes([0.03,0.355,0.17,0.014]); sm_=plt.cm.ScalarMappable(norm=norm,cmap=cmap); cb=fig.colorbar(sm_,cax=cax,orientation='horizontal'); cb.outline.set_visible(False)
cb.set_ticks([-0.4,0,0.5]); cb.set_ticklabels(['−0·4','0','0·5']); cb.ax.tick_params(labelsize=5.8,length=2)
cb.set_label('Local standardised coefficient\n(external share → NTD rate)',fontsize=5.9,color=V.INK2)
txt=(f"MGWR vs OLS: AICc {gw['MGWR_AICc']:.0f} vs {gw['OLS_AICc']:.0f}; R² {gw['MGWR_R2']:.2f} vs {gw['OLS_R2']:.2f}\n"
     f"Bandwidths (of {gw['n']} countries):\nexternal share {gw['MGWR_bw']['ext']:.0f}, UHC {gw['MGWR_bw']['uhc']:.0f}, sanitation {gw['MGWR_bw']['sanit_basic_pct']:.0f}\n"
     f"External share significant in {gw['MGWR_coef_summary']['ext']['pct_sig']:.0f}% of countries; grey = not significant (corrected t-test)").replace('.','·')
fig.text(0.03,0.27,txt.replace('; ','\n').replace(', UHC','\nUHC').replace('; grey','\ngrey'),fontsize=5.8,color=V.INK2,va='top',linespacing=1.35)
fig.text(0.03,0.43,'C.',fontsize=9,fontweight='bold'); fig.text(0.055,0.43,'Spatially varying association (multiscale GWR, LMICs, 2023)',fontsize=7.5,fontweight='bold')
V.save(fig,'Figure7_model_comparison')
