import requests
import json
from bs4 import BeautifulSoup
import sys
import pandas as pd
import geopandas as gpd
import math

def callApi(minLatitude, maxLatitude, minLongitude, maxLongitude, pageNumber):
    url = 'https://www.loopnet.com/services/search'
    headers = {'Content-Type': 'application/json;charset=UTF-8',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0'}
    centerLongitude = str((minLongitude + maxLongitude) / 2)
    centerLatitude = str((minLatitude + maxLatitude) / 2)
    minLatitude = str(minLatitude)
    maxLatitude = str(maxLatitude)
    minLongitude = str(minLongitude)
    maxLongitude = str(maxLongitude)
    pageNumber = str(pageNumber)
    postData = '{"pageguid":"cfbb3a9d-c450-4ad5-b539-f44091747172","criteria":{"LNPropertyTypes":0,"LNIndustrialSubtypes":0,"LNRetailSubtypes":0,"LNShoppingCenterSubtypes":0,"LNMultiFamilySubtypes":0,"LNSpecialtySubtypes":0,"LNOfficeSubtypes":0,"LNHealthCareSubtypes":0,"LNHospitalitySubtypes":0,"LNSportsAndEntertainmentSubtypes":0,"LNLandSubtypes":0,"PropertyTypes":0,"HospitalitySubtypes":0,"IndustrialSubtypes":0,"LandTypes":0,"OfficeSubtypes":0,"GeneralRetailSubtypes":0,"FlexSubtypes":0,"SportsAndEntertainmentSubtypes":0,"SpecialtySubtypes":0,"MultifamilySubtypes":0,"HealthcareSubtypes":0,"ShoppingCenterTypes":0,"ApartmentStyleTypes":0,"Country":"US","Region":"","State":"PA","Market":null,"MSA":null,"County":"Allegheny","City":"","GeographyFilters":[{"BoundingBox":[' + minLongitude + ',' + minLatitude + ',' + maxLongitude + ',' + maxLatitude + '],"Centroid":[' + centerLongitude + ',' + centerLatitude + '],"Display":"Allegheny County","TypeaheadDisplay":"Allegheny County, PA, USA","GeographyId":2251,"Code":"PA","GeographyType":9,"Radius":0,"RadiusLengthMeasure":0,"SubmarketPropertyType":0,"MatchType":10,"Slug":{"ss":"allegheny-county-pa","ps":"allegheny-county-pa","ut":0,"it":1,"bc":[{"ss":"usa","ps":"usa","so":1,"mt":15,"dn":"United States","ni":false},{"ss":"allegheny-county-pa","ps":"allegheny-county-pa","so":2,"mt":10,"dn":"Allegheny County","ni":false}],"lang":"en-US","dn":"Allegheny County","altSlugs":[{"ps":"allegheny-county-pa--usa","lang":"en-CA"},{"ps":"allegheny-county-pa--usa","lang":"fr-CA"}]}}],"PageLocationLabel":"Pittsburgh, PA","TypeaheadLocationLabel":"Pittsburgh, PA - USA","IncludeProximityCities":false,"Distance":0,"CoordinateBounds":{"LatitudeRange":{"Lower":' + minLatitude + ',"Upper":' + maxLatitude + '},"LongitudeRange":{"Lower":' + minLongitude + ',"Upper":' + maxLongitude + '}},"Polygon":null,"HasValidCoordinates":null,"BuildingClass":0,"BuildingSizeUom":"SquareFeet","LotSizeUom":"Acres","SubCategoryList":[],"Editor":"Default","PreserveAddressForRadiusSavedSearch":false,"ListingSearchType":1,"OnMarketDateRange":null,"Keywords":null,"LoopLinkForLeaseDefaultSorting":[],"LoopLinkForSaleDefaultSorting":[],"LoopLinkForSaleAndLeaseDefaultSorting":[],"CountryGeography":null,"PropertyGroupId":null,"HasMultipleLocations":false,"IsForSale":false,"PriceRangeMin":null,"PriceRangeMax":null,"StartingPriceRangeMin":null,"StartingPriceRangeMax":null,"BuildingSizeRangeMin":null,"BuildingSizeRangeMax":null,"PriceRangeCurrency":null,"PriceRangeRateType":null,"LotSizeRangeMin":null,"LotSizeRangeMax":null,"UnitCountRangeMin":null,"UnitCountRangeMax":null,"CapRateRangeMin":null,"CapRateRangeMax":null,"YearBuiltRangeMin":null,"YearBuiltRangeMax":null,"TermLengthRangeMin":null,"TermLengthRangeMax":null,"NetLeased":false,"InContract":false,"Distressed":false,"Auction":false,"IsTenXAuctions":false,"AuctionIds":null,"Single":false,"Multiple":false,"InvestmentTypeCore":null,"InvestmentTypeValueAdd":null,"InvestmentTypeOpportunistic":null,"InvestmentTypeTripleNet":null,"InvestmentTypeOpportunityZone":null,"AuctionAssetTypeProperties":null,"AuctionAssetTypeNotes":null,"AuctionFinanceTypeFinancing":null,"AuctionFinanceTypeBrokerCoOp":null,"BusinessForSale":true,"VacantOwner":true,"Investment":true,"InOpportunityZone":null,"CondosFilter":0,"PortfoliosFilter":0,"BusinessForSaleFilter":0,"ShoppingCenterFilter":0,"BuildingParkFilter":0,"IsForLease":true,"AvailableForLease":true,"AdditionalFeesMin":null,"AdditionalFeesMax":null,"ExcludeLeaseHold":false,"PendingForLease":false,"IsDefaultLeaseRate":true,"LeaseRateRangeMin":null,"LeaseRateRangeMax":null,"SpaceAvailableRangeMin":null,"SpaceAvailableRangeMax":null,"SpaceAvailableOccupancy":null,"LeaseRateTerm":"y","SpaceAvailableUom":"SquareFeet","LeaseRateCurrency":null,"LeaseRatePerSizeUom":"SquareFeet","SubLease":false,"RegionalMarket":null,"SubMarket":null,"MoveInDateIndicator":0,"MoveInDateEnteredType":null,"MoveInDateEnteredRangeMin":null,"MoveInDateEnteredRangeMax":null,"UseClassTypes":0,"SpaceLeaseTypes":0,"LeaseTermCommercial369":null,"LeaseTermShortTermLease":null,"ListingId":null,"DateIndicator":0,"DateEnteredRangeMin":"","DateEnteredRangeMax":"","MinimumDate":"01/01/0001","DateEnteredType":"RT","DateFormat":"MM/dd/yyyy","ViewMode":"None","ListingIdPinClick":null,"IsUserFromUS":true,"ForceRemoveBoundary":false,"BoundsChangedViaMapInteraction":true,"AgentFirstName":null,"AgentLastName":null,"Currency":null,"ListingType":2,"IsAuctionsOnly":false,"ListingCountryCode":"US","ExpandSearch":false,"ShowFavoritesOnly":false,"BuildingListingAmenities":"0","SpaceListingAmenities":"0","ResultLimit":500,"PageNumber":' + pageNumber + ',"PageSize":25,"Timeout":0,"Origin":1,"LeaseRateUomTerm":"SquareFeetYearForUI","Auctions":false}}'
    response = requests.post(url, headers=headers, data=postData)
    return response.text

def callApiRecursive(minLatitude, maxLatitude, minLongitude, maxLongitude, parcel_map, rents_df):
    data = json.loads(callApi(minLatitude, maxLatitude, minLongitude, maxLongitude, 1))
    count = data['MetaState']['TotalResultCount']
    if count < 500:
        print('Processing ' + str(count) + ' entries')
        for i in range(1, math.floor((count - 1) / 25) + 2):
            data = json.loads(callApi(minLatitude, maxLatitude, minLongitude, maxLongitude, i))
            parsed_html = BeautifulSoup(data['SearchPlacards']['Html'], features="html.parser")
            parsed_json = json.loads(data['SearchPlacards']['PlacardsEventModel'])
            locations = {}
            for entry in parsed_json['ListingSearchResultItems']:
                locations[str(entry['ListingID'])] = [entry['Latitude'], entry['Longitude']]
            elements = parsed_html.find_all('article')
            for element in elements:
                listing_id = element['data-id']
                latitude = locations[listing_id][0]
                longitude = locations[listing_id][1]
                list_fields = element.find_all('li')
                is_vacant = False
                for field in list_fields:
                    if field.text.strip() in ['Commercial Land', 'Industrial Land']:
                        is_vacant = True
                        break
                price = element.find("li", {"name": "Price"})
                address = element.find("a", {"class": "left-h4"})
                if address is None:
                    address = element.find("div", {"class": "header-col"})
                    address = address.find("a")
                city_zip = element.find("a", {"class": "right-h6"})
                if city_zip is None:
                    city_zip = element.find("a", {"class": "subtitle-beta"})
                zip_code = city_zip.text.strip().split(' ')[-1]
                address = address.text.strip()
                if price is not None:
                    try:
                        price = price.text.strip()
                        price = price.replace("$", "")
                        price = price.replace(" SF/YR", "")
                        if ' - ' in price:
                            price = price.split(' - ')
                            price = (float(price[0]) + float(price[1])) / 2
                        else:
                            price = float(price)
                    except:
                        print('Error parsing price ' + str(price) + ' for address ' + str(address))
                        price = None
                key_address = address.upper()
                key_address = (key_address.replace('FIRST', '1ST').replace('SECOND', '2ND').replace('THIRD','3RD')
                               .replace('FOURTH', '4TH').replace('FIFTH', '5TH').replace('SIXTH', '6TH').replace('SEVENTH', '7TH')
                               .replace('EIGHTH', '8TH').replace('NINTH', '9TH'))
                key_address = key_address.replace(' MT ', ' MOUNT ')
                key_address = key_address.replace(' ', '')
                key = '{0}{1}'.format(key_address, zip_code)
                parcel_id = ''
                if key in parcel_map:
                    parcel_id = parcel_map[key]
                rents_df.loc[len(rents_df)] = [parcel_id, listing_id, latitude, longitude, address, zip_code, price, is_vacant]
    else:
        print('Found ' + str(count) + ' entries with ' + str(minLatitude) + ' and ' + str(maxLatitude) + ', need to split it to get remaining entries')
        callApiRecursive(minLatitude, (minLatitude + maxLatitude) / 2, minLongitude, maxLongitude, parcel_map, rents_df)
        callApiRecursive((minLatitude + maxLatitude) / 2, maxLatitude, minLongitude, maxLongitude, parcel_map, rents_df)

parcel_data = pd.read_csv(sys.argv[1], dtype={'PARID': str, 'PROPERTYHOUSENUM': str, 'PROPERTYFRACTION': str, 'PROPERTYADDRESS': str, 'PROPERTYZIP': str, 'CLASSDESC': str})
parcel_data = parcel_data[parcel_data['CLASSDESC'] != 'RESIDENTIAL']
parcel_geometry = gpd.read_file(sys.argv[2])
parcel_geometry = parcel_geometry[parcel_geometry['PIN'].isin(parcel_data['PARID'])]
parcel_map = {}
rents_df = pd.DataFrame(columns=['PARCEL_ID_FROM_ADDRESS', 'LISTING_ID', 'LATITUDE', 'LONGITUDE', 'ADDRESS', 'ZIP_CODE', 'PRICE', 'IS_VACANT'])
for i, row in parcel_data.iterrows():
    fraction = str(row['PROPERTYFRACTION']).strip()
    street_name = str(row['PROPERTYADDRESS']).strip().replace(' ', '').upper()
    if fraction.startswith('-'):
        try:
            start = int(row['PROPERTYHOUSENUM'])
            end = int(fraction.replace('-', ''))
            for i in range(start, end + 2, 2):
                key = '{0}{1}{2}'.format(i,
                                            street_name,
                                            str(row['PROPERTYZIP']).replace(' ', '').upper())
                parcel_map[key] = row['PARID']
        except:
            pass
    key = '{0}{1}{2}{3}'.format(str(row['PROPERTYHOUSENUM']).replace(' ', '').upper(),
                                str(fraction).replace(' ', '').upper(),
                                street_name,
                                str(row['PROPERTYZIP']).replace(' ', '').upper())
    parcel_map[key] = row['PARID']

callApiRecursive(40.1, 40.8, -80.4, -79.6, parcel_map, rents_df)

rents_gdf = gpd.GeoDataFrame(
    rents_df, geometry=gpd.points_from_xy(rents_df['LONGITUDE'], rents_df['LATITUDE']), crs="EPSG:4326"
)
rents_with_parcel = gpd.sjoin(rents_gdf, parcel_geometry, how='left', predicate='intersects', lsuffix='parcel', rsuffix='tract')
rents_with_parcel.rename(columns={'PIN': 'PARCEL_ID_FROM_GEOMETRY'}, inplace=True)
output_df = pd.DataFrame(columns=['PARCEL_ID', 'PARCEL_ID_FROM_ADDRESS', 'PARCEL_ID_FROM_GEOMETRY', 'LISTING_ID', 'LATITUDE', 'LONGITUDE', 'ADDRESS', 'ZIP_CODE', 'PRICE', 'IS_VACANT'])
listing_ids = []
for i, row in rents_with_parcel.iterrows():
    if row['LISTING_ID'] in listing_ids:
        continue
    parcel_id = row['PARCEL_ID_FROM_ADDRESS']
    if not parcel_id:
        parcel_id = row['PARCEL_ID_FROM_GEOMETRY']
    output_df.loc[len(output_df)] = [parcel_id, row['PARCEL_ID_FROM_ADDRESS'], row['PARCEL_ID_FROM_GEOMETRY'], row['LISTING_ID'], row['LATITUDE'], row['LONGITUDE'], row['ADDRESS'], row['ZIP_CODE'], row['PRICE'], row['IS_VACANT']]
    listing_ids.append(row['LISTING_ID'])

output_df.to_csv("commercial_rents.csv", index=False, )
