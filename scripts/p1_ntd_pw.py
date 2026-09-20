"""NTD Contractual Relationship tables via headless Chromium (transit.dot.gov 403s plain HTTP). Download xlsx per year, filter for Via entities."""
import asyncio, re
import pandas as pd
from playwright.async_api import async_playwright
from common import COMPETITOR_TERMS, ENTITY_TERMS, ENUM, RAW, UA, log, write_csv
OUT = RAW / "ntd"; OUT.mkdir(exist_ok=True)
pat = re.compile("|".join(re.escape(t) for t in ENTITY_TERMS + COMPETITOR_TERMS + ["Via, Inc", "Via Inc", "ViaVan", "Via Transportation"]), re.I)

async def main():
    files = []
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(user_agent=UA, viewport={"width": 1300, "height": 900})
        pg = await ctx.new_page()
        for year in range(2019, 2025):
            url = f"https://www.transit.dot.gov/ntd/data-product/{year}-annual-database-contractual-relationship"
            try:
                resp = await pg.goto(url, wait_until="domcontentloaded", timeout=60000)
                await pg.wait_for_timeout(2500)
                st = resp.status if resp else None
                hrefs = await pg.eval_on_selector_all("a[href$='.xlsx'], a[href$='.xlsm'], a[href$='.xls']", "els => els.map(e => e.href)")
                log(f"{year}: page {st}, {len(hrefs)} spreadsheet links")
                for h in hrefs[:1]:
                    r = await ctx.request.get(h, timeout=120000)
                    if r.ok:
                        dest = OUT / f"contractual_{year}.xlsx"
                        dest.write_bytes(await r.body())
                        files.append(dict(year=year, url=h, path=str(dest)))
                        log(f"  saved {dest.name} ({dest.stat().st_size//1024} KB)")
                    else:
                        log(f"  download {r.status} {h}")
            except Exception as e:
                log(f"{year}: {type(e).__name__} {str(e)[:100]}")
        await b.close()
    write_csv(ENUM / "ntd_contractual_files.csv", files, ["year", "url", "path"])
    hits = []
    for f in files:
        try:
            sheets = pd.read_excel(f["path"], sheet_name=None, dtype=str)
        except Exception as e:
            log(f"{f['year']}: read failed {e}"); continue
        n = 0
        for sn, df in sheets.items():
            mask = df.apply(lambda col: col.astype(str).str.contains(pat, na=False)).any(axis=1)
            for _, row in df[mask].iterrows():
                d = {str(k): (v if isinstance(v, str) else "") for k, v in row.to_dict().items()}
                d.update(year=f["year"], sheet=sn); hits.append(d); n += 1
        log(f"{f['year']}: {n} matching rows; columns: {list(list(sheets.values())[0].columns)[:12]}")
    if hits:
        fields = ["year", "sheet"] + sorted({k for h in hits for k in h if k not in ("year", "sheet")})
        write_csv(ENUM / "ntd_contractual_hits.csv", hits, fields)
asyncio.run(main())
