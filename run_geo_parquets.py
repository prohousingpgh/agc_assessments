import os, geopandas as gpd, pandas as pd

out = r"C:/projects/openavmkit/notebooks/pipeline/data/us-pa-allegheny/in"
data = r"C:/projects/agc_assessments/data"
os.chdir(out)

print("Loading files...")
city_boundary = gpd.read_file(f"{data}/CityBoundary.geojson")
steep_slopes   = gpd.read_file(f"{data}/slopes.geojson")
flood_zones    = gpd.read_file(f"{data}/flood_zones.geojson")
undermined     = gpd.read_file(f"{data}/undermined.geojson")
city_council_districts   = gpd.read_file(f"{data}/city_council_districts_2022.geojson")
county_council_districts = gpd.read_file(f"{data}/county_council_districts.geojson")

steep_slopes.rename(columns={'slope25': 'STEEP_SLOPE'}, inplace=True)
flood_zones.rename(columns={'fld_zone': 'FLOOD_ZONE'}, inplace=True)
undermined.rename(columns={'undermined': 'UNDERMINED'}, inplace=True)
city_council_districts.rename(columns={'DIST_NAME': 'CITY_COUNCIL_DISTRICT'}, inplace=True)
county_council_districts.rename(columns={'LABEL': 'COUNTY_COUNCIL_DISTRICT'}, inplace=True)

print("CRS city_boundary:", city_boundary.crs)
print("CRS steep_slopes:", steep_slopes.crs)
print("CRS flood_zones:", flood_zones.crs)
print("CRS undermined:", undermined.crs)

city_boundary = city_boundary.to_crs(epsg=4326)
print("Reprojected city_boundary to EPSG:4326")

print("Computing steep slopes difference...")
diff = city_boundary.union_all().difference(steep_slopes.union_all())
rest = gpd.GeoDataFrame(data={"STEEP_SLOPE": "No", "geometry": diff}, index=[0], crs="EPSG:4326")
steep_slopes = pd.concat([steep_slopes, rest])
steep_slopes.to_parquet("steep_slopes.parquet")
print("Saved steep_slopes.parquet")

print("Computing flood zones difference...")
diff = city_boundary.union_all().difference(flood_zones.union_all())
rest = gpd.GeoDataFrame(data={"FLOOD_ZONE": "No", "geometry": diff}, index=[0], crs="EPSG:4326")
flood_zones = pd.concat([flood_zones, rest])
flood_zones.to_parquet("flood_zones.parquet")
print("Saved flood_zones.parquet")

print("Computing undermined difference...")
diff = city_boundary.union_all().difference(undermined.union_all())
rest = gpd.GeoDataFrame(data={"UNDERMINED": "No", "geometry": diff}, index=[0], crs="EPSG:4326")
undermined = pd.concat([undermined, rest])
undermined.to_parquet("undermined.parquet")
print("Saved undermined.parquet")

city_council_districts.to_parquet("city_council_districts.parquet")
print("Saved city_council_districts.parquet")

county_council_districts.to_parquet("county_council_districts.parquet")
print("Saved county_council_districts.parquet")

print("All done.")
