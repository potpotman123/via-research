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
    """Parse a money/number cell. Accepts $ and commas, 'M'/'million' and 'K' suffixes, ranges take the first value.
    Returns None for blank or unparsable text."""
    s = (v or "").strip().replace("$", "").replace(",", "")
    if not s:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*(million|mm|m|k|thousand)?\b", s, re.I)
    if not m:
        return None
    x = float(m.group(1))
    suf = (m.group(2) or "").lower()
    if suf in ("million", "mm", "m"):
        x *= 1e6
    elif suf in ("k", "thousand"):
        x *= 1e3
    return x


def normalize_numeric(r):
    """Rewrite numeric cells to plain digits; return list of cells that could not be parsed."""
    bad = []
    for c in NUMERIC:
        raw = r.get(c, "")
        if not raw.strip():
            continue
        x = num(raw)
        if x is None:
            bad.append(c)
            continue
        if re.search(r"[A-Za-z]", raw):
            r["notes"] = (r["notes"] + f" [numeric normalized: {c} {raw!r} -> {x:g}]").strip()
        r[c] = str(int(x)) if x == int(x) else f"{x:.2f}".rstrip("0").rstrip(".")
    return bad


EXCL = []
if (SHARDS / "_exclusions.csv").exists():
    EXCL = list(csv.DictReader(open(SHARDS / "_exclusions.csv")))

rows, rejects = [], []
for p in sorted(SHARDS.glob("*.csv")):
    if p.name in ("HEADER.csv", "_exclusions.csv", "_corrections.csv"):
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
            bad_cells = normalize_numeric(r)
            if bad_cells:
                reasons.append("unparsable numeric: " + ",".join(bad_cells))
            has_num = any(num(r[c]) is not None for c in NUMERIC)
            if has_num and not (r["source_url_1"].startswith("http") or r["source_url_1"].startswith("bleecker-drive:")):
                reasons.append("number without source_url_1")
            if r["signed_after_2025_12_16"] not in ("", "0", "1", "TRUE", "FALSE", "true", "false"):
                reasons.append("bad signed_after flag")
            (rejects if reasons else rows).append(dict(r, _reason="; ".join(reasons)))

# agency canonicalization: strip parentheticals and slashes, apply alias table, so dedupe and per-agency views line up
ALIASES = {
    "los angeles metropolitan transportation authority": "Los Angeles County Metropolitan Transportation Authority",
    "los angeles county metropolitan transportation authority": "Los Angeles County Metropolitan Transportation Authority",
    "fresno": "City of Fresno", "volusia county": "County of Volusia", "town of wilson": "City of Wilson",
    "trinity metro": "Trinity Metro (Fort Worth Transportation Authority)",
    "douglas county board of county commissioners": "Douglas County", "douglas county": "Douglas County",
    "regional metropolitan transit authority of omaha": "Regional Metropolitan Transit Authority of Omaha (Metro)",
    "region 4 education service center": "Region 4 Education Service Center (OMNIA Partners lead agency)",
    "utah transit authority": "Utah Transit Authority", "metropolitan council": "Metropolitan Council (Metro Transit)",
    "capital metropolitan transportation authority": "Capital Metropolitan Transportation Authority (CapMetro)",
    "denton county transportation authority": "Denton County Transportation Authority (DCTA)",
    "district department of transportation": "District Department of Transportation (DDOT)",
    "imperial county transportation commission": "Imperial County Transportation Commission (ICTC)",
    "maryland transit administration": "Maryland Transit Administration", "stark area regional transit authority": "Stark Area Regional Transit Authority (SARTA)",
    "state of north dakota": "State of North Dakota", "city of fargo": "City of Fargo (Metropolitan Area Transit)",
    "sacramento regional transit district": "Sacramento Regional Transit District (SacRT)",
}


def agency_key(name):
    base = re.sub(r"\(.*?\)", "", name).split(" / ")[0].split(" & ")[0]
    base = re.sub(r"[^a-z0-9 ]", " ", base.lower())
    return re.sub(r"\s+", " ", base).strip()


