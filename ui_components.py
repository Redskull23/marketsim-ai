import streamlit as st 
def kpi_card(label: str, value: str, delta: str | None =None):
    """Creates a KPI card with a label, value, and optional delta."""
    st.metric(label=label, value=value, delta=delta)
    
def apply_style():
    """Applies custom CSS styles to the Streamlit app."""
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.5rem;}
        div[data-testid="stMetic"] {
            background-color: #F40009; 
            border: 1px solid #F40009;
            padding: 16px;
            border-radius: 14px; 
            color: #F40009;
        }
        .stApp {background-color:#black;}
        h1, h2, h3, label, p, span {color: white;}
        </style>
        """, unsafe_allow_html=True,
        )