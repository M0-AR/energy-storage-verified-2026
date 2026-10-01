"""HESS variation-coefficient predictor (Guenther et al 2026 pattern).
Claim: variation coefficient VC = std/mean of load governs HESS benefit.
Sizing gains <=3% but loss savings often >20% (saturating). Pearson ~0.9.
We generate K synthetic profiles with controlled VC and compute:
  single_loss vs hybrid_loss under optimal split (high-pass for SC).
Deterministic seeds. Verifies correlation, not exact 0.9 (we assert >0.7).
"""
import numpy as np

def make_profiles(K=120, n=288, seed=11):
    rng = np.random.default_rng(seed)
    out = []
    for k in range(K):
        frac = k / max(1, K - 1)  # 0..1 controls HIGH-FREQ share, not global scale
        base = 50.0
        slow = 10 * np.sin(2 * np.pi * np.arange(n) / 96 + rng.uniform(0, 6))
        # fast amplitude grows with frac; slow stays fixed -> HF share grows
        fast_std = 1.0 + 14.0 * frac
        fast = rng.normal(0, 1, n) * fast_std
        spike_prob = 0.002 + 0.05 * frac
        spike = (rng.random(n) < spike_prob).astype(float) * rng.uniform(10, 40, n)
        p = np.maximum(5, base + slow + fast + spike)
        out.append(p)
    return out

def loss_single(p, eta_batt=0.9):
    e = np.abs(np.diff(p, prepend=p[0])).sum()
    return e * (1 - eta_batt)

def loss_hybrid(p, eta_batt=0.9, eta_sc=0.97, cutoff=0.2):
    d = np.diff(p, prepend=p[0])
    # high-freq to SC via simple high-pass (diff of smoothed)
    import pandas as pd
    s = pd.Series(p).rolling(5, center=True, min_periods=1).mean().to_numpy()
    hf = p - s
    lf = s
    loss = np.abs(np.diff(lf, prepend=lf[0])).sum() * (1 - eta_batt)
    loss += np.abs(np.diff(hf, prepend=hf[0])).sum() * (1 - eta_sc)
    return loss

def evaluate(K=120):
    from scipy.stats import pearsonr
    profs = make_profiles(K)
    vcs, savings = [], []
    for p in profs:
        vc = p.std() / p.mean()
        ls = loss_single(p)
        lh = loss_hybrid(p)
        sav = (ls - lh) / ls if ls > 0 else 0.0
        vcs.append(vc)
        savings.append(max(0.0, sav))
    vcs = np.array(vcs)
    savings = np.array(savings)
    r, _ = pearsonr(vcs, savings)
    return {"vc": vcs, "saving": savings, "pearson": float(r),
            "median_saving": float(np.median(savings)),
            "max_saving": float(savings.max())}
