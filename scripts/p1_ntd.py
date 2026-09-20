"""NTD annual Contractual Relationship tables: locate on transit.dot.gov, download, filter rows for Via entities."""
import re

import pandas as pd

from common import COMPETITOR_TERMS, ENTITY_TERMS, ENUM, cached_get, get, log, session, write_csv

s = session()
pat = re.compile("|".join(re.escape(t) for t in ENTITY_TERMS + COMPETITOR_TERMS + ["Via, Inc", "Via Inc", "ViaVan"]), re.I)
hits, found_files = [], []
for year in range(2017, 2025):
    got = None
    for slug in (f"{year}-annual-database-contractual-relationship", f"{year}-annual-database-contractual-relationships",
                 f"{year}-contractual-relationship", f"{year}-contractual-relationships",
                 f"{year}-annual-database-contractual-relationship-0"):
        r = get(s, f"https://www.transit.dot.gov/ntd/data-product/{slug}", tries=1, timeout=60)
        if r and r.status_code == 200:
            links = re.findall(r'href="([^"]+\.(?:xlsx|xlsm|xls|csv))"', r.text, re.I)
            if links:
                got = links[0] if links[0].startswith("http") else "https://www.transit.dot.gov" + links[0]
                break
    if not got:
        log(f"{year}: no data-product page found")
        continue
    p = cached_get(s, got, ext=got.rsplit(".", 1)[-1].lower(), timeout=300)
    if not p:
        log(f"{year}: download failed {got}")
        continue
    found_files.append(dict(year=year, url=got, path=str(p)))
    try:
        sheets = pd.read_excel(p, sheet_name=None, dtype=str) if p.suffix != ".csv" else {"csv": pd.read_csv(p, dtype=str)}
    except Exception as e:  # noqa: BLE001
        log(f"{year}: read failed {e}")
        continue
    n = 0
    for sn, df in sheets.items():
        mask = df.apply(lambda col: col.astype(str).str.contains(pat, na=False)).any(axis=1)
        for _, row in df[mask].iterrows():
            d = {str(k): (v if isinstance(v, str) else "") for k, v in row.to_dict().items()}
            d.update(year=year, sheet=sn)
            hits.append(d)
            n += 1
    log(f"{year}: {n} matching rows from {got.rsplit('/', 1)[-1]}")
write_csv(ENUM / "ntd_contractual_files.csv", found_files, ["year", "url", "path"])
if hits:
    fields = ["year", "sheet"] + sorted({k for h in hits for k in h if k not in ("year", "sheet")})
    write_csv(ENUM / "ntd_contractual_hits.csv", hits, fields)
