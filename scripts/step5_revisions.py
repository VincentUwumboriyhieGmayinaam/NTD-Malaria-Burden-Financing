"""Step 5 (revision analyses requested after the evidence review).
A. Socioeconomic inequality over time (1990, 2010, 2023): concentration index (CI), slope index of
   inequality (SII), relative index (RII) and Theil T decomposition, all population weighted, ranked by SDI.
B. 21 GBD regions: 2023 DALYs and age-standardised rates; 2010-2023 percent change (GBD-published UIs).
C. YLD/YLL composition by super-region, 2023.
D. National rankings 2023 with 2010 comparison; countries with rising NTD-and-malaria rates.
E. Cause-specific national leaders (19 NTD causes), 2023.
F. LISA clusters 2010 vs 2023.
G. Triangulation with WHO/UN SDG series (people requiring NTD interventions; malaria incidence).
Outputs -> results/rev_*.csv and results/rev_key_numbers.json"""
import pandas as pd, numpy as np, json, warnings, geopandas as gpd
import statsmodels.api as sm
from scipy.stats import spearmanr
from libpysal.weights import KNN
from esda.moran import Moran, Moran_Local
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings('ignore'); rng = np.random.default_rng(20261021)
R = 'data/raw/gbd'; P = 'data/processed'; K = {}
SR = ['Sub-Saharan Africa', 'South Asia', 'Southeast Asia, East Asia, and Oceania', 'Latin America and Caribbean',
      'North Africa and Middle East', 'Central Europe, Eastern Europe, and Central Asia', 'High-income']
cs = pd.read_csv(f'{P}/analysis_country_2023.csv')
loc = cs[['location_id', 'location_name', 'super_region_name', 'iso3']]

# ---------- country panel of rates, populations and SDI for 1990/2010/2023 ----------
def asr_file(cause, yr):
    d = pd.read_csv(f'{R}/country__{cause}__dalys__{yr}.csv')
    return d.set_index('location_id')[['rate_combined', 'count_combined']]
sdi = pd.read_csv(f'{R}/country__sdi.csv')
pl = pd.read_csv(f'{R}/country_panel_2005_2023_long.csv')
pl = pl[pl.cause_name.str.startswith('Negl')].assign(pop=lambda x: x.count_combined / x.rate_combined * 1e5)
pop90 = pd.read_csv(f'{R}/country__population__1990.csv').set_index('location_id')['pop']
rows = []
for yr in [1990, 2010, 2023]:
    a = asr_file('neglected_tropical_diseases_and_malaria', yr); m = asr_file('malaria', yr)
    d = loc.set_index('location_id').copy()
    d['ntdm'] = a.rate_combined; d['mal'] = m.rate_combined; d['ntd'] = d.ntdm - d.mal
    d['n_ntdm'] = a.count_combined; d['n_mal'] = m.count_combined; d['n_ntd'] = d.n_ntdm - d.n_mal
    d['pop'] = pop90 if yr == 1990 else pl[pl.year == yr].set_index('location_id')['pop']
    d['sdi'] = sdi[sdi.year == yr].set_index('location_id').sdi
    d['year'] = yr; rows.append(d.reset_index())
panel = pd.concat(rows); panel.to_csv('results/rev_country_1990_2010_2023.csv', index=False)

# ---------- A. inequality over time ----------
def ridit(d):
    d = d.sort_values('r'); wf = d.w / d.w.sum(); d = d.assign(wf=wf, R=wf.cumsum() - wf / 2); return d
def ci_fn(y, r, w):
    d = ridit(pd.DataFrame({'y': y, 'r': r, 'w': w}).dropna()); mu = (d.y * d.wf).sum()
    return 2 * (d.wf * (d.y - mu) * (d.R - (d.wf * d.R).sum())).sum() / mu
def sii_fn(y, r, w):
    d = ridit(pd.DataFrame({'y': y, 'r': r, 'w': w}).dropna())
    f = sm.WLS(d.y, sm.add_constant(d.R), weights=d.w).fit()
    b0, b1 = f.params; mu = np.average(d.y, weights=d.w); return b1, b1 / mu   # SII (top minus bottom, per 100 000), relative SII = SII / mean
def theil(y, w, g):
    d = pd.DataFrame({'y': y, 'w': w, 'g': g}).dropna(); d = d[d.y > 0]; s = d.w / d.w.sum(); mu = (s * d.y).sum()
    T = (s * (d.y / mu) * np.log(d.y / mu)).sum(); gg = d.assign(s=s).groupby('g')
    sg = gg.s.sum(); mug = gg.apply(lambda x: (x.s * x.y).sum() / x.s.sum())
    Tb = (sg * (mug / mu) * np.log(mug / mu)).sum(); return T, Tb
