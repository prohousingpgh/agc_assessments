import geopandas as gpd
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

model_groups = ["residential_single_family", "residential_multi_family", "commercial"]

parcel_data = pd.read_csv(sys.argv[1], dtype={'PARID': str, 'PROPERTYHOUSENUM': str, 'PROPERTYFRACTION': str, 'PROPERTYADDRESS': str, 'PROPERTYCITY': str, 'PROPERTYSTATE': str, 'PROPERTYUNIT': str, 'PROPERTYZIP': str, 'MUNICODE': str, 'MUNIDESC': str, 'SCHOOLCODE': str, 'SCHOOLDESC': str, 'LEGAL1': str, 'LEGAL2': str, 'LEGAL3': str, 'NEIGHCODE': str, 'NEIGHDESC': str, 'TAXCODE': str, 'TAXDESC': str, 'TAXSUBCODE': str, 'TAXSUBCODE_DESC': str, 'OWNERCODE': str, 'OWNERDESC': str, 'CLASS': str, 'CLASSDESC': str, 'USECODE': str, 'USEDESC': str, 'LOTAREA': float, 'HOMESTEADFLAG': str, 'FARMSTEADFLAG': str, 'CLEANGREEN': str, 'ABATEMENTFLAG': str, 'RECORDDATE': str, 'SALEDATE': str, 'SALEPRICE': float, 'SALECODE': str, 'SALEDESC': str, 'DEEDBOOK': str, 'DEEDPAGE': str, 'PREVSALEDATE': str, 'PREVSALEPRICE': str, 'PREVSALEDATE2': str, 'PREVSALEPRICE2': str, 'CHANGENOTICEADDRESS1': str, 'CHANGENOTICEADDRESS2': str, 'CHANGENOTICEADDRESS3': str, 'CHANGENOTICEADDRESS4': str, 'COUNTYBUILDING': str, 'COUNTYLAND': str, 'COUNTYTOTAL': str, 'COUNTYEXEMPTBLDG': str, 'LOCALBUILDING': str, 'LOCALLAND': str, 'LOCALTOTAL': str, 'FAIRMARKETBUILDING': str, 'FAIRMARKETLAND': str, 'FAIRMARKETTOTAL': str, 'STYLE': str, 'STYLEDESC': str, 'STORIES': str, 'YEARBLT': str, 'EXTERIORFINISH': str, 'EXTFINISH_DESC': str, 'ROOF': str, 'ROOFDESC': str, 'BASEMENT': str, 'BASEMENTDESC': str, 'GRADE': str, 'GRADEDESC': str, 'CONDITION': str, 'CONDITIONDESC': str, 'CDU': str, 'CDUDESC': str, 'TOTALROOMS': str, 'BEDROOMS': str, 'FULLBATHS': str, 'HALFBATHS': str, 'HEATINGCOOLING': str, 'HEATINGCOOLINGDESC': str, 'FIREPLACES': str, 'BSMTGARAGE': str, 'FINISHEDLIVINGAREA': str, 'CARDNUMBER': str, 'ALT_ID': str, 'TAXYEAR': str, 'ASOFDATE': str})
parcel_geometry = gpd.read_file(sys.argv[2])
census_tract_geometry = gpd.read_file(sys.argv[3], columns=['NAME'])
openavmkit_output_folder = sys.argv[4]
universe_data = pd.DataFrame(data={}, columns=['key','spatial_lag_sale_price_time_adj','spatial_lag_sale_price_time_adj_confidence','spatial_lag_sale_price_time_adj_vacant','spatial_lag_sale_price_time_adj_vacant_confidence','spatial_lag_sale_price_time_adj_land_sqft','spatial_lag_sale_price_time_adj_land_sqft_confidence','spatial_lag_sale_price_time_adj_impr_sqft','spatial_lag_sale_price_time_adj_impr_sqft_confidence','spatial_lag_floor_area_ratio','spatial_lag_bedroom_density','spatial_lag_bldg_age_years','spatial_lag_bldg_area_finished_sqft','spatial_lag_land_area_sqft','spatial_lag_bldg_quality_num','spatial_lag_bldg_condition_num'])
prediction_data_ensemble = pd.DataFrame(data={}, columns=['key','total_prediction','land_area_sqft','census_tract'])
prediction_data_mra = pd.DataFrame(data={}, columns=['key','regression_total_prediction'])
prediction_data_land_ensemble = pd.DataFrame(data={}, columns=['key','land_prediction'])
prediction_data_land_mra = pd.DataFrame(data={}, columns=['key','regression_land_prediction'])
for x in model_groups:
    print(x)
    prediction = pd.read_csv(openavmkit_output_folder + "/" + x + "/main/ensemble/pred_universe.csv", usecols=['key','prediction','land_area_sqft','census_tract'], dtype={'key': str, 'prediction': float, 'land_area_sqft': float, 'census_tract': str})
    prediction.rename(columns={'prediction': 'total_prediction'}, inplace=True)
    prediction_data_ensemble = pd.concat([prediction_data_ensemble, prediction])
    prediction = pd.read_csv(openavmkit_output_folder + "/" + x + "/main/mra/pred_universe.csv", usecols=['key','prediction'], dtype={'key': str, 'prediction': float})
    prediction.rename(columns={'prediction': 'regression_total_prediction'}, inplace=True)
    prediction_data_mra = pd.concat([prediction_data_mra, prediction])
    land_file = openavmkit_output_folder + "/" + x + "/hedonic_land/ensemble/pred_universe.csv"
    if Path(land_file).exists():
        prediction = pd.read_csv(openavmkit_output_folder + "/" + x + "/hedonic_land/ensemble/pred_universe.csv", usecols=['key','prediction'], dtype={'key': str, 'prediction': float})
        prediction.rename(columns={'prediction': 'land_prediction'}, inplace=True)
        prediction_data_land_ensemble = pd.concat([prediction_data_land_ensemble, prediction])
        prediction = pd.read_csv(openavmkit_output_folder + "/" + x + "/hedonic_land/mra/pred_universe.csv", usecols=['key','prediction'], dtype={'key': str, 'prediction': float})
        prediction.rename(columns={'prediction': 'regression_land_prediction'}, inplace=True)
        prediction_data_land_mra = pd.concat([prediction_data_land_mra, prediction])
    universe = pd.read_csv(openavmkit_output_folder + "/" + x + "/main/mra/universe.csv", usecols=['key','spatial_lag_sale_price_time_adj','spatial_lag_sale_price_time_adj_confidence','spatial_lag_sale_price_time_adj_vacant','spatial_lag_sale_price_time_adj_vacant_confidence','spatial_lag_sale_price_time_adj_land_sqft','spatial_lag_sale_price_time_adj_land_sqft_confidence','spatial_lag_sale_price_time_adj_impr_sqft','spatial_lag_sale_price_time_adj_impr_sqft_confidence','spatial_lag_floor_area_ratio','spatial_lag_bedroom_density','spatial_lag_bldg_age_years','spatial_lag_bldg_area_finished_sqft','spatial_lag_land_area_sqft','spatial_lag_bldg_quality_num','spatial_lag_bldg_condition_num','city_council_district','county_council_district','is_vacant'], dtype={'key': str,'spatial_lag_sale_price_time_adj': float,'spatial_lag_sale_price_time_adj_confidence': float,'spatial_lag_sale_price_time_adj_vacant': float,'spatial_lag_sale_price_time_adj_vacant_confidence': float,'spatial_lag_sale_price_time_adj_land_sqft': float,'spatial_lag_sale_price_time_adj_land_sqft_confidence': float,'spatial_lag_sale_price_time_adj_impr_sqft': float,'spatial_lag_sale_price_time_adj_impr_sqft_confidence': float,'spatial_lag_floor_area_ratio': float,'spatial_lag_bedroom_density': float,'spatial_lag_bldg_age_years': float,'spatial_lag_bldg_area_finished_sqft': float,'spatial_lag_land_area_sqft': float,'spatial_lag_bldg_quality_num': float,'spatial_lag_bldg_condition_num': float,'city_council_district': str,'county_council_district': str,'is_vacant': str})
    universe_data = pd.concat([universe_data, universe])

