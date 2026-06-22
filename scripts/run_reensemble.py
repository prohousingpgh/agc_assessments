"""
Re-blend the main ensemble to a fixed member set WITHOUT retraining.

The trained per-engine predictions (out/models/<group>/main/<engine>/pred_*.parquet)
are the source of truth and are never modified. This script recomputes the
ensemble as the per-row MEDIAN of ENSEMBLE_MEMBERS, overwrites the ensemble's
prediction (in model_ensemble.pickle and ensemble/pred_*.parquet), and
regenerates the ratio-study breakdowns — all in ~1 minute, avoiding the
~80-minute finalize_models retrain.

Why: the built-in ensemble optimizer maximizes accuracy (MAPE) with no equity
term, so it blends in the regressive spatial/tree engines and lands at a badly
negative VEI. Restricting the blend to the log MRA engines + lightgbm drives VEI
from roughly -16..-31 down to about -10..+1 across groups with no COD cost
(verified empirically 2026-06-21 on the per-engine test predictions).

Usage:
    python scripts/run_reensemble.py            # DRY RUN: report only, no writes
    python scripts/run_reensemble.py --apply     # overwrite ensemble + rebuild ratio study

Idempotent: re-running reproduces the same blend (it only reads the per-engine
preds). The original all-engine ensemble is recoverable by re-running
finalize_models. On --apply, the prior ensemble prediction is preserved in the
pickle dataframes as 'prediction_pre_reensemble' for comparison.
"""
import os, sys, glob, pickle
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pandas as pd
pd.options.future.infer_string = False
import numpy as np
os.environ["PYTHONIOENCODING"] = "utf-8"

openavmkit_repo = os.path.abspath("C:/projects/openavmkit")
if openavmkit_repo not in sys.path:
    sys.path.insert(0, openavmkit_repo)

locality = "us-pa-allegheny"
ENSEMBLE_MEMBERS = ["mra", "multi_mra", "lightgbm"]
# The fixed trio blend was validated on the residential groups. It does NOT
# suit commercial (~60 sales, very different dynamics — empirically the trio
# drives commercial VEI much worse), so leave commercial's own ensemble alone.
SKIP_GROUPS = {"commercial"}
APPLY = "--apply" in sys.argv

from openavmkit.pipeline import init_notebook, load_settings, run_and_write_ratio_study_breakdowns
from openavmkit.vertical_equity_study import get_vertical_equity_scores

init_notebook(locality)
settings = load_settings()


def cod_trim(ratio, trim=0.05):
    r = np.sort(ratio[np.isfinite(ratio)])
    n = len(r)
    k = int(n * trim)
    if n - 2 * k > 5:
        r = r[k:n - k]
    med = np.median(r)
    return (100 * np.mean(np.abs(r - med)) / med, med, len(r)) if len(r) else (np.nan, np.nan, 0)


def join_key(df):
    return "key_sale" if "key_sale" in df.columns else "key"


def blend_for(base, subset_file):
    """Per-row median of ENSEMBLE_MEMBERS for a subset (pred_test/pred_sales/pred_universe)."""
    merged = None
    for m in ENSEMBLE_MEMBERS:
        p = f"{base}/{m}/{subset_file}.parquet"
        if not os.path.exists(p):
            return None, None
        d = pd.read_parquet(p)
        k = join_key(d)
        d = d[[k, "prediction"]].rename(columns={"prediction": m})
        merged = d if merged is None else merged.merge(d, on=k, how="inner")
    merged["__blend__"] = merged[ENSEMBLE_MEMBERS].median(axis=1)
    return merged[[join_key(merged), "__blend__"]], join_key(merged)


def vei_of(pred, denom):
    d = pd.DataFrame({"s": denom.values, "v": np.asarray(pred)})
    d = d[np.isfinite(d["s"]) & (d["s"] > 0) & np.isfinite(d["v"])]
    try:
        return get_vertical_equity_scores(d, "s", "v")["vei"]
    except Exception:
        return np.nan


print(f"\n{'='*72}")
print(f"Re-ensemble to median{ENSEMBLE_MEMBERS}   mode={'APPLY' if APPLY else 'DRY RUN'}")
print(f"{'='*72}")
print(f"{'group':<46}{'VEI old':>8}{'VEI new':>8}{'mr new':>7}{'COD new':>8}")

