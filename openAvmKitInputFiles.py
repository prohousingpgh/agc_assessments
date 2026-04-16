import geopandas as gpd
import pandas as pd
import numpy as np
import sys

grade_to_num_map = {
    "XX+ Highest Cost +": 21,
    "XX Highest Cost": 20,
    "XX minus HIGHEST COST -": 19,
    "X+ EXCELLENT +": 18,
    "X EXCELLENT": 17,
    "X minus EXCELLENT -": 16,
    "A+ VERY GOOD +": 15,
    "A VERY GOOD": 14,
    "A minus VERY GOOD -": 13,
    "B+ GOOD +": 12,
    "B GOOD": 11,
    "B minus GOOD -": 10,
    "C+ AVERAGE +": 9,
    "C AVERAGE": 8,
    "C minus AVERAGE -": 7,
    "D+ BELOW AVERAGE +": 6,
    "D BELOW AVERAGE": 5,
    "D minus BELOW AVERAGE -": 4,
    "E+ POOR +": 3,
    "E POOR": 2,
    "E minus POOR -": 1
}
condition_to_num_map = {
    "1 EXCELLENT": 8,
    "7 VERY GOOD": 7,
    "2 GOOD": 6,
    "3 AVERAGE": 5,
    "4 FAIR": 4,
    "5 POOR": 3,
    "8 VERY POOR": 2,
    "6 UNSOUND": 1
}

parcel_data = pd.read_csv(sys.argv[1], dtype={'PARID': str, 'PROPERTYHOUSENUM': str, 'PROPERTYFRACTION': str, 'PROPERTYADDRESS': str, 'PROPERTYCITY': str, 'PROPERTYSTATE': str, 'PROPERTYUNIT': str, 'PROPERTYZIP': str, 'MUNICODE': str, 'MUNIDESC': str, 'SCHOOLCODE': str, 'SCHOOLDESC': str, 'LEGAL1': str, 'LEGAL2': str, 'LEGAL3': str, 'NEIGHCODE': str, 'NEIGHDESC': str, 'TAXCODE': str, 'TAXDESC': str, 'TAXSUBCODE': str, 'TAXSUBCODE_DESC': str, 'OWNERCODE': str, 'OWNERDESC': str, 'CLASS': str, 'CLASSDESC': str, 'USECODE': str, 'USEDESC': str, 'LOTAREA': str, 'HOMESTEADFLAG': str, 'FARMSTEADFLAG': str, 'CLEANGREEN': str, 'ABATEMENTFLAG': str, 'RECORDDATE': str, 'SALEDATE': str, 'SALEPRICE': str, 'SALECODE': str, 'SALEDESC': str, 'DEEDBOOK': str, 'DEEDPAGE': str, 'PREVSALEDATE': str, 'PREVSALEPRICE': str, 'PREVSALEDATE2': str, 'PREVSALEPRICE2': str, 'CHANGENOTICEADDRESS1': str, 'CHANGENOTICEADDRESS2': str, 'CHANGENOTICEADDRESS3': str, 'CHANGENOTICEADDRESS4': str, 'COUNTYBUILDING': str, 'COUNTYLAND': str, 'COUNTYTOTAL': str, 'COUNTYEXEMPTBLDG': str, 'LOCALBUILDING': str, 'LOCALLAND': str, 'LOCALTOTAL': str, 'FAIRMARKETBUILDING': str, 'FAIRMARKETLAND': str, 'FAIRMARKETTOTAL': str, 'STYLE': str, 'STYLEDESC': str, 'STORIES': str, 'YEARBLT': str, 'EXTERIORFINISH': str, 'EXTFINISH_DESC': str, 'ROOF': str, 'ROOFDESC': str, 'BASEMENT': str, 'BASEMENTDESC': str, 'GRADE': str, 'GRADEDESC': str, 'CONDITION': str, 'CONDITIONDESC': str, 'CDU': str, 'CDUDESC': str, 'TOTALROOMS': str, 'BEDROOMS': str, 'FULLBATHS': str, 'HALFBATHS': str, 'HEATINGCOOLING': str, 'HEATINGCOOLINGDESC': str, 'FIREPLACES': str, 'BSMTGARAGE': str, 'FINISHEDLIVINGAREA': str, 'CARDNUMBER': str, 'ALT_ID': str, 'TAXYEAR': str, 'ASOFDATE': str})
parcel_geometry = gpd.read_file(sys.argv[2])
census_tracts = gpd.read_file(sys.argv[3])
commercial_rents = pd.read_csv(sys.argv[4], dtype={'PARCEL_ID': str, 'PRICE': float, 'IS_VACANT': bool})
commercial_rents = commercial_rents[commercial_rents['IS_VACANT'] == False]
commercial_rents = commercial_rents[commercial_rents['PRICE'] > 0]
market_value = gpd.read_file(sys.argv[5])
steep_slopes = gpd.read_file(sys.argv[6])
flood_zones = gpd.read_file(sys.argv[7])
undermined = gpd.read_file(sys.argv[8])
city_boundary = gpd.read_file(sys.argv[9])
crexi_data = gpd.read_file(sys.argv[10])
city_council_districts = gpd.read_file(sys.argv[11])
county_council_districts = gpd.read_file(sys.argv[12])

