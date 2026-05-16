"""Dashboard filter helpers."""

import pandas as pd


def by_status(df: pd.DataFrame, status: str) -> pd.DataFrame:
    if status == "all":
        return df
    return df[df["status"] == status]
