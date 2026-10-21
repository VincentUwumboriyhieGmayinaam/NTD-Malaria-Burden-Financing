"""Figure 6. Determinants (standardised) and super-region heterogeneity in the association with donor dependence."""
import pandas as pd, numpy as np, matplotlib.pyplot as plt, json
from matplotlib.ticker import FixedLocator, NullLocator
from matplotlib.lines import Line2D
import vizstyle as V; V.setup()
reg=pd.read_csv('results/regression_determinants.csv'); het=pd.read_csv('results/regression_heterogeneity_external.csv'); K=json.load(open('results/key_numbers.json'))
r=lambda p: 1+p/100
TERMS=['UHC effective coverage index','Income per capita (log LDI)','Basic drinking-water coverage','Basic sanitation coverage','Rural population share','External share of health spending']
fig=plt.figure(figsize=(V.W2,V.W2*0.62))
gs=fig.add_gridspec(1,3,width_ratios=[1,1,1.25],wspace=0.08,left=0.19,right=0.985,top=0.86,bottom=0.13)
LO,HI=0.15,3.0
def setup_ax(ax):
    ax.set_xscale('log'); ax.set_xlim(LO,HI); ax.axvline(1,color=V.INK2,lw=0.7)
    ax.xaxis.set_major_locator(FixedLocator([0.25,0.5,1,2])); ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f'{(v-1)*100:+.0f}%'.replace('+0%','0%').replace('-','−')))
    ax.xaxis.grid(True); ax.set_axisbelow(True); ax.spines['left'].set_visible(False); ax.tick_params(axis='y',length=0)
def draw(ax,y,pt,lo,hi,c,mk='o',filled=True):
    lo2,hi2=max(lo,LO),min(hi,HI)
    ax.plot([lo2,hi2],[y,y],color=c,lw=1.3,solid_capstyle='butt')
    if hi>HI: ax.annotate('',xy=(HI,y),xytext=(HI*0.88,y),arrowprops=dict(arrowstyle='->',color=c,lw=1))
    if lo<LO: ax.annotate('',xy=(LO,y),xytext=(LO/0.88,y),arrowprops=dict(arrowstyle='->',color=c,lw=1))
    ax.scatter([min(max(pt,LO),HI)],[y],s=22,marker=mk,color=c if filled else 'white',edgecolor=c if not filled else 'white',linewidth=1 if not filled else 0.8,zorder=3)
for k,(outc,L) in enumerate([('NTDs (excl. malaria)','A'),('Malaria','B')]):
    ax=fig.add_subplot(gs[k]); setup_ax(ax); y0=np.arange(len(TERMS))[::-1]
    for model,c,off,mk,fl in [('Pooled OLS + super-region FE',V.BLUE if k==0 else V.ORANGE,0.13,'o',True),('Spatial error model (ML)',V.BLUE if k==0 else V.ORANGE,-0.13,'o',False)]:
        d=reg[(reg.outcome==outc)&(reg.model==model)].set_index('term').loc[TERMS]
        for yy,(t,row) in zip(y0,d.iterrows()): draw(ax,yy+off,r(row.pct),r(row.lo),r(row.hi),c,mk,fl)
    ax.set_yticks(y0); ax.set_yticklabels(TERMS if k==0 else [],fontsize=6.5); ax.set_ylim(-0.7,len(TERMS)-0.3)
    ax.set_xlabel('% change in age-standardised DALY rate\nper 1 SD increase (log scale)',fontsize=6.2)
    V.panel(ax,L,outc.replace('(excl. malaria)','excluding malaria'),y=1.02)
    lam=K['lambda_y_ntd' if k==0 else 'lambda_y_mal']; ax.text(0.98,0.02,f"Spatial λ = {lam:.2f}; n = {K['n_regression']}".replace('.','·'),transform=ax.transAxes,ha='right',fontsize=5.8,color=V.INK2)
fig.legend([Line2D([],[],color=V.INK2,marker='o',lw=1.3,markersize=4),Line2D([],[],color=V.INK2,marker='o',markerfacecolor='white',lw=1.3,markersize=4)],
           ['OLS with super-region fixed effects (HC3 95% CI)','Spatial error model (ML, k = 6 nearest neighbours)'],loc='upper left',bbox_to_anchor=(0.18,0.995),ncol=2,fontsize=6.3)
# C heterogeneity
ax=fig.add_subplot(gs[2]); setup_ax(ax)
SR=['Sub-Saharan Africa','South Asia','Southeast Asia, East Asia, and Oceania','Latin America and Caribbean','North Africa and Middle East','Central Europe, Eastern Europe, and Central Asia','High-income']
SH={'Southeast Asia, East Asia, and Oceania':'SE Asia, E Asia & Oceania','Central Europe, Eastern Europe, and Central Asia':'C Europe, E Europe & C Asia','Latin America and Caribbean':'Latin America & Caribbean','North Africa and Middle East':'N Africa & Middle East'}
h=het[het.outcome=='NTDs (excl. malaria)'].set_index('super_region').loc[SR]
yy=np.arange(len(SR)+1)[::-1]
for y,(s,row) in zip(yy[1:],h.iterrows()):
    draw(ax,y,r(row.pct),r(row.lo),r(row.hi),V.BLUE if s=='Sub-Saharan Africa' else V.INK2)
    ax.text(LO*1.06,y+0.28,f"{SH.get(s,s)} (n = {row.n})",fontsize=6,color=V.INK,va='bottom')
pool=reg[(reg.outcome=='NTDs (excl. malaria)')&(reg.model.str.startswith('Pooled'))&(reg.term=='External share of health spending')].iloc[0]
pt,lo,hi=r(pool.pct),r(pool.lo),r(pool.hi)
ax.fill([lo,pt,hi,pt],[yy[0],yy[0]+0.22,yy[0],yy[0]-0.22],color=V.INK,lw=0)
ax.text(LO*1.06,yy[0]+0.28,'Pooled (all super-regions)',fontsize=6,fontweight='bold',va='bottom')
ax.set_yticks([]); ax.set_ylim(-0.6,len(SR)+0.75)
lr=K['het_LR_y_ntd']; ax.text(0.98,0.02,f"Heterogeneity LR χ² = {lr['LR']:.1f}, df = {lr['df']:.0f}, p < 0·001".replace('.','·'),transform=ax.transAxes,ha='right',fontsize=5.8,color=V.INK2)
ax.set_xlabel('% change in NTD DALY rate per 1 SD increase in\nexternal share of health spending (log scale)',fontsize=6.2)
V.panel(ax,'C','Region-specific association with donor dependence',y=1.02)
V.save(fig,'Figure6_determinants_heterogeneity')
