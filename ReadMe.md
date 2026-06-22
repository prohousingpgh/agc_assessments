# Allegheny County Open AVMKit

Allegheny County, PA (FIPS 42003) property valuation models using [OpenAVMKit](https://github.com/larsiusprime/openavmkit), supporting Pro-Housing Pittsburgh's report on tax-assessment fairness. For questions, contact Connor Schwartz (Connor.Schwartz98@gmail.com).

> **Disclaimer:** This is independent research in progress. All models, findings, and estimates are provided for research and educational purposes only. No warranty is made regarding accuracy, completeness, or fitness for any particular purpose. This work does not constitute professional appraisal, legal, tax, or financial advice. Results should not be relied upon for any official, legal, or financial decision, including property tax appeals. Use at your own risk.

> **⚠️ Equity Testing Required — Census Variables in Model**
>
> The residential models use Census tract-level variables as predictors — `median_income` and `median_g_rent` (ACS) — plus the PCRG Market Value Analysis tier `market_value_category`. These capture neighborhood market conditions but also correlate with the racial and socioeconomic composition of residents.
>
> IAAO Standard on Mass Appraisal of Real Property (2017) §7.3 prohibits variables that produce racially discriminatory *outcomes* — the concern is not the input itself but the effect. Census variables can be appropriate if the resulting assessment ratios are equitable across protected groups. The key test is a ratio study stratified by income and, where data permits, by neighborhood racial composition.
>
> **Status:** the ratio study is stratified by income quintile (`ratio_study.breakdowns`). At the current iteration, **level equity by income passes** — the median ratio is flat (~1.0) across all income quintiles in every group. A horizontal-equity concern remains: COD (assessment *uniformity*) is ~1.4–1.7× worse in the lowest-income quintile than the highest, systematically across groups. A `pct_minority` (ACS B03002) racial-composition breakdown is wired into the settings but **pending a Stage-1 rebuild** to enrich the column. **Before any official use,** run the full stratified equity analysis and confirm ratios are within IAAO tolerances across all income and racial-composition strata. See `CLAUDE.md` for the detailed equity findings.

## Overview

This project builds automated valuation models (AVMs) for ~584,000 Allegheny County parcels from publicly available assessment, parcel, and sales data, enriched with Census, OpenStreetMap, and DEM (elevation) features. Models are trained with [OpenAVMKit](https://github.com/larsiusprime/openavmkit) (LightGBM, linear regression, and spatial/comparable-sales engines), and assessment quality is measured with [IAAO-standard ratio studies](https://www.iaao.org/wp-content/uploads/Standard_on_Ratio_Studies.pdf) compared against the county's published assessments. The goal is to support distributional analysis of property-tax fairness and a potential land-value-tax shift.

- **Locality:** Allegheny County, PA · **FIPS:** 42003 · **County seat:** Pittsburgh
- **Valuation date:** 2026-01-01 · **Study period:** 2025-01-01 – 2026-01-01
- **Model groups (5):** `commercial`, `residential_multi_family`, and three residential single-family groups — `urban`, `suburban_prewar`, and `suburban`

## Current Results

> **⚠️ Provisional — iteration in progress (2026-06-21).** These numbers are from the latest in-development run and are **not** final. Caveats: the residential ensembles were just re-blended to fix vertical equity (see below); the suburban group's numbers were salvaged from a stale (pre-rivers) checkpoint and want a clean re-run; `pct_minority` is not yet enriched; commercial is data-starved (~43 study-period sales); and the published `output/` CSVs have not been regenerated against this run.

Per-group ratio study over the 2025–2026 study period. Ratios are `prediction / sale_price` (raw, unadjusted); because the model targets time-adjusted 2026-01-01 values and prices shifted over 2025, a well-calibrated model sits slightly below 1.0. COD = Coefficient of Dispersion (lower = more uniform assessments; IAAO residential standard ≤ 15, acceptable ≤ 20).

| Model group | Study-period sales | This model — Median ratio | This model — COD (trimmed) | County — Median ratio | County — COD |
|---|---|---|---|---|---|
| Residential SF — Suburban | 5,751 | 0.96 | **10.4** | 0.50 | 13.6 |
| Residential SF — Urban | 1,459 | 0.97 | **14.4** | 0.42 | 24.0 |
| Residential SF — Suburban Pre-War | 1,077 | 1.00 | **18.3** | 0.49 | 17.8 |
| Residential Multi-Family | 1,059 | 0.91 | **9.5** | 0.52 | 15.7 |
| Commercial | 43 | 1.82 | 35.9 | 0.54 | 24.3 |

The residential groups meet or approach IAAO COD standards (≤ 15, acceptable ≤ 20). Commercial is data-starved (~43 study-period sales) and should be used with caution.

**Current county assessments run at roughly half of market value.** The county's median assessment ratio is ~0.42–0.54 across groups — properties are assessed at ~42–54% of modeled market value — a key input to the fairness analysis.

**Vertical equity (VEI).** OpenAVMKit's default ensemble optimizes accuracy (MAPE) with no equity term, and is regressive (cheap properties over-assessed relative to expensive). The pipeline re-blends the residential ensembles to the median of `[mra, multi_mra, lightgbm]` (`scripts/run_reensemble.py`), which substantially improves VEI at no COD cost: prewar −32 → −12, urban −12 → +8, suburban −14 → −7, multi-family −11 → −6. Commercial keeps its own ensemble (the trio blend does not suit its thin data).

## Features

Residential models use building, land/geometry, location, and neighborhood-context features:

**Building physical** — finished living area, building area, year built / age, quality grade (`bldg_quality_num`), condition (`bldg_condition_num`), CDU grade, stories, bedrooms, baths.

**Land & geometry** — land area (and `land_area_sqft_log`), parcel polar coordinates (radius/angle from county center), rectangularity, aspect ratio.

**Spatial / location** — latitude/longitude; neighborhood, census tract, school district, municipality; spatial lag of time-adjusted sale price; proximity to OSM **rivers** (Pittsburgh's three rivers, captured as `waterway` linestrings), other water bodies, and parks; DEM-derived slope (`slope_mean_deg`).

**Neighborhood context (Census / market)** ⚠️ *requires equity testing — see notice above* — median household income, median gross rent (ACS), and the PCRG Market Value Analysis tier (`market_value_category`).

The **commercial** model additionally uses commercial rent, jobs-per-sqft (Census LODES), and building footprint.

Linear (`mra`/`multi_mra`) residential models train on `log` sale price to avoid negative/compressed predictions at the tails; tree models (`lightgbm`, `xgboost`, `lcomp`) use a wider "kitchen-sink" variable set in price space.

## Data Sources

Input data lives under `data/us-pa-allegheny/in/` and is **not tracked in git** due to size; download instructions are below. Sources:

- **Allegheny County property assessments** (parcel attributes, assessment values, sale history) — [WPRDC](https://data.wprdc.org/dataset/property-assessments)
- **Parcel geometry** (GeoJSON) — [PASDA](https://www.pasda.psu.edu/uci/DataSummary.aspx?dataset=1214)
- **Census tract / block-group geography** — [Allegheny County GIS open data](https://openac-alcogis.opendata.arcgis.com/datasets/AlCoGIS::allegheny-county-census-tracts-2020) + [WPRDC blocks](https://data.wprdc.org/dataset/allegheny-county-census-blocks-2021)
- **US Census ACS** (FIPS 42003) — tract-level `median_income` (B19013), `median_g_rent` (B25064); `pct_minority` (B03002) wired in, pending a Stage-1 rebuild
- **LODES jobs by block** (`jobs_per_sqft`) — [LEHD/Census](https://lehd.ces.census.gov/data/#lodes)
- **Building footprints & heights** — [Microsoft/Global ML Building Footprints](https://public.tableau.com/views/GlobalMLBuildingFootprintsDataWithEstimatedHeight/GlobalMLBuildingFootprints)
- **PCRG Market Value Analysis tier** (`market_value_category`) — [WPRDC MVA 2021](https://data.wprdc.org/dataset/market-value-analysis-2021)
- **OpenStreetMap** — proximity to rivers, water bodies, and parks (via Overpass)
- **DEM** — elevation/slope enrichment (`slope_mean_deg`)
- **Commercial rents** — scraped from loopnet.com via `scripts/getCommercialRents.py`

The following are converted by the pre-processing script but **not currently used in modeling**: city/county council districts, steep-slope / flood-zone / undermined overlays (Pittsburgh-only), city limits.

## Running the Pipeline

Always use the project Python (`C:/Users/druss/miniconda3/python.exe`) and launch from the repo root (`C:/projects/agc_assessments`). The `openavmkit` clone at `C:/projects/openavmkit` must be on the **`philly-patches-0.6.0`** branch (shared across the PA county projects). A `CENSUS_API_KEY` in `.env` (gitignored) is required for Stage 1 census enrichment. See `CLAUDE.md` for environment details, the enrichment-cache landmines, checkpoint management, and the full-rebuild sequence.

```bash
# Stage 0: acquire + convert raw data into OpenAvmKit format (see detail below)
python scripts/getCommercialRents.py allegheny_county_master_file.csv AlleghenyCounty_Parcels202511.geojson
python scripts/openAvmKitInputFiles.py <inputs...>

# Stages 1–3: assemble + enrich, clean + sales scrutiny, train + ratio studies
python scripts/run_01_assemble.py   # load, enrich (census/OSM/DEM/geometry), tag model groups
python scripts/run_02_clean.py      # sales scrutiny + cleaning
python scripts/run_03_model.py      # train models, ensemble, ratio studies

# Post-process (no retrain): re-blend residential ensembles to fix vertical equity (~1 min)
python scripts/run_reensemble.py --apply

# Optional: combine outputs into the published output/ CSVs
python scripts/combineOutputFiles.py
```

SHAP/contribution generation is **off by default** (`DO_SHAPS=False` in `run_03_model.py`) and should stay off for metric/equity iteration — it is only needed for a final publication run (explainability / IAAO narrative).

---

## Detailed Setup & Data Acquisition

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
python scripts/getCommercialRents.py allegheny_county_master_file.csv AlleghenyCounty_Parcels202511.geojson

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
python scripts/processCrexiData.py

# Convert Data into Usuable Format
Run this script to convert these files into the format which OpenAvmKit uses:<br>
python scripts/OpenAvmKitInputFiles.py allegheny_county_master_file.csv AlleghenyCounty_Parcels202511.geojson Allegheny_County_Census_Tracts_2020_2192142189737482778.geojson commercial_rents.csv mva.geojson slopes.geojson flood_zones.geojson undermined.geojson CityBoundary.geojson city_council_districts_2022.geojson County_Council_Districts_-7561056125954294637.geojson census_blocks_2020.geojson pa_wac_S000_JT00_2023.csv

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
- "enrich" allows you to perform additional calculations and merge additional geometric data onto your dataframes. We are attaching all of the data from our parquet files here with a geometric join. This section also supports OpenStreetMap integration - you can configure it to use OpenStreetMap to compute distances from amenities like parks, schools, bodies of water, etc. and add that to the dataframe. We currently use it to compute proximity to water bodies (rivers and streams), which feeds the models as `proximity_to_osm_water`. Elevation/slope is similarly enriched from a DEM as `slope_mean_deg`.
- "fill" allows you to control null handling - you can choose to fill in with zeros, "None", the median or mode value for that field, etc. You can also split the handling for vacant vs improved parcels.

### "modeling"

This controls how the assessment is actually performed.
- "try_variables" is for testing the significance of different possible variables. It does not impact the final models/results and is just a tool for determining the best variables for the model.
- "model_groups" defines the actual model groups. Parcels will be split into groups (i.e. commercial, single-family, multi-family) for both modeling and result analysis. 
- "instructions" defines the algorithms (regression, decsision tree, etc) to use for each model group. Currently, we are using linear regression ("mra"), spatial models ("local_area", "spatial_lag_area"), and decision tree models ("lightgbm","xgboost") across all model groups.
- "models" specifies which variables to use in the models. The linear residential models ("mra"/"multi_mra") use `land_area_sqft`, `finished_living_area_sqft`, `bldg_age_years`, `bldg_quality_num`, `bldg_condition_num`, `cdu_grade`, `slope_mean_deg` (DEM), `proximity_to_osm_water` (OSM), `polar_radius`/`polar_angle` (location geometry), `spatial_lag_sale_price_time_adj` (local market signal), and the neighborhood-context variables `median_income`, `median_g_rent` (Census ACS) and `market_value_category` (PCRG Market Value Analysis tier). The commercial linear model uses `land_area_sqft`, `commercial_rent`, `jobs_per_sqft`, `bldg_area_footprint_sqft`, `slope_mean_deg`, `proximity_to_osm_water`, `spatial_lag_sale_price_time_adj`, and `polar_radius`/`polar_angle`. The tree/ensemble models (`lightgbm`, `xgboost`, `lcomp`) use a wider "kitchen-sink" set on top of these. All variables live in the "universe" dataframe.
  - The Census neighborhood variables (`median_income`, `median_g_rent`) and the MVA tier are used as market signals, but are paired with equity testing: the ratio study (see "analysis") breaks results down by income quintile — and by Census-tract racial composition (`pct_minority`) once that enrichment is in place — to confirm assessment ratios do not vary systematically across protected groups (per IAAO §7.3).
- "analysis" and "field_classification" are used for ratio studies/results analysis.

### "ref"

This section creates calculations and filters that are used elsewhere in the file. The model groups for ratio studies are defined here.

# Using OpenAvmKit

The modern pipeline is driven by the staged scripts (`scripts/run_01_assemble.py` → `run_02_clean.py` → `run_03_model.py`), which call OpenAvmKit's API directly and write to `data/us-pa-allegheny/out/`. The input files are placed under `data/us-pa-allegheny/in/` as follows:

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

OpenAvmKit also ships a set of Jupyter notebooks that walk through the same process interactively; `03-model.ipynb` is the modeling step the `run_03_model.py` script automates.

## Results

A sample final results file, `residential_predictions.csv`, is available in this repository (and is regenerated by `scripts/combineOutputFiles.py`).

## Attribution

Built on [OpenAVMKit](https://github.com/larsiusprime/openavmkit) by Lars Doucet and contributors.
