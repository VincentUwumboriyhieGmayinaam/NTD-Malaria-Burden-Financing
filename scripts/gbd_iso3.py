"""Crosswalk GBD 2023 national locations -> ISO3 (via Natural Earth names + manual fixes)."""
import pandas as pd, geopandas as gpd, unicodedata
g=pd.read_csv('data/raw/gbd/country__neglected_tropical_diseases_and_malaria__dalys__2023.csv')[['location_id','location_name','super_region_name']]
ne=gpd.read_file('data/raw/geo/ne_50m_admin_0_countries.geojson')
norm=lambda s: unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower().replace('&','and').strip()
lk={}
for _,r in ne.iterrows():
    iso=r['ISO_A3'] if r['ISO_A3']!='-99' else r['ADM0_A3']
    for c in ['ADMIN','NAME','NAME_LONG','FORMAL_EN','NAME_SORT','GEOUNIT','SOVEREIGNT']:
        if r.get(c): lk.setdefault(norm(r[c]),iso)
manual={"Bolivia (Plurinational State of)":"BOL","Iran (Islamic Republic of)":"IRN","Venezuela (Bolivarian Republic of)":"VEN",
"Micronesia (Federated States of)":"FSM","Republic of Moldova":"MDA","United Republic of Tanzania":"TZA","Democratic People's Republic of Korea":"PRK",
"Republic of Korea":"KOR","Lao People's Democratic Republic":"LAO","Viet Nam":"VNM","Syrian Arab Republic":"SYR","Russian Federation":"RUS",
"Côte d'Ivoire":"CIV","Cabo Verde":"CPV","Eswatini":"SWZ","Türkiye":"TUR","Taiwan":"TWN","Palestine":"PSE","Congo":"COG",
"Democratic Republic of the Congo":"COD","Czechia":"CZE","North Macedonia":"MKD","Brunei Darussalam":"BRN","Tokelau":"TKL",
"United States Virgin Islands":"VIR","Sao Tome and Principe":"STP","Gambia":"GMB","Bahamas":"BHS","South Sudan":"SSD","Sudan":"SDN",
"Somalia":"SOM","Kosovo":"XKX","Norway":"NOR","France":"FRA","Guinea-Bissau":"GNB","Timor-Leste":"TLS","Saint Kitts and Nevis":"KNA",
"Saint Vincent and the Grenadines":"VCT","Saint Lucia":"LCA","Antigua and Barbuda":"ATG","Northern Mariana Islands":"MNP","Niue":"NIU",
"Cook Islands":"COK","Monaco":"MCO","San Marino":"SMR","Andorra":"AND","Nauru":"NRU","Tuvalu":"TUV","Marshall Islands":"MHL","Palau":"PLW",
"Kiribati":"KIR","American Samoa":"ASM","Guam":"GUM","Bermuda":"BMU","Greenland":"GRL","Puerto Rico":"PRI","Dominica":"DMA","Grenada":"GRD",
"Tonga":"TON","Samoa":"WSM","Maldives":"MDV","Mauritius":"MUS","Seychelles":"SYC","Comoros":"COM","Barbados":"BRB","Malta":"MLT",
"United Kingdom":"GBR","United States of America":"USA","Bosnia and Herzegovina":"BIH","Serbia":"SRB","Montenegro":"MNE","Cyprus":"CYP","Denmark":"DNK"}
g['iso3']=[manual.get(n) or lk.get(norm(n)) for n in g.location_name]
print('unmatched:',g[g.iso3.isna()].location_name.tolist()); print('dupes:',g[g.iso3.duplicated(keep=False)&g.iso3.notna()].to_string())
g.to_csv('data/processed/gbd_locations_iso3.csv',index=False)
