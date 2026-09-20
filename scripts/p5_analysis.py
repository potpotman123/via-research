"""Phase 5: analysis tables from out/via_contract_census.csv -> out/analysis_summary.md
Sections: mix (count- and dollar-weighted), post-2025-12-16 actions, losses/churn, turnkey hourly rates, software fees,
implementation fee ratios, Downtowner pre-acquisition, Unknown-scope dollars still to adjudicate."""
import csv
import re
from collections import Counter, defaultdict

from common import ROOT, log

OUT = ROOT / "out"
rows = list(csv.DictReader(open(OUT / "via_contract_census.csv")))


def num(v):
    v = (v or "").replace("$", "").replace(",", "").strip()
    try:
        return float(re.sub(r"[^\d.\-]", "", v)) if v else None
    except ValueError:
        return None


def annual(r):
    a = num(r["annual_value_usd"])
    if a is not None:
        return a
    t, y = num(r["total_value_usd"]), num(r["term_years_incl_options"])
    return t / y if (t and y) else None


via = [r for r in rows if r["contract_action"] not in ("competitor-award", "deployment-observed")]
comp = [r for r in rows if r["contract_action"] == "competitor-award"]
obs = [r for r in rows if r["contract_action"] == "deployment-observed"]
dt_pre = [r for r in via if r["notes"].lower().startswith("downtowner, pre-acquisition") or "pre-acquisition" in r["notes"].lower()[:60]]
organic = [r for r in via if r not in dt_pre]
L = ["# VIA contract census: analysis summary", "", f"Generated from out/via_contract_census.csv: {len(rows)} rows = {len(via)} Via contract actions "
     f"({len(dt_pre)} Downtowner pre-acquisition) + {len(comp)} competitor awards + {len(obs)} app-only observations.", ""]

# 1. mix
L += ["## 1. Scope mix (Via contract actions, excl. Downtowner pre-acquisition)", "",
      "| Scope | Actions (count) | Distinct agencies | Rows with $ | Annualized $mm (rows with $) |", "|---|---|---|---|---|"]
tot_c = tot_d = 0
for s in ("Turnkey", "Hybrid", "Software-only", "Unknown"):
    rs = [r for r in organic if r["scope_type"] == s]
    d = [annual(r) for r in rs if annual(r)]
    tot_c += len(rs)
    tot_d += sum(d)
    L.append(f"| {s} | {len(rs)} | {len({r['agency'].lower() for r in rs})} | {len(d)} | {sum(d) / 1e6:,.1f} |")
L.append(f"| **Total** | **{tot_c}** | **{len({r['agency'].lower() for r in organic})}** | | **{tot_d / 1e6:,.1f}** |")
known = [r for r in organic if r["scope_type"] != "Unknown" and annual(r)]
kd = defaultdict(float)
for r in known:
    kd[r["scope_type"]] += annual(r)
if kd:
    tk = sum(kd.values())
    L += ["", "Dollar-weighted shares among rows with a value and a known scope (annualized; NTE ceilings treated as annual where the "
          "document gave only a ceiling and a term, so this overstates spend): " +
          ", ".join(f"{k} {v / tk:.0%}" for k, v in sorted(kd.items(), key=lambda x: -x[1])), ""]
L += ["Caveats: the table above sums every action, so an agency with eight renewals counts eight times. It shows where the documented "
      "dollars sit, not a run-rate. Many software rows carry no dollar value (fees under council approval thresholds).", ""]

# 1b. run-rate view: one value per agency = latest dated action with an annualizable value (excl. terminations)
latest = {}
for r in organic:
    if r["contract_action"] in ("termination", "non-renewal", "budget-exclusion"):
        continue
    a = annual(r)
    if not a:
        continue
    k = r["agency"].lower()
    d = r["award_or_approval_date"] or r["term_start"] or ""
    if k not in latest or d > latest[k][0]:
        latest[k] = (d, a, r)
