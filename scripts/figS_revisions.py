"""Supplementary figures for the revision (each built around one message).
S1  Absolute inequality narrowed while relative concentration persisted (CI, SII, Theil; 1990/2010/2023).
S2  Malaria burden is a western/central African phenomenon; NTD burden is spread across regions; all regions fell.
S3  NTD burden is mostly disability, malaria burden is mostly premature death (why DALYs, not deaths).
S4  Spatial hot spots were stable 2010-2023.
Style: shared vizstyle (validated dataviz palette); blue = NTDs (excl. malaria), orange = malaria, everywhere."""
import pandas as pd, numpy as np, matplotlib.pyplot as plt, geopandas as gpd, sys, json
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
sys.path.insert(0, 'scripts'); import vizstyle as V; V.setup()
COL = {'NTDs (excl. malaria)': V.BLUE, 'Malaria': V.ORANGE}
YRS = [1990, 2010, 2023]

# ---------------- S1 ----------------
iq = pd.read_csv('results/rev_inequality_over_time.csv'); ch = pd.read_csv('results/rev_inequality_change.csv')
fig, axs = plt.subplots(1, 3, figsize=(V.W2, 64 * V.MM)); fig.subplots_adjust(wspace=0.5, bottom=0.2)
def series(ax, m, lo=None, hi=None, fmt='{:.2f}', labelend=True):
    for k, (o, c) in enumerate(COL.items()):
        d = iq[iq.outcome == o].sort_values('year'); x = np.arange(3) + (k - 0.5) * 0.12
        ax.plot(x, d[m], color=c, lw=1.0, zorder=2)
        if lo: ax.vlines(x, d[lo], d[hi], color=c, lw=1.6, alpha=0.45, zorder=1)
        ax.scatter(x, d[m], s=22, color=c, edgecolor='white', linewidth=1.2, zorder=3)
        if labelend: ax.text(x[-1] + 0.12, d[m].iloc[-1], fmt.format(d[m].iloc[-1]).replace('-', '−'), va='center', fontsize=6, color=V.INK2)
    ax.set_xticks(range(3)); ax.set_xticklabels(YRS); ax.set_xlim(-0.35, 2.75)
    ax.grid(True, axis='y'); ax.set_axisbelow(True)
series(axs[0], 'CI', 'CI_lo', 'CI_hi'); axs[0].set_ylim(-1, 0.02); axs[0].axhline(0, color=V.INK2, lw=0.6)
axs[0].set_ylabel('Concentration index (95% CI)\n← concentrated in low-SDI countries')
d = ch[(ch.outcome == 'NTDs (excl. malaria)') & (ch.period == '2010-2023')].iloc[0]
axs[0].text(0.03, -0.1, f'NTDs, change 2010–2023: +{d.dCI:.2f}\n(95% CI {d.dCI_lo:.2f} to {d.dCI_hi:.2f})', fontsize=5.6, color=V.INK2)
axs[0].text(1.0, -0.98, 'Malaria: no detectable change', ha='center', fontsize=5.6, color=V.INK2)
V.panel(axs[0], 'A', 'Relative inequality persisted', x=-0.4, y=1.04)
series(axs[1], 'SII', 'SII_lo', 'SII_hi', fmt='{:,.0f}'); axs[1].axhline(0, color=V.INK2, lw=0.6)
axs[1].set_ylabel('SII, DALYs per 100 000 (95% CI)\nhigh- minus low-SDI end')
axs[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'{v:,.0f}'.replace('-', '−')))
V.panel(axs[1], 'B', 'Absolute gap narrowed', x=-0.4, y=1.04)
series(axs[2], 'Theil', labelend=False); axs[2].set_ylim(0, 1.85)
for k, o in enumerate(COL):
    dd = iq[iq.outcome == o].sort_values('year')
    for xi, (v, b) in enumerate(zip(dd.Theil, dd.between_pct)):
        axs[2].text(xi + (k - 0.5) * 0.12, v + 0.09, f'{b:.0f}%', ha='center', fontsize=5.6, color=V.INK2)
