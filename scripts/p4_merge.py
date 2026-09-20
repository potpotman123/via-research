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


EXCL = []
if (SHARDS / "_exclusions.csv").exists():
    EXCL = list(csv.DictReader(open(SHARDS / "_exclusions.csv")))

rows, rejects = [], []
for p in sorted(SHARDS.glob("*.csv")):
    if p.name in ("HEADER.csv", "_exclusions.csv"):
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
            for e in EXCL:
                if e["agency_contains"].lower() in r["agency"].lower():
                    reasons.append(f"excluded: {e['entity_or_reason'][:80]}")
            if not r["agency"]:
                reasons.append("no agency")
            if r["scope_type"] not in SCOPES:
                reasons.append(f"bad scope_type {r['scope_type']!r}")
            has_num = any(num(r[c]) is not None for c in NUMERIC)
            if has_num and not (r["source_url_1"].startswith("http") or r["source_url_1"].startswith("bleecker-drive:")):
                reasons.append("number without source_url_1")
            if r["signed_after_2025_12_16"] not in ("", "0", "1", "TRUE", "FALSE", "true", "false"):
                reasons.append("bad signed_after flag")
            (rejects if reasons else rows).append(dict(r, _reason="; ".join(reasons)))

seen, deduped, conflicts = {}, [], {}
for r in rows:
    k = (r["agency"].lower(), r["contract_action"].lower(), r["award_or_approval_date"])
    if k in seen:
        old = seen[k]
        if r["scope_type"] != old["scope_type"] and "Unknown" not in (r["scope_type"], old["scope_type"]):
            conflicts.setdefault(k, {old["scope_type"], }).add(r["scope_type"])
        # keep the row with more filled numeric fields; a classified row beats Unknown
        better = (sum(num(r[c]) is not None for c in NUMERIC) + (r["scope_type"] != "Unknown")) > \
                 (sum(num(old[c]) is not None for c in NUMERIC) + (old["scope_type"] != "Unknown"))
        if better:
            deduped[deduped.index(old)] = r
            seen[k] = r
        continue
    seen[k] = r
    deduped.append(r)
for r in deduped:
    k = (r["agency"].lower(), r["contract_action"].lower(), r["award_or_approval_date"])
    if k in conflicts:
        r["_scope_conflict"] = "/".join(sorted(conflicts[k]))

with open(OUT / "via_contract_census.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=HEADER, extrasaction="ignore")
    w.writeheader()
    w.writerows(deduped)
with open(OUT / "rejects.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=HEADER + ["_shard", "_reason"], extrasaction="ignore")
    w.writeheader()
    w.writerows(rejects)
log(f"accepted {len(deduped)} (from {len(rows)}, {len(rows) - len(deduped)} dupes), rejected {len(rejects)}")

# QA flags for Tier-3 review (do not reject; list in out/qa_flags.csv)
flagged = []
for r in deduped:
    fl = []
    t, a, y = num(r["total_value_usd"]), num(r["annual_value_usd"]), num(r["term_years_incl_options"])
    if t and a and y and abs(t - a * y) <= 0.01 * t:
        fl.append("total looks derived (= annual x years)")
    if t and re.search(r"/\s*(year|yr)|per year|annually", r["notes"], re.I) and not a:
        fl.append("notes mention per-year amount but annual_value blank; total may be derived")
    if t and t >= 50_000_000:
        fl.append("total >= $50mm: verify against source")
    if not r["award_or_approval_date"]:
        fl.append("no date")
    if r["scope_type"] == "Turnkey" and r["pricing_basis"] in ("", "not stated") and r["drivers_supplied_by"] in ("", "not stated"):
        fl.append("Turnkey without pricing basis or driver source stated")
    if r.get("_scope_conflict"):
        fl.append(f"scope conflict across shards: {r['_scope_conflict']}")
    if r["scope_type"] == "Unknown" and (t or 0) >= 1_000_000:
        fl.append("Unknown scope on a >= $1mm action: adjudicate")
    if fl:
        flagged.append(dict(r, _flags="; ".join(fl)))
with open(OUT / "qa_flags.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=HEADER + ["_shard", "_flags"], extrasaction="ignore")
    w.writeheader()
    w.writerows(flagged)
log(f"qa flags: {len(flagged)} rows -> out/qa_flags.csv")

# mix summary over Via's own contract actions only (exclude competitor awards and app-only observations)
via_rows = [r for r in deduped if r["contract_action"] not in ("competitor-award", "deployment-observed")]
log(f"rows: {len(deduped)} total = {len(via_rows)} Via actions + "
    f"{sum(1 for r in deduped if r['contract_action'] == 'competitor-award')} competitor awards + "
    f"{sum(1 for r in deduped if r['contract_action'] == 'deployment-observed')} app-only observations")
cnt = Counter(r["scope_type"] for r in via_rows)
dollars = defaultdict(float)
for r in via_rows:
    a = num(r["annual_value_usd"])
    if a is None:
        t, y = num(r["total_value_usd"]), num(r["term_years_incl_options"])
        a = t / y if (t and y) else None
    if a:
        dollars[r["scope_type"]] += a
post = [r for r in via_rows if r["signed_after_2025_12_16"] in ("1", "TRUE", "true")]
log(f"count-weighted: {dict(cnt)}")
log(f"annualized $ by scope: { {k: round(v / 1e6, 1) for k, v in dollars.items()} } ($mm, rows with values only)")
log(f"post-2025-12-16 rows: {len(post)} -> {dict(Counter(r['scope_type'] for r in post))}")
