import geopandas as gpd
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

model_groups = ["residential","commercial"]

parcel_data = pd.read_csv(sys.argv[1], dtype={'PARID': str, 'PROPERTYHOUSENUM': str, 'PROPERTYFRACTION': str, 'PROPERTYADDRESS': str, 'PROPERTYCITY': str, 'PROPERTYSTATE': str, 'PROPERTYUNIT': str, 'PROPERTYZIP': str, 'MUNICODE': str, 'MUNIDESC': str, 'SCHOOLCODE': str, 'SCHOOLDESC': str, 'LEGAL1': str, 'LEGAL2': str, 'LEGAL3': str, 'NEIGHCODE': str, 'NEIGHDESC': str, 'TAXCODE': str, 'TAXDESC': str, 'TAXSUBCODE': str, 'TAXSUBCODE_DESC': str, 'OWNERCODE': str, 'OWNERDESC': str, 'CLASS': str, 'CLASSDESC': str, 'USECODE': str, 'USEDESC': str, 'LOTAREA': str, 'HOMESTEADFLAG': str, 'FARMSTEADFLAG': str, 'CLEANGREEN': str, 'ABATEMENTFLAG': str, 'RECORDDATE': str, 'SALEDATE': str, 'SALEPRICE': str, 'SALECODE': str, 'SALEDESC': str, 'DEEDBOOK': str, 'DEEDPAGE': str, 'PREVSALEDATE': str, 'PREVSALEPRICE': str, 'PREVSALEDATE2': str, 'PREVSALEPRICE2': str, 'CHANGENOTICEADDRESS1': str, 'CHANGENOTICEADDRESS2': str, 'CHANGENOTICEADDRESS3': str, 'CHANGENOTICEADDRESS4': str, 'COUNTYBUILDING': str, 'COUNTYLAND': str, 'COUNTYTOTAL': str, 'COUNTYEXEMPTBLDG': str, 'LOCALBUILDING': str, 'LOCALLAND': str, 'LOCALTOTAL': str, 'FAIRMARKETBUILDING': str, 'FAIRMARKETLAND': str, 'FAIRMARKETTOTAL': str, 'STYLE': str, 'STYLEDESC': str, 'STORIES': str, 'YEARBLT': str, 'EXTERIORFINISH': str, 'EXTFINISH_DESC': str, 'ROOF': str, 'ROOFDESC': str, 'BASEMENT': str, 'BASEMENTDESC': str, 'GRADE': str, 'GRADEDESC': str, 'CONDITION': str, 'CONDITIONDESC': str, 'CDU': str, 'CDUDESC': str, 'TOTALROOMS': str, 'BEDROOMS': str, 'FULLBATHS': str, 'HALFBATHS': str, 'HEATINGCOOLING': str, 'HEATINGCOOLINGDESC': str, 'FIREPLACES': str, 'BSMTGARAGE': str, 'FINISHEDLIVINGAREA': str, 'CARDNUMBER': str, 'ALT_ID': str, 'TAXYEAR': str, 'ASOFDATE': str})
parcel_geometry = gpd.read_file(sys.argv[2])
openavmkit_output_folder = sys.argv[3]
predictions = {}
land_predictions = {}
land_predictions_mra = {}
regression_predictions = {}
total_assessments = {}
land_assessments = {}
land_areas = {}
census_tracts = {}
building_areas = {}
for x in model_groups:
    print(x)
    prediction_data_ensemble = pd.read_csv(openavmkit_output_folder + "/" + x + "/main/ensemble/pred_universe.csv")
    for i, row in prediction_data_ensemble.iterrows():
        predictions[row['key']] = row['prediction']
        land_areas[row['key']] = float(row['land_area_sqft'])
        census_tracts[row['key']] = row['census_tract']
    land_file = openavmkit_output_folder + "/" + x + "/hedonic_land/ensemble/pred_universe.csv"
    if Path(land_file).exists():
        prediction_data_ensemble_land = pd.read_csv(openavmkit_output_folder + "/" + x + "/hedonic_land/ensemble/pred_universe.csv")
        for i, row in prediction_data_ensemble_land.iterrows():
            land_predictions[row['key']] = row['prediction']
        prediction_data_mra_land = pd.read_csv(openavmkit_output_folder + "/" + x + "/hedonic_land/mra/pred_universe.csv")
        for i, row in prediction_data_mra_land.iterrows():
            land_predictions_mra[row['key']] = row['prediction']
    prediction_data_ensemble_regression = pd.read_csv(openavmkit_output_folder + "/" + x + "/main/mra/pred_universe.csv")
    for i, row in prediction_data_ensemble_regression.iterrows():
        regression_predictions[row['key']] = row['prediction']
