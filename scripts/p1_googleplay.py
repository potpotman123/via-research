"""Full Google Play developer listing for Via via Playwright infinite scroll (server-side HTML shows only 20 apps)."""
import asyncio
import re

from playwright.async_api import async_playwright

from common import ENUM, UA, log, write_csv

URL = "https://play.google.com/store/apps/developer?id=Via+Transportation+Inc.&hl=en_US&gl=US"


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        pg = await b.new_page(user_agent=UA, viewport={"width": 1400, "height": 2200})
        await pg.goto(URL, wait_until="domcontentloaded", timeout=90000)
        await pg.wait_for_timeout(3000)
        stable, last = 0, -1
        for _ in range(120):
            await pg.mouse.wheel(0, 25000)
            await pg.wait_for_timeout(1500)
            for sel in ("button:has-text('Show more')", "button:has-text('See more')", "[role=button]:has-text('Show more')"):
                try:
                    btn = pg.locator(sel).first
                    if await btn.count() and await btn.is_visible():
                        await btn.click()
                        await pg.wait_for_timeout(1500)
                except Exception:  # noqa: BLE001
                    pass
            n = await pg.locator("a[href*='/store/apps/details?id=']").count()
            stable = stable + 1 if n == last else 0
            last = n
            if stable >= 6:
                break
        hrefs = await pg.eval_on_selector_all("a[href*='/store/apps/details?id=']",
                                              "els => els.map(e => [e.getAttribute('href'), e.innerText])")
        await b.close()
    apps = {}
    for h, t in hrefs:
        m = re.search(r"id=([a-zA-Z0-9._]+)", h or "")
        if not m:
            continue
        title = (t or "").strip().split("\n")[0]
        if m.group(1) not in apps or (title and not apps[m.group(1)]):
            apps[m.group(1)] = title
    log(f"google play apps: {len(apps)}")
    write_csv(ENUM / "googleplay_apps.csv",
              [dict(package=k, title=v) for k, v in sorted(apps.items(), key=lambda x: x[1].lower())], ["package", "title"])


asyncio.run(main())
