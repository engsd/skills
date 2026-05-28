#!/usr/bin/env python3
"""
Compatibility wrapper for asynchronous batch image generation.

Use async_batch_generate.py directly for new workflows. This wrapper exists so
older references to batch_generate.py still use the async path instead of the
former per-image synchronous loop.
"""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("async_batch_generate.py")), run_name="__main__")
