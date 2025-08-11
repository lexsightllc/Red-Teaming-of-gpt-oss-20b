#!/usr/bin/env python3
from __future__ import annotations
import os, sys, runpy

# Ensure the model_vulnerability_analysis 'src' package is importable as 'src'
THIS_DIR = os.path.dirname(__file__)
MVA_SRC_PARENT = os.path.abspath(os.path.join(THIS_DIR, '..', 'model_vulnerability_analysis'))
if MVA_SRC_PARENT not in sys.path:
    sys.path.insert(0, MVA_SRC_PARENT)

if __name__ == '__main__':
    # Delegate to model_vulnerability_analysis/src/main.py as module 'src.main'
    runpy.run_module('src.main', run_name='__main__')
