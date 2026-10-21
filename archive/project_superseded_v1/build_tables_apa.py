"""Build APA-7 formatted tables (main text + supplementary) into Word documents.
APA style: 'Table N' bold; title italic in title case on the next line; horizontal rules only
(top, below column headings, bottom); no vertical rules; 'Note.' in italics below the table."""
import pandas as pd, numpy as np, json
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

P='data/processed'; R='results'
K=json.load(open(f'{R}/key_numbers.json'))
cs=pd.read_csv(f'{P}/analysis_country_2023.csv')
SR=['Sub-Saharan Africa','South Asia','Southeast Asia, East Asia, and Oceania','Latin America and Caribbean','North Africa and Middle East','Central Europe, Eastern Europe, and Central Asia','High-income']
FONT='Times New Roman'

def f0(v): return '—' if pd.isna(v) else f'{v:,.0f}'
def f1(v): return '—' if pd.isna(v) else f'{v:,.1f}'
def f2(v): return '—' if pd.isna(v) else f'{v:.2f}'
def fp(p):
    if pd.isna(p): return '—'
    return '< .001' if p<0.001 else f'{p:.3f}'.lstrip('0')
def ci(pt,lo,hi,fmt=f1): return f'{fmt(pt)} [{fmt(lo)}, {fmt(hi)}]'
def miqr(s,fmt=f1):
    s=s.dropna(); return '—' if len(s)==0 else f'{fmt(s.median())} ({fmt(s.quantile(.25))}–{fmt(s.quantile(.75))})'

def border(cell,**kw):
    tcPr=cell._tc.get_or_add_tcPr(); b=tcPr.find(qn('w:tcBorders'))
    if b is None: b=OxmlElement('w:tcBorders'); tcPr.append(b)
    for edge,val in kw.items():
        el=OxmlElement(f'w:{edge}'); el.set(qn('w:val'),val); el.set(qn('w:sz'),'8'); el.set(qn('w:space'),'0'); el.set(qn('w:color'),'000000'); b.append(el)

def para(doc,text,bold=False,italic=False,size=11,align=None,space_after=0):
    p=doc.add_paragraph(); r=p.add_run(text); r.bold=bold; r.italic=italic; r.font.size=Pt(size); r.font.name=FONT
    p.paragraph_format.space_after=Pt(space_after); p.paragraph_format.space_before=Pt(0)
    if align: p.alignment=align
    return p

def add_table(doc,num,title,df,note,col_widths=None,size=9,first_col_left=True,group_rows=None):
    para(doc,f'Table {num}',bold=True,size=11)
    para(doc,title,italic=True,size=11,space_after=4)
    t=doc.add_table(rows=1,cols=len(df.columns)); t.autofit=False
    hdr=t.rows[0].cells
    for j,c in enumerate(df.columns):
        hdr[j].text=''; r=hdr[j].paragraphs[0].add_run(str(c)); r.font.size=Pt(size); r.font.name=FONT; r.bold=False
        hdr[j].paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.LEFT if (j==0 and first_col_left) else WD_ALIGN_PARAGRAPH.CENTER
        border(hdr[j],top='single',bottom='single')
    for i,row in enumerate(df.itertuples(index=False)):
        cells=t.add_row().cells
        is_group=group_rows is not None and i in group_rows
        for j,v in enumerate(row):
            cells[j].text=''; r=cells[j].paragraphs[0].add_run('' if (pd.isna(v) if not isinstance(v,str) else False) else str(v))
            r.font.size=Pt(size); r.font.name=FONT; r.italic=is_group
            cells[j].paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.LEFT if (j==0 and first_col_left) else WD_ALIGN_PARAGRAPH.CENTER
            cells[j].paragraphs[0].paragraph_format.space_after=Pt(0)
    for c in t.rows[-1].cells: border(c,bottom='single')
    if col_widths:
        for row in t.rows:
            for j,wd in enumerate(col_widths): row.cells[j].width=Cm(wd)
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(3)
    r=p.add_run('Note. '); r.italic=True; r.font.size=Pt(9); r.font.name=FONT
    r=p.add_run(note); r.font.size=Pt(9); r.font.name=FONT
    doc.add_paragraph()