out = []
for yr in [1990, 2010, 2023]:
    d0 = panel[panel.year == yr].dropna(subset=['sdi', 'pop'])
    for nm, col in [('NTDs (excl. malaria)', 'ntd'), ('Malaria', 'mal')]:
        d = d0[['location_id', col, 'sdi', 'pop', 'super_region_name']].dropna()
        y, r, w = d[col].values, d.sdi.values, d['pop'].values
        ci = ci_fn(y, r, w); sii, rii = sii_fn(y, r, w); T, Tb = theil(y, w, d.super_region_name.values)
        bs = np.array([[ci_fn(y[i], r[i], w[i]), *sii_fn(y[i], r[i], w[i])] for i in
                       (rng.integers(0, len(d), len(d)) for _ in range(2000))])
        lo, hi = np.nanpercentile(bs, 2.5, axis=0), np.nanpercentile(bs, 97.5, axis=0)
        mu = np.average(y, weights=w)
        out.append(dict(outcome=nm, year=yr, n=len(d), pop_weighted_mean=mu, CI=ci, CI_lo=lo[0], CI_hi=hi[0],
                        SII=sii, SII_lo=lo[1], SII_hi=hi[1], rSII=rii, rSII_lo=lo[2], rSII_hi=hi[2],
                        Theil=T, between_pct=100 * Tb / T, within_pct=100 * (T - Tb) / T))
ineq = pd.DataFrame(out)
# paired bootstrap of change in CI and relative SII, 1990 -> 2023 (countries resampled jointly)
dd = panel.pivot_table(index='location_id', columns='year', values=['ntd', 'mal', 'sdi', 'pop']).dropna()
chg = []
for o, nm in [('ntd', 'NTDs (excl. malaria)'), ('mal', 'Malaria')]:
    for y0 in [1990, 2010]:
        def stat(ix):
            a = dd.iloc[ix]; f = lambda yr: (ci_fn(a[(o, yr)].values, a[('sdi', yr)].values, a[('pop', yr)].values), sii_fn(a[(o, yr)].values, a[('sdi', yr)].values, a[('pop', yr)].values)[1])
            c0, r0 = f(y0); c1, r1 = f(2023); return c1 - c0, r1 - r0
        pt = stat(np.arange(len(dd))); bs = np.array([stat(rng.integers(0, len(dd), len(dd))) for _ in range(2000)])
        chg.append(dict(outcome=nm, period=f'{y0}-2023', dCI=pt[0], dCI_lo=np.percentile(bs[:, 0], 2.5), dCI_hi=np.percentile(bs[:, 0], 97.5),
                        drSII=pt[1], drSII_lo=np.percentile(bs[:, 1], 2.5), drSII_hi=np.percentile(bs[:, 1], 97.5)))
chg = pd.DataFrame(chg); chg.to_csv('results/rev_inequality_change.csv', index=False); print(chg.round(3)); K['ineq_change'] = chg.to_dict('records')
ineq.to_csv('results/rev_inequality_over_time.csv', index=False)
print(ineq.round(3).to_string()); K['ineq_time'] = ineq.to_dict('records')

# ---------- B. 21 regions ----------
reg_sr = {'Central Asia': SR[5], 'Central Europe': SR[5], 'Eastern Europe': SR[5], 'Australasia': SR[6],
          'High-income Asia Pacific': SR[6], 'High-income North America': SR[6], 'Southern Latin America': SR[6],
          'Western Europe': SR[6], 'Andean Latin America': SR[3], 'Caribbean': SR[3], 'Central Latin America': SR[3],
          'Tropical Latin America': SR[3], 'North Africa and Middle East': SR[4], 'South Asia': SR[1], 'East Asia': SR[2],
          'Oceania': SR[2], 'Southeast Asia': SR[2], 'Central Sub-Saharan Africa': SR[0],
          'Eastern Sub-Saharan Africa': SR[0], 'Southern Sub-Saharan Africa': SR[0], 'Western Sub-Saharan Africa': SR[0]}
