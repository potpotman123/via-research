"""Compare each Drive subfolder's embedded listing to disk; retry missing files by id (gdown, then curl with confirm)."""
import re, html, subprocess, time
from pathlib import Path
from common import RAW, ROOT, get, log, session
FOLDER = "1jFI7x1sodivnF2uCUtpNrRC65ojkl4VA"; OUT = RAW / "bleecker_drive"
s = session()
def listing(fid):
    r = get(s, f"https://drive.google.com/embeddedfolderview?id={fid}#list", timeout=60)
    if not r or r.status_code != 200: return []
    ents = re.findall(r'<div class="flip-entry" id="entry-([^"]+)"(.*?)flip-entry-title">(.*?)</div>', r.text, re.S)
    out = []
    for i, mid, n in ents:
        name = html.unescape(re.sub(r"<[^>]+>", "", n)).strip()
        is_folder = "folder" in mid.lower() or re.search(r"drive/folders/", mid) is not None or "application/vnd.google-apps.folder" in mid
        out.append((i, name, is_folder))
    return out
def safe(n): return re.sub(r'[\\/:*?"<>|]+', "_", n)[:120]
missing, got, fail = [], 0, 0
def walk(fid, dest, depth=0):
    global got, fail
    dest.mkdir(parents=True, exist_ok=True)
    for i, name, is_folder in listing(fid):
        p = dest / safe(name)
        if is_folder or (not p.exists() and "." not in name[-6:]):
            if depth < 3: walk(i, p, depth + 1)
            continue
        if p.exists() and p.stat().st_size > 0: continue
        missing.append((i, name, p))
        cp = subprocess.run([str(ROOT / ".venv/bin/gdown"), "--fuzzy", "-q", f"https://drive.google.com/uc?id={i}", "-O", str(p)], capture_output=True, text=True)
        if not (p.exists() and p.stat().st_size > 0):
            subprocess.run(["curl", "-s", "-L", "-m", "300", "-o", str(p), f"https://drive.google.com/uc?export=download&id={i}&confirm=t"], capture_output=True)
        if p.exists() and p.stat().st_size > 0 and not p.read_bytes()[:15].lower().startswith(b"<!doctype html"):
            got += 1
        else:
            fail += 1; log(f"FAIL {dest.name}/{name}: {cp.stderr[-120:].strip()}")
            if p.exists(): p.unlink()
        time.sleep(0.5)
walk(FOLDER, OUT)
files = [p for p in OUT.rglob("*") if p.is_file()]
log(f"missing {len(missing)}: recovered {got}, still failed {fail}; total files {len(files)}, {sum(p.stat().st_size for p in files)/1e6:.0f} MB")
