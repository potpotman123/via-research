"""Reverse DCF on free cash flow (WACC and Reverse DCF (KW) sheet, rows 54-98).
Solves the FY2035E unlevered FCF the current enterprise value requires, with UFCF ramping linearly in dollars from the pitch-case FY2026E level.
EV = A + B x X is linear in X, so X = (EV - A) / B: no bisection. Replaces the revenue-CAGR solver; leaves rows 1-53 (WACC build) and 139+ (multiples) alone."""
import re, openpyxl
from copy import copy
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
SRC = "/Users/kwu/Downloads/KW VIA MODEL.xlsx"; OUT = [SRC, "/Users/kwu/Documents/VIA/model/KW VIA MODEL.xlsx"]
GAR = "Garamond"; BLUE, RED, GREEN, BLACK, GREY = "FF0000FF", "FFFF0000", "FF008000", "FF000000", "FF7F7F7F"
FMT_MM = '#,##0.0_);\\(#,##0.0\\);\\-_)'; FMT_PCT = '0.0%;\\(0.0%\\);\\-_)'; FMT_X = '0.0"x"'; THIN = Side(style="thin")
def font(color=BLACK, bold=False, italic=False, size=12): return Font(name=GAR, size=size, bold=bold, italic=italic, color=color)
def put(ws, ref, v, color=BLACK, bold=False, italic=False, fmt=None, size=12, align=None, border_b=False):
    c = ws[ref]; c.value = v; c.font = font(color, bold, italic, size)
    if fmt: c.number_format = fmt
    if align: c.alignment = Alignment(horizontal=align)
    if border_b: c.border = Border(bottom=THIN)
    return c

wb = openpyxl.load_workbook(SRC); w = wb["WACC and Reverse DCF (KW)"]; DCF = "'DCF + EPS (KW)'"; TS = "'Three Statements (KW)'"
# safety: anything outside this sheet pointing at rows 54-137?
refs = [(ws.title, c.coordinate, c.value[:60]) for ws in wb.worksheets if ws.title != w.title for row in ws.iter_rows() for c in row
        if isinstance(c.value, str) and c.value.startswith("=") and re.search(r"WACC and Reverse DCF \(KW\)'!\$?[A-Z]+\$?(5[4-9]|[6-9]\d|1[0-3]\d)\b", c.value)]
print("external references into rows 54-137:", refs or "none")
# clear rows 54-137
for r in range(54, 138):
    for c in range(2, 27):
        cell = w.cell(r, c); cell.value = None; cell.font = font(); cell.number_format = "General"; cell.border = Border(); cell.alignment = Alignment()
w["B3"].value = "Market-implied expectations: what free cash flow does the current enterprise value require?  |  $ in millions except per share"

