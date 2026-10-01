"""Ragone + techno-economic table.
Sources (verified 2026-10-01):
- Brunet (2011) Ch 2/8/9: lead 30-50 Wh/kg, Ni-Cd 45-80, Ni-MH 60-120,
  Li-ion 100-200 Wh/kg, Zebra 120 Wh/kg.
- MDPI Sustainability 2026 review: Li-ion RTE 70-95%, PHES robust long-duration,
  power-to-H2 long duration but low RTE + complexity.
- NREL/NLR ATB 2025: utility BESS = LFP, RTE representative 85% (Cole et al 2025).
- DOE ESGC 2022 Cost & Performance Assessment: LCOS (not LCOE), adds Zn/thermal/
  gravitational, 2-10h + 24h/100h for Long-Duration Shot.
- LDES Council+EPRI Jan 2026: 5 groups (intraday electrochemical/compressed-gas/
  pumped-heat, multi-day 100h+, thermal P2H); RTE + annual full-load hours drive LCOS;
  a-CAES lowest LCOS in low-fee regions; PHES most expensive in that study frame.
- Open-research 2026: Li-ion BESS 85-90% RTE; hybrid CAES-PHES 92% lab;
  Li-ion 85-95%, PHES 75-85%, CAES 50-70%, H2 30-45%.
All numbers are ranges (not point claims) with provenance.
"""
from dataclasses import dataclass
import pandas as pd

@dataclass
class Tech:
    name: str
    wh_per_kg_lo: float
    wh_per_kg_hi: float
    rte_lo: float
    rte_hi: float
    life_note: str
    maturity: str
    source: str

TABLE = [
    Tech("Lead-acid", 30, 50, 70, 85, "400-1200 cycles @80% DOD; -20..60C", "mature", "Brunet Ch8 Tab8.1 + MDPI2026"),
    Tech("Ni-Cd", 45, 80, 65, 75, "~2000 cycles; memory effect; Cd toxicity", "mature-declining", "Brunet Ch8"),
    Tech("Ni-MH", 60, 120, 65, 75, "~1500 cycles; low memory vs Ni-Cd", "mature", "Brunet Ch8"),
    Tech("Li-ion LFP (BESS)", 90, 160, 85, 95, "3000-6000 cycles; ATB RTE 85% rep.", "dominant 2025-26", "NLR ATB2025; MDPI2026; PNNL"),
    Tech("Li-ion NMC", 150, 250, 85, 95, "1000-3000 cycles; higher energy, Ni/Co risk", "dominant EV", "MDPI2026; WikiBattery 2026"),
    Tech("Sodium-ion", 75, 160, 80, 90, "early commercial; crossover w/ LFP 2028-29", "early-commercial", "free-search 2026 survey; SciDirect 2025"),
    Tech("Vanadium redox-flow", 15, 35, 65, 85, ">10k cycles; decoupled E/P; low density", "commercial niche", "DOE 2022; LDES2026 intraday-electrochem"),
    Tech("Supercapacitor (EDLC)", 4, 10, 90, 98, "1e5-1e6 cycles; 2.5-3V/cell; high self-discharge", "commercial power", "Brunet Ch9; Simon+Gogotsi"),
    Tech("Flywheel", 5, 50, 85, 95, "high power, short duration; low maintenance", "commercial niche", "MDPI2026 hybrid HESS"),
    Tech("Pumped hydro (PHES)", 0.5, 1.5, 70, 85, "30-60y; site-constrained; most robust LD", "mature LD", "MDPI2026; DOE2022"),
    Tech("CAES diabatic", 3, 6, 45, 60, "Huntorf/McIntosh; fuel + air", "commercial (2 sites+Jintan)", "howtostoreelectricity 2026"),
    Tech("CAES adiabatic (a-CAES)", 3, 8, 60, 72, "Hydrostor/ALACAES; heat store; lowest LCOS low-fee", "demo-early commercial", "LDES2026; SciDirect2026"),
    Tech("Hydrogen power-to-power", 300, 800, 30, 45, "tank 350-700bar or liquid -253C; 9-13% compress, 30-40% liquefy", "demo + infra", "DOE H2 prog; Brunet Ch5; Fruchard"),
    Tech("Thermal (sensible/PCM P2H)", 20, 150, 40, 70, "power-to-heat; $/kWh-th low", "commercial (heat)", "LDES2026 thermal group"),
]

def dataframe() -> pd.DataFrame:
    return pd.DataFrame([t.__dict__ for t in TABLE])

def hidden_pattern_note() -> str:
    return (
        "Hidden pattern (verified): no single winner. RTE ranking (SC>Li-ion/flywheel>"
        "PHES>flow>CAES>thermal>H2) inverts for long-duration value where energy-capex "
        "and full-load hours dominate. LDES 2026: RTE+FLHt are top LCOS drivers; "
        "100MW/40h LDES may discharge handful times/year — LCOS then misleads, "
        "capacity value matters (Brunet Ch1 'flexibility' thesis)."
    )