prediction_data_ensemble.rename(columns={'key': 'PARID'}, inplace=True)
prediction_data_mra.rename(columns={'key': 'PARID'}, inplace=True)
prediction_data_land_ensemble.rename(columns={'key': 'PARID'}, inplace=True)
prediction_data_land_mra.rename(columns={'key': 'PARID'}, inplace=True)
universe_data.rename(columns={'key': 'PARID'}, inplace=True)

parcel_data = parcel_data.merge(prediction_data_ensemble, how='left', on='PARID')
parcel_data = parcel_data.merge(prediction_data_mra, how='left', on='PARID')
parcel_data = parcel_data.merge(prediction_data_land_ensemble, how='left', on='PARID')
parcel_data = parcel_data.merge(prediction_data_land_mra, how='left', on='PARID')
parcel_data = parcel_data.merge(universe_data, how='left', on='PARID')

parcel_data.rename(columns={'FAIRMARKETLAND': 'assessed_land'}, inplace=True)
parcel_data.rename(columns={'FAIRMARKETTOTAL': 'assessed_total'}, inplace=True)
parcel_data.rename(columns={'FINISHEDLIVINGAREA': 'building_area'}, inplace=True)
parcel_data.rename(columns={'SCHOOLDESC': 'school_district'}, inplace=True)
parcel_data['total_prediction'] = parcel_data['total_prediction'].astype(float)
parcel_data['land_prediction'] = parcel_data['land_prediction'].astype(float)
parcel_data['regression_total_prediction'] = parcel_data['regression_total_prediction'].astype(float)
parcel_data['regression_land_prediction'] = parcel_data['regression_land_prediction'].astype(float)
parcel_data['assessed_land'] = parcel_data['assessed_land'].astype(float)
parcel_data['assessed_total'] = parcel_data['assessed_total'].astype(float)
parcel_data['building_area'] = parcel_data['building_area'].astype(float)

