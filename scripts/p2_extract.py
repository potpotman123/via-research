"""Phase 2b: extract page text from every PDF/DOCX/HTML in raw/cache and raw/bleecker_drive into SQLite FTS5.
Dedupes documents by content hash. Marks pages with no text layer for OCR. Idempotent: re-runs skip known files.
Tables: docs(doc_id, path, url, sha1, n_pages, n_empty), pages(doc_id, page_no, text) with FTS5 index pages_fts."""
import csv
import hashlib
import re
import sqlite3
from pathlib import Path

import fitz  # PyMuPDF

from common import RAW, ROOT, log

DB = ROOT / "text" / "corpus.db"
MANIFEST = ROOT / "text" / "manifest.csv"
con = sqlite3.connect(DB)
con.executescript("""
CREATE TABLE IF NOT EXISTS docs(doc_id INTEGER PRIMARY KEY, path TEXT UNIQUE, url TEXT, sha1 TEXT, n_pages INT, n_empty INT, kind TEXT);
CREATE TABLE IF NOT EXISTS pages(doc_id INT, page_no INT, text TEXT, PRIMARY KEY(doc_id, page_no));
CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(text, content='pages', content_rowid='rowid');
CREATE TABLE IF NOT EXISTS dupes(path TEXT PRIMARY KEY, sha1 TEXT, canonical_path TEXT);
""")
url_by_path = {}
if MANIFEST.exists():
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("path"):
                url_by_path[r["path"]] = r["url"]
known = {r[0] for r in con.execute("SELECT path FROM docs")} | {r[0] for r in con.execute("SELECT path FROM dupes")}
by_sha = {r[0]: r[1] for r in con.execute("SELECT sha1, path FROM docs")}

files = [p for d in (RAW / "cache", RAW / "bleecker_drive") if d.exists() for p in d.rglob("*")
         if p.is_file() and p.suffix.lower() in (".pdf", ".docx", ".doc", ".html", ".htm", ".txt")]
log(f"{len(files)} files, {len(known)} already indexed")
n_new = n_dup = 0
for p in files:
    rel = str(p.relative_to(ROOT))
    if rel in known:
        continue
    data = p.read_bytes()
    sha = hashlib.sha1(data).hexdigest()
    if sha in by_sha:
        con.execute("INSERT OR IGNORE INTO dupes VALUES(?,?,?)", (rel, sha, by_sha[sha]))
        n_dup += 1
        continue
    pages = []
    kind = p.suffix.lower().lstrip(".")
    try:
        if kind == "pdf":
            with fitz.open(stream=data, filetype="pdf") as doc:
                for i, pg in enumerate(doc):
                    pages.append((i + 1, pg.get_text("text")))
        elif kind in ("html", "htm"):
            txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", data.decode("utf-8", "ignore"), flags=re.S)
            txt = re.sub(r"<[^>]+>", " ", txt)
            pages = [(1, re.sub(r"\s+", " ", txt))]
        elif kind == "docx":
            import zipfile
            with zipfile.ZipFile(p) as z:
                xml = z.read("word/document.xml").decode("utf-8", "ignore")
            pages = [(1, re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml)))]
        else:
            pages = [(1, data.decode("utf-8", "ignore"))]
    except Exception as e:  # noqa: BLE001
        log(f"skip {rel}: {type(e).__name__} {e}")
        continue
    n_empty = sum(1 for _, t in pages if len(t.strip()) < 20)
    cur = con.execute("INSERT INTO docs(path,url,sha1,n_pages,n_empty,kind) VALUES(?,?,?,?,?,?)",
                      (rel, url_by_path.get(rel, ""), sha, len(pages), n_empty, kind))
    did = cur.lastrowid
    con.executemany("INSERT INTO pages VALUES(?,?,?)", [(did, no, t) for no, t in pages])
    by_sha[sha] = rel
    n_new += 1
    if n_new % 50 == 0:
        con.commit()
        log(f"indexed {n_new} new docs")
con.execute("INSERT INTO pages_fts(pages_fts) VALUES('rebuild')")
con.commit()
tot = con.execute("SELECT COUNT(*), SUM(n_pages), SUM(n_empty) FROM docs").fetchone()
log(f"new {n_new}, dupes {n_dup}; corpus: {tot[0]} docs, {tot[1]} pages, {tot[2]} pages with no text layer (OCR candidates)")
