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
print(f"contract rows: {len(contracts)}; tags {collections.Counter(c['tag'] for c in contracts)}")

# ---------- open workbook ----------
wb = openpyxl.load_workbook(SRC)
rb = wb["Revenue Build (KW)"]; ts = wb["Three Statements (KW)"]; cover = wb["Cover"]
# preserve reported values already on the sheet
keep = {}
for r in (8, 12, 16, 20, 25, 26, 30, 36, 37, 38):
    for p in PER:
        v = rb[f"{COL[p]}{r}"].value
        if v is not None and not (isinstance(v, str) and v.startswith("=")): keep[(r, p)] = v
# clear sheet
for rng in list(rb.merged_cells.ranges): rb.unmerge_cells(str(rng))
rb.delete_rows(1, rb.max_row + 5)
for col in range(3, 28): rb.column_dimensions[L(col)].width = 11
rb.column_dimensions["A"].width = 58; rb.column_dimensions["B"].width = 8; rb.column_dimensions["AB"].width = 90
rb.freeze_panes = "C5"; rb.sheet_view.showGridLines = False

def header(ws, title, subtitle, years=True):
    put(ws, "A1", title, bold=True, size=14); put(ws, "A2", subtitle, GREY, italic=True)
    if years:
        put(ws, "A3", "Fiscal Year", bold=True, size=14); put(ws, "B3", "Historical", bold=True, size=14, align="center"); put(ws, f"{COL['3Q26E']}3", "Projected", bold=True, size=14, align="center")
        put(ws, "B4", "Units", align="right", border_b=True)
        for p in PER: put(ws, f"{COL[p]}4", p, align="right", border_b=True)
        put(ws, "AB4", "Notes / sources", GREY, italic=True, border_b=True)

header(rb, "VIA, Revenue Projection Model", "Filings-anchored segment split, contract-level services engine, software engine, margin bridge and checks  |  $ in millions unless noted  |  rebuilt 2026-09-21")

def label(ws, row, text, units="", bold=False, italic=False, color=BLACK, size=12):
    put(ws, f"A{row}", text, color, bold, italic, size=size)
    if units: put(ws, f"B{row}", units)

# ---------- Section A: revenue by geography (rows 6-22) ----------
label(rb, 6, "Revenue Projection Model", bold=True, size=14)
label(rb, 7, "Revenue by Geography (drives Total Revenue; annual projections come from the engines below)", bold=True)
GEO = {8: ("United States", {"FY2023A": 167.558, "FY2024A": 221.003}), 12: ("Germany", {"FY2023A": 43.815, "FY2024A": 78.527}), 16: ("All Other Countries", {"FY2023A": 37.481, "FY2024A": 38.100})}
# engine row numbers (defined below) referenced here
R = dict(svc_hard=64, svc_new=65, svc_dt=66, svc_plug=67, svc_us=68, svc_de=69, svc_oth=70, svc_tot=71, svc_us_split=72, memo_imputed=73,
         in_sgm=77, in_de_share=78, in_oth_share=79, in_dt26=80, in_dt_g=81, in_plug_g=82, in_2h_us=83, in_2h_de=84, in_2h_oth=85, in_us_fade=86,
         sw_tot=89, sw_de=90, sw_oth=91, sw_named=92, sw_small=93, sw_us=94, sw_g=95, sw_acv=96, in_logo=98, in_exp=99, in_churn=100, in_doe_p=101, in_sw26=102,
         cust_tk=104, cust_sw=105, cust_dt=106, cust_tot=107, in_tk_adds=108,
         gm_svc=112, gm_sw=113, gm_blend=114, gm_svc_share=115, gm_cogs=116, gm_uplift=117,
         br_hdr=119, chk_hdr=134)
for r, (name, hist) in GEO.items():
    label(rb, r, name, "$mm", bold=True)
    label(rb, r + 1, "% Growth (YoY)", "%", italic=True); label(rb, r + 2, "% of Total Revenue", "%", italic=True)
    for p in PER:
        c = COL[p]; ref = f"{c}{r}"
        if p in hist: put(rb, ref, hist[p], BLUE, bold=True, fmt=FMT_MM)
        elif (r, p) in keep: put(rb, ref, keep[(r, p)], BLUE, bold=True, fmt=FMT_MM)
        elif p == "FY2025A": put(rb, ref, f"=SUM({COL['1Q25A']}{r}:{COL['4Q25A']}{r})", bold=True, fmt=FMT_MM)
        elif p == "FY2026E":
            g2h = {8: R["in_2h_us"], 12: R["in_2h_de"], 16: R["in_2h_oth"]}[r]
            put(rb, ref, f"={COL['1Q26A']}{r}+{COL['2Q26A']}{r}+({COL['3Q25A']}{r}+{COL['4Q25A']}{r})*(1+${COL['FY2026E']}${g2h})", bold=True, fmt=FMT_MM)
        elif p == "FY2027E": put(rb, ref, {8: f"={c}{R['svc_us']}+{c}{R['sw_us']}", 12: f"={COL['FY2026E']}{r}*(1+{c}{r+1})", 16: f"={COL['FY2026E']}{r}*(1+{c}{r+1})"}[r], bold=True, fmt=FMT_MM)
        elif p in ("FY2028E", "FY2029E", "FY2030E"): put(rb, ref, {8: f"={c}{R['svc_us']}+{c}{R['sw_us']}", 12: f"={COL[PREV[p]]}{r}*(1+{c}{r+1})", 16: f"={COL[PREV[p]]}{r}*(1+{c}{r+1})"}[r], bold=True, fmt=FMT_MM)
        elif p in FADE: put(rb, ref, f"={COL[PREV[p]]}{r}*(1+{c}{r+1})", bold=True, fmt=FMT_MM)
        elif p in QTR26:
            g, h = COL["3Q25A"], COL["4Q25A"]; me = COL[p == "3Q26E" and "3Q25A" or "4Q25A"]
            put(rb, ref, f"=({COL['FY2026E']}{r}-{COL['1Q26A']}{r}-{COL['2Q26A']}{r})*{me}{r}/({g}{r}+{h}{r})", bold=True, fmt=FMT_MM)
        elif p in QTR27:
            q = Q25[QTR27.index(p)]; put(rb, ref, f"={COL['FY2027E']}{r}*{COL[q]}{r}/{COL['FY2025A']}{r}", bold=True, fmt=FMT_MM)
        # growth row
        gref = f"{c}{r+1}"
        if r == 8 and p in FADE: put(rb, gref, {"FY2031E": 0.08, "FY2032E": 0.07, "FY2033E": 0.06, "FY2034E": 0.05, "FY2035E": 0.05}[p], RED, italic=True, fmt=FMT_PCT)
        elif r == 12 and p in ("FY2027E", "FY2028E", "FY2029E", "FY2030E") + tuple(FADE): put(rb, gref, {"FY2027E": -0.05, "FY2028E": 0.0, "FY2029E": 0.0, "FY2030E": 0.0}.get(p, 0.0), RED, italic=True, fmt=FMT_PCT)
        elif r == 16 and p in ("FY2027E", "FY2028E", "FY2029E", "FY2030E") + tuple(FADE): put(rb, gref, {"FY2027E": 0.20, "FY2028E": 0.15, "FY2029E": 0.10, "FY2030E": 0.08}.get(p, 0.06), RED, italic=True, fmt=FMT_PCT)
        elif p in ANN and p != "FY2023A": put(rb, gref, f"=IF({COL[PREV[p]]}{r}=0,0,{c}{r}/{COL[PREV[p]]}{r}-1)", italic=True, fmt=FMT_PCT)
        elif p in ("1Q26A", "2Q26A", "3Q26E", "4Q26E"): put(rb, gref, f"=IF({COL[Q25[['1Q26A','2Q26A','3Q26E','4Q26E'].index(p)]]}{r}=0,0,{c}{r}/{COL[Q25[['1Q26A','2Q26A','3Q26E','4Q26E'].index(p)]]}{r}-1)", italic=True, fmt=FMT_PCT)
        elif p in QTR27: put(rb, gref, f"=IF({COL[['1Q26A','2Q26A','3Q26E','4Q26E'][QTR27.index(p)]]}{r}=0,0,{c}{r}/{COL[['1Q26A','2Q26A','3Q26E','4Q26E'][QTR27.index(p)]]}{r}-1)", italic=True, fmt=FMT_PCT)
        put(rb, f"{c}{r+2}", f"=IF({c}20=0,0,{c}{r}/{c}20)", italic=True, fmt=FMT_PCT)
