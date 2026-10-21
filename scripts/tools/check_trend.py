import json,io,sys,pandas as pd
r=json.load(open(sys.argv[1]))['result']
txt=r.split('\n'); body=[l for l in txt if l and l[0].isdigit()]
df=pd.read_csv(io.StringIO('\n'.join([txt[0]]+body)))
print(df.shape, df.location_name.nunique(), sorted(df.year.unique()), df.groupby('location_name').size().value_counts().to_dict())
print([l for l in txt if l and not l[0].isdigit()][1:3])
