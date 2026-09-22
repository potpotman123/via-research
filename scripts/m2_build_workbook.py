"""Build the revenue projection model inside KW VIA MODEL.xlsx (in place; baseline copy kept in model/).
- Rewrites 'Revenue Build (KW)' (rows 20 and 30 stay where Three Statements and Summary expect them).
- Adds 'Contract Layer (KW)' (contract-level services engine), 'NTD Data' (evidence), 'SOTP (KW)'.
- Re-points Three Statements row 11 (cost of revenue % of revenue) to the margin bridge.
- Adds Cover TOC entries and a checks flag.
Formulas use only INDEX/MATCH, SUMIFS, SUMPRODUCT, IF, DATE/YEAR, MIN/MAX so LibreOffice and Excel evaluate identically.
"""
import csv, re, sys, collections
from datetime import date, datetime
from copy import copy
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.hyperlink import Hyperlink

ROOT = "/Users/kwu/Documents/VIA"
SRC = "/Users/kwu/Downloads/KW VIA MODEL.xlsx"
OUT = [SRC, f"{ROOT}/model/KW VIA MODEL.xlsx"]

# ---------- styles ----------
GAR = "Garamond"
BLUE, RED, GREEN, BLACK, GREY = "FF0000FF", "FFFF0000", "FF008000", "FF000000", "FF7F7F7F"
FMT_MM = '#,##0_);\\(#,##0\\);\\-_)'
FMT_MM1 = '#,##0.0_);\\(#,##0.0\\);\\-_)'
FMT_MM2 = '#,##0.00_);\\(#,##0.00\\);\\-_)'
FMT_PCT = '0.0%;\\(0.0%\\);\\-_)'
FMT_INT = '#,##0_);\\(#,##0\\);\\-_)'
FMT_X = '0.0"x"'
FMT_DATE = 'yyyy-mm-dd'
THIN = Side(style="thin")

def font(color=BLACK, bold=False, italic=False, size=12):
    return Font(name=GAR, size=size, bold=bold, italic=italic, color=color)

def put(ws, ref, value, color=BLACK, bold=False, italic=False, fmt=None, size=12, align=None, border_b=False):
    c = ws[ref]; c.value = value; c.font = font(color, bold, italic, size)
    if fmt: c.number_format = fmt
    if align: c.alignment = Alignment(horizontal=align)
    if border_b: c.border = Border(bottom=THIN)
    return c

def note(ws, row, text, col="AB"):
    put(ws, f"{col}{row}", text, GREY, italic=True)

# ---------- period columns (identical on all model sheets) ----------
PER = ["FY2023A", "FY2024A", "1Q25A", "2Q25A", "3Q25A", "4Q25A", "FY2025A", "1Q26A", "2Q26A", "3Q26E", "4Q26E", "FY2026E",
       "1Q27E", "2Q27E", "3Q27E", "4Q27E", "FY2027E", "FY2028E", "FY2029E", "FY2030E", "FY2031E", "FY2032E", "FY2033E", "FY2034E", "FY2035E"]
COL = {p: L(3 + i) for i, p in enumerate(PER)}          # C..AA
ANN = ["FY2023A", "FY2024A", "FY2025A", "FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E", "FY2031E", "FY2032E", "FY2033E", "FY2034E", "FY2035E"]
ENG = ["FY2024A", "FY2025A", "FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E"]     # explicit engine years
FADE = ["FY2031E", "FY2032E", "FY2033E", "FY2034E", "FY2035E"]
PREV = {ANN[i]: ANN[i - 1] for i in range(1, len(ANN))}
QTR26 = ["3Q26E", "4Q26E"]; Q25H2 = ["3Q25A", "4Q25A"]; QTR27 = ["1Q27E", "2Q27E", "3Q27E", "4Q27E"]; Q25 = ["1Q25A", "2Q25A", "3Q25A", "4Q25A"]
CL = "'Contract Layer (KW)'"; RB = "'Revenue Build (KW)'"; TS = "'Three Statements (KW)'"; SC = "'Street Consensus'"; WC = "'WACC and Reverse DCF (KW)'"

# ---------- data ----------
def num(v):
    s = (v or "").replace("$", "").replace(",", "").strip(); m = re.search(r"\d+(?:\.\d+)?", s); return float(m.group(0)) if m else None

census = list(csv.DictReader(open(f"{ROOT}/out/via_contract_census.csv")))
build = list(csv.DictReader(open(f"{ROOT}/out/us_revenue_build.csv")))
hits = [h for h in csv.DictReader(open(f"{ROOT}/text/enum/ntd_contractual_hits.csv")) if h["seller_kind"] == "via" and "downtowner" not in (h["Contractee Operator Name"] + h["Contractee Company Name"]).lower()]
by = collections.defaultdict(list)
for r in census:
    if r["contract_action"] not in ("competitor-award", "deployment-observed"): by[r["agency"].lower()].append(r)
def find_rows(name):
    k = name.lower()
    for key in by:
        if k[:18] in key or key[:18] in k: return by[key]
    return []
FED1 = re.compile(r"CARES|ARPA|American Rescue|CRRSAA|Sandbox|\bIMI\b|\bAIM\b|Accelerating Innovative|discretionary|one-time|Low or No|5312|Access for All|CPUC", re.I)
FEDF = re.compile(r"5307|5310|5311|5339|CMAQ|STBG|Surface Transportation|formula|FTA|Federal Transit|federal", re.I)
STATE = re.compile(r"\bstate\b|TxDOT|Caltrans|LCTOP|SB ?1\b|MassDOT|CTDOT|PennDOT|ODOT|NJDOT|NYSDOT|VDOT|FDOT|GDOT|MDOT|SGR|Mobility Fund|state grant|\bSTA\b|TRiP", re.I)
LOCAL = re.compile(r"general fund|sales tax|local|city fund|county fund|fare|transit fund|municipal|property tax|measure [A-Z]|\bTDA\b|enterprise fund", re.I)
def tag(text):
    if not text: return "unknown"
    if FED1.search(text): return "federal one-time"
    if STATE.search(text) and not FEDF.search(text): return "state"
    if FEDF.search(text): return "federal formula"
    if LOCAL.search(text): return "local"
    return "unknown"
def dt(s):
    if not s: return None
    s = s[:10]
    for f in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try: return datetime.strptime(s, f).date()
        except ValueError: pass
    return None
def add_years(d, y):
    return date(d.year + int(y) + (1 if (y % 1) >= 0.5 else 0), d.month, min(d.day, 28)) if d else None

NTD_MAP = {"City of Arlington": "city of arlington", "Sarasota County": "sarasota county", "Ben Franklin Transit": "ben franklin transit", "Pierce County Transportation Benefit Area Authority": "pierce transit",
           "Transportation District Commission of Hampton Roads": "hampton roads transit", "City of Grand Prairie": "city of grand prairie", "County of Volusia": "county of volusia", "City of Sioux Falls": "sioux falls",
           "Suffolk County": "suffolk county", "Lorain County": "lorain county", "City of Valdosta": "city of valdosta", "County of Muskegon": "muskegon", "Worcester Regional Transit Authority": "worcester",
           "City of Norman": "city of norman", "Snohomish County Public Transportation Benefit Area Corporation": "community transit", "Denton County Transportation Authority": "denton county",
           "Utah Transit Authority": "utah transit", "King County": "king county", "Bi-State Development Agency of the Missouri-Illinois Metropolitan District": "bi-state", "Capital Area Transit System": "capital area transit",
           "Toledo Area Regional Transit Authority": "toledo", "City of Green Bay": "green bay", "Stark Area Regional Transit Authority": "stark area", "Birmingham-Jefferson County Transit Authority": "birmingham",
           "Milwaukee County": "milwaukee county", "Ann Arbor Area Transportation Authority": "ann arbor"}
contracts = []
agg = collections.defaultdict(lambda: dict(pay=0.0, voms=0.0, months=0, op="", modes=set(), fares=0.0, buyer_veh="", hist={}))
for h in hits:
    a = agg[h["Agency Name"].strip()]; a["hist"][h["year"]] = a["hist"].get(h["year"], 0) + float(h["Direct Payment/Agency Subsidy"] or 0)
    if h["year"] != "2024": continue
    a["pay"] += float(h["Direct Payment/Agency Subsidy"] or 0); a["voms"] += float(h["VOMS Under Contract"] or 0)
    a["months"] = max(a["months"], int(float(h["Months Seller Operated in FY"] or 12) or 12)); a["op"] = h["Contractee Operator Name"] or h["Contractee Company Name"]; a["modes"].add(h["Mode"] + "/" + h["TOS"])
    if h["Fares Retained by"] == "Seller": a["fares"] += float(h["PT Fare Revenues/Passenger Fees"] or 0)
    a["buyer_veh"] = h.get("Buyer Supplies Vehicles to Seller", "") or a["buyer_veh"]
ntd_hist = {ag: a["hist"] for ag, a in agg.items()}
for ag, a in sorted(agg.items(), key=lambda x: -x[1]["pay"]):
    if a["pay"] == 0: continue
    m = a["months"]; base = a["pay"] * 12 / m if 0 < m < 12 else a["pay"]
    if 0 < m < 12 and a["voms"]: base = min(base, a["voms"] * 160000)
    crs = find_rows(NTD_MAP.get(ag, ag))
    fund = " | ".join(sorted({r["funding_source"] for r in crs if r["funding_source"] and r["funding_source"].lower() not in ("not stated", "")}))
    term = [r for r in crs if r["contract_action"] in ("termination", "non-renewal")]
    dated = sorted([r for r in crs if dt(r["award_or_approval_date"] or r["term_start"])], key=lambda r: r["award_or_approval_date"] or r["term_start"])
    early = [r for r in dated if (r["award_or_approval_date"] or r["term_start"]) < "2024-01-01"]
    start = dt((early[0]["term_start"] or early[0]["award_or_approval_date"])) if early else date(2020, 1, 1)
    latest = dated[-1] if dated else None; end = None
    if latest and num(latest["term_years_incl_options"]) and (latest["award_or_approval_date"] or latest["term_start"]) >= "2024-01-01":
        end = add_years(dt(latest["term_start"] or latest["award_or_approval_date"]), num(latest["term_years_incl_options"]))
    if term and dt(term[0]["award_or_approval_date"]): end = dt(term[0]["award_or_approval_date"])
    scope = "Hybrid" if any(r["scope_type"] == "Hybrid" for r in crs) else "Turnkey"
    labor = "Y" if a["buyer_veh"] == "Y" else ""
    contracts.append(dict(layer="NTD-paid", agency=ag, entity=a["op"], scope=scope, labor=labor, fund_raw=fund[:120], tag=tag(fund), runrate=a["pay"] / 1e6, haircut=1.0,
                          base=base / 1e6, base_year=2024, start=start, end=end, ntd="Y", term="Y" if term else "",
                          basis=f"NTD RY2024 payment ${a['pay']/1e6:,.2f}mm" + (f" over {m} months, annualized (cap VOMS x $160k)" if 0 < m < 12 else "") + f"; VOMS {a['voms']:.0f}; modes {', '.join(sorted(a['modes']))}; fares retained by Via ${a['fares']/1e6:,.2f}mm",
                          source="FTA NTD RY2024 Contractual Relationship table; census rows: %d" % len(crs)))
for b in [b for b in build if b["layer"].startswith("2")]:
    crs = find_rows(b["agency"]); m = re.search(r"census (\S+) (\S*): run-rate ([\d,]+) x haircut ([\d.]+); start (\S+)", b["basis"])
    action, d0, a, hc, start = m.group(1), m.group(2), float(m.group(3).replace(",", "")), float(m.group(4)), m.group(5)
    start = dt(start if start != "n/a" else (d0 if d0 else ""))
    base_year = int(d0[:4]) if d0[:4].isdigit() else (start.year if start else 2025)
    fund = " | ".join(sorted({r["funding_source"] for r in crs if r["funding_source"] and r["funding_source"].lower() not in ("not stated", "")}))
    tr = [num(r["term_years_incl_options"]) for r in crs if num(r["term_years_incl_options"]) and ((num(r["annual_value_usd"]) and abs(num(r["annual_value_usd"]) - a) < 1) or (num(r["total_value_usd"]) and abs(num(r["total_value_usd"]) / num(r["term_years_incl_options"]) - a) < 1))]
    yrs = tr[0] if tr else None
    term = [r for r in crs if r["contract_action"] in ("termination", "non-renewal") and ((r["award_or_approval_date"] and start and dt(r["award_or_approval_date"]) >= start) or (not r["award_or_approval_date"] and start and start < date(2025, 1, 1)))]
    ent = next((e for e in ("River North", "NoMad", "Tidewater", "Port City", "Sioux Falls Transit", "Twin Cities", "Via Mobility, LLC", "Via Transportation") for r in crs if e.lower() in r["notes"].lower()), "")
    labor = "Y" if any(r["scope_type"] == "Hybrid" and "agency" in r["vehicles_supplied_by"].lower() for r in crs) else ""
    row = dict(layer="Census-priced", agency=b["agency"], entity=ent, scope=b["scope"], labor=labor, fund_raw=fund[:120], tag=tag(fund), runrate=a / 1e6, haircut=hc, base=a * hc / 1e6, base_year=base_year,
               start=start or date(base_year, 1, 1), end=(add_years(start, yrs) if (start and yrs) else None), ntd="", term="Y" if term else "",
               basis=f"census {action} {d0}: annual run-rate ${a/1e6:,.2f}mm x haircut {hc}" + (f"; term {yrs:g} yrs incl. options" if yrs else "; term not stated"), source=b["basis"][:60])
    if "Rochester" in b["agency"]:   # $77.8mm documented as a five-year contract; census term field carries 10 (incl. options)
        row.update(runrate=77.8 / 5, base=77.8 / 5 * hc, end=add_years(start, 5), basis="census award 2026-07-06: $77.8mm over five years (Post Bulletin) = $15.56mm/yr x haircut 0.8; census term field 10 yrs incl. options, base 5 used", labor="Y", scope="Hybrid")
    contracts.append(row)