note(rb, 8, "FY2023A-FY2025A and quarters: 10-K FY2025 Note 'Revenue by geographic area' (p.101) and 10-Qs. FY2026E-FY2030E = US services engine + US software engine (rows below). 3Q/4Q26E split by 2025 3Q/4Q shares; 2027 quarters by 2025 quarterly shares. FY2031E+ fade inputs (red).")
note(rb, 12, "Germany: Muva (Berlin, ~EUR10mm ViaVan operations contract) ended 2026-02-28; 2Q26 -12% YoY. Growth inputs red; services share of Germany set in the inputs block (default 75%: not disclosed).")
note(rb, 16, "All other countries: +41% in 1H26 off a small base; growth inputs red; services share default 50% (not disclosed).")
label(rb, 20, "Total Revenue", "$mm", bold=True); label(rb, 21, "% Growth (YoY)", "%", italic=True); label(rb, 22, "Check vs. Three Statements revenue (should be 0)", "$mm", italic=True, color=GREY)
for p in PER:
    c = COL[p]; put(rb, f"{c}20", f"={c}8+{c}12+{c}16", bold=True, fmt=FMT_MM)
    if p in ANN and p != "FY2023A": put(rb, f"{c}21", f"=IF({COL[PREV[p]]}20=0,0,{c}20/{COL[PREV[p]]}20-1)", italic=True, fmt=FMT_PCT)
    elif p in ("1Q26A", "2Q26A", "3Q26E", "4Q26E"): put(rb, f"{c}21", f"=IF({COL[Q25[['1Q26A','2Q26A','3Q26E','4Q26E'].index(p)]]}20=0,0,{c}20/{COL[Q25[['1Q26A','2Q26A','3Q26E','4Q26E'].index(p)]]}20-1)", italic=True, fmt=FMT_PCT)
    elif p in QTR27: put(rb, f"{c}21", f"=IF({COL[['1Q26A','2Q26A','3Q26E','4Q26E'][QTR27.index(p)]]}20=0,0,{c}20/{COL[['1Q26A','2Q26A','3Q26E','4Q26E'][QTR27.index(p)]]}20-1)", italic=True, fmt=FMT_PCT)
    put(rb, f"{c}22", f"=ROUND({c}20-{TS}!{c}7,3)", GREEN, italic=True, fmt=FMT_MM1)
note(rb, 20, "Total = sum of geographies in every period (the earlier version grew the total off its own 26.7% input). Three Statements row 7 links here.")

# ---------- Section B: customer type memo and KPIs (rows 24-38; row 30 = customers, referenced by Summary) ----------
label(rb, 24, "Revenue by Customer Type (memo)", bold=True)
label(rb, 25, "Government / Public Sector", "$mm"); label(rb, 26, "Commercial", "$mm"); label(rb, 27, "Government % of Revenue", "%", italic=True)
for p in PER:
    c = COL[p]
    if (25, p) in keep: put(rb, f"{c}25", keep[(25, p)], BLUE, fmt=FMT_MM); put(rb, f"{c}26", keep[(26, p)], BLUE, fmt=FMT_MM); put(rb, f"{c}27", f"=IF({c}20=0,0,{c}25/{c}20)", italic=True, fmt=FMT_PCT)
    elif p == "FY2025A": put(rb, f"{c}25", f"=SUM({COL['1Q25A']}25:{COL['4Q25A']}25)", fmt=FMT_MM); put(rb, f"{c}26", f"=SUM({COL['1Q25A']}26:{COL['4Q25A']}26)", fmt=FMT_MM); put(rb, f"{c}27", f"=IF({c}20=0,0,{c}25/{c}20)", italic=True, fmt=FMT_PCT)
    elif p in ("FY2026E", "FY2027E"): put(rb, f"{c}25", f"=SUM({COL['1Q26A' if p=='FY2026E' else '1Q27E']}25:{COL['4Q26E' if p=='FY2026E' else '4Q27E']}25)", fmt=FMT_MM); put(rb, f"{c}26", f"=SUM({COL['1Q26A' if p=='FY2026E' else '1Q27E']}26:{COL['4Q26E' if p=='FY2026E' else '4Q27E']}26)", fmt=FMT_MM); put(rb, f"{c}27", f"=IF({c}20=0,0,{c}25/{c}20)", italic=True, fmt=FMT_PCT)
    else: put(rb, f"{c}27", 0.935, RED, italic=True, fmt=FMT_PCT); put(rb, f"{c}25", f"={c}20*{c}27", fmt=FMT_MM); put(rb, f"{c}26", f"={c}20-{c}25", fmt=FMT_MM)
note(rb, 26, "10-K/10-Q 'Revenue by customer type'. Commercial was $26.6mm / $26.6mm / $27.9mm in 2023-25: flat. The undocumented software base is therefore not a growing private-sector book.")
label(rb, 29, "Key Performance Indicators", bold=True)
label(rb, 30, "Customers (period-end, distinct legal entities generating Platform revenue)", "#", bold=True); label(rb, 31, "% Growth (YoY)", "%", italic=True)
label(rb, 32, "Organic customers (ex-Downtowner's 94)", "#", italic=True); label(rb, 33, "Platform Annual Run-Rate Revenue (quarterly revenue x 4)", "$mm", italic=True)
label(rb, 34, "Annualized Revenue per Average Customer", "$000", italic=True)
label(rb, 36, "Platform Net Revenue Retention (as reported)", "%"); label(rb, 37, "Gross Revenue Retention (as reported)", "%"); label(rb, 38, "Remaining Performance Obligations", "$mm")
Q26 = ["1Q26A", "2Q26A", "3Q26E", "4Q26E"]
for p in PER:
    c = COL[p]
    if (30, p) in keep: put(rb, f"{c}30", keep[(30, p)], BLUE, bold=True, fmt=FMT_INT)
    elif p in ("FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E"): put(rb, f"{c}30", f"=ROUND({c}{R['cust_tot']},0)", bold=True, fmt=FMT_INT)
    elif p in FADE: put(rb, f"{c}30", f"=ROUND({COL[PREV[p]]}30*(1+{c}31),0)", bold=True, fmt=FMT_INT); put(rb, f"{c}31", 0.05, RED, italic=True, fmt=FMT_PCT)
    elif p == "3Q26E": put(rb, f"{c}30", f"=ROUND({COL['2Q26A']}30+({COL['FY2026E']}30-{COL['2Q26A']}30)/2,0)", bold=True, fmt=FMT_INT)
    elif p == "4Q26E": put(rb, f"{c}30", f"={COL['FY2026E']}30", bold=True, fmt=FMT_INT)
    elif p in QTR27: k = QTR27.index(p) + 1; put(rb, f"{c}30", f"=ROUND({COL['FY2026E']}30+({COL['FY2027E']}30-{COL['FY2026E']}30)*{k}/4,0)", bold=True, fmt=FMT_INT)
    if p not in FADE:
        if p in ANN and p != "FY2023A": put(rb, f"{c}31", f"=IF({COL[PREV[p]]}30=0,0,{c}30/{COL[PREV[p]]}30-1)", italic=True, fmt=FMT_PCT)
        elif p in Q26: put(rb, f"{c}31", f"=IF({COL[Q25[Q26.index(p)]]}30=0,0,{c}30/{COL[Q25[Q26.index(p)]]}30-1)", italic=True, fmt=FMT_PCT)
        elif p in QTR27: put(rb, f"{c}31", f"=IF({COL[Q26[QTR27.index(p)]]}30=0,0,{c}30/{COL[Q26[QTR27.index(p)]]}30-1)", italic=True, fmt=FMT_PCT)
    if p in ("FY2025A", "4Q25A") or p >= "1Q26A" and p not in ("FY2023A", "FY2024A"): pass
    dtc = 94 if (p in ("4Q25A", "FY2025A") or PER.index(p) >= PER.index("1Q26A")) else 0
    put(rb, f"{c}32", f"={c}30-{dtc}", italic=True, fmt=FMT_INT)
    if p not in ANN: put(rb, f"{c}33", f"={c}20*4", italic=True, fmt=FMT_MM)
    if p in ANN and p != "FY2023A": put(rb, f"{c}34", f"=IF(AVERAGE({COL[PREV[p]]}30,{c}30)=0,0,{c}20/AVERAGE({COL[PREV[p]]}30,{c}30)*1000)", italic=True, fmt=FMT_INT)
    for r in (36, 37, 38):
        if (r, p) in keep: put(rb, f"{c}{r}", keep[(r, p)], BLUE, fmt=FMT_PCT if r < 38 else FMT_MM1)
note(rb, 30, "10-K/10-Q KPI: 665 (Dec-24), 689 (Jun-25), 821 (Dec-25, incl. 94 from Downtowner), 847 (Jun-26). Projections from the customer engine (turnkey + software + Downtowner) below; quarters interpolated.")
note(rb, 32, "Organic growth 9.3% (Jun-26 vs Jun-25) is total-count growth. Operations customers (~15%-20% of the count) grew faster, so software net logo growth is ~6%-7%.")
note(rb, 38, "RPO $294.4mm at Dec-25 (60% recognized in 2026, 27% in 2027); $318.3mm at Jun-26 (37% due in 2027).")
label(rb, 40, "Guidance Check", bold=True)
label(rb, 41, "Revenue Guidance - Low", "$mm"); label(rb, 42, "Revenue Guidance - High", "$mm"); label(rb, 43, "Model vs. Guidance Midpoint", "%", italic=True)
for p in ("FY2026E",):
    c = COL[p]; put(rb, f"{c}41", f"={SC}!{c}22", GREEN, italic=True, fmt=FMT_MM1); put(rb, f"{c}42", f"={SC}!{c}23", GREEN, italic=True, fmt=FMT_MM1)
    put(rb, f"{c}43", f"=IF(AVERAGE({c}41,{c}42)=0,0,{c}20/AVERAGE({c}41,{c}42)-1)", italic=True, fmt=FMT_PCT)
