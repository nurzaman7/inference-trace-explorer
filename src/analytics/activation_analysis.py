"""Activation summary metrics."""

import numpy as np


def vector_stats(vector: list[float]) -> dict[str, float]:
    arr = np.array(vector, dtype=float)
    return {"mean": float(arr.mean()), "std": float(arr.std()), "max": float(arr.max())}