L += ["## 1b. Run-rate view: latest priced action per agency (excl. terminations)", "",
      "| Scope | Agencies | Annualized $mm | Share of $ | Median $mm |", "|---|---|---|---|---|"]
rr = defaultdict(list)
for d, a, r in latest.values():
    rr[r["scope_type"]].append(a)
tot_rr = sum(sum(v) for v in rr.values())
for s in ("Turnkey", "Hybrid", "Software-only", "Unknown"):
    v = sorted(rr.get(s, []))
    if v:
        L.append(f"| {s} | {len(v)} | {sum(v) / 1e6:,.1f} | {sum(v) / tot_rr:.0%} | {v[len(v) // 2] / 1e6:,.2f} |")
L.append(f"| **Total** | **{sum(len(v) for v in rr.values())}** | **{tot_rr / 1e6:,.1f}** | | |")
kn = {s: sum(v) for s, v in rr.items() if s != "Unknown"}
if kn:
    L.append("")
    L.append("Excluding Unknown: " + ", ".join(f"{s} {v / sum(kn.values()):.0%}" for s, v in sorted(kn.items(), key=lambda x: -x[1])))
L += ["", "Method: annual_value_usd if stated, else total_value_usd / term_years_incl_options; rows lacking both are excluded, so this "
      "understates the software tail (small subscriptions often lack a stated term). Ceilings (NTE) are treated as the annual figure when "
      "the document states them per year, which overstates actual spend.", ""]
L += ["Top 15 agencies by run-rate:", "", "| Agency | State | Scope | Latest action date | Annualized $mm | Basis |", "|---|---|---|---|---|---|"]
for d, a, r in sorted(latest.values(), key=lambda x: -x[1])[:15]:
    L.append(f"| {r['agency'][:40]} | {r['state']} | {r['scope_type']} | {d} | {a / 1e6:,.1f} | {r['pricing_basis'][:22]} |")
L.append("")

