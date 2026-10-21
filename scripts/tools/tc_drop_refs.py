import sys,re; sys.path.insert(0,'scripts/tools')
from tc_lib import *
from lxml import etree
P='manuscript/source/unpacked/word/document.xml'
tree=etree.parse(P); body=tree.find('.//w:body',ns)
starts=[l.strip() for l in open(sys.argv[1]) if l.strip()]
def dtext(p): return ''.join(t.text or '' for r in p if r.tag==q('r') for t in r.findall('w:t',ns))
n=0
for s in starts:
    hits=[p for p in body.iter(q('p')) if dtext(p).startswith(s[:60])]
    if len(hits)!=1: print('skip',len(hits),s[:50]); continue
    delete_par(hits[0]); n+=1
tree.write(P,xml_declaration=True,encoding='UTF-8',standalone=True); print('deleted',n)
