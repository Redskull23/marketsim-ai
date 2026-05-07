CREATE TABLE IF NOT EXISTS scenarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  scenario_name TEXT NOT NULL,
  assumptions_json TEXT NOT NULL,
  predictions_json TEXT NOT NULL,
  model_version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actuals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scenario_id INTEGER,
  timestamp TEXT NOT NULL,
  actual_revenue REAL,
  actual_unit_volume REAL,
  actual_margin REAL,
  notes TEXT,
  FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
);