parcel_data['OWNER_OCCUPIED'] = pd.Series(dtype='string')
parcel_data['municipality'] = pd.Series(dtype='string')
parcel_data['YEARS_SINCE_SALE'] = pd.Series(dtype='float64')
parcel_data['ASSESSMENT_RATIO'] = pd.Series(dtype='float64')
parcel_data['NEW_SALES_RATIO'] = pd.Series(dtype='float64')
parcel_data['OLD_SALES_RATIO'] = pd.Series(dtype='float64')
total_existing_residential_assessment = parcel_data.loc[parcel_data['CLASS'] == 'R', 'assessed_total'].sum()
total_new_residential_assessment = parcel_data.loc[parcel_data['CLASS'] == 'R', 'total_prediction'].sum()
total_residential_assessment_ratio = total_new_residential_assessment / total_existing_residential_assessment
print('total_residential_assessment_ratio is', total_residential_assessment_ratio)

parcel_geometry.rename(columns={'PIN': 'PARCEL_ID'}, inplace=True)
census_tract_geometry.rename(columns={'NAME': 'census_tract'}, inplace=True)
census_tract_geometry = census_tract_geometry.to_crs('EPSG:3857')
parcel_data['land_ratio'] = parcel_data['assessed_land'] / parcel_data['assessed_total']

