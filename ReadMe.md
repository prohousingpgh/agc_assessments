# Introduction

This ReadMe contains step-by-step instructions for replicating the assessments found in this repository and used in Pro-Housing Pittsburgh's report on Tax Assessments.
For any questions, please contact Connor Schwartz (Connor.Schwartz98@gmail.com).

Instructions for downloading and installing OpenAvmKit are available at https://www.OpenAvmKit.com/

# Download following files

The followed data input files are used with OpenAvmKit:<br>
Allgheny County property assessment csv: https://data.wprdc.org/dataset/property-assessments<br>
Allgheny County parcel GeoJSON: https://www.pasda.psu.edu/uci/DataSummary.aspx?dataset=1214<br>
Allgheny County census tract GeoJSON: https://openac-alcogis.opendata.arcgis.com/datasets/AlCoGIS::allegheny-county-census-tracts-2020<br>
Allegheny County census block boundaries: https://data.wprdc.org/dataset/allegheny-county-census-blocks-2021<br>
Allegheny County jobs by census block: https://lehd.ces.census.gov/data/#lodes<br>
Building heights and footprints: https://public.tableau.com/views/GlobalMLBuildingFootprintsDataWithEstimatedHeight/GlobalMLBuildingFootprints.<br>
For heights and footprints, users may need to download a few files to get all of Allegheny County. Unzip these files and put the raw csvs under agc_assessments/building_footprints. <br>
Run this script, which uses commercial rents scraped from loopnet.com to create a commercial_rents.csv file:<br>
python getCommercialRents.py allegheny_county_master_file.csv AlleghenyCounty_Parcels202511.geojson

The following data input files are used for the graphs in the report, but are not currently used in the actual modeling: <br>
City council districts: https://data.wprdc.org/dataset/city-council-districts-2012<br>
County council districts: https://openac-alcogis.opendata.arcgis.com/datasets/AlCoGIS::allegheny-county-council-districts<br>

