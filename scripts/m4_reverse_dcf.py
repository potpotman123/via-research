"""Reverse DCF on free cash flow, mirroring the SOLS layout: sell-side base-year FCF -> solve the FCF CAGR the current EV implies.
Base year = FY2027E (William Blair, 8/25/2026: revenue $676.0mm, adj. EBITDA $22.2mm, FCF $13.1mm), the first street year with positive FCF.
Projections FY2028E-FY2032E = base x (1 + g)^n, Gordon terminal value on FY2032E, 30-step bisection in cells. No pitch-case inputs.
Rewrites 'WACC and Reverse DCF (KW)' rows 54-138; leaves rows 1-53 (WACC build) and 139+ (multiples, notes) alone."""
import re, openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter as L
SRC = "/Users/kwu/Downloads/KW VIA MODEL.xlsx"; OUT = [SRC, "/Users/kwu/Documents/VIA/model/KW VIA MODEL.xlsx"]
GAR = "Garamond"; BLUE, RED, GREEN, BLACK, GREY = "FF0000FF", "FFFF0000", "FF008000", "FF000000", "FF7F7F7F"
FMT_MM = '#,##0.0_);\\(#,##0.0\\);\\-_)'; FMT_PCT = '0.00%;\\(0.00%\\);\\-_)'; FMT_PCT1 = '0.0%;\\(0.0%\\);\\-_)'; FMT_X = '0.0"x"'; THIN = Side(style="thin"); YELLOW = PatternFill("solid", fgColor="FFFFFF00")
def font(color=BLACK, bold=False, italic=False, size=12): return Font(name=GAR, size=size, bold=bold, italic=italic, color=color)
def put(ws, ref, v, color=BLACK, bold=False, italic=False, fmt=None, size=12, align=None, border_b=False, fill=None):
    c = ws[ref]; c.value = v; c.font = font(color, bold, italic, size)
    if fmt: c.number_format = fmt
    if align: c.alignment = Alignment(horizontal=align)
    if border_b: c.border = Border(bottom=THIN)
    if fill: c.fill = fill
    return c

wb = openpyxl.load_workbook(SRC); w = wb["WACC and Reverse DCF (KW)"]; st = wb["Street Consensus"]; DCF = "'DCF + EPS (KW)'"; SC = "'Street Consensus'"
def wrow(prefix, col=2, lo=1, hi=60):
    for r in range(lo, hi):
        v = w.cell(r, col).value
        if isinstance(v, str) and v.strip().lower().startswith(prefix.lower()): return r
    raise KeyError(prefix)
R_EV, R_WACC = wrow("Enterprise Value"), wrow("Weighted Average Cost of Capital", lo=40)

# ---------- Street Consensus: William Blair FY2026E/FY2027E estimates (single broker, dated) ----------
def srow(prefix):
    for r in range(1, 40):
        v = st.cell(r, 1).value
        if isinstance(v, str) and v.strip().lower().startswith(prefix.lower()): return r
    raise KeyError(prefix)
S_REV, S_EBITDA, S_FCF = srow("Revenue"), srow("Adjusted EBITDA"), srow("Free Cash Flow")
WB = {S_REV: {"S": 676.021}, S_EBITDA: {"N": -11.573, "S": 22.248}, S_FCF: {"N": -38.408, "S": 13.100}}
for r, cells in WB.items():
    for col, v in cells.items():
        if st[f"{col}{r}"].value in (None, ""): put(st, f"{col}{r}", v, BLUE, fmt=FMT_MM)
    tag = "FY2027E (and FY2026E adj. EBITDA / FCF): William Blair, 'Updating Fiscal 2027 Estimates', 8/25/2026 (single broker; FCF as defined by the broker)."
    if not (st[f"AB{r}"].value and "William Blair" in str(st[f"AB{r}"].value)):
        st[f"AB{r}"].value = ((st[f"AB{r}"].value + " | ") if st[f"AB{r}"].value else "") + tag
    st[f"AB{r}"].font = font(GREY, italic=True)

# ---------- clear rows 54-138 ----------
refs = [(ws.title, c.coordinate) for ws in wb.worksheets if ws.title != w.title for row in ws.iter_rows() for c in row
        if isinstance(c.value, str) and c.value.startswith("=") and re.search(r"WACC and Reverse DCF \(KW\)'!\$?[A-Z]+\$?(5[4-9]|[6-9]\d|1[0-3]\d)\b", c.value)]
print("external references into rows 54-138 (Summary block, re-pointed below):", len(refs))
for r in range(54, 139):
    for c in range(2, 40):
        cell = w.cell(r, c); cell.value = None; cell.font = font(); cell.number_format = "General"; cell.border = Border(); cell.alignment = Alignment(); cell.fill = PatternFill()
