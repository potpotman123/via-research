"""Reverse DCF on free cash flow, self-contained (WACC and Reverse DCF (KW) sheet, rows 54-137).
No pitch-case inputs. The only company figure is FY2025A unlevered FCF on a reported basis (DCF tab actual column).
Solve 1 (closed form): the FY2035E UFCF the current enterprise value requires, with UFCF ramping linearly in dollars from FY2025A.
Solve 2 (30-step bisection in cells): the FCF CAGR the current EV requires from a stated base year and base FCF, with a linear ramp from
FY2025A to the base and Gordon terminal value. Sensitivities: WACC x terminal growth (solve 1) and base FCF (solve 2)."""
import re, openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from datetime import date
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

wb = openpyxl.load_workbook(SRC); w = wb["WACC and Reverse DCF (KW)"]; DCF = "'DCF + EPS (KW)'"
def wrow(prefix, col=2, lo=1, hi=60):
    for r in range(lo, hi):
        v = w.cell(r, col).value
        if isinstance(v, str) and v.strip().lower().startswith(prefix.lower()): return r
    raise KeyError(prefix)
R_EV, R_WACC = wrow("Enterprise Value"), wrow("Weighted Average Cost of Capital", lo=40)
print("EV row", R_EV, "| WACC row", R_WACC)
refs = [(ws.title, c.coordinate, c.value[:60]) for ws in wb.worksheets if ws.title != w.title for row in ws.iter_rows() for c in row
        if isinstance(c.value, str) and c.value.startswith("=") and re.search(r"WACC and Reverse DCF \(KW\)'!\$?[A-Z]+\$?(5[4-9]|[6-9]\d|1[0-3]\d)\b", c.value)]
print("external references into rows 54-137:", len(refs), "(Summary block re-pointed below)")
for r in range(54, 139):
    for c in range(2, 40):
        cell = w.cell(r, c); cell.value = None; cell.font = font(); cell.number_format = "General"; cell.border = Border(); cell.alignment = Alignment()
w["B3"].value = "Market-implied expectations: what free cash flow does the current enterprise value require?  |  $ in millions except per share"

# ---------- assumptions (rows 54-64) ----------
put(w, "B54", "VIA Reverse DCF on Free Cash Flow (no forecast inputs; the only company figure is reported FY2025A free cash flow)", bold=True, size=14)
AS = [(55, "Current Enterprise Value", "$mm", f"=D{R_EV}", BLACK, FMT_MM, ""),
      (56, "WACC", "%", f"=G{R_WACC}", BLACK, FMT_PCT, ""),
      (57, "Terminal Growth Rate (input)", "%", 0.03, RED, FMT_PCT, "Same default as the DCF tab; an assumption, not a forecast."),
      (58, "Valuation Date (input)", "date", date(2026, 9, 18), RED, "m/d/yyyy", ""),
      (59, "Fiscal Year End (input)", "date", date(2026, 12, 31), RED, "m/d/yyyy", ""),
      (60, "Stub Period (fraction of FY2026 remaining)", "yrs", "=(D59-D58)/365", BLACK, "0.000", ""),
      (61, "Mid-Year Convention (1 = yes)", "flag", 1, RED, "0", ""),
      (62, "Horizon: FY2026E stub + FY2027E-FY2035E", "yrs", 10, BLACK, "0", "t = 0 is FY2025A (reported), t = 1 the FY2026E stub, t = 10 FY2035E."),
      (63, "FY2025A Unlevered FCF, reported basis (DCF tab actual column: NOPAT + D&A - capex - change in NWC)", "$mm", f"={DCF}!F38", GREEN, FMT_MM, "Reported year, not a projection. Both solves start the path here."),
      (64, "Base year for the FCF CAGR solve (input: 2028-2032)", "year", 2028, RED, "0", "Year from which free cash flow is assumed to compound at the solved rate; the path ramps linearly from FY2025A to the base level before that.")]
for r, lab, unit, f, colr, fmt, nt in AS:
    put(w, f"B{r}", lab); put(w, f"C{r}", unit, align="right"); put(w, f"D{r}", f, colr, italic=(colr in (GREEN, RED)), fmt=fmt)
    if nt: put(w, f"F{r}", nt, GREY, italic=True)
put(w, "B65", "Base FCF for the FCF CAGR solve (input, $mm; the level reached in the base year)", ); put(w, "C65", "$mm", align="right"); put(w, "D65", 25.0, RED, italic=True, fmt=FMT_MM)
put(w, "F65", "Deliberately a market-style assumption, not the pitch case: the sensitivity table at the bottom re-solves for $10mm, $25mm, $50mm and $75mm.", GREY, italic=True)

