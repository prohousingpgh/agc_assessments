import requests
import json
from bs4 import BeautifulSoup
import sys
import pandas as pd
import geopandas as gpd
import math

crexi_data = pd.DataFrame(columns=['PARCEL_ID', 'ADDRESS_COUNT', 'BUILDING_COUNT', 'UNIT_COUNT', 'BUILDING_FOOTPRINT', 'BUILDING_AREA', 'DESCRIPTION', 'TYPE'])
for i in range(1, 155):
    with open('crexi_data/' + str(i) + '.json') as f:
        parsed_json = json.load(f)
        locations = {}
        for entry in parsed_json['items']:
            buildings_count = 0
            address_count = 0
            footprint_sqft = 0
            description = ''
            building_sqft = 0
            unit_count = 0
            property_type = ''
            parcel_id = ''
            if 'buildingsCount' in entry['propertyAttributes']:
                buildings_count = entry['propertyAttributes']['buildingsCount']
            if 'addressCount' in entry['propertyAttributes']:
                address_count = entry['propertyAttributes']['addressCount']
            if 'footprintSqft' in entry['propertyAttributes']:
                footprint_sqft = entry['propertyAttributes']['footprintSqft']
            if 'structureDescription' in entry['propertyAttributes']:
                description = entry['propertyAttributes']['structureDescription']
            if 'buildingSqft' in entry['propertyAttributes']:
                building_sqft = entry['propertyAttributes']['buildingSqft']
            if 'unitsCount' in entry['propertyAttributes']:
                units_count = entry['propertyAttributes']['unitsCount']
            if 'type' in entry['propertyAttributes']:
                property_type = entry['propertyAttributes']['type']
            if 'apn' in entry['address'][0]:
                parcel_id = entry['address'][0]['apn'].replace("-", "")
            crexi_data.loc[len(crexi_data)] = [parcel_id, address_count, buildings_count, units_count, footprint_sqft, building_sqft, description, property_type]

crexi_data.to_csv("crexi_data.csv", index=False, )