parcel_data.rename(columns={'PARID': 'PARCEL_ID'}, inplace=True)
parcel_geometry.rename(columns={'PIN': 'PARCEL_ID'}, inplace=True)
census_tracts.rename(columns={'NAME': 'CENSUS_TRACT'}, inplace=True)
market_value.rename(columns={'MVA21': 'MARKET_VALUE'}, inplace=True)
steep_slopes.rename(columns={'slope25': 'STEEP_SLOPE'}, inplace=True)
flood_zones.rename(columns={'fld_zone': 'FLOOD_ZONE'}, inplace=True)
undermined.rename(columns={'undermined': 'UNDERMINED'}, inplace=True)
city_council_districts.rename(columns={'DIST_NAME': 'CITY_COUNCIL_DISTRICT'}, inplace=True)
county_council_districts.rename(columns={'LABEL': 'COUNTY_COUNCIL_DISTRICT'}, inplace=True)

commercial_rents_gdf = gpd.GeoDataFrame(
    commercial_rents, geometry=gpd.points_from_xy(commercial_rents['LONGITUDE'], commercial_rents['LATITUDE']), crs="EPSG:4326"
)

sales_data_1 = parcel_data[['PARCEL_ID','RECORDDATE','SALEDATE','SALEPRICE','SALECODE','SALEDESC','DEEDBOOK','DEEDPAGE','CHANGENOTICEADDRESS1','CHANGENOTICEADDRESS2','CHANGENOTICEADDRESS3','CHANGENOTICEADDRESS4','USECODE','USEDESC','CLASS','CLASSDESC']].copy()
sales_data = sales_data_1[~sales_data_1['SALEDATE'].isnull()].copy()
sales_data['SALECODE'] = sales_data['SALECODE'] + ' ' + sales_data['SALEDESC']
sales_data['USE'] = sales_data['USECODE'] + ' ' + sales_data['USEDESC']
sales_data['SALEYEAR'] = sales_data['SALEDATE'].str.slice(6, 10)
sales_data['CLASS'] = sales_data['CLASS'] + ' ' + sales_data['CLASSDESC']
vacant_codes = ["098 CONDEMNED/BOARDED-UP", "100 VACANT LAND", "110 >10 ACRES VACANT", "111 BUILDERS LOT", "300 VACANT INDUSTRIAL LAND", "400 VACANT COMMERCIAL LAND", "500 RESIDENTIAL VACANT LAND", "998 TOTAL/MAJOR FIRE DAMAGE - COMM", "999 UNLOCATED PARCEL"]
sales_data['FINISHEDAREA'] = np.where(sales_data['USE'].isin(vacant_codes), 0, 1)