axs[2].set_ylabel('Theil T\n(labels: % between super-regions)')
V.panel(axs[2], 'C', 'Total inequality and its source', x=-0.4, y=1.04)
fig.legend(handles=[Line2D([], [], color=c, marker='o', lw=1, ms=4, mec='white', label=o) for o, c in COL.items()],
           loc='lower center', ncol=2, bbox_to_anchor=(0.5, 0.0))
V.save(fig, 'FigureS1_inequality_over_time')

# ---------------- S2 ----------------
r = pd.read_csv('results/rev_region21.csv').set_index('region')
SRO = ['Sub-Saharan Africa', 'South Asia', 'Southeast Asia, East Asia, and Oceania', 'Latin America and Caribbean',
       'North Africa and Middle East', 'Central Europe, Eastern Europe, and Central Asia', 'High-income']
SRS = ['Sub-Saharan Africa', 'South Asia', 'SE Asia, E Asia & Oceania', 'Latin America & Caribbean', 'N Africa & Middle East',
       'C Europe, E Europe & C Asia', 'High-income']
order = []
for sr in SRO: order += list(r[r.super_region == sr].sort_values('ntdm_asr', ascending=False).index)
r = r.loc[order]; ypos = []; y = 0; grp_y = {}
for sr in SRO:
    grp_y[sr] = y
    for g in order:
        if r.loc[g, 'super_region'] == sr: ypos.append(y); y += 1
    y += 0.9
ypos = np.array(ypos)
fig, axs = plt.subplots(1, 3, figsize=(V.W2, 120 * V.MM), sharey=True, gridspec_kw={'width_ratios': [1.25, 0.5, 1.1]})
fig.subplots_adjust(wspace=0.07, left=0.2)
ax = axs[0]
mm = (r.mal_asr > 1).values
for i, g in enumerate(order):
    if mm[i]: ax.plot([min(r.ntd_asr.iloc[i], r.mal_asr.iloc[i]), max(r.ntd_asr.iloc[i], r.mal_asr.iloc[i])], [ypos[i]] * 2, color=V.GRID, lw=1.6, zorder=1)
ax.scatter(r.ntd_asr, ypos, s=26, color=V.BLUE, edgecolor='white', lw=1.2, zorder=3, label='NTDs (excl. malaria)')
ax.scatter(r.mal_asr[mm], ypos[mm], s=26, color=V.ORANGE, edgecolor='white', lw=1.2, zorder=3, label='Malaria')
ax.scatter(np.full((~mm).sum(), 1.15), ypos[~mm], s=16, marker='|', color=V.ORANGE, lw=0.9, zorder=3)
ax.set_xscale('log'); ax.set_xlim(1, 9000); ax.grid(True, axis='x'); ax.set_axisbelow(True)
ax.set_xticks([1, 10, 100, 1000]); ax.set_xticklabels(['≤1', '10', '100', '1 000'])
ax.set_yticks(ypos); ax.set_yticklabels(order); ax.set_ylim(y - 0.5, -1.6)
for t, g in zip(ax.get_yticklabels(), order): t.set_fontweight('bold' if r.loc[g, 'super_region'] == 'Sub-Saharan Africa' else 'normal')
ax.set_xlabel('Age-standardised DALYs per 100 000, 2023\n(log scale; | = malaria ≤1)')
for sr, s in zip(SRO, SRS): ax.text(-0.02, grp_y[sr] - 0.75, s.upper(), transform=ax.get_yaxis_transform(), fontsize=5.3, color=V.MUTED, fontweight='bold', va='center', ha='right')
V.panel(ax, 'A', 'Rate by GBD region', x=0.0, y=1.01)
ax = axs[1]
ax.barh(ypos, r.share_global_ntdm, height=0.62, color=V.INK2, edgecolor='white', lw=0.6)
for yi, v in zip(ypos, r.share_global_ntdm):
    if v >= 0.95: ax.text(v + 1, yi, f'{v:.1f}', va='center', fontsize=5.6, color=V.INK2)
