"""Token usage analytics."""

import pandas as pd


def token_totals(df: pd.DataFrame) -> dict[str, int]:
    if df.empty:
        return {"tokens_in": 0, "tokens_out": 0}
    return {
        "tokens_in": int(df["tokens_in"].sum()),
        "tokens_out": int(df["tokens_out"].sum()),
    }
