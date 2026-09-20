"""Download Bleecker's public Drive folder completely: list children via embeddedfolderview (plain HTML), gdown each subfolder."""
import re, subprocess, sys, html
from pathlib import Path
from common import RAW, ROOT, get, log, session
FOLDER = "1jFI7x1sodivnF2uCUtpNrRC65ojkl4VA"
OUT = RAW / "bleecker_drive"; OUT.mkdir(exist_ok=True)
s = session()
r = get(s, f"https://drive.google.com/embeddedfolderview?id={FOLDER}#list", timeout=60)
if not r or r.status_code != 200:
    log(f"embedded view status {r.status_code if r else None}"); sys.exit(1)
entries = re.findall(r'<div class="flip-entry" id="entry-([^"]+)".*?flip-entry-title">(.*?)</div>', r.text, re.S)
log(f"top-level entries: {len(entries)}")
folders = [(i, html.unescape(re.sub(r"<[^>]+>", "", n)).strip()) for i, n in entries]
# entries can be files too; gdown handles both (--folder fails on a file id, so try file fallback)
ok = fail = 0
for fid, name in folders:
    safe = re.sub(r'[\\/:*?"<>|]+', "_", name)[:120]
    dest = OUT / safe
    if dest.exists() and any(dest.rglob("*")):
        ok += 1; continue
    cp = subprocess.run([str(ROOT / ".venv/bin/gdown"), "--folder", f"https://drive.google.com/drive/folders/{fid}", "-O", str(dest), "--remaining-ok", "-q"],
                        capture_output=True, text=True)
    if cp.returncode != 0 or not dest.exists():
        cp2 = subprocess.run([str(ROOT / ".venv/bin/gdown"), fid, "-O", str(OUT / safe), "-q"], capture_output=True, text=True)
        if cp2.returncode != 0:
            fail += 1; log(f"FAIL {name}: {(cp.stderr or cp2.stderr)[-150:].strip()}"); continue
    ok += 1
files = list(p for p in OUT.rglob("*") if p.is_file())
log(f"folders ok {ok}, failed {fail}; total files {len(files)}, {sum(p.stat().st_size for p in files)/1e6:.0f} MB")