# ---------- solve 1: implied FY2035E UFCF, dollar ramp from FY2025A (rows 67-88) ----------
put(w, "B67", "Solve 1: Market-Implied FY2035E Unlevered FCF (linear dollar ramp from FY2025A; closed form)", bold=True, size=14)
S1 = [(68, "Market-Implied FY2035E Unlevered FCF (solved)", "$mm", "=(D55-D86)/D87", FMT_MM, True),
      (69, "Implied Terminal EV / FY2035E UFCF = (1 + g) / (WACC - g)", "x", "=(1+D57)/(D56-D57)", FMT_X, False),
      (70, "Implied FY2035E FCF yield on today's enterprise value", "%", "=IF(D55=0,0,D68/D55)", FMT_PCT, False),
      (71, "Implied year free cash flow turns positive on this path", "year", "=2026+SUMPRODUCT((E79:N79<=0)*1)", "0", False),
      (72, "Cumulative implied UFCF, FY2026E stub - FY2035E", "$mm", "=SUM(E79:N79)", FMT_MM, False),
      (73, "PV of Terminal Value as % of EV", "%", "=IF(D55=0,0,D85/D55)", FMT_PCT, False)]
for r, lab, unit, f, fmt, bold in S1: put(w, f"B{r}", lab, bold=bold); put(w, f"C{r}", unit, align="right"); put(w, f"D{r}", f, bold=bold, fmt=fmt)
put(w, "F68", "EV = A + B x X with UFCF_t = FCF2025 x (1 - t/10) + X x t/10 (FY2026E x stub); so X = (EV - A) / B, rows 86-87.", GREY, italic=True)
years = ["FY2025A"] + ["FY2026E (stub)"] + [f"FY{y}E" for y in range(2027, 2036)]; cols = [L(4 + i) for i in range(11)]   # D..N, t = 0..10
put(w, "B75", "Fiscal Year", bold=True); put(w, "C75", "Units", align="right", border_b=True)
for c, y in zip(cols, years): put(w, f"{c}75", y, bold=True, align="right", border_b=True)
put(w, "B76", "Year Index (t)", ); put(w, "C76", "#", align="right")
put(w, "B77", "Ramp weight w = t / 10"); put(w, "C77", "x", align="right")
put(w, "B78", "Discount Period (stub in FY2026E; mid-year convention)"); put(w, "C78", "yrs", align="right")
put(w, "B79", "Market-Implied Unlevered FCF", bold=True); put(w, "C79", "$mm", align="right")
put(w, "B80", "Discount Factor"); put(w, "C80", "x", align="right")
put(w, "B81", "Present Value of Implied UFCF"); put(w, "C81", "$mm", align="right")
for i, c in enumerate(cols):
    put(w, f"{c}76", i, fmt="0", align="right"); put(w, f"{c}77", f"={c}76/$D$62", fmt="0.000")
    if i == 0:
        put(w, f"{c}78", None); put(w, f"{c}79", "=$D$63", GREEN, italic=True, fmt=FMT_MM); put(w, f"{c}80", None); put(w, f"{c}81", None)
    else:
        put(w, f"{c}78", f"=IF({c}76=1,$D$60*(1-0.5*$D$61),$D$60+{c}76-1-0.5*$D$61)", fmt="0.000")
        put(w, f"{c}79", f"=($D$63*(1-{c}77)+$D$68*{c}77)*IF({c}76=1,$D$60,1)", bold=True, fmt=FMT_MM)
        put(w, f"{c}80", f"=1/(1+$D$56)^{c}78", fmt="0.000"); put(w, f"{c}81", f"={c}79*{c}80", fmt=FMT_MM)
S1T = [(83, "Terminal Value at FY2035E = implied UFCF x (1 + g) / (WACC - g)", "$mm", "=N79*(1+$D$57)/($D$56-$D$57)"),
       (84, "Sum of PV of Implied UFCF", "$mm", "=SUM(E81:N81)"),
       (85, "Present Value of Terminal Value (discounted stub + 9 years)", "$mm", "=D83/(1+$D$56)^($D$60+9)"),
       (86, "A: PV of the part of the path fixed by FY2025A FCF", "$mm", "=$D$63*SUMPRODUCT(E80:N80,1-E77:N77,1+(E76:N76=1)*($D$60-1))"),
       (87, "B: PV weight on the solved FY2035E UFCF (path + terminal value)", "x", "=SUMPRODUCT(E80:N80,E77:N77,1+(E76:N76=1)*($D$60-1))+(1+$D$57)/($D$56-$D$57)/(1+$D$56)^($D$60+9)"),
       (88, "Check: PV of path + PV of TV - Current EV (should be 0)", "$mm", "=ROUND(D84+D85-D55,3)")]