w["B3"].value = "Market-implied expectations: what free cash flow growth does the current enterprise value require?  |  $ in millions except per share"
for col, wd in (("B", 44), ("C", 10), ("D", 13), ("E", 13), ("F", 4), ("G", 40), ("H", 4), ("I", 4), ("J", 13), ("K", 13), ("L", 13), ("M", 13)):
    if (w.column_dimensions[col].width or 0) < wd: w.column_dimensions[col].width = wd

# ---------- Block A (left): sell-side base-year FCF | Block B (right): assumptions ----------
put(w, "B54", "VIA Base Year FCF (sell-side: William Blair, 8/25/2026; FY2027E, the first street year with positive FCF)", bold=True, size=14)
put(w, "G54", "VIA Reverse DCF Assumptions", bold=True, size=14)
A_ = [(55, "FY2027E Revenue (GAAP)", f"={SC}!S{S_REV}", GREEN, FMT_MM, False),
      (56, "FY2027E Adjusted EBITDA", f"={SC}!S{S_EBITDA}", GREEN, FMT_MM, False),
      (57, "EBITDA-to-FCF conversion embedded in the estimates", "=IF(D56=0,0,D59/D56)", BLACK, FMT_PCT1, False),
      (59, "FY2027E Free Cash Flow (broker definition)", f"={SC}!S{S_FCF}", GREEN, FMT_MM, True),
      (60, "Memo: FY2025A Free Cash Flow (broker)", -32.532, BLUE, FMT_MM, False),
      (61, "Memo: FY2026E Free Cash Flow (broker)", f"={SC}!N{S_FCF}", GREEN, FMT_MM, False)]
for r, lab, f, colr, fmt, bold in A_: put(w, f"B{r}", lab, bold=bold); put(w, f"D{r}", f, colr, italic=(colr == GREEN), bold=bold, fmt=fmt)
put(w, "B62", "FY2025A and FY2026E street FCF are negative, so the base year is FY2027E, the first year the street has Via generating cash. A CAGR needs a positive base.", GREY, italic=True, size=10)
B_ = [(55, "Base Year FCF (FY2027E)", "=D59", BLACK, FMT_MM, ""),
      (56, "WACC", f"=G{R_WACC}", BLACK, FMT_PCT, ""),
      (57, "Terminal Growth Rate", f"={DCF}!D20", GREEN, FMT_PCT, "Linked to the DCF + EPS tab."),
      (58, "Forecast Years (FY2028E - FY2032E)", 5, BLACK, "0", ""),
      (59, "Current Market EV", f"=D{R_EV}", BLACK, FMT_MM, ""),
      (60, "Discount-period offset (years; 0 = FY2028E is year 1, as in the SOLS layout)", 0, RED, "0.00", "Set to 1.28 to start discounting from the 9/18/2026 valuation date (FY2027 year-end is 1.28 years out); memo below shows that case."),
      (61, "Trial FCF Growth (linked to the solved rate; overwrite to test a value)", "=J62", BLACK, FMT_PCT, ""),
      (62, "Actual FCF Growth (solved: 30-step bisection, rows 93-123)", "=F123", BLACK, FMT_PCT, "The FCF CAGR FY2027E-FY2032E that makes PV(FCF) + PV(TV) equal today's enterprise value.")]
for r, lab, f, colr, fmt, nt in B_:
    put(w, f"G{r}", lab, bold=(r == 62)); put(w, f"J{r}", f, colr, italic=(colr in (GREEN, RED)), bold=(r == 62), fmt=fmt, fill=(YELLOW if r == 62 else None))
    if nt: put(w, f"L{r}", nt, GREY, italic=True, size=10)

# ---------- Block C: projections ----------
put(w, "B64", "VIA Free Cash Flow Projections", bold=True, size=14)
for ref, t in (("B65", "Year"), ("C65", "Projected Free Cash Flows"), ("E65", "Trial"), ("G65", "Discount To Present"), ("J65", "Trial")): put(w, ref, t, bold=True, border_b=True, align=("right" if ref[0] in "EJ" else None))
for n in range(1, 6):
    r = 65 + n; put(w, f"B{r}", 2027 + n, fmt="0", align="center")
    put(w, f"C{r}", f"Base Year * (1 + FCF Growth) ^ {n}", italic=True); put(w, f"E{r}", f"=$J$55*(1+$J$61)^{n}", fmt=FMT_MM)
    put(w, f"G{r}", "PV = FCF / (1 + WACC) ^ (Year # + offset)", italic=True); put(w, f"J{r}", f"=E{r}/(1+$J$56)^({n}+$J$60)", fmt=FMT_MM)
