"""Run all experiments end-to-end, offline-capable."""
import argparse, os, sys
sys.path.insert(0, "src")
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from esbench import ragone, supercap, lcos, joint, hess, pvbess

os.makedirs("results/figures", exist_ok=True)
os.makedirs("results/tables", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

def exp_ragone():
    df = ragone.dataframe()
    df.to_csv("results/tables/ragone.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(df))
    x = (df["wh_per_kg_lo"] + df["wh_per_kg_hi"]) / 2
    xerr = [(df["wh_per_kg_hi"] - df["wh_per_kg_lo"]) / 2]
    # log-x Ragone-style (energy) with RTE as color
    rte_mid = (df["rte_lo"] + df["rte_hi"]) / 2
    sc = ax.scatter(x, rte_mid, s=90)
    for i, n in enumerate(df["name"]):
        ax.text(x.iloc[i] * 1.05, rte_mid.iloc[i], n, fontsize=7)
    ax.set_xscale("log")
    ax.set_xlabel("Specific energy mid-point (Wh/kg, log)")
    ax.set_ylabel("Round-trip efficiency mid-point (%)")
    ax.set_title("Ragone-style map: energy vs efficiency (ranges in ragone.csv)")
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig("results/figures/ragone.png", dpi=150)
    print(f"[01] ragone rows={len(df)} -> results/tables/ragone.csv")
    print("     " + ragone.hidden_pattern_note()[:120] + "...")

def exp_supercap():
    W, P, C, U, Rs = 170e3, 30e3, 350.0, 2.5, 3.2e-3
    for eta in (0.90, 0.92, 0.94):
        r = supercap.size_bank(W, P, C, U, Rs, eta)
        print(f"[02] eta={eta:.2f} -> d*={r['d_star']:.3f} N*={r['N_star']:.1f}")
    # locus plot at 90%
    r90 = supercap.size_bank(W, P, C, U, Rs, 0.90)
    d = r90["d_grid"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(d, r90["n_energy"], label="N energy (170 kJ)")
    ax.plot(d, r90["n_power"], label="N power (30 kW @90%)")
    ax.plot(d, r90["n_feas"], label="N feasible = max", linewidth=2)
    ax.set_xlabel("discharge factor d = Umin/Umax")
    ax.set_ylabel("cells N (350F/2.5V)")
    ax.set_title("Supercap sizing locus (Brunet Fig 9.7 reproduction)")
    ax.legend(); ax.grid(True, alpha=0.3)
    fig.tight_layout(); fig.savefig("results/figures/supercap_locus.png", dpi=150)
    # SODR check
    d_star, N_star = supercap.sodr_analytic(W, P, C, U, Rs, 0.90)
    n_arbitrary = supercap.n_energy(W, C, U, 0.50)
    # power at d=0.5 for 90%
    n_p05 = supercap.n_power(P, U, 0.50, Rs, 0.90)
    n_arb = max(n_arbitrary, n_p05)
    saving = 100 * (n_arb - N_star) / n_arb
    print(f"[02] SODR d*={d_star:.3f} N*={N_star:.1f} vs arbitrary d=0.5 N={n_arb:.1f} saving={saving:.1f}%")
    pd.DataFrame({"d": d, "N_energy": r90["n_energy"], "N_power": r90["n_power"], "N_feas": r90["n_feas"]}).to_csv("results/tables/supercap_locus.csv", index=False)

def exp_lcos():
    import numpy as np
    rtes = np.linspace(0.5, 0.95, 10)
    flhs = [500, 1500, 3000]
    rows = []
    for flh in flhs:
        for rte in rtes:
            v = lcos.lcos_per_mwh(80, 120, 4, rte, flh)
            rows.append({"FLH": flh, "RTE": round(float(rte), 3), "LCOS_$per_kWh": round(float(v), 4)})
    df = pd.DataFrame(rows)
    df.to_csv("results/tables/lcos_sweep.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    for flh in flhs:
        sub = df[df.FLH == flh]
        ax.plot(sub["RTE"], sub["LCOS_$per_kWh"], marker="o", label=f"FLH={flh}h/yr")
    ax.set_xlabel("round-trip efficiency"); ax.set_ylabel("LCOS proxy ($/kWh discharged)")
    ax.set_title("LCOS sensitivity: RTE + utilisation drive cost (LDES 2026)")
    ax.legend(); ax.grid(True, alpha=0.3)
    fig.tight_layout(); fig.savefig("results/figures/lcos.png", dpi=150)
    lo = df[df.RTE == 0.5].iloc[0]["LCOS_$per_kWh"]; hi = df[df.RTE == 0.95].iloc[0]["LCOS_$per_kWh"]
    print(f"[06] lcos rows={len(df)} RTE 0.5->0.95 cuts LCOS ~{(lo/hi-1)*100:.0f}% (illustrative)")

def exp_joint():
    load, reg = joint.synth_day()
    r = joint.dispatch(load, reg)
    print(f"[03] joint peak {r['peak_before']:.1f}->{r['peak_after']:.1f} kW cut={r['peak_cut']:.1f} reg_served={r['served_reg_kwh']:.1f} kWh")
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(load, label="load before"); ax.set_title("Synthetic day load (peak-shave + FCR demo)")
    ax.set_xlabel("15-min step"); ax.set_ylabel("kW"); ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig("results/figures/joint_load.png", dpi=150)
    pd.DataFrame({"load": load, "reg": reg}).to_csv("data/processed/joint_day.csv", index=False)

def exp_hess():
    r = hess.evaluate(K=120)
    print(f"[04] hess Pearson VC-vs-saving r={r['pearson']:.3f} median={r['median_saving']:.3f} max={r['max_saving']:.3f}")
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(r["vc"], r["saving"], s=12)
    ax.set_xlabel("variation coefficient std/mean"); ax.set_ylabel("hybrid loss saving fraction")
    ax.set_title(f"HESS: VC predicts saving (r={r['pearson']:.2f})")
    ax.grid(alpha=0.3); fig.tight_layout(); fig.savefig("results/figures/hess.png", dpi=150)
    pd.DataFrame({"vc": r["vc"], "saving": r["saving"]}).to_csv("results/tables/hess.csv", index=False)

def exp_pv_live(offline=0):
    # Live Grenoble solar if available, else synthetic bell
    import json, requests
    ghi = None
    try:
        if not offline and os.path.exists("data/raw/open_meteo_grenoble.json"):
            j = json.load(open("data/raw/open_meteo_grenoble.json"))
            ghi = np.array(j["hourly"]["shortwave_radiation"][:48], dtype=float)
            print(f"[05] pv live solar from vendored open-meteo n={len(ghi)}")
        elif not offline:
            u = "https://api.open-meteo.com/v1/forecast?latitude=45.18&longitude=5.72&hourly=shortwave_radiation&forecast_days=2&timezone=UTC"
            j = requests.get(u, timeout=20).json()
            ghi = np.array(j["hourly"]["shortwave_radiation"][:48], dtype=float)
            print(f"[05] pv LIVE open-meteo n={len(ghi)} mean={ghi.mean():.1f} W/m2")
        else:
            raise RuntimeError("offline")
    except Exception as e:
        t = np.arange(48)
        ghi = np.maximum(0, 800 * np.sin(np.pi * (t % 24 - 6) / 12))
        print(f"[05] pv fallback synthetic solar ({e})"[:120])
    # 2.5 kWp -> kW ~ GHI/1000 * 0.85 * 2.5; simple BESS 5kWh/2kW self-consumption
    # Scaled to ensure Oct Grenoble yields full charge/discharge cycles for PI demo
    pv = ghi / 1000 * 0.85 * 2.5
    load = 0.4 + 0.3 * np.sin(2 * np.pi * np.arange(48) / 24 - 1.0) ** 2
    load = np.maximum(0.15, load)
    E, P, eta, soc = 5.0, 2.0, 0.9, [2.5]
    p_hist, soc_hist = [], [2.5]
    dt = 1.0
    for i in range(48):
        net = pv[i] - load[i]
        p = float(np.clip(net, -P, P))
        if p >= 0:  # charge: terminal -> stored*eta; curtail if full
            e = min(p * dt * eta, E - soc_hist[-1]); soc_hist.append(soc_hist[-1] + e); p_hist.append(e / eta / dt if eta > 0 else 0.0)
        else:
            e = min(-p * dt, soc_hist[-1] - 0.2); soc_hist.append(soc_hist[-1] - e); p_hist.append(-e / dt)
    soc_hist = np.array(soc_hist[1:]); p_hist = np.array(p_hist)
    # compute_pi convention: discharge + / charge - . Our p_hist is charge + / discharge -.
    # Correct for stock drift: RTE_balanced = e_dis_term / (e_ch_term + max(0,soc0-soc1)/eta-ish)
    # If window is deficit (Oct Grenoble load>PV), RTE undefined -> report deficit honestly.
    import math
    p_term = -p_hist  # discharge +
    e_ch = float(np.sum(np.clip(p_term, -1e9, 0)) * -1.0)
    e_dis = float(np.sum(np.clip(p_term, 0, 1e9)))
    soc0, soc1 = 2.5, float(soc_hist[-1])
    drift = soc0 - soc1  # positive = stock consumed
    # stock-corrected RTE: terminal out / (terminal in + stock cost). Stock cost = drift/eta.
    if e_ch < 0.5:
        rte_note = f"deficit window (e_ch={e_ch:.2f}, e_dis={e_dis:.2f}, stock_used={drift:.2f}); RTE n/a - needs autonomy sizing (Brunet Ch3)"
        rte_rep = float("nan")
    else:
        denom = e_ch + max(0.0, drift) / max(1e-9, eta)
        rte_rep = e_dis / max(1e-9, denom)
        rte_note = f"stock-corrected (drift={drift:.2f})"
    pi = pvbess.compute_pi(np.arange(48, dtype=float), p_term, soc_hist, E_nom=E, P_nom=P)
    print(f"[05] pv pi cap={pi['capacity_kwh']:.2f}kWh standby={pi['standby_kw']:.3f}kW e_ch={e_ch:.2f} e_dis={e_dis:.2f} RTE_rep={rte_rep} [{rte_note}]")
    # Balanced synthetic control for PI validation (full sun day, RTE~eta)
    t2 = np.arange(48); ghi2 = np.maximum(0, 900 * np.sin(np.pi * (t2 % 24 - 6) / 12))
    pv2 = ghi2 / 1000 * 0.85 * 2.5
    socB, pB = [2.5], []
    for i in range(48):
        net2 = pv2[i] - load[i]
        p2 = float(np.clip(net2, -P, P))
        if p2 >= 0:
            e2 = min(p2 * 1.0 * eta, E - socB[-1]); socB.append(socB[-1] + e2); pB.append(e2 / eta if eta > 0 else 0.0)
        else:
            e2 = min(-p2 * 1.0, socB[-1] - 0.2); socB.append(socB[-1] - e2); pB.append(-e2)
    socB = np.array(socB[1:]); pB = np.array(pB)
    pB_term = -np.array(pB)
    e_chB = float(np.sum(np.clip(pB_term, -1e9, 0)) * -1.0); e_disB = float(np.sum(np.clip(pB_term, 0, 1e9)))
    driftB = 2.5 - float(socB[-1])
    rteB_corr = e_disB / max(1e-9, e_chB + max(0.0, driftB) / max(1e-9, eta))
    piB = pvbess.compute_pi(np.arange(48, dtype=float), -np.array(pB), socB, E_nom=E, P_nom=P)
    print(f"[05b] balanced-sun control RTE_stockcorr={rteB_corr:.3f} cap={piB['capacity_kwh']:.2f} (expects ~{eta})")
    pd.DataFrame({"ghi": ghi, "pv_kw": pv, "load_kw": load, "p_batt": p_hist, "soc": soc_hist}).to_csv("data/processed/pv_grenoble.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(ghi, label="GHI W/m2"); ax.plot(pv * 400, label="PV x400"); ax.legend(); ax.grid(alpha=0.3)
    ax.set_title("Grenoble live/fallback solar (Open-Meteo)"); fig.tight_layout()
    fig.savefig("results/figures/pv_solar.png", dpi=150)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", default="0")
    a = ap.parse_args()
    off = str(a.offline) == "1"
    exp_ragone(); exp_supercap(); exp_lcos(); exp_joint(); exp_hess(); exp_pv_live(offline=off)
    print("ALL EXPERIMENTS DONE. See results/figures + results/tables + data/processed.")

if __name__ == "__main__":
    main()