def new_doc(title,landscape=True):
    doc=Document(); st=doc.styles['Normal']; st.font.name=FONT; st.font.size=Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'),FONT)
    s=doc.sections[0]
    if landscape:
        s.orientation=WD_ORIENT.LANDSCAPE; s.page_width,s.page_height=s.page_height,s.page_width
    for m in ['left_margin','right_margin','top_margin','bottom_margin']: setattr(s,m,Cm(2.0))
    para(doc,title,bold=True,size=13,align=WD_ALIGN_PARAGRAPH.CENTER,space_after=10)
    return doc

SHORT={'Southeast Asia, East Asia, and Oceania':'Southeast Asia, East Asia, and Oceania'}
cs['sr']=pd.Categorical(cs.super_region_name,SR)
t1=pd.read_csv(f'{R}/table1_superregion_burden.csv',index_col=0)

# ======================= MAIN TABLES =======================
doc=new_doc('Main-text tables')
rows=[]
for s in SR+['Global']:
    d=cs if s=='Global' else cs[cs.sr==s]
    tb=t1.loc[s] if s!='Global' else None
    rows.append({'Super-region':s,'Countries, n':len(d),
      'Population, millions (%)':f"{d.pop_latest.sum()/1e6:,.0f} ({100*d.pop_latest.sum()/cs.pop_latest.sum():.1f})",
      'NTD DALYs, thousands (%)':f"{d.daly_n_ntd_excl_malaria.sum()/1e3:,.0f} ({100*d.daly_n_ntd_excl_malaria.sum()/cs.daly_n_ntd_excl_malaria.sum():.1f})",
      'Malaria DALYs, thousands (%)':f"{d.daly_n_malaria.sum()/1e3:,.0f} ({100*d.daly_n_malaria.sum()/cs.daly_n_malaria.sum():.1f})",
      'NTD ASR':f1(tb.asr_ntd_2023) if tb is not None else '—','Malaria ASR':f1(tb.asr_mal_2023) if tb is not None else '—',
      'SDI, Mdn (IQR)':miqr(d.sdi_2023,f2),'UHC index, Mdn (IQR)':miqr(d.uhc_2023,f1),
      'CHE per capita, US$, Mdn (IQR)':miqr(d.che_pc_usd_latest,f0),'External share of CHE, %, Mdn (IQR)':miqr(d.ext_pct_che_latest,f1),
      'Basic sanitation, %, Mdn (IQR)':miqr(d.sanit_basic_pct_latest,f1)})
T1=pd.DataFrame(rows)
add_table(doc,1,'Burden of Neglected Tropical Diseases and Malaria and Health-System Characteristics by GBD Super-Region, 2023',T1,
 'NTD = neglected tropical diseases excluding malaria (19 GBD causes); DALYs = disability-adjusted life-years; ASR = age-standardised DALY rate per 100,000 '
 '(super-region values from GBD 2023; NTD ASR = NTDs-and-malaria ASR minus malaria ASR); SDI = Socio-demographic Index; UHC = universal health coverage effective-coverage index (0–100); '
 'CHE = current health expenditure; external share = external (donor) health expenditure as % of CHE. Medians and interquartile ranges (IQR) are across countries (unweighted). '
 'Population and expenditure from World Bank WDI (latest value 2019–2023). Sources: GBD 2023 (IHME), World Bank WDI.',size=8)

reg=pd.read_csv(f'{R}/regression_determinants.csv')
TERMS=['Income per capita (log LDI)','UHC effective coverage index','Basic sanitation coverage','Basic drinking-water coverage','Rural population share','External share of health spending']
rows=[]
for t in TERMS:
    row={'Predictor (per 1 SD)':t}
    for outc,ab in [('NTDs (excl. malaria)','NTD'),('Malaria','Malaria')]:
        for mod,mb in [('Pooled OLS + super-region FE','OLS'),('Spatial error model (ML)','SEM')]:
            r=reg[(reg.outcome==outc)&(reg.model==mod)&(reg.term==t)].iloc[0]
            row[f'{ab}: {mb} % change [95% CI]']=ci(r.pct,r.lo,r.hi); row[f'{ab}: {mb} p']=fp(r.p)
    rows.append(row)
