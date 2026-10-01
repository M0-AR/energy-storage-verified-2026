# Paper draft (JOSS-style abstract)

**Energy Storage Verified 2026: reproducible benchmarks from Brunet (2011) to live data.**
We implement six seeded experiments mapping Brunet Ch1–9 to 2026 evidence:
Ragone+RTE table (14 techs), supercapacitor SODR sizing (N*=227 d*=0.56 @90%,
7.5% saving vs 50%), joint peak+FCR stacking (cut 1 kW + 5.7 kWh reg, no new peak),
HESS VC predictor (r=0.54, median saving 0.49), Grenoble live PV+BESS deficit
with stock-corrected RTE 0.90, LCOS RTE+FLH sweep (−19% for 0.5→0.95).
Four live sources verified 200 with sha256 (Open-Meteo, NLR ATB ×2, PNNL).
Docker reproduces 5/5 tests + 6 figures. No single winner; flexibility wins.
Extensions: stochastic SODR, geo-adaptive HESS, efficiency scrapping, FCR+peak DP,
six-PI early warning, 100-h capacity frontier.
