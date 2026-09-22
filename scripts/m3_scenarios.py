"""Scenario runner: copy KW VIA MODEL.xlsx to scratch, set input cells, recalc with LibreOffice, read outputs. The real file is never modified.
Usage: .venv/bin/python scripts/m3_scenarios.py  (edit SCENARIOS below)."""
import openpyxl, subprocess, os, shutil
SRC = "/Users/kwu/Downloads/KW VIA MODEL.xlsx"; D = "/Users/kwu/Documents/VIA/model/tmp/scen"
CL, RB, TS = "Contract Layer (KW)", "Revenue Build (KW)", "Three Statements (KW)"
def run(name, edits):
    os.makedirs(D + "/out", exist_ok=True); wb = openpyxl.load_workbook(SRC)
    for sheet, cells in edits.items():
        for ref, val in cells.items(): wb[sheet][ref].value = val
    p = f"{D}/{name}.xlsx"; wb.save(p); subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", f"{D}/out", p], capture_output=True)
    w = openpyxl.load_workbook(f"{D}/out/{name}.xlsx", data_only=True); rb, ts, d, so = w[RB], w[TS], w["DCF + EPS (KW)"], w["SOTP (KW)"]
    g = lambda ws, ref: (round(ws[ref].value, 3) if isinstance(ws[ref].value, (int, float)) else ws[ref].value)
    return dict(name=name, rev27=g(ts, "S7"), rev30=g(ts, "V7"), rev35=g(ts, "AA7"), g27=g(rb, "S14"), g28=g(rb, "T14"), svc27=g(rb, "S8"), gm27=g(ts, "S13"), gm35=g(ts, "AA13"),
                ebitda27=g(ts, "S52"), ebitda35=g(ts, "AA52"), ebitda35m=g(ts, "AA53"), ufcf30=g(d, "K38"), ufcf35=g(d, "P38"), dcf=g(d, "D81"), sotp=g(so, "C25"), checks=g(rb, "N124"))
def merge(*ds):
    out = {}
    for d_ in ds:
        for k, v in d_.items(): out.setdefault(k, {}).update(v)
    return out
HAZARDS_OFF = {CL: {**{f"B{r}": 0 for r in range(82, 87)}, **{f"C{r}": 1 for r in range(82, 87)}, **{f"D{r}": 0 for r in range(82, 87)}, "C88": 0, "C90": 0}}
HIGH_GROWTH = {CL: {"B96": 400, "B97": 350, "B98": 300, "B99": 300, "V77": 0.10, "W77": 0.08, "X77": 0.06, "Y77": 0.05},
               RB: {"S67": 0.30, "T67": 0.25, "U67": 0.20, "V67": 0.15, "S66": 0.10, "T66": 0.10, "U66": 0.08, "V66": 0.06,
                    "W77": 0.12, "X77": 0.10, "Y77": 0.08, "Z77": 0.07, "AA77": 0.06, "W78": 0.10, "X78": 0.09, "Y78": 0.08, "Z78": 0.07, "AA78": 0.06}}
FLAT_SVC_GM = {RB: {"S61": 0, "T61": 0, "U61": 0, "V61": 0}}
SERVICES_OPEX = {TS: {**dict(zip([f"{c}16" for c in ["T", "U", "V", "W", "X", "Y", "Z", "AA"]], [0.14, 0.13, 0.12, 0.11, 0.10, 0.09, 0.085, 0.08])),
                      **dict(zip([f"{c}18" for c in ["T", "U", "V", "W", "X", "Y", "Z", "AA"]], [0.12, 0.11, 0.10, 0.09, 0.085, 0.08, 0.075, 0.07])),
                      **dict(zip([f"{c}20" for c in ["T", "U", "V", "W", "X", "Y", "Z", "AA"]], [0.15, 0.135, 0.12, 0.11, 0.10, 0.095, 0.09, 0.085]))}}
SCENARIOS = [("S0_base", {}), ("S1_hazards_off", HAZARDS_OFF), ("S2_high_growth", HIGH_GROWTH), ("S3_high_growth_flat_svc_GM", merge(HIGH_GROWTH, FLAT_SVC_GM)), ("S4_S3_plus_services_opex", merge(HIGH_GROWTH, FLAT_SVC_GM, SERVICES_OPEX))]
if __name__ == "__main__":
    res = [run(n, e) for n, e in SCENARIOS]; keys = list(res[0].keys())
    print(" | ".join(f"{k:>9s}" for k in keys))
    for r in res: print(" | ".join(f"{str(r[k])[:9]:>9s}" for k in keys))
    shutil.rmtree(D, ignore_errors=True)
