"""
Stage 1: Load and assemble data, enrich with census/OSM/spatial data, tag model groups.
Run from any directory. Output written to openavmkit/notebooks/pipeline/data/us-pa-allegheny/out/
"""
import os, sys
import pandas as pd
pd.options.future.infer_string = False
os.environ["PYTHONIOENCODING"] = "utf-8"

# Load .env from repo root so CENSUS_API_KEY is available to OpenAvmKit
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# Ensure the local openavmkit patch branch is used
openavmkit_repo = os.path.abspath("C:/projects/openavmkit")
if openavmkit_repo not in sys.path:
    sys.path.insert(0, openavmkit_repo)

locality = "us-pa-allegheny"
verbose = True

from openavmkit.pipeline import (
    init_notebook,
    load_settings,
    load_dataframes,
    process_dataframes,
    tag_model_groups_sup,
    write_notebook_output_sup,
)

# init_notebook changes cwd to openavmkit/notebooks/pipeline/data/us-pa-allegheny/
# so all subsequent relative paths are rooted there.
print(f"\n{'='*60}")
print(f"Step 1: init_notebook")
print(f"{'='*60}")
init_notebook(locality)

print(f"\n{'='*60}")
print(f"Step 2: load_settings")
print(f"{'='*60}")
settings = load_settings()
print(f"  locality: {settings.get('locality', {}).get('name')}")
print(f"  valuation_date: {settings.get('modeling', {}).get('metadata', {}).get('valuation_date')}")

print(f"\n{'='*60}")
print(f"Step 3: load_dataframes")
print(f"{'='*60}")
dataframes = load_dataframes(settings=settings, verbose=verbose)
for k, df in dataframes.items():
    print(f"  {k}: {len(df):,} rows, {len(df.columns)} cols")

print(f"\n{'='*60}")
print(f"Step 4: process_dataframes (merge + enrich)")
print(f"{'='*60}")
sup = process_dataframes(dataframes=dataframes, settings=settings, verbose=verbose)
print(f"\nSalesUniversePair created:")
print(f"  universe: {len(sup.universe):,} rows")
print(f"  sales:    {len(sup.sales):,} rows")

print(f"\n{'='*60}")
print(f"Step 5: tag_model_groups_sup")
print(f"{'='*60}")
sup = tag_model_groups_sup(sup=sup, settings=settings, verbose=verbose)
print("\nModel group distribution (universe):")
print(sup.universe["model_group"].value_counts(dropna=False).to_string())

print(f"\n{'='*60}")
print(f"Step 6: write output")
print(f"{'='*60}")
write_notebook_output_sup(sup, "1-assemble", parquet=True, gpkg=False, shp=False)
print("Done! Output written to out/")