put(w, "B72", "VIA Terminal Value Calculation", bold=True, size=14)
put(w, "B73", "2032 Terminal Value", bold=True, border_b=True); put(w, "E73", "Trial", bold=True, border_b=True, align="right"); put(w, "G73", "Discount to Present", bold=True, border_b=True); put(w, "J73", "Trial", bold=True, border_b=True, align="right")
put(w, "B74", "2032 FCF * (1 + Terminal Growth Rate) / (WACC - Terminal Growth Rate)", italic=True); put(w, "E74", "=E70*(1+$J$57)/($J$56-$J$57)", fmt=FMT_MM)
put(w, "G74", "PV = TV / (1 + WACC) ^ (5 + offset)", italic=True); put(w, "J74", "=E74/(1+$J$56)^(5+$J$60)", fmt=FMT_MM)
put(w, "B76", "Total Enterprise Value", bold=True, border_b=True); put(w, "E76", "Trial", bold=True, border_b=True, align="right"); put(w, "J76", "Actual", bold=True, border_b=True, align="right")
put(w, "B77", "Present Value of TV + Present Value of FCFs", italic=True); put(w, "E77", "=SUM(J66:J70)+J74", fmt=FMT_MM); put(w, "J77", "=$J$59", fmt=FMT_MM)
put(w, "B78", "Check: Trial less Actual (0 when the trial growth equals the solved growth)", GREY, italic=True); put(w, "E78", "=ROUND(E77-J77,2)", GREEN, italic=True, fmt=FMT_MM)

# ---------- Block D: FCF to EBITDA bridge ----------
put(w, "B80", "VIA FCF to EBITDA Bridge", bold=True, size=14)
for ref, t in (("B81", "Year"), ("C81", "Projected Free Cash Flows"), ("E81", "EBITDA-to-FCF Conversion (held at the FY2027E street rate)"), ("J81", "Implied Adj. EBITDA"), ("K81", "Revenue at street FY2027 growth, held"), ("L81", "Implied Adj. EBITDA Margin")): put(w, ref, t, bold=True, border_b=True, size=11, align=(None if ref[0] in "BCE" else "right"))
put(w, "M81", "Street FY2027E revenue growth (input, red) ->", GREY, italic=True, size=10); put(w, "M82", f"=IF({SC}!N{S_REV}=0,0,{SC}!S{S_REV}/{SC}!N{S_REV}-1)", RED, italic=True, fmt=FMT_PCT1)
for n in range(0, 6):
    r = 82 + n; put(w, f"B{r}", 2027 + n, fmt="0", align="center")
    put(w, f"C{r}", "=$J$55" if n == 0 else f"=E{65+n}", fmt=FMT_MM)
    put(w, f"E{r}", "=$D$57" if n == 0 else "=$E$82", RED if n == 0 else BLACK, italic=True, fmt=FMT_PCT1)
    put(w, f"J{r}", f"=IF(E{r}=0,0,C{r}/E{r})", GREEN if n == 0 else BLACK, italic=(n == 0), fmt=FMT_MM)
    put(w, f"K{r}", "=$D$55" if n == 0 else f"=K{r-1}*(1+$M$82)", fmt=FMT_MM); put(w, f"L{r}", f"=IF(K{r}=0,0,J{r}/K{r})", fmt=FMT_PCT1)
put(w, "B88", "Reading: the EBITDA the price implies if free cash flow converts from EBITDA at the FY2027E street rate; margin shown against revenue compounding at the street's FY2027 growth rate.", GREY, italic=True, size=10)
put(w, "B89", "Memo: implied FCF CAGR if discounting runs from the valuation date (offset 1.28 years)", italic=True); put(w, "J89", "=K123", italic=True, fmt=FMT_PCT)
put(w, "B90", "Memo: implied FY2032E FCF at the solved rate", italic=True); put(w, "J90", "=$J$55*(1+$J$62)^5", italic=True, fmt=FMT_MM)

