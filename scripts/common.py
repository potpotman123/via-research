"""Shared helpers for the VIA enumeration/extraction scripts. Zero model tokens: everything here is deterministic."""
import csv
import hashlib
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
ENUM = ROOT / "text" / "enum"
CACHE = RAW / "cache"
for _p in (RAW, ENUM, CACHE):
    _p.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
SEC_UA = "Kendall Wu kendall_wu@college.harvard.edu"

# Via contracting entities (FY2025 10-K Exhibit 21.1) that sign public-sector contracts.
ENTITY_TERMS = [
    "River North Transit", "NoMad Transit", "Crosby Street Transit", "Via Mobility",
    "Via Transportation", "Via Transit", "Remix Technologies", "Downtowner",
    "Flatiron Transit", "Greenpoint Transit", "Port City Transit", "Tidewater Transit",
    "Sioux Falls Transit", "Citymapper",
]
# Competitors whose awards at a former Via agency are how losses surface.
COMPETITOR_TERMS = ["Spare Labs", "RideCo"]


def log(msg):
    print(msg, flush=True)


def session(ua=UA):
    s = requests.Session()
    s.headers.update({"User-Agent": ua, "Accept-Language": "en-US,en;q=0.9"})
    return s


def get(s, url, tries=3, timeout=60, **kw):
    """GET with retry on 429/5xx/connection errors. Returns Response or None."""
    for i in range(tries):
        try:
            r = s.get(url, timeout=timeout, **kw)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 * (i + 1))
                continue
            return r
        except requests.RequestException:
            time.sleep(2 * (i + 1))
    return None


def cached_get(s, url, ext="bin", **kw):
    """Download once into raw/cache keyed by sha1(url). Returns Path or None."""
    p = CACHE / (hashlib.sha1(url.encode()).hexdigest() + "." + ext)
    if p.exists() and p.stat().st_size > 0:
        return p
    r = get(s, url, **kw)
    if r is None or r.status_code != 200:
        return None
    p.write_bytes(r.content)
    return p


def write_csv(path, rows, fields):
    path = Path(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    log(f"wrote {len(rows)} rows -> {path.relative_to(ROOT)}")