# manual rows (documented totals without a stated term)
contracts.append(dict(layer="Census-priced", agency="City of Sunnyvale", entity="NoMad Transit LLC", scope="Turnkey", labor="", fund_raw="", tag="unknown", runrate=8.358 / 3, haircut=0.8, base=8.358 / 3 * 0.8, base_year=2026,
                      start=date(2026, 3, 1), end=date(2029, 2, 28), ntd="", term="", basis="ASSUMPTION: $8.358mm service order (matters 2025-08-15 and 2026-02-11) spread over an assumed 3-year term; term not stated in the documents", source="census; Sunnyvale council matters"))
contracts.append(dict(layer="Census-priced", agency="Town of Highland Park", entity="(791 cooperative / Tidewater Transit likely)", scope="Unknown", labor="", fund_raw="FY26 budget amendment", tag="local", runrate=1.55, haircut=1.0, base=1.55, base_year=2026,
                      start=date(2026, 5, 13), end=None, ntd="", term="", basis="ASSUMPTION: $1.55mm FY26 budget amendment (People Newspapers, 2026-04-21) treated as the annual amount; scope not documented", source="census T-row; news"))
# overrides
for c in contracts:
    if c["agency"].startswith("Transportation District Commission"): c["tag"] = "unknown"; c["fund_raw"] = "TRiP grant applies to the 2025 microtransit award only; funding of the larger paratransit contract not stated"
    if c["agency"].startswith("Bi-State"): c["end"] = date(2026, 6, 30); c["basis"] += "; one-year extension to mid-2026 (Resolution 1421), renewal probability applies after"
    if c["agency"] == "City of Mobile": c["end"] = date(2030, 9, 30)
    if c["agency"] == "Stark Area Regional Transit Authority": c["end"] = date(2024, 11, 7); c["term"] = "Y"
# funding tags / shares from model/inputs/funding_tags.csv (document-specific shares > NTD funding mix > municipal default)
TAGS = list(csv.DictReader(open(f"{ROOT}/model/inputs/funding_tags.csv")))
for c in contracts:
    c["shares"] = None; c["evidence"] = ""
    for t in TAGS:
        if t["match"].lower() in c["agency"].lower():
            sh = {k: float(t[k]) for k in ("local", "state", "fed_formula", "fed_onetime") if t[k] not in ("", None)}
            if sh and sum(sh.values()) > 0: c["shares"] = sh; c["tag"] = "shares"
            elif t["tag"]: c["tag"] = t["tag"]
            c["evidence"] = (t["evidence"] + " [" + t["source"] + "]").strip(); break
n_sh = sum(1 for c in contracts if c["shares"]); n_unk = sum(1 for c in contracts if c["tag"] == "unknown")
print(f"contract rows: {len(contracts)}; share-weighted {n_sh}; tagged {len(contracts)-n_sh-n_unk}; unknown {n_unk}")

# ---------- open workbook ----------
wb = openpyxl.load_workbook(SRC)
rb = wb["Revenue Build (KW)"]; ts = wb["Three Statements (KW)"]; cover = wb["Cover"]; summ = wb["Summary"]
# reported quarterly/annual values come from the untouched baseline copy of the sheet (stable positions)
base = openpyxl.load_workbook(f"{ROOT}/model/KW VIA MODEL v1 baseline 2026-09-21.xlsx")["Revenue Build (KW)"]
keep = {}
for r in (8, 12, 16, 20, 25, 26, 30, 36, 37, 38):
    for p in PER:
        v = base[f"{COL[p]}{r}"].value
        if v is not None and not (isinstance(v, str) and v.startswith("=")): keep[(r, p)] = v
keep[(20, "1Q25A")] = keep[(8, "1Q25A")] + keep[(12, "1Q25A")] + keep[(16, "1Q25A")]
GEO_HIST = {(8, "FY2023A"): 167.558, (8, "FY2024A"): 221.003, (12, "FY2023A"): 43.815, (12, "FY2024A"): 78.527, (16, "FY2023A"): 37.481, (16, "FY2024A"): 38.100}
keep.update(GEO_HIST)
# clear the sheet
for rng in list(rb.merged_cells.ranges): rb.unmerge_cells(str(rng))
rb.delete_rows(1, rb.max_row + 5)
for col in range(3, 28): rb.column_dimensions[L(col)].width = 11
rb.column_dimensions["A"].width = 74; rb.column_dimensions["B"].width = 8; rb.column_dimensions["AB"].width = 95
rb.freeze_panes = "C5"; rb.sheet_view.showGridLines = False
rb.column_dimensions.group("O", "R", hidden=True, outline_level=1)   # 2027 quarters exist (income statement pulls them) but are collapsed

R = dict(seg_hdr=6, svc=7, svc_g=8, svc_sh=9, sw=10, sw_g=11, sw_sh=12, tot=13, tot_g=14, tot_org=15, us=16, intl=17, tot_chk=18,
         gp_hdr=19, gm_svc=20, gp_svc=21, gm_sw=22, gp_sw=23, uplift=24, gp_tot=25, gm_blend=26, cogs=27,
         se_hdr=29, svc_hard=30, svc_new=31, svc_dt=32, svc_plug=33, svc_us=34, svc_intl=35, svc_tot=36, memo_split=37, memo_imp=38,
         sw_hdr=40, sw_named=41, sw_small=42, sw_us=43, sw_intl=44, sw_tot=45, sw_acv=46,
         cu_hdr=48, cust_tk=49, cust_sw=50, cust_dt=51, cust_tot=52, cust_g=53, cust_org=54, rpo=55, nrr=56, grr=57,
         in_hdr=59, in_sgm=60, in_sgm_chg=61, in_uplift=62, in_intl_share=63, in_2h_us=64, in_2h_intl=65, in_intl_g=66, in_plug_g=67, in_dt26=68, in_dt_g=69,
         in_sw26=70, in_logo=71, in_exp=72, in_churn=73, in_doe=74, in_tk_adds=75, in_tk_base=76, in_fade_svc=77, in_fade_sw=78, in_alloc=79,
         gd_hdr=81, gd_low=82, gd_high=83, gd_vs=84,
         ap_hdr=86, a_cost=87, a_other=88, a_ls=89, a_loaded=90, a_svc=91, a_sw=92, a_swcost=93, a_swgm=94, a_chk=95,
         br_hdr=97, chk_hdr=110)
CL_TOT_HARD = 6 + len(contracts) + 2
CL_TOT_NEW = CL_TOT_HARD + 33
CLY = {"FY2024A": "S", "FY2025A": "T", "FY2026E": "U", "FY2027E": "V", "FY2028E": "W", "FY2029E": "X", "FY2030E": "Y"}
HIST3 = ("FY2023A", "FY2024A", "FY2025A"); PROJ = [p for p in ANN if p.endswith("E")]; ENGP = ["FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E"]
N_ = COL["FY2026E"]
def IN(key): return f"${N_}${R[key]}"
def label(ws, row, text, units="", bold=False, italic=False, color=BLACK, size=12):
    put(ws, f"A{row}", text, color, bold, italic, size=size)
    if units: put(ws, f"B{row}", units)
def growth(ws, row, base_row=None):
    base_row = base_row or row - 1
    for p in ANN:
        if p == "FY2023A": continue
        c, pc = COL[p], COL[PREV[p]]
        put(ws, f"{c}{row}", f"=IF({pc}{base_row}=0,0,{c}{base_row}/{pc}{base_row}-1)", italic=True, fmt=FMT_PCT)
def share(ws, row, base_row, tot_row):
    for p in ANN: put(ws, f"{COL[p]}{row}", f"=IF({COL[p]}{tot_row}=0,0,{COL[p]}{base_row}/{COL[p]}{tot_row})", italic=True, fmt=FMT_PCT)

put(rb, "A1", "VIA, SOTP RPM", bold=True, size=14)   # title as Kendall set it in Excel
put(rb, "A2", "Revenue and gross profit by segment (services vs. software) feeding the income statement  |  $ in millions unless noted  |  2027 quarterly columns are grouped (click + to expand)  |  rebuilt 2026-09-21", GREY, italic=True)
put(rb, "A3", "Fiscal Year", bold=True, size=14)
for col in range(3, 28): rb[f"{L(col)}3"].border = Border(bottom=THIN)
put(rb, "C3", "Historical (reported)", bold=True, size=12, align="center", border_b=True); rb.merge_cells("C3:K3")
put(rb, "L3", "Projected", bold=True, size=12, align="center", border_b=True); rb.merge_cells("L3:AA3")
put(rb, "B4", "Units", align="right", border_b=True)
FYFILL = PatternFill("solid", fgColor="FFF2F2F2")
for p in PER:
    put(rb, f"{COL[p]}4", p, align="right", border_b=True, bold=p.startswith("FY"))
    if p.startswith("FY"): rb[f"{COL[p]}4"].fill = FYFILL
put(rb, "A4", "Quarters are reported (A) through 2Q26; 3Q26E-4Q27E are projected. FY columns shaded.", GREY, italic=True, size=10)
put(rb, "AB4", "Notes / sources", GREY, italic=True, border_b=True)

# ---------- 1. Revenue by segment ----------
label(rb, R["seg_hdr"], "Revenue by Segment", bold=True, size=14)
label(rb, R["svc"], "Services revenue (turnkey, hybrid and labor-only operations)", "$mm", bold=True)
label(rb, R["svc_g"], "% Growth (YoY)", "%", italic=True); label(rb, R["svc_sh"], "% of Total Revenue", "%", italic=True)
label(rb, R["sw"], "Software revenue (subscriptions, Remix, named accounts)", "$mm", bold=True)
label(rb, R["sw_g"], "% Growth (YoY)", "%", italic=True); label(rb, R["sw_sh"], "% of Total Revenue", "%", italic=True)
label(rb, R["tot"], "Total Revenue (feeds Three Statements row 7)", "$mm", bold=True)
label(rb, R["tot_g"], "% Growth (YoY)", "%", italic=True); label(rb, R["tot_org"], "% Growth (YoY) ex-Downtowner, at the Downtowner revenue estimate in the inputs", "%", bold=True)
label(rb, R["tot_chk"], "Check vs. Three Statements revenue (should be 0)", "$mm", italic=True, color=GREY)
label(rb, R["us"], "Memo: United States revenue (reported; FY2026E anchored to 1H26A)", "$mm", italic=True)
label(rb, R["intl"], "Memo: International revenue, Germany + all other (reported)", "$mm", italic=True)
QA = ("1Q25A", "2Q25A", "3Q25A", "4Q25A", "1Q26A", "2Q26A")
for p in PER:
    c = COL[p]; tot = R["tot"]
    if p in HIST3 or p in QA:
        put(rb, f"{c}{R['svc']}", f"={c}{R['a_svc']}", bold=True, fmt=FMT_MM1); put(rb, f"{c}{R['sw']}", f"={c}{R['a_sw']}", bold=True, fmt=FMT_MM1)
    elif p in PROJ:
        put(rb, f"{c}{R['svc']}", f"={c}{R['svc_tot']}", bold=True, fmt=FMT_MM1); put(rb, f"{c}{R['sw']}", f"={c}{R['sw_tot']}", bold=True, fmt=FMT_MM1)
    elif p in QTR26:
        me = COL["3Q25A" if p == "3Q26E" else "4Q25A"]
        for rr in (R["svc"], R["sw"]): put(rb, f"{c}{rr}", f"=({N_}{rr}-{COL['1Q26A']}{rr}-{COL['2Q26A']}{rr})*{me}{rr}/({COL['3Q25A']}{rr}+{COL['4Q25A']}{rr})", bold=True, fmt=FMT_MM1)
    elif p in QTR27:
        q = COL[Q25[QTR27.index(p)]]
        for rr in (R["svc"], R["sw"]): put(rb, f"{c}{rr}", f"={COL['FY2027E']}{rr}*{q}{rr}/{COL['FY2025A']}{rr}", bold=True, fmt=FMT_MM1)
    # total revenue
    if p in ("FY2023A", "FY2024A", "1Q25A", "2Q25A", "3Q25A", "4Q25A", "1Q26A", "2Q26A"): put(rb, f"{c}{tot}", keep[(20, p)], BLUE, bold=True, fmt=FMT_MM1)
    elif p == "FY2025A": put(rb, f"{c}{tot}", f"=SUM({COL['1Q25A']}{tot}:{COL['4Q25A']}{tot})", bold=True, fmt=FMT_MM1)
    else: put(rb, f"{c}{tot}", f"={c}{R['svc']}+{c}{R['sw']}", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['tot_chk']}", f"=ROUND({c}{tot}-{TS}!{c}7,3)", GREEN, italic=True, fmt=FMT_MM1)
    # US memo
    u = R["us"]
    if p in ("FY2023A", "FY2024A", "1Q25A", "2Q25A", "3Q25A", "4Q25A", "1Q26A", "2Q26A"): put(rb, f"{c}{u}", keep[(8, p)], BLUE, italic=True, fmt=FMT_MM1)
    elif p == "FY2025A": put(rb, f"{c}{u}", f"=SUM({COL['1Q25A']}{u}:{COL['4Q25A']}{u})", italic=True, fmt=FMT_MM1)
    elif p == "FY2026E": put(rb, f"{c}{u}", f"={COL['1Q26A']}{u}+{COL['2Q26A']}{u}+({COL['3Q25A']}{u}+{COL['4Q25A']}{u})*(1+{IN('in_2h_us')})", italic=True, fmt=FMT_MM1)
    elif p in PROJ: put(rb, f"{c}{u}", f"={c}{R['svc_us']}+{c}{R['sw_us']}", italic=True, fmt=FMT_MM1)
    elif p in QTR26: put(rb, f"{c}{u}", f"=({N_}{u}-{COL['1Q26A']}{u}-{COL['2Q26A']}{u})*{COL['3Q25A' if p == '3Q26E' else '4Q25A']}{u}/({COL['3Q25A']}{u}+{COL['4Q25A']}{u})", italic=True, fmt=FMT_MM1)
    elif p in QTR27: put(rb, f"{c}{u}", f"={COL['FY2027E']}{u}*{COL[Q25[QTR27.index(p)]]}{u}/{COL['FY2025A']}{u}", italic=True, fmt=FMT_MM1)
    # International memo
    i_ = R["intl"]
    if p in ("FY2023A", "FY2024A", "1Q25A", "2Q25A", "3Q25A", "4Q25A", "1Q26A", "2Q26A"): put(rb, f"{c}{i_}", round(keep[(12, p)] + keep[(16, p)], 3), BLUE, italic=True, fmt=FMT_MM1)
    elif p == "FY2025A": put(rb, f"{c}{i_}", f"=SUM({COL['1Q25A']}{i_}:{COL['4Q25A']}{i_})", italic=True, fmt=FMT_MM1)
    elif p == "FY2026E": put(rb, f"{c}{i_}", f"={COL['1Q26A']}{i_}+{COL['2Q26A']}{i_}+({COL['3Q25A']}{i_}+{COL['4Q25A']}{i_})*(1+{IN('in_2h_intl')})", italic=True, fmt=FMT_MM1)
    elif p in ENGP: put(rb, f"{c}{i_}", f"={COL[PREV[p]]}{i_}*(1+{c}{R['in_intl_g']})", italic=True, fmt=FMT_MM1)
    elif p in FADE: put(rb, f"{c}{i_}", f"={c}{R['svc_intl']}+{c}{R['sw_intl']}", italic=True, fmt=FMT_MM1)
    elif p in QTR26: put(rb, f"{c}{i_}", f"=({N_}{i_}-{COL['1Q26A']}{i_}-{COL['2Q26A']}{i_})*{COL['3Q25A' if p == '3Q26E' else '4Q25A']}{i_}/({COL['3Q25A']}{i_}+{COL['4Q25A']}{i_})", italic=True, fmt=FMT_MM1)
    elif p in QTR27: put(rb, f"{c}{i_}", f"={COL['FY2027E']}{i_}*{COL[Q25[QTR27.index(p)]]}{i_}/{COL['FY2025A']}{i_}", italic=True, fmt=FMT_MM1)
