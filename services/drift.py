import pandas as  pd

def drift_summary(variance_df: pd.DataFrame) -> dict:
    if variance_df.empty:
        return {
            "status": "No actuals loaded",
            "avg_revenue_variance": 0,
            "confidence_degradation": 0,
        }

    avg_abs_var = variance_df["revenue_variance_pct"].abs().mean()
    status = "Stable" if avg_abs_var < 0.08 else "Watch" if avg_abs_var < 0.15 else "Drift Risk"
    
    return {
        "status": status,
        "avg_revenue_variance": round(float(avg_abs_var), 4),
        "confidence_degradation": round(float(min(avg_abs_var * 1.7, 0.35)), 4),
    }