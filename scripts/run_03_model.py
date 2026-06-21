"""
Stage 3: Spatial-lag enrichment, feature selection, model training, ratio studies.
Requires Stage 2 output (out/2-clean-sup.pickle).
Run from any directory.

Flags (set before running):
  DO_SHAPS = True   — compute SHAP contributions (slow, ~minutes per group)
  RUN_TRY_STEPS = False — skip try_variables/try_models, go straight to finalize_models
"""
import os, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import matplotlib
matplotlib.use("Agg")
import pandas as pd
pd.options.future.infer_string = False
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUNBUFFERED"] = "1"
sys.stdout.reconfigure(line_buffering=True)

openavmkit_repo = os.path.abspath("C:/projects/openavmkit")
if openavmkit_repo not in sys.path:
    sys.path.insert(0, openavmkit_repo)

locality = "us-pa-allegheny"
verbose = True

DO_SHAPS = False
RUN_TRY_STEPS = False

from openavmkit.pipeline import (
    init_notebook,
    from_checkpoint,
    delete_checkpoints,
    load_settings,
    load_cleaned_data_for_modeling,
    examine_sup,
    write_canonical_splits,
    try_variables,
    try_models,
    finalize_models,
    compute_model_contributions,
    run_and_write_ratio_study_breakdowns,
    enrich_sup_spatial_lag,
    write_parquet,
)

print(f"\n{'='*60}")
print(f"Step 1: init_notebook + clear non-preserved checkpoints")
print(f"{'='*60}")
init_notebook(locality)
# Preserve the expensive spatial-lag checkpoint across re-runs.
# Delete manually (out/checkpoints/3-model-00-enrich-spatial-lag*) if input data changes.
import glob as _glob
_PRESERVE = {"spatial-lag", "02a-train-predict"}
for _f in _glob.glob("out/checkpoints/3-model-*.pickle"):
    if not any(tag in _f for tag in _PRESERVE):
        os.remove(_f)
del _glob, _PRESERVE

print(f"\n{'='*60}")
print(f"Step 2: load_settings + load Stage 2 output")
print(f"{'='*60}")
settings = load_settings()
sup = load_cleaned_data_for_modeling(settings)
print(f"  universe: {len(sup.universe):,} rows")
print(f"  sales:    {len(sup.sales):,} rows")

print(f"\n{'='*60}")
print(f"Step 3: examine_sup")
print(f"{'='*60}")
examine_sup(sup, load_settings())

print(f"\n{'='*60}")
print(f"Step 4: write_canonical_splits")
print(f"{'='*60}")
write_canonical_splits(sup, load_settings(), verbose=verbose)

print(f"\n{'='*60}")
print(f"Step 5: enrich_sup_spatial_lag (checkpointed — expensive)")
print(f"{'='*60}")
sup = from_checkpoint(
    "3-model-00-enrich-spatial-lag",
    enrich_sup_spatial_lag,
    {"sup": sup, "settings": load_settings(), "verbose": verbose},
)
write_parquet(sup.universe, "out/look/3-spatial-lag-universe.parquet")
write_parquet(sup.sales,    "out/look/3-spatial-lag-sales.parquet")

if RUN_TRY_STEPS:
    print(f"\n{'='*60}")
    print(f"Step 6: try_variables")
    print(f"{'='*60}")
    try_variables(sup=sup, settings=load_settings(), verbose=verbose)

    print(f"\n{'='*60}")
    print(f"Step 7: try_models")
    print(f"{'='*60}")
    try_models(sup=sup, settings=load_settings(), verbose=verbose)
else:
    print("\nSkipping try_variables / try_models (RUN_TRY_STEPS=False)")

print(f"\n{'='*60}")
print(f"Step 8: finalize_models")
print(f"{'='*60}")
sup = from_checkpoint(
    "3-model-02a-train-predict",
    finalize_models,
    {"sup": sup, "settings": load_settings(),
     "run_main": True, "run_vacant": False, "verbose": verbose},
)

if DO_SHAPS:
    print(f"\n{'='*60}")
    print(f"Step 9: compute_model_contributions (SHAP)")
    print(f"{'='*60}")
    compute_model_contributions(sup=sup, settings=load_settings(), verbose=verbose)
else:
    print("\nSkipping SHAP contributions (DO_SHAPS=False)")

print(f"\n{'='*60}")
print(f"Step 10: ratio study breakdowns")
print(f"{'='*60}")
try:
    run_and_write_ratio_study_breakdowns(load_settings())
except Exception as e:
    print(f"WARNING: ratio study breakdowns failed: {e}")
    print("Continuing — model outputs in out/models/ are complete.")

print("\nDone! Results in out/models/")