Q26 = ["1Q26A", "2Q26A", "3Q26E", "4Q26E"]
def qgrowth(ws, row, base_row):
    for p in Q26: put(ws, f"{COL[p]}{row}", f"=IF({COL[Q25[Q26.index(p)]]}{base_row}=0,0,{COL[p]}{base_row}/{COL[Q25[Q26.index(p)]]}{base_row}-1)", italic=True, fmt=FMT_PCT)
    for p in QTR27: put(ws, f"{COL[p]}{row}", f"=IF({COL[Q26[QTR27.index(p)]]}{base_row}=0,0,{COL[p]}{base_row}/{COL[Q26[QTR27.index(p)]]}{base_row}-1)", italic=True, fmt=FMT_PCT)
def qshare(ws, row, base_row, tot_row):
    for p in Q25 + Q26 + QTR27: put(ws, f"{COL[p]}{row}", f"=IF({COL[p]}{tot_row}=0,0,{COL[p]}{base_row}/{COL[p]}{tot_row})", italic=True, fmt=FMT_PCT)
for rr, base_ in ((R["svc_g"], R["svc"]), (R["sw_g"], R["sw"]), (R["tot_g"], R["tot"])): growth(rb, rr, base_); qgrowth(rb, rr, base_)
share(rb, R["svc_sh"], R["svc"], R["tot"]); share(rb, R["sw_sh"], R["sw"], R["tot"]); qshare(rb, R["svc_sh"], R["svc"], R["tot"]); qshare(rb, R["sw_sh"], R["sw"], R["tot"])
DT = R["svc_dt"]; T_ = R["tot"]
for p in ANN:
    if p in ("FY2023A", "FY2024A"): continue
    c, pc = COL[p], COL[PREV[p]]
    put(rb, f"{c}{R['tot_org']}", f"=IF({pc}{T_}=0,0,({c}{T_}-{c}{DT}+{pc}{DT})/{pc}{T_}-1)", bold=True, fmt=FMT_PCT)
for p in Q26:   # 2026 quarters vs 2025 quarters: remove a quarter of the FY2026E Downtowner estimate (4Q25 held the 19-day stub)
    c = COL[p]; pq = COL[Q25[Q26.index(p)]]; prior_dt = f"{COL['FY2025A']}{DT}" if p == "4Q26E" else "0"
    put(rb, f"{c}{R['tot_org']}", f"=IF({pq}{T_}=0,0,({c}{T_}-{N_}{DT}/4+{prior_dt})/{pq}{T_}-1)", bold=True, fmt=FMT_PCT)
for p in QTR27:
    c = COL[p]; pq = COL[Q26[QTR27.index(p)]]
    put(rb, f"{c}{R['tot_org']}", f"=IF({pq}{T_}=0,0,({c}{T_}-{COL['FY2027E']}{DT}/4)/({pq}{T_}-{N_}{DT}/4)-1)", bold=True, fmt=FMT_PCT)
note(rb, R["tot_org"], "Total growth with Downtowner's revenue removed from both years. Downtowner's revenue is NOT disclosed (10-K: 'not material'); the line uses the $25mm FY2026E estimate in the inputs block, so it is an estimate: at $15mm the FY2026E figure is ~2.3 pts higher, at $35mm ~2.3 pts lower. Quarters spread the year's estimate evenly. Documented Downtowner contracts total ~$7mm-$8mm a year (Placer, Denver Montbello, Salisbury, Lake County, Washoe) across 6 of its 94 customers.")
note(rb, R["svc"], "FY2023A-FY2025A and 1H26A from the cost-of-revenue identity (appendix): services revenue = loaded services cost / (1 - services GM). 2025 quarters allocate the year's services cost by each quarter's share of reported cost of revenue; 1Q26/2Q26 use the disclosed YoY changes (+$18.0mm, +$13.6mm). 3Q26E/4Q26E = FY2026E less 1H26A split by the 2025 3Q/4Q pattern; 2027 quarters follow 2025 shares. FY2026E+ from the services engine.")
note(rb, R["sw"], "Residual of total revenue less services. Grew ~+23% a year 2024-25; FY2026E carries a 20% anchored rate, then logos + expansion - churn.")
note(rb, R["tot"], "Reported quarters and years in blue. 3Q26E/4Q26E = FY2026E less 1H26A, split by 2025's 3Q/4Q shares; 2027 quarters by 2025 quarterly shares (approximation, quarterly columns grouped).")
note(rb, R["us"], "10-K Note 'Revenue by geographic area' and 10-Qs. 1H26 US +35.1% YoY. Kept as a memo because the FY2026E anchor and the undocumented-services plug are US figures.")
note(rb, R["intl"], "Germany $83.5mm + all other $41.1mm in 2025. Muva (Berlin) ended 2026-02-28; Germany 2Q26 -12%, other countries 1H26 +41%. Blended 2H26 input default +5%.")

# ---------- 2. Gross profit by segment ----------
label(rb, R["gp_hdr"], "Gross Profit by Segment (feeds Three Statements cost of revenue)", bold=True, size=14)
label(rb, R["gm_svc"], "Services gross margin (loaded basis)", "%")
label(rb, R["gp_svc"], "Services gross profit", "$mm", bold=True)
label(rb, R["gm_sw"], "Software gross margin (implied 2023A-2025A; held at FY2025A)", "%")
label(rb, R["gp_sw"], "Software gross profit", "$mm", bold=True)
label(rb, R["uplift"], "Non-recurring margin uplift (implementation fees), points of revenue", "%", italic=True)
label(rb, R["gp_tot"], "Total gross profit", "$mm", bold=True)
label(rb, R["gm_blend"], "Blended gross margin", "%", bold=True)
label(rb, R["cogs"], "Cost of revenue as % of revenue (to Three Statements row 11)", "%", italic=True, color=GREY)
for p in PER:
    c = COL[p]; fy = {"3Q26E": "FY2026E", "4Q26E": "FY2026E"}.get(p, "FY2027E" if p in QTR27 else p)
    if p in HIST3 or p in QA: put(rb, f"{c}{R['gm_svc']}", f"={IN('in_sgm')}", italic=True, fmt=FMT_PCT); put(rb, f"{c}{R['gm_sw']}", f"={c}{R['a_swgm']}", italic=True, fmt=FMT_PCT)
    elif p == "FY2026E": put(rb, f"{c}{R['gm_svc']}", f"={IN('in_sgm')}", fmt=FMT_PCT); put(rb, f"{c}{R['gm_sw']}", f"=${COL['FY2025A']}${R['a_swgm']}", fmt=FMT_PCT)
    elif p in ENGP: put(rb, f"{c}{R['gm_svc']}", f"={COL[PREV[p]]}{R['gm_svc']}+{c}{R['in_sgm_chg']}", fmt=FMT_PCT); put(rb, f"{c}{R['gm_sw']}", f"={COL[PREV[p]]}{R['gm_sw']}", fmt=FMT_PCT)
    elif p in FADE: put(rb, f"{c}{R['gm_svc']}", f"={COL[PREV[p]]}{R['gm_svc']}", fmt=FMT_PCT); put(rb, f"{c}{R['gm_sw']}", f"={COL[PREV[p]]}{R['gm_sw']}", fmt=FMT_PCT)
    else: put(rb, f"{c}{R['gm_svc']}", f"={COL[fy]}{R['gm_svc']}", fmt=FMT_PCT); put(rb, f"{c}{R['gm_sw']}", f"={COL[fy]}{R['gm_sw']}", fmt=FMT_PCT)   # projected quarters take the year's margins
    put(rb, f"{c}{R['gp_svc']}", f"={c}{R['svc']}*{c}{R['gm_svc']}", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['gp_sw']}", f"={c}{R['sw']}*{c}{R['gm_sw']}", bold=True, fmt=FMT_MM1)
    proj = p in PROJ or p in QTR26 or p in QTR27
    if proj: put(rb, f"{c}{R['uplift']}", f"={COL[fy]}{R['in_uplift']}", italic=True, fmt=FMT_PCT)
    put(rb, f"{c}{R['gp_tot']}", f"={c}{R['gp_svc']}+{c}{R['gp_sw']}" + (f"+{c}{R['uplift']}*{c}{R['tot']}" if proj else ""), bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['gm_blend']}", f"=IF({c}{R['tot']}=0,0,{c}{R['gp_tot']}/{c}{R['tot']})", bold=True, fmt=FMT_PCT)
    if proj: put(rb, f"{c}{R['cogs']}", f"=1-{c}{R['gm_blend']}", GREEN, italic=True, fmt=FMT_PCT)
note(rb, R["gm_svc"], "Input (inputs block). Bleecker's 26%; identity band 20%-32%; drifts by the red annual change from FY2027E. Management: FY2024 and 1Q26 declines 'attributable to a revenue mix shift towards certain lower gross margin contracts'.")
note(rb, R["gm_sw"], "Derived in the appendix (software cost = IT and other + software share of launch/support). Override by typing over the FY2026E cell.")
note(rb, R["uplift"], "10-Q 2Q26: margin rose to 41% 'primarily attributable to a higher percentage of non-subscription revenue' (implementation fees ~5% of revenue vs ~2%). Worth 2-3 points while launches run hot; +2.0 pts FY2026E, +0.5 FY2027E, zero after.")
note(rb, R["gm_blend"], "Historical years reproduce reported gross margin exactly (identity). Each 5-point mix shift toward services costs ~2.5 points of blended margin; the 50% long-term target needs software to be most of revenue.")

# ---------- 3. Services engine ----------
label(rb, R["se_hdr"], "Services Engine (contract-level detail on 'Contract Layer (KW)')", bold=True, size=14)
label(rb, R["svc_hard"], "US documented contracts (26 NTD-paid + 33 census-priced; Contract Layer)", "$mm")
label(rb, R["svc_new"], "US unsigned new wins (vehicle-equivalent vintages x $153k, ramped)", "$mm")
label(rb, R["svc_dt"], "Downtowner (acquired 2025-12-12; revenue undisclosed)", "$mm")
label(rb, R["svc_plug"], "US undocumented and unpriced services (plug; by subtraction to FY2026E)", "$mm")
label(rb, R["svc_us"], "US services revenue", "$mm", bold=True)
label(rb, R["svc_intl"], "International services (= international revenue x services share)", "$mm")
label(rb, R["svc_tot"], "Total services revenue", "$mm", bold=True)
label(rb, R["memo_split"], "Memo: US services implied by the identity (less international services)", "$mm", italic=True, color=GREY)
label(rb, R["memo_imp"], "Memo: imputed floor for the plug (unpriced operators + app-only agencies)", "$mm", italic=True, color=GREY)
for p in ENG:
    c = COL[p]; y = CLY[p]; pc = COL[PREV[p]]
    put(rb, f"{c}{R['svc_hard']}", f"={CL}!{y}{CL_TOT_HARD}", GREEN, italic=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_new']}", f"={CL}!{y}{CL_TOT_NEW}", GREEN, italic=True, fmt=FMT_MM1)
    if p == "FY2024A": put(rb, f"{c}{R['svc_dt']}", 0, fmt=FMT_MM1)
    elif p == "FY2025A": put(rb, f"{c}{R['svc_dt']}", f"={IN('in_dt26')}*19/365", fmt=FMT_MM1)
    elif p == "FY2026E": put(rb, f"{c}{R['svc_dt']}", f"={IN('in_dt26')}", fmt=FMT_MM1)
    else: put(rb, f"{c}{R['svc_dt']}", f"={pc}{R['svc_dt']}*(1+{c}{R['in_dt_g']})", fmt=FMT_MM1)
    if p in ("FY2024A", "FY2025A"): put(rb, f"{c}{R['svc_plug']}", f"={c}{R['memo_split']}-{c}{R['svc_hard']}-{c}{R['svc_dt']}", fmt=FMT_MM1)
    elif p == "FY2026E": put(rb, f"{c}{R['svc_plug']}", f"={c}{R['svc_us']}-{c}{R['svc_hard']}-{c}{R['svc_new']}-{c}{R['svc_dt']}", fmt=FMT_MM1)
    else: put(rb, f"{c}{R['svc_plug']}", f"={pc}{R['svc_plug']}*(1+{c}{R['in_plug_g']})", fmt=FMT_MM1)
    if p == "FY2026E": put(rb, f"{c}{R['svc_us']}", f"={c}{R['us']}-{c}{R['sw_us']}", bold=True, fmt=FMT_MM1)
    else: put(rb, f"{c}{R['svc_us']}", f"={c}{R['svc_hard']}+{c}{R['svc_new']}+{c}{R['svc_dt']}+{c}{R['svc_plug']}", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_intl']}", f"={c}{R['intl']}*{IN('in_intl_share')}", fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_tot']}", f"={c}{R['svc_us']}+{c}{R['svc_intl']}", bold=True, fmt=FMT_MM1)
    if p in ("FY2024A", "FY2025A"): put(rb, f"{c}{R['memo_split']}", f"={c}{R['a_svc']}-{c}{R['svc_intl']}", italic=True, fmt=FMT_MM1); put(rb, f"{c}{R['memo_imp']}", 45.7, BLUE, italic=True, fmt=FMT_MM1)
