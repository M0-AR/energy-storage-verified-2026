# REPRODUCIBILITY — zero to hero in 3 commands

1. `docker compose build bench`
2. `docker compose run --rm bench bash -c "pytest -q && python scripts/run_all.py --offline=0"`
3. `docker compose --profile live run --rm fetch-live` (needs net; else offline=1 uses synthetic)

Verified 2026-10-01: 5 passed; 6 experiments; 4/4 live 200 (open-meteo 1687 B, atb_data 34520 B, atb_bess 49427 B, pnnl 79990 B).
Figures: ragone, supercap_locus, lcos, joint_load, hess, pv_solar. Tables: ragone, supercap_locus, lcos_sweep, hess. Processed: joint_day, pv_grenoble.
Offline Docker run reproduces all except live solar text (falls back, same RTE 0.90).
No secrets, no keys, no private data. Public sources only, snapshots under data/raw.
