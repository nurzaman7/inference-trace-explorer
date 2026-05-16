"""Activation serialization utilities."""

import json


def serialize_activation(payload: dict) -> str:
    return json.dumps(payload)
