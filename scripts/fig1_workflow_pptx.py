"""Figure 1 as an editable PowerPoint flow diagram (Lancet: study profiles/flow diagrams supplied as editable .ppt/.doc)."""
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree
W,H=760,768; S=12000  # EMU per layout unit
prs=Presentation(); prs.slide_width=Emu(W*S); prs.slide_height=Emu(H*S)
sl=prs.slides.add_slide(prs.slide_layouts[6])
INK=RGBColor(0x0b,0x0b,0x0b); INK2=RGBColor(0x52,0x51,0x4e); BLUE=RGBColor(0x2a,0x78,0xd6); BL=RGBColor(0xb7,0xd3,0xf6); AX=RGBColor(0xc3,0xc2,0xb7); MU=RGBColor(0x89,0x87,0x81)
def box(x,y,w,h,lines,main=False,center=False):
    s=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Emu(x*S),Emu(y*S),Emu(w*S),Emu(h*S)); s.adjustments[0]=min(0.5,8/min(w,h))
    s.fill.solid(); s.fill.fore_color.rgb=BL if main else RGBColor(255,255,255); s.line.color.rgb=BLUE if main else AX; s.line.width=Pt(1.1 if main else 0.7); s.shadow.inherit=False
    tf=s.text_frame; tf.word_wrap=True; tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    for m in ('margin_left','margin_right'): setattr(tf,m,Emu(10*S))
    tf.margin_top=tf.margin_bottom=Emu(3*S)
    for i,(txt,bold) in enumerate(lines):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.alignment=PP_ALIGN.CENTER if center else PP_ALIGN.LEFT
        r=p.add_run(); r.text=txt; r.font.name='Arial'; r.font.size=Pt(7 if bold else 6.2); r.font.bold=bold; r.font.color.rgb=INK if bold else INK2
    return s
def label(x,y,txt):
    t=sl.shapes.add_textbox(Emu(x*S),Emu((y-14)*S),Emu(300*S),Emu(18*S)); r=t.text_frame.paragraphs[0].add_run(); r.text=txt; r.font.name='Arial'; r.font.size=Pt(7.5); r.font.bold=True; r.font.color.rgb=INK
def arrow(x1,y1,x2,y2):
    c=sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Emu(x1*S),Emu(y1*S),Emu(x2*S),Emu(y2*S)); c.line.color.rgb=MU; c.line.width=Pt(0.7)
    ln=c.line._get_or_add_ln(); ln.append(etree.SubElement(ln,qn('a:tailEnd'),{'type':'triangle','w':'sm','len':'sm'}))
label(24,40,'Data sources')
src=[('GBD 2023','DALYs · SDI · UHC · LDI'),('World Bank WDI','Health finance · WASH'),('WHO via UN SDG','SDG 3.3.5 · 3.3.3'),('IHME FGH','DAH 2024–2025'),('Natural Earth','Admin-0 boundaries')]
for i,(a,b) in enumerate(src):
    x=24+144*i; box(x,56,136,56,[(a,True),(b,False)],center=True); arrow(x+68,112,x+68,148)
for y,a,b in [(148,'1. Data acquisition','Programmatic download, raw files archived; truncated calls re-queried; completeness checked per country-year'),
              (212,'2. Harmonisation and linkage','ISO3 and GBD location IDs; GBD super-region and region assignment; 204 countries × 2005–2023 panel'),
              (276,'3. Quality control and missing data','Interior interpolation, carry-forward ≤2 years, every fill flagged; complete-case, balanced-panel and MICE (m = 20) checks')]:
    box(24,y,712,48,[(a,True),(b,False)])
arrow(380,196,380,212); arrow(380,260,380,276)
for x,a,ls in [(24,'4. Descriptive and inequality',['Rates and trends, 1990–2023','Concentration index and SII ranked by SDI','Theil T: super-region, region, country']),
               (268,'5. Spatial analysis',["Global Moran's I, KNN k = 6",'LISA, 9 999 permutations','Benjamini–Hochberg FDR, q<0.05']),
               (512,'6. Panel econometrics',['7 estimators, 6 assumption tests','Two-way FE, Driscoll–Kraay SE; Mundlak CRE','153 LMICs, 2007–2022'])]:
    box(x,360,224,96,[(a,True)]+[(l,False) for l in ls]); arrow(x+112,324,x+112,360)
box(268,480,468,80,[('7. Robustness and heterogeneity',True),('Spatial panel SAR and SEM (two-way FE) · GWR and MGWR · random forest, LightGBM, elastic net',False),('Leave-country-out, spatial-block and temporal validation; SHAP attribution',False)])
box(268,584,468,80,[('8. Funding-cut scenarios',True),('Accounting and econometric models · 4 000 Monte Carlo draws',False),('Economic value at 0.5–3 × GDP per capita · domestic financing gap',False)])
arrow(380,456,380,480); arrow(624,456,624,480); arrow(502,560,502,584)
box(24,688,712,56,[('Outputs',True),('Tables 1–4 and S1–S26 · Figures 1–8 and S1–S4 · archived code and processed data',False)],main=True)
arrow(136,456,136,688); arrow(502,664,502,688)
prs.save('figures/main/Figure1_workflow_editable.pptx'); print('ok')
