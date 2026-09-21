"""Filter downloaded NTD contractual relationship tables for Via entities (as SELLER) and for competitor sellers; write text/enum/ntd_contractual_hits.csv.
2026-09-21 fix: the original matched exact entity strings anywhere in the row, so sellers entered as 'VIA', 'River North (VIA)',
'VIA, North River Transit', 'Via (RiverNorth Transit)' or 'Via / River North LLC' were missed (RY2024 undercounted $96.8mm as $42.7mm)."""
import csv, re
import pandas as pd
from common import ENUM, ROOT, log, write_csv
VIA = re.compile(r"\bvia\b|river\s*north|north\s*river|nomad|crosby\s*street|tidewater|port\s*city\s*transit|sioux\s*falls\s*transit|downtowner|remix|twin\s*cities|viavan|flatiron\s*transit|greenpoint\s*transit", re.I)
TRAP = re.compile(r"via\s*mobility\s*services|via\s*metropolitan|rideco|ridecorp", re.I)   # Boulder nonprofit; San Antonio agency; competitors
COMP = re.compile(r"rideco|spare\s*labs|\bspare\b|ridecorp", re.I)
hits = []
for f in csv.DictReader(open(ENUM / "ntd_contractual_files.csv")):
    p = ROOT / f["path"]; n = 0
    for sn, df in pd.read_excel(p, sheet_name=None, dtype=str).items():
        seller_cols = [c for c in df.columns if re.search(r"Operator Name|Company Name", str(c))]
        if not seller_cols: continue
        seller = df[seller_cols].fillna("").astype(str).agg(" | ".join, axis=1)
        is_via = seller.str.contains(VIA, na=False) & ~seller.str.contains(TRAP, na=False)
        is_comp = seller.str.contains(COMP, na=False)
        for idx in df.index[is_via | is_comp]:
            row = df.loc[idx]
            d = {str(k): (v if isinstance(v, str) else "") for k, v in row.to_dict().items()}
            d.update(year=f["year"], sheet=sn, seller_kind=("competitor" if is_comp[idx] else "via")); hits.append(d); n += 1
    log(f"{f['year']}: {n} matching rows")
fields = ["year", "sheet", "seller_kind"] + sorted({k for h in hits for k in h if k not in ("year", "sheet", "seller_kind")})
write_csv(ENUM / "ntd_contractual_hits.csv", hits, fields)
