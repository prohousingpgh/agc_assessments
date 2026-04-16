Instructions for downloading and installing OpenAvmKit are available at https://www.OpenAvmKit.com/

# Downloading input files

We need a few data input files to use OpenAvmKit:<br>
Get the property assessment csv from here: https://data.wprdc.org/dataset/property-assessments<br>
Get the parcel GeoJSON from here: https://www.pasda.psu.edu/uci/DataSummary.aspx?dataset=1214<br>
Get the census tract GeoJSON from here: https://openac-alcogis.opendata.arcgis.com/datasets/AlCoGIS::allegheny-county-census-tracts-2020<br>
Get market value categories from here: https://data.wprdc.org/dataset/market-value-analysis-2021<br>
Steep slopes overlay: https://data.wprdc.org/dataset/25-or-greater-slope<br>
Flood zones: https://data.wprdc.org/dataset/2014-fema-flood-zones<br>
Undermined overlay: https://data.wprdc.org/dataset/undermined-areas<br>
Pittsburgh city limits: https://data.wprdc.org/dataset/pittsburgh-city-boundary<br>
City council districts: https://data.wprdc.org/dataset/city-council-districts-2012<br>
County council districts: https://openac-alcogis.opendata.arcgis.com/datasets/AlCoGIS::allegheny-county-council-districts<br>
Note that the steep slopes, flood zone, and undermined overlays are for Pittsburgh, not all of Allegheny County. The values outside Pittsburgh will be marked Unknown during analysis.<br>

Run this script, which uses commercial rents scraped from loopnet.com to create a commercial_rents.csv file:<br>
python getCommercialRents.py allegheny_county_master_file.csv AlleghenyCounty_Parcels202511.geojson

Get commercial parcel data by extracting json responses from the search page of Crexi (https://www.crexi.com/search). These responses can be combined into a csv using this script:
python processCrexiData.py

Run this script to convert these files into the format which OpenAvmKit uses:<br>
python OpenAvmKitInputFiles.py allegheny_county_master_file.csv AlleghenyCounty_Parcels202511.geojson Allegheny_County_Census_Tracts_2020_2192142189737482778.geojson commercial_rents.csv mva.geojson slopes.geojson flood_zones.geojson undermined.geojson CityBoundary.geojson crexi_data.csv city_council_districts_2022.geojson County_Council_Districts_-7561056125954294637.geojson

This should generate 10 files:<br>
parcels.csv<br>
sales.csv<br>
parcels.parquet<br>
census_tracts.parquet<br>
market_value.parquet<br>
steep_slopes.parquet<br>
flood_zones.parquet<br>
undermined.parquet<br>
city_council_districts.parquet<br>
county_council_districts.parquet

Additionally, I've provided the settings.json file which OpenAvmKit uses to read and analyze the data.

# OpenAvmKit settings

The settings.json file controls how data is read and used by OpenAvmKit. Here are some details on the sections of this file and how I filled them out:

### "locality"

Just some basic metadata.

### "data"

This is where our input files actually get loaded. Some notes about this:
- There are 3 essential datasets here - "parcels" which is a CSV with data on every parcel, "sales" which is a CSV with records for all of our sales, and "geo_parcels" which contains geometric data for each parcel id. We can load in as many additional datasets as we want.
- The "key" attribute is essential, as it's used to join the datasets. We need to include the parcel id as the key for any file we load in (except for additional geometric files, which are matched using geometric joins instead)
- Some basic calculations can be performed in the "calcs" section to form new fields from existing ones.
- A few fields are mandatory - "land_area_sqft", "bldg_area_finished_sqft", "valid_sale", "vacant_sale", "sale_price", and "sale_date". Aside from that, we can load in whatever variables we want to use for modeling.

### "process"

This is where the data gets processed, joined together, and loaded into dataframes. Some notes:
- The "merge" section creates 2 dataframes - "universe" and "sales". "universe" contains parcel data and "sales" contains sales data - any additional datasets should be added to these lists, and would be joined using the aforementioned "key" attribute.
- "enrich" allows you to perform additional calculations and merge additional geometric data onto your dataframes. Right now, all we're doing here is attaching the census tract with a geometric join. This section also supports OpenStreetMap integration - you can configure it to use OpenStreetMap to compute distances from parks, schools, bodies of water, etc. and add that to the dataframe.
- "fill" allows you to control null handling - you can choose to fill in with zeros, "None", the median or mode value for that field, etc. You can also split the handling for vacant vs improved parcels.

### "modeling"

This controls how the assessment is actually performed. Some notes:
- "try_variables", "instructions", and "models" control which algorithms are used for modeling, and which variables they use. I have not investigated this much - I mostly just used the configuration from Lars' sample dataset.
- "model_groups" creates different buckets for analysis - this is used for ratio studies/determining whether the model works well for different types of parcel. I just split it into a few broad categories of land uses.
- "analysis" and "field_classification" are also used for ratio studies/results analysis.

### "ref"

This section allows you to create calculations and filters that are used elsewhere in the file. The model groups for ratio studies are defined here.

# Using OpenAvmKit
Once you've generated the input files and installed OpenAvmKit, place them in the OpenAvmKit repository as follows:

notebooks/<br>
├──pipeline/<br>
&emsp;├──data/<br>
&emsp;&emsp;├──us-pa-allegheny/<br>
&emsp;&emsp;&emsp;├── in/<br>
&emsp;&emsp;&emsp;&emsp; ├── geo/<br>
&emsp;&emsp;&emsp;&emsp;&emsp;  ├── census_tracts.parquet<br>
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

This will allow you to perform all of the OpenAvmKit operations on our data.

There is a set of Jupyter notebooks in OpenAvmKit that walk you through the process of generating assessments. Book 03-model.ipynb allows you to actually generate some valuations.

If you want to try running through it with our data, I would recommend trimming the csv input files to 1000 rows or so - some of the steps are slow so it's best to use smaller files if you just want to play around with it.