for p in FADE:
    c = COL[p]; pc = COL[PREV[p]]
    put(rb, f"{c}{R['svc_us']}", f"={pc}{R['svc_us']}*(1+{c}{R['in_fade_svc']})", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_intl']}", f"={pc}{R['svc_intl']}*(1+{c}{R['in_fade_svc']})", fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_tot']}", f"={c}{R['svc_us']}+{c}{R['svc_intl']}", bold=True, fmt=FMT_MM1)
note(rb, R["svc_hard"], "Actual NTD RY2024 payments (agency fiscal years) and census ceilings x 0.8 haircut. Each row carries start, end, escalator (4%), volume expansion (8%/6%/5%/4% from 2027, gliding from observed NTD hours growth), funding tag, hazards and renewal probability. Signed 2025-26 wins (Mobile, Rochester, Plano, Sunnyvale, Addison, Grand County) are rows here.")
note(rb, R["svc_new"], "Vintages 50 / 250 / 200 / 175 / 150 vehicle-equivalents (2026-30) x $153k revenue per contracted vehicle-year (NTD RY2024: $96.8mm / 632 vehicles), 50% first-year ramp, turnkey survival after. 2026 signings ran +200 to +300 vehicle-equivalents; the base follows that pace and fades.")
note(rb, R["svc_dt"], "10-K Note 3: $40.7mm cash, 94 customers, revenue since acquisition 'not material', pro forma not presented. Level $25mm (range $15mm-$35mm); growth by year from the inputs block (15% / 12% / 8% / 6%), organic from FY2027E onward.")
note(rb, R["svc_plug"], "Holds what documents cannot price: agencies below approval thresholds, app-only deployments, 2026 wins with no stated price (Citilink Fort Wayne paratransit, TCATA, Highland Park), and any haircut that is too harsh on new whole-system contracts. Grew +27% in 2025 and ~+50% in 2026; glides 30% / 22% / 16% / 12%.")
note(rb, R["svc_tot"], "FY2031E+ fade at the services growth inputs (contract detail ends 2030).")

# ---------- 4. Software engine ----------
label(rb, R["sw_hdr"], "Software Engine", bold=True, size=14)
label(rb, R["sw_named"], "US named account: NYC DOE ($7.2mm/yr; renewal probability from FY2030E)", "$mm")
label(rb, R["sw_small"], "US small-subscription base (residual through FY2026E; logos x expansion glide x churn after)", "$mm")
label(rb, R["sw_us"], "US software revenue", "$mm", bold=True)
label(rb, R["sw_intl"], "International software (= international revenue x (1 - services share))", "$mm")
label(rb, R["sw_tot"], "Total software revenue", "$mm", bold=True)
label(rb, R["sw_acv"], "Memo: implied ACV of the US small base per software customer ($000)", "$000", italic=True, color=GREY)
put(rb, f"{COL['FY2023A']}{R['sw_tot']}", f"={COL['FY2023A']}{R['a_sw']}", bold=True, fmt=FMT_MM1)
for p in ENG:
    c = COL[p]; pc = COL[PREV[p]]
    if p in ("FY2024A", "FY2025A"): put(rb, f"{c}{R['sw_named']}", 7.2, BLUE, fmt=FMT_MM1)
    elif p == "FY2030E": put(rb, f"{c}{R['sw_named']}", f"={pc}{R['sw_named']}*{IN('in_doe')}", fmt=FMT_MM1)
    else: put(rb, f"{c}{R['sw_named']}", f"={pc}{R['sw_named']}", fmt=FMT_MM1)
    put(rb, f"{c}{R['sw_intl']}", f"={c}{R['intl']}*(1-{IN('in_intl_share')})", fmt=FMT_MM1)
    if p in ("FY2024A", "FY2025A"): put(rb, f"{c}{R['sw_small']}", f"={c}{R['a_sw']}-{c}{R['sw_intl']}-{c}{R['sw_named']}", fmt=FMT_MM1)
    elif p == "FY2026E": put(rb, f"{c}{R['sw_small']}", f"={c}{R['sw_us']}-{c}{R['sw_named']}", fmt=FMT_MM1)   # anchored year: residual of the anchored software total
    else: put(rb, f"{c}{R['sw_small']}", f"={pc}{R['sw_small']}*(1+{IN('in_logo')})*(1+{c}{R['in_exp']})*(1-{IN('in_churn')})", fmt=FMT_MM1)
    if p == "FY2026E":
        put(rb, f"{c}{R['sw_tot']}", f"={COL['1Q26A']}{R['sw']}+{COL['2Q26A']}{R['sw']}+({COL['3Q25A']}{R['sw']}+{COL['4Q25A']}{R['sw']})*(1+{IN('in_sw26')})", bold=True, fmt=FMT_MM1)
        put(rb, f"{c}{R['sw_us']}", f"={c}{R['sw_tot']}-{c}{R['sw_intl']}", bold=True, fmt=FMT_MM1)
    else:
        put(rb, f"{c}{R['sw_us']}", f"={c}{R['sw_named']}+{c}{R['sw_small']}", bold=True, fmt=FMT_MM1)
        put(rb, f"{c}{R['sw_tot']}", f"={c}{R['sw_us']}+{c}{R['sw_intl']}", bold=True, fmt=FMT_MM1)
    if p != "FY2024A": put(rb, f"{c}{R['sw_acv']}", f"=IF({c}{R['cust_sw']}=0,0,{c}{R['sw_small']}/{c}{R['cust_sw']}*1000)", italic=True, fmt=FMT_INT)
for p in FADE:
    c = COL[p]; pc = COL[PREV[p]]
    put(rb, f"{c}{R['sw_named']}", f"={pc}{R['sw_named']}", fmt=FMT_MM1)
    put(rb, f"{c}{R['sw_small']}", f"={pc}{R['sw_small']}*(1+{c}{R['in_fade_sw']})", fmt=FMT_MM1)
    put(rb, f"{c}{R['sw_us']}", f"={c}{R['sw_named']}+{c}{R['sw_small']}", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['sw_intl']}", f"={pc}{R['sw_intl']}*(1+{c}{R['in_fade_sw']})", fmt=FMT_MM1)
    put(rb, f"{c}{R['sw_tot']}", f"={c}{R['sw_us']}+{c}{R['sw_intl']}", bold=True, fmt=FMT_MM1)
note(rb, R["sw_named"], "Census: five-year $36mm NYC DOE contract (2019-08). All other documented software accounts are under $1mm a year (Miami-Dade $0.32mm, El Paso $0.25mm, MTA Maryland $0.22mm) and sit in the residual.")
note(rb, R["sw_small"], "Net logo growth 6% (customer count ex-Downtowner grew 9.3%, operations customers faster), expansion 7%, churn 3.5% (6-7 Spare/RideCo displacements out of ~70 documented software relationships).")
note(rb, R["sw_acv"], "Denominator = organic customers less operations customers (still includes international software customers, so the true US ACV is higher). Far above $43k means the software residual is too large, i.e. services GM too low.")

# ---------- 5. Customers ----------
label(rb, R["cu_hdr"], "Customers (period-end; distinct legal entities with Platform revenue)", bold=True, size=14)
label(rb, R["cust_tk"], "Operations (turnkey/hybrid) customers, organic", "#"); label(rb, R["cust_sw"], "Software customers, organic (= organic total - operations)", "#")
label(rb, R["cust_dt"], "Downtowner customers", "#"); label(rb, R["cust_tot"], "Total customers (feeds Summary)", "#", bold=True)
label(rb, R["cust_g"], "% Growth (YoY)", "%", italic=True); label(rb, R["cust_org"], "Organic customers (ex-Downtowner's 94)", "#", italic=True)
label(rb, R["rpo"], "Remaining performance obligations (reported)", "$mm"); label(rb, R["nrr"], "Platform net revenue retention (reported)", "%"); label(rb, R["grr"], "Gross revenue retention (reported)", "%")
for p in PER:
    c = COL[p]
    if (30, p) in keep: put(rb, f"{c}{R['cust_tot']}", keep[(30, p)], BLUE, bold=True, fmt=FMT_INT)
    if p in ("FY2024A", "FY2025A"):
        put(rb, f"{c}{R['cust_tk']}", f"={c}{R['in_tk_base']}", fmt=FMT_INT)
        put(rb, f"{c}{R['cust_sw']}", f"={c}{R['cust_org']}-{c}{R['cust_tk']}", fmt=FMT_INT); put(rb, f"{c}{R['cust_dt']}", 94 if p == "FY2025A" else 0, BLUE if p == "FY2025A" else BLACK, fmt=FMT_INT)
    elif p in ENGP:
        pc = COL[PREV[p]]
        put(rb, f"{c}{R['cust_tk']}", f"={pc}{R['cust_tk']}+{IN('in_tk_adds')}", fmt=FMT_INT)
        put(rb, f"{c}{R['cust_sw']}", f"={pc}{R['cust_sw']}*(1+{IN('in_logo')}-{IN('in_churn')})", fmt=FMT_INT); put(rb, f"{c}{R['cust_dt']}", f"={pc}{R['cust_dt']}", fmt=FMT_INT)
        put(rb, f"{c}{R['cust_tot']}", f"=ROUND({c}{R['cust_tk']}+{c}{R['cust_sw']}+{c}{R['cust_dt']},0)", bold=True, fmt=FMT_INT)
    elif p in FADE: put(rb, f"{c}{R['cust_tot']}", f"=ROUND({COL[PREV[p]]}{R['cust_tot']}*(1+{IN('in_logo')}-{IN('in_churn')}),0)", bold=True, fmt=FMT_INT)
    elif p == "3Q26E": put(rb, f"{c}{R['cust_tot']}", f"=ROUND({COL['2Q26A']}{R['cust_tot']}+({N_}{R['cust_tot']}-{COL['2Q26A']}{R['cust_tot']})/2,0)", bold=True, fmt=FMT_INT)
    elif p == "4Q26E": put(rb, f"{c}{R['cust_tot']}", f"={N_}{R['cust_tot']}", bold=True, fmt=FMT_INT)
    elif p in QTR27: put(rb, f"{c}{R['cust_tot']}", f"=ROUND({N_}{R['cust_tot']}+({COL['FY2027E']}{R['cust_tot']}-{N_}{R['cust_tot']})*{QTR27.index(p)+1}/4,0)", bold=True, fmt=FMT_INT)
    if p in ANN:
        dtc = 94 if p >= "FY2025A" and p != "FY2023A" and p != "FY2024A" else 0
        put(rb, f"{c}{R['cust_org']}", f"={c}{R['cust_tot']}-{dtc}", italic=True, fmt=FMT_INT)
    for r_, k_ in ((R["rpo"], 38), (R["nrr"], 36), (R["grr"], 37)):
        if (k_, p) in keep: put(rb, f"{c}{r_}", keep[(k_, p)], BLUE, fmt=FMT_MM1 if k_ == 38 else FMT_PCT)
growth(rb, R["cust_g"], R["cust_tot"]); qgrowth(rb, R["cust_g"], R["cust_tot"])
note(rb, R["cust_tot"], "10-K/10-Q KPI: 665 (Dec-24), 689 (Jun-25), 821 (Dec-25, incl. 94 from Downtowner), 847 (Jun-26). Organic growth 9.3%.")
note(rb, R["cust_tk"], "Census: 78 US agencies ever turnkey/hybrid, 26 NTD-paid (overlapping), a share of 62 app-only agencies, plus international operations customers: ~105 (2024), ~120 (2025); inputs.")
note(rb, R["rpo"], "RPO $294.4mm at Dec-25 (60% recognized in 2026, 27% in 2027); $318.3mm at Jun-26 (37% due in 2027).")

