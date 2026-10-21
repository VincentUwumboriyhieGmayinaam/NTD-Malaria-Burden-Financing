"""Figure 1. Geography of NTD and malaria burden, 2023 (choropleth + super-region summary)."""
import pandas as pd, numpy as np, geopandas as gpd, matplotlib.pyplot as plt, warnings
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Rectangle
import vizstyle as V; warnings.filterwarnings('ignore'); V.setup()
cs=pd.read_csv('data/processed/analysis_country_2023.csv')
ne=gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson'); ne['iso3']=np.where(ne.ISO_A3=='-99',ne.ADM0_A3,ne.ISO_A3)
ne.loc[ne.ADMIN=='France','iso3']='FRA'; ne.loc[ne.ADMIN=='Norway','iso3']='NOR'
ne=ne[ne.ADMIN!='Antarctica']
world=ne[['iso3','geometry']].dissolve('iso3').reset_index().merge(cs,on='iso3',how='left').to_crs('EPSG:8857')
srb=world.dropna(subset=['super_region_name']).dissolve('super_region_name').reset_index()
t1=pd.read_csv('results/table1_superregion_burden.csv',index_col=0)
SHORT={'Sub-Saharan Africa':'Sub-Saharan Africa','South Asia':'South Asia','Southeast Asia, East Asia, and Oceania':'SE Asia, E Asia & Oceania',
'Latin America and Caribbean':'Latin America & Caribbean','North Africa and Middle East':'N Africa & Middle East','Central Europe, Eastern Europe, and Central Asia':'C Europe, E Europe & C Asia','High-income':'High-income'}
specs=[('A','NTDs excluding malaria','daly_asr_ntd_excl_malaria',[0,25,50,100,250,500,1000,1e9],['<25','25–49','50–99','100–249','250–499','500–999','≥1000'],V.BLUE_RAMP,'asr_ntd_2023'),
       ('B','Malaria','daly_asr_malaria',[1,10,100,500,1000,2500,5000,1e9],['1–9','10–99','100–499','500–999','1k–2·5k','2·5k–5k','≥5k'],V.ORANGE_RAMP,'asr_mal_2023')]
fig=plt.figure(figsize=(V.W2,V.W2*1.02))
gs=fig.add_gridspec(4,2,width_ratios=[3.3,0.9],height_ratios=[1,0.09,1,0.09],hspace=0.18,wspace=0.40,left=0.01,right=0.985,top=0.965,bottom=0.03)
for r,(L,title,col,br,lab,ramp,trcol) in enumerate(specs):
    ax=fig.add_subplot(gs[2*r,0]); ax.set_axis_off()
    cmap=ListedColormap(ramp); norm=BoundaryNorm(br,cmap.N)
    world[world[col].isna()].plot(ax=ax,color=V.NODATA,edgecolor='white',linewidth=0.15,hatch='/////')
    if r==1:
        world[(world[col]<1)].plot(ax=ax,color=V.NEUTRAL,edgecolor='white',linewidth=0.15)
        world[world[col]>=1].plot(ax=ax,column=col,cmap=cmap,norm=norm,edgecolor='white',linewidth=0.15)
    else:
        world[world[col].notna()].plot(ax=ax,column=col,cmap=cmap,norm=norm,edgecolor='white',linewidth=0.15)
    srb.boundary.plot(ax=ax,color=V.INK,linewidth=0.45)
    ax.set_xlim(-1.32e7,1.62e7); ax.set_ylim(-6.8e6,8.5e6)
    V.panel(ax,L,f'{title}: age-standardised DALY rate per 100 000, 2023',y=1.0)
    # stepped legend
    lg=fig.add_subplot(gs[2*r+1,0]); lg.set_axis_off(); lg.set_xlim(0,1); lg.set_ylim(0,1)
    x0,wd=0.13,0.098
    if r==1:
        lg.add_patch(Rectangle((x0-0.11,0.45),wd*0.9,0.35,color=V.NEUTRAL)); lg.text(x0-0.11+wd*0.45,0.25,'<1',ha='center',va='top',fontsize=6,color=V.INK2)
    for i,(c,t) in enumerate(zip(ramp,lab)):
        lg.add_patch(Rectangle((x0+i*wd,0.45),wd-0.004,0.35,color=c)); lg.text(x0+i*wd+wd/2,0.25,t,ha='center',va='top',fontsize=6,color=V.INK2)
    xn=x0+len(ramp)*wd+0.04
    lg.add_patch(Rectangle((xn,0.45),wd*0.6,0.35,facecolor=V.NODATA,hatch='/////',edgecolor='white',linewidth=0)); lg.text(xn+wd*0.3,0.25,'No data',ha='center',va='top',fontsize=6,color=V.INK2)
    lg.plot([xn+wd*0.9,xn+wd*1.3],[0.62,0.62],color=V.INK,lw=0.6); lg.text(xn+wd*1.38,0.62,'Super-region boundary',va='center',fontsize=6,color=V.INK2)
    # super-region summary bars
    bx=fig.add_subplot(gs[2*r,1]); order=t1[trcol].sort_values()
    yy=np.arange(len(order)); bx.barh(yy,order.values,height=0.55,color=ramp[4],edgecolor='none')
    for y,v in zip(yy,order.values): bx.text(v+order.max()*0.02,y,f'{v:,.0f}',va='center',fontsize=6,color=V.INK)
    bx.set_yticks(yy); bx.set_yticklabels([SHORT[s] for s in order.index],fontsize=6.2); bx.tick_params(axis='y',length=0)
    bx.set_xlim(0,order.max()*1.32); bx.spines['left'].set_visible(False); bx.xaxis.grid(True); bx.set_axisbelow(True)
    bx.set_xlabel('Super-region rate',fontsize=6.2); bx.tick_params(axis='x',labelsize=6)
    bx.xaxis.set_major_locator(plt.MaxNLocator(3))
V.save(fig,'Figure2_burden_maps')