for r, lab, unit, f in S1T:
    put(w, f"B{r}", lab, italic=(r >= 86), color=GREY if r >= 86 else BLACK); put(w, f"C{r}", unit, align="right")
    put(w, f"D{r}", f, GREEN if r == 88 else BLACK, italic=(r >= 86), fmt={"x": "0.000"}.get(unit, FMT_MM))

# ---------- solve 2: implied FCF CAGR from a base (rows 90-133) ----------
put(w, "B90", "Solve 2: Market-Implied FCF CAGR from the base year (linear ramp FY2025A -> base, then compounding; 30-step bisection in cells)", bold=True, size=14)
put(w, "B91", "Market-Implied FCF CAGR, base year to FY2035E (solved, at the base FCF in D65)", bold=True); put(w, "C91", "%", align="right"); put(w, "D91", "=F133", bold=True, fmt=FMT_PCT)
put(w, "B92", "Implied FY2035E UFCF on this path"); put(w, "C92", "$mm", align="right"); put(w, "D92", "=$D$65*(1+D91)^(2035-$D$64)", fmt=FMT_MM)
put(w, "B93", "Implied FY2035E UFCF as a multiple of the base FCF"); put(w, "C93", "x", align="right"); put(w, "D93", "=IF($D$65=0,0,D92/$D$65)", fmt=FMT_X)
put(w, "F91", "Read as: if free cash flow reaches the base level in the base year, this is the annual growth it must then sustain to 2035 for today's price to be fair.", GREY, italic=True)
# helper rows for solve 2 (columns E..N = t 1..10 = FY2026E..FY2035E)
put(w, "B96", "Helper rows for solve 2 (per year t = 1..10)", bold=True, size=11)
put(w, "B97", "Year"); put(w, "B98", "Discount factor DF(t)"); put(w, "B99", "Pre-base ramp weight (share of the way from FY2025A to the base year)"); put(w, "B100", "Compounding years past the base (0 before the base year)"); put(w, "B101", "In compounding phase (1 = yes)")
for i, c in enumerate(cols[1:], start=1):
    put(w, f"{c}97", 2025 + i, fmt="0", align="right", size=11)
    put(w, f"{c}98", f"={c}80", fmt="0.000", size=11)
    put(w, f"{c}99", f"=IF({c}97<$D$64,({c}97-2025)/($D$64-2025),0)", fmt="0.000", size=11)
    put(w, f"{c}100", f"=MAX(0,{c}97-$D$64)", fmt="0", size=11); put(w, f"{c}101", f"=IF({c}97>=$D$64,1,0)", fmt="0", size=11)
put(w, "F102", "Pre-base years: UFCF_t = FCF2025 + (base - FCF2025) x ramp weight (FY2026E x stub). Base year onward: UFCF_t = base x (1 + g)^(years past base).", GREY, italic=True)
# PV of the pre-base ramp for a given base FCF (independent of g): row 103 per scenario column
bases = [("D", "$D$65"), ("F", "$F$104"), ("H", "$H$104"), ("J", "$J$104"), ("L", "$L$104")]   # scenario blocks: D uses the input; F/H/J/L use the sensitivity bases
put(w, "B103", "PV of pre-base ramp (independent of g)", italic=True, size=11)
put(w, "B104", "Base FCF for each scenario block", italic=True, size=11)
put(w, "F104", 10.0, RED, italic=True, fmt=FMT_MM, size=11); put(w, "H104", 25.0, RED, italic=True, fmt=FMT_MM, size=11); put(w, "J104", 50.0, RED, italic=True, fmt=FMT_MM, size=11); put(w, "L104", 75.0, RED, italic=True, fmt=FMT_MM, size=11)
put(w, "D104", "=$D$65", fmt=FMT_MM, size=11)
for col, base in bases:
    put(w, f"{col}103", f"=SUMPRODUCT($E$98:$N$98,(1-$E$101:$N$101),($D$63+({base}-$D$63)*$E$99:$N$99),1+($E$97:$N$97=2026)*($D$60-1))", fmt=FMT_MM, size=11)
