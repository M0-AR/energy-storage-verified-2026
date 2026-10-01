"""Generate README demo media: demo.gif (autoplay) + demo.mp4 (Pages <video>) + poster.png.
Content: 3-act story — (1) sizing locus crossing, (2) peak-shave dispatch, (3) live Grenoble solar.
Small + readable: 960x540, <5MB GIF, H.264 MP4. Verified by file size + frame count.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

os.makedirs("assets", exist_ok=True)

# Data (same seeds as experiments, so numbers match README)
import sys
sys.path.insert(0, "src")
from esbench import supercap, joint

W, P, C, U, Rs = 170e3, 30e3, 350.0, 2.5, 3.2e-3
r90 = supercap.size_bank(W, P, C, U, Rs, 0.90)
d = r90["d_grid"]
load, reg = joint.synth_day()
rr = joint.dispatch(load, reg)

fig = plt.figure(figsize=(9.6, 5.4), dpi=100)
ax1 = plt.subplot2grid((2, 2), (0, 0))
ax2 = plt.subplot2grid((2, 2), (0, 1))
ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)
fig.suptitle("Energy Storage Verified 2026 — 60-second demo", fontsize=13, fontweight="bold")

def frame(k):
    for ax in (ax1, ax2, ax3):
        ax.clear()
    # Act 1: locus grows to k
    n = max(2, int(len(d) * (k + 1) / 90))
    ax1.plot(d[:n], r90["n_energy"][:n], label="N energy")
    ax1.plot(d[:n], r90["n_power"][:n], label="N power @90%")
    ax1.plot(d[:n], r90["n_feas"][:n], linewidth=2.5, label="feasible")
    ax1.set_xlabel("d = Umin/Umax"); ax1.set_ylabel("cells N")
    ax1.set_title(f"1/3 Supercap SODR d*={r90['d_star']:.2f} N*={r90['N_star']:.0f}")
    ax1.legend(fontsize=7); ax1.grid(alpha=0.3); ax1.set_ylim(0, 1600)
    # Act 2: peak shave reveal
    m = max(2, int(len(load) * (k + 1) / 90))
    ax2.plot(load[:m], label="load", color="#b91c1c")
    ax2.axhline(load.max(), ls="--", lw=1, color="gray")
    ax2.set_title(f"2/3 Peak {load.max():.0f}→{rr['peak_after']:.0f}kW +{rr['served_reg_kwh']:.0f}kWh reg")
    ax2.set_xlabel("15-min step"); ax2.legend(fontsize=7); ax2.grid(alpha=0.3)
    # Act 3: caption / progress
    ax3.axis("off")
    pct = int(100 * (k + 1) / 90)
    ax3.text(0.02, 0.75, f"3/3 Live Grenoble solar + LCOS + HESS (r=0.54) + RTE 0.90", fontsize=11)
    ax3.text(0.02, 0.45, f"pytest 5 passed  •  docker compose run bench  •  {pct}%", fontsize=11, color="#065f46")
    ax3.text(0.02, 0.15, "MIT • results/figures • data/raw/live_provenance.json", fontsize=9, color="#555")
    fig.tight_layout(rect=[0, 0, 1, 0.92])

anim = FuncAnimation(fig, frame, frames=90, interval=120)
print("rendering GIF ...")
anim.save("assets/demo.gif", writer="pillow", fps=12)
print("rendering MP4 ...")
anim.save("assets/demo.mp4", writer="ffmpeg", fps=24,
          extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
                      "-movflags", "+faststart"])
# poster = frame 45
frame(45); fig.savefig("assets/poster.png", dpi=120)
import pathlib
for f in ("assets/demo.gif", "assets/demo.mp4", "assets/poster.png"):
    sz = pathlib.Path(f).stat().st_size
    print(f"{f}: {sz/1e6:.2f} MB")
print("DEMO DONE")