note(rb, 41, "8-K 2026-08-06: FY2026 revenue $550mm-$553mm; adjusted EBITDA $(12.5)mm-$(7.5)mm.")

# ---------- Section C: segment split (rows 45-58) ----------
SP = dict(cost=46, other=47, loaded=48, gm=49, svc=50, sw=51, svc_sh=52, sw_sh=53, svc_g=54, sw_g=55, sw_cost=56, sw_gm=57, alloc=58, ls_share=59, chk=60)
label(rb, 45, "Segment Split: services vs. software from the cost-of-revenue identity (annual)", bold=True, size=14)
label(rb, SP["cost"], "Technology-enabled services cost (drivers, fleet, customer support)", "$mm")
label(rb, SP["other"], "Other cost of revenue (launch/support personnel + IT and other) = total cost of revenue - services cost", "$mm")
label(rb, SP["loaded"], "Loaded services cost = services cost + services share of launch/support personnel", "$mm")
label(rb, SP["gm"], "Services gross margin, loaded basis (input; identity band 20%-32%)", "%", italic=True)
label(rb, SP["svc"], "Services revenue = loaded services cost / (1 - services GM)", "$mm", bold=True)
label(rb, SP["sw"], "Software revenue (residual = total - services)", "$mm", bold=True)
label(rb, SP["svc_sh"], "Services % of revenue", "%", italic=True); label(rb, SP["sw_sh"], "Software % of revenue", "%", italic=True)
label(rb, SP["svc_g"], "Services revenue growth", "%", italic=True); label(rb, SP["sw_g"], "Software revenue growth", "%", italic=True)
label(rb, SP["sw_cost"], "Software cost of revenue = IT and other + software share of launch/support personnel", "$mm")
label(rb, SP["sw_gm"], "Implied software gross margin", "%", italic=True)
label(rb, SP["alloc"], "Launch/support personnel allocated to software (input)", "%", italic=True)
label(rb, SP["ls_share"], "Launch/support personnel as a share of other cost of revenue (FY2025: $25.8mm of $39.1mm)", "%", italic=True)
label(rb, SP["chk"], "Check: services GP + software GP - reported gross profit (should be 0)", "$mm", italic=True, color=GREY)
SVC_COST = {"FY2023A": 117.5, "FY2024A": 167.7, "FY2025A": 223.5}
A_, LS_ = f"${COL['FY2025A']}${SP['alloc']}", f"${COL['FY2025A']}${SP['ls_share']}"
for p in ("FY2023A", "FY2024A", "FY2025A"):
    c = COL[p]; put(rb, f"{c}{SP['cost']}", SVC_COST[p], BLUE, fmt=FMT_MM1)
    put(rb, f"{c}{SP['other']}", f"={TS}!{c}10-{c}{SP['cost']}", GREEN, italic=True, fmt=FMT_MM1)
    put(rb, f"{c}{SP['loaded']}", f"={c}{SP['cost']}+(1-{A_})*{LS_}*{c}{SP['other']}", fmt=FMT_MM1)
    put(rb, f"{c}{SP['gm']}", f"=${COL['FY2026E']}${R['in_sgm']}", italic=True, fmt=FMT_PCT)
    put(rb, f"{c}{SP['svc']}", f"={c}{SP['loaded']}/(1-{c}{SP['gm']})", bold=True, fmt=FMT_MM1); put(rb, f"{c}{SP['sw']}", f"={c}20-{c}{SP['svc']}", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{SP['svc_sh']}", f"={c}{SP['svc']}/{c}20", italic=True, fmt=FMT_PCT); put(rb, f"{c}{SP['sw_sh']}", f"={c}{SP['sw']}/{c}20", italic=True, fmt=FMT_PCT)
    if p != "FY2023A": put(rb, f"{c}{SP['svc_g']}", f"={c}{SP['svc']}/{COL[PREV[p]]}{SP['svc']}-1", italic=True, fmt=FMT_PCT); put(rb, f"{c}{SP['sw_g']}", f"={c}{SP['sw']}/{COL[PREV[p]]}{SP['sw']}-1", italic=True, fmt=FMT_PCT)
    put(rb, f"{c}{SP['sw_cost']}", f"={c}{SP['other']}-({c}{SP['loaded']}-{c}{SP['cost']})", fmt=FMT_MM1)
    put(rb, f"{c}{SP['sw_gm']}", f"=1-{c}{SP['sw_cost']}/{c}{SP['sw']}", italic=True, fmt=FMT_PCT)
    put(rb, f"{c}{SP['chk']}", f"=ROUND(({c}{SP['svc']}-{c}{SP['loaded']})+({c}{SP['sw']}-{c}{SP['sw_cost']})-({TS}!{c}7-{TS}!{c}10),3)", GREEN, italic=True, fmt=FMT_MM1)
c = COL["FY2025A"]
put(rb, f"{c}{SP['alloc']}", 0.5, RED, italic=True, fmt=FMT_PCT); put(rb, f"{c}{SP['ls_share']}", 25.8 / 39.1, BLUE, italic=True, fmt=FMT_PCT)
note(rb, SP["cost"], "10-K FY2025 MD&A: cost of revenue $262.5mm = $223.5mm technology-enabled services + $25.8mm launch and support personnel + $13.3mm IT and other. 2024 and 2023 from the MD&A change sentences (+$55.8mm; +$50.2mm). 1H26 est. $137.5mm (10-Q deltas +$18.0mm 1Q, +$13.6mm 2Q on a pro-rated 1H25).")
note(rb, SP["other"], "Other cost of revenue was $31.9mm / $39.1mm / $39.0mm in 2023-25: flat, so software cost of revenue is not growing with software revenue.")
note(rb, SP["gm"], "Loaded basis (Bleecker's 26% is on this basis; on technology-enabled services cost alone the same split is ~30%). Default 26%: it is the value at which the documented US operations book (NTD $96.8mm + census-priced contracts) fits inside the split with a positive undocumented plug. Cases 22% / 30%.")
note(rb, SP["svc"], "The split ties to reported totals by construction; its implications (services share, implied software GM, implied ACV, the US plug) are what the checks test.")
note(rb, SP["sw_gm"], "Should land 70%-80%. Corner cases fail: all launch/support on software at 80% GM implies services at 6% margin.")

# ---------- Section D: services engine (rows 62-73) + inputs (75-85) ----------
label(rb, 62, "Services Engine (annual; contract-level detail on 'Contract Layer (KW)')", bold=True, size=14)
label(rb, 63, "United States", bold=True)
label(rb, R["svc_hard"], "Documented contracts: NTD-paid + census-priced (57 rows incl. signed 2025-26 wins), after haircut, hazards and expiries", "$mm")
label(rb, R["svc_new"], "Unsigned new wins (vehicle-equivalent vintages, ramped)", "$mm")
label(rb, R["svc_dt"], "Downtowner (acquired 2025-12-12; revenue undisclosed)", "$mm")
label(rb, R["svc_plug"], "Undocumented and unpriced US services (plug = US services from the split - documented, then grown)", "$mm")
label(rb, R["svc_us"], "US services revenue", "$mm", bold=True)
label(rb, R["svc_de"], "Germany services (= Germany revenue x services share)", "$mm")
label(rb, R["svc_oth"], "Other international services (= other revenue x services share)", "$mm")
label(rb, R["svc_tot"], "Total services revenue (engine)", "$mm", bold=True)
label(rb, R["svc_us_split"], "Memo: US services implied by the split (services revenue - international services)", "$mm", italic=True)
label(rb, R["memo_imputed"], "Memo: imputed value of 22 documented-but-unpriced US operators ($0.9mm each) + app-only agencies (30% x $0.8mm x 108) - a floor for the plug", "$mm", italic=True)
CLY = {"FY2024A": "S", "FY2025A": "T", "FY2026E": "U", "FY2027E": "V", "FY2028E": "W", "FY2029E": "X", "FY2030E": "Y"}   # Contract Layer year columns
CL_TOT_HARD = 6 + len(contracts) + 2   # Contract Layer: contracts start row 6, totals two rows after the last contract
CL_TOT_NEW = CL_TOT_HARD + 33           # inputs (+4), hazard table (+10), vintages (+12), total (+7); asserted below
for p in ENG:
    c = COL[p]; y = CLY[p]
    put(rb, f"{c}{R['svc_hard']}", f"={CL}!{y}{CL_TOT_HARD}", GREEN, italic=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_new']}", f"={CL}!{y}{CL_TOT_NEW}", GREEN, italic=True, fmt=FMT_MM1)
    if p == "FY2024A": put(rb, f"{c}{R['svc_dt']}", 0, fmt=FMT_MM1)
    elif p == "FY2025A": put(rb, f"{c}{R['svc_dt']}", f"={COL['FY2026E']}{R['in_dt26']}*19/365", fmt=FMT_MM1)
    elif p == "FY2026E": put(rb, f"{c}{R['svc_dt']}", f"={c}{R['in_dt26']}", fmt=FMT_MM1)
    else: put(rb, f"{c}{R['svc_dt']}", f"={COL[PREV[p]]}{R['svc_dt']}*(1+${COL['FY2026E']}${R['in_dt_g']})", fmt=FMT_MM1)
    if p in ("FY2024A", "FY2025A"): put(rb, f"{c}{R['svc_plug']}", f"={c}{R['svc_us_split']}-{c}{R['svc_hard']}-{c}{R['svc_dt']}", fmt=FMT_MM1)
    elif p == "FY2026E": put(rb, f"{c}{R['svc_plug']}", f"={c}{R['svc_us']}-{c}{R['svc_hard']}-{c}{R['svc_new']}-{c}{R['svc_dt']}", fmt=FMT_MM1)
    else: put(rb, f"{c}{R['svc_plug']}", f"={COL[PREV[p]]}{R['svc_plug']}*(1+{c}{R['in_plug_g']})", fmt=FMT_MM1)
    if p == "FY2026E": put(rb, f"{c}{R['svc_us']}", f"={c}8-{c}{R['sw_us']}", bold=True, fmt=FMT_MM1)
    else: put(rb, f"{c}{R['svc_us']}", f"={c}{R['svc_hard']}+{c}{R['svc_new']}+{c}{R['svc_dt']}+{c}{R['svc_plug']}", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_de']}", f"={c}12*${COL['FY2026E']}${R['in_de_share']}", fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_oth']}", f"={c}16*${COL['FY2026E']}${R['in_oth_share']}", fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_tot']}", f"={c}{R['svc_us']}+{c}{R['svc_de']}+{c}{R['svc_oth']}", bold=True, fmt=FMT_MM1)
    if p in ("FY2024A", "FY2025A"): put(rb, f"{c}{R['svc_us_split']}", f"={c}{SP['svc']}-{c}{R['svc_de']}-{c}{R['svc_oth']}", italic=True, fmt=FMT_MM1)
