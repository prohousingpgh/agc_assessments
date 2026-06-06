import pandas as pd
import sys
import os

# Check for diffs between historical records from https://data.wprdc.org/dataset/property-assessments and appeals from https://data.wprdc.org/dataset/allegheny-county-property-assessment-appeals

file_list = os.listdir('historical_assessments')
changes_df = pd.DataFrame(columns=['PARCEL_ID','FIELD_NAMES','OLD_VALUES','NEW_VALUES','CHANGE_DATE_START','CHANGE_DATE_END'])
appeals = pd.read_csv('appeals.csv')
appeals.rename(columns={'PARCEL ID': 'PARCEL_ID'}, inplace=True)
appeals.set_index('PARCEL_ID', inplace=True)

for i in range(len(file_list) - 1):
    parcel_data_1 = pd.read_csv(os.path.join('historical_assessments', file_list[i]), dtype={'PARID': str, 'PROPERTYHOUSENUM': str, 'PROPERTYFRACTION': str, 'PROPERTYADDRESS': str, 'PROPERTYCITY': str, 'PROPERTYSTATE': str, 'PROPERTYUNIT': str, 'PROPERTYZIP': str, 'MUNICODE': str, 'MUNIDESC': str, 'SCHOOLCODE': str, 'SCHOOLDESC': str, 'LEGAL1': str, 'LEGAL2': str, 'LEGAL3': str, 'NEIGHCODE': str, 'NEIGHDESC': str, 'TAXCODE': str, 'TAXDESC': str, 'TAXSUBCODE': str, 'TAXSUBCODE_DESC': str, 'OWNERCODE': str, 'OWNERDESC': str, 'CLASS': str, 'CLASSDESC': str, 'USECODE': str, 'USEDESC': str, 'LOTAREA': str, 'HOMESTEADFLAG': str, 'FARMSTEADFLAG': str, 'CLEANGREEN': str, 'ABATEMENTFLAG': str, 'RECORDDATE': str, 'SALEDATE': str, 'SALEPRICE': str, 'SALECODE': str, 'SALEDESC': str, 'DEEDBOOK': str, 'DEEDPAGE': str, 'PREVSALEDATE': str, 'PREVSALEPRICE': str, 'PREVSALEDATE2': str, 'PREVSALEPRICE2': str, 'CHANGENOTICEADDRESS1': str, 'CHANGENOTICEADDRESS2': str, 'CHANGENOTICEADDRESS3': str, 'CHANGENOTICEADDRESS4': str, 'COUNTYBUILDING': str, 'COUNTYLAND': str, 'COUNTYTOTAL': str, 'COUNTYEXEMPTBLDG': str, 'LOCALBUILDING': str, 'LOCALLAND': str, 'LOCALTOTAL': str, 'FAIRMARKETBUILDING': str, 'FAIRMARKETLAND': str, 'FAIRMARKETTOTAL': str, 'STYLE': str, 'STYLEDESC': str, 'STORIES': str, 'YEARBLT': str, 'EXTERIORFINISH': str, 'EXTFINISH_DESC': str, 'ROOF': str, 'ROOFDESC': str, 'BASEMENT': str, 'BASEMENTDESC': str, 'GRADE': str, 'GRADEDESC': str, 'CONDITION': str, 'CONDITIONDESC': str, 'CDU': str, 'CDUDESC': str, 'TOTALROOMS': str, 'BEDROOMS': str, 'FULLBATHS': str, 'HALFBATHS': str, 'HEATINGCOOLING': str, 'HEATINGCOOLINGDESC': str, 'FIREPLACES': str, 'BSMTGARAGE': str, 'FINISHEDLIVINGAREA': str, 'CARDNUMBER': str, 'ALT_ID': str, 'TAXYEAR': str, 'ASOFDATE': str})
    parcel_data_2 = pd.read_csv(os.path.join('historical_assessments', file_list[i + 1]), dtype={'PARID': str, 'PROPERTYHOUSENUM': str, 'PROPERTYFRACTION': str, 'PROPERTYADDRESS': str, 'PROPERTYCITY': str, 'PROPERTYSTATE': str, 'PROPERTYUNIT': str, 'PROPERTYZIP': str, 'MUNICODE': str, 'MUNIDESC': str, 'SCHOOLCODE': str, 'SCHOOLDESC': str, 'LEGAL1': str, 'LEGAL2': str, 'LEGAL3': str, 'NEIGHCODE': str, 'NEIGHDESC': str, 'TAXCODE': str, 'TAXDESC': str, 'TAXSUBCODE': str, 'TAXSUBCODE_DESC': str, 'OWNERCODE': str, 'OWNERDESC': str, 'CLASS': str, 'CLASSDESC': str, 'USECODE': str, 'USEDESC': str, 'LOTAREA': str, 'HOMESTEADFLAG': str, 'FARMSTEADFLAG': str, 'CLEANGREEN': str, 'ABATEMENTFLAG': str, 'RECORDDATE': str, 'SALEDATE': str, 'SALEPRICE': str, 'SALECODE': str, 'SALEDESC': str, 'DEEDBOOK': str, 'DEEDPAGE': str, 'PREVSALEDATE': str, 'PREVSALEPRICE': str, 'PREVSALEDATE2': str, 'PREVSALEPRICE2': str, 'CHANGENOTICEADDRESS1': str, 'CHANGENOTICEADDRESS2': str, 'CHANGENOTICEADDRESS3': str, 'CHANGENOTICEADDRESS4': str, 'COUNTYBUILDING': str, 'COUNTYLAND': str, 'COUNTYTOTAL': str, 'COUNTYEXEMPTBLDG': str, 'LOCALBUILDING': str, 'LOCALLAND': str, 'LOCALTOTAL': str, 'FAIRMARKETBUILDING': str, 'FAIRMARKETLAND': str, 'FAIRMARKETTOTAL': str, 'STYLE': str, 'STYLEDESC': str, 'STORIES': str, 'YEARBLT': str, 'EXTERIORFINISH': str, 'EXTFINISH_DESC': str, 'ROOF': str, 'ROOFDESC': str, 'BASEMENT': str, 'BASEMENTDESC': str, 'GRADE': str, 'GRADEDESC': str, 'CONDITION': str, 'CONDITIONDESC': str, 'CDU': str, 'CDUDESC': str, 'TOTALROOMS': str, 'BEDROOMS': str, 'FULLBATHS': str, 'HALFBATHS': str, 'HEATINGCOOLING': str, 'HEATINGCOOLINGDESC': str, 'FIREPLACES': str, 'BSMTGARAGE': str, 'FINISHEDLIVINGAREA': str, 'CARDNUMBER': str, 'ALT_ID': str, 'TAXYEAR': str, 'ASOFDATE': str})

    parcel_data_1.rename(columns={'PARID': 'PARCEL_ID'}, inplace=True)
    parcel_data_2.rename(columns={'PARID': 'PARCEL_ID'}, inplace=True)
    parcel_data_1['UNIQUE_ID'] = parcel_data_1['PARCEL_ID']
    parcel_data_2['UNIQUE_ID'] = parcel_data_2['PARCEL_ID']
    parcel_data_1.set_index('UNIQUE_ID', inplace=True)
    parcel_data_2.set_index('UNIQUE_ID', inplace=True)

    attributes = ['STYLE', 'STYLEDESC', 'STORIES', 'YEARBLT', 'EXTERIORFINISH', 'EXTFINISH_DESC', 'ROOF', 'ROOFDESC', 'BASEMENT', 'BASEMENTDESC', 'GRADE', 'GRADEDESC', 'CONDITION', 'CONDITIONDESC', 'CDU', 'CDUDESC', 'TOTALROOMS', 'BEDROOMS', 'FULLBATHS', 'HALFBATHS', 'HEATINGCOOLING', 'HEATINGCOOLINGDESC', 'FIREPLACES', 'BSMTGARAGE', 'FINISHEDLIVINGAREA']
    assessments = ['COUNTYBUILDING', 'COUNTYLAND', 'COUNTYTOTAL', 'COUNTYEXEMPTBLDG', 'LOCALBUILDING', 'LOCALLAND', 'LOCALTOTAL', 'FAIRMARKETBUILDING', 'FAIRMARKETLAND', 'FAIRMARKETTOTAL']
    changed_parcels = []
    count = 0
    for index, row in parcel_data_1.iterrows():
        count += 1
        if count % 10000 == 0:
            print('file', i, count, 'entries processed')
        if row['PARCEL_ID'] in parcel_data_2.index:
            entry_1 = row
            entry_2 = parcel_data_2.loc[row['PARCEL_ID']]
            changed_assessments = []
            changed_attributes = []
            old_values = []
            new_values = []
            for attribute in assessments:
                if entry_1[attribute] == entry_1[attribute] and entry_2[attribute] == entry_2[attribute] and entry_1[attribute] != entry_2[attribute]:
                    changed_assessments.append(attribute)
            for attribute in attributes:
                if entry_1[attribute] == entry_1[attribute] and entry_2[attribute] == entry_2[attribute] and entry_1[attribute] != entry_2[attribute]:
                    changed_parcels.append(row['PARCEL_ID'])
                    changed_attributes.append(attribute)
                    old_values.append(entry_1[attribute])
                    new_values.append(entry_2[attribute])
            if len(changed_attributes) > 0:
                changes_df.loc[len(changes_df)] = [row['PARCEL_ID'], changed_attributes, old_values, new_values, entry_1['ASOFDATE'], entry_2['ASOFDATE']]
merged_df = changes_df.merge(appeals, on='PARCEL_ID', how='outer')
merged_df.to_csv('changes_data.csv', index=False)