T2=pd.DataFrame(rows)
r2n=reg[(reg.model.str.startswith('Pooled'))].groupby('outcome').r2.first()
add_table(doc,2,'Country-Level Determinants of Age-Standardised NTD and Malaria DALY Rates, 2023',T2,
 f"Estimates are percentage changes in the age-standardised DALY rate associated with a 1-SD increase in each predictor, from log-linear models with super-region fixed effects (n = {K['n_regression']} countries). "
 f"OLS = ordinary least squares with HC3 robust standard errors (R² = {r2n['NTDs (excl. malaria)']:.2f} for NTDs, {r2n['Malaria']:.2f} for malaria); SEM = maximum-likelihood spatial error model with row-standardised k = 6 nearest-neighbour weights "
 f"(λ = {K['lambda_y_ntd']:.2f} and {K['lambda_y_mal']:.2f}). LDI = lag-distributed income. Malaria outcome modelled as log(1 + rate). Associations are ecological and cross-sectional and should not be interpreted causally.",size=8)

sc=pd.read_csv(f'{R}/scenario_excess_dalys_superregion.csv'); gap=pd.read_csv(f'{R}/scenario_financing_gap.csv')
rows=[]
for s in SR[:-1]+['All endemic (LMIC) countries']:
    row={'Super-region':s}
    for outc,ab in [('NTDs (excl. malaria)','NTD'),('Malaria','Malaria')]:
        r=sc[(sc.scenario=='Reference')&(sc.outcome==outc)&(sc.super_region==s)].iloc[0]
        row[f'{ab} excess DALYs/yr [95% UI]']=ci(r.excess_dalys,r.lo,r.hi,f0)
        row[f'{ab} % of 2023 burden']=f1(r.pct_of_2023_burden)
        row[f'{ab} value, US$ million']=f0(r.value_usd_1gdp/1e6)
    if s in SR:
        gg=gap[(gap.scenario=='Reference')&(gap.sr==s)].iloc[0]; row['Lost external funds, US$ million']=f0(gg.lost_ext_usd/1e6); row['Domestic increase needed, %']=f1(gg.domestic_increase_needed_pct)
    else:
        gg=gap[gap.scenario=='Reference']; row['Lost external funds, US$ million']=f0(gg.lost_ext_usd.sum()/1e6); row['Domestic increase needed, %']=f1(100*gg.lost_ext_usd.sum()/gg.ghed_total_usd.sum())
    rows.append(row)
for scn in ['Mild','Severe']:
    row={'Super-region':f'All LMICs — {scn.lower()} scenario'}
    for outc,ab in [('NTDs (excl. malaria)','NTD'),('Malaria','Malaria')]:
        r=sc[(sc.scenario==scn)&(sc.outcome==outc)&(sc.super_region.str.startswith('All'))].iloc[0]
        row[f'{ab} excess DALYs/yr [95% UI]']=ci(r.excess_dalys,r.lo,r.hi,f0); row[f'{ab} % of 2023 burden']=f1(r.pct_of_2023_burden); row[f'{ab} value, US$ million']=f0(r.value_usd_1gdp/1e6)
    gg=gap[gap.scenario==scn]; row['Lost external funds, US$ million']=f0(gg.lost_ext_usd.sum()/1e6); row['Domestic increase needed, %']=f1(100*gg.lost_ext_usd.sum()/gg.ghed_total_usd.sum())
    rows.append(row)
T3=pd.DataFrame(rows)
add_table(doc,3,'Projected Excess Annual DALYs, Economic Value, and Domestic Financing Gap Under External Funding-Cut Scenarios',T3,
 'Reference scenario (rows 1–7) applies a 19–26% reduction in external health financing, bracketing the IHME preliminary 2024–2025 decline in development assistance for health (US$49.6 billion to US$38.4 billion; '
 'Apeagyei et al., 2025); mild = 5–15%, severe = 40–60%. Excess DALYs = donor-attributable share of each country\'s 2010–2023 reduction in age-standardised DALY rate that is lost, '
 'computed as max(0, ASR₂₀₁₀ − ASR₂₀₂₃) × population × external share of CHE × cut fraction, summed over 14 NTDs with 2010 estimates (or malaria). '
 '95% uncertainty intervals (UI) from 2,000 Monte Carlo draws over GBD UIs and the cut range. Values are steady-state annual DALYs once gains erode, not first-year effects. '
 'Economic value at 1 × GDP per capita per DALY (0.5× and 3× in Table S7). Domestic increase = lost external funds as % of domestic general government health expenditure. High-income super-region excluded.',size=8)
