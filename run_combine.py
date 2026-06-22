import os, sys

os.chdir(r'C:/projects/agc_assessments/output')

sys.argv = [
    'C:/projects/agc_assessments/scripts/combineOutputFiles.py',
    r'C:/projects/agc_assessments/data/assessments.csv',
    r'C:/projects/agc_assessments/data/AlleghenyCounty_Parcels20260608/AlleghenyCounty_Parcels20260608.shp',
    r'C:/projects/agc_assessments/data/allegheny_census_tracts_2020.geojson',
    r'C:/projects/agc_assessments/data/us-pa-allegheny/out/models',
]

exec(open('C:/projects/agc_assessments/scripts/combineOutputFiles.py').read())
