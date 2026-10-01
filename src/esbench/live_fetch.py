"""Live fetch with provenance + offline fallback.
Live (no key):
 - Open-Meteo forecast (Grenoble 45.18,5.72) — PV + temp.
 - NLR ATB landing pages (atb.nlr.gov) — cost/RTE text evidence.
 - PNNL cost-performance landing — LCOS framing evidence.
Writes data/raw/live_provenance.json with url, status, bytes, sha256, timestamp.
Never fails hard: records error and relies on vendored snapshots.
"""
import hashlib, json, time, os
from datetime import datetime, timezone
import requests

GRENOBLE = {"lat": 45.18, "lon": 5.72}
URLS = {
    "open_meteo": "https://api.open-meteo.com/v1/forecast?latitude=45.18&longitude=5.72&hourly=shortwave_radiation,temperature_2m&forecast_days=2&timezone=UTC",
    "atb_data": "https://atb.nlr.gov/electricity/2025/data",
    "atb_bess": "https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage",
    "pnnl": "https://www.pnnl.gov/projects/esgc-cost-performance",
}

def fetch(url, timeout=20):
    t0 = time.time()
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "esbench/0.1 (reproducibility)"})
        body = r.content
        return {"url": url, "status": r.status_code, "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "seconds": round(time.time() - t0, 3),
                "utc": datetime.now(timezone.utc).isoformat(),
                "ok": r.status_code == 200,
                "snippet": body[:400].decode("utf-8", "ignore")}
    except Exception as e:
        return {"url": url, "status": None, "bytes": 0, "sha256": None,
                "seconds": round(time.time() - t0, 3),
                "utc": datetime.now(timezone.utc).isoformat(),
                "ok": False, "error": str(e)[:300]}

def main(out="data/raw/live_provenance.json"):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    rec = {"utc": datetime.now(timezone.utc).isoformat(), "results": {}}
    for k, u in URLS.items():
        rec["results"][k] = fetch(u)
        # persist raw for audit (first 200kB max)
        try:
            import requests as rq
            r = rq.get(u, timeout=20, headers={"User-Agent": "esbench/0.1"})
            if r.status_code == 200:
                with open(os.path.join(os.path.dirname(out), f"live_{k}.bin"), "wb") as f:
                    f.write(r.content[:200000])
        except Exception:
            pass
    # also save open-meteo parsed sample for PV experiment
    try:
        om = rec["results"]["open_meteo"]
        if om.get("ok"):
            r = requests.get(URLS["open_meteo"], timeout=20)
            j = r.json()
            with open("data/raw/open_meteo_grenoble.json", "w") as f:
                json.dump(j, f, indent=2)
    except Exception:
        pass
    with open(out, "w") as f:
        json.dump(rec, f, indent=2)
    print(json.dumps({k: (v.get("status"), v.get("bytes"), v.get("ok")) for k, v in rec["results"].items()}, indent=2))
    return rec

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw/live_provenance.json")
    a = ap.parse_args()
    main(a.out)