doc.save('tables/Main_Tables_APA.docx')

# ======================= SUPPLEMENTARY =======================
doc=new_doc('Supplementary tables')
src=pd.DataFrame([
 ['NTD and malaria burden (DALYs, deaths, prevalence)','GBD 2023, IHME','204 countries, 7 super-regions','1990, 2000, 2010, 2019, 2023','Age-standardised rate, all-age count, 95% UI'],
 ['Percent change 2010–2023','GBD 2023, IHME','204 countries, 7 super-regions','2010–2023','Published % change with 95% UI'],
 ['Socio-demographic Index (SDI)','GBD 2023, IHME','204 countries','1990–2023','Index 0–1'],
 ['UHC effective coverage; lag-distributed income','GBD 2023 covariates, IHME','204 countries','2005–2023','Index 0–100; I$ per capita'],
 ['Health expenditure (current, government, external, out-of-pocket)','World Bank WDI (WHO GHED)','~190 countries','2005–2024','US$ per capita; % of CHE'],
 ['Official development assistance','World Bank WDI (OECD DAC)','~140 recipient countries','2005–2023','US$; per capita; % GNI'],
 ['GDP, GNI, population, rurality, poverty','World Bank WDI','~215 economies','2005–2024','Various'],
 ['Basic water, basic sanitation, open defecation','World Bank WDI (WHO/UNICEF JMP)','~215 economies','2005–2024','% population'],
 ['People requiring interventions against NTDs (SDG 3.3.5)','WHO via UN SDG Global Database','194 countries','2010–2024','Number'],
 ['Malaria incidence per 1,000 at risk (SDG 3.3.3)','WHO via UN SDG Global Database','109 countries','2000–2024','Rate'],
 ['Development assistance for health totals and 2025 cuts','IHME Financing Global Health (Apeagyei et al., 2025)','Global; by source','1990–2030','US$ (2023)'],
 ['US NTD Program countries and budget','USAID NTD Program; KFF; NPR; WHO','32 countries','2006–2025','List; US$'],
 ['Country boundaries','Natural Earth 1:50m','Global','—','Robinson projection']],
 columns=['Indicator','Source','Coverage','Years','Metric'])
add_table(doc,'S1','Data Sources and Indicator Definitions',src,'All data accessed 7 October 2026. WHO Global Health Observatory API returned server errors on the access date; WHO-reported SDG indicators were retrieved from the UN SDG Global Database, which republishes them.',size=8.5)

share=pd.read_csv(f'{R}/cause_by_superregion_share_of_global.csv',index_col=0); glob=pd.read_csv(f'{R}/cause_global_dalys_2023.csv',index_col=0).iloc[:,0]
NAMES={'malaria':'Malaria','other_neglected_tropical_diseases':'Other NTDs','dengue':'Dengue','schistosomiasis':'Schistosomiasis','intestinal_nematode_infections':'Soil-transmitted helminthiases','lymphatic_filariasis':'Lymphatic filariasis','cysticercosis':'Cysticercosis','leishmaniasis':'Leishmaniasis','food_borne_trematodiases':'Food-borne trematodiases','onchocerciasis':'Onchocerciasis','rabies':'Rabies','yellow_fever':'Yellow fever','chagas_disease':'Chagas disease','trachoma':'Trachoma','cystic_echinococcosis':'Cystic echinococcosis','african_trypanosomiasis':'Human African trypanosomiasis','leprosy':'Leprosy','zika_virus':'Zika virus','ebola':'Ebola','guinea_worm_disease':'Guinea worm disease'}
order=[c for c in glob.sort_values(ascending=False).index if c in NAMES]
S2=pd.DataFrame({'Cause':[NAMES[c] for c in order],'Global DALYs':[f0(glob[c]) if glob[c]>=1 else f'{glob[c]:.2f}' for c in order]})
ABR={'Sub-Saharan Africa':'SSA','South Asia':'SA','Southeast Asia, East Asia, and Oceania':'SEAO','Latin America and Caribbean':'LAC','North Africa and Middle East':'NAME','Central Europe, Eastern Europe, and Central Asia':'CEEC','High-income':'HI'}
for s in SR: S2[f'{ABR[s]}, %']=[f1(share.loc[c,s]) for c in order]
add_table(doc,'S2','Global DALYs by Cause and Percentage Distribution Across GBD Super-Regions, 2023',S2,
 'Percentages are each super-region\'s share of that cause\'s global DALYs (rows sum to 100). SSA = Sub-Saharan Africa; SA = South Asia; SEAO = Southeast Asia, East Asia, and Oceania; LAC = Latin America and Caribbean; NAME = North Africa and Middle East; CEEC = Central Europe, Eastern Europe, and Central Asia; HI = high-income. Sums of country-level counts.',size=8)
