from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np

MODEL = Path("models/marketsim_rf.joblib")
METRICS = Path("models/model_metrics.json")

def load_model():
    return joblib.load(MODEL)

def load_metrics():
    return json.loads(METRICS.read_text())

def predict_scenario(assumptions: dict) -> dict:
    pipe = load_model()
    X = pd.DataFrame([assumptions])
    pred = pipe.predict(X)[0]

    revenue, units, margin = pred
    baseline_revenue = assumptions.get("baseline_revenue", revenue * 0.94)
    lift = (revenue - baseline_revenue) / max(baseline_revenue, 1)

    confidence = np.clip(
        0.92
        - abs(assumptions["pricing_change"]) * 0.012
        - assumptions["competitor_pressure"] / 700
        + assumptions["inventory_availability"] / 1600,
        0.45,
        0.95,
    )

    return {
        "predicted_revenue": round(float(revenue), 2),
        "predicted_unit_volume": round(float(units), 0),
        "predicted_margin": round(float(margin), 2),
        "campaign_lift_estimate": round(float(lift), 4),
        "confidence_score": round(float(confidence), 3),
        "model_version": load_metrics()["model_version"],
    }