import geopandas as gpd
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

model_groups = ["residential_single_family", "residential_multi_family", "commercial"]

parcel_data = pd.read_csv(sys.argv[1], dtype={'PARID': str, 'PROPERTYHOUSENUM': str, 'PROPERTYFRACTION': str, 'PROPERTYADDRESS': str, 'PROPERTYCITY': str, 'PROPERTYSTATE': str, 'PROPERTYUNIT': str, 'PROPERTYZIP': str, 'MUNICODE': str, 'MUNIDESC': str, 'SCHOOLCODE': str, 'SCHOOLDESC': str, 'LEGAL1': str, 'LEGAL2': str, 'LEGAL3': str, 'NEIGHCODE': str, 'NEIGHDESC': str, 'TAXCODE': str, 'TAXDESC': str, 'TAXSUBCODE': str, 'TAXSUBCODE_DESC': str, 'OWNERCODE': str, 'OWNERDESC': str, 'CLASS': str, 'CLASSDESC': str, 'USECODE': str, 'USEDESC': str, 'LOTAREA': str, 'HOMESTEADFLAG': str, 'FARMSTEADFLAG': str, 'CLEANGREEN': str, 'ABATEMENTFLAG': str, 'RECORDDATE': str, 'SALEDATE': str, 'SALEPRICE': float, 'SALECODE': str, 'SALEDESC': str, 'DEEDBOOK': str, 'DEEDPAGE': str, 'PREVSALEDATE': str, 'PREVSALEPRICE': str, 'PREVSALEDATE2': str, 'PREVSALEPRICE2': str, 'CHANGENOTICEADDRESS1': str, 'CHANGENOTICEADDRESS2': str, 'CHANGENOTICEADDRESS3': str, 'CHANGENOTICEADDRESS4': str, 'COUNTYBUILDING': str, 'COUNTYLAND': str, 'COUNTYTOTAL': str, 'COUNTYEXEMPTBLDG': str, 'LOCALBUILDING': str, 'LOCALLAND': str, 'LOCALTOTAL': str, 'FAIRMARKETBUILDING': str, 'FAIRMARKETLAND': str, 'FAIRMARKETTOTAL': str, 'STYLE': str, 'STYLEDESC': str, 'STORIES': str, 'YEARBLT': str, 'EXTERIORFINISH': str, 'EXTFINISH_DESC': str, 'ROOF': str, 'ROOFDESC': str, 'BASEMENT': str, 'BASEMENTDESC': str, 'GRADE': str, 'GRADEDESC': str, 'CONDITION': str, 'CONDITIONDESC': str, 'CDU': str, 'CDUDESC': str, 'TOTALROOMS': str, 'BEDROOMS': str, 'FULLBATHS': str, 'HALFBATHS': str, 'HEATINGCOOLING': str, 'HEATINGCOOLINGDESC': str, 'FIREPLACES': str, 'BSMTGARAGE': str, 'FINISHEDLIVINGAREA': str, 'CARDNUMBER': str, 'ALT_ID': str, 'TAXYEAR': str, 'ASOFDATE': str})
parcel_geometry = gpd.read_file(sys.argv[2])
openavmkit_output_folder = sys.argv[3]
predictions = {}
land_predictions = {}
land_predictions_mra = {}
regression_predictions = {}
land_areas = {}
census_tracts = {}
universe_data = pd.DataFrame(data={}, columns=['key','spatial_lag_sale_price_time_adj','spatial_lag_sale_price_time_adj_confidence','spatial_lag_sale_price_time_adj_vacant','spatial_lag_sale_price_time_adj_vacant_confidence','spatial_lag_sale_price_time_adj_land_sqft','spatial_lag_sale_price_time_adj_land_sqft_confidence','spatial_lag_sale_price_time_adj_impr_sqft','spatial_lag_sale_price_time_adj_impr_sqft_confidence','spatial_lag_floor_area_ratio','spatial_lag_bedroom_density','spatial_lag_bldg_age_years','spatial_lag_bldg_area_finished_sqft','spatial_lag_land_area_sqft','spatial_lag_bldg_quality_num','spatial_lag_bldg_condition_num'])
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
    universe = pd.read_csv(openavmkit_output_folder + "/" + x + "/main/mra/universe.csv", usecols=['key','spatial_lag_sale_price_time_adj','spatial_lag_sale_price_time_adj_confidence','spatial_lag_sale_price_time_adj_vacant','spatial_lag_sale_price_time_adj_vacant_confidence','spatial_lag_sale_price_time_adj_land_sqft','spatial_lag_sale_price_time_adj_land_sqft_confidence','spatial_lag_sale_price_time_adj_impr_sqft','spatial_lag_sale_price_time_adj_impr_sqft_confidence','spatial_lag_floor_area_ratio','spatial_lag_bedroom_density','spatial_lag_bldg_age_years','spatial_lag_bldg_area_finished_sqft','spatial_lag_land_area_sqft','spatial_lag_bldg_quality_num','spatial_lag_bldg_condition_num'])
    universe_data = pd.concat([universe_data, universe])