rate=pd.read_csv(f'{R}/cause_by_superregion_rate_per100k.csv',index_col=0)
S3=pd.DataFrame({'Cause':[NAMES[c] for c in order]})
for s in SR: S3[ABR[s]]=[(f2(rate.loc[c,s]) if rate.loc[c,s]<10 else f1(rate.loc[c,s])) for c in order]
add_table(doc,'S3','All-Age DALY Rate per 100,000 by Cause and GBD Super-Region, 2023',S3,'Rates computed as the sum of country DALY counts divided by World Bank population. Abbreviations as in Table S2.',size=8)

ineq=pd.read_csv(f'{R}/inequality_metrics.csv',index_col=0)
S4=pd.DataFrame({'Outcome':['NTDs excluding malaria','Malaria'],
 'Concentration index [95% CI]':[ci(ineq.loc[k,'CI'],ineq.loc[k,'lo'],ineq.loc[k,'hi'],lambda v: f'{v:.3f}') for k in ineq.index],
 'Theil T':[f'{ineq.loc[k,"Theil"]:.3f}' for k in ineq.index],'Between super-regions, %':[f1(ineq.loc[k,'between_pct']) for k in ineq.index],'Within super-regions, %':[f1(ineq.loc[k,'within_pct']) for k in ineq.index]})
add_table(doc,'S4','Socioeconomic and Geographic Inequality in Age-Standardised DALY Rates, 2023',S4,
 'Concentration index computed on population-weighted age-standardised DALY rates with countries ranked by SDI (negative values = burden concentrated in low-SDI countries); 95% CI from 2,000 bootstrap resamples. Theil T is population-weighted and decomposed into between- and within-super-region components; countries with zero burden are excluded from the malaria Theil index (undefined at zero).',size=9)

sens=pd.read_csv(f'{R}/sensitivity_analyses.csv'); lisa=pd.read_csv(f'{R}/spatial_lisa_country.csv')
s1=sens[sens.analysis.str.startswith('S1')]
S5=pd.DataFrame({'Outcome':s1.outcome,'Spatial weights':s1.specification,"Moran's I":s1.estimate.map(lambda v:f'{v:.3f}'),'p (permutation)':s1.p.map(fp)})
add_table(doc,'S5',"Global Spatial Autocorrelation (Moran's I) Under Alternative Spatial Weight Specifications",S5,
 'Outcome = log(1 + age-standardised DALY rate). 999 permutations (9,999 for the main k = 6 specification). Distance-band weights use inverse distance within 2,500 km. ' +
 f"Local High–High clusters (k = 6, p < .05): NTDs, {K['spatial']['ntd']['n_HH']} countries; malaria, {K['spatial']['mal']['n_HH']} countries (country lists in Table S12).",size=9)

