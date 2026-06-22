# TODO — AGC Assessments

Open items for the Allegheny County AVM project. See `CLAUDE.md` for operating
facts and `README` for current results. Status as of 2026-06-22.

## Near-term / decisions

- [ ] **Permanently disable Modern Standby** so unattended pipeline runs stop getting
  killed mid-run. In an **elevated** PowerShell/Command Prompt, then **reboot**:
  `reg add HKLM\SYSTEM\CurrentControlSet\Control\Power /v PlatformAoAcOverride /t REG_DWORD /d 0 /f`
  (reversible — delete the value to restore). After reboot, `powercfg /change standby-timeout-ac 0`
  actually works. Three runs were killed by Modern Standby before this was understood;
  software keep-awake (powercfg, SetThreadExecutionState, input nudges) did **not** override it.
- [x] **`scripts/combineOutputFiles.py` committed** (`9e1414d`) — reviewed the pre-existing
  vectorization refactor (per-row `iterrows` → pandas masks; updated `model_groups` to the five
  current groups; robust date parsing), restored a dropped `CLASS=='R'` guard on the
  `NEW_SALES_RATIO`/`OLD_SALES_RATIO` columns, and committed + pushed. Repo output now matches
  its generator.
- [ ] **`scripts/openAvmKitInputFiles.py`** — separate Stage-0 converter, still has uncommitted
  WIP (~17-line diff, unrelated to this publish). Decide whether to review + commit.
- [ ] **AGENTS.md doc gotchas** — two verified notes (enrichment cache signs on inputs not code;
  ratio-study uses raw `sale_price` while VEI uses `dep_var`) are committed on the openavmkit
  `philly-patches-0.6.0` branch (`2b14007`). PR-able upstream — diff against upstream's AGENTS.md
  first. File or leave.

## Deliverable

- [ ] **LaTeX report** of the assessment-fairness analysis, analogous to Pro-Housing Pittsburgh's
  `drafts/2026-06-15 Allegheny_County_Reassessment.pdf`. Not started — first study the PDF's
  structure. Pull from the current results: 5-group ratio study (median ratio / COD vs county;
  county assesses at ~half of market), the VEI fix, and the equity findings (level equity passes
  across income AND racial composition; COD/uniformity gap in majority-minority older/urban tracts).
  Apply the global LaTeX preamble rules (see global CLAUDE.md). For a publication run, set
  `DO_SHAPS=True` in `run_03_model.py` (explainability / IAAO narrative — never for iteration).

## Modeling / analysis

- [ ] **Commercial group** — data-starved (~43 study-period sales; median ratio 1.84, COD 36).
  Decide: limited-engine model, keep-with-disclaimer (current), or exclude from published valuations.
  It is in `run_reensemble.py`'s `SKIP_GROUPS` (the trio blend doesn't suit it).
- [ ] **Horizontal-equity gap** — COD is ~1.4–1.7× worse in the lowest-income / highest-minority
  strata, systematically; prewar breaches IAAO ≤20 in majority-minority tracts (COD ~25–31).
  Level equity (median ratio) passes on both axes. Investigate/mitigate (likely sales sparsity +
  heterogeneous stock in those areas); disclose as a known limitation in the report regardless.
- [ ] **Deferred feature experiments** (each its own iteration, one change at a time):
  - `homestead_flag` / `abatement_flag` as predictors — **equity-sensitive** (owner-occupancy
    correlates with demographics); needs its own equity check.
  - `years_since_last_sale` / `pct_price_change_since_last_sale` — needs a Stage-0 change in
    `openAvmKitInputFiles.py` (derive from `PREVSALEPRICE`/`PREVSALEDATE`).
  - `ngboost` for per-parcel prediction intervals (adds ~30–45 min; not needed for metric/equity work).

## Future / migration

- [ ] **OpenAvmKit upgrade past v0.6.0** — upstream master already fixed the `ensemble.models` key
  and added an `ensemble.optimize` flag. On upgrade, the (currently inert) `settings.json`
  `ensemble.models=[mra,multi_mra,lightgbm]` pin activates and would force the trio onto **commercial**
  too — add a per-group ensemble override, and reassess `run_reensemble.py` (post-processing) vs.
  the native `ensemble.models` + `optimize` path. Clear `__pycache__` after any branch switch.

## Settled / not doing (don't re-raise)

- **Upstream PRs filed 2026-06-22:** clear_cache ([#364](https://github.com/larsiusprime/openavmkit/pull/364)),
  OSM rivers ([#365](https://github.com/larsiusprime/openavmkit/pull/365)),
  ratio_study binning+bins ([#366](https://github.com/larsiusprime/openavmkit/pull/366)).
- **Kept private (never public PR):** `vei_significance` fix, `census.py`/`data.py` pct_minority
  enrichment — equity/racial-composition material; Lars handles privately (#361/#362 were closed).
- **Bulk-deed contamination:** already excluded in Allegheny via `SALECODE` + `deed_id` — no action.
- **Ensemble `models`-key bug:** already fixed on upstream master — nothing to PR.