a = pd.read_csv(f'{R}/region21__ntdm__dalys__2023.csv').set_index('location_name')
m = pd.read_csv(f'{R}/region21__malaria__dalys__2023.csv').set_index('location_name')
pa = pd.read_csv(f'{R}/region21_pctchange__ntdm__dalys__2010_2023.csv').set_index('location_name')
pm = pd.read_csv(f'{R}/region21_pctchange__malaria__dalys__2010_2023.csv').set_index('location_name')
reg = pd.DataFrame(index=['Global'] + list(reg_sr))
reg['super_region'] = pd.Series(reg_sr)
reg['ntdm_n'] = a.count_combined; reg['ntdm_n_lo'] = a.count_lower_combined; reg['ntdm_n_hi'] = a.count_upper_combined
reg['ntdm_asr'] = a.rate_age_std_combined; reg['mal_n'] = m.count_combined; reg['mal_asr'] = m.rate_age_std_combined
reg['ntd_n'] = reg.ntdm_n - reg.mal_n; reg['ntd_asr'] = reg.ntdm_asr - reg.mal_asr
reg['share_global_ntdm'] = 100 * reg.ntdm_n / reg.loc['Global', 'ntdm_n']
reg['share_global_ntd'] = 100 * reg.ntd_n / reg.loc['Global', 'ntd_n']
for p, pre in [(pa, 'pc_ntdm'), (pm, 'pc_mal')]:
    reg[pre] = p.percent_change_rate_age_std_combined; reg[pre + '_lo'] = p.lower_rate_age_std_combined
    reg[pre + '_hi'] = p.upper_rate_age_std_combined
    reg[pre + '_sig'] = np.where(reg[pre + '_hi'] < 0, 'decrease', np.where(reg[pre + '_lo'] > 0, 'increase', 'uncertain'))
reg.index.name = 'region'; reg.to_csv('results/rev_region21.csv'); print(reg.round(1).to_string())
ssa = reg[reg.super_region == SR[0]]
K['ssa_regions'] = ssa[['ntdm_n', 'ntdm_asr', 'mal_n', 'mal_asr', 'ntd_n', 'ntd_asr', 'share_global_ntdm', 'pc_ntdm', 'pc_ntdm_lo', 'pc_ntdm_hi', 'pc_mal', 'pc_mal_lo', 'pc_mal_hi']].to_dict('index')
K['wssa_central_share_ntdm'] = float(reg.loc[['Western Sub-Saharan Africa', 'Central Sub-Saharan Africa'], 'share_global_ntdm'].sum())

# ---------- C. YLD / YLL ----------
yy = []
for cause, tag in [('ntdm', 'NTDs and malaria'), ('malaria', 'Malaria')]:
    yl = pd.read_csv(f'{R}/superregion__{cause}__ylds__2023.csv').set_index('location_name')
    ll = pd.read_csv(f'{R}/superregion__{cause}__ylls__2023.csv').set_index('location_name')
    for loc_ in yl.index:
        yy.append(dict(cause=tag, location=loc_, yld=yl.loc[loc_, 'count_combined'], yld_lo=yl.loc[loc_, 'count_lower_combined'],
                       yld_hi=yl.loc[loc_, 'count_upper_combined'], yll=ll.loc[loc_, 'count_combined'],
                       yll_lo=ll.loc[loc_, 'count_lower_combined'], yll_hi=ll.loc[loc_, 'count_upper_combined'],
                       yld_asr=yl.loc[loc_, 'rate_age_std_combined'], yll_asr=ll.loc[loc_, 'rate_age_std_combined']))
yy = pd.DataFrame(yy)
nt = yy[yy.cause == 'NTDs and malaria'].set_index('location')[['yld', 'yll']] - yy[yy.cause == 'Malaria'].set_index('location')[['yld', 'yll']]
nt = nt.reset_index().assign(cause='NTDs (excl. malaria)')
yy = pd.concat([yy, nt], ignore_index=True); yy['yld_share_pct'] = 100 * yy.yld / (yy.yld + yy.yll)
yy.to_csv('results/rev_yld_yll.csv', index=False); print(yy[['cause', 'location', 'yld', 'yll', 'yld_share_pct']].round(1).to_string())
K['yld_share'] = yy[yy.location == 'Global'].set_index('cause').yld_share_pct.to_dict()
K['yld_share_ntd_by_sr'] = yy[yy.cause == 'NTDs (excl. malaria)'].set_index('location').yld_share_pct.to_dict()

# ---------- D. national rankings ----------
p23 = panel[panel.year == 2023].set_index('location_id'); p10 = panel[panel.year == 2010].set_index('location_id')
nat = loc.set_index('location_id').copy()
for c in ['ntd', 'mal', 'ntdm', 'n_ntd', 'n_mal', 'n_ntdm']:
    nat[c + '_2023'] = p23[c]; nat[c + '_2010'] = p10[c]