# ---------- 6. Inputs ----------
label(rb, R["in_hdr"], "Inputs (red): single values in the FY2026E column; by-year inputs under their year", bold=True, size=14)
INPUTS = [
    ("in_sgm", "Services gross margin, loaded basis (22% / 26% / 30% cases)", {"FY2026E": 0.26}, FMT_PCT, "26% is the value at which the documented US operations book (NTD $96.8mm + priced contracts) fits inside the split with a positive undocumented plug; Bleecker's figure; identity band 20%-32%."),
    ("in_sgm_chg", "Annual change in services gross margin (wage inflation vs escalators)", {p: -0.005 for p in ("FY2027E", "FY2028E", "FY2029E", "FY2030E")}, FMT_PCT, "Base -0.5 pt a year; bear -1.0; bull 0."),
    ("in_uplift", "Non-recurring margin uplift (implementation fees), points of revenue", {"FY2026E": 0.02, "FY2027E": 0.005, **{p: 0.0 for p in ("FY2028E", "FY2029E", "FY2030E") + tuple(FADE)}}, FMT_PCT, "2Q26 non-subscription revenue ~5% of revenue vs ~2% run-rate."),
    ("in_intl_share", "International revenue: services share", {"FY2026E": 0.67}, FMT_PCT, "Not disclosed. Germany (Muva was a ViaVan operations contract) ~75% services, other countries ~50%: blended 67%. Bear 85% / bull 50%."),
    ("in_2h_us", "2H26 YoY growth, United States", {"FY2026E": 0.35}, FMT_PCT, "1H26 US +35.1% YoY. Holding the rate lands FY2026E on the guidance midpoint; the differentiated view starts in 2027."),
    ("in_2h_intl", "2H26 YoY growth, International", {"FY2026E": 0.05}, FMT_PCT, "Germany 2Q26 -12% (Muva ended), other countries +41%: blend ~+5%."),
    ("in_intl_g", "International revenue growth, by year", {"FY2027E": 0.06, "FY2028E": 0.07, "FY2029E": 0.05, "FY2030E": 0.04}, FMT_PCT, "Germany -5% then flat; other countries +20% / +15% / +10% / +8%: blended."),
    ("in_plug_g", "US undocumented services growth, by year (glide; FY2026E by subtraction)", {"FY2027E": 0.30, "FY2028E": 0.22, "FY2029E": 0.16, "FY2030E": 0.12}, FMT_PCT, "Grew +27% in 2025 and ~+50% in 2026 (it holds the unpriced Dec-2025 launches: Citilink Fort Wayne paratransit, TCATA, plus Highland Park), which annualize in 2027. Glide 30% / 22% / 16% / 12%. Bear 15% flat; bull 35% / 30% / 25% / 20%."),
    ("in_dt26", "Downtowner FY2026E revenue ($mm)", {"FY2026E": 25.0}, FMT_MM1, "10-K Note 3: acquired 2025-12-12 for $40.7mm cash (goodwill $26.4mm; intangibles $13.0mm, of which developed technology only $5.0mm, customer relationships $6.8mm); revenue since acquisition 'not material'; pro forma not presented. A mostly-services business at $40.7mm implies ~1x-2x revenue, i.e. $20mm-$40mm; base $25mm, range $15mm-$35mm."),
    ("in_dt_g", "Downtowner growth, by year (FY2027E+)", {"FY2027E": 0.15, "FY2028E": 0.12, "FY2029E": 0.08, "FY2030E": 0.06}, FMT_PCT, "Bought to expand into destination cities (Aspen, Park City, Truckee) that Via's release calls 'an important and growing market'; cross-sell of Via software to 94 customers plus new towns. Base follows the services book with a lag; bear 4% (escalators only); bull 20%."),
    ("in_sw26", "2H26 YoY growth, software (FY2026E software = 1H26A + 2H25A x (1 + this))", {"FY2026E": 0.20}, FMT_PCT, "The software residual grew +23% in 2025 and +25% in 1H26 (2Q26 includes the implementation-fee spike management cited). Base 20%; bear 15%; bull 25%."),
    ("in_logo", "Net software logo growth (FY2027E+)", {"FY2026E": 0.06}, FMT_PCT, "Customer count ex-Downtowner +9.3%; operations customers (~15%-20% of count) grew ~15%-20%, leaving ~6%-7% for software. Bull 9%."),
    ("in_exp", "Expansion at existing software accounts, by year (glide)", {"FY2027E": 0.17, "FY2028E": 0.14, "FY2029E": 0.11, "FY2030E": 0.08}, FMT_PCT, "The software residual grew ~23% in each of 2024, 2025 and 2026 with net logos near 6%, so expansion ran ~14-16 pts. The glide starts there (17%) and fades to 8% by 2030. Bear 10% flat; bull 17% flat."),
    ("in_churn", "Competitive software churn (Spare, RideCo)", {"FY2026E": 0.035}, FMT_PCT, "6-7 displacements since 2024 out of ~70 documented software relationships."),
    ("in_doe", "NYC DOE renewal probability at the FY2030E re-bid", {"FY2026E": 0.70}, "0.00", "Judgment; single largest software account."),
    ("in_tk_adds", "Net new operations customers per year", {"FY2026E": 15}, FMT_INT, "2025-26 pace: Mobile, TCATA, Rochester, Plano, Addison, Highland Park, Grand County, Sunnyvale, Citilink."),
    ("in_tk_base", "Operations customers, FY2024A and FY2025A (under their year)", {"FY2024A": 105, "FY2025A": 120}, FMT_INT, "Census + NTD count; assumption."),
    ("in_fade_svc", "Services revenue growth FY2031E-FY2035E (under their year)", {"FY2031E": 0.08, "FY2032E": 0.07, "FY2033E": 0.06, "FY2034E": 0.05, "FY2035E": 0.05}, FMT_PCT, "Contract detail ends 2030; fade to GDP-plus."),
    ("in_fade_sw", "Software revenue growth FY2031E-FY2035E (under their year)", {"FY2031E": 0.08, "FY2032E": 0.07, "FY2033E": 0.06, "FY2034E": 0.05, "FY2035E": 0.05}, FMT_PCT, "Same fade as services by default."),
    ("in_alloc", "Launch/support personnel allocated to software (identity)", {"FY2026E": 0.50}, FMT_PCT, "Half of the $25.8mm launch and support cost sits with software; the identity table in growth_model_design.md section 9 shows the corners.")]
for key, text, vals, fmt, nt in INPUTS:
    label(rb, R[key], text, "", italic=True)
    for p, v in vals.items(): put(rb, f"{COL[p]}{R[key]}", v, RED, italic=True, fmt=fmt)
    note(rb, R[key], nt)

# ---------- 7. Guidance ----------
label(rb, R["gd_hdr"], "Guidance Check (FY2026E)", bold=True)
label(rb, R["gd_low"], "Revenue guidance - low", "$mm"); label(rb, R["gd_high"], "Revenue guidance - high", "$mm"); label(rb, R["gd_vs"], "Model vs. guidance midpoint", "%", italic=True)
put(rb, f"{N_}{R['gd_low']}", f"={SC}!{N_}22", GREEN, italic=True, fmt=FMT_MM1); put(rb, f"{N_}{R['gd_high']}", f"={SC}!{N_}23", GREEN, italic=True, fmt=FMT_MM1)
put(rb, f"{N_}{R['gd_vs']}", f"=IF(AVERAGE({N_}{R['gd_low']},{N_}{R['gd_high']})=0,0,{N_}{R['tot']}/AVERAGE({N_}{R['gd_low']},{N_}{R['gd_high']})-1)", italic=True, fmt=FMT_PCT)
note(rb, R["gd_low"], "8-K 2026-08-06: FY2026 revenue $550mm-$553mm; adjusted EBITDA $(12.5)mm-$(7.5)mm.")

# ---------- 8. Appendix: historical split ----------
label(rb, R["ap_hdr"], "Appendix: historical segment split from the cost-of-revenue identity", bold=True, size=14)
label(rb, R["a_cost"], "Technology-enabled services cost (drivers, fleet, customer support)", "$mm")
label(rb, R["a_other"], "Other cost of revenue (launch/support + IT) = total COGS - services cost", "$mm")
label(rb, R["a_ls"], "Launch/support share of other cost of revenue (FY2025: 25.8 of 39.1)", "%", italic=True)
label(rb, R["a_loaded"], "Loaded services cost = services cost + services share of launch/support", "$mm")
label(rb, R["a_svc"], "Services revenue = loaded services cost / (1 - services GM)", "$mm", bold=True)
label(rb, R["a_sw"], "Software revenue = total revenue - services revenue", "$mm", bold=True)
label(rb, R["a_swcost"], "Software cost of revenue = other COGS - launch/support kept in services", "$mm")
label(rb, R["a_swgm"], "Implied software gross margin", "%", italic=True)
label(rb, R["a_chk"], "Check: services GP + software GP - reported gross profit (= 0)", "$mm", italic=True, color=GREY)
SVC_COST = {"FY2023A": 117.5, "FY2024A": 167.7, "FY2025A": 223.5}
LS_ = f"${COL['FY2025A']}${R['a_ls']}"
put(rb, f"{COL['FY2025A']}{R['a_ls']}", 25.8 / 39.1, BLUE, italic=True, fmt=FMT_PCT)
label(rb, R["a_chk"] + 1, "Memo: YoY change in technology-enabled services cost, 1Q26 and 2Q26 (10-Q MD&A)", "$mm", italic=True, color=GREY)
put(rb, f"{COL['1Q26A']}{R['a_chk']+1}", 18.0, BLUE, italic=True, fmt=FMT_MM1); put(rb, f"{COL['2Q26A']}{R['a_chk']+1}", 13.6, BLUE, italic=True, fmt=FMT_MM1)
for p in HIST3 + QA:
    c = COL[p]
    if p in HIST3: put(rb, f"{c}{R['a_cost']}", SVC_COST[p], BLUE, fmt=FMT_MM1)
    elif p in Q25: put(rb, f"{c}{R['a_cost']}", f"=${COL['FY2025A']}${R['a_cost']}*{TS}!{c}10/{TS}!${COL['FY2025A']}$10", fmt=FMT_MM1)
    else: put(rb, f"{c}{R['a_cost']}", f"={COL[Q25[QA.index(p)-4]]}{R['a_cost']}+{c}{R['a_chk']+1}", fmt=FMT_MM1)
    put(rb, f"{c}{R['a_other']}", f"={TS}!{c}10-{c}{R['a_cost']}", GREEN, italic=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['a_loaded']}", f"={c}{R['a_cost']}+(1-{IN('in_alloc')})*{LS_}*{c}{R['a_other']}", fmt=FMT_MM1)
    put(rb, f"{c}{R['a_svc']}", f"={c}{R['a_loaded']}/(1-{IN('in_sgm')})", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['a_sw']}", f"={c}{R['tot']}-{c}{R['a_svc']}", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['a_swcost']}", f"={c}{R['a_other']}-({c}{R['a_loaded']}-{c}{R['a_cost']})", fmt=FMT_MM1)
    put(rb, f"{c}{R['a_swgm']}", f"=1-{c}{R['a_swcost']}/{c}{R['a_sw']}", italic=True, fmt=FMT_PCT)
    put(rb, f"{c}{R['a_chk']}", f"=ROUND(({c}{R['a_svc']}-{c}{R['a_loaded']})+({c}{R['a_sw']}-{c}{R['a_swcost']})-({TS}!{c}7-{TS}!{c}10),3)", GREEN, italic=True, fmt=FMT_MM1)
note(rb, R["a_cost"], "10-K FY2025 MD&A: cost of revenue $262.5mm = $223.5mm technology-enabled services + $25.8mm launch and support personnel + $13.3mm IT and other; 2024 and 2023 from the MD&A change sentences (+$55.8mm; +$50.2mm). Quarterly 2025 = FY allocated by each quarter's share of reported cost of revenue (estimate); 1Q26/2Q26 = prior-year quarter + disclosed change.")
note(rb, R["a_other"], "Was $31.9mm / $39.1mm / $39.0mm in 2023-25: flat, so software cost of revenue is not growing with software revenue.")
note(rb, R["a_swgm"], "Should land 70%-80%. Corner cases fail: all launch/support on software at 80% GM would imply services at 6% margin.")

# ---------- 9. Growth bridge ----------
label(rb, R["br_hdr"], "Growth Bridge (annual change in revenue by driver, $mm)", bold=True, size=14)
BR = [("Total revenue change", lambda c, pc: f"={c}{R['tot']}-{pc}{R['tot']}", True, FMT_MM1),
      ("US documented contracts (signed wins, escalators, expansion, expiries)", lambda c, pc: f"={c}{R['svc_hard']}-{pc}{R['svc_hard']}", False, FMT_MM1),
      ("US unsigned new wins", lambda c, pc: f"={c}{R['svc_new']}-{pc}{R['svc_new']}", False, FMT_MM1),
      ("US undocumented services", lambda c, pc: f"={c}{R['svc_plug']}-{pc}{R['svc_plug']}", False, FMT_MM1),
      ("Downtowner (acquisition)", lambda c, pc: f"={c}{R['svc_dt']}-{pc}{R['svc_dt']}", False, FMT_MM1),
      ("International (services + software)", lambda c, pc: f"={c}{R['intl']}-{pc}{R['intl']}", False, FMT_MM1),
      ("US software", lambda c, pc: f"={c}{R['sw_us']}-{pc}{R['sw_us']}", False, FMT_MM1),
      ("Check: components - total (should be 0)", lambda c, pc: f"=ROUND(SUM({c}{R['br_hdr']+2}:{c}{R['br_hdr']+7})-{c}{R['br_hdr']+1},3)", False, FMT_MM1),
      ("Share of growth from acquisition + unsigned new wins", lambda c, pc: f"=IF({c}{R['br_hdr']+1}=0,0,({c}{R['br_hdr']+3}+{c}{R['br_hdr']+5})/{c}{R['br_hdr']+1})", False, FMT_PCT),
      ("Organic growth ex-Downtowner", lambda c, pc: f"=IF({pc}{R['tot']}=0,0,({c}{R['tot']}-{c}{R['svc_dt']}+{pc}{R['svc_dt']})/{pc}{R['tot']}-1)", False, FMT_PCT)]
for i, (text, f, bold, fmt) in enumerate(BR):
    r = R["br_hdr"] + 1 + i; label(rb, r, text, "$mm" if fmt == FMT_MM1 else "%", bold=bold, italic=(i >= 7), color=GREY if i == 7 else BLACK)
    for p in ("FY2025A", "FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E"):
        c, pc = COL[p], COL[PREV[p]]; put(rb, f"{c}{r}", f(c, pc), GREEN if i == 7 else BLACK, bold=bold, italic=(i >= 7), fmt=fmt)
note(rb, R["br_hdr"] + 1, "FY2025A components use the engine's 2024A/2025A rows, so the 2025 bridge shows how much of reported growth the documented book explains.")
R_ORG = R["br_hdr"] + 10; R_BRCHK = R["br_hdr"] + 8