# ---------- bisection (rows 92-123): block 1 at the input offset (D-G), block 2 at offset 1.28 (I-L) ----------
put(w, "B92", "Solver: 30-step bisection on g such that PV(FCF) + PV(TV) = Current Market EV (block 1: input offset; block 2: offset 1.28)", bold=True, size=11)
for start, off in (("D", "$J$60"), ("I", "1.28")):
    c0 = openpyxl.utils.column_index_from_string(start); lo, hi, mid, res = L(c0), L(c0 + 1), L(c0 + 2), L(c0 + 3)
    for ref, t in ((lo, "g low"), (hi, "g high"), (mid, "g mid"), (res, "PV(mid) - EV")): put(w, f"{ref}93", t, bold=True, size=10, align="right", border_b=True)
    for k in range(30):
        r = 94 + k
        if k == 0: put(w, f"{lo}{r}", -0.5, size=10, fmt=FMT_PCT); put(w, f"{hi}{r}", 5.0, size=10, fmt=FMT_PCT)
        else: put(w, f"{lo}{r}", f"=IF({res}{r-1}>0,{lo}{r-1},{mid}{r-1})", size=10, fmt=FMT_PCT); put(w, f"{hi}{r}", f"=IF({res}{r-1}>0,{mid}{r-1},{hi}{r-1})", size=10, fmt=FMT_PCT)
        put(w, f"{mid}{r}", f"=({lo}{r}+{hi}{r})/2", size=10, fmt=FMT_PCT)
        pv = "+".join([f"$J$55*(1+{mid}{r})^{n}/(1+$J$56)^({n}+{off})" for n in range(1, 6)])
        put(w, f"{res}{r}", f"={pv}+$J$55*(1+{mid}{r})^5*(1+$J$57)/($J$56-$J$57)/(1+$J$56)^(5+{off})-$J$59", size=10, fmt=FMT_MM)
put(w, "B94", "Iteration 1 ... 30 (row 123 = converged)", GREY, italic=True, size=10)
put(w, "B125", "Notes", bold=True)
put(w, "B126", "Layout follows the SOLS reverse DCF: sell-side base-year FCF, FCF projections at a single growth rate, Gordon terminal value, trial vs. actual enterprise value. Only street inputs are used; the pitch case does not enter.", GREY, italic=True, size=10)
put(w, "B127", "Base year FY2027E because the street's FY2025A and FY2026E free cash flows are negative. Discounting defaults to the SOLS convention (FY2028E = year 1); the offset input and the memo show the valuation-date convention.", GREY, italic=True, size=10)
for r in range(139, 170):
    v = w.cell(r, 2).value
    if isinstance(v, str) and (v.startswith("Reverse DCF") or v.startswith("The solver is a 30-step") or v.startswith("No iteration") or v.startswith("Solve 2 uses")):
        w.cell(r, 2).value = "Reverse DCF: see the notes in rows 125-127 (sell-side base-year FCF, single FCF growth rate, bisection in cells)."

# ---------- Summary block (N20:O34) ----------
sm = wb["Summary"]; W = "'WACC and Reverse DCF (KW)'"
SUMM = [("Base Year FCF: FY2027E street (William Blair, 8/25/2026, $mm)", f"={W}!J55", FMT_MM), ("Current Market EV ($mm)", f"={W}!J59", FMT_MM),
        ("Market-Implied FCF CAGR, FY2027E - FY2032E", f"={W}!J62", FMT_PCT), ("Implied FY2032E FCF ($mm)", f"={W}!J90", FMT_MM),
        ("Implied FY2032E Adj. EBITDA at the street conversion rate ($mm)", f"={W}!J87", FMT_MM), ("Implied FY2032E Adj. EBITDA margin (revenue at street FY2027 growth, held)", f"={W}!L87", FMT_PCT1),
        ("Memo: implied FCF CAGR discounting from the valuation date", f"={W}!J89", FMT_PCT)]
for i, (lab, f, fmt) in enumerate(SUMM):
    r = 22 + i; sm[f"N{r}"].value = lab; sm[f"O{r}"].value = f; sm[f"O{r}"].number_format = fmt; sm[f"O{r}"].font = font(GREEN, italic=True)
for r in range(29, 35): sm[f"N{r}"].value = None; sm[f"O{r}"].value = None
for row in sm.iter_rows():
    for c in row:
        if isinstance(c.value, str) and c.value.startswith("Reverse DCF"): c.value = "Reverse DCF uses only street inputs: from William Blair's FY2027E free cash flow it solves for the FCF growth rate FY2027E-FY2032E that the current enterprise value requires."
# ---------- Cover ----------
cv = wb["Cover"]
for r in range(5, 40):
    b = cv.cell(r, 2).value
    if isinstance(b, str) and (b.startswith("Market-Implied FY2035E UFCF") or b.startswith("Market-Implied FCF CAGR")):
        cv.cell(r, 2).value = "Market-Implied FCF CAGR (FY2027E street base to FY2032E)"; cv.cell(r, 3).value = f"={W}!J62"; cv.cell(r, 3).number_format = FMT_PCT1; cv.cell(r, 3).font = font(GREEN, italic=True)
    if isinstance(b, str) and (b.startswith("Pitch-Case FY2035E UFCF") or b.startswith("Pitch-Case FCF CAGR")):
        cv.cell(r, 2).value = "Street FY2027E Free Cash Flow, base year ($mm; William Blair)"; cv.cell(r, 3).value = f"={W}!J55"; cv.cell(r, 3).number_format = FMT_MM; cv.cell(r, 3).font = font(GREEN, italic=True)
for o in OUT: wb.save(o)
print("saved")
