"""Figure 3. Trends in age-standardised DALY rates, 1990-2023: small multiples by super-region (shared log axis)."""
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullLocator
import vizstyle as V; V.setup()
tr=pd.read_csv('data/processed/gbd_superregion_trends.csv'); tr=tr[tr.measure=='dalys']
p=tr.pivot_table(index=['location_name','year'],columns='cause_name',values='rate_age_std_combined').reset_index()
p['NTD']=p['Neglected tropical diseases and malaria']-p['Malaria']
pc=pd.read_csv('data/raw/gbd/superregion_pctchange__ntdm__dalys__2010_2023.csv').set_index('location_name')
ORDER=['Global','Sub-Saharan Africa','South Asia','Southeast Asia, East Asia, and Oceania','Latin America and Caribbean','North Africa and Middle East','Central Europe, Eastern Europe, and Central Asia','High-income']
TT={'Southeast Asia, East Asia, and Oceania':'SE Asia, E Asia & Oceania','Central Europe, Eastern Europe, and Central Asia':'C Europe, E Europe & C Asia','Latin America and Caribbean':'Latin America & Caribbean','North Africa and Middle East':'N Africa & Middle East'}
fig,axs=plt.subplots(2,4,figsize=(V.W2,V.W2*0.52),sharex=True,sharey=True,gridspec_kw={'hspace':0.42,'wspace':0.12,'left':0.07,'right':0.99,'top':0.85,'bottom':0.1})
for ax,loc in zip(axs.flat,ORDER):
    d=p[p.location_name==loc].sort_values('year')
    for col,c in [('NTD',V.BLUE),('Malaria',V.ORANGE)]:
        y=d[col].where(d[col]>0.5)
        ax.plot(d.year,y,color=c,lw=1.4)
        ax.scatter(d.year.iloc[-1:],y.iloc[-1:],s=10,color=c,edgecolor='white',linewidth=0.6,zorder=3)
    ax.set_yscale('log'); ax.set_ylim(0.8,15000); ax.yaxis.set_major_locator(FixedLocator([1,10,100,1000,10000])); ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f'{v:,.0f}'.replace(',',' ')))
    ax.yaxis.grid(True); ax.set_axisbelow(True); ax.set_xlim(1988,2025); ax.set_xticks([1990,2005,2023])
    ax.axvspan(2010,2023,color=V.NEUTRAL,zorder=0,lw=0)
    ax.set_title(TT.get(loc,loc),fontsize=6.8,pad=10,fontweight='bold' if loc=='Global' else 'normal')
    r=pc.loc[loc]; sig='' if (r.pc_rate_agestd_lo<0<r.pc_rate_agestd_hi) else ''
    txt=f"2010–23: {r.pc_rate_agestd:+.0f}% ({r.pc_rate_agestd_lo:+.0f} to {r.pc_rate_agestd_hi:+.0f})".replace('-','−')
    ax.text(0.0,1.015,txt,transform=ax.transAxes,fontsize=5.6,color=V.INK2,va='bottom')
    if loc=='Global':
        for col,c,lab,dy in [('NTD',V.BLUE,'NTDs excl. malaria',0.38),('Malaria',V.ORANGE,'Malaria',1.6)]:
            ax.text(1991,d[col].iloc[0]*dy,lab,color=V.INK,fontsize=6)
for ax in axs[:,0]: ax.set_ylabel('Age-standardised DALYs\nper 100 000 (log)',fontsize=6.3)
from matplotlib.lines import Line2D
fig.legend([Line2D([],[],color=V.BLUE,lw=1.6),Line2D([],[],color=V.ORANGE,lw=1.6),plt.Rectangle((0,0),1,1,color=V.NEUTRAL)],
           ['NTDs excluding malaria','Malaria','2010–2023 window (label: GBD % change in age-standardised NTD + malaria DALY rate, 95% UI)'],
           loc='upper left',bbox_to_anchor=(0.065,0.995),ncol=3,fontsize=6.3,handlelength=1.6,columnspacing=1.4)
V.save(fig,'Figure4_trends_superregion')