parcel_data['OWNER_OCCUPIED'] = pd.Series(dtype='string')
parcel_data['YEARS_SINCE_SALE'] = pd.Series(dtype='float64')
for i, row in parcel_data.iterrows():
    parcel_data.at[i, 'OWNER_OCCUPIED'] = 'N'
    if isinstance(row['SALEDATE'], str):
        sale_date = datetime.strptime(row['SALEDATE'], "%m-%d-%Y")
        updated_date = datetime.strptime(row['ASOFDATE'], "%d-%b-%y")
        ownership_time = updated_date - sale_date
        parcel_data.at[i, 'YEARS_SINCE_SALE'] = ownership_time.total_seconds() / (365 * 24 * 60 * 60)
    if row['CLASS'] == 'R':
        full_address = str(row['PROPERTYHOUSENUM']) + str(row['PROPERTYFRACTION']) + str(row['PROPERTYADDRESS']) + str(row['PROPERTYUNIT'])
        if full_address.replace(" ", "") == row['CHANGENOTICEADDRESS1'].replace(" ", ""):
            parcel_data.at[i, 'OWNER_OCCUPIED'] = 'Y'
    land_assessments[row['PARID']] = float(row['FAIRMARKETLAND'])
    total_assessments[row['PARID']] = float(row['FAIRMARKETTOTAL'])
    building_areas[row['PARID']] = float(row['FINISHEDLIVINGAREA'])

print(parcel_geometry.head())
parcel_geometry.rename(columns={'PIN': 'PARCEL_ID'}, inplace=True)
parcel_data['total_prediction'] = parcel_data['PARID'].map(predictions)
parcel_data['land_prediction'] = parcel_data['PARID'].map(land_predictions)
parcel_data['regression_prediction'] = parcel_data['PARID'].map(regression_predictions)
parcel_data['regression_land_prediction'] = parcel_data['PARID'].map(land_predictions_mra)
parcel_data['assessed_land'] = parcel_data['PARID'].map(land_assessments)
parcel_data['assessed_total'] = parcel_data['PARID'].map(total_assessments)
parcel_data['land_area_sqft'] = parcel_data['PARID'].map(land_areas)
parcel_data['building_area'] = parcel_data['PARID'].map(building_areas)
parcel_data['census_tract'] = parcel_data['PARID'].map(census_tracts)

# Simple land valuation algorithm - https://progressandpoverty.substack.com/p/valuing-land-the-simplest-viable
median_assessments = parcel_data.groupby(['census_tract'])['total_prediction'].median().reset_index()
median_lot_sizes = parcel_data.groupby(['census_tract'])['land_area_sqft'].median().reset_index()
total_land_valuations = parcel_data.groupby(['census_tract'])['assessed_land'].sum().reset_index()
total_valuations = parcel_data.groupby(['census_tract'])['assessed_total'].sum().reset_index()
price_per_sqft = median_assessments.merge(median_lot_sizes, left_on=['census_tract'], right_on=['census_tract'])
price_per_sqft['census_tract_total_price_per_sqft'] = price_per_sqft['total_prediction'] / price_per_sqft['land_area_sqft']
valuation_ratios = total_land_valuations.merge(total_valuations, left_on=['census_tract'], right_on=['census_tract'])
valuation_ratios['census_tract_land_percentage'] = valuation_ratios['assessed_land'] / valuation_ratios['assessed_total']
census_tract_land_price_per_sqft = price_per_sqft.merge(valuation_ratios, left_on=['census_tract'], right_on=['census_tract'])
census_tract_land_price_per_sqft['census_tract_land_price_per_sqft'] = census_tract_land_price_per_sqft['census_tract_total_price_per_sqft'] * census_tract_land_price_per_sqft['census_tract_land_percentage']
census_tract_land_price_per_sqft = census_tract_land_price_per_sqft[['census_tract','census_tract_total_price_per_sqft','census_tract_land_percentage','census_tract_land_price_per_sqft']]
pd.set_option('display.max_columns', None)
print(census_tract_land_price_per_sqft)
parcel_data = parcel_data.merge(census_tract_land_price_per_sqft, how='left', left_on=['census_tract'], right_on=['census_tract'])
parcel_data['lycd_land_prediction'] = parcel_data['land_area_sqft'] * parcel_data['census_tract_land_price_per_sqft']

parcel_geometry_assessments = parcel_geometry[['PARCEL_ID','geometry']]
parcel_geometry_assessments = parcel_geometry_assessments.merge(parcel_data, left_on=['PARCEL_ID'], right_on=['PARID'])

parcel_data.to_csv("predictions.csv", index=False)
parcel_geometry_assessments.to_parquet('predictions.parquet')