# ---------- 10. Checks ----------
label(rb, R["chk_hdr"], "Checks (PASS / FAIL)", bold=True, size=14)
c25, c24, c27 = COL["FY2025A"], COL["FY2024A"], COL["FY2027E"]
CHK = [("Total revenue equals reported revenue, FY2023A-FY2025A and 1H26A", f"=IF(AND(ROUND({COL['FY2023A']}{R['tot_chk']},1)=0,ROUND({c24}{R['tot_chk']},1)=0,ROUND({c25}{R['tot_chk']},1)=0,ROUND({COL['1Q26A']}{R['tot_chk']},1)=0,ROUND({COL['2Q26A']}{R['tot_chk']},1)=0),\"PASS\",\"FAIL\")"),
       ("Segment split reconciles to reported gross profit (appendix check = 0)", f"=IF(ABS({c25}{R['a_chk']})<0.5,\"PASS\",\"FAIL\")"),
       ("Services gross margin input inside the identity band 20%-32%", f"=IF(AND({N_}{R['in_sgm']}>=0.20,{N_}{R['in_sgm']}<=0.32),\"PASS\",\"FAIL\")"),
       ("Implied software gross margin (FY2025A) within 70%-85%", f"=IF(AND({c25}{R['a_swgm']}>=0.70,{c25}{R['a_swgm']}<=0.85),\"PASS\",\"FAIL\")"),
       ("Undocumented services plug positive (FY2024A-FY2026E)", f"=IF(AND({c24}{R['svc_plug']}>0,{c25}{R['svc_plug']}>0,{N_}{R['svc_plug']}>0),\"PASS\",\"FAIL\")"),
       ("Plug covers at least half the imputed floor (FY2025A)", f"=IF({c25}{R['svc_plug']}>=0.5*{c25}{R['memo_imp']},\"PASS\",\"FAIL\")"),
       ("FY2026E revenue inside guidance $550mm-$553mm", f"=IF(AND({N_}{R['tot']}>={N_}{R['gd_low']},{N_}{R['tot']}<={N_}{R['gd_high']}),\"PASS\",\"FAIL\")"),
       ("FY2026E organic growth ex-Downtowner within 19%-24%", f"=IF(AND({N_}{R_ORG}>=0.19,{N_}{R_ORG}<=0.24),\"PASS\",\"FAIL\")"),
       ("FY2027E services revenue covers RPO due in 2027 ($117.8mm)", f"=IF({c27}{R['svc_tot']}>=318.3*0.37,\"PASS\",\"FAIL\")"),
       ("FY2026E blended gross margin within 39%-42%", f"=IF(AND({N_}{R['gm_blend']}>=0.39,{N_}{R['gm_blend']}<=0.42),\"PASS\",\"FAIL\")"),
       ("FY2026E adj. EBITDA within $3mm of guidance $(12.5)mm-$(7.5)mm", f"=IF(AND({TS}!{N_}52>=-15.5,{TS}!{N_}52<=-4.5),\"PASS\",\"FAIL\")"),
       ("Implied US software ACV below 3x the documented $43k median (FY2025A)", f"=IF({c25}{R['sw_acv']}<129,\"PASS\",\"FAIL\")"),
       ("Growth bridge components sum to the total change (all years)", f"=IF(SUMPRODUCT(ABS({c25}{R_BRCHK}:{COL['FY2030E']}{R_BRCHK}))<0.01,\"PASS\",\"FAIL\")")]
for i, (text, f) in enumerate(CHK):
    r = R["chk_hdr"] + 1 + i; label(rb, r, text, "", italic=True); put(rb, f"{N_}{r}", f, GREEN, italic=True, align="right")
r_flag = R["chk_hdr"] + 1 + len(CHK)
label(rb, r_flag, "All checks", "", bold=True)
put(rb, f"{N_}{r_flag}", f"=IF(COUNTIF({N_}{R['chk_hdr']+1}:{N_}{r_flag-1},\"FAIL\")=0,\"ALL PASS\",COUNTIF({N_}{R['chk_hdr']+1}:{N_}{r_flag-1},\"FAIL\")&\" FAIL\")", GREEN, bold=True, align="right")
note(rb, R["chk_hdr"] + 5, "The reconciliation between the census/NTD book and the filings: fails when the services GM input is too low for the documented US operations revenue.")
note(rb, R["chk_hdr"] + 11, "Adjusted EBITDA flows from the Three Statements opex assumptions, which this rebuild did not change; the tolerance covers that.")
label(rb, r_flag + 2, "Notes", bold=True)
NOTES = ["Architecture: filings set totals and the historical services/software split (one assumption, services GM); the contract layer dates the services book; software is the residual grown by logos, expansion and churn; gross margin follows mix. See via-research repo: growth_model_design.md sections 8-12, rpm_spec.md, rpm_walkthrough.md.",
         "Colour legend as on the Cover: blue reported input, red assumption, black formula, green cross-sheet link or check.",
         "Quarterly cells (grouped columns) exist only for total revenue and are derived from annual totals by 2025 seasonality; the Three Statements pull them for 3Q26E-4Q27E.",
         "NTD report year is each agency's fiscal year; RY2025 (published ~Oct 2026) will replace the 2025 volume assumptions on the NTD rows.",
         "Known gaps carried as labelled inputs: Downtowner revenue, international services share, services GM, software customer count (derived), Sunnyvale term, Highland Park scope."]
for i, t in enumerate(NOTES): label(rb, r_flag + 3 + i, t, "", italic=True, color=GREY)
# ---------- Contract Layer sheet ----------
if "Contract Layer (KW)" in wb.sheetnames: del wb["Contract Layer (KW)"]
cl = wb.create_sheet("Contract Layer (KW)", index=wb.sheetnames.index("Revenue Build (KW)") + 1)
cl.sheet_view.showGridLines = False
put(cl, "A1", "VIA, Contract Layer: documented US operations contracts (services engine detail)", bold=True, size=14)
put(cl, "A2", "One row per contract. Value in year Y = base x start proration x (1+escalator)^(Y-base year) x NTD volume growth x (1-annual hazard)^(Y-2025) x FY2027 level cut x expiry treatment (renewal probability after the end date). $ in millions.", GREY, italic=True)
HDR = ["Agency", "Via entity", "Scope", "Labor-only (agency vehicles)", "Layer", "Funding (census text)", "Funding tag (editable)", "Run-rate / NTD payment ($mm)", "Haircut", "Base ($mm)", "Base year", "Start", "End (blank = none stated)", "NTD row", "Terminated",
       "Annual hazard", "Renewal prob. at end", "FY27 level cut", "FY2024A", "FY2025A", "FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E", "Basis", "Source",
       "Local share", "State share", "Federal formula share", "Federal one-time share", "Funding evidence"]
YEARS = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
for i, h in enumerate(HDR): put(cl, f"{L(i+1)}4", h, bold=True, align="center" if i > 6 else None, border_b=True, size=11)
for i, y in enumerate(YEARS): put(cl, f"{L(19+i)}3", y, GREY, italic=True, align="center", size=11)   # numeric years used by formulas
put(cl, "A3", "Year (numeric, used by formulas) ->", GREY, italic=True, size=11)
widths = {"A": 44, "B": 22, "C": 10, "D": 10, "E": 13, "F": 34, "G": 15, "H": 12, "I": 8, "J": 10, "K": 8, "L": 11, "M": 11, "N": 7, "O": 9, "P": 9, "Q": 9, "R": 9, "Z": 70, "AA": 40, "AB": 9, "AC": 9, "AD": 9, "AE": 9, "AF": 90}
for k, v in widths.items(): cl.column_dimensions[k].width = v
for i in range(19, 26): cl.column_dimensions[L(i)].width = 10
cl.freeze_panes = "B5"
# inputs & hazard table location (below the contracts)
first = 6
n = len(contracts)
ROW_TOT_HARD = first + n + 2               # totals
assert ROW_TOT_HARD == CL_TOT_HARD, (ROW_TOT_HARD, CL_TOT_HARD)
r_in = ROW_TOT_HARD + 4                    # inputs block start
r_idx_n, r_idx_c = r_in + 7, r_in + 8      # volume index rows (written in the inputs block)
ESC, VOL25, VOL26, RATE, RAMP = f"$C${r_in+1}", f"$C${r_in+2}", f"$C${r_in+3}", f"$C${r_in+4}", f"$C${r_in+5}"
r_hz = r_in + 10                           # hazard table header row
HZ_TAGS = ["local", "federal formula", "federal one-time", "state", "unknown"]
HZ = {"local": (0.01, 0.95, 0.0), "federal formula": (0.0, 0.90, 0.0), "federal one-time": (0.0, 0.60, 0.0), "state": (0.0, 0.80, 0.0), "unknown": (0.005, 0.85, 0.0)}   # base = observed retention; funding-cliff set lives in scripts/m3_scenarios.py
tag_rng = f"$A${r_hz+1}:$A${r_hz+len(HZ_TAGS)}"; ann_rng = f"$B${r_hz+1}:$B${r_hz+len(HZ_TAGS)}"; ren_rng = f"$C${r_hz+1}:$C${r_hz+len(HZ_TAGS)}"; cut_rng = f"$D${r_hz+1}:$D${r_hz+len(HZ_TAGS)}"
COMP_TK, COMP_SW, DOWNSELL = f"$C${r_hz+7}", f"$C${r_hz+8}", f"$C${r_hz+9}"
put(cl, f"A{first-1}", "Contracts", bold=True)
put(cl, f"AB{first-2}", "Funding shares (red): when filled, the hazard, renewal probability and level cut are share-weighted across the hazard table below and the tag in column G is ignored ('shares'). Blank shares fall back to the tag.", GREY, italic=True, size=10)
for i, c in enumerate(contracts):
    r = first + i
    put(cl, f"A{r}", c["agency"], size=11); put(cl, f"B{r}", c["entity"], size=11); put(cl, f"C{r}", c["scope"], size=11); put(cl, f"D{r}", c["labor"], size=11, align="center"); put(cl, f"E{r}", c["layer"], size=11)
    put(cl, f"F{r}", c["fund_raw"], GREY, italic=True, size=10); put(cl, f"G{r}", c["tag"], RED, italic=True, size=11)
    put(cl, f"H{r}", round(c["runrate"], 3), BLUE, fmt=FMT_MM2, size=11); put(cl, f"I{r}", c["haircut"], RED, italic=True, fmt="0.00", size=11); put(cl, f"J{r}", f"=H{r}*I{r}", fmt=FMT_MM2, size=11)
    put(cl, f"K{r}", c["base_year"], BLUE, size=11, align="center"); put(cl, f"L{r}", c["start"], BLUE, fmt=FMT_DATE, size=11)
    if c["end"]: put(cl, f"M{r}", c["end"], BLUE if not c["basis"].startswith("ASSUMPTION") else RED, fmt=FMT_DATE, size=11)
    put(cl, f"N{r}", c["ntd"], size=11, align="center"); put(cl, f"O{r}", c["term"], size=11, align="center")
    if c["shares"]:
        for col, k in (("AB", "local"), ("AC", "state"), ("AD", "fed_formula"), ("AE", "fed_onetime")): put(cl, f"{col}{r}", round(c["shares"].get(k, 0.0), 3), RED, italic=True, fmt=FMT_PCT, size=11)
    put(cl, f"AF{r}", c["evidence"], GREY, italic=True, size=10)
    S_ = f"SUM(AB{r}:AE{r})"; rl, rf, r1, rs = r_hz + 1, r_hz + 2, r_hz + 3, r_hz + 4
    wsum = lambda colhz: f"(AB{r}*${colhz}${rl}+AC{r}*${colhz}${rs}+AD{r}*${colhz}${rf}+AE{r}*${colhz}${r1})"
    put(cl, f"P{r}", f"=IF(C{r}=\"Software-only\",{COMP_SW},{COMP_TK})+IF({S_}>0,{wsum('B')},INDEX({ann_rng},MATCH(G{r},{tag_rng},0)))+IF(C{r}<>\"Software-only\",{DOWNSELL}*IF({S_}>0,AB{r},IF(G{r}=\"local\",1,0)),0)", fmt=FMT_PCT, size=11)
    put(cl, f"Q{r}", f"=IF(O{r}=\"Y\",0,IF({S_}>0,{wsum('C')},INDEX({ren_rng},MATCH(G{r},{tag_rng},0))))", fmt="0.00", size=11)
    put(cl, f"R{r}", f"=IF({S_}>0,{wsum('D')},INDEX({cut_rng},MATCH(G{r},{tag_rng},0)))", fmt=FMT_PCT, size=11)
    for j, y in enumerate(YEARS):
        col = L(19 + j); Y = f"{col}$3"
        f = (f"=IF(OR($J{r}=0,{Y}<YEAR($L{r})),0,$J{r}*IF({Y}=YEAR($L{r}),(DATE({Y},12,31)-$L{r}+1)/365,1)*(1+{ESC})^({Y}-$K{r})"
             f"*IF($N{r}=\"Y\",{col}${r_idx_n},{col}${r_idx_c})*IF({Y}>2025,(1-$P{r})^({Y}-2025),1)*IF({Y}>=2027,1-$R{r},1)"
             f"*IF($M{r}=\"\",1,IF({Y}>YEAR($M{r}),$Q{r},IF({Y}=YEAR($M{r}),($M{r}-DATE({Y},1,1)+1)/365+(DATE({Y},12,31)-$M{r})/365*$Q{r},1))))")
        put(cl, f"{col}{r}", f, fmt=FMT_MM2, size=11)
    put(cl, f"Z{r}", c["basis"], GREY, italic=True, size=10); put(cl, f"AA{r}", c["source"], GREY, italic=True, size=10)
last = first + n - 1
put(cl, f"A{ROW_TOT_HARD-1}", "Total NTD-paid rows", bold=True, size=11); put(cl, f"A{ROW_TOT_HARD}", "Total documented US operations contracts (feeds Revenue Build row %d)" % R["svc_hard"], bold=True)
for j in range(7):
    col = L(19 + j)
    put(cl, f"{col}{ROW_TOT_HARD-1}", f"=SUMIFS({col}{first}:{col}{last},$E{first}:$E{last},\"NTD-paid\")", bold=True, fmt=FMT_MM1, size=11)
    put(cl, f"{col}{ROW_TOT_HARD}", f"=SUM({col}{first}:{col}{last})", bold=True, fmt=FMT_MM1)
