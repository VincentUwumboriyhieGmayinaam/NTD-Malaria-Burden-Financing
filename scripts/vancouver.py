"""Convert APA 7 reference strings to Lancet (Vancouver) style and parse author–year citations.

Lancet rules applied: up to six authors listed as 'Surname Initials'; seven or more -> first three + 'et al';
journal names abbreviated (Index Medicus); 'Journal Year; vol: pages.' with an en rule and shortened page ranges;
books give edition, city, publisher and year; online material gives the URL and access date."""
import re

JABBR = {
 'The Lancet': 'Lancet', 'The Lancet Global Health': 'Lancet Glob Health', 'PLoS ONE': 'PLoS One', 'PLOS ONE': 'PLoS One',
 'PLOS Neglected Tropical Diseases': 'PLoS Negl Trop Dis', 'PLoS Neglected Tropical Diseases': 'PLoS Negl Trop Dis',
 'PLOS Medicine': 'PLoS Med', 'BMC Public Health': 'BMC Public Health', 'BMC Infectious Diseases': 'BMC Infect Dis',
 'Malaria Journal': 'Malar J', 'Nature': 'Nature', 'Nature Communications': 'Nat Commun', 'JAMA Internal Medicine': 'JAMA Intern Med',
 'Health Economics': 'Health Econ', 'Journal of Health Economics': 'J Health Econ', 'Review of Economics and Statistics': 'Rev Econ Stat',
 'Journal of the Royal Statistical Society Series B: Statistical Methodology': 'J R Stat Soc Series B Stat Methodol',
 'Geographical Analysis': 'Geogr Anal', 'Political Science Research and Methods': 'Polit Sci Res Methods', 'Political Analysis': 'Polit Anal',
 'Medical Decision Making': 'Med Decis Making', 'The Stata Journal': 'Stata J', 'Journal of Econometrics': 'J Econom',
 'Journal of Epidemiology and Global Health': 'J Epidemiol Glob Health', 'International Health': 'Int Health',
 'Journal of Travel Medicine': 'J Travel Med', 'Scientific Reports': 'Sci Rep', 'Social Science & Medicine': 'Soc Sci Med',
 'Biometrika': 'Biometrika', 'Annual Review of Public Health': 'Annu Rev Public Health', 'Econometrica': 'Econometrica',
 'Health Policy and Planning': 'Health Policy Plan', 'Review of Regional Studies': 'Rev Reg Stud', 'Global Public Health': 'Glob Public Health',
 'American Journal of Political Science': 'Am J Pol Sci', 'Annals of the American Association of Geographers': 'Ann Am Assoc Geogr',
 'BMJ': 'BMJ', 'Bulletin of the World Health Organization': 'Bull World Health Organ', 'Ecography': 'Ecography',
 'Empirical Economics': 'Empir Econ', 'ISPRS International Journal of Geo-Information': 'ISPRS Int J Geoinf',
 'Information Sciences': 'Inf Sci', 'Journal of Advanced Research': 'J Adv Res', 'Journal of Statistical Software': 'J Stat Softw',
 'Machine Learning': 'Mach Learn', 'Quality & Quantity': 'Qual Quant', 'Statistics in Medicine': 'Stat Med',
 'The Journal of Politics': 'J Polit', 'The Review of Economic Studies': 'Rev Econ Stud'}

