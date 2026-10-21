"""Figure 4. Spatial clustering (LISA) and socioeconomic inequality of NTD and malaria burden."""
import pandas as pd, numpy as np, geopandas as gpd, matplotlib.pyplot as plt, json, warnings
from matplotlib.patches import Patch
import vizstyle as V; warnings.filterwarnings('ignore'); V.setup()
lisa=gpd.read_file('results/lisa.gpkg'); K=json.load(open('results/key_numbers.json'))
ne=gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson'); ne=ne[ne.ADMIN!='Antarctica'].to_crs('EPSG:8857')
COL={'High–High':V.RED,'High–Low':V.RED_LIGHT,'Low–High':V.BLUE_LIGHT,'Low–Low':V.BLUE,'Not significant':V.NEUTRAL}
fig=plt.figure(figsize=(V.W2,V.W2*0.78))
gs=fig.add_gridspec(2,2,height_ratios=[1,0.95],hspace=0.22,wspace=0.18,left=0.02,right=0.985,top=0.94,bottom=0.08)
for k,(L,nm,col) in enumerate([('A','NTDs excluding malaria','lisa_ntd_fdr'),('B','Malaria','lisa_mal_fdr')]):
    ax=fig.add_subplot(gs[0,k]); ax.set_axis_off()
    ne.plot(ax=ax,color=V.NODATA,edgecolor='white',linewidth=0.1)
    for cat,c in COL.items(): lisa[lisa[col]==cat].plot(ax=ax,color=c,edgecolor='white',linewidth=0.12)
    ax.set_xlim(-1.32e7,1.62e7); ax.set_ylim(-6.8e6,8.5e6)
    sp=K['spatial']['ntd' if k==0 else 'mal']
    V.panel(ax,L,f'{nm}: local clusters (LISA, FDR q<0·05)',y=1.02)
    ax.text(0.0,0.30,f"Global Moran's I = {sp['I']:.2f}".replace('.','·')+"\np<0·001 (9999 permutations)",transform=ax.transAxes,fontsize=6,color=V.INK,va='bottom')
    n=lisa[col].value_counts()
    h=[Patch(color=COL[c],label=f'{c} ({n.get(c,0)})') for c in ['High–High','Low–Low','High–Low','Low–High','Not significant']]
    ax.legend(handles=h,loc='lower left',bbox_to_anchor=(-0.01,-0.06),fontsize=5.8,handlelength=1.0,handleheight=0.8,ncol=1,labelspacing=0.25)
# C concentration curves
cc=pd.read_csv('results/concentration_curves.csv'); ineq=K['inequality']
ax=fig.add_subplot(gs[1,0])
ax.plot([0,1],[0,1],color=V.AXIS,lw=0.8); 
for nm,c,lx,ly in [('NTDs (excl. malaria)',V.BLUE,0.33,0.14),('Malaria',V.ORANGE,0.33,0.22)]:
    d=cc[cc.measure==nm]; ax.plot(np.r_[0,d.cum_pop],np.r_[0,d.cum_y],color=c,lw=1.5)
    ci=ineq[nm]; num=lambda v: f'{v:.2f}'.replace('-','−').replace('.','·'); lab=f"{'NTDs excl. malaria' if nm.startswith('NTD') else 'Malaria'}: C = {num(ci['CI'])} ({num(ci['lo'])} to {num(ci['hi'])})"
    ax.text(lx,ly,lab,color=V.INK,fontsize=6,va='center')
    ax.plot([lx-0.03,lx-0.005],[ly,ly],color=c,lw=1.5)
ax.text(0.80,0.74,'Equality',rotation=45,fontsize=5.8,color=V.MUTED)
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_aspect('equal')
ax.set_xlabel('Cumulative share of population, ranked from lowest to highest SDI',fontsize=6.3); ax.set_ylabel('Cumulative share of age-standardised DALYs',fontsize=6.3)
ax.set_xticks([0,.25,.5,.75,1]); ax.set_yticks([0,.25,.5,.75,1]); fmt=plt.FuncFormatter(lambda v,_: f'{v*100:.0f}%'); ax.xaxis.set_major_formatter(fmt); ax.yaxis.set_major_formatter(fmt)
ax.grid(True); ax.set_axisbelow(True); V.panel(ax,'C','Concentration curves by Socio-demographic Index',x=-0.20,y=1.03)
# D Theil decomposition
ax=fig.add_subplot(gs[1,1])
rows=[('NTDs excl. malaria','NTDs (excl. malaria)'),('Malaria','Malaria')]
y=np.arange(len(rows))[::-1]
for yi,(lab,key) in zip(y,rows):
    b=ineq[key]['between_pct']; w=ineq[key]['within_pct']
    ax.barh(yi,b,height=0.42,color=V.BLUE,edgecolor='white',linewidth=1.2); ax.barh(yi,w,left=b,height=0.42,color=V.BLUE_RAMP[1],edgecolor='white',linewidth=1.2)
    ax.text(b/2,yi,f'{b:.0f}%',ha='center',va='center',color='white',fontsize=6.5,fontweight='bold'); ax.text(b+w/2,yi,f'{w:.0f}%',ha='center',va='center',color=V.INK,fontsize=6.5,fontweight='bold')
    ax.text(101,yi,f"Theil T = {ineq[key]['Theil']:.2f}".replace('.','·'),va='center',fontsize=6,color=V.INK2)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows]); ax.tick_params(axis='y',length=0); ax.spines['left'].set_visible(False)
ax.set_xlim(0,125); ax.set_xticks([0,25,50,75,100]); ax.set_xlabel('Share of total inequality (population-weighted Theil T)',fontsize=6.3); ax.set_ylim(-0.8,1.9)
ax.legend(handles=[Patch(color=V.BLUE,label='Between super-regions'),Patch(color=V.BLUE_RAMP[1],label='Within super-regions')],loc='upper left',bbox_to_anchor=(0,1.02),ncol=2,fontsize=6)
V.panel(ax,'D','Decomposition of between-country inequality',y=1.03)
V.save(fig,'Figure5_spatial_clusters_inequality')
