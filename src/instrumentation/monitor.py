"""Runtime resource monitoring."""

import os
import psutil


def memory_mb() -> float:
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024
