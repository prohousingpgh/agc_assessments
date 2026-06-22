"""
Stage 2: Fill nulls, compute horizontal equity clusters, run sales scrutiny.
Requires Stage 1 output (out/1-assemble-sup.pickle).
Run from any directory.
"""
import os, sys
import pandas as pd
pd.options.future.infer_string = False
os.environ["PYTHONIOENCODING"] = "utf-8"

openavmkit_repo = os.path.abspath("C:/projects/openavmkit")
if openavmkit_repo not in sys.path:
    sys.path.insert(0, openavmkit_repo)

locality = "us-pa-allegheny"
verbose = True

from openavmkit.pipeline import (
    init_notebook,
    from_checkpoint,
    delete_checkpoints,
    load_settings,
    examine_sup,
    fill_unknown_values_sup,
    process_sales,
    mark_horizontal_equity_clusters_per_model_group_sup,
    run_sales_scrutiny,
    write_notebook_output_sup,
    read_pickle,
)

print(f"\n{'='*60}")
print(f"Step 1: init_notebook + clear checkpoints")
print(f"{'='*60}")
init_notebook(locality)
delete_checkpoints("2-clean")

print(f"\n{'='*60}")
print(f"Step 2: load_settings + read Stage 1 output")
print(f"{'='*60}")
settings = load_settings()
sup = read_pickle("out/1-assemble-sup")
print(f"  universe: {len(sup.universe):,} rows")
print(f"  sales:    {len(sup.sales):,} rows")

print(f"\n{'='*60}")
print(f"Step 3: examine_sup")
print(f"{'='*60}")
examine_sup(sup, settings)

print(f"\n{'='*60}")
print(f"Step 4: fill_unknown_values_sup")
print(f"{'='*60}")
sup = fill_unknown_values_sup(sup, settings)

print(f"\n{'='*60}")
print(f"Step 5: horizontal equity clusters")
print(f"{'='*60}")
sup = from_checkpoint(
    "2-clean-00-horizontal-equity",
    mark_horizontal_equity_clusters_per_model_group_sup,
    {"sup": sup, "settings": settings, "verbose": verbose,
     "do_land_clusters": True, "do_impr_clusters": True},
)

print(f"\n{'='*60}")
print(f"Step 6: process_sales")
print(f"{'='*60}")
sup = from_checkpoint(
    "2-clean-01-process_sales",
    process_sales,
    {"sup": sup, "settings": load_settings(), "verbose": verbose},
)

print(f"\n{'='*60}")
print(f"Step 7: sales scrutiny")
print(f"{'='*60}")
sup = from_checkpoint(
    "2-clean-02-sales-scrutiny",
    run_sales_scrutiny,
    {"sup": sup, "settings": load_settings(),
     "drop_cluster_outliers": True,
     "drop_heuristic_outliers": True,
     "verbose": verbose},
)

print(f"\n{'='*60}")
print(f"Step 8: write output")
print(f"{'='*60}")
write_notebook_output_sup(sup, "2-clean")
print(f"  universe: {len(sup.universe):,} rows")
print(f"  sales:    {len(sup.sales):,} rows")
print("Done!")