The following data input files are not currently used in our assessment analysis. However, they are converted into OpenAVMKit-compatible files by our pre-processing script, and could easily be added to our models in the future:<br>
Allgheny County market value categories: https://data.wprdc.org/dataset/market-value-analysis-2021<br>
Pittsburgh Steep slopes overlay: https://data.wprdc.org/dataset/25-or-greater-slope<br>
Pittsburgh Flood zones: https://data.wprdc.org/dataset/2014-fema-flood-zones<br>
Pittsburgh Undermined overlay: https://data.wprdc.org/dataset/undermined-areas<br>
Pittsburgh city limits: https://data.wprdc.org/dataset/pittsburgh-city-boundary<br>
Note that the steep slopes, flood zone, and undermined overlays are for Pittsburgh, not all of Allegheny County. The values outside Pittsburgh will be marked Unknown during analysis. <br>
Commercial parcel data can be obtained by extracting json responses from the search page of Crexi (https://www.crexi.com/search). These responses can be combined into a csv using this script: <br>
python processCrexiData.py

# Convert Data into Usuable Format
Run this script to convert these files into the format which OpenAvmKit uses:<br>
python OpenAvmKitInputFiles.py allegheny_county_master_file.csv AlleghenyCounty_Parcels202511.geojson Allegheny_County_Census_Tracts_2020_2192142189737482778.geojson commercial_rents.csv mva.geojson slopes.geojson flood_zones.geojson undermined.geojson CityBoundary.geojson crexi_data.csv city_council_districts_2022.geojson County_Council_Districts_-7561056125954294637.geojson census_blocks_2020.geojson pa_wac_S000_JT00_2023.csv

This should generate 9 files:<br>
parcels.csv<br>
sales.csv<br>
parcels.parquet<br>
city_council_districts.parquet (currently only used for reports/results analysis)<br>
county_council_districts.parquet (currently only used for reports/results analysis)<br>
market_value.parquet (currently not used for modeling)<br>
steep_slopes.parquet (currently not used for modeling)<br>
flood_zones.parquet (currently not used for modeling)<br>
undermined.parquet (currently not used for modeling)

# OpenAvmKit settings

The settings.json file controls how data is read and used by OpenAvmKit. Here are some details on the sections of this file and how I filled them out:

### "locality"

Locality metadata (state, county name, imperial or metric, geographic coordinates of county center).

### "data"

This is where the input files get loaded.
- There are 3 datasets here - "parcels"[parcels.csv] which is a CSV with data on every parcel (commercial rent data is included in "parcels"), "sales"[sales.csv] which is a CSV with records for all of our sales, and "geo_parcels"[parcels.parquet] which contains geometric data for each parcel id. We can load in as many additional datasets as we want.
- The "key" attribute in all 3 datasets is used to join the datasets. We need to include the parcel id as the key for any file we load in (except for additional geometric files, which are matched using geometric joins instead)
- Some basic calculations can be performed in the "calcs" section of settings.json to form new fields from existing ones.
- The following fields are mandatory - "land_area_sqft", "bldg_area_finished_sqft", "valid_sale", "vacant_sale", "sale_price", and "sale_date". Additonal variables besides these may be used for modeling.

### "process"

This is where the data gets processed, joined together, and loaded into dataframes.
- The "merge" section creates 2 dataframes - "universe" and "sales". "universe" contains parcel data (including commercial rents) and "sales" contains sales data - any additional datasets should be added to these lists, and would be joined using the aforementioned "key" attribute.
- "enrich" allows you to perform additional calculations and merge additional geometric data onto your dataframes. We are attaching all of the data from our parquet files here with a geometric join. This section also supports OpenStreetMap integration - you can configure it to use OpenStreetMap to compute distances from amenities like parks, schools, bodies of water, etc. and add that to the dataframe. We do not currently do that.
- "fill" allows you to control null handling - you can choose to fill in with zeros, "None", the median or mode value for that field, etc. You can also split the handling for vacant vs improved parcels.

### "modeling"

This controls how the assessment is actually performed.
- "try_variables" is for testing the significance of different possible variables. It does not impact the final models/results and is just a tool for determining the best variables for the model.
- "model_groups" defines the actual model groups. Parcels will be split into groups (i.e. commercial, single-family, multi-family) for both modeling and result analysis. 
- "instructions" defines the algorithms (regression, decsision tree, etc) to use for each model group. Currently, we are using linear regression ("mra"), spatial models ("local_area", "spatial_lag_area"), and decision tree models ("lightgbm","xgboost") across all model groups.
- "models" specifies which variables to use in the models. We use "land_area_sqft", "bldg_year_built", "finished_living_area_sqft", "bldg_quality_num", "building_condition_num", and "spatial_lag_sale_price_time_adj" for residential parcels. We use "land_area_sqft", "commercial_rent", "building_footprint", "building_height", "jobs_per_sqft", and "spatial_lag_sale_price_time_adj" for commercial parcels. These variables are in the "universe" dataframe.
- "analysis" and "field_classification" are used for ratio studies/results analysis.

### "ref"

This section creates calculations and filters that are used elsewhere in the file. The model groups for ratio studies are defined here.

# Using OpenAvmKit
Once the input files are generated and OpenAvmKit installed, the user places them in the OpenAvmKit repository as follows:

notebooks/<br>
├──pipeline/<br>
&emsp;├──data/<br>
&emsp;&emsp;├──us-pa-allegheny/<br>
&emsp;&emsp;&emsp;├── in/<br>
&emsp;&emsp;&emsp;&emsp; ├── geo/<br>
&emsp;&emsp;&emsp;&emsp;&emsp;  ├── city_council_districts.parquet<br>
&emsp;&emsp;&emsp;&emsp;&emsp;  ├── county_council_districts.parquet<br>
&emsp;&emsp;&emsp;&emsp;&emsp;  ├── flood_zones.parquet<br>
&emsp;&emsp;&emsp;&emsp;&emsp;  ├── market_value.parquet<br>
&emsp;&emsp;&emsp;&emsp;&emsp;  ├── parcels.parquet<br>
&emsp;&emsp;&emsp;&emsp;&emsp;  ├── steep_slopes.parquet<br>
&emsp;&emsp;&emsp;&emsp;&emsp;  ├── undermined.parquet<br>
&emsp;&emsp;&emsp;&emsp; ├── parcels.csv<br>
&emsp;&emsp;&emsp;&emsp; ├── sales.csv<br>
&emsp;&emsp;&emsp;&emsp; ├── settings.json<br>
&emsp;&emsp;&emsp;├── out/

This allows users to perform all of the OpenAvmKit operations on the data.

There is a set of Jupyter notebooks in OpenAvmKit that walk users through the process of generating assessments. Book 03-model.ipynb allows users to generate valuations.

# Results
A sample final results file, residential_predictions_20260503.csv, is available in this repository.
