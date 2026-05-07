# MarketSim AI

MarketSim AI demonstrates how enterprise analytical enablement evolves from static dashboards into AI-assisted decision simulation systems.

## Setup

```bash
uv sync
cp .env.example .env
uv run python data/generate_synthetic_data.py
uv run python models/train_model.py
uv run streamlit run streamlit_app.py