"""Assemble annual country panel (2005-2023) of age-standardised NTD&M and malaria DALY rates from saved GBD trend calls."""
import json,io,glob,pandas as pd
D='/root/.claude/projects/-home-claude/1a0ef615-1d0c-5aca-a60a-c54f84840f32/tool-results'
fr=[]
for f in sorted(glob.glob(f'{D}/mcp-GBD_2023_Collab-get_multi_location_trend-*.txt')):
    r=json.load(open(f))['result']
    if r.lstrip().startswith('{'): continue
    t=r.split('\n'); body=[l for l in t[1:] if l and l[0].isdigit()]
    d=pd.read_csv(io.StringIO('\n'.join([t[0]]+body)))
    if d.location_id.nunique()<=8: continue      # super-region calls
    fr.append(d[['location_id','location_name','year','cause_name','rate_age_std_combined','rate_combined','count_combined','count_lower_combined','count_upper_combined']])
p=pd.concat(fr).drop_duplicates(['location_id','year','cause_name'])
p.to_csv('data/raw/gbd/country_panel_2005_2023_long.csv',index=False)
w=p.pivot_table(index=['location_id','location_name','year'],columns='cause_name',values=['rate_age_std_combined','count_combined']).reset_index()
w.columns=['location_id','location_name','year','n_malaria','n_ntdm','asr_malaria','asr_ntdm']
w['asr_ntd']=w.asr_ntdm-w.asr_malaria; w['n_ntd']=w.n_ntdm-w.n_malaria
w.to_csv('data/processed/gbd_country_panel_2005_2023.csv',index=False)
c=w.groupby('location_id').year.nunique()
print(w.shape,'countries',w.location_id.nunique(),'complete 19y:',(c==19).sum()); print(w.isna().sum().to_dict())