het=pd.read_csv(f'{R}/regression_heterogeneity_external.csv')
S6=pd.DataFrame({'Outcome':het.outcome,'Super-region':het.super_region,'n':het.n,'% change per SD external share [95% CI]':[ci(a,b,c) for a,b,c in zip(het.pct,het.lo,het.hi.clip(upper=9999))]})
add_table(doc,'S6','Super-Region-Specific Associations Between External Share of Health Spending and DALY Rates',S6,
 f"Interaction model (super-region × standardised external share) adjusting for the other predictors in Table 2; HC3 robust CIs; upper limits truncated at 9,999%. Likelihood-ratio test of slope heterogeneity: NTDs χ²({K['het_LR_y_ntd']['df']:.0f}) = {K['het_LR_y_ntd']['LR']:.1f}, p {fp(K['het_LR_y_ntd']['p'])}; malaria χ²({K['het_LR_y_mal']['df']:.0f}) = {K['het_LR_y_mal']['LR']:.1f}, p = {fp(K['het_LR_y_mal']['p'])}. Estimates for South Asia (n = 5) are unstable.",size=8.5)

s2=sens[~sens.analysis.str.startswith('S1')]
S7=pd.DataFrame({'Analysis':s2.analysis.str.replace(r'^S\d ','',regex=True),'Outcome':s2.outcome,'Specification':s2.specification,
 'Estimate [95% CI or UI]':[(ci(a,b,c) if not pd.isna(b) else (f0(a) if abs(a)>100 else f2(a))) for a,b,c in zip(s2.estimate,s2.lo,s2.hi)],'p':s2.p.map(fp),'n':s2.n})
add_table(doc,'S7','Sensitivity Analyses Addressing Anticipated Reviewer Concerns',S7,
 'External-dependence rows report % change in the outcome per 1-SD increase in external share of CHE. Scenario attribution rows report excess annual DALYs (reference scenario; sum of country medians). Economic valuation rows report US$ billion per year. The programme-dependence upper bound sets donor attribution to at least 80% in the 32 US NTD Program countries, reflecting the high donor dependence of mass drug administration.',size=8)

try:
    au=pd.read_csv(f'{R}/audit_checks.csv')
    S8=pd.DataFrame({'Check':au.check,'Value':au.value.map(lambda v: f'{v:,.3f}' if abs(v)<100 else f'{v:,.0f}'),'Result':au.verdict})
    add_table(doc,'S8','Methodological Audit Checks',S8,'See Supplementary Methods for the rationale of each check. VIF = variance inflation factor.',size=8)
except FileNotFoundError: pass

S9=sc.copy(); S9=S9[['scenario_label','outcome','super_region','excess_dalys','lo','hi','pct_of_2023_burden','value_usd_1gdp','value_lo','value_hi']]
S9=pd.DataFrame({'Scenario':S9.scenario_label,'Outcome':S9.outcome,'Super-region':S9.super_region,'Excess DALYs/yr [95% UI]':[ci(a,b,c,f0) for a,b,c in zip(S9.excess_dalys,S9.lo,S9.hi)],
 '% of 2023 burden':S9.pct_of_2023_burden.map(f1),'Value, US$ million [95% UI]':[ci(a/1e6,b/1e6,c/1e6,f0) for a,b,c in zip(S9.value_usd_1gdp,S9.value_lo,S9.value_hi)]})
add_table(doc,'S9','Excess Annual DALYs and Economic Value by Scenario, Outcome, and Super-Region',S9,'Method as in Table 3. LMIC = low- and middle-income countries (all super-regions except high-income).',size=7.5)

g2=gap.copy(); S10=pd.DataFrame({'Scenario':g2.scenario,'Super-region':g2.sr,'Lost external health funds, US$ million':g2.lost_ext_usd.map(lambda v:f0(v/1e6)),'Domestic government health expenditure, US$ million':g2.ghed_total_usd.map(lambda v:f0(v/1e6)),'Increase needed, %':g2.domestic_increase_needed_pct.map(f1)})
add_table(doc,'S10','Domestic Financing Gap by Scenario and Super-Region',S10,'Lost funds = scenario mid-point cut × external health expenditure per capita × population (latest 2019–2023, current US$).',size=8.5)