universe_data.rename(columns={'key': 'PARID'}, inplace=True)
parcel_data = parcel_data.merge(universe_data, how='left', on='PARID')

parcel_data['total_prediction'] = parcel_data['PARID'].map(predictions)
parcel_data['land_prediction'] = parcel_data['PARID'].map(land_predictions)
parcel_data['regression_prediction'] = parcel_data['PARID'].map(regression_predictions)
parcel_data['regression_land_prediction'] = parcel_data['PARID'].map(land_predictions_mra)
parcel_data.rename(columns={'FAIRMARKETLAND': 'assessed_land'}, inplace=True)
parcel_data.rename(columns={'FAIRMARKETTOTAL': 'assessed_total'}, inplace=True)
parcel_data.rename(columns={'FINISHEDLIVINGAREA': 'building_area'}, inplace=True)
parcel_data['total_prediction'] = parcel_data['total_prediction'].astype(float)
parcel_data['land_prediction'] = parcel_data['land_prediction'].astype(float)
parcel_data['regression_prediction'] = parcel_data['regression_prediction'].astype(float)
parcel_data['regression_land_prediction'] = parcel_data['regression_land_prediction'].astype(float)
parcel_data['assessed_land'] = parcel_data['assessed_land'].astype(float)
parcel_data['assessed_total'] = parcel_data['assessed_total'].astype(float)
parcel_data['building_area'] = parcel_data['building_area'].astype(float)

parcel_data['OWNER_OCCUPIED'] = pd.Series(dtype='string')
parcel_data['YEARS_SINCE_SALE'] = pd.Series(dtype='float64')
parcel_data['ASSESSMENT_RATIO'] = pd.Series(dtype='float64')
parcel_data['NEW_SALES_RATIO'] = pd.Series(dtype='float64')
parcel_data['OLD_SALES_RATIO'] = pd.Series(dtype='float64')
for i, row in parcel_data.iterrows():
    parcel_data.at[i, 'OWNER_OCCUPIED'] = 'N'
    if isinstance(row['SALEDATE'], str):
        sale_date = datetime.strptime(row['SALEDATE'], "%m-%d-%Y")
        updated_date = datetime.strptime(row['ASOFDATE'], "%d-%b-%y")
        ownership_time = updated_date - sale_date
        if row['assessed_total'] > 0 and row['total_prediction'] > 0:
            parcel_data.at[i, 'ASSESSMENT_RATIO'] = (row['total_prediction'] / (row['assessed_total'] / 0.527))
        if row['SALEDESC'] == 'VALID SALE' and sale_date.year >= 2024 and row['total_prediction'] > 0 and row['SALEPRICE'] > 0:
            parcel_data.at[i, 'NEW_SALES_RATIO'] = (row['total_prediction'] / (row['SALEPRICE']))
            parcel_data.at[i, 'OLD_SALES_RATIO'] = ((row['assessed_total'] / 0.527) / (row['SALEPRICE']))
        parcel_data.at[i, 'YEARS_SINCE_SALE'] = ownership_time.total_seconds() / (365 * 24 * 60 * 60)
    if row['CLASS'] == 'R':
        full_address = str(row['PROPERTYHOUSENUM']) + str(row['PROPERTYFRACTION']) + str(row['PROPERTYADDRESS']) + str(row['PROPERTYUNIT'])
        if full_address.replace(" ", "") == row['CHANGENOTICEADDRESS1'].replace(" ", ""):
            parcel_data.at[i, 'OWNER_OCCUPIED'] = 'Y'

