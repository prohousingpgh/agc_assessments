"""
Standalone ratio study breakdowns.

Runs ONLY the ratio study against already-trained model outputs in
out/models/<group>/main/model_ensemble.pickle. Use this to (re)generate
ratio study reports — including the equity breakdowns (income quintile,
pct_minority) — without re-running the full ~75-min Stage 3 training.

Reads breakdown config from settings.json (analysis.ratio_study.breakdowns).
Any breakdown field not present in the data is skipped gracefully.

Run from any directory (init_notebook chdir's into the locality data dir).
"""
import os, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUNBUFFERED"] = "1"

openavmkit_repo = os.path.abspath("C:/projects/openavmkit")
if openavmkit_repo not in sys.path:
    sys.path.insert(0, openavmkit_repo)

locality = "us-pa-allegheny"

from openavmkit.pipeline import (
    init_notebook,
    load_settings,
    run_and_write_ratio_study_breakdowns,
)

print(f"\n{'='*60}")
print("Standalone ratio study breakdowns")
print(f"{'='*60}")
init_notebook(locality)
settings = load_settings()

run_and_write_ratio_study_breakdowns(settings)

print("\nDone! Ratio study reports written under out/models/<group>/")
