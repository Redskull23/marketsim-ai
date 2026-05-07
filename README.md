# MarketSim AI

MarketSim AI demonstrates how enterprise analytical enablement evolves from static dashboards into AI-assisted decision simulation systems.

## Streamlit Cloud Secrets

In Streamlit Cloud, configure secrets at: Manage app -> Settings -> Secrets.

```toml
OPENAI_API_KEY = "sk-..."
APP_PASSWORD = "your-demo-password"
OPENAI_MODEL = "gpt-4.1-mini"
```

Never commit API keys to GitHub.

## Setup

```bash
uv sync
cp .env.example .env
uv run python data/generate_synthetic_data.py
uv run python models/train_model.py
uv run streamlit run streamlit_app.py
```