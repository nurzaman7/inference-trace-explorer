"""Streamlit dashboard entrypoint."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.storage.sqlite_store import SQLiteStore
from src.storage.query_engine import QueryEngine
from src.dashboard.filters import by_status
from src.dashboard.charts import latency_histogram
from src.dashboard.metrics import fetch_queue_metrics
from src.utils.config import settings


st.set_page_config(page_title="Inference Trace Explorer", layout="wide")
st.title("Inference Trace Explorer")

# Top controls
control_a, control_b = st.columns([3, 1])
with control_a:
    api_base = st.text_input("API Base URL", value=settings.api_base_url)
with control_b:
    st.caption("Queue metrics")
    if st.button("Refresh Metrics"):
        st.rerun()

# Queue metrics cards
q = fetch_queue_metrics(api_base)
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Queue Depth", q["queue_depth"])
m2.metric("Enqueued", q["enqueued_total"])
m3.metric("Written", q["written_total"])
m4.metric("Dropped", q["dropped_total"])
m5.metric("Flush Batches", q["flush_batches_total"])
m6.metric("Writer Errors", q["errors_total"])

st.divider()

# Trace table and charts
store = SQLiteStore(settings.sqlite_path)
query = QueryEngine(store)
rows = query.recent_traces(limit=500)
df = pd.DataFrame(rows)

status = st.selectbox("Status", ["all", "success", "error"])
if not df.empty:
    filtered = by_status(df, status)
    st.dataframe(filtered, use_container_width=True)
    fig = latency_histogram(filtered)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No traces yet. Call POST /infer first.")
