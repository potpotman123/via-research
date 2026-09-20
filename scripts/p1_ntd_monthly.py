"""Pull NTD monthly UPT/VRH/VOMS (dataset 8bui-9xvu) for every agency that appears in the contractual-relationship hits,
demand-response modes (DR, DT) all types of service, 2018 onward. Output: text/enum/ntd_monthly_via_agencies.csv"""
import csv, json, time, urllib.parse
from common import ENUM, get, log, session, write_csv
hits = list(csv.DictReader(open(ENUM / "ntd_contractual_hits.csv")))
ids = sorted({(h["NTD ID"].strip().zfill(5), h["Agency Name"].strip()) for h in hits if h.get("NTD ID")})
log(f"{len(ids)} agencies")
s = session(); rows = []
for ntd_id, name in ids:
    where = f"ntd_id='{ntd_id}' AND mode in('DR','DT') AND date >= '2018-01-01T00:00:00'"
    url = "https://datahub.transportation.gov/resource/8bui-9xvu.json?$limit=50000&$order=date&$where=" + urllib.parse.quote(where)
    r = get(s, url, timeout=120); time.sleep(0.5)
    if not r or r.status_code != 200:
        log(f"{ntd_id} {name}: status {r.status_code if r else None} {(r.text[:100] if r else '')}"); continue
    data = r.json()
    for d in data:
        rows.append(dict(ntd_id=ntd_id, agency=d.get("agency") or name, mode=d.get("mode"), tos=d.get("tos"), date=(d.get("date") or "")[:10],
                         upt=d.get("upt"), vrh=d.get("vrh"), vrm=d.get("vrm"), voms=d.get("voms"), status=d.get("mode_type_of_service_status")))
    log(f"{ntd_id} {name[:35]}: {len(data)} rows, latest {max((d.get('date') or '')[:10] for d in data) if data else '-'}")
write_csv(ENUM / "ntd_monthly_via_agencies.csv", rows, ["ntd_id", "agency", "mode", "tos", "date", "upt", "vrh", "vrm", "voms", "status"])
