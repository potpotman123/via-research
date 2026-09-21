"""Phase 7: stratified bottom-up build of Via's US public-sector revenue from the census + NTD, for the SOTP model.
Layers (each row tagged): 1 NTD-paid operators (actual RY2024 payments, grown); 2 census-priced operations contracts not in NTD
(ceiling x haircut, prorated by start); 3 documented operations agencies with no price (imputed); 4 app-only agencies (probability-weighted);
5 documented software agencies (ACV where stated, imputed otherwise); 6 Remix/unenumerated software (imputed count x ACV); 7 Downtowner (range).
Assumptions are constants below and are written into the output. Output: out/us_revenue_build.csv and a summary printed."""
import csv, re
from collections import defaultdict
from common import ROOT, log

HAIRCUT = 0.80          # NTD payments / census ceiling; re-estimate from the overlap pairs printed at the end (2026-09-21: 26 NTD agencies)
ESC = 0.04              # annual escalator on operations contracts (UTA per-hour rates rose $55.23 -> $68.33 over 2022-24)
NTD_GROWTH_2025 = 0.10  # NTD Via agencies' DR/PT hours grew ~10% median 2024->2025 (Sarasota +12%, Volusia +29%, HRT +10%, Suffolk +3%)
NTD_GROWTH_2026 = 0.08  # Jan-Jul 2026 vs 2025 median across the same agencies (range -29% to +78%)
IMPUTE_OPS_NO_PRICE = 900_000     # documented turnkey agency, no stated price: median of small NTD-paid operators RY2024 (BJCTA 0.59, Worcester 0.61, Norman 0.70, Valdosta 0.86, Muskegon 1.05, Volusia 1.68, Suffolk 1.70, Green Bay 1.91)
APPONLY_P_TURNKEY = 0.30          # share of app-only agencies assumed Via-operated (documented app agencies ~45% turnkey; undocumented skew small/software)
APPONLY_OPS_SIZE = 800_000        # small operations contract
APPONLY_SW_SIZE = 60_000          # small software subscription
SW_IMPUTE_ACV = 60_000            # documented software agency without a stated fee
REMIX_UNENUMERATED = 250          # Remix said 350+ cities in 2021; ~60 Remix/software agencies are documented; remainder assumed still active
REMIX_ACV = 30_000                # OMNIA Remix annual minimums $18,690-$28,930; documented Remix fees $11k-$84k
DOWNTOWNER = (15_000_000, 35_000_000)   # undisclosed; 10-K: pro forma not material; spec base 25

def num(v):
    s = (v or "").replace("$", "").replace(",", "").strip(); m = re.search(r"\d+(?:\.\d+)?", s); return float(m.group(0)) if m else None

rows = list(csv.DictReader(open(ROOT / "out/via_contract_census.csv")))
via = [r for r in rows if r["contract_action"] not in ("competitor-award", "deployment-observed")]
def annual(r):
    a = num(r["annual_value_usd"])
    if a: return a
    t = num(r["total_value_usd"]); y = num(r["term_years_incl_options"]); return t / y if (t and y) else None

# latest priced OPERATIONS action per agency (ignore software fee amendments when picking the ops run-rate)
ops_latest, sw_latest, scopes = {}, {}, defaultdict(set)
for r in via:
    k = r["agency"].lower(); scopes[k].add(r["scope_type"])
    if r["contract_action"] in ("termination", "non-renewal", "budget-exclusion"): continue
    a = annual(r)
    if not a: continue
    d = r["award_or_approval_date"] or r["term_start"] or ""
    if r["scope_type"] in ("Turnkey", "Hybrid") and a >= 200_000:
        # concurrent same-day awards (LA Metro North + South) are summed; a later date replaces the group
        if k not in ops_latest or d > ops_latest[k][0]: ops_latest[k] = (d, a, r)
        elif d == ops_latest[k][0] and abs(a - ops_latest[k][1]) > 0.05 * max(a, ops_latest[k][1]) and r["total_value_usd"] != ops_latest[k][2]["total_value_usd"]:
            ops_latest[k] = (d, ops_latest[k][1] + a, ops_latest[k][2])
    elif r["scope_type"] == "Software-only" or (r["scope_type"] == "Unknown" and a < 200_000):
        if k not in sw_latest or d > sw_latest[k][0]: sw_latest[k] = (d, a, r)

