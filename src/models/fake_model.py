"""Synthetic model for inference simulation."""

import random


class FakeModel:
    def infer(self, prompt: str) -> str:
        choices = ["ok", "needs watering", "anomaly detected", "stable"]
        return f"response:{random.choice(choices)} for '{prompt[:20]}'"