nat['chg_ntd_asr_pct'] = 100 * (nat.ntd_2023 / nat.ntd_2010 - 1)          # computed from point estimates (no UI)
nat['chg_mal_asr_pct'] = 100 * (nat.mal_2023 / nat.mal_2010 - 1)
pc = pd.read_csv(f'{R}/country_pctchange__neglected_tropical_diseases_and_malaria__2010_2023.csv').set_index('location_id')
nat['pc_ntdm'] = pc.percent_change_rate_age_std_combined; nat['pc_ntdm_lo'] = pc.lower_rate_age_std_combined
nat['pc_ntdm_hi'] = pc.upper_rate_age_std_combined
nat['pc_ntdm_sig'] = np.where(nat.pc_ntdm_hi < 0, 'decrease', np.where(nat.pc_ntdm_lo > 0, 'increase', 'uncertain'))
nat['sdi_2023'] = p23.sdi
for c in ['ntd_2023', 'mal_2023', 'n_ntd_2023', 'n_mal_2023']: nat['rank_' + c] = nat[c].rank(ascending=False, method='min')
nat.to_csv('results/rev_national.csv')
K['n_countries_sig'] = nat.pc_ntdm_sig.value_counts().to_dict()
K['countries_increase'] = nat[nat.pc_ntdm_sig == 'increase'].sort_values('pc_ntdm', ascending=False)[['location_name', 'pc_ntdm', 'pc_ntdm_lo', 'pc_ntdm_hi']].round(1).to_dict('records')
K['n_ntd_rate_rose_point'] = int((nat.chg_ntd_asr_pct > 0).sum()); K['n_mal_rate_rose_point'] = int(((nat.chg_mal_asr_pct > 0) & (nat.mal_2010 > 1)).sum())
K['top10_ntd_rate'] = nat.nsmallest(10, 'rank_ntd_2023')[['location_name', 'ntd_2023', 'ntd_2010', 'chg_ntd_asr_pct']].round(1).to_dict('records')
K['top10_mal_rate'] = nat.nsmallest(10, 'rank_mal_2023')[['location_name', 'mal_2023', 'mal_2010', 'chg_mal_asr_pct']].round(1).to_dict('records')
K['top10_ntd_count'] = nat.nsmallest(10, 'rank_n_ntd_2023')[['location_name', 'n_ntd_2023']].round(0).to_dict('records')
K['top10_mal_count'] = nat.nsmallest(10, 'rank_n_mal_2023')[['location_name', 'n_mal_2023']].round(0).to_dict('records')
tot_ntd = nat.n_ntd_2023.sum(); tot_mal = nat.n_mal_2023.sum()
K['top10_ntd_count_share'] = float(100 * nat.nlargest(10, 'n_ntd_2023').n_ntd_2023.sum() / tot_ntd)
K['top10_mal_count_share'] = float(100 * nat.nlargest(10, 'n_mal_2023').n_mal_2023.sum() / tot_mal)
K['top3_ntd_count_share'] = float(100 * nat.nlargest(3, 'n_ntd_2023').n_ntd_2023.sum() / tot_ntd)
K['top2_mal_count_share'] = float(100 * nat.nlargest(2, 'n_mal_2023').n_mal_2023.sum() / tot_mal)
print(json.dumps({k: K[k] for k in ['n_countries_sig', 'countries_increase', 'top10_ntd_count_share', 'top10_mal_count_share']}, indent=1))

# ---------- E. cause-specific leaders ----------
causes = [c[len('daly_n_'):] for c in cs.columns if c.startswith('daly_n_') and c not in
          ('daly_n_neglected_tropical_diseases_and_malaria', 'daly_n_ntd_excl_malaria', 'daly_n_malaria')]
lead = []
for c in causes:
    n = cs.set_index('location_name')[f'daly_n_{c}']; r = cs.set_index('location_name')[f'daly_asr_{c}']
    if n.sum() <= 0: continue
    top = n.nlargest(3)
    lead.append(dict(cause=c.replace('_', ' ').capitalize(), global_dalys=n.sum(), top_count_country=top.index[0],
                     top_count_share=100 * top.iloc[0] / n.sum(), top3_count_countries='; '.join(top.index),
                     top3_count_share=100 * top.sum() / n.sum(), top_rate_country=r.idxmax(), top_rate=r.max()))