parcel_data['ADDRESS'] = parcel_data['PROPERTYHOUSENUM'] + ' ' + parcel_data['PROPERTYFRACTION'] + ' ' + parcel_data['PROPERTYADDRESS'] + ' ' + parcel_data['PROPERTYUNIT']
parcel_data['MUNICIPALITY'] = parcel_data['MUNICODE'] + ' ' + parcel_data['MUNIDESC']
parcel_data['SCHOOL'] = parcel_data['SCHOOLCODE'] + ' ' + parcel_data['SCHOOLDESC']
parcel_data['LEGAL'] = parcel_data['LEGAL1'] + ' ' + parcel_data['LEGAL2'] + ' ' + parcel_data['LEGAL3']
parcel_data['NEIGHBORHOOD'] = parcel_data['NEIGHCODE'] + ' ' + parcel_data['NEIGHDESC']
parcel_data['TAXCODE'] = parcel_data['TAXCODE'] + ' ' + parcel_data['TAXDESC']
parcel_data['TAXSUBCODE'] = parcel_data['TAXSUBCODE'] + ' ' + parcel_data['TAXSUBCODE_DESC']
parcel_data['OWNER'] = parcel_data['OWNERCODE'] + ' ' + parcel_data['OWNERDESC']
parcel_data['CLASS'] = parcel_data['CLASS'] + ' ' + parcel_data['CLASSDESC']
parcel_data['USE'] = parcel_data['USECODE'] + ' ' + parcel_data['USEDESC']
parcel_data['STYLE'] = parcel_data['STYLE'] + ' ' + parcel_data['STYLEDESC']
parcel_data['EXTERIORFINISH'] = parcel_data['EXTERIORFINISH'] + ' ' + parcel_data['EXTFINISH_DESC']
parcel_data['ROOF'] = parcel_data['ROOF'] + ' ' + parcel_data['ROOFDESC']
parcel_data['BASEMENT'] = parcel_data['BASEMENT'] + ' ' + parcel_data['BASEMENTDESC']
parcel_data['GRADE'] = parcel_data['GRADE'].str.replace("-", " minus") + ' ' + parcel_data['GRADEDESC']
parcel_data['GRADENUM'] = parcel_data['GRADE'].map(grade_to_num_map)
parcel_data['CONDITION'] = parcel_data['CONDITION'] + ' ' + parcel_data['CONDITIONDESC']
parcel_data['CONDITIONNUM'] = parcel_data['CONDITION'].map(condition_to_num_map)
parcel_data['CDU'] = parcel_data['CDU'] + ' ' + parcel_data['CDUDESC']
parcel_data['HEATINGCOOLING'] = parcel_data['HEATINGCOOLING'] + ' ' + parcel_data['HEATINGCOOLINGDESC']
parcel_data['FINISHEDAREA'] = np.where(parcel_data['USE'].isin(vacant_codes), 0, 1)
parcel_data['COMMERCIALRENT'] = pd.Series(dtype='float')
parcel_data['IS_PITTSBURGH_SD'] = [1 if x == '47 Pittsburgh' else 0 for x in parcel_data['SCHOOL']]
parcel_geometry_distance = parcel_geometry.to_crs('EPSG:3857')
parcel_geometry_area = parcel_geometry.to_crs('EPSG:6933')
parcel_geometry_area['PARCEL_AREA'] = parcel_geometry_area.geometry.area * 10.76391
commercial_rents_gdf = commercial_rents_gdf.to_crs('EPSG:3857')

parcel_geometry_calculations = pd.merge(parcel_geometry_area, parcel_geometry_distance, on='PARCEL_ID', suffixes=('_area', '_distance'))
parcel_data = pd.merge(parcel_data, parcel_geometry_calculations, how='left', on='PARCEL_ID')
parcel_data = pd.merge(parcel_data, crexi_data, how='left', on='PARCEL_ID')
count = 0
for i, row in parcel_data.iterrows():
    count += 1
    if count % 1000 == 0:
        print(count, 'entries processed')
    if row['geometry_distance'] is not None:
        geometry_distance = row['geometry_distance']
        # Get commercial rent for non-residential parcels
        if row['CLASS'] != 'R RESIDENTIAL':
            distances = commercial_rents_gdf.distance(geometry_distance)
            distances.sort_values(ascending=True, inplace=True)
            values_list = []
            for parcel_id, distance in distances.items():
                # Average together at least 1 but no more than 5 nearest commercial rents, no more than 1 km away
                if len(values_list) >= 5 or (len(values_list) >= 1 and distance > 1000):
                    break
                values_list.append(commercial_rents_gdf.loc[parcel_id]['PRICE'])
            parcel_data.at[i, 'COMMERCIALRENT'] = sum(values_list) / float(len(values_list))
        else:
            parcel_data.at[i, 'ADDRESS_COUNT'] = None
            parcel_data.at[i, 'BUILDING_COUNT'] = None
            parcel_data.at[i, 'UNIT_COUNT'] = None
            parcel_data.at[i, 'BUILDING_FOOTPRINT'] = None
            parcel_data.at[i, 'BUILDING_AREA'] = None
            parcel_data.at[i, 'DESCRIPTION'] = None
            parcel_data.at[i, 'TYPE'] = None

