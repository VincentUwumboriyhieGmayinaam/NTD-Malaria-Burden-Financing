"""Figure 7. Funding-cut scenarios: excess annual DALYs, most-affected countries, and the domestic financing gap."""
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import vizstyle as V; V.setup()
sr=pd.read_csv('results/scenario_v2_superregion.csv'); cty=pd.read_csv('results/scenario_v2_country.csv')
gap=pd.read_csv('results/scenario_financing_gap.csv'); cs=pd.read_csv('data/processed/analysis_country_2023.csv')
SC=['Mild','Reference','Severe']; SCL={'Mild':'Mild\n(5–15% cut)','Reference':'Reference\n(19–26% cut)','Severe':'Severe\n(40–60% cut)'}
SHADE={'NTDs (excl. malaria)':[V.BLUE_RAMP[2],V.BLUE_RAMP[4],V.BLUE_RAMP[6]],'Malaria':[V.ORANGE_RAMP[2],V.ORANGE_RAMP[4],V.ORANGE_RAMP[6]]}
fig=plt.figure(figsize=(V.W2,V.W2*0.80))
gs=fig.add_gridspec(2,2,height_ratios=[1,1.15],width_ratios=[1,1.15],hspace=0.55,wspace=0.42,left=0.12,right=0.975,top=0.94,bottom=0.08)
fm=lambda v: (f'{v/1e6:.2f}M' if v>=1e6 else f'{v/1e3:.0f}k').replace('.','·')
# A: global excess DALYs per scenario
for k,(outc,L,title) in enumerate([('NTDs (excl. malaria)','A','NTDs excluding malaria'),('Malaria','B','Malaria')]):
    ax=fig.add_subplot(gs[0,k]) if k==0 else fig.add_subplot(gs[0,1])
    d=sr[(sr.outcome==outc)&(sr.super_region=='All LMICs')].set_index('scenario').loc[SC]
    x=np.arange(3)
    for i,(s_,row) in enumerate(d.iterrows()):
        c=SHADE[outc][i]
        ax.plot([i-0.13]*2,[row.A_lo,row.A_hi],color=c,lw=2,solid_capstyle='round'); ax.scatter(i-0.13,row.A_excess,s=30,color=c,edgecolor='white',linewidth=1,zorder=3)
        ax.plot([i+0.13]*2,[max(row.B_lo,-3e5),row.B_hi],color=c,lw=1.2,solid_capstyle='round'); ax.scatter(i+0.13,row.B_excess,s=24,color='white',edgecolor=c,linewidth=1.2,zorder=3,marker='D')
        ax.text(i-0.2,row.A_excess,fm(row.A_excess),ha='right',va='center',fontsize=5.8,color=V.INK)
        ax.text(i,-0.13,f"{row.A_pct_2023:.1f}% of 2023\nburden".replace('.','·'),transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=5.6,color=V.INK2)
    ax.axhline(0,color=V.INK2,lw=0.6)
    if k==0: ax.legend([Line2D([],[],color=SHADE[outc][1],marker='o',lw=2,markersize=4),Line2D([],[],color=SHADE[outc][1],marker='D',markerfacecolor='white',lw=1.2,markersize=3.5)],
                       ['Gains-at-risk accounting model','Econometric (two-way FE) model'],loc='upper left',fontsize=5.9)
    ax.set_xticks(x); ax.set_xticklabels([SCL[s] for s in SC],fontsize=6.2); ax.set_xlim(-0.4,2.9); ax.tick_params(axis='x',length=0,pad=2)
    ax.yaxis.grid(True); ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: fm(v) if v>0 else ('0' if v==0 else '−'+fm(-v))))
    ax.set_ylabel('Excess DALYs per year in LMICs\n(median, 95% UI)',fontsize=6.3)
    V.panel(ax,L,f'{title}: excess DALYs per year',y=1.04)