# ---- assumptions and solved outputs (rows 54-69) ----
put(w, "B54", "VIA Reverse DCF on Free Cash Flow", bold=True, size=14)
A = [("Current Enterprise Value", "$mm", "=D17", BLACK, FMT_MM, ""),
     ("WACC", "%", "=G52", BLACK, FMT_PCT, ""),
     ("Terminal Growth Rate (linked to the DCF tab)", "%", f"={DCF}!D20", GREEN, FMT_PCT, "Same terminal growth as the DCF + EPS tab so the two tabs are comparable."),
     ("Stub Period (fraction of FY2026 remaining after valuation date)", "yrs", f"={DCF}!D16", GREEN, "0.000", ""),
     ("Mid-Year Convention (1 = yes)", "flag", f"={DCF}!D17", GREEN, "0", ""),
     ("Forecast Horizon (FY2027E - FY2035E)", "yrs", 9, BLACK, "0", ""),
     ("FY2026E Unlevered FCF, pitch case (full year; the ramp starts here)", "$mm", f"={DCF}!G38", GREEN, FMT_MM, "DCF + EPS tab row 38. Negative today: the market-implied path must climb out of this burn."),
     ("FY2035E Revenue, pitch case (to translate implied FCF into a margin)", "$mm", f"={TS}!AA7", GREEN, FMT_MM, ""),
     ("FY2035E Unlevered FCF, pitch case", "$mm", f"={DCF}!P38", GREEN, FMT_MM, ""),
     ("Market-Implied FY2035E Unlevered FCF (solved)", "$mm", "=(D55-D87)/D88", BLACK, FMT_MM, "Closed form: EV = A + B x X with a linear dollar ramp from the FY2026E level to X, so X = (EV - A) / B. A and B are in rows 87-88."),
     ("Market-Implied FY2035E UFCF Margin (on pitch-case revenue)", "%", "=IF(D62=0,0,D64/D62)", BLACK, FMT_PCT, "What the current price requires Via to earn on the revenue path in this model."),
     ("Pitch-Case FY2035E UFCF Margin", "%", "=IF(D62=0,0,D63/D62)", BLACK, FMT_PCT, ""),
     ("Gap: market-implied less pitch-case FY2035E UFCF", "$mm", "=D64-D63", BLACK, FMT_MM, "Positive = the price needs more terminal cash flow than the pitch case produces."),
     ("Market-Implied FY2035E UFCF as a multiple of the pitch case", "x", "=IF(D63=0,0,D64/D63)", BLACK, FMT_X, ""),
     ("Implied Terminal EV / FY2035E UFCF = (1 + g) / (WACC - g)", "x", "=(1+D57)/(D56-D57)", BLACK, FMT_X, "")]
for i, (lab, unit, f, colr, fmt, nt) in enumerate(A):
    r = 55 + i; put(w, f"B{r}", lab, bold=lab.startswith("Market-Implied FY2035E Unlevered")); put(w, f"C{r}", unit, align="right")
    put(w, f"D{r}", f, colr, italic=(colr == GREEN), bold=lab.startswith("Market-Implied FY2035E Unlevered"), fmt=fmt)
    if nt: put(w, f"F{r}", nt, GREY, italic=True)

# ---- path (rows 70-88) ----
put(w, "B70", "Market-Implied Free Cash Flow Path (linear ramp in dollars from FY2026E to the solved FY2035E level)", bold=True, size=14)
years = ["FY2026E (stub)"] + [f"FY{y}E" for y in range(2027, 2036)]; cols = [L(4 + i) for i in range(10)]   # D..M
put(w, "B71", "Fiscal Year", bold=True); put(w, "C71", "Units", align="right", border_b=True)
for c, y in zip(cols, years): put(w, f"{c}71", y, bold=True, align="right", border_b=True)
ROWS = {72: ("Year Index (t)", "#"), 73: ("Ramp weight w = t / 9", "x"), 74: ("Market-Implied Unlevered FCF (stub-adjusted in FY2026E)", "$mm"), 75: ("Pitch-Case Unlevered FCF (DCF + EPS tab, stub-adjusted)", "$mm"),
        76: ("Discount Period", "yrs"), 77: ("Discount Factor", "x"), 78: ("Present Value of Implied UFCF", "$mm")}
for r, (lab, unit) in ROWS.items(): put(w, f"B{r}", lab, bold=(r == 74)); put(w, f"C{r}", unit, align="right")
for i, c in enumerate(cols):
    put(w, f"{c}72", i, fmt="0", align="right"); put(w, f"{c}73", f"={c}72/$D$60", fmt="0.000")
    put(w, f"{c}74", f"=IF({c}72=0,$D$61*$D$58,$D$61*(1-{c}73)+$D$64*{c}73)", bold=True, fmt=FMT_MM)
    put(w, f"{c}75", f"={DCF}!{L(7 + i)}41" if i == 0 else f"={DCF}!{L(7 + i)}38", GREEN, italic=True, fmt=FMT_MM)
    put(w, f"{c}76", f"=IF({c}72=0,$D$58*(1-0.5*$D$59),$D$58+{c}72-0.5*$D$59)", fmt="0.000")
    put(w, f"{c}77", f"=1/(1+$D$56)^{c}76", fmt="0.000"); put(w, f"{c}78", f"={c}74*{c}77", fmt=FMT_MM)