groups = sorted(glob.glob("out/models/*/main/model_ensemble.pickle"))
for pkl_path in groups:
    base = os.path.dirname(pkl_path)                 # out/models/<group>/main
    g = os.path.basename(os.path.dirname(base))      # <group>
    base = base.replace("\\", "/")

    if g in SKIP_GROUPS:
        print(f"{g:<46}{'-- skipped (SKIP_GROUPS) --':>31}")
        continue

    # blends per subset
    blends = {}
    ok = True
    for subset in ["pred_test", "pred_sales", "pred_universe"]:
        b, k = blend_for(base, subset)
        if b is None:
            ok = False
            break
        blends[subset] = (b, k)
    if not ok:
        print(f"{g:<46}{'-- missing member predictions, skipped --':>31}")
        continue

    res = pickle.load(open(pkl_path, "rb"))

    # report old vs new VEI on the test set (vs the model's time-adjusted target)
    df_test = getattr(res, "df_test", None)
    vei_old = vei_new = mr_new = cod_new = np.nan
    if df_test is not None and "sale_price_time_adj" in df_test.columns:
        k = join_key(df_test)
        bt = blends["pred_test"][0].rename(columns={blends["pred_test"][1]: k})
        merged = df_test.merge(bt, on=k, how="inner")
        vei_old = vei_of(merged["prediction"], merged["sale_price_time_adj"]) if "prediction" in merged else np.nan
        vei_new = vei_of(merged["__blend__"], merged["sale_price_time_adj"])
        if "sale_price" in merged.columns:
            ratio = (merged["__blend__"] / merged["sale_price"]).values
            cod_new, mr_new, _ = cod_trim(ratio)
    print(f"{g:<46}{vei_old:>8.1f}{vei_new:>8.1f}{mr_new:>7.2f}{cod_new:>8.1f}")

    if APPLY:
        # overwrite prediction in the pickle dataframes and the ensemble pred parquets
        for attr, subset in [("df_test", "pred_test"), ("df_sales", "pred_sales"), ("df_universe", "pred_universe")]:
            df = getattr(res, attr, None)
            if df is None:
                continue
            b, bk = blends[subset]
            k = join_key(df)
            if k != bk:
                b = b.rename(columns={bk: k})
            df = df.copy()
            if "prediction" in df.columns and "prediction_pre_reensemble" not in df.columns:
                df["prediction_pre_reensemble"] = df["prediction"]
            df = df.drop(columns=["prediction"], errors="ignore").merge(
                b.rename(columns={"__blend__": "prediction"}), on=k, how="left")
            setattr(res, attr, df)

        pickle.dump(res, open(pkl_path, "wb"))

        # keep the ensemble/pred_*.parquet consistent for downstream consumers
        for subset in ["pred_test", "pred_sales", "pred_universe"]:
            epath = f"{base}/ensemble/{subset}.parquet"
            if os.path.exists(epath):
                edf = pd.read_parquet(epath)
                b, bk = blends[subset]
                k = join_key(edf) if join_key(edf) in edf.columns else bk
                if k != bk:
                    b = b.rename(columns={bk: k})
                if "prediction" in edf.columns and "prediction_pre_reensemble" not in edf.columns:
                    edf["prediction_pre_reensemble"] = edf["prediction"]
                edf = edf.drop(columns=["prediction"], errors="ignore").merge(
                    b.rename(columns={"__blend__": "prediction"}), on=k, how="left")
                edf.to_parquet(epath, index=False)
                # Also refresh the .csv twin — downstream consumers
                # (combineOutputFiles.py and the maps) read the CSV, not the
                # parquet, so leaving it stale silently publishes the old
                # all-engine ensemble. Drop geometry to keep it CSV-friendly.
                edf.drop(columns=[c for c in ("geometry",) if c in edf.columns]).to_csv(
                    epath[: -len(".parquet")] + ".csv", index=False)

if APPLY:
    print(f"\nRegenerating ratio-study breakdowns with the new blend...")
    run_and_write_ratio_study_breakdowns(settings)
    print("Done. Updated ensemble + ratio-study reports under out/models/<group>/.")
else:
    print(f"\nDRY RUN — nothing written. Re-run with --apply to overwrite the ensemble and rebuild the ratio study.")
