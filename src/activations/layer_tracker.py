"""Track synthetic layer activations by layer name."""

from collections import defaultdict


class LayerTracker:
    def __init__(self) -> None:
        self._store: dict[str, list[list[float]]] = defaultdict(list)

    def add(self, layer_name: str, vector: list[float]) -> None:
        self._store[layer_name].append(vector)

    def as_dict(self) -> dict[str, list[list[float]]]:
        return dict(self._store)