put(rb, f"{COL['FY2024A']}{R['memo_imputed']}", 19.8 + 25.9, BLUE, italic=True, fmt=FMT_MM1); put(rb, f"{COL['FY2025A']}{R['memo_imputed']}", 19.8 + 25.9, BLUE, italic=True, fmt=FMT_MM1)
for p in FADE:
    c = COL[p]; pc = COL[PREV[p]]
    for r in (R["svc_hard"], R["svc_new"], R["svc_dt"], R["svc_plug"]): put(rb, f"{c}{r}", f"={pc}{r}*(1+{c}9)", fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_us']}", f"={c}{R['svc_hard']}+{c}{R['svc_new']}+{c}{R['svc_dt']}+{c}{R['svc_plug']}", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_de']}", f"={c}12*${COL['FY2026E']}${R['in_de_share']}", fmt=FMT_MM1); put(rb, f"{c}{R['svc_oth']}", f"={c}16*${COL['FY2026E']}${R['in_oth_share']}", fmt=FMT_MM1)
    put(rb, f"{c}{R['svc_tot']}", f"={c}{R['svc_us']}+{c}{R['svc_de']}+{c}{R['svc_oth']}", bold=True, fmt=FMT_MM1)
note(rb, R["svc_hard"], "26 NTD-paid agencies (actual RY2024 payments, agency fiscal years) + 31 census-priced contracts (ceiling or rate x 0.8 haircut) + Sunnyvale and Highland Park (flagged assumptions). Each row carries start, end, escalator, funding tag, hazards and renewal probability.")
note(rb, R["svc_new"], "Vintages of unsigned wins in vehicle-equivalents x $153k revenue per contracted vehicle-year (NTD RY2024: $96.8mm / 632 vehicles), 50% ramp in the first year, turnkey hazards after. Signed 2026 contracts (Rochester, Plano, Addison, Grand County, Sunnyvale) are in the documented layer, so the 2026 vintage is small.")
note(rb, R["svc_dt"], "10-K: Downtowner purchase 2025-12-12, 94 customers, pro forma 'not material'. Revenue undisclosed; $15mm-$35mm range, default $25mm.")
note(rb, R["svc_plug"], "2024A/2025A by subtraction (US services from the split less documented contracts and Downtowner); FY2026E by subtraction from the anchored US total less US software. A negative plug means the documented book exceeds what the split allows (raise services GM or lower international services shares). FY2027E+ grown at red inputs.")
note(rb, R["memo_imputed"], "From out/us_revenue_build.csv layers 3-4 (documented turnkey agencies with no price: BJCTA 0.59, Worcester 0.61, Norman 0.70, Valdosta 0.86 per NTD -> $0.9mm median). If the plug is below this, the split is too small.")
label(rb, 75, "Services engine inputs", bold=True)
INP = [(R["in_sgm"], "Services gross margin, loaded basis (base; 22% / 26% / 30% cases)", 0.26, FMT_PCT, "Loaded basis = services cost plus the services share of launch/support personnel. Bleecker: 26%. Identity band 20%-32% at software GM 70%-80%. Reconciles the documented US operations book with a positive plug (see checks)."),
       (R["in_de_share"], "Germany: services share of revenue", 0.75, FMT_PCT, "Not disclosed. Muva was a ViaVan operations contract; other German deployments run with operator partners. Bear/bull: 100% / 50%."),
       (R["in_oth_share"], "Other international: services share of revenue", 0.50, FMT_PCT, "Not disclosed."),
       (R["in_dt26"], "Downtowner FY2026E revenue ($mm)", 25.0, FMT_MM1, "Range $15mm-$35mm (10-K: not material pro forma; 94 customers, resort-town shuttles)."),
       (R["in_dt_g"], "Downtowner growth after 2026", 0.04, FMT_PCT, "Escalators only."),
       (R["in_plug_g"], "Undocumented US services growth (FY2027E+ inputs; FY2026E by subtraction from the anchored US total)", None, FMT_PCT, "The plug grew +27% in 2025 and faster in 2026 (it holds 2026 wins that are documented but unpriced: Citilink Fort Wayne paratransit, TCATA, Highland Park). Base decays 20% / 15% / 12% / 10%; bear 10% flat; bull 25%."),
       ]
for r, text, val, fmt, nt in INP:
    label(rb, r, text, "", italic=True)
    if val is not None: put(rb, f"{COL['FY2026E']}{r}", val, RED, italic=True, fmt=fmt)
    note(rb, r, nt)
for p, v in zip(("FY2027E", "FY2028E", "FY2029E", "FY2030E"), (0.20, 0.15, 0.12, 0.10)): put(rb, f"{COL[p]}{R['in_plug_g']}", v, RED, italic=True, fmt=FMT_PCT)
put(rb, f"{COL['FY2026E']}{R['in_plug_g']}", "by subtraction", GREY, italic=True, align="right")
for r, text, val, nt in [(R["in_2h_us"], "2H26 YoY revenue growth, United States (FY2026E = 1H26A + 2H25A x (1 + this))", 0.35, "1H26 US grew +35.1% YoY (+35% incl. Downtowner from 2025-12-12). Holding that rate for 2H26 lands FY2026E at the guidance midpoint; the differentiated view starts in 2027."),
                         (R["in_2h_de"], "2H26 YoY revenue growth, Germany", -0.12, "2Q26 -12% YoY after Muva ended 2026-02-28."),
                         (R["in_2h_oth"], "2H26 YoY revenue growth, all other countries", 0.35, "1H26 +41% off a small base.")]:
    label(rb, r, text, "", italic=True); put(rb, f"{COL['FY2026E']}{r}", val, RED, italic=True, fmt=FMT_PCT); note(rb, r, nt)
label(rb, R["in_us_fade"], "Germany and other-international growth FY2027E+: rows 13 and 17 (red). US growth FY2031E-FY2035E: row 9 (red); services and software fade at the same rate.", "", italic=True, color=GREY)

