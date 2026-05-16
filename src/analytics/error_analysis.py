"""Error-rate calculations."""

import pandas as pd


def error_rate(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    return float((df["status"] == "error").mean())
