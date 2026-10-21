"""Figure 2. Cause-specific burden by GBD super-region, 2023: all-age DALY rate heatmap (log colour scale),
cells annotated where a super-region holds >=50% of that cause's global DALYs; global DALYs dot plot (log)."""
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, LinearSegmentedColormap
import vizstyle as V; V.setup()
rate=pd.read_csv('results/cause_by_superregion_rate_per100k.csv',index_col=0)
share=pd.read_csv('results/cause_by_superregion_share_of_global.csv',index_col=0)
glob=pd.read_csv('results/cause_global_dalys_2023.csv',index_col=0).iloc[:,0]
NAMES={'malaria':'Malaria','other_neglected_tropical_diseases':'Other NTDs','dengue':'Dengue','schistosomiasis':'Schistosomiasis',
'intestinal_nematode_infections':'Soil-transmitted helminths','lymphatic_filariasis':'Lymphatic filariasis','cysticercosis':'Cysticercosis',
'leishmaniasis':'Leishmaniasis','food_borne_trematodiases':'Food-borne trematodiases','onchocerciasis':'Onchocerciasis','rabies':'Rabies',
'yellow_fever':'Yellow fever','chagas_disease':'Chagas disease','trachoma':'Trachoma','cystic_echinococcosis':'Cystic echinococcosis',
'african_trypanosomiasis':'Human African trypanosomiasis','leprosy':'Leprosy','zika_virus':'Zika virus','ebola':'Ebola','guinea_worm_disease':'Guinea worm disease'}
COLS=['Sub-Saharan Africa','South Asia','Latin America and Caribbean','Southeast Asia, East Asia, and Oceania','North Africa and Middle East','Central Europe, Eastern Europe, and Central Asia','High-income']
CL=['Sub-\nSaharan\nAfrica','South\nAsia','Latin\nAmerica &\nCaribbean','SE Asia,\nE Asia &\nOceania','N Africa\n& Middle\nEast','C Europe,\nE Europe\n& C Asia','High-\nincome']
order=[c for c in glob.sort_values(ascending=False).index if c in NAMES]
R=rate.loc[order,COLS]; S=share.loc[order,COLS]; G=glob.loc[order]
cmap=LinearSegmentedColormap.from_list('b',V.BLUE_RAMP); cmap.set_bad(V.NEUTRAL)
Rm=R.mask(R<0.01)
fig=plt.figure(figsize=(V.W2,V.W2*0.72))
gs=fig.add_gridspec(1,3,width_ratios=[3.1,0.06,1.25],wspace=0.08,left=0.19,right=0.985,top=0.84,bottom=0.12)
ax=fig.add_subplot(gs[0]); cax=fig.add_axes([0.19,0.045,0.33,0.018])
norm=LogNorm(vmin=0.01,vmax=5000)
im=ax.imshow(Rm.values,aspect='auto',cmap=cmap,norm=norm,interpolation='nearest')
ax.set_xticks(range(len(COLS))); ax.set_xticklabels(CL,fontsize=6.1,linespacing=1.05); ax.xaxis.tick_top(); ax.tick_params(length=0)
ax.set_yticks(range(len(order))); ax.set_yticklabels([NAMES[c] for c in order],fontsize=6.5)
for s in ax.spines.values(): s.set_visible(False)
ax.set_xticks(np.arange(-.5,len(COLS)),minor=True); ax.set_yticks(np.arange(-.5,len(order)),minor=True)
ax.grid(which='minor',color='white',linewidth=1.2); ax.tick_params(which='minor',length=0)
ax.axhline(0.5,color=V.INK,lw=0.6)   # separate malaria from NTDs
for i,c in enumerate(order):
    for j,col in enumerate(COLS):
        sh=S.loc[c,col]
        if sh>=50:
            v=Rm.loc[c,col]; dark=(not np.isnan(v)) and v>30
            ax.text(j,i,f'{sh:.0f}%',ha='center',va='center',fontsize=6,fontweight='bold',color='white' if dark else V.INK)
cb=fig.colorbar(im,cax=cax,orientation='horizontal'); cb.outline.set_visible(False); cb.ax.minorticks_off()
cb.set_ticks([0.01,0.1,1,10,100,1000]); cb.set_ticklabels(['0·01','0·1','1','10','100','1000']); cb.ax.tick_params(labelsize=6,length=2,color=V.AXIS)
cb.set_label('All-age DALY rate per 100 000 (log scale); grey = <0·01',fontsize=6.3,color=V.INK2)
fig.text(0.19,0.955,'A.',fontsize=9,fontweight='bold'); fig.text(0.21,0.955,'Rate by cause and GBD super-region, 2023',fontsize=7.5,fontweight='bold')
fig.text(0.21,0.93,'Cell label = super-region share of that cause\'s global DALYs, shown where ≥50%',fontsize=6.3,color=V.INK2)
# B: global DALYs dot plot (log)
bx=fig.add_subplot(gs[2],sharey=ax)
y=np.arange(len(order)); bx.hlines(y,1,G.values,color=V.GRID,lw=0.8)
bx.scatter(G.values,y,s=16,color=V.BLUE,edgecolor='white',linewidth=0.8,zorder=3)
bx.scatter(G.values[:1],y[:1],s=16,color=V.ORANGE,edgecolor='white',linewidth=0.8,zorder=4)
bx.set_xscale('log'); bx.set_xlim(0.03,4e8); bx.tick_params(axis='y',which='both',labelleft=False,length=0)
bx.set_xticks([1,1e2,1e4,1e6,1e8]); bx.set_xticklabels(['1','100','10k','1M','100M'],fontsize=6)
bx.xaxis.grid(True,color=V.GRID,lw=0.5); bx.set_axisbelow(True); bx.spines['left'].set_visible(False)
for yi,v in zip(y,G.values):
    lab=f'{v/1e6:.1f}M' if v>=1e6 else (f'{v/1e3:.0f}k' if v>=1e3 else f'{v:.1f}' if v>=1 else f'{v:.2f}')
    bx.text(v*1.6,yi,lab,va='center',fontsize=5.8,color=V.INK2)
bx.set_xlabel('Global DALYs, 2023 (log scale)',fontsize=6.3)
fig.text(0.715,0.955,'B.',fontsize=9,fontweight='bold'); fig.text(0.735,0.955,'Global DALYs by cause',fontsize=7.5,fontweight='bold')
V.save(fig,'Figure3_cause_superregion_heatmap')