# ---------- Section E: software engine (rows 87-101) ----------
label(rb, 87, "Software Engine (annual)", bold=True, size=14)
label(rb, R["sw_tot"], "Total software revenue (2023A-2025A from the split; projections from the engine)", "$mm", bold=True)
label(rb, R["sw_de"], "Germany software (= Germany revenue x (1 - services share))", "$mm")
label(rb, R["sw_oth"], "Other international software", "$mm")
label(rb, R["sw_named"], "US named large accounts: NYC DOE ($36mm / 5 yrs = $7.2mm, 2019-2024 base term; renewal probability applies from 2030)", "$mm")
label(rb, R["sw_small"], "US small-subscription base (residual): grows at (1 + net logo growth) x (1 + expansion) x (1 - competitive churn)", "$mm")
label(rb, R["sw_us"], "US software revenue", "$mm", bold=True)
label(rb, R["sw_g"], "Total software growth", "%", italic=True)
label(rb, R["sw_acv"], "Memo: implied average ACV of the US small-subscription base per software customer ($000; documented median $43k)", "$000", italic=True)
for p in ANN:
    c = COL[p]
    if p == "FY2023A": put(rb, f"{c}{R['sw_tot']}", f"={c}{SP['sw']}", bold=True, fmt=FMT_MM1); continue
    put(rb, f"{c}{R['sw_de']}", f"={c}12*(1-${COL['FY2026E']}${R['in_de_share']})", fmt=FMT_MM1)
    put(rb, f"{c}{R['sw_oth']}", f"={c}16*(1-${COL['FY2026E']}${R['in_oth_share']})", fmt=FMT_MM1)
    if p in ("FY2024A", "FY2025A"):
        put(rb, f"{c}{R['sw_named']}", 7.2, BLUE, fmt=FMT_MM1)
        put(rb, f"{c}{R['sw_small']}", f"={c}{SP['sw']}-{c}{R['sw_de']}-{c}{R['sw_oth']}-{c}{R['sw_named']}", fmt=FMT_MM1)
        put(rb, f"{c}{R['sw_tot']}", f"={c}{SP['sw']}", bold=True, fmt=FMT_MM1)
    else:
        pc = COL[PREV[p]]
        put(rb, f"{c}{R['sw_named']}", f"={pc}{R['sw_named']}*IF({c}$4=\"FY2030E\",${COL['FY2026E']}${R['in_doe_p']},1)" if p in ENG else f"={pc}{R['sw_named']}", fmt=FMT_MM1)
        if p == "FY2026E": put(rb, f"{c}{R['sw_small']}", f"={pc}{R['sw_small']}*(1+${COL['FY2026E']}${R['in_sw26']})", fmt=FMT_MM1)
        elif p in ENG: put(rb, f"{c}{R['sw_small']}", f"={pc}{R['sw_small']}*(1+${COL['FY2026E']}${R['in_logo']})*(1+${COL['FY2026E']}${R['in_exp']})*(1-${COL['FY2026E']}${R['in_churn']})", fmt=FMT_MM1)
        else: put(rb, f"{c}{R['sw_small']}", f"={pc}{R['sw_small']}*(1+{c}9)", fmt=FMT_MM1)
        put(rb, f"{c}{R['sw_tot']}", f"={c}{R['sw_us']}+{c}{R['sw_de']}+{c}{R['sw_oth']}", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['sw_us']}", f"={c}{R['sw_named']}+{c}{R['sw_small']}", bold=True, fmt=FMT_MM1)
    put(rb, f"{c}{R['sw_g']}", f"=IF({COL[PREV[p]]}{R['sw_tot']}=0,0,{c}{R['sw_tot']}/{COL[PREV[p]]}{R['sw_tot']}-1)", italic=True, fmt=FMT_PCT)
    if p in ENG and p != "FY2024A": put(rb, f"{c}{R['sw_acv']}", f"=IF({c}{R['cust_sw']}=0,0,{c}{R['sw_small']}/{c}{R['cust_sw']}*1000)", italic=True, fmt=FMT_INT)
note(rb, R["sw_named"], "Census: NYC DOE $36mm five-year software contract (2019-08). Other documented software accounts are all under $1mm (Miami-Dade $0.32mm, El Paso $0.25mm, MTA Maryland $0.22mm) and sit in the residual.")
note(rb, R["sw_small"], "Residual software grew about +21% / +17% (2024 / 2025 at the default split). Net logo growth is 6%-7% (customer count ex-Downtowner and ex-turnkey), so 10-14 points of history were expansion or large accounts; the engine carries expansion explicitly (red).")
note(rb, R["sw_acv"], "Denominator = organic customers less turnkey customers (row below), which still includes international software customers, so the true US ACV is higher than shown. A figure far above the $43k documented median means the software residual is too large (services GM too low).")
label(rb, 97, "Software engine inputs", bold=True)
for r, text, val, nt in [(R["in_logo"], "Net software logo growth", 0.06, "Customer count grew 9.3% organically; operations customers (~15%-20% of count) grew ~15%-20%, leaving ~6%-7% for software. Bull 9%."),
                         (R["in_exp"], "Expansion at existing software accounts (price, seats, modules)", 0.07, "Historic residual growth less logos = 10-14 pts; carry 7% base, 3% bear, 9% bull."),
                         (R["in_churn"], "Competitive churn (Spare, RideCo displacements)", 0.035, "6-7 documented displacements since 2024 out of ~70 documented software relationships = 3%-4% a year."),
                         (R["in_doe_p"], "NYC DOE renewal probability at the 2030 re-bid", 0.70, "Judgment; the contract is the single largest software account."),
                         (R["in_sw26"], "US small-subscription software growth, FY2026E (anchored year)", 0.20, "The software residual grew +23% in 2025 and about the same in 1H26; the engine's decelerated rate (logos + expansion - churn) applies from FY2027E.")]:
    label(rb, r, text, "", italic=True); put(rb, f"{COL['FY2026E']}{r}", val, RED, italic=True, fmt=FMT_PCT); note(rb, r, nt)

# ---------- Section F: customers (rows 103-108) ----------
label(rb, 103, "Customer Engine (annual, period-end)", bold=True, size=14)
label(rb, R["cust_tk"], "Operations (turnkey/hybrid) customers, organic", "#"); label(rb, R["cust_sw"], "Software customers, organic (= organic total - operations)", "#")
label(rb, R["cust_dt"], "Downtowner customers", "#"); label(rb, R["cust_tot"], "Total customers (feeds row 30)", "#", bold=True)
label(rb, R["in_tk_adds"], "Net new operations customers per year (input)", "#", italic=True)
for p in ENG:
    c = COL[p]
    if p == "FY2024A": put(rb, f"{c}{R['cust_tk']}", 105, RED, italic=True, fmt=FMT_INT); put(rb, f"{c}{R['cust_sw']}", f"={c}32-{c}{R['cust_tk']}", fmt=FMT_INT); put(rb, f"{c}{R['cust_dt']}", 0, fmt=FMT_INT)
    elif p == "FY2025A": put(rb, f"{c}{R['cust_tk']}", 120, RED, italic=True, fmt=FMT_INT); put(rb, f"{c}{R['cust_sw']}", f"={c}32-{c}{R['cust_tk']}", fmt=FMT_INT); put(rb, f"{c}{R['cust_dt']}", 94, BLUE, fmt=FMT_INT)
    else:
        pc = COL[PREV[p]]
        put(rb, f"{c}{R['cust_tk']}", f"={pc}{R['cust_tk']}+{c}{R['in_tk_adds']}", fmt=FMT_INT); put(rb, f"{c}{R['in_tk_adds']}", 15, RED, italic=True, fmt=FMT_INT)
        put(rb, f"{c}{R['cust_sw']}", f"={pc}{R['cust_sw']}*(1+${COL['FY2026E']}${R['in_logo']}-${COL['FY2026E']}${R['in_churn']})", fmt=FMT_INT)
        put(rb, f"{c}{R['cust_dt']}", f"={pc}{R['cust_dt']}", fmt=FMT_INT)
    put(rb, f"{c}{R['cust_tot']}", f"={c}{R['cust_tk']}+{c}{R['cust_sw']}+{c}{R['cust_dt']}", bold=True, fmt=FMT_INT)
note(rb, R["cust_tk"], "Census: 78 US agencies ever turnkey/hybrid + 26 NTD-paid (overlapping) + a share of 62 app-only agencies + international operations customers: ~105 (2024), ~120 (2025). Assumption.")

# ---------- Section G: margin bridge (rows 110-116) ----------
label(rb, 110, "Margin Bridge (blended gross margin from segment mix; feeds Three Statements cost of revenue)", bold=True, size=14)
label(rb, R["gm_svc"], "Services gross margin", "%"); label(rb, R["gm_sw"], "Software gross margin", "%")
label(rb, R["gm_blend"], "Blended gross margin (engine)", "%", bold=True); label(rb, R["gm_svc_share"], "Services share of revenue (engine)", "%", italic=True)
label(rb, R["gm_cogs"], "Cost of revenue % of revenue -> Three Statements row 11 (projected periods)", "%", italic=True, color=GREY)
GM_PATH = {"FY2026E": None, "FY2027E": -0.005, "FY2028E": -0.005, "FY2029E": -0.005, "FY2030E": -0.005}
for p in ANN:
    c = COL[p]
    if p in ("FY2023A", "FY2024A", "FY2025A"):
        put(rb, f"{c}{R['gm_svc']}", f"={c}{SP['gm']}", italic=True, fmt=FMT_PCT)
        put(rb, f"{c}{R['gm_sw']}", f"={c}{SP['sw_gm']}", italic=True, fmt=FMT_PCT)
    elif p == "FY2026E": put(rb, f"{c}{R['gm_svc']}", f"=${COL['FY2026E']}${R['in_sgm']}", fmt=FMT_PCT); put(rb, f"{c}{R['gm_sw']}", f"=${COL['FY2025A']}${SP['sw_gm']}", fmt=FMT_PCT)
    elif p in ENG: put(rb, f"{c}{R['gm_svc']}", f"={COL[PREV[p]]}{R['gm_svc']}+{c}{R['gm_svc']+6}", fmt=FMT_PCT); put(rb, f"{c}{R['gm_sw']}", f"={COL[PREV[p]]}{R['gm_sw']}", fmt=FMT_PCT)
    else: put(rb, f"{c}{R['gm_svc']}", f"={COL[PREV[p]]}{R['gm_svc']}", fmt=FMT_PCT); put(rb, f"{c}{R['gm_sw']}", f"={COL[PREV[p]]}{R['gm_sw']}", fmt=FMT_PCT)
    svc = f"{c}{R['svc_tot']}" if p != "FY2023A" else f"{c}{SP['svc']}"; sw = f"{c}{R['sw_tot']}"
    put(rb, f"{c}{R['gm_blend']}", f"=IF({c}20=0,0,({svc}*{c}{R['gm_svc']}+{sw}*{c}{R['gm_sw']})/{c}20)+{c}{R['gm_uplift']}", bold=True, fmt=FMT_PCT)
    if p in ("FY2026E", "FY2027E"): put(rb, f"{c}{R['gm_uplift']}", {"FY2026E": 0.02, "FY2027E": 0.005}[p], RED, italic=True, fmt=FMT_PCT)
    elif p not in ("FY2023A", "FY2024A", "FY2025A"): put(rb, f"{c}{R['gm_uplift']}", 0.0, RED, italic=True, fmt=FMT_PCT)
    put(rb, f"{c}{R['gm_svc_share']}", f"=IF({c}20=0,0,{svc}/{c}20)", italic=True, fmt=FMT_PCT)
    put(rb, f"{c}{R['gm_cogs']}", f"=1-{c}{R['gm_blend']}", italic=True, fmt=FMT_PCT)