# bisection blocks: each block = 4 columns (g low, g high, g mid, PV(mid) - EV) starting at column D, F+... use blocks at D-G? They overlap; lay them out in 4-column groups: D:G, H:K, L:O, P:S, T:W
put(w, "B105", "Bisection on g (30 steps): PV(pre-base ramp) + PV(compounding phase) + PV(TV) - EV. Blocks: input base (D-G), then $10mm, $25mm, $50mm, $75mm bases.", italic=True, size=11)
blocks = [("D", "$D$104"), ("H", "$F$104"), ("L", "$H$104"), ("P", "$J$104"), ("T", "$L$104")]
ramp_pv = {"D": "$D$103", "H": "$F$103", "L": "$H$103", "P": "$J$103", "T": "$L$103"}
for start, base in blocks:
    c0 = openpyxl.utils.column_index_from_string(start); lo, hi, mid, res = L(c0), L(c0 + 1), L(c0 + 2), L(c0 + 3)
    put(w, f"{lo}106", "g low", bold=True, size=10, align="right", border_b=True); put(w, f"{hi}106", "g high", bold=True, size=10, align="right", border_b=True)
    put(w, f"{mid}106", "g mid", bold=True, size=10, align="right", border_b=True); put(w, f"{res}106", "PV(mid) - EV", bold=True, size=10, align="right", border_b=True)
    for k in range(30):
        r = 107 + k
        if k == 0: put(w, f"{lo}{r}", -0.5, size=10, fmt=FMT_PCT); put(w, f"{hi}{r}", 3.0, size=10, fmt=FMT_PCT)
        else:
            put(w, f"{lo}{r}", f"=IF({res}{r-1}>0,{lo}{r-1},{mid}{r-1})", size=10, fmt=FMT_PCT); put(w, f"{hi}{r}", f"=IF({res}{r-1}>0,{mid}{r-1},{hi}{r-1})", size=10, fmt=FMT_PCT)
        put(w, f"{mid}{r}", f"=({lo}{r}+{hi}{r})/2", size=10, fmt=FMT_PCT)
        put(w, f"{res}{r}", (f"={ramp_pv[start]}+SUMPRODUCT($E$98:$N$98,$E$101:$N$101,{base}*(1+{mid}{r})^$E$100:$N$100)"
                              f"+{base}*(1+{mid}{r})^(2035-$D$64)*(1+$D$57)/($D$56-$D$57)/(1+$D$56)^($D$60+9)-$D$55"), size=10, fmt=FMT_MM)
put(w, "B107", "Iteration 1 ... 30 (row 136 holds the converged g mid)", italic=True, size=10)
# sensitivity summary rows (row 134-135): base FCF -> implied CAGR
put(w, "B94", "Sensitivity: implied FCF CAGR (base year to FY2035E) by base FCF ($mm, red) ->", bold=True, size=11)
put(w, "B95", "Implied FCF CAGR", bold=True, size=11)
for j, (start, base) in enumerate(blocks[1:]):
    c0 = openpyxl.utils.column_index_from_string(start); col = L(4 + j)
    put(w, f"{col}94", f"={base}", RED, italic=True, fmt=FMT_MM, border_b=True, align="right", size=11); put(w, f"{col}95", f"={L(c0+2)}136", fmt=FMT_PCT, size=11)
put(w, "D91", "=F136", bold=True, fmt=FMT_PCT)   # converged mid of the input-base block (columns D-G, mid = F)
# ---------- solve 1 sensitivity grid: placed at rows 138-142 (multiples table starts at 139 in the original: check and shift if needed) ----------
# find the multiples header to avoid overwriting
if True:
    put(w, "P67", "Solve 1 sensitivity: implied FY2035E UFCF ($mm)  |  rows: WACC  |  columns: terminal growth", bold=True, size=11)
    gs = [0.01, 0.02, 0.03, 0.04]
    put(w, "P68", "WACC \\ g", bold=True, border_b=True, size=11)
    for j, g in enumerate(gs): put(w, f"{L(17 + j)}68", g, RED, italic=True, fmt=FMT_PCT, border_b=True, align="right", size=11)
    for i, dw in enumerate((-0.01, 0.0, 0.01)):
        r = 69 + i; put(w, f"P{r}", f"=$D$56+({dw})", RED, italic=True, fmt=FMT_PCT, size=11)
        for j in range(len(gs)):
            col = L(17 + j); wref, gref = f"$P{r}", f"{col}$68"
            A_ = f"$D$63*SUMPRODUCT((1+{wref})^(-$E$78:$N$78),1-$E$77:$N$77,1+($E$76:$N$76=1)*($D$60-1))"
            B_ = f"SUMPRODUCT((1+{wref})^(-$E$78:$N$78),$E$77:$N$77,1+($E$76:$N$76=1)*($D$60-1))+(1+{gref})/({wref}-{gref})/(1+{wref})^($D$60+9)"
            put(w, f"{col}{r}", f"=($D$55-{A_})/({B_})", fmt=FMT_MM, size=11)
    put(w, "P73", "Discount periods in row 78 are held at the base WACC's schedule (they do not depend on WACC).", GREY, italic=True, size=10)