# C: top countries per 100k (reference, NTDs)
ax=fig.add_subplot(gs[1,0])
r=cty[(cty.scenario=='Reference')&(cty.outcome=='NTDs (excl. malaria)')].copy()
for c,cc in [('excess_A','excess_dalys_r'),('A_lo','lo_r'),('A_hi','hi_r')]: r[cc]=r[c]/r.pop2023*1e5
t=r.nlargest(15,'excess_dalys_r').iloc[::-1]; y=np.arange(len(t))
SH={'Democratic Republic of the Congo':'DR Congo','Central African Republic':'Central African Rep.','United Republic of Tanzania':'Tanzania'}
col=[V.BLUE if s=='Sub-Saharan Africa' else V.INK2 for s in t.sr]
ax.hlines(y,t.lo_r,t.hi_r,color=col,lw=1.4); ax.scatter(t.excess_dalys_r,y,s=20,color=col,edgecolor='white',linewidth=0.8,zorder=3)
ax.set_yticks(y); ax.set_yticklabels([SH.get(n,n) for n in t.location_name],fontsize=6.2); ax.tick_params(axis='y',length=0)
ax.xaxis.grid(True); ax.set_axisbelow(True); ax.spines['left'].set_visible(False); ax.set_xlim(0,None)
ax.set_xlabel('Excess NTD DALYs per 100 000 per year\n(reference scenario, accounting model; median, 95% UI)',fontsize=6.3)
ax.legend([Line2D([],[],color=V.BLUE,marker='o',lw=1.4,markersize=4),Line2D([],[],color=V.INK2,marker='o',lw=1.4,markersize=4)],['Sub-Saharan Africa','Other super-regions'],loc='center right',fontsize=6)
V.panel(ax,'C','Most affected countries (NTDs, per capita)',x=-0.33,y=1.02)
# D: domestic financing gap
ax=fig.add_subplot(gs[1,1])
ORD=['Sub-Saharan Africa','South Asia','North Africa and Middle East','Latin America and Caribbean','Southeast Asia, East Asia, and Oceania','Central Europe, Eastern Europe, and Central Asia']
SHR={'Southeast Asia, East Asia, and Oceania':'SE Asia, E Asia & Oceania','Central Europe, Eastern Europe, and Central Asia':'C Europe, E Europe & C Asia','Latin America and Caribbean':'Latin America & Caribbean','North Africa and Middle East':'N Africa & Middle East'}
g=gap.pivot(index='sr',columns='scenario',values='domestic_increase_needed_pct').loc[ORD]; lost=gap.pivot(index='sr',columns='scenario',values='lost_ext_usd').loc[ORD]
y=np.arange(len(ORD))[::-1]
ax.barh(y,g['Reference'],height=0.5,color=V.BLUE,edgecolor='none')
ax.hlines(y,g['Mild'],g['Severe'],color=V.INK,lw=0.9); ax.scatter(g['Mild'],y,marker='|',color=V.INK,s=30); ax.scatter(g['Severe'],y,marker='|',color=V.INK,s=30)
for yi,s in zip(y,ORD):
    ax.text(g.loc[s,'Severe']+0.6,yi,f"{g.loc[s,'Reference']:.1f}%  (US${lost.loc[s,'Reference']/1e9:.2f}bn)".replace('.','·'),va='center',fontsize=5.9,color=V.INK)
ax.set_yticks(y); ax.set_yticklabels([SHR.get(s,s) for s in ORD],fontsize=6.2); ax.tick_params(axis='y',length=0); ax.spines['left'].set_visible(False)
ax.set_xlim(0,34); ax.xaxis.grid(True); ax.set_axisbelow(True)
ax.set_xlabel('Increase in domestic government health spending needed\nto replace lost external funds (%; bar = reference, whisker = mild–severe)',fontsize=6.3)
V.panel(ax,'D','Domestic financing gap by super-region',x=-0.42,y=1.02)
V.save(fig,'Figure8_funding_cut_scenarios')
