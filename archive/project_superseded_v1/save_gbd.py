import json,io,sys,pandas as pd
src,dst=sys.argv[1],sys.argv[2]
r=json.load(open(src))['result']
df=pd.read_csv(io.StringIO(r))
df.to_csv(dst,index=False)
print(dst,df.shape, df.location_name.nunique())
print(df[['location_name','super_region_name','rate_combined','count_combined']].head(3).to_string())
