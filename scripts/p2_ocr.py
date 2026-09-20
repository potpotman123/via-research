"""Phase 2d: OCR pages that have no text layer, using Apple Vision via ocrmac. Updates pages.text in corpus.db and
rebuilds the FTS index. Only touches pages flagged empty (len(text) < 20)."""
import sqlite3

import fitz
from ocrmac import ocrmac

from common import ROOT, log

DB = ROOT / "text" / "corpus.db"
con = sqlite3.connect(DB)
todo = con.execute("""SELECT p.doc_id, p.page_no, d.path FROM pages p JOIN docs d USING(doc_id)
                      WHERE d.kind='pdf' AND length(trim(p.text)) < 20 ORDER BY p.doc_id, p.page_no""").fetchall()
log(f"{len(todo)} empty PDF pages to OCR")
done = 0
cur_path, doc = None, None
for did, pno, path in todo:
    if path != cur_path:
        if doc:
            doc.close()
        doc = fitz.open(ROOT / path)
        cur_path = path
    try:
        pix = doc[pno - 1].get_pixmap(dpi=200)
        img_path = ROOT / "text" / "_ocr_tmp.png"
        pix.save(str(img_path))
        res = ocrmac.OCR(str(img_path), language_preference=["en-US"], recognition_level="accurate").recognize()
        text = "\n".join(t for t, _conf, _bbox in res)
        con.execute("UPDATE pages SET text=? WHERE doc_id=? AND page_no=?", (text, did, pno))
        done += 1
        if done % 25 == 0:
            con.commit()
            log(f"ocr {done}/{len(todo)}")
    except Exception as e:  # noqa: BLE001
        log(f"ocr failed {path} p{pno}: {type(e).__name__}")
if doc:
    doc.close()
con.execute("UPDATE docs SET n_empty=(SELECT COUNT(*) FROM pages p WHERE p.doc_id=docs.doc_id AND length(trim(p.text))<20)")
con.execute("INSERT INTO pages_fts(pages_fts) VALUES('rebuild')")
con.commit()
log(f"ocr done: {done} pages")
