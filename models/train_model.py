from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

DATA = Path("data/marketsim_synthetic.csv")
MODEL = Path("models/marketsim_rf.joblib")
METRICS = Path("models/model_metrics.json")

TARGETS = ["revenue", "unit_sales", "margin"]
CAT = ["region", "product_category", "channel"]
NUM = [
    "media_spend", "promotion_depth", "weather_index", "seasonality",
    "competitor_pressure", "store_execution_score",
    "inventory_availability", "pricing_change"
]

def train():
    df = pd.read_csv(DATA, parse_dates=["date"])
    X = df[CAT + NUM]
    y = df[TARGETS]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
        ("num", "passthrough", NUM),
    ])

    model = RandomForestRegressor(
        n_estimators=180,
        max_depth=18,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1,
    )

    pipe = Pipeline([("pre", pre), ("model", model)])
    pipe.fit(X_train, y_train)

    pred = pipe.predict(X_test)
    metrics = {
        "model_version": "rf-enterprise-sandbox-v1",
        "r2": float(r2_score(y_test, pred)),
        "mape": float(mean_absolute_percentage_error(y_test, pred)),
        "features": CAT + NUM,
        "targets": TARGETS,
    }

    MODEL.parent.mkdir(exist_ok=True)
    joblib.dump(pipe, MODEL)
    METRICS.write_text(json.dumps(metrics, indent=2))
    print(metrics)

if __name__ == "__main__":
    train()