ax.set_xlim(0, 64); ax.set_xticks([0, 25, 50]); ax.set_xlabel('Share of global\nNTD + malaria DALYs (%)')
V.panel(ax, 'B', 'Share', x=0.0, y=1.01)
ax = axs[2]
for k, (pre, c, lab) in enumerate([('pc_ntdm', V.BLUE, 'NTDs and malaria'), ('pc_mal', V.ORANGE, 'Malaria')]):
    yy_ = ypos + (k - 0.5) * 0.32; ok = (r[pre].notna() & (r[pre] > -99.9)).values; el = (r[pre] <= -99.9).values
    ax.hlines(yy_[ok], r[pre + '_lo'][ok], r[pre + '_hi'][ok], color=c, lw=1.4, alpha=0.5)
    ax.scatter(r[pre][ok], yy_[ok], s=18, color=c, edgecolor='white', lw=1, zorder=3, label=lab)
    ax.scatter(np.full(el.sum(), -100), yy_[el], s=14, marker='x', color=c, lw=0.8, zorder=3)
ax.axvline(0, color=V.INK2, lw=0.6); ax.set_xlim(-106, 55); ax.grid(True, axis='x'); ax.set_axisbelow(True)
ax.set_xlabel('Change in age-standardised rate, 2010–2023\n(%, 95% UI; × = eliminated)')
yn = ypos[order.index('North Africa and Middle East')]
ax.annotate('Only regional increase:\nmalaria, N Africa & Middle East', xy=(26.3, yn + 0.16), xytext=(6, yn - 4.6), fontsize=5.6, color=V.INK2,
            arrowprops=dict(arrowstyle='-', color=V.MUTED, lw=0.5))
V.panel(ax, 'C', 'Change, 2010–2023', x=0.0, y=1.01)
fig.subplots_adjust(bottom=0.14)
fig.legend(handles=[Line2D([], [], ls='', marker='o', color=V.BLUE, mec='white', ms=5, label='NTDs excl. malaria (A); NTDs and malaria combined (C)'), Line2D([], [], ls='', marker='o', color=V.ORANGE, mec='white', ms=5, label='Malaria')], loc='lower center', ncol=2, bbox_to_anchor=(0.55, 0.0))
V.save(fig, 'FigureS2_gbd_regions')

# ---------------- S3 ----------------
yy = pd.read_csv('results/rev_yld_yll.csv')
order3 = ['Global'] + SRO; short = ['Global'] + SRS
fig, axs = plt.subplots(1, 2, figsize=(V.W2, 66 * V.MM), sharey=True); fig.subplots_adjust(wspace=0.1, bottom=0.26)
for ax, (cause, L) in zip(axs, [('NTDs (excl. malaria)', 'A'), ('Malaria', 'B')]):
    d = yy[yy.cause == cause].set_index('location').reindex(order3); tot = d.yld + d.yll
    s1 = (100 * d.yld / tot).where(tot >= 1000); s2 = 100 - s1; yv = np.arange(len(order3))[::-1]
    ax.barh(yv, s1, height=0.66, color=COL[cause], edgecolor='white', lw=1.2)
    ax.barh(yv, s2, left=s1, height=0.66, color=V.DEEMPH, edgecolor='white', lw=1.2)
    for yi, a, t in zip(yv, s1, tot):
        if pd.isna(a): ax.text(2, yi, 'negligible burden', va='center', fontsize=5.6, color=V.MUTED); continue
        inside = a > 14
        ax.text(a - 2 if inside else a + 1.5, yi, f'{a:.0f}%', va='center', ha='right' if inside else 'left', fontsize=5.8,
                color='white' if inside else V.INK, fontweight='bold')
        ax.text(102, yi, f'{t/1e6:.2f}M', va='center', fontsize=5.6, color=V.INK2)
    ax.text(102, len(order3) - 0.35, 'DALYs', fontsize=5.6, color=V.MUTED)
    ax.set_xlim(0, 117); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xlabel('Share of DALYs, 2023 (%)')
    V.panel(ax, L, f'{cause}: share from disability', x=0.0, y=1.04)