# Simple land valuation algorithm - https://progressandpoverty.substack.com/p/valuing-land-the-simplest-viable
all_census_tracts = parcel_data.groupby(['census_tract'])['PARID'].agg(parcel_count='count')
all_census_tracts = census_tract_geometry.merge(all_census_tracts, on='census_tract')
median_assessments = parcel_data[parcel_data['CLASS'] == 'R'].groupby(['census_tract'])['total_prediction'].agg(total_prediction_median='median', residential_parcel_count='count')
median_lot_sizes = parcel_data[parcel_data['CLASS'] == 'R'].groupby(['census_tract'])['land_area_sqft'].agg(land_area_sqft_median='median')
mean_assessments = parcel_data[parcel_data['CLASS'] == 'R'].groupby(['census_tract'])['total_prediction'].agg(total_prediction_mean='mean')
mean_lot_sizes = parcel_data[parcel_data['CLASS'] == 'R'].groupby(['census_tract'])['land_area_sqft'].agg(land_area_sqft_mean='mean')
land_ratios = parcel_data[parcel_data['LOTAREA'] > 0].groupby(['census_tract'])['land_ratio'].median().reset_index()
median_assessments = all_census_tracts.merge(median_assessments, how='left', left_on=['census_tract'], right_on=['census_tract'])
price_per_sqft = median_assessments.merge(median_lot_sizes, how='left', left_on=['census_tract'], right_on=['census_tract'])
price_per_sqft = price_per_sqft.merge(mean_assessments, how='left', left_on=['census_tract'], right_on=['census_tract'])
price_per_sqft = price_per_sqft.merge(mean_lot_sizes, how='left', left_on=['census_tract'], right_on=['census_tract'])
price_per_sqft['census_tract_total_price_per_sqft_median'] = price_per_sqft['total_prediction_median'] / price_per_sqft['land_area_sqft_median']
price_per_sqft['census_tract_total_price_per_sqft_mean'] = price_per_sqft['total_prediction_mean'] / price_per_sqft['land_area_sqft_mean']
census_tract_land_price_per_sqft = price_per_sqft.merge(land_ratios, how='left', left_on=['census_tract'], right_on=['census_tract'])
census_tract_land_price_per_sqft.rename(columns={'land_ratio': 'census_tract_land_percentage'}, inplace=True)
census_tract_land_price_per_sqft['census_tract_land_price_per_sqft_temp_median'] = census_tract_land_price_per_sqft['census_tract_total_price_per_sqft_median'] * census_tract_land_price_per_sqft['census_tract_land_percentage']
census_tract_land_price_per_sqft['census_tract_land_price_per_sqft_temp_mean'] = census_tract_land_price_per_sqft['census_tract_total_price_per_sqft_mean'] * census_tract_land_price_per_sqft['census_tract_land_percentage']
# For tracts with less than 10 residential parcels, use values from a different nearby tract instead
census_tract_land_price_per_sqft['centroid'] = census_tract_land_price_per_sqft.geometry.centroid
census_tract_land_price_per_sqft.set_geometry('centroid', inplace=True)
census_tract_land_price_per_sqft.drop(columns='geometry', inplace=True)
census_tract_land_price_per_sqft_valid = census_tract_land_price_per_sqft[census_tract_land_price_per_sqft['residential_parcel_count'] > 10][['census_tract', 'centroid', 'census_tract_land_price_per_sqft_temp_median', 'census_tract_land_price_per_sqft_temp_mean']]
census_tract_land_price_per_sqft_valid.rename(columns={'census_tract': 'nearest_valid_census_tract'}, inplace=True)
census_tract_land_price_per_sqft_valid.rename(columns={'census_tract_land_price_per_sqft_temp_median': 'census_tract_land_price_per_sqft_median'}, inplace=True)
census_tract_land_price_per_sqft_valid.rename(columns={'census_tract_land_price_per_sqft_temp_mean': 'census_tract_land_price_per_sqft_mean'}, inplace=True)
census_tract_land_price_per_sqft = gpd.sjoin_nearest(census_tract_land_price_per_sqft, census_tract_land_price_per_sqft_valid, how='left', rsuffix='nearest')
census_tract_land_price_per_sqft.to_csv('census_tract_land_price_per_sqft.csv', index=False)
census_tract_land_price_per_sqft = census_tract_land_price_per_sqft[['census_tract','census_tract_total_price_per_sqft_median','census_tract_total_price_per_sqft_mean','census_tract_land_percentage','census_tract_land_price_per_sqft_median','census_tract_land_price_per_sqft_mean']]
parcel_data = parcel_data.merge(census_tract_land_price_per_sqft, how='left', left_on=['census_tract'], right_on=['census_tract'])
parcel_data['census_tract_lycd_land_prediction_median'] = parcel_data['land_area_sqft'] * parcel_data['census_tract_land_price_per_sqft_median']
parcel_data['census_tract_lycd_land_prediction_mean'] = parcel_data['land_area_sqft'] * parcel_data['census_tract_land_price_per_sqft_mean']

for i, row in parcel_data.iterrows():
    # For vacant parcels and parcels where our estimated land value is greater than the total value, just use the land value as the total
    if row['is_vacant'] == "True" or row['census_tract_lycd_land_prediction_mean'] > row['total_prediction']:
        parcel_data.at[i, 'total_prediction'] = row['census_tract_lycd_land_prediction_mean']

for i, row in parcel_data.iterrows():
    muni = row['MUNIDESC'].replace("  ", " ")
    if "Ward - " in muni:
        muni = muni.split("Ward - ")[1]
    parcel_data.at[i, 'municipality'] = muni
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
            if row['assessed_total'] > 0 and row['total_prediction'] > 0:
                parcel_data.at[i, 'ASSESSMENT_RATIO'] = (row['total_prediction'] / (row['assessed_total'] * total_residential_assessment_ratio))
            if row['SALEDESC'] == 'VALID SALE' and sale_date.year >= 2024 and row['total_prediction'] > 0 and row['SALEPRICE'] > 0:
                parcel_data.at[i, 'NEW_SALES_RATIO'] = (row['total_prediction'] / (row['SALEPRICE']))
                parcel_data.at[i, 'OLD_SALES_RATIO'] = ((row['assessed_total'] * total_residential_assessment_ratio) / (row['SALEPRICE']))

# Land price per sqft under current assessment, scaled for comparison with new assessments
parcel_data['current_land_price_per_sqft_adjusted'] = (parcel_data['assessed_land'] / parcel_data['land_area_sqft']) * total_residential_assessment_ratio

