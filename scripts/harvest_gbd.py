"""Harvest every saved GBD 2023 MCP tool result into tidy CSVs (data/raw/gbd/)."""
import json,io,glob,os,re,pandas as pd
D='/root/.claude/projects/-home-claude/1a0ef615-1d0c-5aca-a60a-c54f84840f32/tool-results'
out='data/raw/gbd'; os.makedirs(out,exist_ok=True)
slug=lambda s: re.sub(r'[^a-z0-9]+','_',str(s).lower()).strip('_')
groups={}
for f in sorted(glob.glob(f'{D}/mcp-GBD_2023_Collab-*.txt')):
    tool=os.path.basename(f).split('-')[2]
    r=json.load(open(f))['result']
    if r.lstrip().startswith('{'):
        j=json.loads(r); df=pd.DataFrame(j.get('rows') or j.get('data') or [])
    else: df=pd.read_csv(io.StringIO(r))
    if df.empty: continue
    if tool=='get_top_locations':
        key=f"country__{slug(df.cause_name[0])}__{df.measure[0]}__{df.year[0]}"
    elif tool=='get_sdi': key='country__sdi'
    elif tool=='get_covariate': key=f"country__cov_{slug(df.covariate_name[0])}"
    elif tool=='get_percent_change': key=f"country_pctchange__{slug(df.cause_name[0])}__{df.year_start[0]}_{df.year_end[0]}"
    elif tool=='get_multi_location_trend': key=f"superregion_trend__{slug(df.cause_name[0])}__{df.measure[0]}"
    else: key=f"{tool}__{os.path.basename(f)[:-4]}"
    groups.setdefault(key,[]).append(df)
for k,v in sorted(groups.items()):
    df=pd.concat(v).drop_duplicates()
    df.to_csv(f'{out}/{k}.csv',index=False); print(df.shape,k)