# 2. post-Bleecker
post = [r for r in via if r["signed_after_2025_12_16"] in ("1", "TRUE", "true")]
post.sort(key=lambda r: r["award_or_approval_date"] or r["term_start"] or "9")
L += ["## 2. Actions dated after 2025-12-16 (Bleecker report date)", "",
      "| Date | Agency | State | Action | Scope | Total $ | Annual $ | $/hr | Basis | Src | Conf | Notes |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in post:
    L.append(f"| {r['award_or_approval_date'] or r['term_start']} | {r['agency'][:40]} | {r['state']} | {r['contract_action']} | {r['scope_type']} | "
             f"{r['total_value_usd']} | {r['annual_value_usd']} | {r['hourly_rate_usd']} | {r['pricing_basis'][:18]} | {r['source_type'][:8]} | {r['confidence']} | "
             f"{r['notes'][:140].replace('|', '/')} |")
pc = Counter(r["scope_type"] for r in post)
L += ["", f"Post-report mix by count: {dict(pc)}. Annualized $ by scope: " +
      str({k: round(v / 1e6, 1) for k, v in {s: sum(annual(r) or 0 for r in post if r['scope_type'] == s) for s in pc}.items()}) + " ($mm)", ""]

# 3. losses / churn
loss_actions = {"termination", "non-renewal", "budget-exclusion"}
losses = [r for r in via if r["contract_action"] in loss_actions] + comp
losses.sort(key=lambda r: r["award_or_approval_date"] or "9")
L += ["## 3. Losses, terminations, budget exclusions and competitor awards", "",
      "| Date | Agency | State | Action | Scope | $ | Notes |", "|---|---|---|---|---|---|---|"]
for r in losses:
    L.append(f"| {r['award_or_approval_date']} | {r['agency'][:40]} | {r['state']} | {r['contract_action']} | {r['scope_type']} | {r['total_value_usd']} | {r['notes'][:150].replace('|', '/')} |")
L.append("")

# 4. turnkey hourly rates
hr = [(num(r["hourly_rate_usd"]), r) for r in via if num(r["hourly_rate_usd"])]
hr = [(h, r) for h, r in hr if 20 <= h <= 400]
hr.sort(key=lambda x: x[0])
L += ["## 4. Stated per-hour rates (turnkey / operations)", "", "| $/hr | Agency | State | Date | Basis | Scope |", "|---|---|---|---|---|---|"]
for h, r in hr:
    L.append(f"| {h:,.2f} | {r['agency'][:40]} | {r['state']} | {r['award_or_approval_date']} | {r['pricing_basis'][:22]} | {r['scope_type']} |")
if hr:
    vals = [h for h, _ in hr]
    L += ["", f"n={len(vals)}, min {min(vals):,.2f}, median {sorted(vals)[len(vals) // 2]:,.2f}, max {max(vals):,.2f}. "
          "OMNIA R250802 list: microtransit turnkey $50.47-$80.75/vehicle hour, paratransit $60.56-$100.94, fixed route $90.85-$141.32 (net).", ""]

# 5. software fees + implementation
sw = [r for r in via if num(r["software_fee_usd"])]
L += ["## 5. Stated software fees and implementation fees", "", "| Agency | State | Date | Software fee | Basis | Implementation fee | Impl % yr1 | Scope |", "|---|---|---|---|---|---|---|---|"]
for r in sorted(sw, key=lambda r: r["agency"]):
    L.append(f"| {r['agency'][:40]} | {r['state']} | {r['award_or_approval_date']} | {r['software_fee_usd']} | {r['software_fee_basis'][:24]} | {r['implementation_fee_usd']} | {r['implementation_fee_pct_of_year1']} | {r['scope_type']} |")
impl = [num(r["implementation_fee_pct_of_year1"]) for r in via if num(r["implementation_fee_pct_of_year1"])]
L += ["", f"Implementation fee as % of year-1 fees where both were stated: n={len(impl)}" + (f", range {min(impl):.0f}%-{max(impl):.0f}%" if impl else ""),
      "OMNIA list: microtransit software installation $27,758.50 (<=20 vehicles) / $37,852.50 (>20); per vehicle per month tiers $1,514.10 (vehicle 1) "
      "down to $302.82 (vehicles 21+). Example 10-vehicle fleet: monthly software = 1,514.10+504.70+252.35+151.41+100.94+5x353.29 = $4,289.95 "
      "-> $51,479/yr; installation $27,758.50 = 54% of year-1 software fees.", ""]

# 6. Downtowner pre-acquisition
L += ["## 6. Downtowner (pre-acquisition) actions captured", ""]
for r in dt_pre:
    L.append(f"- {r['award_or_approval_date']} {r['agency']} ({r['state']}): {r['contract_action']}, {r['scope_type']}, total {r['total_value_usd']}, annual {r['annual_value_usd']}")
L.append("")

# 7. Unknown-scope dollars to adjudicate
unk = sorted([r for r in via if r["scope_type"] == "Unknown" and annual(r)], key=lambda r: -annual(r))
L += ["## 7. Unknown-scope actions with dollars (Tier-3 adjudication queue)", "", "| Annualized $mm | Agency | Date | Action | Total | Notes |", "|---|---|---|---|---|---|"]
for r in unk[:40]:
    L.append(f"| {annual(r) / 1e6:,.1f} | {r['agency'][:40]} | {r['award_or_approval_date']} | {r['contract_action']} | {r['total_value_usd']} | {r['notes'][:120].replace('|', '/')} |")
(OUT / "analysis_summary.md").write_text("\n".join(L))
log(f"wrote out/analysis_summary.md: {len(via)} Via actions, {len(post)} post-report, {len(losses)} losses/competitor rows, {len(hr)} hourly rates, {len(sw)} software-fee rows, {len(unk)} Unknown with $")