parcel_geometry.rename(columns={'PIN': 'PARCEL_ID'}, inplace=True)
parcel_data['land_area_sqft'] = parcel_data['PARID'].map(land_areas)
parcel_data['census_tract'] = parcel_data['PARID'].map(census_tracts)
parcel_data['land_ratio'] = parcel_data['assessed_land'] / parcel_data['assessed_total']

# Simple land valuation algorithm - https://progressandpoverty.substack.com/p/valuing-land-the-simplest-viable
median_assessments = parcel_data.groupby(['census_tract'])['total_prediction'].median().reset_index()
median_lot_sizes = parcel_data.groupby(['census_tract'])['land_area_sqft'].median().reset_index()
land_ratios = parcel_data.groupby(['census_tract'])['land_ratio'].median().reset_index()
price_per_sqft = median_assessments.merge(median_lot_sizes, left_on=['census_tract'], right_on=['census_tract'])
price_per_sqft['census_tract_total_price_per_sqft'] = price_per_sqft['total_prediction'] / price_per_sqft['land_area_sqft']
census_tract_land_price_per_sqft = price_per_sqft.merge(land_ratios, left_on=['census_tract'], right_on=['census_tract'])
census_tract_land_price_per_sqft.rename(columns={'land_ratio': 'census_tract_land_percentage'}, inplace=True)
census_tract_land_price_per_sqft['census_tract_land_price_per_sqft'] = census_tract_land_price_per_sqft['census_tract_total_price_per_sqft'] * census_tract_land_price_per_sqft['census_tract_land_percentage']
census_tract_land_price_per_sqft = census_tract_land_price_per_sqft[['census_tract','census_tract_total_price_per_sqft','census_tract_land_percentage','census_tract_land_price_per_sqft']]
parcel_data = parcel_data.merge(census_tract_land_price_per_sqft, how='left', left_on=['census_tract'], right_on=['census_tract'])
parcel_data['census_tract_lycd_land_prediction'] = parcel_data['land_area_sqft'] * parcel_data['census_tract_land_price_per_sqft']
# Try it at the neighborhood level as well
median_assessments = parcel_data.groupby(['NEIGHCODE'])['total_prediction'].median().reset_index()
median_lot_sizes = parcel_data.groupby(['NEIGHCODE'])['land_area_sqft'].median().reset_index()
land_ratios = parcel_data.groupby(['NEIGHCODE'])['land_ratio'].median().reset_index()
price_per_sqft = median_assessments.merge(median_lot_sizes, left_on=['NEIGHCODE'], right_on=['NEIGHCODE'])
price_per_sqft['neighborhood_total_price_per_sqft'] = price_per_sqft['total_prediction'] / price_per_sqft['land_area_sqft']
neighborhood_land_price_per_sqft = price_per_sqft.merge(land_ratios, left_on=['NEIGHCODE'], right_on=['NEIGHCODE'])
neighborhood_land_price_per_sqft.rename(columns={'land_ratio': 'neighborhood_land_percentage'}, inplace=True)
neighborhood_land_price_per_sqft['neighborhood_land_price_per_sqft'] = neighborhood_land_price_per_sqft['neighborhood_total_price_per_sqft'] * neighborhood_land_price_per_sqft['neighborhood_land_percentage']
neighborhood_land_price_per_sqft = neighborhood_land_price_per_sqft[['NEIGHCODE','neighborhood_total_price_per_sqft','neighborhood_land_percentage','neighborhood_land_price_per_sqft']]
parcel_data = parcel_data.merge(neighborhood_land_price_per_sqft, how='left', left_on=['NEIGHCODE'], right_on=['NEIGHCODE'])
parcel_data['neighborhood_lycd_land_prediction'] = parcel_data['land_area_sqft'] * parcel_data['neighborhood_land_price_per_sqft']

