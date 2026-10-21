REG={'Central Asia':'ARM AZE GEO KAZ KGZ MNG TJK TKM UZB','Central Europe':'ALB BIH BGR HRV CZE HUN MKD MNE POL ROU SRB SVK SVN',
'Eastern Europe':'BLR EST LVA LTU MDA RUS UKR','Australasia':'AUS NZL','High-income Asia Pacific':'BRN JPN KOR SGP',
'High-income North America':'CAN USA GRL BMU','Southern Latin America':'ARG CHL URY',
'Western Europe':'AND AUT BEL CYP DNK FIN FRA DEU GRC ISL IRL ISR ITA LUX MLT MCO NLD NOR PRT SMR ESP SWE CHE GBR',
'Andean Latin America':'BOL ECU PER','Caribbean':'ATG BHS BRB BLZ CUB DMA DOM GRD GUY HTI JAM LCA VCT SUR TTO PRI VIR KNA',
'Central Latin America':'COL CRI SLV GTM HND MEX NIC PAN VEN','Tropical Latin America':'BRA PRY',
'North Africa and Middle East':'AFG DZA BHR EGY IRN IRQ JOR KWT LBN LBY MAR PSE OMN QAT SAU SDN SYR TUN TUR ARE YEM',
'South Asia':'BGD BTN IND NPL PAK','East Asia':'CHN PRK TWN',
'Oceania':'ASM COK FJI KIR MHL FSM NRU NIU MNP PLW PNG WSM SLB TKL TON TUV VUT GUM',
'Southeast Asia':'KHM IDN LAO MYS MDV MUS MMR PHL LKA SYC THA TLS VNM',
'Central Sub-Saharan Africa':'AGO CAF COG COD GNQ GAB','Eastern Sub-Saharan Africa':'BDI COM DJI ERI ETH KEN MDG MWI MOZ RWA SOM SSD TZA UGA ZMB',
'Southern Sub-Saharan Africa':'BWA LSO NAM ZAF SWZ ZWE','Western Sub-Saharan Africa':'BEN BFA CMR CPV TCD CIV GMB GHA GIN GNB LBR MLI MRT NER NGA STP SEN SLE TGO'}
ISO2REG={i:r for r,v in REG.items() for i in v.split()}
ISO2REG['ALA']='Western Europe'  # Finland is coded ALA in gbd_locations_iso3
