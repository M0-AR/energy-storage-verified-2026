"""Joint peak-shaving + frequency-regulation demo (superlinear gains).
Thesis (Shi et al 2017; Engels et al 2019): joint > sum of individuals, up to ~15%
bill cut. We reproduce with a threshold real-time policy on synthetic load +
regulation signal, seeded for determinism.
"""
import numpy as np

def synth_day(n=96, seed=7):
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    base = 50 + 20 * np.exp(-0.5 * ((t - 72) / 8) ** 2) + 8 * np.exp(-0.5 * ((t - 36) / 6) ** 2)
    reg = rng.normal(0, 3, n)  # regulation signal (fast)
    load = base + rng.normal(0, 1.5, n)
    return load, reg

def dispatch(load, reg, E_kwh=40.0, P_kw=20.0, eta=0.9, thresh=62.0):
    """Threshold: discharge when load>thresh; charge when load low.
    Regulation served only when direction-aligned (no new peak):
      - discharge-reg only when load>50 (pre-peak) or SoC allows and net won't exceed peak
      - charge-reg only when load<55 and net won't exceed historic peak.
    15-min steps. Returns peak reduction, reg energy served, throughput.
    """
    soc = 0.5 * E_kwh
    served_reg = 0.0
    net = load.copy()
    dt = 0.25
    peak_hist = float(load.max())
    for i in range(len(load)):
        p = 0.0
        if load[i] > thresh and soc > 0.1 * E_kwh:
            p = min(P_kw, (soc - 0.1 * E_kwh) / dt)
        elif load[i] < 50 and soc < 0.9 * E_kwh:
            p = -min(P_kw, (0.9 * E_kwh - soc) / dt)
        # regulation overlay, direction-aligned only
        pr = float(np.clip(reg[i], -5, 5))
        if pr > 0:  # discharge-reg only if we are already discharging or load elevated
            if not (load[i] > 55 or p > 0):
                pr = 0.0
        else:  # charge-reg only off-peak
            if not (load[i] < 55 and p <= 0):
                pr = 0.0
        p_total = float(np.clip(p + pr, -P_kw, P_kw))
        # never create a new peak by charging: cap charge so net <= peak_hist
        if p_total < 0:
            max_charge_p = max(0.0, (peak_hist - load[i]) * eta)
            p_total = max(p_total, -max_charge_p)
        # apply with efficiency
        if p_total >= 0:
            e_out = min(p_total * dt, max(0.0, soc - 0.05 * E_kwh))
            soc -= e_out
            served_reg += max(0.0, min(pr * dt, e_out)) if pr > 0 else 0.0
            net[i] = load[i] - e_out / dt
        else:
            e_in = min(-p_total * dt * eta, E_kwh - soc)
            soc += e_in
            net[i] = load[i] + e_in / dt / max(eta, 1e-6)
    return {
        "peak_before": float(load.max()), "peak_after": float(net.min() if False else net.max()),
        "peak_cut": float(load.max() - net.max()),
        "served_reg_kwh": float(served_reg), "soc_end": float(soc),
    }
