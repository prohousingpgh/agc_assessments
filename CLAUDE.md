# CLAUDE.md — AGC Assessments (Allegheny County, PA)

Allegheny County property-assessment AVM pipeline built on OpenAvmKit (FIPS 42003,
valuation date 2026-01-01). This file holds **AGC-specific operating facts**. For
general OpenAvmKit library/code patterns (public API surface, the `settings.json`
`__comment`/`$$ref` preprocessor, how to modify the library safely) see the shared
canonical doc: `C:/projects/openavmkit/AGENTS.md`.

Sibling projects on the same machine share the same OpenAvmKit clone: `philly_open_avmkit`,
`berks_open_avmkit`. Their CLAUDE.md files hold deeper operational detail — consult them
when a pitfall here is under-documented.

---

## Environment / running the pipeline

- **Python:** always `C:/Users/druss/miniconda3/python.exe`. The system `python` is a
  Microsoft Store stub and does not work.
- **Working directory:** launch all Stage scripts with cwd = `C:/projects/agc_assessments`.
  `init_notebook(locality)` does `os.chdir("data/us-pa-allegheny")` *from cwd* — launching
  from anywhere else doubles the path and crashes with "Could not find settings file:
  in/settings.json".
- **Encoding (script startup):** scripts call `sys.stdout.reconfigure(encoding="utf-8")`.
  Setting `os.environ["PYTHONIOENCODING"]` inside a running process has no effect — the
  live-stream reconfigure is what's required.
- **`pd.options.future.infer_string = False`** must be set before openavmkit imports
  (pandas 2.x Arrow-string default otherwise triggers `ArrowExtensionArray` errors deep in
  the library). Present in `run_03_model.py`; ensure it's in any new pipeline script.
- **Census API key** lives in `.env` as `CENSUS_API_KEY` (gitignored). Required for Stage 1
  census enrichment.

## Editing settings.json (CRLF + tabs + BOM)

