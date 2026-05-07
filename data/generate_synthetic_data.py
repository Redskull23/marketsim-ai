from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("data/marketsim_synthetic.csv")

REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
CATEGORIES = ["Sparkling", "Still", "Energy", "Tea", "Juice"]
CHANNELS = ["Grocery", "Convenience", "Foodservice", "Club", "Dollar"]

def generate(n_rows: int = 12000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2022-01-01", periods=156, freq="W")

    rows = []
    for i in range(n_rows):
        date = rng.choice(dates)
        region = rng.choice(REGIONS)
        category = rng.choice(CATEGORIES)
        channel = rng.choice(CHANNELS)

        week = pd.Timestamp(date).isocalendar().week
        seasonality = 1 + 0.18 * np.sin(2 * np.pi * week / 52)
        weather_index = rng.normal(70, 14)
        competitor_pressure = np.clip(rng.normal(50, 18), 0, 100)
        media_spend = rng.lognormal(10.3, 0.45)
        promo_depth = np.clip(rng.normal(18, 8), 0, 45)
        store_execution_score = np.clip(rng.normal(82, 9), 45, 100)
        inventory_availability = np.clip(rng.normal(92, 6), 60, 100)
        pricing_change = np.clip(rng.normal(1.5, 4), -10, 15)

        region_factor = {
            "Northeast": 1.05, "Southeast": 1.12, "Midwest": 0.96,
            "Southwest": 0.98, "West": 1.08
        }[region]
        category_factor = {
            "Sparkling": 1.15, "Still": 0.9, "Energy": 1.25,
            "Tea": 0.82, "Juice": 0.78
        }[category]

        lift = (
            0.00045 * media_spend
            + 21 * promo_depth
            + 14 * store_execution_score
            + 16 * inventory_availability
            - 18 * competitor_pressure
            - 75 * pricing_change
            + 9 * weather_index
        )

        base_units = 42000 * region_factor * category_factor * seasonality
        units = max(1000, base_units + lift + rng.normal(0, 7000))
        price = 2.1 * (1 + pricing_change / 100)
        revenue = units * price
        margin_rate = np.clip(
            0.37 - promo_depth / 220 - competitor_pressure / 900 + store_execution_score / 900,
            0.12, 0.48
        )
        margin = revenue * margin_rate

        rows.append({
            "date": date,
            "region": region,
            "product_category": category,
            "channel": channel,
            "media_spend": round(media_spend, 2),
            "promotion_depth": round(promo_depth, 2),
            "weather_index": round(weather_index, 2),
            "seasonality": round(seasonality, 4),
            "competitor_pressure": round(competitor_pressure, 2),
            "store_execution_score": round(store_execution_score, 2),
            "inventory_availability": round(inventory_availability, 2),
            "pricing_change": round(pricing_change, 2),
            "unit_sales": round(units),
            "revenue": round(revenue, 2),
            "margin": round(margin, 2),
        })

    return pd.DataFrame(rows).sort_values("date")

if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    df = generate()
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df):,} rows to {OUT}")