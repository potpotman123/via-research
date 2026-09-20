"""Phase 2c: query the FTS5 corpus for entity + pricing terms; write hit pages (+/-1 page of context) as snippet files.
Output: snippets/<doc_id>_p<page>.txt and snippets/index.csv (doc_id, path, url, page, terms, chars). Also a regex
pre-classification hint per snippet (turnkey_hint / software_hint) so Tier 0 can skip the obvious rows."""
import csv
import re
import sqlite3
from collections import defaultdict

from common import COMPETITOR_TERMS, ENTITY_TERMS, ROOT, log

DB = ROOT / "text" / "corpus.db"
SNIP = ROOT / "snippets"
SNIP.mkdir(exist_ok=True)
con = sqlite3.connect(DB)

ENTITY_Q = " OR ".join(f'"{t}"' for t in ENTITY_TERMS + COMPETITOR_TERMS + ["Via"])
PRICING = ["per revenue hour", "per service hour", "per vehicle hour", "revenue service hour", "not to exceed", "not-to-exceed",
           "hourly rate", "per hour", "per trip", "subscription", "license fee", "licensing", "implementation fee", "software fee",
           "platform fee", "annual fee", "per vehicle per month", "SaaS", "turnkey", "drivers", "vehicles", "fleet"]
TURNKEY_RX = re.compile(r"per (revenue|service|vehicle) hour|revenue service hour|vehicle hours?|turnkey|provide[s]? (the )?(drivers|vehicles)|"
                        r"operat(e|es|ing) the service|driver(s)? (employed|provided|supplied) by (via|river north|the contractor)", re.I)
SOFTWARE_RX = re.compile(r"software as a service|saas|subscription|license fee|licens(e|ing) agreement|platform fee|implementation fee|"
                         r"agency[- ]owned vehicles|(agency|city|county|district)['’]?s? (own )?drivers|operated by (the )?(city|county|agency|district)", re.I)

# entity hits
hits = defaultdict(set)  # (doc_id, page) -> terms
for t in ENTITY_TERMS + COMPETITOR_TERMS:
    for rowid, in con.execute("SELECT rowid FROM pages_fts WHERE pages_fts MATCH ?", (f'"{t}"',)):
        did, pno = con.execute("SELECT doc_id, page_no FROM pages WHERE rowid=?", (rowid,)).fetchone()
        hits[(did, pno)].add(t)
log(f"entity-term hit pages: {len(hits)} across {len({d for d, _ in hits})} docs")

# bare "Via" only counts when a pricing term is on the same page (limits false positives like 'via email')
for t in PRICING:
    for rowid, in con.execute("SELECT rowid FROM pages_fts WHERE pages_fts MATCH ?", (f'"Via" AND "{t}"',)):
        did, pno = con.execute("SELECT doc_id, page_no FROM pages WHERE rowid=?", (rowid,)).fetchone()
        hits[(did, pno)].add(f"Via+{t}")
log(f"with Via+pricing pages: {len(hits)}")

docs = {r[0]: (r[1], r[2], r[3]) for r in con.execute("SELECT doc_id, path, url, n_pages FROM docs")}
rows = []
for (did, pno), terms in sorted(hits.items()):
    path, url, n = docs[did]
    lo, hi = max(1, pno - 1), min(n, pno + 1)
    parts = []
    for p in range(lo, hi + 1):
        t = con.execute("SELECT text FROM pages WHERE doc_id=? AND page_no=?", (did, p)).fetchone()
        parts.append(f"=== page {p} ===\n{(t[0] if t else '').strip()}")
    body = "\n".join(parts)
    out = SNIP / f"{did}_p{pno}.txt"
    out.write_text(f"# source: {url or path}\n# path: {path}\n# hit page: {pno} of {n}\n# terms: {', '.join(sorted(terms))}\n\n{body}")
    rows.append(dict(doc_id=did, path=path, url=url, page=pno, n_pages=n, terms="; ".join(sorted(terms)), chars=len(body),
                     turnkey_hint=int(bool(TURNKEY_RX.search(body))), software_hint=int(bool(SOFTWARE_RX.search(body))),
                     snippet=str(out.relative_to(ROOT))))
with open(SNIP / "index.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["doc_id"])
    w.writeheader()
    w.writerows(rows)
tk = sum(r["turnkey_hint"] and not r["software_hint"] for r in rows)
sw = sum(r["software_hint"] and not r["turnkey_hint"] for r in rows)
both = sum(r["software_hint"] and r["turnkey_hint"] for r in rows)
log(f"{len(rows)} snippets; hints: turnkey-only {tk}, software-only {sw}, both {both}, neither {len(rows) - tk - sw - both}")