for r in rows:
    k = agency_key(r["agency"])
    if k in ALIASES:
        r["agency"] = ALIASES[k]
    # deterministic relabel: rows whose notes identify a competitor's contract are competitor awards
    if r["contract_action"] != "competitor-award" and re.search(r"\bcompetitor\b|RideCo, Inc\.|Spare Labs, Inc\.", r["notes"]) \
            and not re.search(r"NoMad|Nomad|River North|Via Mobility, LLC|Crosby|Tidewater|Port City", r["notes"][:400]) \
            and re.search(r"RideCo|Spare", r["notes"][:300]):
        r["notes"] = f"[relabeled competitor-award from {r['contract_action']}] " + r["notes"]
        r["contract_action"] = "competitor-award"

seen, deduped, conflicts = {}, [], {}


def value_bucket(r):
    """Distinguish same-day actions with materially different totals (e.g., LA Metro North vs South awards)."""
    t = num(r["total_value_usd"])
    return int(round(t / 1e5)) if t else ""


for r in rows:
    k = (agency_key(r["agency"]), r["contract_action"].lower(), r["award_or_approval_date"])
    if k in seen and seen[k]["total_value_usd"] and r["total_value_usd"]:
        t_old, t_new = num(seen[k]["total_value_usd"]), num(r["total_value_usd"])
        if t_old and t_new and abs(t_old - t_new) > 0.05 * max(t_old, t_new):
            k = k + (value_bucket(r),)  # distinct action on the same day
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
# fold undated rows into a dated row of the same agency/action/total (same document seen twice, one copy without a date)
dated = {}
for r in deduped:
    if r["award_or_approval_date"] and r["total_value_usd"]:
        dated[(agency_key(r["agency"]), r["contract_action"].lower(), value_bucket(r))] = r
before = len(deduped)
kept = []
for r in deduped:
    if not r["award_or_approval_date"] and r["total_value_usd"]:
        twin = dated.get((agency_key(r["agency"]), r["contract_action"].lower(), value_bucket(r)))
        if twin is not None and twin is not r:
            if not twin["source_url_2"] and r["source_url_1"] != twin["source_url_1"]:
                twin["source_url_2"] = r["source_url_1"]
            continue
    kept.append(r)
deduped = kept
log(f"undated twins folded into dated rows: {before - len(deduped)}")

for r in deduped:
    k = (agency_key(r["agency"]), r["contract_action"].lower(), r["award_or_approval_date"])
    if k in conflicts:
        r["_scope_conflict"] = "/".join(sorted(conflicts[k]))

# Tier-3 corrections (shards/_corrections.csv): agency_contains, contract_action, award_or_approval_date, field, new_value, reason
CORR = list(csv.DictReader(open(SHARDS / "_corrections.csv"))) if (SHARDS / "_corrections.csv").exists() else []
n_corr = 0
for c in CORR:
    for r in deduped:
        if (c["agency_contains"].lower() in r["agency"].lower() and (not c["contract_action"] or r["contract_action"] == c["contract_action"])
                and (not c["award_or_approval_date"] or r["award_or_approval_date"] == c["award_or_approval_date"])):
            old = r.get(c["field"], "")
            r[c["field"]] = c["new_value"]
            r["notes"] = (r["notes"] + f" [T3 correction: {c['field']} {old!r} -> {c['new_value']!r}: {c['reason']}]").strip()
            n_corr += 1
log(f"tier-3 corrections applied: {n_corr}")

# recompute the post-report flag deterministically from dates (agents set it inconsistently)
n_flag = 0
for r in deduped:
    d = r["award_or_approval_date"] or r["term_start"]
    if re.match(r"^\d{4}-\d{2}(-\d{2})?", d or ""):
        new = "1" if d[:10] > "2025-12-16" else "0"
        if r["signed_after_2025_12_16"] != new:
            n_flag += 1
        r["signed_after_2025_12_16"] = new
log(f"post-report flags recomputed from dates: {n_flag} changed")

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
