"""Phase 2a: download candidate documents into raw/cache with per-host throttling. Input: one or more CSVs with a `url`
column (default: text/enum/legistar_attachments.csv). Output/append: text/manifest.csv (url, path, status, content_type, bytes).
Usage: python scripts/p2_fetch.py [csv ...]"""
import csv
import hashlib
import mimetypes
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

from common import CACHE, ENUM, ROOT, get, log, session

MANIFEST = ROOT / "text" / "manifest.csv"
FIELDS = ["url", "path", "status", "content_type", "bytes"]
inputs = [Path(a) for a in sys.argv[1:]] or [ENUM / "legistar_attachments.csv"]

done = {}
if MANIFEST.exists():
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            done[r["url"]] = r
urls = []
for p in inputs:
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            u = (r.get("url") or "").strip()
            if u.startswith("http") and u not in done:
                urls.append(u)
urls = sorted(set(urls))
log(f"{len(urls)} new urls to fetch ({len(done)} already in manifest)")

s = session()
host_lock = defaultdict(threading.Lock)
last_hit = defaultdict(float)
write_lock = threading.Lock()
EXT = {"application/pdf": "pdf", "text/html": "html", "application/msword": "doc",
       "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
       "application/vnd.ms-excel": "xls", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx"}


def fetch(u):
    host = urlparse(u).netloc
    with host_lock[host]:
        wait = 1.0 - (time.time() - last_hit[host])
        if wait > 0:
            time.sleep(wait)
        last_hit[host] = time.time()
        r = get(s, u, tries=2, timeout=120)
    row = dict(url=u, path="", status=(r.status_code if r else "ERR"), content_type="", bytes=0)
    if r is not None and r.status_code == 200 and r.content:
        ct = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        ext = EXT.get(ct) or (mimetypes.guess_extension(ct) or "").lstrip(".") or Path(urlparse(u).path).suffix.lstrip(".") or "bin"
        if r.content[:5] == b"%PDF-":
            ext = "pdf"
        p = CACHE / (hashlib.sha1(u.encode()).hexdigest() + "." + ext)
        p.write_bytes(r.content)
        row.update(path=str(p.relative_to(ROOT)), content_type=ct, bytes=len(r.content))
    with write_lock:
        new = not MANIFEST.exists()
        with open(MANIFEST, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if new:
                w.writeheader()
            w.writerow(row)
    return row


ok = 0
with ThreadPoolExecutor(6) as ex:
    for i, row in enumerate(ex.map(fetch, urls)):
        ok += row["status"] == 200
        if i and i % 100 == 0:
            log(f"{i}/{len(urls)} fetched, {ok} ok")
log(f"done: {ok}/{len(urls)} ok -> {MANIFEST.relative_to(ROOT)}")
