import json
import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd

DB = Path("db/marketsim.sqlite")
SCHEMA = Path("db/schema.sql")

def init_db():
    DB.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB) as con:
        con.executescript(SCHEMA.read_text())

def save_scenario(name: str, assumptions: dict, predictions: dict) -> int:
    init_db()
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO scenarios
            (timestamp, scenario_name, assumptions_json, predictions_json, model_version)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                name,
                json.dumps(assumptions),
                json.dumps(predictions),
                predictions["model_version"],
            ),
        )
        return int(cur.lastrowid)

def list_scenarios() -> pd.DataFrame:
    init_db()
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query("SELECT * FROM scenarios ORDER BY id DESC", con)

def add_actual(scenario_id: int, revenue: float, units: float, margin: float, notes: str = ""):
    init_db()
    with sqlite3.connect(DB) as con:
        con.execute(
            """
            INSERT INTO actuals
            (scenario_id, timestamp, actual_revenue, actual_unit_volume, actual_margin, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (scenario_id, datetime.utcnow().isoformat(), revenue, units, margin, notes),
        )

def list_actuals() -> pd.DataFrame:
    init_db()
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query("SELECT * FROM actuals ORDER BY id DESC", con)