label(rb, R["gm_uplift"], "Non-recurring margin uplift: implementation fees above the ~2%-of-revenue run-rate (input, fades)", "%", italic=True)
note(rb, R["gm_uplift"], "10-Q 2Q26: gross margin rose to 41% 'primarily attributable to a higher percentage of non-subscription revenue' (implementation fees ~5% of revenue vs ~2% normally). At ~90% margin that is worth ~2-3 points while launches run hot; carried +2.0 pts in FY2026E, +0.5 in FY2027E, zero after.")
label(rb, R["gm_svc"] + 6, "Annual change in services gross margin (input; driver wage inflation and self-insured incident costs vs 3%-4% escalators)", "", italic=True)
for p, v in GM_PATH.items():
    if v is not None: put(rb, f"{COL[p]}{R['gm_svc']+6}", v, RED, italic=True, fmt=FMT_PCT)
note(rb, R["gm_svc"], "2023A-2025A = the split's input; FY2026E = input; then drifts by the red annual change. Management: FY2024 and 1Q26 margin declines were 'attributable to a revenue mix shift towards certain lower gross margin contracts'; 2Q26's rise came from non-subscription (implementation) fees.")
note(rb, R["gm_sw"], "Default = implied 2025 software GM from the identity at the launch/support allocation in row 55.")
note(rb, R["gm_blend"], "Each 5-point mix shift toward services costs ~2.3 points of blended margin at these segment margins. 50% long-term target requires software to be most of revenue.")

# ---------- Section H: growth bridge (rows 119-131) ----------
label(rb, R["br_hdr"], "Growth Bridge (annual change in revenue, $mm, by driver)", bold=True, size=14)
BR = [("Total revenue change", lambda c, pc: f"={c}20-{pc}20", True),
      ("Documented contracts (annualization of signed wins, escalators, expansions, expiries, churn)", lambda c, pc: f"={c}{R['svc_hard']}-{pc}{R['svc_hard']}", False),
      ("Unsigned new wins", lambda c, pc: f"={c}{R['svc_new']}-{pc}{R['svc_new']}", False),
      ("Undocumented US services", lambda c, pc: f"={c}{R['svc_plug']}-{pc}{R['svc_plug']}", False),
      ("Downtowner (acquisition)", lambda c, pc: f"={c}{R['svc_dt']}-{pc}{R['svc_dt']}", False),
      ("Germany (total)", lambda c, pc: f"={c}12-{pc}12", False),
      ("Other international (total)", lambda c, pc: f"={c}16-{pc}16", False),
      ("US software", lambda c, pc: f"={c}{R['sw_us']}-{pc}{R['sw_us']}", False),
      ("Check: components - total (should be 0)", lambda c, pc: f"=ROUND(SUM({c}{R['br_hdr']+2}:{c}{R['br_hdr']+8})-{c}{R['br_hdr']+1},3)", False),
      ("Share of growth from acquisition + unsigned new wins", lambda c, pc: f"=IF({c}{R['br_hdr']+1}=0,0,({c}{R['br_hdr']+3}+{c}{R['br_hdr']+5})/{c}{R['br_hdr']+1})", False),
      ("Organic growth ex-Downtowner", lambda c, pc: f"=IF({pc}20=0,0,({c}20-{c}{R['svc_dt']}+{pc}{R['svc_dt']})/{pc}20-1)", False)]
for i, (text, f, bold) in enumerate(BR):
    r = R["br_hdr"] + 1 + i; label(rb, r, text, "$mm" if i < 9 else "%", bold=bold, italic=(i >= 8), color=GREY if i == 8 else BLACK)
    for p in ("FY2025A", "FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E"):
        c, pc = COL[p], COL[PREV[p]]; put(rb, f"{c}{r}", f(c, pc), GREEN if i == 8 else BLACK, bold=bold, italic=(i >= 8), fmt=FMT_PCT if i >= 9 else FMT_MM1)
note(rb, R["br_hdr"] + 1, "FY2025A components use the engine's 2024A/2025A rows (documented layer actuals and the by-subtraction plug), so the 2025 bridge shows how much of reported growth the documented book explains.")

# ---------- Section I: checks (rows 134-150) ----------
label(rb, R["chk_hdr"], "Checks (PASS / FAIL)", bold=True, size=14)
c26, c27, c25, c24 = COL["FY2026E"], COL["FY2027E"], COL["FY2025A"], COL["FY2024A"]
CHK = [("Geography sums equal reported revenue, FY2023A-FY2025A and 1H26A", f"=IF(AND(ROUND({COL['FY2023A']}22,1)=0,ROUND({c24}22,1)=0,ROUND({c25}22,1)=0,ROUND({COL['1Q26A']}22,1)=0,ROUND({COL['2Q26A']}22,1)=0),\"PASS\",\"FAIL\")"),
       ("Segment split reconciles to reported gross profit (check row = 0)", f"=IF(ABS({c25}{SP['chk']})<0.5,\"PASS\",\"FAIL\")"),
       ("Services gross margin input inside the identity band 20%-32%", f"=IF(AND({c26}{R['in_sgm']}>=0.20,{c26}{R['in_sgm']}<=0.32),\"PASS\",\"FAIL\")"),
       ("Implied software gross margin within 70%-85%", f"=IF(AND({c25}{SP['sw_gm']}>=0.70,{c25}{SP['sw_gm']}<=0.85),\"PASS\",\"FAIL\")"),
       ("Undocumented US services plug is positive in 2024A and 2025A", f"=IF(AND({c24}{R['svc_plug']}>0,{c25}{R['svc_plug']}>0),\"PASS\",\"FAIL\")"),
       ("Plug covers at least half the imputed value of unpriced and app-only agencies (2025A)", f"=IF({c25}{R['svc_plug']}>=0.5*{c25}{R['memo_imputed']},\"PASS\",\"FAIL\")"),
       ("FY2026E revenue inside guidance $550mm-$553mm", f"=IF(AND({c26}20>={c26}41,{c26}20<={c26}42),\"PASS\",\"FAIL\")"),
       ("FY2026E organic growth ex-Downtowner within 19%-24%", f"=IF(AND({c26}{R['br_hdr']+11}>=0.19,{c26}{R['br_hdr']+11}<=0.24),\"PASS\",\"FAIL\")"),
       ("FY2027E services revenue at least covers RPO due in 2027 ($318.3mm x 37% = $117.8mm)", f"=IF({c27}{R['svc_tot']}>=318.3*0.37,\"PASS\",\"FAIL\")"),
       ("FY2026E blended gross margin within 39%-42%", f"=IF(AND({c26}{R['gm_blend']}>=0.39,{c26}{R['gm_blend']}<=0.42),\"PASS\",\"FAIL\")"),
       ("FY2026E adjusted EBITDA (Three Statements) within $3mm of guidance $(12.5)mm-$(7.5)mm", f"=IF(AND({TS}!{c26}52>=-15.5,{TS}!{c26}52<=-4.5),\"PASS\",\"FAIL\")"),
       ("Implied US software ACV below 3x the documented $43k median", f"=IF({c25}{R['sw_acv']}<129,\"PASS\",\"FAIL\")"),
       ("Growth bridge components sum to the total change (all years)", f"=IF(SUMPRODUCT(ABS({c25}{R['br_hdr']+9}:{COL['FY2030E']}{R['br_hdr']+9}))<0.01,\"PASS\",\"FAIL\")")]
for i, (text, f) in enumerate(CHK):
    r = R["chk_hdr"] + 1 + i; label(rb, r, text, "", italic=True); put(rb, f"{c26}{r}", f, GREEN, italic=True, align="right")
