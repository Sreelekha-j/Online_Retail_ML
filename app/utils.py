"""
utils.py

Helper file for my Streamlit app.
It loads all the data and models in one place, so every page can use them
without writing the same code again.
Caching makes sure each file is loaded only once, so the app stays fast.
"""
from pathlib import Path
import pandas as pd
import joblib
import streamlit as st

# Project folder = the folder above "app"
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
MODELS = ROOT / "models"

# ---------- Data files (st.cache_data remembers the data after the first load) ----------

@st.cache_data
def load_sales():
    return pd.read_parquet(DATA / "clean_sales.parquet")


@st.cache_data
def load_rfm():
    return pd.read_parquet(DATA / "rfm_clusters.parquet")


@st.cache_data
def load_churn_current():
    return pd.read_parquet(DATA / "churn_current.parquet")

# ---------- Models (st.cache_resource keeps the model in memory) ----------

@st.cache_data
def load_results():
    return pd.read_csv(MODELS / "all_results.csv")


@st.cache_data
def load_importance():
    return pd.read_csv(MODELS / "feature_importance.csv")


@st.cache_resource
def load_final_model():
    return joblib.load(MODELS / "final_model.pkl")


@st.cache_resource
def load_cluster_tools():
    scaler = joblib.load(MODELS / "rfm_scaler.pkl")
    kmeans = joblib.load(MODELS / "kmeans.pkl")
    names = joblib.load(MODELS / "cluster_names.pkl")
    return scaler, kmeans, names


# ---------- Dashboard styling ----------

def apply_style():
    """Makes the KPI cards look like dashboard cards (white box, rounded corners, shadow)."""
    st.markdown("""
        <style>
        [data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-left: 6px solid #4F46E5;
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }
        [data-testid="stMetricLabel"] p {
            font-size: 15px;
            color: #6B7280;
        }
        [data-testid="stMetricValue"] {
            font-size: 30px;
            font-weight: 700;
            color: #1F2937;
        }
        .block-container {
            padding-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)