pd.set_option('display.max_columns', None)
print(parcel_data.head())
print(census_tracts.head())
print(sales_data.head())
print(parcel_geometry.head())
print(market_value.head())

parcel_data.to_csv("parcels.csv", index=False, columns=["PARCEL_ID", "ADDRESS", "PROPERTYCITY", "PROPERTYSTATE", "PROPERTYZIP", "MUNICIPALITY", "SCHOOL", "LEGAL", "NEIGHBORHOOD", "TAXCODE", "TAXSUBCODE", "OWNER", "CLASS", "USE", "LOTAREA", "HOMESTEADFLAG", "FARMSTEADFLAG", "CLEANGREEN", "ABATEMENTFLAG", "COUNTYBUILDING", "COUNTYLAND", "COUNTYTOTAL", "COUNTYEXEMPTBLDG", "LOCALBUILDING", "LOCALLAND", "LOCALTOTAL", "FAIRMARKETBUILDING", "FAIRMARKETLAND", "FAIRMARKETTOTAL", "STYLE", "STORIES", "YEARBLT", "EXTERIORFINISH", "ROOF", "BASEMENT", "GRADE", "GRADENUM", "CONDITION", "CONDITIONNUM", "CDU", "TOTALROOMS", "BEDROOMS", "FULLBATHS", "HALFBATHS", "HEATINGCOOLING", "FIREPLACES", "BSMTGARAGE", "FINISHEDLIVINGAREA", "CARDNUMBER", "ALT_ID", "FINISHEDAREA", "COMMERCIALRENT", "PARCEL_AREA", "PARCEL_ID", "ADDRESS_COUNT", "BUILDING_COUNT", "UNIT_COUNT", "BUILDING_FOOTPRINT", "BUILDING_AREA", "DESCRIPTION", "TYPE", "IS_PITTSBURGH_SD"])
sales_data.to_csv("sales.csv", index=False, columns=["PARCEL_ID", "RECORDDATE", "SALEDATE", "SALEPRICE", "SALECODE", "DEEDBOOK", "DEEDPAGE", "CHANGENOTICEADDRESS1", "CHANGENOTICEADDRESS2", "CHANGENOTICEADDRESS3", "CHANGENOTICEADDRESS4", "USE", "SALEYEAR", "CLASS", "FINISHEDAREA"])
parcel_geometry.to_parquet('parcels.parquet')
census_tracts.to_parquet('census_tracts.parquet')
market_value.to_parquet('market_value.parquet')

city_boundary = city_boundary.to_crs(epsg=4326)
diff = city_boundary.union_all().difference(steep_slopes.union_all())
rest_of_pittsburgh = gpd.GeoDataFrame(data={"STEEP_SLOPE": "No", "geometry": diff}, index=[0], crs="EPSG:4326")
steep_slopes = pd.concat([steep_slopes, rest_of_pittsburgh])
steep_slopes.to_parquet('steep_slopes.parquet')

diff = city_boundary.union_all().difference(flood_zones.union_all())
rest_of_pittsburgh = gpd.GeoDataFrame(data={"FLOOD_ZONE": "No", "geometry": diff}, index=[0], crs="EPSG:4326")
flood_zones = pd.concat([flood_zones, rest_of_pittsburgh])
flood_zones.to_parquet('flood_zones.parquet')

diff = city_boundary.union_all().difference(undermined.union_all())
rest_of_pittsburgh = gpd.GeoDataFrame(data={"UNDERMINED": "No", "geometry": diff}, index=[0], crs="EPSG:4326")
undermined = pd.concat([undermined, rest_of_pittsburgh])
undermined.to_parquet('undermined.parquet')

city_council_districts.to_parquet('city_council_districts.parquet')
county_council_districts.to_parquet('county_council_districts.parquet')