# notes
for r in range(140, 160):
    v = w.cell(r, 2).value
    if isinstance(v, str) and v.startswith("Reverse DCF"): w.cell(r, 2).value = "Reverse DCF on free cash flow with no forecast inputs: the path starts at reported FY2025A UFCF. Solve 1 finds the FY2035E FCF the price requires (closed form); solve 2 finds the FCF CAGR from a stated base year and level (bisection in cells)."
    if isinstance(v, str) and v.startswith("The solver is a 30-step bisection"): w.cell(r, 2).value = "Solve 2 uses a 30-step bisection on g between -50% and +300%; each block re-solves for a different base FCF."
    if isinstance(v, str) and v.startswith("No iteration is required"): w.cell(r, 2).value = "Solve 2 uses a 30-step bisection on g between -50% and +300%; each block re-solves for a different base FCF."
# ---------- Summary block (N20:O34) ----------
sm = wb["Summary"]; W = "'WACC and Reverse DCF (KW)'"
SUMM = [("FY2025A Unlevered FCF, reported basis ($mm)", f"={W}!D63", FMT_MM), ("Market-Implied FY2035E Unlevered FCF ($mm)", f"={W}!D68", FMT_MM),
        ("Implied year FCF turns positive", f"={W}!D71", "0"), ("Implied FY2035E FCF yield on today's EV", f"={W}!D70", FMT_PCT),
        ("Implied terminal EV / FY2035E UFCF", f"={W}!D69", FMT_X), ("Market-Implied FCF CAGR from the base year (base in WACC tab D64-D65)", f"={W}!D91", FMT_PCT),
        ("Implied FY2035E UFCF on the CAGR path ($mm)", f"={W}!D92", FMT_MM)]
for i, (lab, f, fmt) in enumerate(SUMM):
    r = 22 + i; sm[f"N{r}"].value = lab; sm[f"O{r}"].value = f; sm[f"O{r}"].number_format = fmt; sm[f"O{r}"].font = font(GREEN, italic=True)
sm["N29"].value = "Implied FCF CAGR by base FCF ($mm -> CAGR):"
for i, col in enumerate("DEFG"):
    r = 30 + i; sm[f"N{r}"].value = f"={W}!{col}94"; sm[f"N{r}"].number_format = FMT_MM; sm[f"N{r}"].font = font(GREEN, italic=True)
    sm[f"O{r}"].value = f"={W}!{col}95"; sm[f"O{r}"].number_format = FMT_PCT; sm[f"O{r}"].font = font(GREEN, italic=True)
sm["N34"].value = None; sm["O34"].value = None
for row in sm.iter_rows():
    for c in row:
        if isinstance(c.value, str) and c.value.startswith("Reverse DCF"): c.value = "Reverse DCF uses no forecast inputs: it solves for the FY2035E free cash flow and the FCF growth rate the current enterprise value requires, starting from reported FY2025A free cash flow."
# ---------- Cover ----------
cv = wb["Cover"]
for r in range(5, 40):
    b = cv.cell(r, 2).value
    if isinstance(b, str) and b.startswith("Market-Implied FY2035E UFCF"):
        cv.cell(r, 2).value = "Market-Implied FY2035E UFCF ($mm) / year FCF turns positive"; cv.cell(r, 3).value = f"=TEXT({W}!D68,\"#,##0\")&\" / \"&TEXT({W}!D71,\"0\")"; cv.cell(r, 3).font = font(GREEN, italic=True)
    if isinstance(b, str) and b.startswith("Pitch-Case FY2035E UFCF"):
        cv.cell(r, 2).value = "Market-Implied FCF CAGR (base year to FY2035E)"; cv.cell(r, 3).value = f"=TEXT({W}!D91,\"0.0%\")&\" from $\"&TEXT({W}!D65,\"#,##0\")&\"mm in \"&TEXT({W}!D64,\"0\")"; cv.cell(r, 3).font = font(GREEN, italic=True)
for o in OUT: wb.save(o)
print("saved")
