"""EDGAR: full-text search for each Via entity; Via's own filing index; Form 4 count since the lock-up expiry."""
import time

from common import COMPETITOR_TERMS, ENTITY_TERMS, ENUM, SEC_UA, get, log, session, write_csv

s = session(SEC_UA)
rows = []
for term in ENTITY_TERMS + COMPETITOR_TERMS:
    r = get(s, "https://efts.sec.gov/LATEST/search-index",
            params={"q": f'"{term}"', "dateRange": "custom", "startdt": "2015-01-01", "enddt": "2026-12-31"})
    time.sleep(0.3)
    if not r or r.status_code != 200:
        log(f"{term}: status {r.status_code if r else None}")
        continue
    hits = r.json().get("hits", {}).get("hits", [])
    for h in hits:
        src = h.get("_source", {})
        adsh = src.get("adsh", "")
        ciks = src.get("ciks", [])
        cik = ciks[0].lstrip("0") if ciks else ""
        fn = h.get("_id", "").split(":")[-1]
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fn}" if cik and adsh else ""
        rows.append(dict(term=term, file_date=src.get("file_date"), form=src.get("form"),
                         filer=" | ".join(src.get("display_names", [])), adsh=adsh, url=url))
    log(f"{term}: {len(hits)} hits")
write_csv(ENUM / "edgar_fts.csv", rows, ["term", "file_date", "form", "filer", "adsh", "url"])

r = get(s, "https://www.sec.gov/files/company_tickers.json")
cik = None
for v in (r.json().values() if r else []):
    if v.get("ticker") == "VIA":
        cik = str(v["cik_str"]).zfill(10)
        log(f"VIA CIK {cik} ({v.get('title')})")
if cik:
    r = get(s, f"https://data.sec.gov/submissions/CIK{cik}.json")
    rec = r.json().get("filings", {}).get("recent", {}) if r else {}
    frows = []
    for i in range(len(rec.get("form", []))):
        acc = rec["accessionNumber"][i]
        frows.append(dict(form=rec["form"][i], filingDate=rec["filingDate"][i], reportDate=rec["reportDate"][i], accession=acc,
                          url=f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{acc.replace('-', '')}/{rec['primaryDocument'][i]}"))
    write_csv(ENUM / "via_filings.csv", frows, ["form", "filingDate", "reportDate", "accession", "url"])
    f4 = [x for x in frows if x["form"] in ("4", "4/A") and x["filingDate"] >= "2026-03-01"]
    log(f"Form 4s since 2026-03-01: {len(f4)}; total filings listed: {len(frows)}")
