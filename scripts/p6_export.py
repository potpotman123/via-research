"""Phase 6: export the census and supporting tables to out/via_contract_census.xlsx (one sheet per table)."""
import csv
import pandas as pd
from common import ROOT, log
OUT = ROOT / "out"
census = pd.read_csv(OUT / "via_contract_census.csv", dtype=str).fillna("")
via = census[~census.contract_action.isin(["competitor-award", "deployment-observed"])]
sheets = {
    "census_via_actions": via,
    "post_2025_12_16": via[via.signed_after_2025_12_16 == "1"].sort_values("award_or_approval_date"),
    "losses_and_competitors": census[census.contract_action.isin(["competitor-award", "termination", "non-renewal", "budget-exclusion"])].sort_values("award_or_approval_date"),
    "app_only_observed": census[census.contract_action == "deployment-observed"],
    "ntd_via_payments": pd.read_csv(ROOT / "text/enum/ntd_contractual_hits.csv", dtype=str).fillna(""),
    "ntd_monthly_dr": pd.read_csv(ROOT / "text/enum/ntd_monthly_via_agencies.csv", dtype=str).fillna(""),
    "omnia_price_schedule": pd.read_csv(ROOT / "text/enum/omnia_price_schedule.csv", dtype=str).fillna(""),
    "safer_fleets": pd.read_csv(ROOT / "text/enum/safer_snapshots.csv", dtype=str).fillna(""),
    "targets": pd.read_csv(ROOT / "text/enum/targets.csv", dtype=str).fillna(""),
    "qa_flags": pd.read_csv(OUT / "qa_flags.csv", dtype=str).fillna(""),
    "corrections_applied": pd.read_csv(ROOT / "shards/_corrections.csv", dtype=str).fillna(""),
}
with pd.ExcelWriter(OUT / "via_contract_census.xlsx", engine="openpyxl") as xw:
    for name, df in sheets.items():
        df.to_excel(xw, sheet_name=name[:31], index=False)
        ws = xw.sheets[name[:31]]
        for col in ws.columns:
            width = min(60, max(10, max((len(str(c.value)) for c in col[:200] if c.value), default=10) + 2))
            ws.column_dimensions[col[0].column_letter].width = width
        ws.freeze_panes = "A2"
log("wrote out/via_contract_census.xlsx: " + ", ".join(f"{k}={len(v)}" for k, v in sheets.items()))