ACCESS = 'accessed Oct 21, 2026'
# Non-journal items: (first author/organisation, year) -> Vancouver text
SPECIAL = {
 ('Theil', '1967'): 'Theil H. Economics and information theory. Amsterdam: North-Holland, 1967.',
 ('Wooldridge', '2010'): 'Wooldridge JM. Econometric analysis of cross section and panel data, 2nd edn. Cambridge, MA: MIT Press, 2010.',
 ('Anselin', '1988'): 'Anselin L. Spatial econometrics: methods and models. Dordrecht: Kluwer Academic Publishers, 1988.',
 ('Elhorst', '2014'): 'Elhorst JP. Spatial econometrics: from cross-sectional data to spatial panels. Heidelberg: Springer, 2014.',
 ('Fitzpatrick', '2017'): 'Fitzpatrick C, Nwankwo U, Lenk E, de Vlas SJ, Bundy DAP. An investment case for ending neglected tropical diseases. In: Holmes KK, Bertozzi S, Bloom BR, Jha P, eds. Major infectious diseases, 3rd edn. Washington, DC: World Bank, 2017: 411–31.',
 ('Greene', '2018'): 'Greene WH. Econometric analysis, 8th edn. New York, NY: Pearson, 2018.',
 ('Ke', '2017'): 'Ke G, Meng Q, Finley T, et al. LightGBM: a highly efficient gradient boosting decision tree. Adv Neural Inf Process Syst 2017; 30: 3146–54.',
 ('LeSage', '2009'): 'LeSage J, Pace RK. Introduction to spatial econometrics. Boca Raton, FL: Chapman & Hall/CRC, 2009.',
 ('Lundberg', '2017'): 'Lundberg SM, Lee S-I. A unified approach to interpreting model predictions. Adv Neural Inf Process Syst 2017; 30: 4765–74.',
 ('Natural Earth', 'n.d.'): f'Natural Earth. Admin 0 – countries, 1:50m cultural vectors. https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/ (accessed Oct 7, 2026).',
 ('O’Donnell', '2008'): 'O’Donnell O, van Doorslaer E, Wagstaff A, Lindelow M. Analyzing health equity using household survey data: a guide to techniques and their implementation. Washington, DC: World Bank, 2008.',
 ('Rubin', '1987'): 'Rubin DB. Multiple imputation for nonresponse in surveys. New York, NY: Wiley, 1987.',
 ('United Nations Statistics Division', 'n.d.'): 'United Nations Statistics Division. Global SDG Indicators Database. https://unstats.un.org/sdgs/dataportal (accessed Oct 7, 2026).',
 ('World Health Organization', 'n.d.'): 'WHO. Global Health Expenditure Database. https://apps.who.int/nha/database (accessed Oct 7, 2026).',
 ('World Bank', 'n.d.'): 'World Bank. World Development Indicators. https://databank.worldbank.org/source/world-development-indicators (accessed Oct 7, 2026).',
 ('World Health Organization', '2020'): 'WHO. Ending the neglect to attain the Sustainable Development Goals: a road map for neglected tropical diseases 2021–2030. Geneva: World Health Organization, 2020.',
 ('World Health Organization', '2025a'): f'WHO. Global report on neglected tropical diseases 2025. Geneva: World Health Organization, 2025. https://www.who.int/publications/i/item/9789240114043 ({ACCESS}).',
 ('World Health Organization', '2025b'): f'WHO. World malaria report 2025: addressing the threat of antimalarial drug resistance. Geneva: World Health Organization, 2025. https://www.who.int/publications/i/item/9789240117822 ({ACCESS}).',
 ('World Health Organization Regional Office for Africa', '2025'): f'WHO Regional Office for Africa. Sustaining momentum in NTD programmes amidst a reduced funding landscape: a regional assessment. Brazzaville: WHO Regional Office for Africa, 2025. https://espen.afro.who.int/sites/default/files/content/document/Sustaining%20Momentum%20in%20NTD%20Programmes%20Amidst%20a%20Reduced%20Funding%20Landscape_A%20Regional%20Assessment_0.pdf ({ACCESS}).',
}

INIT = re.compile(r'^(?:[A-Z][a-z]?\.(?:-[A-Z]\.)?\s?)+$')

def split_apa(r):
    m = re.match(r'^(?P<auth>.+?) \((?P<year>\d{4}[a-z]?|n\.d\.)\)\. (?P<rest>.+)$', r.strip())
    return m.group('auth'), m.group('year'), m.group('rest')