el=K['elasticity']
S11=pd.DataFrame({'Outcome':['NTDs (14 causes with 2010 estimates)','Malaria'],'Elasticity of DALY rate to CHE per capita [95% CI]':[ci(el['dy_ntd']['beta'],el['dy_ntd']['lo'],el['dy_ntd']['hi'],lambda v:f'{v:.3f}'),ci(el['dy_mal']['beta'],el['dy_mal']['lo'],el['dy_mal']['hi'],lambda v:f'{v:.3f}')],'p':[fp(el['dy_ntd']['p']),fp(el['dy_mal']['p'])],'n':[int(el['dy_ntd']['n']),int(el['dy_mal']['n'])]})
add_table(doc,'S11','First-Difference (2010–2023) Elasticity of DALY Rates With Respect to Health Expenditure',S11,
 'Δlog(age-standardised DALY rate) regressed on Δlog(CHE per capita, current US$), Δlog(GDP per capita, PPP), Δ basic sanitation and super-region indicators; endemic low- and middle-income countries (2010 NTD rate > 10 per 100,000). The null, imprecise elasticity (likely attenuated by exchange-rate noise in current-US$ expenditure and by reverse causation) motivated the transparent attribution-based scenario model rather than an elasticity-based projection.',size=9)

hh=lisa[lisa.lisa_ntd=='High–High'][['location_name','super_region_name']].assign(Outcome='NTDs')
hm=lisa[lisa.lisa_mal=='High–High'][['location_name','super_region_name']].assign(Outcome='Malaria')
S12=pd.concat([hh,hm]).groupby(['Outcome','super_region_name']).location_name.apply(lambda x: ', '.join(sorted(x))).reset_index()
S12.columns=['Outcome','Super-region','Countries in High–High clusters']
add_table(doc,'S12','Countries in Statistically Significant High–High Local Clusters (LISA)',S12,'Local Moran\'s I, k = 6 nearest neighbours, 9,999 permutations, p < .05 (unadjusted). False-discovery-rate adjusted classifications are provided in the country-level data file.',size=8)

miss=pd.read_csv(f'{R}/sensitivity_missingness.csv',index_col=0); ex=pd.read_csv(f'{R}/excluded_countries_regression.csv')
S13=miss.reset_index().rename(columns={'index':'Characteristic'}); S13=S13.map(lambda v: f1(v) if isinstance(v,float) else v)
add_table(doc,'S13','Comparison of Countries Included in and Excluded From Regression Analyses',S13,'Excluded countries (missing one or more covariates): '+'; '.join(ex.location_name)+'.',size=9)

# country-level appendix
cs2=cs.merge(lisa[['iso3','lisa_ntd','lisa_mal']],on='iso3',how='left')
scr=pd.read_csv(f'{R}/scenario_excess_dalys_country.csv'); ref=scr[(scr.scenario=='Reference')&(scr.outcome=='NTDs (excl. malaria)')].set_index('iso3')
cs2=cs2.sort_values(['sr','location_name'])
S14=pd.DataFrame({'Country':cs2.location_name,'Super-region':cs2.sr.map(ABR),'NTD ASR [95% UI]':[f1(v) for v in cs2.daly_asr_ntd_excl_malaria],
 'Malaria ASR [95% UI]':[f1(v) for v in cs2.daly_asr_malaria],'NTD+malaria % change 2010–23 [95% UI]':[ci(a,b,c) for a,b,c in zip(cs2.pc_asr_ntdm_2010_2023,cs2.pc_asr_ntdm_lo,cs2.pc_asr_ntdm_hi)],
 'SDI':cs2.sdi_2023.map(f2),'External share of CHE, %':cs2.ext_pct_che_latest.map(f1),'LISA (NTD)':cs2.lisa_ntd.fillna('—'),
 'Excess NTD DALYs/yr, reference':cs2.iso3.map(ref.excess_dalys).map(f0)})
S14.columns=['Country','Super-region','NTD ASR','Malaria ASR','NTD + malaria ASR % change 2010–2023 [95% UI]','SDI','External share of CHE, %','LISA cluster (NTD)','Excess NTD DALYs/yr (reference)']
add_table(doc,'S14','Country-Level Burden, Change, Development, Donor Dependence, Spatial Cluster, and Projected Excess DALYs (204 Countries)',S14,
 'ASR = age-standardised DALY rate per 100,000, 2023. Excess DALYs not estimated for high-income countries or where external share is unavailable (—). Abbreviations as in Table S2.',size=7)
doc.save('tables/Supplementary_Tables_APA.docx')
print('tables written')
