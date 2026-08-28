#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to run text and corpus analysis, generating frequency files and advanced_report.txt.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline.runner import run_text_analysis


def main():
    run_text_analysis()


if __name__ == "__main__":
    main()
