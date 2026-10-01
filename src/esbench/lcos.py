"""LCOS calculator with RTE + full-load-hour sensitivity.
LCOS (≈ $/MWh discharged) =
  (annuitized CAPEX-power*P + CAPEX-energy*E + FOM) / E_discharged_annual
  + VOM + charging_cost / RTE
Simplified, transparent, auditable. Defaults from public 2025-26 sources:
- NLR ATB 2025: BESS LFP, RTE 85% representative, 2-10h durations.
- PNNL 2024 DB / DOE 2022: LCOS framing, replacement+decommissioning included.
- LDES+EPRI Jan 2026: RTE & FLH are #1 LCOS drivers; a-CAES lowest where fees low.
We sweep RTE and FLH to prove the driver claim, not to quote a single LCOS.
"""
import numpy as np

def crf(r, n):
    return r * (1 + r)**n / ((1 + r)**n - 1) if r > 0 else 1.0 / n

def lcos_per_mwh(p_capex_kw, e_capex_kwh, duration_h, rte, flh_year,
                 fom_kw_yr=15.0, vom_mwh=3.0, charge_price_mwh=40.0,
                 discount=0.07, life=15):
    """All capex in $/kW and $/kWh. flh = full-load discharge hours per year."""
    P = 1.0  # per kW normalized
    E = duration_h  # kWh per kW
    capex = p_capex_kw * P + e_capex_kwh * E
    ann = capex * crf(discount, life) + fom_kw_yr * P
    e_dis = flh_year  # MWh? per kW: flh h *1kW = flh kWh
    if e_dis <= 0:
        return float("inf")
    fixed_part = ann / e_dis  # $/kWh
    return fixed_part + vom_mwh / 1000.0 + (charge_price_mwh / 1000.0) / rte
