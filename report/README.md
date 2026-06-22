# AGC Reassessment Report

LaTeX report of the Allegheny County automated-valuation analysis, modeled on
Pro-Housing Pittsburgh's June 2026 reassessment report and extended with equity
testing.

**No numbers are hand-written in `report.tex`.** Every figure, table, and inline
statistic is generated from the pipeline outputs and pulled in via `\input`.

## Build

```bash
# 1. Generate the data fragments (macros + tables) from the model outputs.
#    Reads the ratio-study reports, ensemble pickles, published CSVs, and the
#    100-parcel data-quality sanity-check CSV.
python build_report.py            # -> generated/macros.tex, results_table.tex,
                                  #    equity_*.tex, audit_table.tex, coef_tables.tex

# 2. Generate the figures into figures/ (census-tract choropleths from the
#    ensemble pickles + land CSV; valuation-ratio-by-district maps and ranked
#    bar charts from the published district CSVs). Until this is run, report.tex
#    shows labeled placeholder boxes instead.
python build_figures.py           # -> figures/*.png (sales-ratio, land, valuation
                                  #    ratio, + 4 district views)

# 3. Compile.
pdflatex report && bibtex report && pdflatex report && pdflatex report
```

## Layout

- `report.tex` — the document (prose + structure; no hardcoded numbers)
- `build_report.py` — generates `generated/*.tex` (macros + tables) from pipeline outputs
- `build_figures.py` — generates `figures/*.png` (choropleth maps) from pipeline outputs
- `references.bib` — bibliography
- `generated/` — build output (gitignored; regenerate with `build_report.py`)
- `figures/` — choropleth PNGs (gitignored; regenerate with `build_figures.py`)