ntd = defaultdict(float); ntd_name = {}; ntd_months = {}; ntd_voms = defaultdict(float)
VOMS_CAP = 160_000      # cap on annualizing partial-year NTD rows: revenue per contracted vehicle-year (NTD RY2024: $96.8mm / 632 VOMS = $153k)
for h in csv.DictReader(open(ROOT / "text/enum/ntd_contractual_hits.csv")):
    op = (h.get("Contractee Operator Name") or h.get("Contractee Company Name") or "")
    if h["year"] == "2024" and h.get("seller_kind") == "via" and not re.search(r"downtowner", op, re.I):   # Downtowner is layer 7
        ag = h["Agency Name"].strip(); ntd[ag] += float(h.get("Direct Payment/Agency Subsidy") or 0); ntd_name[ag] = op
        m = int(float(h.get("Months Seller Operated in FY") or 12) or 12); ntd_months[ag] = max(ntd_months.get(ag, 0), m); ntd_voms[ag] += float(h.get("VOMS Under Contract") or 0)
NTD_MAP = {"City of Arlington": "city of arlington", "Sarasota County": "sarasota county", "Ben Franklin Transit": "ben franklin transit",
           "Pierce County Transportation Benefit Area Authority": "pierce transit", "Transportation District Commission of Hampton Roads": "hampton roads transit",
           "City of Grand Prairie": "city of grand prairie", "County of Volusia": "county of volusia", "City of Sioux Falls": "sioux falls", "Suffolk County": "suffolk county",
           "Lorain County": "lorain county", "City of Valdosta": "city of valdosta", "County of Muskegon": "muskegon", "Worcester Regional Transit Authority": "worcester",
           "City of Norman": "city of norman", "Snohomish County Public Transportation Benefit Area Corporation": "community transit",
           "Denton County Transportation Authority": "denton county", "Utah Transit Authority": "utah transit", "King County": "king county",
           "Bi-State Development Agency of the Missouri-Illinois Metropolitan District": "bi-state", "Capital Area Transit System": "capital area transit",
           "Toledo Area Regional Transit Authority": "toledo", "City of Green Bay": "green bay", "Stark Area Regional Transit Authority": "stark area",
           "Birmingham-Jefferson County Transit Authority": "birmingham", "Milwaukee County": "milwaukee county", "Ann Arbor Area Transportation Authority": "ann arbor"}
l1_tokens = set(NTD_MAP.values())
out = []
def add(**k): out.append(k)
used = set()
# Layer 1: NTD-paid operators
for ag, paid in sorted(ntd.items(), key=lambda x: -x[1]):
    key = NTD_MAP.get(ag, ag.lower()); hit = next(((k, v) for k, v in ops_latest.items() if key in k), None)
    for k in scopes:                       # any census row for this agency is now covered by layer 1 (prevents layers 3/4 re-adding it)
        if key in k: used.add(k)
    months = ntd_months.get(ag, 12); base = paid
    note = f"NTD RY2024 direct payment to {ntd_name[ag]}"
    if 0 < months < 12:
        base = min(paid * 12 / months, ntd_voms[ag] * VOMS_CAP) if ntd_voms[ag] else paid * 12 / months
        note += f"; {months} months in FY, annualized to {base:,.0f} (capped at VOMS x {VOMS_CAP:,.0f})"
    y25 = base * (1 + NTD_GROWTH_2025); y26 = y25 * (1 + NTD_GROWTH_2026); y27 = y26 * (1 + ESC)
    if any(r["agency"].lower().find(key) >= 0 and r["contract_action"] in ("termination", "non-renewal") for r in via):
        y25 = y26 = y27 = 0.0; note += "; census termination -> zero from 2025"
    if hit:
        used.add(hit[0]); d, a, r = hit[1]
        # if a newer, larger contract exists (e.g., HRT 10/2025 $2.95mm), let it lift 2026-27
        if d >= "2025-01-01" and a * HAIRCUT > y26: y26 = max(y26, a * HAIRCUT * (0.5 if d >= "2026-01-01" else 1.0)); y27 = a * HAIRCUT * (1 + ESC); note += f"; census {r['contract_action']} {d} run-rate {a:,.0f} x {HAIRCUT} lifts 2026-27"
    add(layer="1 NTD-paid operations", agency=ag, state="", scope="Turnkey", basis=note, y2024=paid, y2025=y25, y2026=y26, y2027=y27, p=1.0)
