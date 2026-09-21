"""NTD purchased-transportation payments to Via entities by agency and report year -> docs/ntd_turnkey_summary.md"""
import csv, re
from collections import defaultdict
hits = list(csv.DictReader(open("text/enum/ntd_contractual_hits.csv")))
VIA = re.compile(r"\bvia\b|river\s*north|north\s*river|nomad|crosby|tidewater|port\s*city|sioux\s*falls\s*transit|downtowner|twin\s*cities|viavan", re.I)
EXCL = re.compile(r"via mobility services|via metropolitan|ridecorp|rideco", re.I)
tbl = defaultdict(dict); meta = defaultdict(dict)
for h in hits:
    op = (h.get("Contractee Operator Name") or h.get("Contractee Company Name") or "").strip()
    if not op or EXCL.search(op) or not VIA.search(op): continue
    key = (h["NTD ID"].strip().zfill(5), h["Agency Name"].strip()); y = h["year"]
    tbl[key][y] = tbl[key].get(y, 0) + float(h.get("Direct Payment/Agency Subsidy") or 0)
    meta[key][y] = dict(op=op, voms=(meta[key].get(y, {}).get("voms", 0) + int(float(h.get("VOMS Under Contract") or 0))), modes=meta[key].get(y, {}).get("modes", set()) | {h["Mode"] + "/" + h["TOS"]})
years = ["2019", "2020", "2021", "2022", "2023", "2024"]
L = ["# NTD purchased-transportation payments to Via entities (Direct Payment/Agency Subsidy, $)", "",
     "Source: FTA NTD Annual Database Contractual Relationship tables RY2019-RY2024 (`text/enum/ntd_contractual_files.csv`, downloaded 2026-09-20). Regenerated 2026-09-21 after widening the seller match to plain 'VIA' and misspelled subsidiaries (RY2024 was previously understated at $42.7mm / 15 agencies). Report year = each agency's own fiscal year, not the calendar year. Payments exclude fares retained by Via where 'Fares Retained by' = Seller (about $2.3mm in RY2024). "
     "Excludes Denver RTD's 'Via Mobility Services' (a Boulder, CO nonprofit unrelated to Via Transportation) and competitor rows (RideCo at VIA Metropolitan Transit, San Antonio; RideCorp at Ann Arbor). "
     "Tahoe Downtowner LLC (Placer County) is shown separately as pre-acquisition Downtowner.", "",
     "| NTD ID | Agency | Operator name as reported (latest) | " + " | ".join(years) + " | Latest VOMS | Modes |", "|---|---|---|" + "---|" * len(years) + "---|---|"]
tot = defaultdict(float); dt = defaultdict(float)
for key in sorted(tbl, key=lambda k: -tbl[k].get("2024", 0)):
    ly = max(meta[key]); m = meta[key][ly]; isdt = "downtowner" in m["op"].lower()
    for y in years: (dt if isdt else tot)[y] += tbl[key].get(y, 0)
    L.append(f"| {key[0]} | {key[1]} | {m['op']} | " + " | ".join(f"{tbl[key][y]:,.0f}" if y in tbl[key] else "" for y in years) + f" | {m['voms']} ({ly}) | {', '.join(sorted(m['modes']))} |")
L.append("| | **Total, Via entities** | | " + " | ".join(f"**{tot[y]:,.0f}**" for y in years) + " | | |")
L.append("| | Downtowner (pre-acquisition) | | " + " | ".join(f"{dt[y]:,.0f}" for y in years) + " | | |")
L += ["", "Notes: full reporters only (agencies under the reduced-reporting threshold, universities, non-NTD cities and all non-US customers are absent). "
      "LA Metro's Metro Micro was directly operated by Metro employees through RY2024, so NoMad/Crosby Street will first appear in RY2025 (publishes ~Oct 2026). "
      "An agency known to run Via software but absent here (e.g., Jersey City, Miami-Dade, Trinity Metro whose RY2024 rows list no Via seller) is evidence that Via is software-only there, that a third-party operator holds the purchased-transportation contract, or that the agency reported it under another name or year. "
      "Mode DR = demand response, DT = demand response taxi, MB = bus; TOS PT = purchased transportation, TN = purchased TNC, TX = purchased taxi."]
open("docs/ntd_turnkey_summary.md", "w").write("\n".join(L)); print("\n".join(L[4:-2]))
