"""Minimal tracked-change helpers for word/document.xml (w:ins / w:del)."""
import copy, itertools
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XML = 'http://www.w3.org/XML/1998/namespace'
ns = {'w': W}
def q(t): return f'{{{W}}}{t}'
AUTHOR = 'Claude'; DATE = '2026-10-21T09:00:00Z'; _id = itertools.count(9000)

def _mark(tag):
    e = etree.Element(q(tag)); e.set(q('id'), str(next(_id))); e.set(q('author'), AUTHOR); e.set(q('date'), DATE); return e

def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))

def _runs(p): return [r for r in p if r.tag == q('r')]

def _rtext(r): return ''.join(t.text or '' for t in r.findall('w:t', ns))

def _mkrun(text, rpr=None, deleted=False):
    r = etree.Element(q('r'))
    if rpr is not None: r.append(copy.deepcopy(rpr))
    t = etree.SubElement(r, q('delText' if deleted else 't')); t.text = text
    t.set(f'{{{XML}}}space', 'preserve'); return r

def _split(p, run, k):
    """split run at char k -> (left, right); both remain in p. Only for simple text runs."""
    txt = _rtext(run); rpr = run.find('w:rPr', ns)
    a = _mkrun(txt[:k], rpr); b = _mkrun(txt[k:], rpr)
    i = list(p).index(run); p.remove(run); p.insert(i, b); p.insert(i, a); return a, b

def replace(p, old, new, nth=0):
    """Track-change replace text `old` (may span runs) with `new` in paragraph p. new='' -> deletion only."""
    full = ''.join(_rtext(r) for r in _runs(p)); pos = -1
    for _ in range(nth + 1):
        pos = full.find(old, pos + 1)
        if pos < 0: raise ValueError(f'not found: {old[:60]!r} in {full[:80]!r}')
    end = pos + len(old)
    # map runs to offsets (only direct text runs)
    off = 0; spans = []
    for r in _runs(p):
        tx = _rtext(r); spans.append((r, off, off + len(tx))); off += len(tx)
    if off != len(full):  # text in hyperlinks/fields: fall back to runs only
        full = ''.join(_rtext(r) for r in _runs(p)); pos = full.find(old); end = pos + len(old)
        if pos < 0: raise ValueError('text outside simple runs: ' + old[:50])
    # split at boundaries
    for r, s, e in list(spans):
        if s < pos < e:
            _split(p, r, pos - s)
    off = 0; spans = []
    for r in _runs(p):
        tx = _rtext(r); spans.append((r, off, off + len(tx))); off += len(tx)
    for r, s, e in list(spans):
        if s < end < e: _split(p, r, end - s)
    off = 0; target = []
    for r in _runs(p):
        tx = _rtext(r)
        if off >= pos and off + len(tx) <= end and len(tx): target.append(r)
        off += len(tx)
    if not target:  # pure insertion at pos
        raise ValueError('empty target')
    rpr = target[0].find('w:rPr', ns)
    first_idx = list(p).index(target[0])
    if old:
        d = _mark('del'); p.insert(first_idx, d)
        for r in target:
            p.remove(r)
            for t in r.findall('w:t', ns): t.tag = q('delText')
            for t in r.findall('w:instrText', ns): t.tag = q('delInstrText')
            d.append(r)
        anchor = d
    if new:
        ins = _mark('ins'); ins.append(_mkrun(new, rpr))
        anchor.addnext(ins)
    return p

def insert_after_text(p, after, new):
    """Insert `new` immediately after the text `after` (tracked)."""
    full = ''.join(_rtext(r) for r in _runs(p)); pos = full.find(after)
    if pos < 0: raise ValueError('anchor not found: ' + after[:60])
    end = pos + len(after); off = 0
    for r in _runs(p):
        tx = _rtext(r)
        if off < end < off + len(tx): _split(p, r, end - off); break
        off += len(tx)
    off = 0
    for r in _runs(p):
        tx = _rtext(r); off += len(tx)
        if off == end:
            ins = _mark('ins'); ins.append(_mkrun(new, r.find('w:rPr', ns))); r.addnext(ins); return p
    raise ValueError('boundary not found')

def new_par_after(anchor, text, template=None, runs=None):
    """Insert a tracked new paragraph after `anchor`, formatted like `template` (default anchor).
    runs: optional list of (text, bold, italic)."""
    tpl = template if template is not None else anchor
    p = etree.Element(q('p'))
    ppr = tpl.find('w:pPr', ns)
    ppr = copy.deepcopy(ppr) if ppr is not None else etree.Element(q('pPr'))
    for x in ppr.findall('w:rPr', ns): ppr.remove(x)
    rp = etree.SubElement(ppr, q('rPr')); rp.append(_mark('ins'))
    p.append(ppr)
    tr = _runs(tpl); base = tr[-1].find('w:rPr', ns) if tr else None
    ins = _mark('ins'); p.append(ins)
    for (tx, b, it) in (runs or [(text, None, None)]):
        rpr = copy.deepcopy(base) if base is not None else etree.Element(q('rPr'))
        for tag, val in (('b', b), ('i', it)):
            if val is None: continue
            for x in rpr.findall(f'w:{tag}', ns) + rpr.findall(f'w:{tag}Cs', ns): rpr.remove(x)
            if val: rpr.insert(0, etree.Element(q(tag)))
        ins.append(_mkrun(tx, rpr))
    anchor.addnext(p); return p

def delete_par(p):
    ppr = p.find('w:pPr', ns)
    if ppr is None: ppr = etree.Element(q('pPr')); p.insert(0, ppr)
    rp = ppr.find('w:rPr', ns)
    if rp is None: rp = etree.SubElement(ppr, q('rPr'))
    rp.insert(0, _mark('del'))
    for parent in [p] + p.findall('w:hyperlink', ns) + p.findall('w:smartTag', ns):
        for r in [r for r in parent if r.tag == q('r')]:
            d = _mark('del'); r.addprevious(d); parent.remove(r)
            for t in r.findall('w:t', ns): t.tag = q('delText')
            for t in r.findall('w:instrText', ns): t.tag = q('delInstrText')
            d.append(r)
