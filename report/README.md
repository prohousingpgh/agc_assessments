# AGC Reassessment Report

LaTeX report of the Allegheny County automated-valuation analysis, modeled on
Pro-Housing Pittsburgh's June 2026 reassessment report and extended with equity
testing.

**No numbers are hand-written in `report.tex`.** Every figure, table, and inline
statistic is generated from the pipeline outputs and pulled in via `\input`.

## Build

```bash
# 1. Generate the data fragments (macros + tables) from the model outputs.
#    Reads the ratio-study reports, ensemble pickles, and published CSVs.
python build_report.py            # -> generated/macros.tex, results_table.tex, equity_*.tex

# 2. (optional) Generate the choropleth maps and copy them into figures/.
#    The pipeline's make_maps.py writes PNGs to out/maps/; copy the ones the
#    report references (median_sales_ratio_*, land_value_*, valuation_ratio_*)
#    into report/figures/. Until then report.tex shows placeholder boxes.

# 3. Compile.
pdflatex report && bibtex report && pdflatex report && pdflatex report
```

## Layout

- `report.tex` — the document (prose + structure; no hardcoded numbers)
- `build_report.py` — generates `generated/*.tex` from pipeline outputs
- `references.bib` — bibliography
- `generated/` — build output (gitignored; regenerate with `build_report.py`)
- `figures/` — choropleth PNGs from `make_maps.py` (gitignored)