axs[0].set_yticks(np.arange(len(order3))[::-1]); axs[0].set_yticklabels(short)
axs[0].get_yticklabels()[0].set_fontweight('bold')
fig.legend(handles=[Patch(color=V.BLUE, label='YLDs (disability), NTDs'), Patch(color=V.ORANGE, label='YLDs (disability), malaria'), Patch(color=V.DEEMPH, label='YLLs (premature death)')],
           loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0.0))
V.save(fig, 'FigureS3_yld_yll')

# ---------------- S4 ----------------
lc = pd.read_csv('results/rev_lisa_country_over_time.csv'); K = json.load(open('results/rev_key_numbers.json'))
li = pd.read_csv('results/rev_lisa_over_time.csv').set_index('series')
ne = gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson'); ne['iso3'] = np.where(ne.ISO_A3 == '-99', ne.ADM0_A3, ne.ISO_A3)
ne.loc[ne.ADMIN == 'France', 'iso3'] = 'FRA'; ne.loc[ne.ADMIN == 'Norway', 'iso3'] = 'NOR'
g = ne[['iso3', 'geometry']].dissolve('iso3').reset_index().merge(lc.assign(iso3=lc.iso3.replace({'ALA': 'FIN'})), on='iso3', how='left')
g = g[g.iso3 != 'ATA'].to_crs('ESRI:54030')
cmap = {'High–High': V.RED, 'Low–Low': V.BLUE, 'High–Low': V.RED_LIGHT, 'Low–High': V.BLUE_LIGHT, 'Not significant': V.NEUTRAL}
fig, axs = plt.subplots(2, 2, figsize=(V.W2, 96 * V.MM)); fig.subplots_adjust(wspace=0.0, hspace=0.06, bottom=0.08)
for ax, (col, L, T) in zip(axs.flat, [('ntd_2010', 'A', 'NTDs (excl. malaria), 2010'), ('ntd_2023', 'B', 'NTDs (excl. malaria), 2023'),
                                     ('mal_2010', 'C', 'Malaria, 2010'), ('mal_2023', 'D', 'Malaria, 2023')]):
    g.plot(ax=ax, color=g[col].map(cmap).fillna(V.NODATA), edgecolor='white', linewidth=0.15)
    o = col.split('_')[0]; s = li.loc[col]
    txt = f"Moran's I = {s.moran_I:.2f}; high–high n = {int(s.HH)}"
    if col.endswith('2023'):
        g[g.location_name.isin(K[f'lisa_{o}_HH_entered'])].plot(ax=ax, facecolor='none', edgecolor=V.INK, linewidth=0.9)
        txt += f"\nEntered high–high: {', '.join(K[f'lisa_{o}_HH_entered']) or 'none'}; left: {', '.join(K[f'lisa_{o}_HH_exited']) or 'none'}"
    ax.text(0.03, 0.04, txt, transform=ax.transAxes, fontsize=5.6, color=V.INK2, va='bottom')
    ax.set_xlim(-1.3e7, 1.6e7); ax.set_ylim(-6.3e6, 8.6e6); ax.set_axis_off(); V.panel(ax, L, T, x=0.0, y=0.97)
fig.legend(handles=[Patch(color=c, label=k) for k, c in cmap.items()] + [Patch(color=V.NODATA, label='No data'), Patch(facecolor='none', edgecolor=V.INK, label='Entered high–high')],
           loc='lower center', ncol=7, bbox_to_anchor=(0.5, 0.0), handlelength=1.2, columnspacing=0.9)
V.save(fig, 'FigureS4_lisa_2010_2023')
print('ok')