r_flag = R["chk_hdr"] + 1 + len(CHK)
label(rb, r_flag, "All checks", "", bold=True)
put(rb, f"{c26}{r_flag}", f"=IF(COUNTIF({c26}{R['chk_hdr']+1}:{c26}{r_flag-1},\"FAIL\")=0,\"ALL PASS\",COUNTIF({c26}{R['chk_hdr']+1}:{c26}{r_flag-1},\"FAIL\")&\" FAIL\")", GREEN, bold=True, align="right")
note(rb, R["chk_hdr"] + 4, "This is the reconciliation between the census/NTD book and the filings. It fails when the services GM input is too low for the documented US operations revenue.")
note(rb, R["chk_hdr"] + 11, "Adjusted EBITDA flows from the Three Statements opex assumptions, which were not changed in this rebuild; the tolerance covers that.")
label(rb, r_flag + 2, "Notes", bold=True)
NOTES = ["Architecture: filings define totals and the services/software split (one assumption: services GM); the contract layer dates the services book; software is the residual grown by logos, expansion and churn; margin follows mix. See via-research repo docs: growth_model_design.md sections 8-12, rpm_spec.md, rpm_walkthrough.md.",
         "Colour legend as on the Cover: blue reported input, red assumption, black formula, green cross-sheet link or check.",
         "Quarterly projections are derived from annual engine outputs (3Q/4Q26 by 2025 3Q/4Q shares; 2027 quarters by 2025 quarterly shares): an approximation, since contracts are dated annually.",
         "NTD report year is each agency's fiscal year; RY2025 (published ~Oct 2026) will replace the 2025 growth assumptions on the NTD rows.",
         "Known gaps carried as labelled inputs: Downtowner revenue, Germany and other-international services shares, services GM, software customer count (derived), Sunnyvale term, Highland Park scope."]
for i, t in enumerate(NOTES): label(rb, r_flag + 3 + i, t, "", italic=True, color=GREY)

# ---------- Contract Layer sheet ----------
if "Contract Layer (KW)" in wb.sheetnames: del wb["Contract Layer (KW)"]
cl = wb.create_sheet("Contract Layer (KW)", index=wb.sheetnames.index("Revenue Build (KW)") + 1)
cl.sheet_view.showGridLines = False
put(cl, "A1", "VIA, Contract Layer: documented US operations contracts (services engine detail)", bold=True, size=14)
put(cl, "A2", "One row per contract. Value in year Y = base x start proration x (1+escalator)^(Y-base year) x NTD volume growth x (1-annual hazard)^(Y-2025) x FY2027 level cut x expiry treatment (renewal probability after the end date). $ in millions.", GREY, italic=True)
HDR = ["Agency", "Via entity", "Scope", "Labor-only (agency vehicles)", "Layer", "Funding (census text)", "Funding tag (editable)", "Run-rate / NTD payment ($mm)", "Haircut", "Base ($mm)", "Base year", "Start", "End (blank = none stated)", "NTD row", "Terminated",
       "Annual hazard", "Renewal prob. at end", "FY27 level cut", "FY2024A", "FY2025A", "FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E", "Basis", "Source"]
YEARS = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
for i, h in enumerate(HDR): put(cl, f"{L(i+1)}4", h, bold=True, align="center" if i > 6 else None, border_b=True, size=11)
for i, y in enumerate(YEARS): put(cl, f"{L(19+i)}3", y, GREY, italic=True, align="center", size=11)   # numeric years used by formulas
put(cl, "A3", "Year (numeric, used by formulas) ->", GREY, italic=True, size=11)
widths = {"A": 44, "B": 22, "C": 10, "D": 10, "E": 13, "F": 34, "G": 15, "H": 12, "I": 8, "J": 10, "K": 8, "L": 11, "M": 11, "N": 7, "O": 9, "P": 9, "Q": 9, "R": 9, "Z": 70, "AA": 40}
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
HZ = {"local": (0.02, 0.90, 0.0), "federal formula": (0.0, 0.85, 0.10), "federal one-time": (0.0, 0.55, 0.0), "state": (0.0, 0.70, 0.0), "unknown": (0.01, 0.75, 0.03)}
tag_rng = f"$A${r_hz+1}:$A${r_hz+len(HZ_TAGS)}"; ann_rng = f"$B${r_hz+1}:$B${r_hz+len(HZ_TAGS)}"; ren_rng = f"$C${r_hz+1}:$C${r_hz+len(HZ_TAGS)}"; cut_rng = f"$D${r_hz+1}:$D${r_hz+len(HZ_TAGS)}"
COMP_TK, COMP_SW, DOWNSELL = f"$C${r_hz+7}", f"$C${r_hz+8}", f"$C${r_hz+9}"
put(cl, f"A{first-1}", "Contracts", bold=True)
for i, c in enumerate(contracts):
    r = first + i
    put(cl, f"A{r}", c["agency"], size=11); put(cl, f"B{r}", c["entity"], size=11); put(cl, f"C{r}", c["scope"], size=11); put(cl, f"D{r}", c["labor"], size=11, align="center"); put(cl, f"E{r}", c["layer"], size=11)
    put(cl, f"F{r}", c["fund_raw"], GREY, italic=True, size=10); put(cl, f"G{r}", c["tag"], RED, italic=True, size=11)
    put(cl, f"H{r}", round(c["runrate"], 3), BLUE, fmt=FMT_MM2, size=11); put(cl, f"I{r}", c["haircut"], RED, italic=True, fmt="0.00", size=11); put(cl, f"J{r}", f"=H{r}*I{r}", fmt=FMT_MM2, size=11)
    put(cl, f"K{r}", c["base_year"], BLUE, size=11, align="center"); put(cl, f"L{r}", c["start"], BLUE, fmt=FMT_DATE, size=11)
    if c["end"]: put(cl, f"M{r}", c["end"], BLUE if not c["basis"].startswith("ASSUMPTION") else RED, fmt=FMT_DATE, size=11)
    put(cl, f"N{r}", c["ntd"], size=11, align="center"); put(cl, f"O{r}", c["term"], size=11, align="center")
    put(cl, f"P{r}", f"=IF(C{r}=\"Software-only\",{COMP_SW},{COMP_TK})+INDEX({ann_rng},MATCH(G{r},{tag_rng},0))+IF(AND(G{r}=\"local\",C{r}<>\"Software-only\"),{DOWNSELL},0)", fmt=FMT_PCT, size=11)
    put(cl, f"Q{r}", f"=IF(O{r}=\"Y\",0,INDEX({ren_rng},MATCH(G{r},{tag_rng},0)))", fmt="0.00", size=11)
    put(cl, f"R{r}", f"=INDEX({cut_rng},MATCH(G{r},{tag_rng},0))", fmt=FMT_PCT, size=11)
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
put(cl, f"F{r_exp}", "Existing-account expansion has been a main growth source (NRR 119%; UTA service orders, Douglas, HRT zones). Base decays 5% / 4% / 3% / 3%; bear 2%; bull 8%.", GREY, italic=True, size=10)
for j, y in enumerate(YEARS):
    col = L(19 + j)
    if y >= 2027: put(cl, f"{col}{r_exp}", {2027: 0.05, 2028: 0.04, 2029: 0.03, 2030: 0.03}[y], RED, italic=True, fmt=FMT_PCT, size=11)
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
HZN = {"local": "Local budgets renew ~98%/yr; downsell 2%-4% on locally funded turnkey (Palo Alto, Milwaukee, SacRT, Arlington ceilings).",
       "federal formula": "5307/5310/5311 continue but a 5%-15% level cut is a judgment for FY2027 (federal FY from 2026-10-01); 85% renewal at re-bid.",
       "federal one-time": "CARES/ARPA/Sandbox pilots: about half survive expiry (Volusia, Suffolk continued; Milwaukee cut; SARTA ended).",
       "state": "State grant programs (TRiP, LCTOP, CPUC Access for All) renew 65%-75% at expiry.",
       "unknown": "Blend of the above weighted by documented funding exposure (local ~45%, grant-linked ~30%)."}
for k, t in enumerate(HZ_TAGS, start=1):
    a, rp, cut = HZ[t]; put(cl, f"A{r_hz+k}", t, size=11); put(cl, f"B{r_hz+k}", a, RED, italic=True, fmt=FMT_PCT, size=11); put(cl, f"C{r_hz+k}", rp, RED, italic=True, fmt="0.00", size=11); put(cl, f"D{r_hz+k}", cut, RED, italic=True, fmt=FMT_PCT, size=11); put(cl, f"F{r_hz+k}", HZN[t], GREY, italic=True, size=10)