`data/us-pa-allegheny/in/settings.json` uses **Windows CRLF** line endings and **7 tabs**
of indentation for `ind_vars` list items. The Edit tool often can't match this. Use
PowerShell `[System.IO.File]::ReadAllText/WriteAllText` with backtick-escaped `` `r`n ``
and `` `t ``. **Write BOM-free UTF-8** via `New-Object System.Text.UTF8Encoding($false)` —
the default `[System.Text.Encoding]::UTF8` writes a BOM and Python then fails with
"Unexpected UTF-8 BOM". Always `json.load` the file afterward to validate.

## Checkpoint management

Stage 3 (`run_03_model.py`) deletes all `out/checkpoints/3-model-*.pickle` on launch
**except** those tagged `spatial-lag` and `02a-train-predict` (the `_PRESERVE` set):
- `3-model-00-enrich-spatial-lag.pickle` (~765 MB) — expensive KDE/KNN; reused across runs.
- `3-model-02a-train-predict.pickle` — trained models; delete manually to force re-training
  (a settings/feature change alone won't retrain unless this is removed).

**To pick up new Stage-1 enrichment (e.g. `pct_minority`) in the ratio study, the spatial-lag
checkpoint MUST be deleted** — otherwise Stage 3 rebuilds `sup` from the stale checkpoint
that lacks the new column.

**SHAP/contributions are OFF by default and must stay off for iteration.** `finalize_models`
defaults to `do_contributions=True`, which computes slow per-engine SHAP/contribution CSVs
*inside the training pass*. `run_03_model.py` now passes `do_contributions=False` (commit
`5f1f46b`) so contributions are only ever computed in Step 9, gated by `DO_SHAPS` (default
`False`). This roughly halves Stage 3 wall-clock (~40 min vs 80+). Only set `DO_SHAPS=True`
for a final publication run (explainability / IAAO narrative) — never for metric/equity
iteration. The 2026-06-21 runs were killed by Modern Standby partly because the un-deferred
contributions step kept Stage 3 running long enough to hit the idle-sleep window.

### Full-rebuild sequence (Stage 1 → 3) — the enrichment-cache landmine

**Verified mechanism (`openavmkit/utilities/cache.py`):** enrichment steps (census, OSM,
DEM, geometry) cache their output under `cache/<name>.cols.parquet` with a signature keyed
on the **base input DataFrame shape + that enrichment's settings dict** — *not* on the
enrichment output or the enrichment **code**. So if you change enrichment *code* (e.g. add a
variable to `census.py`'s `get_census_map`, or change which OSM tags `openstreetmap.py`
queries) without changing the base parcels or the settings dict, the signature still matches
and the **stale cached result is served silently** — your code change does nothing.
`clear_cache()` itself is buggy (malformed `.cols`/`.rows` paths, ~line 160), so it does not
reliably remove these — **delete the files manually.**

**Lessons from the 2026-06-21 rebuild (rivers worked; pct_minority needed a 2nd patch; sleep killed it):**

- **OSM rivers fix: WORKED.** AGC enriches TWO separate OSM features: `rivers` (2-mi radius,
  uses `_get_tags("rivers")`, cached at `cache/osm/rivers.parquet` + `do_distance_osm_rivers`)
  AND `water` (1-mi, `_get_tags("water")` = reservoirs/canals/natural, cached at
  `osm/water.parquet`). `proximity_to_osm_rivers` and `proximity_to_osm_water` are BOTH in
  ind_vars. The `openstreetmap.py` `waterway` patch is on the `rivers` tag set — after the
  rebuild `osm/rivers.parquet` has 7,059 waterway linestrings (500 river + 6,559 stream),
  vs polygons-only before. Deleting `osm/all.cols.parquet` cascades a full OSM re-enrich that
  re-fetches rivers too, so rivers regenerated even though only the water caches were
  explicitly deleted — but to be safe, also delete `osm/rivers.parquet` + sig +
  `osm/do_distance_osm_rivers.cols.parquet` + sig when changing the rivers tags.
- **`pct_minority` needs TWO patches, not one.** `census.py` computes it, but
  `_enrich_df_census` in `data.py` built its keep-list only from `get_census_map()`'s raw ACS
  fields, so the *derived* `pct_minority` was filtered out before the parcel join. Fixed in
  `data.py` (commit `7eacf70`, philly-patches-0.6.0) to also keep known derived census cols.
  Both patches must be present for `pct_minority` to enrich. Still needs a Stage-1 rebuild to
  populate (the 2026-06-21 rebuild produced everything EXCEPT pct_minority because the data.py
  fix landed after).
- **Disable sleep for any unattended Stage 1/3 run.** The 2026-06-21 rebuild died at Stage 3
  when the machine entered Modern Standby (DC/battery standby timeout was **3 minutes**),
  which suspends/kills background processes. Before a long run: `powercfg /change
  standby-timeout-ac 0` and `standby-timeout-dc 0`, and **restore the captured originals
  after** (AC was 60 min, DC 3 min).

Then the full sequence:
1. Delete the enrichment caches: `cache/census.cols.parquet` + sig (→ `pct_minority`);
   `cache/osm/rivers.parquet` + sig + `osm/do_distance_osm_rivers.cols.parquet` + sig and
   `osm/all.cols.parquet` + sig (→ river-aware proximity). Leave `osm/do_distance_osm_parks*`
   alone (unaffected, expensive).
2. Disable sleep (see above).
3. Re-run Stage 1, Stage 2, Stage 3 in order.
4. Delete `out/checkpoints/3-model-00-enrich-spatial-lag.pickle` so Stage 3 rebuilds `sup`
   with the new columns (otherwise the stale checkpoint is reused).
5. On a Stage-1 rebuild that changes the row set, also clear the horizontal-equity cluster
   caches `cache/he_id.cols.parquet`, `cache/impr_he_id.cols.parquet`,
   `cache/land_he_id.cols.parquet`.
6. Hyperparameter JSONs (`out/models/<group>/main/*_params.json`) are **not** cleared by
   checkpoint deletion; delete manually only if you intend to re-tune. *(Relayed — unverified.)*
7. Restore the sleep timeouts when the run completes.

## Interpreting ratio-study output

**Verified:** `ratio_study.py` uses the raw `sale_price` column as ground truth at every
breakdown (lines ~452–613); `time_adjustment.py` writes only the separate
`sale_price_time_adj` column and never overwrites `sale_price`. So the ratio-study
median-ratio/COD tables compare predictions against **raw, non-time-adjusted sale price**,
even though the model targets the 2026-01-01 valuation date. Because test sales are from
2025, a *well-calibrated* model shows a median ratio **somewhat below 1.0** — the offset
tracks Allegheny's 2025→2026 price trend (confirm magnitude from the time-adjustment factor
in the run logs). **Do not read a sub-1.0 median ratio as pure under-prediction.**

**Asymmetry — VEI uses a different denominator.** `get_vertical_equity_scores`
(`vertical_equity_study.py`, called from `modeling.py:1410`) computes the ratio against
`dep_var_test`, which for log/time-adjusted targets is **not** raw `sale_price`. So the VEI
column and the ratio-study median-ratio tables are measured against different reference
prices — don't expect them to reconcile exactly.

## OpenAvmKit shared clone — branch + local patches

The clone at `C:/projects/openavmkit` is **shared across all three PA county projects** and
rides whatever branch is checked out — currently **`philly-patches-0.6.0`**. Don't switch
branches without confirming the pipeline still runs (and clear `__pycache__` after any
switch). Local patches committed on this branch by AGC work:
- `utilities/census.py` (`fc9c57e`) — fetch ACS B03002, compute `pct_minority`.
  **Equity-sensitive — do NOT re-file publicly** (upstream #361 was closed at Lars's request;
  he handles racial-composition changes privately).
- `utilities/openstreetmap.py` (`fc9c57e`) — `rivers` query also matches `waterway`
  linestrings (Pittsburgh's three rivers are linestrings, not polygon water areas).
- `data.py` (`7eacf70`) — `_enrich_df_census` keeps *derived* census cols (`pct_minority`)
  through the parcel join, not just the raw ACS fields in `get_census_map()`. **Required
  alongside census.py for `pct_minority` to enrich.** Equity-sensitive — keep private.
- `utilities/cache.py` (`5e719aa`) — fix `clear_cache()` malformed `.cols`/`.rows` paths.
  Generic; safe to PR.
- `vertical_equity_study.py` (`5f8ef07`) — fix `vei_significance` to use inner CI bounds.
  vei_sig is now trustworthy. Generic; safe to PR.
- `ratio_study.py` (`87fcbf3`, `b794690`) — robust quantile binning (np.nanquantile +
  strict-monotonic edges; skips degenerate) AND a new explicit-`bins`/`bin_labels` breakdown
  option (used for the `pct_minority` composition bands). Generic; safe to PR.

Because the branch is shared, all of these affect Philly/Berks on their next Stage 1/3 too
(all additive). The generic infra fixes (cache, ratio_study, vei_sig) are upstream-PR
candidates; the equity-sensitive ones (census.py, data.py) must NOT be PR'd publicly.

## Open issues we're tracking

- **Ratio-study call signature:** `run_and_write_ratio_study_breakdowns(settings)` takes
  only `settings`. `run_03_model.py` was calling it with `sup=/verbose=` and silently
  failing at Step 10 — fixed. `scripts/run_ratio_study.py` runs the breakdowns standalone
  against trained pickles (~1 min) without re-training.
- **`vei_significance` — FIXED** (`5f8ef07`): was using outer CI bounds (couldn't distinguish
  significant from non-significant regressivity); now uses inner bounds and is trustworthy.
  (The related upstream equity-testing issue #362 was closed at Lars's request — handle
  equity testing privately.)
- **Bulk/multi-parcel deed contamination:** Philly found deed records stamp the full bundle
  price on every parcel, inflating vacant/commercial $/sqft ~4×; OpenAvmKit heuristics have
  a structural blind spot. **Check whether Allegheny sales data has the same structure.**

## Current model config (as of this session)

- Groups: `commercial`, `residential_multi_family`, `residential_single_family_urban`,
  `residential_single_family_suburban_prewar`, `residential_single_family_suburban`.
- `mra` + `multi_mra` use `"log": true` in **all** residential groups (fixes OLS
  reversion-to-mean / negative VEI; prewar was the last to get it).
- Residential linear `ind_vars` include census `median_income`, `median_g_rent`, and the
  PCRG MVA tier `market_value_category` (categorical) — **kept on condition of equity
  testing** (ratio-study breakdowns by income quintile, and `pct_minority` once enriched).
- `ratio_study.breakdowns` include `{"by":"median_income","quantiles":5}` and
  `{"by":"pct_minority","bins":[0,0.1,0.25,0.5,0.75,1.0],"bin_labels":[...]}` — explicit
  composition bands (isolating a majority-minority >50% stratum); quantiles are degenerate on
  zero-inflated `pct_minority`. `pct_minority` is now enriched (needs both the census.py +
  data.py patches). **Equity result (2026-06-22):** level equity passes across income AND
  racial composition; COD/uniformity gradient breaches IAAO ≤20 only in majority-minority
  older/urban tracts (prewar, urban). See the `agc-rebuild-2026-06-21-night-recovery` memory.
- **VEI fix — ensemble re-blend.** OpenAvmKit's ensemble optimizer maximizes accuracy (MAPE)
  with no equity term, so the default all-engine blend is badly regressive (prewar VEI ~−32).
  Restricting the blend to the median of `[mra, multi_mra, lightgbm]` (drop the regressive
  spatial/comparable engines) fixes it with no COD cost. Apply via
  `python scripts/run_reensemble.py --apply` (no retrain; reads the trained per-engine preds,
  overwrites the ensemble + regenerates the ratio study in ~1 min; dry-run without `--apply`).
  **Commercial is in `SKIP_GROUPS`** (the trio worsens its VEI — ~60 sales, different
  dynamics). Applied 2026-06-21: prewar −32→−12, urban −12→+8, suburban −14→−7, MF −11→−6.
  `settings.json` also pins `ensemble.models=[trio]`, but that's currently inert — the
  prediction path reads the wrong key (`benchmark.py` ~3114 reads `"list"` not `"models"`);
  the permanent fix is that one-liner, after which commercial needs a per-group override.
