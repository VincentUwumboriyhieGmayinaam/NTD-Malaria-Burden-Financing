"""Render the appendix twice: pass 1 locates each heading's page in the PDF, pass 2 writes the page numbers into the contents."""
import json, subprocess, glob, os, re
SK=glob.glob('/root/.claude/skills/synced/*/docx')[0]
def render():
    subprocess.run(['node','scripts/render_appendix.js'],check=True)
    subprocess.run(['python3',f'{SK}/scripts/office/soffice.py','--headless','--convert-to','pdf','--outdir','manuscript','manuscript/Supplementary_Appendix.docx'],check=True,capture_output=True)
if os.path.exists('results/appendix_toc_pages.json'): os.remove('results/appendix_toc_pages.json')
render()
keys=json.load(open('results/appendix_toc_keys.json'))
n=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo','manuscript/Supplementary_Appendix.pdf'],capture_output=True,text=True).stdout).group(1))
pages=[subprocess.run(['pdftotext','-layout','-f',str(i),'-l',str(i),'manuscript/Supplementary_Appendix.pdf','-'],capture_output=True,text=True).stdout for i in range(1,n+1)]
# skip contents pages: body starts at the page holding the checklist heading after the contents
start=next(i for i,t in enumerate(pages) if i>0 and re.search(r'^\s*1\. Reporting checklists: GATHER and STROBE\s*$',t,re.M) and '....' not in t)
PG={}
for k in keys:
    tail=r'\s*$' if k.startswith('Table') else (r':' if k.startswith('Figure') else r'')
    pat=re.compile(r'^\s*'+re.escape(k)+tail,re.M)
    for i in range(start,n):
        if pat.search(pages[i]): PG[k]=i+1; break
missing=[k for k in keys if k not in PG]; print('pages', n, 'located', len(PG), 'missing', missing)
json.dump(PG,open('results/appendix_toc_pages.json','w'))
render()
