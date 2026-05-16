"""Activation compression helpers."""

import base64
import zlib


def compress_text(raw: str) -> str:
    return base64.b64encode(zlib.compress(raw.encode("utf-8"))).decode("utf-8")


def decompress_text(blob: str) -> str:
    return zlib.decompress(base64.b64decode(blob.encode("utf-8"))).decode("utf-8")
