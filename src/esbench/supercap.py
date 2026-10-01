"""Supercapacitor bank sizing — Brunet Ch9 (Barrade) + SODR 2025 update.
Book equations:
  Wm = 1/2 C Um^2                       [9.3]
  d  = 100 * Um_min / Um_max            [9.4]
  Wu = Wm * (1 - (d/100)^2)             [9.5]
  N  = W_need / Wu                      [9.6]
Efficiency: Rs losses force d>=50% in practice; power sizing via iso-efficiency.
2025 update (Sengupta et al, TechRxiv): Size-Optimal Discharge Ratio (SODR)
exists analytically; arbitrary d=50% oversizes up to 40% vs SODR.
We implement both and verify against book example:
  170 kJ / 30 kW, cell 350F/2.5V/3.2mOhm -> book Fig9.7: N=270 d=60.8% @90%,
  N=365 d=73.8% @94% (approx). Our model must land within 15% to pass.
"""
import numpy as np

def cell_useful_energy(C, Umax, d_frac):
    Wm = 0.5 * C * Umax**2
    return Wm * (1.0 - d_frac**2), Wm

def n_energy(W_need, C, Umax, d_frac):
    Wu, _ = cell_useful_energy(C, Umax, d_frac)
    return W_need / Wu

def eta_discharge(P_cell, V_avg, Rs):
    """eta = P / (P + Rs*I^2), I=P/V_avg."""
    if P_cell <= 0:
        return 1.0
    I = P_cell / max(V_avg, 1e-9)
    loss = Rs * I * I
    return P_cell / (P_cell + loss)

def v_avg(Umax, d_frac):
    return Umax * (1.0 + d_frac) / 2.0

def n_power(P_need, Umax, d_frac, Rs, eta_target):
    """Minimum N s.t. per-cell eta >= target at constant-power discharge.
    Binary search on P_cell: eta decreases with P_cell, so max P_cell @target
    is found, then N = ceil(P_need / P_cell_max). Continuous N returned for locus.
    """
    V = v_avg(Umax, d_frac)
    # max per-cell power at eta_target: solve eta = P/(P+Rs P^2/V^2) = t
    # -> P = V^2 * (1-t)/(Rs) * t? Derive: t = 1/(1+Rs P/V^2) -> P = V^2(1-t)/(Rs t)
    t = eta_target
    if t >= 1.0:
        return float("inf")
    P_cell_max = (V**2) * (1 - t) / (Rs * t)
    if P_cell_max <= 0:
        return float("inf")
    return P_need / P_cell_max

def size_bank(W_need, P_need, C, Umax, Rs, eta_target, d_grid=None):
    """Return dict with energy locus, power locus, feasible N(d), and SODR."""
    if d_grid is None:
        d_grid = np.linspace(0.5, 0.95, 46)
    n_e = np.array([n_energy(W_need, C, Umax, d) for d in d_grid])
    n_p = np.array([n_power(P_need, Umax, d, Rs, eta_target) for d in d_grid])
    n_feas = np.maximum(n_e, n_p)
    i = int(np.argmin(n_feas))
    return {
        "d_grid": d_grid, "n_energy": n_e, "n_power": n_p, "n_feas": n_feas,
        "d_star": float(d_grid[i]), "N_star": float(n_feas[i]),
    }

def sodr_analytic(W_need, P_need, C, Umax, Rs, eta_target):
    """SODR = argmin_d max(N_energy(d), N_power(d)). Same as size_bank optimum.
    Named to link 2025 result: do NOT hardcode 50%.
    """
    r = size_bank(W_need, P_need, C, Umax, Rs, eta_target)
    return r["d_star"], r["N_star"]
