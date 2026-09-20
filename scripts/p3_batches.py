"""Phase 3 prep: split classification packets into batches for subagents. Tiering by regex hints:
  tier1 (Haiku): packets where exactly one of turnkey_hint/software_hint fires and there are $ mentions
  tier2 (Sonnet): packets with both/neither hints, or no $ mentions (ambiguous), or very long
Writes shards/batches/<tier>_<nn>.txt (one packet path per line) and prints the plan.
Usage: python scripts/p3_batches.py [batch_size=12]"""
import csv
import sys
from pathlib import Path

from common import ROOT, log

BATCH = int(sys.argv[1]) if len(sys.argv) > 1 else 12
idx = list(csv.DictReader(open(ROOT / "snippets" / "packets" / "index.csv")))
out = ROOT / "shards" / "batches"
out.mkdir(parents=True, exist_ok=True)
for old in out.glob("*.txt"):
    old.unlink()

tier1, tier2 = [], []
for r in idx:
    t, s_, money = int(r["turnkey_hint"]), int(r["software_hint"]), int(r["money_mentions"])
    (tier1 if (t ^ s_) and money > 0 and int(r["chars"]) < 12000 else tier2).append(r)
# order: most $ mentions first so the richest documents land in early batches
for lst in (tier1, tier2):
    lst.sort(key=lambda r: -int(r["money_mentions"]))


def write(lst, name):
    n = 0
    for i in range(0, len(lst), BATCH):
        p = out / f"{name}_{i // BATCH:02d}.txt"
        p.write_text("\n".join(r["packet"] for r in lst[i:i + BATCH]) + "\n")
        n += 1
    return n


n1, n2 = write(tier1, "tier1_haiku"), write(tier2, "tier2_sonnet")
log(f"packets: {len(idx)} -> tier1 {len(tier1)} in {n1} batches, tier2 {len(tier2)} in {n2} batches (batch size {BATCH})")
