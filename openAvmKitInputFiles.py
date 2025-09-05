import geopandas as gpd
import pandas as pd
import numpy as np
import sys

parcel_data = pd.read_csv(sys.argv[1], dtype={'PARID': str, 'PROPERTYHOUSENUM': str, 'PROPERTYFRACTION': str, 'PROPERTYADDRESS': str, 'PROPERTYCITY': str, 'PROPERTYSTATE': str, 'PROPERTYUNIT': str, 'PROPERTYZIP': str, 'MUNICODE': str, 'MUNIDESC': str, 'SCHOOLCODE': str, 'SCHOOLDESC': str, 'LEGAL1': str, 'LEGAL2': str, 'LEGAL3': str, 'NEIGHCODE': str, 'NEIGHDESC': str, 'TAXCODE': str, 'TAXDESC': str, 'TAXSUBCODE': str, 'TAXSUBCODE_DESC': str, 'OWNERCODE': str, 'OWNERDESC': str, 'CLASS': str, 'CLASSDESC': str, 'USECODE': str, 'USEDESC': str, 'LOTAREA': str, 'HOMESTEADFLAG': str, 'FARMSTEADFLAG': str, 'CLEANGREEN': str, 'ABATEMENTFLAG': str, 'RECORDDATE': str, 'SALEDATE': str, 'SALEPRICE': str, 'SALECODE': str, 'SALEDESC': str, 'DEEDBOOK': str, 'DEEDPAGE': str, 'PREVSALEDATE': str, 'PREVSALEPRICE': str, 'PREVSALEDATE2': str, 'PREVSALEPRICE2': str, 'CHANGENOTICEADDRESS1': str, 'CHANGENOTICEADDRESS2': str, 'CHANGENOTICEADDRESS3': str, 'CHANGENOTICEADDRESS4': str, 'COUNTYBUILDING': str, 'COUNTYLAND': str, 'COUNTYTOTAL': str, 'COUNTYEXEMPTBLDG': str, 'LOCALBUILDING': str, 'LOCALLAND': str, 'LOCALTOTAL': str, 'FAIRMARKETBUILDING': str, 'FAIRMARKETLAND': str, 'FAIRMARKETTOTAL': str, 'STYLE': str, 'STYLEDESC': str, 'STORIES': str, 'YEARBLT': str, 'EXTERIORFINISH': str, 'EXTFINISH_DESC': str, 'ROOF': str, 'ROOFDESC': str, 'BASEMENT': str, 'BASEMENTDESC': str, 'GRADE': str, 'GRADEDESC': str, 'CONDITION': str, 'CONDITIONDESC': str, 'CDU': str, 'CDUDESC': str, 'TOTALROOMS': str, 'BEDROOMS': str, 'FULLBATHS': str, 'HALFBATHS': str, 'HEATINGCOOLING': str, 'HEATINGCOOLINGDESC': str, 'FIREPLACES': str, 'BSMTGARAGE': str, 'FINISHEDLIVINGAREA': str, 'CARDNUMBER': str, 'ALT_ID': str, 'TAXYEAR': str, 'ASOFDATE': str})
parcel_geometry = gpd.read_file(sys.argv[2])
census_tracts = gpd.read_file(sys.argv[3])

sales_data_1 = parcel_data[['PARID','RECORDDATE','SALEDATE','SALEPRICE','SALECODE','SALEDESC','DEEDBOOK','DEEDPAGE','CHANGENOTICEADDRESS1','CHANGENOTICEADDRESS2','CHANGENOTICEADDRESS3','CHANGENOTICEADDRESS4','USECODE','USEDESC']].copy()
sales_data = sales_data_1[~sales_data_1['SALEDATE'].isnull()].copy()
sales_data['SALECODE'] = sales_data['SALECODE'] + ' ' + sales_data['SALEDESC']
sales_data['USE'] = sales_data['USECODE'] + ' ' + sales_data['USEDESC']
sales_data['SALEYEAR'] = sales_data['SALEDATE'].str.slice(6, 10)
sales_data.rename(columns={'PARID': 'PARCEL_ID'}, inplace=True)

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
parcel_data['CONDITION'] = parcel_data['CONDITION'] + ' ' + parcel_data['CONDITIONDESC']
parcel_data['CDU'] = parcel_data['CDU'] + ' ' + parcel_data['CDUDESC']
parcel_data['HEATINGCOOLING'] = parcel_data['HEATINGCOOLING'] + ' ' + parcel_data['HEATINGCOOLINGDESC']
parcel_data.rename(columns={'PARID': 'PARCEL_ID'}, inplace=True)
vacant_codes = ["098 CONDEMNED/BOARDED-UP", "100 VACANT LAND", "110 >10 ACRES VACANT", "111 BUILDERS LOT", "300 VACANT INDUSTRIAL LAND", "400 VACANT COMMERCIAL LAND", "500 RESIDENTIAL VACANT LAND", "998 TOTAL/MAJOR FIRE DAMAGE - COMM", "999 UNLOCATED PARCEL"]
parcel_data['FINISHEDAREA'] = np.where(parcel_data['USE'].isin(vacant_codes), 0, 1)

parcel_geometry.rename(columns={'PIN': 'PARCEL_ID'}, inplace=True)
census_tracts.rename(columns={'NAME': 'CENSUS_TRACT'}, inplace=True)

pd.set_option('display.max_columns', None)
print(parcel_data.head())
print(census_tracts.head())
print(sales_data.head())
print(parcel_data.head())

parcel_data.to_csv("parcels.csv", index=False, columns=["PARCEL_ID", "ADDRESS", "PROPERTYCITY", "PROPERTYSTATE", "PROPERTYZIP", "MUNICIPALITY", "SCHOOL", "LEGAL", "NEIGHBORHOOD", "TAXCODE", "TAXSUBCODE", "OWNER", "CLASS", "USE", "LOTAREA", "HOMESTEADFLAG", "FARMSTEADFLAG", "CLEANGREEN", "ABATEMENTFLAG", "COUNTYBUILDING", "COUNTYLAND", "COUNTYTOTAL", "COUNTYEXEMPTBLDG", "LOCALBUILDING", "LOCALLAND", "LOCALTOTAL", "FAIRMARKETBUILDING", "FAIRMARKETLAND", "FAIRMARKETTOTAL", "STYLE", "STORIES", "YEARBLT", "EXTERIORFINISH", "ROOF", "BASEMENT", "GRADE", "CONDITION", "CDU", "TOTALROOMS", "BEDROOMS", "FULLBATHS", "HALFBATHS", "HEATINGCOOLING", "FIREPLACES", "BSMTGARAGE", "FINISHEDLIVINGAREA", "CARDNUMBER", "ALT_ID", "FINISHEDAREA"])
sales_data.to_csv("sales.csv", index=False, columns=["PARCEL_ID", "RECORDDATE", "SALEDATE", "SALEPRICE", "SALECODE", "DEEDBOOK", "DEEDPAGE", "CHANGENOTICEADDRESS1", "CHANGENOTICEADDRESS2", "CHANGENOTICEADDRESS3", "CHANGENOTICEADDRESS4", "USE", "SALEYEAR"])
parcel_geometry.to_parquet('parcels.parquet')
census_tracts.to_parquet('census_tracts.parquet')
