"""Generate the report's choropleth figures from the pipeline outputs.

Companion to build_report.py: that script generates the *numbers* (macros + tables);
this one generates the *maps*. Both read only from committed pipeline outputs so the
report has no hand-authored content.

Outputs (report/figures/, gitignored — regenerate from data):
  median_sales_ratio_existing.png   median(current assessment / sale price) by tract
  median_sales_ratio_new.png        median(model prediction / sale price) by tract
  land_value_existing.png           current land assessment per sqft by tract
  land_value_new.png                modeled land value per sqft by tract
  valuation_ratio_parcel.png        median(new / current total assessment) by tract

All maps are census-tract choropleths over Allegheny County (FIPS 42003). The five
model groups are concatenated so each map covers the whole county. Tracts with too
few observations are left blank (grey) rather than drawn from noise.

Run:  C:/Users/druss/miniconda3/python.exe report/build_figures.py
"""

import gc
import os
import pickle
import sys

import pandas as pd

pd.options.future.infer_string = False  # avoid pandas 2.x Arrow-string errors in openavmkit
sys.path.insert(0, "C:/projects/openavmkit")

import geopandas as gpd  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LogNorm, TwoSlopeNorm  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MODELS = os.path.join(ROOT, "data", "us-pa-allegheny", "out", "models")
OUTPUT = os.path.join(ROOT, "output")
TRACTS_GEOJSON = os.path.join(ROOT, "data", "allegheny_census_tracts_2020.geojson")
FIGDIR = os.path.join(HERE, "figures")

GROUPS = [
    "commercial",
    "residential_multi_family",
    "residential_single_family_urban",
    "residential_single_family_suburban_prewar",
    "residential_single_family_suburban",
]

# Suppress tracts with too few observations (single-sale ratios are pure noise).
MIN_SALES = 5      # for the sales-ratio maps
MIN_PARCELS = 15   # for the universe-based (land / valuation-ratio) maps

PROJ = 3857        # web mercator — nicer county shape than raw lat/lon for display


# ----------------------------------------------------------------------------- joins
def ct_to_tractce(series):
    """'4520' / '4070.02' -> 6-digit TRACTCE '452000' / '407002' (= round(ct*100))."""
    v = pd.to_numeric(series, errors="coerce")
    code = (v * 100).round()
    out = code.astype("Int64").astype("string").str.zfill(6)
    return out.where(v.notna(), pd.NA)


def ratio(num, den):
    """Float division with non-positive denominators -> NaN (nullable-int cols raise on /0)."""
    num = pd.to_numeric(num, errors="coerce").astype("float64")
    den = pd.to_numeric(den, errors="coerce").astype("float64")
    return num / den.where(den > 0)


def load_group(group):
    """Return (sales_df, universe_df) slimmed to the columns the maps need, or (None, None)."""
    path = os.path.join(MODELS, group, "main", "model_ensemble.pickle")
    if not os.path.exists(path):
        print(f"  [skip] {group}: no model_ensemble.pickle")
        return None, None
    with open(path, "rb") as fh:
        r = pickle.load(fh)
    s_cols = [c for c in ["census_tract", "sale_price", "assr_market_value", "prediction"]
              if c in r.df_sales.columns]
    u_cols = [c for c in ["census_tract", "assr_land_value", "land_area_sqft",
                          "assr_market_value", "prediction"] if c in r.df_universe.columns]
    sales = r.df_sales[s_cols].copy()
    univ = r.df_universe[u_cols].copy()
    del r
    gc.collect()
    print(f"  [ok]   {group}: {len(sales):,} sales, {len(univ):,} parcels")
    return sales, univ


def tract_aggregate(df, value_fn, min_count):
    """value_fn(df)->per-row Series; return per-TRACTCE median with a min-count floor."""
    d = df.copy()
    d["tractce"] = ct_to_tractce(d["census_tract"])
    d["_v"] = value_fn(d)
    d = d[d["tractce"].notna() & np.isfinite(d["_v"])]
    g = d.groupby("tractce")["_v"]
    out = g.median()
    out = out[g.count() >= min_count]
    return out


def tract_ratio_weighted(df, num, den, min_count):
    """Per-TRACTCE sum(num)/sum(den) (e.g. total land value / total land area)."""
    d = df.copy()
    d["tractce"] = ct_to_tractce(d["census_tract"])
    d = d[d["tractce"].notna() & (d[den] > 0) & d[num].notna() & (d[num] > 0)]
    g = d.groupby("tractce")
    out = g[num].sum() / g[den].sum()
    out = out[g.size() >= min_count]
    return out


