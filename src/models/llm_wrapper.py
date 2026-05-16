"""Wrapper contract around model inference."""

from src.models.fake_model import FakeModel


class LLMWrapper:
    def __init__(self) -> None:
        self.model = FakeModel()

    def run(self, prompt: str) -> str:
        return self.model.infer(prompt)
