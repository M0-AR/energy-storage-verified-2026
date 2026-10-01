import sys
sys.path.insert(0, "src")
from esbench.live_fetch import main
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--out", default="data/raw/live_provenance.json")
a = ap.parse_args()
main(a.out)
