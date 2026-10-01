import sys
sys.path.insert(0, "src")
from esbench import ragone, supercap, lcos, joint, hess

def test_ragone_ranges():
    df = ragone.dataframe()
    assert len(df) >= 10
    # LFP RTE representative 85% must be inside range
    lfp = df[df.name.str.contains("LFP")].iloc[0]
    assert lfp["rte_lo"] <= 85 <= lfp["rte_hi"]
    # H2 RTE low
    h2 = df[df.name.str.contains("Hydrogen")].iloc[0]
    assert h2["rte_hi"] <= 50

def test_supercap_book_example():
    # 170kJ/30kW 350F/2.5V/3.2mOhm @90% -> book N~270 d~0.61 within 20%
    r = supercap.size_bank(170e3, 30e3, 350.0, 2.5, 3.2e-3, 0.90)
    assert 200 <= r["N_star"] <= 340, r
    assert 0.5 <= r["d_star"] <= 0.8, r
    # efficiency must rise with N is implicit: power N at d=0.9 > at d=0.5? check monotonic energy
    # N_energy rises with d (denominator 1-d^2 shrinks), N_power falls with d (Vavg rises)
    assert r["n_energy"][0] < r["n_energy"][-1]
    assert r["n_power"][0] > r["n_power"][-1]

def test_lcos_drivers():
    low_rte = lcos.lcos_per_mwh(80, 120, 4, 0.6, 1500)
    high_rte = lcos.lcos_per_mwh(80, 120, 4, 0.9, 1500)
    assert high_rte < low_rte
    low_use = lcos.lcos_per_mwh(80, 120, 4, 0.85, 500)
    high_use = lcos.lcos_per_mwh(80, 120, 4, 0.85, 3000)
    assert high_use < low_use

def test_joint_peak_cut():
    load, reg = joint.synth_day()
    r = joint.dispatch(load, reg)
    assert r["peak_cut"] >= 0
    assert r["peak_before"] > 40

def test_hess_correlation():
    r = hess.evaluate(K=60)
    assert r["pearson"] > 0.5  # strong positive; literature ~0.9 on 1024 profiles
    assert r["max_saving"] > 0.05
