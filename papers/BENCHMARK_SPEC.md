# BENCHMARK SPEC — pass/fail gates (v0.1)

- Ragone: ≥10 techs; LFP contains RTE 85%; H₂ hi ≤50%.
- Supercap book: N* 200–340, d* 0.5–0.8; N_energy ↑ with d, N_power ↓ with d.
- LCOS: higher RTE → lower LCOS; higher FLH → lower LCOS.
- Joint: peak_cut ≥0; peak_before >40; reg_served >0.
- HESS: Pearson >0.5 (lit 0.9 full); max_saving >0.05.
- PV live: stock-corrected RTE in [0.8,1.0] when e_ch≥0.5; else deficit reported, not hidden.
- Live: provenance JSON with 4 URLs, UTC, sha256; no hard fail offline.

Future gates: field BESS series, 1024 profiles, price-based joint arbitrage, 24/100 h LCOS.