assessment_ratios = parcel_data[(parcel_data['ASSESSMENT_RATIO'] > 0) | (parcel_data['ASSESSMENT_RATIO'] < 0)]
neighborhood_assessment_ratios = assessment_ratios.groupby(['NEIGHCODE'])['ASSESSMENT_RATIO'].median().reset_index()
neighborhood_assessment_ratios.rename(columns={'ASSESSMENT_RATIO': 'neighborhood_assessment_ratio'}, inplace=True)
census_tract_assessment_ratios = assessment_ratios.groupby(['census_tract'])['ASSESSMENT_RATIO'].median().reset_index()
census_tract_assessment_ratios.rename(columns={'ASSESSMENT_RATIO': 'census_tract_assessment_ratio'}, inplace=True)
parcel_data = parcel_data.merge(neighborhood_assessment_ratios, how='left', left_on=['NEIGHCODE'], right_on=['NEIGHCODE'])
parcel_data = parcel_data.merge(census_tract_assessment_ratios, how='left', left_on=['census_tract'], right_on=['census_tract'])

old_sales_ratios = parcel_data[(parcel_data['OLD_SALES_RATIO'] > 0) | (parcel_data['OLD_SALES_RATIO'] < 0)]
neighborhood_old_sales_ratios = old_sales_ratios.groupby(['NEIGHCODE'])['OLD_SALES_RATIO'].median().reset_index()
neighborhood_old_sales_ratios.rename(columns={'SALES_RATIO': 'neighborhood_old_sales_ratio'}, inplace=True)
census_tract_old_sales_ratios = old_sales_ratios.groupby(['census_tract'])['OLD_SALES_RATIO'].median().reset_index()
census_tract_old_sales_ratios.rename(columns={'OLD_SALES_RATIO': 'census_tract_old_sales_ratio'}, inplace=True)
parcel_data = parcel_data.merge(neighborhood_old_sales_ratios, how='left', left_on=['NEIGHCODE'], right_on=['NEIGHCODE'])
parcel_data = parcel_data.merge(census_tract_old_sales_ratios, how='left', left_on=['census_tract'], right_on=['census_tract'])

new_sales_ratios = parcel_data[(parcel_data['NEW_SALES_RATIO'] > 0) | (parcel_data['NEW_SALES_RATIO'] < 0)]
neighborhood_new_sales_ratios = new_sales_ratios.groupby(['NEIGHCODE'])['NEW_SALES_RATIO'].median().reset_index()
neighborhood_new_sales_ratios.rename(columns={'SALES_RATIO': 'neighborhood_new_sales_ratio'}, inplace=True)
census_tract_new_sales_ratios = new_sales_ratios.groupby(['census_tract'])['NEW_SALES_RATIO'].median().reset_index()
census_tract_new_sales_ratios.rename(columns={'NEW_SALES_RATIO': 'census_tract_new_sales_ratio'}, inplace=True)
parcel_data = parcel_data.merge(neighborhood_new_sales_ratios, how='left', left_on=['NEIGHCODE'], right_on=['NEIGHCODE'])
parcel_data = parcel_data.merge(census_tract_new_sales_ratios, how='left', left_on=['census_tract'], right_on=['census_tract'])

parcel_geometry_assessments = parcel_geometry[['PARCEL_ID','geometry']]
parcel_geometry_assessments = parcel_geometry_assessments.merge(parcel_data, left_on=['PARCEL_ID'], right_on=['PARID'])

parcel_data.to_csv("predictions.csv", index=False)
parcel_geometry_assessments.to_parquet('predictions.parquet')
