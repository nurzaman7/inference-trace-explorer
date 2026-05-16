"""Synthetic activation extractor."""

import random


def synthetic_vector(size: int = 16) -> list[float]:
    return [random.uniform(-1.0, 1.0) for _ in range(size)]


def simulate_layers() -> dict[str, list[float]]:
    return {
        "embeddings": synthetic_vector(),
        "attention": synthetic_vector(),
        "mlp": synthetic_vector(),
        "hidden_state": synthetic_vector(),
    }