assessment_ratios = parcel_data[(parcel_data['ASSESSMENT_RATIO'] > 0) | (parcel_data['ASSESSMENT_RATIO'] < 0)]
neighborhood_assessment_ratios = assessment_ratios.groupby(['NEIGHCODE'])['ASSESSMENT_RATIO'].median().reset_index()
neighborhood_assessment_ratios.rename(columns={'ASSESSMENT_RATIO': 'neighborhood_assessment_ratio'}, inplace=True)
parcel_data = parcel_data.merge(neighborhood_assessment_ratios, how='left', left_on=['NEIGHCODE'], right_on=['NEIGHCODE'])
census_tract_assessment_ratios = assessment_ratios.groupby(['census_tract'])['ASSESSMENT_RATIO'].median().reset_index()
census_tract_assessment_ratios.rename(columns={'ASSESSMENT_RATIO': 'census_tract_assessment_ratio'}, inplace=True)
parcel_data = parcel_data.merge(census_tract_assessment_ratios, how='left', left_on=['census_tract'], right_on=['census_tract'])
school_district_assessment_ratios = assessment_ratios.groupby(['school_district'])['ASSESSMENT_RATIO'].median().reset_index()
school_district_assessment_ratios.rename(columns={'ASSESSMENT_RATIO': 'school_district_assessment_ratio'}, inplace=True)
parcel_data = parcel_data.merge(school_district_assessment_ratios, how='left', left_on=['school_district'], right_on=['school_district'])
school_district_assessment_ratios.to_csv("school_district_assessment_ratios.csv", index=False)
municipality_assessment_ratios = assessment_ratios.groupby(['municipality'])['ASSESSMENT_RATIO'].median().reset_index()
municipality_assessment_ratios.rename(columns={'ASSESSMENT_RATIO': 'municipality_assessment_ratio'}, inplace=True)
parcel_data = parcel_data.merge(municipality_assessment_ratios, how='left', left_on=['municipality'], right_on=['municipality'])
municipality_assessment_ratios.to_csv("municipality_assessment_ratios.csv", index=False)
city_council_district_assessment_ratios = assessment_ratios.groupby(['city_council_district'])['ASSESSMENT_RATIO'].median().reset_index()
city_council_district_assessment_ratios.rename(columns={'ASSESSMENT_RATIO': 'city_council_district_assessment_ratio'}, inplace=True)
parcel_data = parcel_data.merge(city_council_district_assessment_ratios, how='left', left_on=['city_council_district'], right_on=['city_council_district'])
city_council_district_assessment_ratios.to_csv("city_council_district_assessment_ratios.csv", index=False)
county_council_district_assessment_ratios = assessment_ratios.groupby(['county_council_district'])['ASSESSMENT_RATIO'].median().reset_index()
county_council_district_assessment_ratios.rename(columns={'ASSESSMENT_RATIO': 'county_council_district_assessment_ratio'}, inplace=True)
parcel_data = parcel_data.merge(county_council_district_assessment_ratios, how='left', left_on=['county_council_district'], right_on=['county_council_district'])
county_council_district_assessment_ratios.to_csv("county_council_district_assessment_ratios.csv", index=False)

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

parcel_geometry = parcel_geometry.to_crs('EPSG:3857')
parcel_geometry_assessments = parcel_geometry[['PARCEL_ID','geometry']]
parcel_geometry_assessments = parcel_geometry_assessments.merge(parcel_data, left_on=['PARCEL_ID'], right_on=['PARID'])

parcel_data.to_csv("predictions.csv", index=False)
parcel_geometry_assessments.to_parquet('predictions.parquet')

parcel_data[parcel_data['CLASS'] == 'R'].to_csv("residential_predictions.csv", header=['PARCEL_ID', 'USE_DESCRIPTION', 'MUNICIPALITY', 'SCHOOL_DISTRICT', 'LAND_AREA_SQFT', 'BUILDING_AREA_SQFT', 'CURRENT_ASSESSMENT_LAND', 'CURRENT_ASSESSMENT_TOTAL', 'NEW_ASSESSMENT_LAND', 'NEW_ASSESSMENT_TOTAL', 'VALUATION_RATIO'], columns=['PARID', 'USEDESC', 'municipality', 'school_district', 'land_area_sqft', 'building_area', 'assessed_land', 'assessed_total', 'census_tract_lycd_land_prediction_mean', 'total_prediction', 'ASSESSMENT_RATIO'], index=False)
parcel_data[parcel_data['CLASS'] != 'R'].to_csv("commercial_existing_valuations.csv", header=['PARCEL_ID', 'USE_DESCRIPTION', 'MUNICIPALITY', 'SCHOOL_DISTRICT', 'LAND_AREA_SQFT', 'CURRENT_ASSESSMENT_LAND', 'CURRENT_ASSESSMENT_TOTAL'], columns=['PARID', 'USEDESC', 'municipality', 'school_district', 'land_area_sqft', 'assessed_land', 'assessed_total'], index=False)
