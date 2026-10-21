"""Parse browser-relayed World Bank payloads into data/raw/wb/ (long format) + country metadata."""
import json,glob,os,io,pandas as pd
D='/root/.claude/projects/-home-claude/1a0ef615-1d0c-5aca-a60a-c54f84840f32/tool-results'
os.makedirs('data/raw/wb',exist_ok=True); frames={}; meta=None
for f in sorted(glob.glob(f'{D}/mcp-remote-devices-Claude_Browser__javascript_tool-*.txt')):
    a=json.load(open(f)); t=a[0]['text']
    try:
        s,_=json.JSONDecoder().raw_decode(t.strip()); s=json.loads(s) if isinstance(s,str) else s
    except Exception as e: print('skip (truncated?)',os.path.basename(f),e); continue
    if not isinstance(s,dict) or 'd' not in s: continue
    if s.get('meta'): meta=s['meta']
    for ind,txt in s['d'].items():
        if not txt: continue
        df=pd.read_csv(io.StringIO(txt),sep='|',header=None,names=['iso3','year','value']); df['indicator']=ind
        frames[ind]=df
if meta: pd.read_csv(io.StringIO(meta),sep='|').to_csv('data/raw/wb/wb_country_metadata.csv',index=False)
for k,v in frames.items(): print(k,v.shape, v.year.min(), v.year.max())
if frames: pd.concat(frames.values()).to_csv('data/raw/wb/wdi_long_2005_2024.csv',index=False)
