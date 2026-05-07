import json
import pandas as pd

def build_variance_table(scenarios: pd.DataFrame, actuals: pd.DataFrame) -> pd.DataFrame:
    if scenarios.empty or actuals.empty:
        return pd.DataFrame()

    records = []
    for _, a in actuals.iterrows():
        s = scenarios[scenarios["id"] == a["scenario_id"]]
        if s.empty:
            continue

        pred = json.loads(s.iloc[0]["predictions_json"])
        records.append({
            "scenario_id": int(a["scenario_id"]),
            "scenario_name": s.iloc[0]["scenario_name"],
            "predicted_revenue": pred["predicted_revenue"],
            "actual_revenue": a["actual_revenue"],
            "revenue_variance_pct": (a["actual_revenue"] - pred["predicted_revenue"]) / pred["predicted_revenue"],
            "predicted_margin": pred["predicted_margin"],
            "actual_margin": a["actual_margin"],
            "margin_variance_pct": (a["actual_margin"] - pred["predicted_margin"]) / pred["predicted_margin"],
        })

    return pd.DataFrame(records)