put(cl, f"A{ROW_TOT_HARD+1}", "Memo: NTD RY2024 payments as reported (fiscal-year basis) = $96.8mm; the FY2024A column annualizes partial-year rows.", GREY, italic=True, size=10)
# inputs
put(cl, f"A{r_in}", "Engine inputs", bold=True)
for k, (text, val, fmt, nt) in enumerate([("Annual rate escalator on operations contracts", 0.04, FMT_PCT, "UTA per-hour rates rose $55.23 to $68.33 over 2022-24 (~10%/yr on that account); OMNIA schedule implies 3%-4%."),
                                          ("NTD-row volume growth 2025 (revenue hours)", 0.10, FMT_PCT, "NTD monthly module: DR/PT hours at Via agencies +10% median 2024->2025."),
                                          ("NTD-row volume growth 2026", 0.08, FMT_PCT, "Jan-Jul 2026 vs 2025, median across the same agencies."),
                                          ("Revenue per contracted vehicle-year ($mm) for unsigned wins", 0.153, FMT_MM2 if False else "0.000", "NTD RY2024: $96.8mm / 632 VOMS under Via contracts."),
                                          ("First-year ramp on new wins", 0.5, FMT_PCT, "6-9 month launch cycle.")], start=1):
    put(cl, f"A{r_in+k}", text, italic=True, size=11); put(cl, f"C{r_in+k}", val, RED, italic=True, fmt=fmt, size=11); put(cl, f"F{r_in+k}", nt, GREY, italic=True, size=10)
r_exp = r_in + 6
put(cl, f"A{r_exp}", "Volume expansion at existing documented contracts, by year (zones, hours; applies to all rows from 2027)", italic=True, size=11)
put(cl, f"F{r_exp}", "Existing-account expansion has been a main growth source (NRR 119%; NTD hours +10% in 2025, +8% in 2026; UTA service orders, Douglas, HRT zones). Glide 8% / 6% / 5% / 4%; bear 3% flat; bull 10% flat.", GREY, italic=True, size=10)
for j, y in enumerate(YEARS):
    col = L(19 + j)
    if y >= 2027: put(cl, f"{col}{r_exp}", {2027: 0.08, 2028: 0.06, 2029: 0.05, 2030: 0.04}[y], RED, italic=True, fmt=FMT_PCT, size=11)
put(cl, f"A{r_idx_n}", "Volume index, NTD rows (2025 and 2026 from NTD hours, then expansion)", italic=True, size=11)
put(cl, f"A{r_idx_c}", "Volume index, census-priced rows (expansion from 2027)", italic=True, size=11)
for j, y in enumerate(YEARS):
    col = L(19 + j); prev = L(18 + j)
    if y == 2024: put(cl, f"{col}{r_idx_n}", 1.0, fmt="0.000", size=11); put(cl, f"{col}{r_idx_c}", 1.0, fmt="0.000", size=11)
    elif y == 2025: put(cl, f"{col}{r_idx_n}", f"={prev}{r_idx_n}*(1+{VOL25})", fmt="0.000", size=11); put(cl, f"{col}{r_idx_c}", f"={prev}{r_idx_c}", fmt="0.000", size=11)
    elif y == 2026: put(cl, f"{col}{r_idx_n}", f"={prev}{r_idx_n}*(1+{VOL26})", fmt="0.000", size=11); put(cl, f"{col}{r_idx_c}", f"={prev}{r_idx_c}", fmt="0.000", size=11)
    else: put(cl, f"{col}{r_idx_n}", f"={prev}{r_idx_n}*(1+{col}{r_exp})", fmt="0.000", size=11); put(cl, f"{col}{r_idx_c}", f"={prev}{r_idx_c}*(1+{col}{r_exp})", fmt="0.000", size=11)
# hazard table
put(cl, f"A{r_hz}", "Funding tag", bold=True, size=11, border_b=True); put(cl, f"B{r_hz}", "Annual funding hazard", bold=True, size=11, border_b=True, align="center"); put(cl, f"C{r_hz}", "Renewal probability at expiry", bold=True, size=11, border_b=True, align="center"); put(cl, f"D{r_hz}", "FY2027 level cut", bold=True, size=11, border_b=True, align="center"); put(cl, f"F{r_hz}", "Basis (growth_model_design.md sections 10-11)", bold=True, size=11, border_b=True)
HZN = {"local": "Base: NTD 2019-24 shows 25 of 26 Via agencies continuous with rising payments; budget exits (SacRT, SARTA, Palo Alto, Milwaukee) ~1%/yr of the book. Funding-cliff case: 2%/yr, 0.90 renewal.",
       "federal formula": "5307/5310/5311 formula money continued through every cycle in the panel. Funding-cliff case: 10% FY2027 level cut, 0.85 renewal.",
       "federal one-time": "CARES/ARPA/Sandbox pilots: Volusia, Suffolk continued; Milwaukee cut; SARTA ended. Base 0.60 renewal; cliff case 0.55.",
       "state": "TRiP, LCTOP, CPUC Access for All cycles renew most of the time. Base 0.80; cliff case 0.70.",
       "unknown": "Blend weighted by documented funding exposure (local ~45%, grant-linked ~30%). Base 0.5%/yr, 0.85 renewal; cliff case 1%/yr, 3% cut, 0.75 renewal."}
for k, t in enumerate(HZ_TAGS, start=1):
    a, rp, cut = HZ[t]; put(cl, f"A{r_hz+k}", t, size=11); put(cl, f"B{r_hz+k}", a, RED, italic=True, fmt=FMT_PCT, size=11); put(cl, f"C{r_hz+k}", rp, RED, italic=True, fmt="0.00", size=11); put(cl, f"D{r_hz+k}", cut, RED, italic=True, fmt=FMT_PCT, size=11); put(cl, f"F{r_hz+k}", HZN[t], GREY, italic=True, size=10)
put(cl, f"A{r_hz+7}", "Competitive hazard, turnkey/hybrid (annual)", italic=True, size=11); put(cl, COMP_TK.replace("$", ""), 0.005, RED, italic=True, fmt=FMT_PCT, size=11); put(cl, f"F{r_hz+7}", "No competitive turnkey loss found in NTD RY2019-24; exits are budget decisions.", GREY, italic=True, size=10)
put(cl, f"A{r_hz+8}", "Competitive hazard, software (annual)", italic=True, size=11); put(cl, COMP_SW.replace("$", ""), 0.035, RED, italic=True, fmt=FMT_PCT, size=11); put(cl, f"F{r_hz+8}", "6-7 displacements by Spare/RideCo since 2024 out of ~70 documented software relationships.", GREY, italic=True, size=10)
put(cl, f"A{r_hz+9}", "Downsell hazard, locally funded operations (annual)", italic=True, size=11); put(cl, DOWNSELL.replace("$", ""), 0.015, RED, italic=True, fmt=FMT_PCT, size=11); put(cl, f"F{r_hz+9}", "Ceiling reductions that GRR does not count (Palo Alto, Arlington, Milwaukee), net of expansions elsewhere. Cliff case 3%.", GREY, italic=True, size=10)
# new-win vintages
r_nw = r_hz + 12
assert r_nw + 7 == CL_TOT_NEW, (r_nw + 7, CL_TOT_NEW)
put(cl, f"A{r_nw}", "Unsigned new wins by vintage (vehicle-equivalents; revenue = vehicles x $/vehicle-year x ramp x escalator x turnkey survival)", bold=True)
put(cl, f"A{r_nw+1}", "Vintage", bold=True, size=11, border_b=True); put(cl, f"B{r_nw+1}", "Vehicle-equivalents (input)", bold=True, size=11, border_b=True, align="center")
for j, y in enumerate(YEARS): put(cl, f"{L(19+j)}{r_nw+1}", f"FY{y}{'A' if y < 2026 else 'E'}", bold=True, size=11, border_b=True, align="center")
VINT = {2026: 50, 2027: 250, 2028: 200, 2029: 175, 2030: 150}
for k, (v, veh) in enumerate(VINT.items(), start=2):
    r = r_nw + k; put(cl, f"A{r}", v, size=11); put(cl, f"B{r}", veh, RED, italic=True, fmt=FMT_INT, size=11)
    for j, y in enumerate(YEARS):
        col = L(19 + j); Y = f"{col}$3"
        put(cl, f"{col}{r}", f"=IF({Y}<$A{r},0,$B{r}*{RATE}*IF({Y}=$A{r},{RAMP},1)*(1+{ESC})^({Y}-$A{r})*(1-{COMP_TK}-INDEX({ann_rng},MATCH(\"unknown\",{tag_rng},0)))^MAX(0,{Y}-$A{r}))", fmt=FMT_MM2, size=11)
put(cl, f"A{CL_TOT_NEW}", "Total unsigned new wins (feeds Revenue Build row %d)" % R["svc_new"], bold=True)
for j in range(7):
    col = L(19 + j); put(cl, f"{col}{CL_TOT_NEW}", f"=SUM({col}{r_nw+2}:{col}{r_nw+6})", bold=True, fmt=FMT_MM1)
assert CL_TOT_NEW == r_nw + 7
put(cl, f"F{r_nw+2}", "2026 vintage is small because Rochester, Plano, Addison, Grand County and Sunnyvale are already rows above. 2026 signings totalled +200 to +300 vehicle-equivalents.", GREY, italic=True, size=10)
put(cl, f"F{r_nw+3}", "Base 250 / 200 / 175 / 150 sits inside the 2026 signing pace (+200 to +300) and fades; bear 100 / 75 / 60 / 60; bull 300 / 300 / 250 / 250.", GREY, italic=True, size=10)

# ---------- NTD Data sheet ----------
if "NTD Data" in wb.sheetnames: del wb["NTD Data"]
nd = wb.create_sheet("NTD Data", index=wb.sheetnames.index("Contract Layer (KW)") + 1); nd.sheet_view.showGridLines = False
put(nd, "A1", "FTA National Transit Database: purchased-transportation payments to Via entities, by agency and report year ($)", bold=True, size=14)
put(nd, "A2", "Source: NTD Annual Database 'Contractual Relationship' tables RY2019-RY2024 (Direct Payment / Agency Subsidy). Seller names are free text ('VIA', 'River North (VIA)', 'VIA, North River Transit'); matched on a word-boundary 'via' plus subsidiary names, excluding Via Mobility Services (Boulder nonprofit) and RideCo/RideCorp. Report year = agency fiscal year. Regenerated 2026-09-21.", GREY, italic=True)
yrs = ["2019", "2020", "2021", "2022", "2023", "2024"]
for i, h in enumerate(["Agency", "Seller as reported (RY2024)"] + [f"RY{y}" for y in yrs] + ["VOMS under contract (RY2024)", "Fares retained by Via (RY2024)", "Modes"]): put(nd, f"{L(i+1)}4", h, bold=True, border_b=True, size=11, align="center" if i > 1 else None)
nd.column_dimensions["A"].width = 52; nd.column_dimensions["B"].width = 26; nd.column_dimensions["K"].width = 14
rr = 5
for ag, a in sorted(agg.items(), key=lambda x: -x[1]["pay"]):
    if not a["hist"]: continue
    put(nd, f"A{rr}", ag, size=11); put(nd, f"B{rr}", a["op"], size=11)
    for i, y in enumerate(yrs):
        if y in a["hist"]: put(nd, f"{L(3+i)}{rr}", round(a["hist"][y]), BLUE, fmt=FMT_INT, size=11)
    put(nd, f"I{rr}", a["voms"], BLUE, fmt=FMT_INT, size=11); put(nd, f"J{rr}", round(a["fares"]), BLUE, fmt=FMT_INT, size=11); put(nd, f"K{rr}", ", ".join(sorted(a["modes"])), size=11); rr += 1
put(nd, f"A{rr}", "Total, Via entities", bold=True)
for i, y in enumerate(yrs): put(nd, f"{L(3+i)}{rr}", f"=SUM({L(3+i)}5:{L(3+i)}{rr-1})", bold=True, fmt=FMT_INT)
put(nd, f"I{rr}", f"=SUM(I5:I{rr-1})", bold=True, fmt=FMT_INT)
put(nd, f"A{rr+2}", "Reading: payments rose $2.0mm (RY2019) -> $9.7mm -> $17.6mm -> $37.2mm -> $58.6mm -> $96.8mm (RY2024) across 2 -> 26 agencies. LA Metro's Metro Micro was directly operated through RY2024 and will first appear in RY2025 (~Oct 2026). Trinity Metro's RY2024 rows list no Via seller.", GREY, italic=True)

# ---------- SOTP sheet ----------
def wrow(prefix):
    wsx = wb["WACC and Reverse DCF (KW)"]
    for r in range(1, 60):
        v = wsx.cell(r, 2).value
        if isinstance(v, str) and v.strip().lower().startswith(prefix.lower()): return r
    raise KeyError(prefix)
W_EV, W_SH, W_DEBT, W_CASH, W_STI, W_PX = wrow("Enterprise Value"), wrow("Fully Diluted Shares"), wrow("(+) Total Debt"), wrow("(-) Cash"), wrow("(-) Short-Term"), wrow("Current Share Price")
if "SOTP (KW)" in wb.sheetnames: del wb["SOTP (KW)"]
so = wb.create_sheet("SOTP (KW)"); so.sheet_view.showGridLines = False
so.column_dimensions["A"].width = 72; so.column_dimensions["B"].width = 8
for c in "CDEFG": so.column_dimensions[c].width = 13
so.column_dimensions["I"].width = 90
put(so, "A1", "VIA, Sum-of-the-Parts: services and software valued on segment gross profit", bold=True, size=14)
put(so, "A2", "Segment revenue and gross profit link to the Revenue Build; share count, cash and price link to the WACC sheet. Services = labor-intensive operations (transit-operator / rideshare gross-profit multiples); software = vertical SaaS gross-profit multiples.", GREY, italic=True)
put(so, "B4", "Units", align="right", border_b=True)
for j, p in enumerate(("FY2026E", "FY2027E", "FY2028E")): put(so, f"{L(3+j)}4", p, bold=True, align="right", border_b=True)
put(so, "I4", "Notes", GREY, italic=True, border_b=True)
SEGROWS = [("Services revenue", R["svc"], FMT_MM1, True), ("Services gross margin", R["gm_svc"], FMT_PCT, False), ("Services gross profit", R["gp_svc"], FMT_MM1, True),
           ("Software revenue", R["sw"], FMT_MM1, True), ("Software gross margin", R["gm_sw"], FMT_PCT, False), ("Software gross profit", R["gp_sw"], FMT_MM1, True),
           ("Total revenue", R["tot"], FMT_MM1, True), ("Total gross profit (incl. non-recurring uplift)", R["gp_tot"], FMT_MM1, True), ("Blended gross margin", R["gm_blend"], FMT_PCT, False)]
