"""Hook interfaces for model lifecycle instrumentation."""

from typing import Protocol, Any


class InferenceHook(Protocol):
    def before_infer(self, payload: dict[str, Any]) -> None: ...
    def after_infer(self, payload: dict[str, Any], output: dict[str, Any]) -> None: ...
