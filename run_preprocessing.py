import os
os.chdir(r'C:/projects/openavmkit/notebooks/pipeline/data/us-pa-allegheny/in')

import sys
sys.argv = [
    'C:/projects/agc_assessments/scripts/openAvmKitInputFiles.py',
    r'C:/projects/agc_assessments/data/assessments.csv',
    r'C:/projects/agc_assessments/data/AlleghenyCounty_Parcels20260608/AlleghenyCounty_Parcels20260608.shp',
    r'C:/projects/agc_assessments/data/allegheny_census_tracts_2020.geojson',
    r'C:/projects/agc_assessments/data/commercial_rents.csv',
    r'C:/projects/agc_assessments/data/mva.geojson',
    r'C:/projects/agc_assessments/data/slopes.geojson',
    r'C:/projects/agc_assessments/data/flood_zones.geojson',
    r'C:/projects/agc_assessments/data/undermined.geojson',
    r'C:/projects/agc_assessments/data/CityBoundary.geojson',
    r'C:/projects/agc_assessments/data/city_council_districts_2022.geojson',
    r'C:/projects/agc_assessments/data/county_council_districts.geojson',
    r'C:/projects/agc_assessments/data/census_blocks_2020.geojson',
    r'C:/projects/agc_assessments/data/pa_wac_S000_JT00_2023.csv',
]

exec(open('C:/projects/agc_assessments/scripts/openAvmKitInputFiles.py').read())
