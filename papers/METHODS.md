# METHODS — what we ran, seeded, and logged

## Book equations (Barrade Ch9)
Wm=1/2·C·Um²; d=100·Um_min/Um_max; Wu=Wm·(1−(d/100)²); N=W/Wu.
Power: Vavg=Um(1+d)/2; η=P/(P+Rs·(P/Vavg)²); P_cell_max=Vavg²(1−η)/(Rs·η); N_power=P/P_cell_max.
Feasible N(d)=max(N_energy,N_power); SODR=argmin N(d).

## LCOS proxy
CRF=r(1+r)ⁿ/((1+r)ⁿ−1); LCOS=(CAPEX·CRF+FOM)/FLH+VOM+charge/RTE.
Defaults: p_capex $80/kW, e_capex $120/kWh, 4h, FOM $15/kW-yr, charge $40/MWh, r7% n15y.
Sweep RTE 0.5–0.95, FLH 500/1500/3000 — proves drivers, not a quote.

## Joint dispatch
96×15-min synthetic day (seed 7): evening peak + morning hump + N(0,1.5) + reg N(0,3).
Threshold + direction-aligned reg + peak_hist cap. Reports peak cut + reg served.

## HESS VC
K=120 profiles (seed 11): slow sine fixed, fast std 1→15·frac, spikes 0.002→0.05.
Loss single=|Δp|·(1−0.9); hybrid splits via rolling-5 high-pass, SC η0.97.
Pearson VC-vs-saving; median/max saving.

## PV+BESS PIs
Live Grenoble GHI (Open-Meteo) ×2.5 kWp, load 0.4+0.3sin², BESS 5 kWh/2 kW η0.9.
Terminal bookkeeping (charge terminal=e/η) + stock-corrected RTE=e_dis/(e_ch+drift⁺/η).
Balanced-sun control (900 W/m² bell) validates 0.900=η. Six PIs via pvbess.compute_pi.

## Live fetch
requests GET ×4 with UA esbench/0.1, 20 s timeout; records status/bytes/sha256/UTC/snippet.
Never fails hard; offline fallback synthetic. Provenance in data/raw/live_provenance.json.
Seeds fixed; matplotlib Agg; pytest 5 tests gate merges.
