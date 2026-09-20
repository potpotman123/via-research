"""Download NTD contractual relationship xlsx files by clicking the link in a headful Chromium page (transit.dot.gov blocks non-browser fetches)."""
import asyncio, csv
from playwright.async_api import async_playwright
from common import ENUM, ROOT, UA, log
files = list(csv.DictReader(open(ENUM / "ntd_contractual_files.csv")))
async def main():
    ok = 0
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        ctx = await b.new_context(user_agent=UA, viewport={"width": 1200, "height": 800}, accept_downloads=True)
        pg = await ctx.new_page()
        for f in files:
            dest = ROOT / f["path"]
            if dest.exists() and dest.stat().st_size > 10000: ok += 1; continue
            page_url = f"https://www.transit.dot.gov/ntd/data-product/{f['year']}-annual-database-contractual-relationship"
            try:
                await pg.goto(page_url, wait_until="domcontentloaded", timeout=60000)
                await pg.wait_for_timeout(2000)
                async with pg.expect_download(timeout=120000) as dl_info:
                    await pg.click("a[href$='.xlsx']")
                dl = await dl_info.value
                await dl.save_as(dest)
                if dest.read_bytes()[:2] == b"PK":
                    ok += 1; log(f"{f['year']}: saved {dest.stat().st_size//1024} KB")
                else:
                    log(f"{f['year']}: not a zip/xlsx"); dest.unlink()
            except Exception as e:
                log(f"{f['year']}: {type(e).__name__} {str(e)[:120]}")
        await b.close()
    log(f"downloaded {ok}/{len(files)}")
asyncio.run(main())