# ----------------------------------------------------------------------------- plotting
def choropleth(tracts, county, values, title, fname, *, cmap, norm, cbar_label):
    gdf = tracts.merge(values.rename("val"), left_on="TRACTCE", right_index=True, how="left")
    n_shown = int(gdf["val"].notna().sum())
    fig, ax = plt.subplots(figsize=(9, 7.5))
    gdf.plot(column="val", ax=ax, cmap=cmap, norm=norm, linewidth=0.05, edgecolor="white",
             missing_kwds={"color": "#e9e9e9", "edgecolor": "white", "linewidth": 0.05})
    county.boundary.plot(ax=ax, color="#333333", linewidth=0.8)
    ax.set_title(title, fontsize=14, pad=10)
    ax.axis("off")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.62, fraction=0.04, pad=0.01)
    cbar.set_label(cbar_label, fontsize=10)
    ax.annotate(f"{n_shown} of {len(tracts)} tracts shown (grey = insufficient data)",
                xy=(0.5, 0.005), xycoords="axes fraction", ha="center", fontsize=7,
                color="#777777")
    fig.savefig(fname, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {os.path.relpath(fname, ROOT)}  ({n_shown} tracts)")


def ratio_norm(*series, cap_lo=0.2, cap_hi=1.6):
    """Shared diverging norm centered at 1.0 across one or more ratio series."""
    allv = pd.concat([s for s in series])
    lo = max(cap_lo, float(np.nanpercentile(allv, 2)))
    hi = min(cap_hi, float(np.nanpercentile(allv, 98)))
    lo = min(lo, 0.99)
    hi = max(hi, 1.01)
    return TwoSlopeNorm(vmin=lo, vcenter=1.0, vmax=hi)


def log_norm(*series):
    allv = pd.concat([s for s in series])
    lo = max(0.25, float(np.nanpercentile(allv, 2)))
    hi = float(np.nanpercentile(allv, 98))
    return LogNorm(vmin=lo, vmax=hi)


# ----------------------------------------------------------------------------- main
def main():
    os.makedirs(FIGDIR, exist_ok=True)

    print("Loading geometry...")
    tracts = gpd.read_file(TRACTS_GEOJSON)[["TRACTCE", "geometry"]].to_crs(epsg=PROJ)
    county = tracts.dissolve()

    print("Loading model groups...")
    sales_parts, univ_parts = [], []
    for grp in GROUPS:
        s, u = load_group(grp)
        if s is not None:
            sales_parts.append(s)
            univ_parts.append(u)
    sales = pd.concat(sales_parts, ignore_index=True)
    univ = pd.concat(univ_parts, ignore_index=True)
    print(f"Combined: {len(sales):,} sales, {len(univ):,} parcels")

    # --- 1 & 2: median sales ratio (existing vs new), shared diverging scale ----
    sr_exist = tract_aggregate(sales, lambda d: ratio(d["assr_market_value"], d["sale_price"]), MIN_SALES)
    sr_new = tract_aggregate(sales, lambda d: ratio(d["prediction"], d["sale_price"]), MIN_SALES)
    sr_norm = ratio_norm(sr_exist, sr_new)
    choropleth(tracts, county, sr_exist,
               "Median sales ratio by census tract\nCurrent assessments",
               os.path.join(FIGDIR, "median_sales_ratio_existing.png"),
               cmap="RdBu", norm=sr_norm, cbar_label="assessed ÷ sale price")
    choropleth(tracts, county, sr_new,
               "Median sales ratio by census tract\nNew assessments",
               os.path.join(FIGDIR, "median_sales_ratio_new.png"),
               cmap="RdBu", norm=sr_norm, cbar_label="predicted ÷ sale price")

    # --- 3 & 4: land value per sqft (existing vs new), shared log scale ----------
    land_exist = tract_ratio_weighted(univ, "assr_land_value", "land_area_sqft", MIN_PARCELS)
    land_new = pd.read_csv(os.path.join(OUTPUT, "census_tract_land_price_per_sqft.csv"))
    land_new = land_new.assign(TRACTCE=ct_to_tractce(land_new["CENSUS_TRACT"])) \
                       .dropna(subset=["TRACTCE"]).set_index("TRACTCE")["LAND_VALUE_PER_SQFT"]
    land_norm = log_norm(land_exist, land_new)
    choropleth(tracts, county, land_exist,
               "Land value per square foot by census tract\nCurrent assessments",
               os.path.join(FIGDIR, "land_value_existing.png"),
               cmap="viridis", norm=land_norm, cbar_label="$ / sqft (log scale)")
    choropleth(tracts, county, land_new,
               "Land value per square foot by census tract\nNew assessments",
               os.path.join(FIGDIR, "land_value_new.png"),
               cmap="viridis", norm=land_norm, cbar_label="$ / sqft (log scale)")

    # --- 5: valuation ratio (new / current total assessment) by tract -----------
    val_ratio = tract_aggregate(univ, lambda d: ratio(d["prediction"], d["assr_market_value"]), MIN_PARCELS)
    # New assessments exceed current almost everywhere (county under-assesses ~2x), so the
    # ratio is rarely < 1. Center the diverging scale on the county-typical increase (median)
    # to show which tracts rise more vs. less than typical.
    vr_lo = float(np.nanpercentile(val_ratio, 2))
    vr_hi = float(np.nanpercentile(val_ratio, 98))
    vr_mid = min(max(float(np.nanmedian(val_ratio)), vr_lo + 1e-6), vr_hi - 1e-6)
    vr_norm = TwoSlopeNorm(vmin=vr_lo, vcenter=vr_mid, vmax=vr_hi)
    choropleth(tracts, county, val_ratio,
               "Valuation ratio by census tract\nNew ÷ current total assessment",
               os.path.join(FIGDIR, "valuation_ratio_parcel.png"),
               cmap="RdBu_r", norm=vr_norm, cbar_label="new ÷ current (white = county median)")

    print("\nDone. Figures in", os.path.relpath(FIGDIR, ROOT))


if __name__ == "__main__":
    main()
