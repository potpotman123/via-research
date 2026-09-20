"""Phase 2e: group hit pages per document into classification packets. One packet = one document: header (source url,
path, agency guess from path/Legistar client), then the most informative hit pages (pricing terms and dollar signs first),
capped at MAX_CHARS. Output: snippets/packets/<doc_id>.txt and snippets/packets/index.csv with regex hints."""
import csv
import re
import sqlite3
from collections import defaultdict

from common import ENUM, ROOT, log

DB = ROOT / "text" / "corpus.db"
PK = ROOT / "snippets" / "packets"
PK.mkdir(parents=True, exist_ok=True)
MAX_CHARS = 14000
con = sqlite3.connect(DB)

# map cached path -> legistar client / matter title (for agency context)
ctx_by_url = {}
try:
    att = {r["url"]: r for r in csv.DictReader(open(ENUM / "legistar_attachments.csv"))}
    hits = {(r["client"], r["MatterId"]): r for r in csv.DictReader(open(ENUM / "legistar_hits.csv"))}
    for u, a in att.items():
        h = hits.get((a["client"], a["MatterId"]))
        if h:
            ctx_by_url[u] = f"legistar client={a['client']}; matter {h['MatterFile']} ({(h['MatterIntroDate'] or '')[:10]}): {h['MatterTitle'][:300]}"
except FileNotFoundError:
    pass

snips = list(csv.DictReader(open(ROOT / "snippets" / "index.csv")))
by_doc = defaultdict(list)
for s in snips:
    by_doc[int(s["doc_id"])].append(s)
log(f"{len(snips)} hit pages in {len(by_doc)} documents")

MONEY = re.compile(r"\$\s?\d[\d,]*(\.\d+)?")
PRICE_RX = re.compile(r"per (revenue|service|vehicle) hour|not.to.exceed|hourly|per trip|subscription|license|implementation|"
                      r"platform fee|annual fee|per vehicle|compensation|total contract|term of", re.I)
TURNKEY_RX = re.compile(r"per (revenue|service|vehicle) hour|revenue service hour|vehicle hours?|turnkey|provide[s]? (the )?(drivers|vehicles)|"
                        r"operat(e|es|ing) the service|driver(s)? (employed|provided|supplied) by (via|river north|the contractor)", re.I)
SOFTWARE_RX = re.compile(r"software as a service|saas|subscription|license fee|licens(e|ing) agreement|platform fee|implementation fee|"
                         r"agency[- ]owned vehicles|(agency|city|county|district)['’]?s? (own )?drivers|operated by (the )?(city|county|agency|district)", re.I)

rows = []
for did, items in sorted(by_doc.items()):
    path, url, n_pages = items[0]["path"], items[0]["url"], int(items[0]["n_pages"])
    pages = sorted({int(s["page"]) for s in items})
    texts = {p: (con.execute("SELECT text FROM pages WHERE doc_id=? AND page_no=?", (did, p)).fetchone() or [""])[0] for p in pages}
    # score pages: money mentions + pricing terms + entity terms, keep order by score then page number
    def score(p):
        t = texts[p]
        return len(MONEY.findall(t)) * 2 + len(PRICE_RX.findall(t)) + sum(1 for s in items if int(s["page"]) == p)
    ranked = sorted(pages, key=lambda p: (-score(p), p))
    chosen, total = [], 0
    for p in ranked:
        t = texts[p].strip()
        if not t:
            continue
        if total + len(t) > MAX_CHARS and chosen:
            break
        chosen.append(p)
        total += len(t)
    chosen.sort()
    body = "\n\n".join(f"=== page {p} of {n_pages} ===\n{texts[p].strip()[:MAX_CHARS]}" for p in chosen)
    agency_ctx = ctx_by_url.get(url, "")
    folder = path.split("/")[2] if path.startswith("raw/bleecker_drive/") and path.count("/") >= 3 else ""
    header = (f"# source_url: {url or '(local file from Bleecker sample)'}\n# path: {path}\n# pages_total: {n_pages}; hit_pages: {pages}; included: {chosen}\n"
              f"# context: {agency_ctx or ('Bleecker Drive folder: ' + folder if folder else '')}\n")
    (PK / f"{did}.txt").write_text(header + "\n" + body)
    full = " ".join(texts.values())
    rows.append(dict(doc_id=did, path=path, url=url, n_pages=n_pages, n_hit_pages=len(pages), n_included=len(chosen), chars=len(body),
                     money_mentions=len(MONEY.findall(full)), turnkey_hint=int(bool(TURNKEY_RX.search(full))),
                     software_hint=int(bool(SOFTWARE_RX.search(full))), context=agency_ctx[:200] or folder, packet=f"snippets/packets/{did}.txt"))
with open(PK / "index.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
log(f"{len(rows)} packets; avg chars {sum(r['chars'] for r in rows) // max(1, len(rows))}; "
    f"with $ mentions {sum(1 for r in rows if r['money_mentions'])}; turnkey-hint {sum(r['turnkey_hint'] for r in rows)}, "
    f"software-hint {sum(r['software_hint'] for r in rows)}")
