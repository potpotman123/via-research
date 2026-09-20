"""Print only the pages of a PDF that match any of the given terms (case-insensitive), trimmed. Falls back to Apple Vision OCR
for pages with no text layer. Usage: python scripts/gap_pdf.py file.pdf [--terms "Via,River North,$"] [--max-chars 3500] [--max-pages 8]"""
import argparse
import re
import sys

import fitz

ap = argparse.ArgumentParser()
ap.add_argument("pdf")
ap.add_argument("--terms", default="Via,River North,NoMad,Remix,Downtowner,$,per hour,not to exceed,microtransit")
ap.add_argument("--max-chars", type=int, default=3500)
ap.add_argument("--max-pages", type=int, default=8)
a = ap.parse_args()
terms = [t.strip() for t in a.terms.split(",") if t.strip()]
rx = re.compile("|".join(re.escape(t) for t in terms), re.I)
doc = fitz.open(a.pdf)
print(f"# {a.pdf}: {len(doc)} pages")
hits = []
for i, pg in enumerate(doc):
    txt = pg.get_text("text")
    if len(txt.strip()) < 20:
        try:
            from ocrmac import ocrmac
            pix = pg.get_pixmap(dpi=200)
            pix.save("/tmp/_gap_ocr.png")
            txt = "\n".join(t for t, _c, _b in ocrmac.OCR("/tmp/_gap_ocr.png", language_preference=["en-US"]).recognize())
        except Exception:  # noqa: BLE001
            txt = ""
    score = len(rx.findall(txt)) + 3 * len(re.findall(r"\$\s?\d[\d,]{3,}", txt))
    if score:
        hits.append((score, i + 1, txt))
if not hits:
    print("# no pages matched", ", ".join(terms))
    sys.exit(0)
hits.sort(key=lambda h: (-h[0], h[1]))
for _score, pno, txt in sorted(hits[: a.max_pages], key=lambda h: h[1]):
    t = re.sub(r"\n{3,}", "\n\n", txt.strip())
    print(f"\n=== page {pno} ===\n{t[: a.max_chars]}")
print(f"\n# matched pages: {[h[1] for h in sorted(hits, key=lambda h: h[1])]}")
