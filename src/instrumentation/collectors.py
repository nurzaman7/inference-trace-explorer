"""Telemetry collector interfaces."""

from typing import Any


class Collector:
    def collect(self, record: dict[str, Any]) -> None:
        raise NotImplementedError
