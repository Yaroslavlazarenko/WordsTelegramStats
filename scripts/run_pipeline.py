#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to execute the complete end-to-end NLP analytics and infographics pipeline.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline.runner import run_full_pipeline


def run_all(callback=None):
    run_full_pipeline(log_callback=callback)


if __name__ == "__main__":
    run_full_pipeline()
