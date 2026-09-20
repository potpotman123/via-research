"""Filter downloaded NTD contractual relationship tables for Via entities; print per-year hits and the column layout."""
import csv, re
import pandas as pd
from common import COMPETITOR_TERMS, ENTITY_TERMS, ENUM, ROOT, log, write_csv
pat = re.compile("|".join(re.escape(t) for t in ENTITY_TERMS + COMPETITOR_TERMS + ["Via, Inc", "Via Inc", "ViaVan", "Via Transportation", "Via  Transportation"]), re.I)
hits = []
for f in csv.DictReader(open(ENUM / "ntd_contractual_files.csv")):
    p = ROOT / f["path"]
    sheets = pd.read_excel(p, sheet_name=None, dtype=str)
    n = 0
    for sn, df in sheets.items():
        if f["year"] == "2024": log(f"sheet {sn}: {len(df)} rows; cols {list(df.columns)}")
        mask = df.apply(lambda col: col.astype(str).str.contains(pat, na=False)).any(axis=1)
        for _, row in df[mask].iterrows():
            d = {str(k): (v if isinstance(v, str) else "") for k, v in row.to_dict().items()}
            d.update(year=f["year"], sheet=sn); hits.append(d); n += 1
    log(f"{f['year']}: {n} matching rows")
fields = ["year", "sheet"] + sorted({k for h in hits for k in h if k not in ("year", "sheet")})
write_csv(ENUM / "ntd_contractual_hits.csv", hits, fields)
# compact view
for h in sorted(hits, key=lambda x: (x["year"], x.get("Agency", ""))):
    keys = [k for k in h if re.search(r"agency|contract|other party|mode|tos|type of service|amount|paid|expense|city|state", k, re.I)]
    print(h["year"], "|", " | ".join(f"{k[:18]}={str(h[k])[:38]}" for k in keys if h[k]))