put(cl, f"A{r_hz+7}", "Competitive hazard, turnkey/hybrid (annual)", italic=True, size=11); put(cl, COMP_TK.replace("$", ""), 0.005, RED, italic=True, fmt=FMT_PCT, size=11); put(cl, f"F{r_hz+7}", "No competitive turnkey loss found in NTD RY2019-24; exits are budget decisions.", GREY, italic=True, size=10)
put(cl, f"A{r_hz+8}", "Competitive hazard, software (annual)", italic=True, size=11); put(cl, COMP_SW.replace("$", ""), 0.035, RED, italic=True, fmt=FMT_PCT, size=11); put(cl, f"F{r_hz+8}", "6-7 displacements by Spare/RideCo since 2024 out of ~70 documented software relationships.", GREY, italic=True, size=10)
put(cl, f"A{r_hz+9}", "Downsell hazard, locally funded operations (annual)", italic=True, size=11); put(cl, DOWNSELL.replace("$", ""), 0.03, RED, italic=True, fmt=FMT_PCT, size=11); put(cl, f"F{r_hz+9}", "Ceiling reductions that GRR does not count.", GREY, italic=True, size=10)
# new-win vintages
r_nw = r_hz + 12
assert r_nw + 7 == CL_TOT_NEW, (r_nw + 7, CL_TOT_NEW)
put(cl, f"A{r_nw}", "Unsigned new wins by vintage (vehicle-equivalents; revenue = vehicles x $/vehicle-year x ramp x escalator x turnkey survival)", bold=True)
put(cl, f"A{r_nw+1}", "Vintage", bold=True, size=11, border_b=True); put(cl, f"B{r_nw+1}", "Vehicle-equivalents (input)", bold=True, size=11, border_b=True, align="center")
for j, y in enumerate(YEARS): put(cl, f"{L(19+j)}{r_nw+1}", f"FY{y}{'A' if y < 2026 else 'E'}", bold=True, size=11, border_b=True, align="center")
VINT = {2026: 50, 2027: 150, 2028: 100, 2029: 100, 2030: 100}
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
put(cl, f"F{r_nw+3}", "Bear 100 / 60 / 60; bull 220 / 200 / 200 for 2027-29.", GREY, italic=True, size=10)

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
if "SOTP (KW)" in wb.sheetnames: del wb["SOTP (KW)"]
so = wb.create_sheet("SOTP (KW)", index=wb.sheetnames.index("DCF + EPS (KW)") + 1); so.sheet_view.showGridLines = False
so.column_dimensions["A"].width = 58; so.column_dimensions["B"].width = 8
for c in "CDEFGHI": so.column_dimensions[c].width = 12
put(so, "A1", "VIA, Sum-of-the-Parts on FY2027E segment gross profit", bold=True, size=14)
put(so, "A2", "Services (labor-intensive operations) valued on a transit-operator / rideshare gross-profit multiple; software on a vertical-SaaS gross-profit multiple. Links to the Revenue Build engine and to the WACC sheet's share count and cash.", GREY, italic=True)
S = [("FY2027E services revenue", f"={RB}!{c27}{R['svc_tot']}", FMT_MM1, GREEN), ("Services gross margin (FY2027E)", f"={RB}!{c27}{R['gm_svc']}", FMT_PCT, GREEN), ("Services gross profit", "=C5*C6", FMT_MM1, BLACK),
     ("FY2027E software revenue", f"={RB}!{c27}{R['sw_tot']}", FMT_MM1, GREEN), ("Software gross margin (FY2027E)", f"={RB}!{c27}{R['gm_sw']}", FMT_PCT, GREEN), ("Software gross profit", "=C8*C9", FMT_MM1, BLACK),
     ("Services EV / gross profit multiple (input)", 2.2, FMT_X, RED), ("Software EV / gross profit multiple (input)", 10.0, FMT_X, RED),
     ("Services enterprise value", "=C7*C11", FMT_MM1, BLACK), ("Software enterprise value", "=C10*C12", FMT_MM1, BLACK), ("Total enterprise value", "=C13+C14", FMT_MM1, BLACK),
     ("(+) Cash & short-term investments (6/30/2026)", f"={WC}!D16+{WC}!D17", FMT_MM1, GREEN), ("(-) Total debt", f"={WC}!D15", FMT_MM1, GREEN), ("Equity value", "=C15+C16-C17", FMT_MM1, BLACK),
     ("Fully diluted shares (mm)", f"={WC}!D13", FMT_MM1, GREEN), ("SOTP value per share", "=C18/C19", '"$"#,##0.00', BLACK), ("Current share price", f"={WC}!D6", '"$"#,##0.00', GREEN), ("Implied upside / (downside)", "=C20/C21-1", FMT_PCT, BLACK),
     ("Market-implied software multiple at the current price (EV less services EV, over software GP)", f"=({WC}!D18-C13)/C10", FMT_X, BLACK)]
for i, (t, f, fmt, colr) in enumerate(S):
    r = 5 + i; put(so, f"A{r}", t, bold=(t.startswith(("Total", "Equity", "SOTP")))); put(so, f"C{r}", f, colr, italic=(colr in (GREEN, RED)), fmt=fmt)
put(so, "E11", "Lyft trades ~2.2x 2027E gross profit (Bleecker); transit operators (Transdev, Keolis) lower. Sensitivity 1.5x-4.0x.", GREY, italic=True); put(so, "E12", "Vertical SaaS peers 8x-15x GP; sensitivity below.", GREY, italic=True)
put(so, "A25", "Sensitivity: SOTP value per share  |  rows: services gross margin applied to FY2027E services revenue; columns: software EV / gross profit multiple", bold=True)
put(so, "A26", "Services GM \\ Software multiple", bold=True, size=11, border_b=True)
mults = [6, 8, 10, 12, 15]; gms = [0.26, 0.28, 0.30, 0.32, 0.34]
for j, m in enumerate(mults): put(so, f"{L(3+j)}26", m, RED, italic=True, fmt=FMT_X, border_b=True, align="center")
for i, g in enumerate(gms):
    r = 27 + i; put(so, f"A{r}", g, RED, italic=True, fmt=FMT_PCT)
    for j in range(len(mults)):
        col = L(3 + j); put(so, f"{col}{r}", f"=(($C$5*$A{r})*$C$11+$C$10*{col}$26+$C$16-$C$17)/$C$19", fmt='"$"#,##0.00')
put(so, "A33", "Note: the sensitivity holds FY2027E segment revenues fixed and varies the services margin as a margin on services revenue; in the engine a different services GM also changes the historical split. Use the Revenue Build input for the full effect.", GREY, italic=True)

# ---------- Three Statements: re-point cost of revenue % ----------
for p in ("3Q26E", "4Q26E"): put(ts, f"{COL[p]}11", f"={RB}!{COL['FY2026E']}{R['gm_cogs']}", GREEN, italic=True, fmt=FMT_PCT)
for p in QTR27: put(ts, f"{COL[p]}11", f"={RB}!{COL['FY2027E']}{R['gm_cogs']}", GREEN, italic=True, fmt=FMT_PCT)
for p in ("FY2028E", "FY2029E", "FY2030E") + tuple(FADE): put(ts, f"{COL[p]}11", f"={RB}!{COL[p]}{R['gm_cogs']}", GREEN, italic=True, fmt=FMT_PCT)
ts["AB11"].value = (ts["AB11"].value or "") + " | Rebuilt 2026-09-21: projected cost of revenue % links to the Revenue Build margin bridge (segment mix x segment margins) instead of the 59% constant."
ts["AB11"].font = font(GREY, italic=True)

# ---------- Cover: TOC entries and checks flag ----------
merges = [str(m) for m in cover.merged_cells.ranges]
low = min(int(re.search(r"\d+", m).group(0)) for m in merges) if merges else 999
if all(int(re.findall(r"\d+", m)[-1]) < 12 for m in merges):
    cover.insert_rows(12, 3)
    for k, (name, desc) in enumerate([("Contract Layer (KW)", "Contract-level services engine: 59 documented US operations contracts with dates, funding tags, hazards; unsigned-win vintages"),
                                      ("NTD Data", "FTA NTD purchased-transportation payments to Via entities, RY2019-RY2024 (evidence for the services book)"),
                                      ("SOTP (KW)", "Sum-of-the-parts on FY2027E segment gross profit with market-implied software multiple and sensitivity")]):
        r = 12 + k; src = cover["E11"]
        c = cover[f"E{r}"]; c.value = name; c.font = copy(src.font); c.hyperlink = Hyperlink(ref=f"E{r}", location=f"'{name}'!A1", display=name)
        d = cover[f"F{r}"]; d.value = desc; d.font = copy(cover["F11"].font)
        cover.row_dimensions[r].height = cover.row_dimensions[11].height
    put(cover, "B25", "Revenue model checks (Revenue Build)", bold=False); cover["B25"].font = copy(cover["B24"].font) if cover["B24"].value else font()
    put(cover, "C25", f"={RB}!{c26}{r_flag}", GREEN, italic=True)
else:
    put(cover, "B25", "Revenue model checks (Revenue Build)"); put(cover, "C25", f"={RB}!{c26}{r_flag}", GREEN, italic=True)
    put(cover, "E25", "Contract Layer (KW) | NTD Data | SOTP (KW): added 2026-09-21", GREY, italic=True)

# reorder: Contract Layer and NTD Data right after Revenue Build; SOTP after DCF
for name in ("Contract Layer (KW)", "NTD Data"):
    ws = wb[name]; wb._sheets.remove(ws); wb._sheets.insert(wb.sheetnames.index("Revenue Build (KW)") + (1 if name.startswith("Contract") else 2), ws)
ws = wb["SOTP (KW)"]; wb._sheets.remove(ws); wb._sheets.insert(wb.sheetnames.index("DCF + EPS (KW)") + 1, ws)

for o in OUT: wb.save(o)
print("saved:", OUT, "| checks flag cell:", f"{c26}{r_flag}", "| contract rows:", n, "| CL totals rows:", CL_TOT_HARD, CL_TOT_NEW)