T = [("Terminal Value at FY2035E = implied UFCF x (1 + g) / (WACC - g)", "$mm", "=M74*(1+$D$57)/($D$56-$D$57)"),
     ("Present Value of Terminal Value", "$mm", "=D79/(1+$D$56)^($D$58+$D$60)"),
     ("Sum of PV of Implied UFCF", "$mm", "=SUM(D78:M78)"),
     ("Implied Enterprise Value (PV of UFCF + PV of TV)", "$mm", "=D81+D80"),
     ("Check vs. Current Enterprise Value (should be 0)", "$mm", "=ROUND(D82-D55,3)"),
     ("PV of Terminal Value as % of EV", "%", "=IF(D82=0,0,D80/D82)"),
     ("Cumulative implied UFCF, FY2027E - FY2035E", "$mm", "=SUM(E74:M74)"),
     ("Cumulative pitch-case UFCF, FY2027E - FY2035E", "$mm", "=SUM(E75:M75)"),
     ("A: PV of the part of the path fixed by FY2026E UFCF", "$mm", "=$D$61*$D$58*D77+$D$61*SUMPRODUCT(E77:M77,1-E73:M73)"),
     ("B: PV weight on the solved FY2035E UFCF (path + terminal value)", "x", "=SUMPRODUCT(E77:M77,E73:M73)+(1+$D$57)/($D$56-$D$57)/(1+$D$56)^($D$58+$D$60)")]
for i, (lab, unit, f) in enumerate(T):
    r = 79 + i; put(w, f"B{r}", lab, italic=(r in (83, 87, 88)), color=GREY if r in (83, 87, 88) else BLACK); put(w, f"C{r}", unit, align="right")
    put(w, f"D{r}", f, GREEN if r == 83 else BLACK, italic=(r in (83, 87, 88)), fmt={"%": FMT_PCT, "x": "0.000"}.get(unit, FMT_MM))

# ---- sensitivity (rows 90-98) ----
put(w, "B90", "Sensitivity: market-implied FY2035E UFCF ($mm, top) and margin on pitch-case revenue (bottom)  |  rows: WACC  |  columns: terminal growth", bold=True, size=14)
gs = [0.01, 0.02, 0.03, 0.04]
def solve(wref, gref):
    return (f"=($D$55-($D$61*$D$58/(1+{wref})^($D$58*(1-0.5*$D$59))+$D$61*SUMPRODUCT((1+{wref})^(-($D$58+$E$72:$M$72-0.5*$D$59)),1-$E$73:$M$73)))"
            f"/(SUMPRODUCT((1+{wref})^(-($D$58+$E$72:$M$72-0.5*$D$59)),$E$73:$M$73)+(1+{gref})/({wref}-{gref})/(1+{wref})^($D$58+$D$60))")
for blk, (r0, label, as_margin) in enumerate([(91, "Implied FY2035E UFCF ($mm): WACC \\ terminal g", False), (96, "Implied FY2035E UFCF margin: WACC \\ terminal g", True)]):
    put(w, f"B{r0}", label, bold=True, border_b=True, size=11)
    for j, g in enumerate(gs): put(w, f"{L(4 + j)}{r0}", g, RED, italic=True, fmt=FMT_PCT, border_b=True, align="right")
    for i, dw in enumerate((-0.01, 0.0, 0.01)):
        r = r0 + 1 + i; put(w, f"C{r}", f"=$D$56+({dw})", RED, italic=True, fmt=FMT_PCT)
        for j in range(len(gs)):
            col = L(4 + j); f = solve(f"$C{r}", f"{col}${r0}")
            put(w, f"{col}{r}", (f"={f[1:]}" if not as_margin else f"=IF($D$62=0,0,({f[1:]})/$D$62)"), fmt=(FMT_PCT if as_margin else FMT_MM))
put(w, "F95", "Reading: each cell is the FY2035E free cash flow the current price requires under that discount rate and terminal growth.", GREY, italic=True)

