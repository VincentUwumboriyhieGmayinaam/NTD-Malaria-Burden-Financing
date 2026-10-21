"""Main tables as a separate, editable Word file in Lancet submission format.

Lancet table rules applied: all grid lines visible; no merged cells (group labels sit in the first column of their own row);
empty cells hold two mid-dots (··); top-left cell left empty; no multi-part tables; mid-line decimal points; minus signs;
95% intervals as (lower to upper); no soft returns; concise sentence-case titles; abbreviations spelt out in footnotes."""
import json, re
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

T = {t['id']: t for t in json.load(open('results/tables.json'))}
TITLES = {
 'Table 1': 'Burden of NTDs and malaria by GBD super-region, 2023',
 'Table 2': 'Spatial autocorrelation and socioeconomic inequality in age-standardised DALY rates, 2023',
 'Table 3': 'Association between the external share of health expenditure and age-standardised DALY rates, by estimator',
 'Table 4': 'Projected excess annual DALYs under development-assistance cut scenarios in low-income and middle-income countries'}
ABBR = {
 'Table 1': 'NTD=neglected tropical disease. DALY=disability-adjusted life-year. GBD=Global Burden of Disease. UI=uncertainty interval. WDI=World Development Indicators. IHME=Institute for Health Metrics and Evaluation.',
 'Table 2': 'NTD=neglected tropical disease. DALY=disability-adjusted life-year. LISA=local indicators of spatial association. SDI=Socio-demographic Index. GBD=Global Burden of Disease.',
 'Table 3': 'NTD=neglected tropical disease. DALY=disability-adjusted life-year. OLS=ordinary least squares. FE=fixed effects. SE=standard error. CRE=correlated random effects. SAR=spatial autoregressive model. SEM=spatial error model. LDI=lag-distributed income. UHC=universal health coverage. LMIC=low-income and middle-income country.',
 'Table 4': 'NTD=neglected tropical disease. DALY=disability-adjusted life-year. UI=uncertainty interval. GDP=gross domestic product. GBD=Global Burden of Disease.'}

def lancet(s):
    s = str(s).strip()
    if s in ('—', '–', '-', ''): return '··'
    s = re.sub(r'\[([^\[\],]+), ([^\[\]]+)\]', r'(\1 to \2)', s)          # [a, b] -> (a to b)
    s = re.sub(r'(^|[\s(=;/])-(?=\d)', r'\1−', s)                          # minus sign
    s = re.sub(r'(?<![\w/])(\d+)\.(\d+)', r'\1·\2', s)                     # mid-line decimal
    s = s.replace('\n', ' ')
    return s

def borders(tbl):
    tblPr = tbl._tbl.tblPr; b = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4'); e.set(qn('w:space'), '0'); e.set(qn('w:color'), '000000'); b.append(e)
    tblPr.append(b)

doc = Document()
st = doc.styles['Normal']; st.font.name = 'Times New Roman'; st.font.size = Pt(10)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
sec = doc.sections[0]; sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
for m in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'): setattr(sec, m, Cm(1.8))
for n, tid in enumerate(['Table 1', 'Table 2', 'Table 3', 'Table 4']):
    t = T[tid]
    if n: doc.add_page_break()
    p = doc.add_paragraph(); r = p.add_run(f'{tid}: {TITLES[tid]}'); r.bold = True
    cols = [''] + [lancet(c) for c in t['cols'][1:]]                         # top-left cell empty
    tbl = doc.add_table(rows=1, cols=len(cols)); borders(tbl)
    for i, c in enumerate(cols):
        cell = tbl.rows[0].cells[i]; cell.text = ''; run = cell.paragraphs[0].add_run(c); run.bold = True
    for row in t['rows']:
        vals = [lancet(row['group'])] + [''] * (len(cols) - 1) if isinstance(row, dict) else [lancet(v) for v in row]
        cells = tbl.add_row().cells
        for i, v in enumerate(vals):
            cells[i].text = ''; run = cells[i].paragraphs[0].add_run(v)
            if isinstance(row, dict): run.italic = True
    note = lancet(t.get('note', '')).replace('··', '')
    doc.add_paragraph(ABBR[tid] + (' ' + note if note else ''))
doc.save('manuscript/Tables_Main_Lancet.docx'); print('ok')
