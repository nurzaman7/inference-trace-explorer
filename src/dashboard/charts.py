"""Plotly chart helpers."""

import pandas as pd
import plotly.express as px


def latency_histogram(df: pd.DataFrame):
    if df.empty:
        return None
    return px.histogram(df, x="latency_ms", nbins=30, title="Latency Distribution")