lead = pd.DataFrame(lead).sort_values('global_dalys', ascending=False); lead.to_csv('results/rev_cause_leaders.csv', index=False)
print(lead.round(1).to_string())
cn = cs.set_index('location_name')[[f'daly_n_{c}' for c in causes]]; cn.columns = causes
K['leading_ntd_cause_by_country'] = cn.idxmax(axis=1)[cn.sum(axis=1) > 0].value_counts().to_dict()

# ---------- F. LISA 2010 vs 2023 ----------
ne = gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson')
ne['iso3'] = np.where(ne.ISO_A3 == '-99', ne.ADM0_A3, ne.ISO_A3)
ne.loc[ne.ADMIN == 'France', 'iso3'] = 'FRA'; ne.loc[ne.ADMIN == 'Norway', 'iso3'] = 'NOR'; ne.loc[ne.ADMIN == 'Kosovo', 'iso3'] = 'XKX'
wide = panel.pivot_table(index='iso3', columns='year', values=['ntd', 'mal']); wide.columns = [f'{a}_{b}' for a, b in wide.columns]
geo = ne[['iso3', 'geometry']].dissolve('iso3').reset_index().merge(loc, on='iso3').merge(wide.reset_index(), on='iso3').to_crs('ESRI:54030')
pts = geo.copy(); pts['geometry'] = geo.representative_point(); w = KNN.from_dataframe(pts, k=6); w.transform = 'r'
lis = []; lc = geo[['iso3', 'location_name', 'super_region_name']].copy()
for col in ['ntd_1990', 'ntd_2010', 'ntd_2023', 'mal_1990', 'mal_2010', 'mal_2023']:
    y = np.log1p(geo[col].clip(lower=0).values); mi = Moran(y, w, permutations=9999); L = Moran_Local(y, w, permutations=9999, seed=1)
    q = pd.Series(L.q).map({1: 'High–High', 2: 'Low–High', 3: 'Low–Low', 4: 'High–Low'}).values
    fdr = multipletests(L.p_sim, method='fdr_bh')[0]; lab = np.where(fdr, q, 'Not significant'); lc[col] = lab
    lis.append(dict(series=col, moran_I=mi.I, z=mi.z_sim, p=mi.p_sim, HH=int((lab == 'High–High').sum()),
                    LL=int((lab == 'Low–Low').sum()), outliers=int(((lab == 'High–Low') | (lab == 'Low–High')).sum())))
lis = pd.DataFrame(lis); lis.to_csv('results/rev_lisa_over_time.csv', index=False); lc.to_csv('results/rev_lisa_country_over_time.csv', index=False)
print(lis.round(3).to_string())
for o in ['ntd', 'mal']:
    a10 = set(lc.loc[lc[f'{o}_2010'] == 'High–High', 'location_name']); a23 = set(lc.loc[lc[f'{o}_2023'] == 'High–High', 'location_name'])
    K[f'lisa_{o}_HH_persist'] = sorted(a10 & a23); K[f'lisa_{o}_HH_entered'] = sorted(a23 - a10); K[f'lisa_{o}_HH_exited'] = sorted(a10 - a23)
K['lisa_time'] = lis.to_dict('records')

# ---------- G. WHO triangulation ----------
who = pd.read_csv('data/raw/who/un_sdg_ntd_malaria_series.csv')
tri = []
for yr in [2010, 2023]:
    pp = panel[panel.year == yr].set_index('iso3')
    t = who[(who.series == 'SDG_SH_TRP_INTVN') & (who.year == yr)].groupby('iso3').value.first()
    d = pd.DataFrame({'gbd': pp.ntd, 'who': t / pp['pop'] * 1e5}).dropna(); d = d[d.who > 0]
    r = spearmanr(d.gbd, d.who); tri.append(dict(pair='NTD DALY rate vs people requiring NTD interventions per 100 000', year=yr, n=len(d), rho=r.statistic, p=r.pvalue))
    t = who[(who.series == 'SDG_SH_STA_MALR') & (who.year == yr)].groupby('iso3').value.first()
    d = pd.DataFrame({'gbd': pp.mal, 'who': t}).dropna(); d = d[(d.who > 0) & (d.gbd > 0)]
    r = spearmanr(d.gbd, d.who); tri.append(dict(pair='Malaria DALY rate vs WHO malaria incidence per 1000 at risk', year=yr, n=len(d), rho=r.statistic, p=r.pvalue))
tri = pd.DataFrame(tri); tri.to_csv('results/rev_who_triangulation.csv', index=False); print(tri.round(3)); K['who_tri'] = tri.to_dict('records')

json.dump(K, open('results/rev_key_numbers.json', 'w'), indent=1, default=float)
