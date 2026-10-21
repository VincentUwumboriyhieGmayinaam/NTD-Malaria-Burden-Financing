"""Figure 1. Analytical workflow: data acquisition (sources) -> 8 numbered stages -> outputs. Same layout as the manuscript doc diagram."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import vizstyle as V; V.setup()
W,H=760,768
fig=plt.figure(figsize=(V.W2,V.W2*H/W)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(H,0); ax.set_axis_off()
def box(x,y,w,h,main=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=8',fc=V.BLUE_LIGHT if main else 'white',
                                ec=V.BLUE if main else V.AXIS,lw=1.1 if main else 0.7,alpha=1))
def t(x,y,s,bold=False,c=None,size=6.6,ha='left'): ax.text(x,y,s,fontsize=size,fontweight='bold' if bold else 'normal',color=c or (V.INK if bold else V.INK2),ha=ha,va='baseline')
def ar(x1,y1,x2,y2): ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='-|>,head_length=0.35,head_width=0.18',color=V.MUTED,lw=0.7,shrinkA=0,shrinkB=0))
src=[('GBD 2023','DALYs · SDI · UHC · LDI'),('World Bank WDI','Health finance · WASH'),('WHO via UN SDG','SDG 3.3.5 · 3.3.3'),('IHME FGH','DAH 2024–2025'),('Natural Earth','Admin-0 boundaries')]
for i,(a,b) in enumerate(src):
    x=24+144*i; box(x,56,136,56); t(x+68,80,a,True,ha='center',size=7); t(x+68,99,b,ha='center',size=6.2); ar(x+68,112,x+68,147)
t(24,40,'Data sources',True,size=7.5)
stages=[(148,'1. Data acquisition','Programmatic download, raw files archived; truncated calls re-queried; completeness checked per country-year'),
        (212,'2. Harmonisation and linkage','ISO3 and GBD location IDs; GBD super-region assignment; 204 countries × 2005–2023 panel'),
        (276,'3. Quality control and missing data','Interior interpolation, carry-forward ≤2 years, every fill flagged; complete-case, balanced-panel and MICE (m = 20) checks')]
for y,a,b in stages: box(24,y,712,48); t(40,y+20,a,True,size=7); t(40,y+38,b,size=6.2)
ar(380,196,380,211); ar(380,260,380,275)
cols=[(24,'4. Descriptive and inequality',['Rates and trends, 1990–2023','Concentration index ranked by SDI','Theil T: between/within super-region']),
      (268,'5. Spatial analysis',["Global Moran's I, KNN k = 6",'LISA, 9 999 permutations','Benjamini–Hochberg FDR, q < .05']),
      (512,'6. Panel econometrics',['7 estimators, 6 assumption tests','Two-way FE, Driscoll–Kraay SE','153 LMICs, 2007–2022'])]
for x,a,ls in cols:
    box(x,360,224,96); t(x+16,384,a,True,size=7)
    for k,l in enumerate(ls): t(x+16,404+18*k,l,size=6.2)
    ar(x+112,324,x+112,359)
box(268,480,468,80); t(284,504,'7. Robustness and heterogeneity',True,size=7)
t(284,524,'Spatial panel SAR and SEM (two-way FE) · GWR and MGWR · random forest, LightGBM, elastic net',size=6.2)
t(284,542,'Leave-country-out, spatial-block and temporal validation; SHAP attribution',size=6.2)
box(268,584,468,80); t(284,608,'8. Funding-cut scenarios',True,size=7)
t(284,628,'Accounting and econometric models · 4 000 Monte Carlo draws',size=6.2)
t(284,646,'Economic value at 0.5–3 × GDP per capita · domestic financing gap',size=6.2)
ar(380,456,380,479); ar(624,456,624,479); ar(502,560,502,583)
box(24,688,712,56,True); t(40,712,'Outputs',True,size=7); t(40,731,'Tables 1–4 and S1–S13 · Figures 1–8 · archived code and processed data',c=V.INK,size=6.2)
ar(136,456,136,687); ar(502,664,502,687)
V.save(fig,'Figure1_workflow')
