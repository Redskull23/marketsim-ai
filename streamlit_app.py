import os
import json
import time
import pandas as pd
import plotly.express as px
import streamlit as st

from dotenv import load_dotenv

from ui_components import kpi_card, apply_style
from db.scenario_store import save_scenario, list_scenarios, add_actual, list_actuals
from models.predictor import predict_scenario, load_metrics
from services.actuals import build_variance_table
from services.drift import drift_summary
from agents.analyst_agent import ask_analyst

load_dotenv()
st.set_page_config(page_title="MarketSIM AI", layout="wide")
apply_style()

MAX_CALLS = 5
WINDOW_SECONDS = 3600

app_password = st.secrets.get("APP_PASSWORD")
if app_password:
    password = st.text_input("Demo password", type="password")
    if password != app_password:
        st.info("Enter the demo password to continue.")
        st.stop()

openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
openai_model = st.secrets.get("OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))

if not openai_api_key:
    st.error("OpenAI API key not configured. Add OPENAI_API_KEY to Streamlit secrets.")
    st.stop()

st.title("MarketSIM AI - Marketing Scenario Simulator")
st.caption("AI assisted enterprise decision simulation for marketing, revenue, and margin planning.")

df = pd.read_csv("data/marketsim_synthetic.csv", parse_dates=["date"])
metrics = load_metrics()

with st.sidebar:
    st.header("Scenario Controls")
    region = st.selectbox("Region", sorted(df["region"].unique()), index=1)
    category = st.selectbox("Product Category", sorted(df["product_category"].unique()))
    channel = st.selectbox("Channel", sorted(df["channel"].unique()))
    
    media_spend = st.slider("Media Spend ($K)", 10000, 90000, 35000, 1000)
    promotion_depth = st.slider("Promotion Depth (%)", 0, 45, 18)
    weather_index = st.slider("Weather Index", 30, 110, 72)
    seasonality = st.slider("Seasonality Index", 0.75, 1.25, 1.02)
    competitor_pressure = st.slider("Competitor Pressure", 0, 100, 48)
    store_execution_score = st.slider("Store Execution Score", 45, 100, 84)
    inventory_availability = st.slider("Inventory Availability", 60, 100, 93)
    pricing_change = st.slider("Pricing Change (%)", -10, 15, 2)
    
assumptions = {
    "region": region,
    "product_category": category,
    "channel": channel,
    "media_spend": media_spend,
    "promotion_depth": promotion_depth,
    "weather_index": weather_index,
    "seasonality": seasonality,
    "competitor_pressure": competitor_pressure,
    "store_execution_score": store_execution_score,
    "inventory_availability": inventory_availability,
    "pricing_change": pricing_change,
}

prediction = predict_scenario(assumptions)
k1, k2, k3, k4, k5 = st.columns(5)
with k1: kpi_card("Predicted Revenue", f"${prediction['predicted_revenue']:,.0f}")
with k2: kpi_card("Unit Volume", f"{prediction['predicted_unit_volume']:,.0f}")
with k3: kpi_card("Margin", f"${prediction['predicted_margin']:,.0f}")
with k4: kpi_card("Campaign Lift", f"{prediction['campaign_lift_estimate']:.1%}")
with k5: kpi_card("Confidence", f"{prediction['confidence_score']:.0%}")

tab1, tab2, tab3, tab4 = st.tabs([
    "Performance",
    "Scenario Sandbox",
    "Actuals & Drift",
    "AI Analyst"
])
with tab1:
    c1, c2 = st.columns(2)
    region_perf = df.groupby(["date", "region"], as_index=False)["revenue"].sum()
    with c1:
        st.subheader("Regional Revenue Trend")
        st.plotly_chart(
            px.line(region_perf, x="date", y="revenue", color="region"), 
            use_container_width=True,
        )
    with c2:
        st.subheader("Revenue by Product Category")
        st.plotly_chart(
            px.bar(df, x="product_category", y="revenue"),
            use_container_width=True,
        )
    st.subheader("Model Heath")
    st.json(metrics)
with tab2:
    st.subheader("Scenario Prediction")
    st.json({"assumptions": assumptions, "prediction": prediction})
    
    scenario_name = st.text_input("Scenario Name", value=f"{region} {category} optimization")
    if st.button("Save Scenario"):
        sid = save_scenario(scenario_name, assumptions, prediction)
        st.success(f"Saved scenario #{sid}")
        
    scenarios = list_scenarios()
    st.subheader("Saved Scenarios History")
    if not scenarios.empty:
        display = scenarios.copy()
        display["assumptions"] = display["assumptions_json"].apply(json.loads)
        display["predictions"] = display["predictions_json"].apply(json.loads)
        st.dataframe(display[["id", "timestamp", "scenario_name", "model_version"]], use_container_width=True)
    else:
        st.info("No scenarios saved yet.")
        
with tab3:
    scenarios = list_scenarios()
    actuals = list_actuals()

    st.subheader("Simulate or Enter Actual Outcomes")
    if not scenarios.empty:
        scenario_id = st.selectbox("Scenario", scenarios["id"].tolist())
        actual_revenue = st.number_input("Actual Revenue", value=float(prediction["predicted_revenue"] * 0.96))
        actual_units = st.number_input("Actual Unit Volume", value=float(prediction["predicted_unit_volume"] * 0.97))
        actual_margin = st.number_input("Actual Margin", value=float(prediction["predicted_margin"] * 0.94))
        notes = st.text_area("Actuals Notes", value="Simulated field outcome.")
        if st.button("Save Actual"):
            add_actual(scenario_id, actual_revenue, actual_units, actual_margin, notes)
            st.success("Actual outcome saved.")

    variance = build_variance_table(scenarios, actuals)
    drift = drift_summary(variance)

    st.subheader("Forecast Variance")
    if not variance.empty:
        st.dataframe(variance, use_container_width=True)
        st.plotly_chart(
            px.bar(variance, x="scenario_name", y="revenue_variance_pct",
                title="Revenue Forecast Variance %"),
            use_container_width=True,
        )
    else:
        st.info("Save actuals to activate variance and drift analysis.")
    st.subheader("Drift Status")
    st.json(drift)
    
with tab4: 
    scenarios = list_scenarios()
    actuals = list_actuals()
    variance = build_variance_table(scenarios, actuals)
    drift = drift_summary(variance)
    
    st.subheader("AI Insights Panel")
    question = st.text_area(
        "Ask MarketSim AI",
        value="Why might this scenario underperform prediction, and what should we test next quarter?"
    )
    scenario_context = {
        "current_assumptions": assumptions, 
        "current_prediction": prediction,
        "recent_scenarios": scenarios.head(5).to_dict("records") if not scenarios.empty else [],
        "variance_table": variance.head(5).to_dict("records") if not variance.empty else [],
    }
    if st.button("Generate Analyst Readout"):
        if "usage_log" not in st.session_state:
            st.session_state.usage_log = []

        now = time.time()
        st.session_state.usage_log = [
            t for t in st.session_state.usage_log
            if now - t < WINDOW_SECONDS
        ]

        if len(st.session_state.usage_log) >= MAX_CALLS:
            st.warning("You have reached the demo limit. Please try again later.")
            st.stop()

        st.session_state.usage_log.append(now)

        with st.spinner("Analyzing scenario context ......"):
            answer = ask_analyst(
                question,
                scenario_context,
                metrics,
                drift,
                api_key=openai_api_key,
                model=openai_model,
                max_output_tokens=400,
            )
            st.markdown(answer)