# Layer 2: census-priced operations contracts not covered by NTD
for k, (d, a, r) in sorted(ops_latest.items(), key=lambda x: -x[1][1]):
    if k in used: continue
    rr = a * HAIRCUT; start = r["term_start"] or d
    frac26 = 1.0
    if start[:4] == "2026" and len(start) >= 7: frac26 = max(0.0, (12 - int(start[5:7]) + 1) / 12)
    y25 = rr if start < "2025-07" else (rr * 0.5 if start < "2026" else 0.0)
    frac24 = 1.0 if start[:4] < "2024" else (max(0.0, (12 - int(start[5:7]) + 1) / 12) if start[:4] == "2024" and len(start) >= 7 else 0.0)
    add(layer="2 census-priced operations", agency=r["agency"], state=r["state"], scope=r["scope_type"],
        basis=f"census {r['contract_action']} {d}: run-rate {a:,.0f} x haircut {HAIRCUT}; start {start or 'n/a'}", y2024=rr * frac24, y2025=y25, y2026=rr * frac26, y2027=rr * (1 + ESC), p=1.0)
    used.add(k)
# Layer 3: documented turnkey agencies with no usable price
for k, s in scopes.items():
    if k in used or "Turnkey" not in s and "Hybrid" not in s: continue
    if any(k in u or u in k for u in used): continue
    name = next(r["agency"] for r in via if r["agency"].lower() == k); st = next(r["state"] for r in via if r["agency"].lower() == k)
    ended = any(r["agency"].lower() == k and r["contract_action"] in ("termination", "non-renewal") for r in via)
    if ended: continue
    add(layer="3 documented operations, no price", agency=name, state=st, scope="Turnkey", basis=f"imputed {IMPUTE_OPS_NO_PRICE:,.0f} (small documented operator)",
        y2024=IMPUTE_OPS_NO_PRICE, y2025=IMPUTE_OPS_NO_PRICE, y2026=IMPUTE_OPS_NO_PRICE * (1 + ESC), y2027=IMPUTE_OPS_NO_PRICE * (1 + ESC) ** 2, p=1.0); used.add(k)
# Layer 5: documented software agencies
for k, (d, a, r) in sw_latest.items():
    if k in used: continue
    ended = any(x["agency"].lower() == k and x["contract_action"] in ("termination", "non-renewal") for x in via)
    if ended: continue
    add(layer="5 documented software (priced)", agency=r["agency"], state=r["state"], scope="Software-only", basis=f"census {r['contract_action']} {d}: annualized fee {a:,.0f}",
        y2024=a, y2025=a, y2026=a * 1.03, y2027=a * 1.03 ** 2, p=1.0); used.add(k)
n_sw_unpriced = 0
for k, s in scopes.items():
    if k in used or "Software-only" not in s: continue
    if any(x["agency"].lower() == k and x["contract_action"] in ("termination", "non-renewal") for x in via): continue
    name = next(r["agency"] for r in via if r["agency"].lower() == k); st = next(r["state"] for r in via if r["agency"].lower() == k)
    add(layer="5 documented software (imputed)", agency=name, state=st, scope="Software-only", basis=f"imputed ACV {SW_IMPUTE_ACV:,.0f}", y2024=SW_IMPUTE_ACV, y2025=SW_IMPUTE_ACV, y2026=SW_IMPUTE_ACV, y2027=SW_IMPUTE_ACV, p=1.0)
    used.add(k); n_sw_unpriced += 1
# Layer 4: app-only agencies (from targets with no document)
t = list(csv.DictReader(open(ROOT / "text/enum/targets.csv")))
def documented(ag):
    a = ag.lower(); return any(a[:20] in k or k[:20] in a for k in scopes) or any(tok in a for tok in l1_tokens)
apponly = [x for x in t if not documented(x["agency"]) and x["state"]]
for x in apponly:
    exp = APPONLY_P_TURNKEY * APPONLY_OPS_SIZE + (1 - APPONLY_P_TURNKEY) * APPONLY_SW_SIZE
    add(layer="4 app-only (probability-weighted)", agency=x["agency"], state=x["state"], scope="Unknown",
        basis=f"{APPONLY_P_TURNKEY:.0%} x {APPONLY_OPS_SIZE:,.0f} ops + {1-APPONLY_P_TURNKEY:.0%} x {APPONLY_SW_SIZE:,.0f} software", y2024=exp, y2025=exp, y2026=exp, y2027=exp, p=APPONLY_P_TURNKEY)
