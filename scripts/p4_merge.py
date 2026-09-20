"""Phase 4: merge shards/*.csv into out/via_contract_census.csv with validation.
Rules: schema must match shards/HEADER.csv; any row carrying a number without source_url_1 is rejected; dedupe on
(agency, contract_action, award_or_approval_date); scope_type must be Turnkey|Software-only|Hybrid|Unknown.
Rejected rows go to out/rejects.csv with a reason so they can be routed up a tier. Prints a mix summary."""
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

from common import ROOT, log

SHARDS = ROOT / "shards"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
HEADER = next(csv.reader(open(SHARDS / "HEADER.csv")))
NUMERIC = ["total_value_usd", "annual_value_usd", "hourly_rate_usd", "software_fee_usd", "implementation_fee_usd",
           "implementation_fee_pct_of_year1", "fleet_size", "term_years_incl_options"]
SCOPES = {"Turnkey", "Software-only", "Hybrid", "Unknown"}


def num(v):
    v = (v or "").strip().replace("$", "").replace(",", "")
    if not v:
        return None
    try:
        return float(re.sub(r"[^\d.\-]", "", v))
    except ValueError:
        return None


rows, rejects = [], []
for p in sorted(SHARDS.glob("*.csv")):
    if p.name == "HEADER.csv":
        continue
    with open(p, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if [c.strip() for c in (rd.fieldnames or [])] != HEADER:
            log(f"SCHEMA MISMATCH {p.name}: {rd.fieldnames}")
            continue
        for i, r in enumerate(rd, 2):
            r = {k: (v or "").strip() for k, v in r.items()}
            r["_shard"] = f"{p.name}:{i}"
            reasons = []
            if not r["agency"]:
                reasons.append("no agency")
            if r["scope_type"] not in SCOPES:
                reasons.append(f"bad scope_type {r['scope_type']!r}")
            has_num = any(num(r[c]) is not None for c in NUMERIC)
            if has_num and not r["source_url_1"].startswith("http"):
                reasons.append("number without source_url_1")
            if r["signed_after_2025_12_16"] not in ("", "0", "1", "TRUE", "FALSE", "true", "false"):
                reasons.append("bad signed_after flag")
            (rejects if reasons else rows).append(dict(r, _reason="; ".join(reasons)))

seen, deduped = {}, []
for r in rows:
    k = (r["agency"].lower(), r["contract_action"].lower(), r["award_or_approval_date"])
    if k in seen:
        # keep the row with more filled numeric fields
        old = seen[k]
        if sum(num(r[c]) is not None for c in NUMERIC) > sum(num(old[c]) is not None for c in NUMERIC):
            deduped[deduped.index(old)] = r
            seen[k] = r
        continue
    seen[k] = r
    deduped.append(r)

with open(OUT / "via_contract_census.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=HEADER, extrasaction="ignore")
    w.writeheader()
    w.writerows(deduped)
with open(OUT / "rejects.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=HEADER + ["_shard", "_reason"], extrasaction="ignore")
    w.writeheader()
    w.writerows(rejects)
log(f"accepted {len(deduped)} (from {len(rows)}, {len(rows) - len(deduped)} dupes), rejected {len(rejects)}")

# mix summary: count-weighted and dollar-weighted (annual where present, else total/term)
cnt = Counter(r["scope_type"] for r in deduped)
dollars = defaultdict(float)
for r in deduped:
    a = num(r["annual_value_usd"])
    if a is None:
        t, y = num(r["total_value_usd"]), num(r["term_years_incl_options"])
        a = t / y if (t and y) else None
    if a:
        dollars[r["scope_type"]] += a
post = [r for r in deduped if r["signed_after_2025_12_16"] in ("1", "TRUE", "true")]
log(f"count-weighted: {dict(cnt)}")
log(f"annualized $ by scope: { {k: round(v / 1e6, 1) for k, v in dollars.items()} } ($mm, rows with values only)")
log(f"post-2025-12-16 rows: {len(post)} -> {dict(Counter(r['scope_type'] for r in post))}")