# ---- notes (rows 150-151 exist as text) ----
for r in range(148, 156):
    v = w.cell(r, 2).value
    if isinstance(v, str) and v.startswith("Reverse DCF"): w.cell(r, 2).value = "Reverse DCF solves for free cash flow, not revenue: UFCF ramps linearly in dollars from the pitch-case FY2026E level to a solved FY2035E level, plus a Gordon terminal value. Because enterprise value is linear in that level, it solves in closed form (rows 87-88)."
    if isinstance(v, str) and v.startswith("The solver is a 30-step bisection"): w.cell(r, 2).value = "No iteration is required; the sensitivity grid re-solves the same closed form for each WACC and terminal growth pair."
# ---- Cover outputs ----
cv = wb["Cover"]
for r in range(5, 40):
    b = cv.cell(r, 2).value
    if isinstance(b, str) and "Market-Implied FCF CAGR" in b:
        cv.cell(r, 2).value = "Market-Implied FY2035E UFCF ($mm) / margin"; cv.cell(r, 3).value = f"=TEXT('WACC and Reverse DCF (KW)'!D64,\"#,##0\")&\" / \"&TEXT('WACC and Reverse DCF (KW)'!D65,\"0.0%\")"; cv.cell(r, 3).font = font(GREEN, italic=True)
    if isinstance(b, str) and "Pitch-Case FCF CAGR" in b:
        cv.cell(r, 2).value = "Pitch-Case FY2035E UFCF ($mm) / margin"; cv.cell(r, 3).value = f"=TEXT('WACC and Reverse DCF (KW)'!D63,\"#,##0\")&\" / \"&TEXT('WACC and Reverse DCF (KW)'!D66,\"0.0%\")"; cv.cell(r, 3).font = font(GREEN, italic=True)
sm = wb["Summary"]
for row in sm.iter_rows():
    for c in row:
        if isinstance(c.value, str) and c.value.startswith("Reverse DCF holds"): c.value = "Reverse DCF solves for the FY2035E free cash flow the current enterprise value requires (linear dollar ramp from the FY2026E pitch-case burn), not for revenue growth."
# ---- Summary block (N20:O34) pointed at the old rows; re-point to the FCF outputs ----
W = "'WACC and Reverse DCF (KW)'"
SUMM = [("FY2026E Unlevered FCF, pitch case ($mm)", f"={W}!D61", FMT_MM), ("FY2035E Unlevered FCF, pitch case ($mm)", f"={W}!D63", FMT_MM),
        ("Market-Implied FY2035E Unlevered FCF ($mm)", f"={W}!D64", FMT_MM), ("Market-Implied FY2035E UFCF Margin (on pitch revenue)", f"={W}!D65", FMT_PCT),
        ("Pitch-Case FY2035E UFCF Margin", f"={W}!D66", FMT_PCT), ("Gap: market-implied less pitch-case FY2035E UFCF ($mm)", f"={W}!D67", FMT_MM),
        ("Market-Implied FY2035E UFCF as a multiple of the pitch case", f"={W}!D68", FMT_X)]
for i, (lab, f, fmt) in enumerate(SUMM):
    r = 22 + i; sm[f"N{r}"].value = lab; sm[f"O{r}"].value = f; sm[f"O{r}"].number_format = fmt; sm[f"O{r}"].font = font(GREEN, italic=True)
sm["N29"].value = "Implied FY2035E UFCF ($mm) by WACC (terminal growth as on the DCF tab):"
for i, r in enumerate((30, 31, 32)):
    sm[f"N{r}"].value = f"={W}!C{92+i}"; sm[f"N{r}"].number_format = FMT_PCT; sm[f"N{r}"].font = font(GREEN, italic=True)
    sm[f"O{r}"].value = f"={W}!F{92+i}"; sm[f"O{r}"].number_format = FMT_MM; sm[f"O{r}"].font = font(GREEN, italic=True)
for r in (33, 34): sm[f"N{r}"].value = None; sm[f"O{r}"].value = None
for o in OUT: wb.save(o)
print("saved")