# Layer 6: Remix / unenumerated software
rem = REMIX_UNENUMERATED * REMIX_ACV
add(layer="6 Remix/unenumerated software", agency=f"~{REMIX_UNENUMERATED} Remix cities not in census", state="", scope="Software-only", basis=f"{REMIX_UNENUMERATED} x {REMIX_ACV:,.0f}", y2024=rem, y2025=rem, y2026=rem, y2027=rem, p=0.0)
# Layer 7: Downtowner
mid = sum(DOWNTOWNER) / 2
add(layer="7 Downtowner (acquired 2025-12-12)", agency="Downtowner LLCs (~94 towns)", state="", scope="Turnkey", basis=f"range {DOWNTOWNER[0]:,.0f}-{DOWNTOWNER[1]:,.0f}; pre-acquisition revenue not Via's", y2024=0.0, y2025=mid * 19 / 365, y2026=mid, y2027=mid * (1 + ESC), p=1.0)

fields = ["layer", "agency", "state", "scope", "basis", "y2024", "y2025", "y2026", "y2027", "p"]
with open(ROOT / "out/us_revenue_build.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
    for o in out: w.writerow({k: (f"{v:.0f}" if isinstance(v, float) else v) for k, v in o.items()})
# summary
tot = defaultdict(lambda: defaultdict(float)); cnt = defaultdict(int)
for o in out:
    for y in ("y2024", "y2025", "y2026", "y2027"): tot[o["layer"]][y] += o[y]
    cnt[o["layer"]] += 1
log("US public-sector revenue build ($mm)")
log(f"{'layer':40} | {'n':>4} | {'2024':>7} | {'2025':>7} | {'2026E':>7} | {'2027E':>7}")
G = defaultdict(float)
for L in sorted(tot):
    v = tot[L]; log(f"{L:40} | {cnt[L]:4} | {v['y2024']/1e6:7.1f} | {v['y2025']/1e6:7.1f} | {v['y2026']/1e6:7.1f} | {v['y2027']/1e6:7.1f}")
    for y in v: G[y] += v[y]
log(f"{'TOTAL documented + imputed US':40} | {len(out):4} | {G['y2024']/1e6:7.1f} | {G['y2025']/1e6:7.1f} | {G['y2026']/1e6:7.1f} | {G['y2027']/1e6:7.1f}")
ops = {y: sum(o[y] for o in out if o["scope"] in ("Turnkey", "Hybrid")) + sum(o[y] * o["p"] for o in out if o["layer"].startswith("4")) for y in ("y2024", "y2025", "y2026", "y2027")}
sw = {y: G[y] - ops[y] for y in ops}
log(f"of which operations (turnkey+hybrid+app-only ops share): 2024 {ops['y2024']/1e6:.1f} | 2025 {ops['y2025']/1e6:.1f} | 2026E {ops['y2026']/1e6:.1f} | 2027E {ops['y2027']/1e6:.1f}")
log(f"of which software:                                      2024 {sw['y2024']/1e6:.1f} | 2025 {sw['y2025']/1e6:.1f} | 2026E {sw['y2026']/1e6:.1f} | 2027E {sw['y2027']/1e6:.1f}")
log("Anchors: US revenue 2024 $221.0mm, 2025 $309.7mm (10-K); 2026E US ~$420mm if international ~+6% (est.). Services revenue (global) ~$302mm 2025 at 26% GM (est. from $223.5mm services COGS).")

# overlap pairs for haircut re-estimation: NTD RY2024 (annualized) vs census annual run-rate at the same agency
log("Haircut pairs (NTD RY2024 annualized / census annual run-rate):")
for ag, paid in sorted(ntd.items(), key=lambda x: -x[1]):
    key = NTD_MAP.get(ag, ag.lower()); hit = next(((k, v) for k, v in ops_latest.items() if key in k), None)
    m = ntd_months.get(ag, 12); ann = paid * 12 / m if 0 < m < 12 else paid
    if hit: d, a, r = hit[1]; log(f"  {ag[:45]:45} NTD {ann/1e6:6.2f} | census {a/1e6:6.2f} ({r['contract_action']} {d}) | ratio {ann/a:4.2f}")
    else: log(f"  {ag[:45]:45} NTD {ann/1e6:6.2f} | no priced census ops row")