def authors(auth):
    a = auth.replace('&', '').replace('…', ',')
    toks = [t.strip() for t in a.split(',') if t.strip()]
    out, i = [], 0
    while i < len(toks):
        if i + 1 < len(toks) and INIT.match(toks[i + 1]):
            ini = toks[i + 1].replace('.', '').replace(' ', '')
            out.append(f'{toks[i]} {ini}'); i += 2
        else:
            out.append(toks[i]); i += 1
    return out

def first_key(auth):
    return authors(auth)[0].rsplit(' ', 1)[0] if INIT.match(auth.split(',')[1].strip() if ',' in auth else 'x') else authors(auth)[0]

def key(r):
    auth, year, _ = split_apa(r)
    if ',' in auth and INIT.match(auth.split(',')[1].strip() + ''):
        return auth.split(',')[0].strip(), year
    return auth.rstrip('.').strip(), year

def pages(p):
    p = p.replace('Article ', '').strip()
    m = re.match(r'^(e?)(\d+)[–-](e?)(\d+)$', p)
    if not m: return p
    pre, a, _, b = m.groups()
    if len(a) == len(b):
        k = 0
        while k < len(a) - 2 and a[k] == b[k]: k += 1
        b = b[k:]
    return f'{pre}{a}–{b}'

def lower_after_colon(t):
    return re.sub(r'(: |—)([A-Z])(?=[a-z]|\s)', lambda m: m.group(1) + m.group(2).lower(), t)

def vancouver(r):
    k = key(r)
    if k in SPECIAL: return SPECIAL[k]
    auth, year, rest = split_apa(r)
    m = re.search(r'[.?]\s(?P<j>[^.]+?), (?P<v>\d+)(?:\((?P<i>[^)]*)\))?, (?P<p>(?:Article )?[^,]+?)\.(?:\s(?P<doi>https?://\S+))?\s*$', rest)
    if not m: raise ValueError('cannot parse: ' + r[:90])
    title = rest[:m.start() + 1].strip()
    title = lower_after_colon(title.rstrip('.'))
    au = [a.rstrip('.') for a in authors(auth)]
    if len(au) >= 7: au = au[:3] + ['et al']
    j = JABBR.get(m.group('j').strip(), m.group('j').strip())
    yr = re.sub(r'[a-z]$', '', year)
    end = '' if title.endswith(('?', '!')) else '.'
    return f"{', '.join(au)}. {title}{end} {j} {yr}; {m.group('v')}: {pages(m.group('p'))}."

# ---------- in-text citations ----------
ALIAS = {'WHO': 'World Health Organization', 'World Health Organization [WHO]': 'World Health Organization'}
def cite_keys(s):
    """'Akachi & Atun, 2011; WHO, 2025a, 2025b' -> [('Akachi','2011'),('World Health Organization','2025a'),...]"""
    out = []
    for part in s.split(';'):
        part = part.strip()
        m = re.match(r'^(?P<n>.+?),\s*(?P<y>(?:\d{4}[a-z]?|n\.d\.)(?:,\s*(?:\d{4}[a-z]?|n\.d\.))*)$', part)
        if not m: return None
        n = m.group('n').strip(); n = ALIAS.get(n, n)
        n = re.sub(r'\s+et al\.$', '', n); n = n.split(' & ')[0].strip()
        n = re.sub(r'^(?:[A-Z]\.\s?)+', '', n).strip()      # 'A. F. da Silva' -> 'da Silva'
        for y in re.split(r',\s*', m.group('y')): out.append((n, y))
    return out

def fmt_nums(ns):
    ns = sorted(set(ns)); out = []; i = 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1: j += 1
        out.append(f'{ns[i]}–{ns[j]}' if j - i >= 2 else (f'{ns[i]},{ns[j]}' if j == i + 1 else f'{ns[i]}'))
        i = j + 1
    return ','.join(out)

CITE_RE = re.compile(r' \(((?:[^()]*?(?:\d{4}[a-z]?|n\.d\.))(?:; [^()]*?(?:\d{4}[a-z]?|n\.d\.))*)\)')