for i, (t, rr, fmt, bold) in enumerate(SEGROWS):
    r = 5 + i; put(so, f"A{r}", t, bold=bold); put(so, f"B{r}", "$mm" if fmt == FMT_MM1 else "%")
    for j, p in enumerate(("FY2026E", "FY2027E", "FY2028E")): put(so, f"{L(3+j)}{r}", f"={RB}!{COL[p]}{rr}", GREEN, italic=True, bold=bold, fmt=fmt)
# valuation on FY2027E (column D of the table above)
put(so, "A15", "Valuation on FY2027E segment gross profit", bold=True, size=14)
V = [("Services EV / gross profit multiple (input)", 2.2, FMT_X, RED, "Lyft trades ~2.2x 2027E gross profit (Bleecker); transit operators (Transdev, Keolis, MV) lower. Sensitivity below 1.5x-4.0x."),
     ("Software EV / gross profit multiple (input)", 10.0, FMT_X, RED, "Vertical SaaS peers ~8x-15x gross profit; sensitivity below."),
     ("Services enterprise value", "=D7*C16", FMT_MM1, BLACK, ""), ("Software enterprise value", "=D10*C17", FMT_MM1, BLACK, ""),
     ("Enterprise value", "=C18+C19", FMT_MM1, BLACK, ""),
     ("(+) Cash and short-term investments", f"={WC}!D{W_CASH}+{WC}!D{W_STI}", FMT_MM1, GREEN, ""), ("(-) Total debt", f"={WC}!D{W_DEBT}", FMT_MM1, GREEN, ""),
     ("Equity value", "=C20+C21-C22", FMT_MM1, BLACK, ""), ("Fully diluted shares (mm)", f"={WC}!D{W_SH}", FMT_MM1, GREEN, ""),
     ("SOTP value per share", "=C23/C24", '"$"#,##0.00', BLACK, ""), ("Current share price", f"={WC}!D{W_PX}", '"$"#,##0.00', GREEN, ""), ("Implied upside / (downside)", "=C25/C26-1", FMT_PCT, BLACK, ""),
     ("Memo: DCF blended value per share (DCF + EPS sheet)", "='DCF + EPS (KW)'!D81", '"$"#,##0.00', GREEN, "The DCF runs off the same revenue and gross-profit path with the Three Statements opex assumptions."),
     ("Memo: SOTP enterprise value / FY2027E revenue", "=C20/D11", FMT_X, BLACK, "")]
for i, (t, f, fmt, colr, nt) in enumerate(V):
    r = 16 + i; put(so, f"A{r}", t, bold=t in ("Enterprise value", "Equity value", "SOTP value per share")); put(so, f"C{r}", f, colr, italic=(colr in (GREEN, RED)), bold=t in ("Enterprise value", "Equity value", "SOTP value per share"), fmt=fmt)
    if nt: put(so, f"I{r}", nt, GREY, italic=True)
put(so, "A31", "What the current share price implies", bold=True, size=14)
M = [("Market enterprise value (WACC sheet)", f"={WC}!D{W_EV}", FMT_MM1, GREEN), ("(-) Services enterprise value at the input multiple", "=C18", FMT_MM1, BLACK),
     ("Implied software enterprise value", "=C32-C33", FMT_MM1, BLACK), ("Implied software EV / FY2027E software gross profit", "=IF(D10=0,0,C34/D10)", FMT_X, BLACK),
     ("Implied software EV / FY2027E software revenue", "=IF(D8=0,0,C34/D8)", FMT_X, BLACK),
     ("Services multiple needed to justify the price with software at the input multiple", "=IF(D7=0,0,(C32-C19)/D7)", FMT_X, BLACK)]
for i, (t, f, fmt, colr) in enumerate(M):
    r = 32 + i; put(so, f"A{r}", t, bold=(i in (2, 3))); put(so, f"C{r}", f, colr, italic=(colr == GREEN), bold=(i in (2, 3)), fmt=fmt)
put(so, "I34", "The market pays a SaaS multiple for a gross-profit pool that is ~half services at a ~26% margin.", GREY, italic=True)
put(so, "A39", "Scenarios (FY2027E gross profit; value per share)", bold=True, size=14)
for j, h in enumerate(("Services x GP", "Software x GP", "Enterprise value", "Value per share", "vs. current price")): put(so, f"{L(3+j)}40", h, bold=True, align="right", border_b=True, size=11)
put(so, "A40", "Scenario", bold=True, border_b=True, size=11)
for k, (name, sm, wm) in enumerate((("Bear", 1.5, 6.0), ("Base", 2.2, 10.0), ("Bull", 4.0, 15.0))):
    r = 41 + k; put(so, f"A{r}", name); put(so, f"C{r}", sm, RED, italic=True, fmt=FMT_X); put(so, f"D{r}", wm, RED, italic=True, fmt=FMT_X)
    put(so, f"E{r}", f"=$D$7*C{r}+$D$10*D{r}", fmt=FMT_MM1); put(so, f"F{r}", f"=(E{r}+$C$21-$C$22)/$C$24", fmt='"$"#,##0.00'); put(so, f"G{r}", f"=F{r}/$C$26-1", fmt=FMT_PCT)
put(so, "A46", "Sensitivity: value per share  |  rows: services EV / gross profit  |  columns: software EV / gross profit", bold=True, size=14)
put(so, "A47", "Services multiple  \\  Software multiple", bold=True, border_b=True, size=11)
for j, m in enumerate((6, 8, 10, 12, 15)): put(so, f"{L(3+j)}47", m, RED, italic=True, fmt=FMT_X, border_b=True, align="right")
for i, sm in enumerate((1.5, 2.2, 3.0, 4.0)):
    r = 48 + i; put(so, f"A{r}", sm, RED, italic=True, fmt=FMT_X)
    for j in range(5): put(so, f"{L(3+j)}{r}", f"=($D$7*$A{r}+$D$10*{L(3+j)}$47+$C$21-$C$22)/$C$24", fmt='"$"#,##0.00')
put(so, "A53", "Sensitivity: value per share  |  rows: services gross margin applied to FY2027E services revenue (services at the input multiple)  |  columns: software EV / gross profit", bold=True, size=14)
put(so, "A54", "Services gross margin  \\  Software multiple", bold=True, border_b=True, size=11)
for j, m in enumerate((6, 8, 10, 12, 15)): put(so, f"{L(3+j)}54", m, RED, italic=True, fmt=FMT_X, border_b=True, align="right")
for i, g in enumerate((0.22, 0.24, 0.26, 0.28, 0.30)):
    r = 55 + i; put(so, f"A{r}", g, RED, italic=True, fmt=FMT_PCT)
    for j in range(5): put(so, f"{L(3+j)}{r}", f"=(($D$5*$A{r})*$C$16+$D$10*{L(3+j)}$54+$C$21-$C$22)/$C$24", fmt='"$"#,##0.00')
put(so, "A61", "The margin sensitivity holds FY2027E segment revenues fixed; changing the services GM input on the Revenue Build also moves the historical split and the software residual.", GREY, italic=True)

# ---------- re-point Three Statements (revenue row 7, cost of revenue % row 11) ----------
for p in QTR26 + QTR27 + ["FY2028E", "FY2029E", "FY2030E"] + FADE:
    c = COL[p]; put(ts, f"{c}7", f"={RB}!{c}{R['tot']}", GREEN, italic=True, bold=True, fmt=FMT_MM1)
for p in QTR26 + QTR27: put(ts, f"{COL[p]}11", f"={RB}!{COL[p]}{R['cogs']}", GREEN, italic=True, fmt=FMT_PCT)
for p in ("FY2028E", "FY2029E", "FY2030E") + tuple(FADE): put(ts, f"{COL[p]}11", f"={RB}!{COL[p]}{R['cogs']}", GREEN, italic=True, fmt=FMT_PCT)
ts["AB7"].value = "Projected periods link to the Revenue Build total (row %d), 2026-09-21." % R["tot"]; ts["AB7"].font = font(GREY, italic=True)
ts["AB11"].value = "Projected cost of revenue %% links to the Revenue Build gross-profit block (row %d): segment mix x segment margins, plus a fading implementation-fee uplift (2026-09-21)." % R["cogs"]; ts["AB11"].font = font(GREY, italic=True)
# ---------- Three Statements: operating-expense ratios for a services-heavy mix (FY2028E-FY2035E; 2026-27 quarterly inputs untouched) ----------
OPEX = {16: ("Research & development", [0.155, 0.14, 0.125, 0.115, 0.105, 0.095, 0.09, 0.085], "was 16.0% -> 12.0%"),
        18: ("Sales & marketing", [0.125, 0.115, 0.105, 0.095, 0.09, 0.085, 0.08, 0.075], "was 13.5% -> 10.0%"),
        20: ("General & administrative", [0.16, 0.145, 0.13, 0.12, 0.11, 0.10, 0.095, 0.09], "was 17.5% -> 12.0%")}
for row, (name, path, was) in OPEX.items():
    for p, val in zip(["FY2028E", "FY2029E", "FY2030E", "FY2031E", "FY2032E", "FY2033E", "FY2034E", "FY2035E"], path):
        cell = ts[f"{COL[p]}{row}"]; cell.value = val; cell.font = font(RED, italic=True); cell.number_format = FMT_PCT
    ts[f"AB{row}"].value = (f"{name} % of revenue, FY2028E-FY2035E ({was}), reset 2026-09-21 for a mix that is ~75% services: total opex steps from 50% of revenue "
                            f"(FY2027E) to 44% (FY2028E) and 25% (FY2035E). Mix-weighted floor: software-company opex ~37% x 24% share + operator overhead ~10% x 76% share = ~16.5%; "
                            f"the path stays above it for platform cost. In dollars, {name.lower()} grows ~1%-2% a year 2025-35.")
    ts[f"AB{row}"].font = font(GREY, italic=True)
# ---------- re-point Summary customers (row 21) ----------
for sc_, rc_ in (("D", "C"), ("E", "D"), ("F", "I"), ("G", "N"), ("H", "S"), ("I", "T"), ("J", "U"), ("K", "V")):
    cell = summ[f"{sc_}21"]; cell.value = f"={RB}!{rc_}{R['cust_tot']}"
# ---------- Cover: TOC entries, description, checks flag ----------
toc_names = {str(cover.cell(r, 5).value): r for r in range(5, 40) if cover.cell(r, 5).value}
if "Contract Layer (KW)" not in toc_names:
    merges = [str(m) for m in cover.merged_cells.ranges]
    def shift(rng, at, n):
        m = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", rng); c1, r1, c2, r2 = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
        return f"{c1}{r1+n if r1>=at else r1}:{c2}{r2+n if r2>=at else r2}"
    for m in merges: cover.unmerge_cells(m)
    heights = {r: cover.row_dimensions[r].height for r in range(1, cover.max_row + 1) if cover.row_dimensions[r].height}
    cover.insert_rows(12, 3)
    for m in merges: cover.merge_cells(shift(m, 12, 3))
    for r, h in sorted(heights.items(), reverse=True): cover.row_dimensions[r + 3 if r >= 12 else r].height = h
    for k, (name, desc) in enumerate([("Contract Layer (KW)", "Contract-level services engine: 59 documented US operations contracts with dates, funding tags, hazards; unsigned-win vintages"),
                                      ("NTD Data", "FTA NTD purchased-transportation payments to Via entities, RY2019-RY2024 (evidence base for the services book)"),
                                      ("SOTP (KW)", "Sum-of-the-parts on FY2027E segment gross profit, market-implied software multiple, scenarios and sensitivities")]):
        r = 12 + k; c = cover[f"E{r}"]; c.value = name; c.font = copy(cover["E11"].font); c.alignment = copy(cover["E11"].alignment)
        c.hyperlink = Hyperlink(ref=f"E{r}", location=f"'{name}'!A1", display=name)
        d = cover[f"F{r}"]; d.value = desc; d.font = copy(cover["F11"].font); d.alignment = copy(cover["F11"].alignment)
        cover.row_dimensions[r].height = cover.row_dimensions[11].height
    for col in "EF":
        b11 = copy(cover[f"{col}11"].border); cover[f"{col}14"].border = copy(b11)
        cover[f"{col}11"].border = Border(left=b11.left, right=b11.right, top=b11.top)
        for r in (12, 13): cover[f"{col}{r}"].border = Border(left=b11.left, right=b11.right)
    toc_names = {str(cover.cell(r, 5).value): r for r in range(5, 40) if cover.cell(r, 5).value}
cover[f"F{toc_names['Revenue Build (KW)']}"].value = "Revenue build by segment (services / software): contract-level services engine, software engine, gross profit by segment, growth bridge, checks"
flag_row = next((r for r in range(5, 45) if str(cover.cell(r, 2).value).startswith("Revenue model checks")), None)
if flag_row is None:
    flag_row = max(r for r in range(5, 45) if cover.cell(r, 2).value) + 1
    put(cover, f"B{flag_row}", "Revenue model checks (Revenue Build)"); cover[f"B{flag_row}"].font = copy(cover[f"B{flag_row-1}"].font)
cover[f"C{flag_row}"].value = f"={RB}!{N_}{r_flag}"; cover[f"C{flag_row}"].font = font(GREEN, italic=True)
for r in range(5, 45):
    v = cover.cell(r, 5).value
    if isinstance(v, str) and "added 2026-09-21" in v: cover.cell(r, 5).value = None

# ---------- order and save ----------
for name in ("Contract Layer (KW)", "NTD Data"):
    ws = wb[name]; wb._sheets.remove(ws); wb._sheets.insert(wb.sheetnames.index("Revenue Build (KW)") + (1 if name.startswith("Contract") else 2), ws)
ws = wb["SOTP (KW)"]; wb._sheets.remove(ws); wb._sheets.insert(wb.sheetnames.index("DCF + EPS (KW)") + 1, ws)
for o in OUT: wb.save(o)
print("saved:", OUT, "| checks flag:", f"{N_}{r_flag}", "| contract rows:", len(contracts), "| CL totals rows:", CL_TOT_HARD, CL_TOT_NEW)
