#!/usr/bin/env python3
from __future__ import annotations
import os, sys, runpy
from pathlib import Path

# Ensure the model_vulnerability_analysis 'src' package is importable as 'src'
THIS_DIR = os.path.dirname(__file__)
MVA_SRC_PARENT = os.path.abspath(os.path.join(THIS_DIR, '..', 'model_vulnerability_analysis'))
if MVA_SRC_PARENT not in sys.path:
    sys.path.insert(0, MVA_SRC_PARENT)

if __name__ == '__main__':
    # If the downstream CLI expects a scoring rubric but the caller didn't provide
    # --scoring_rubric, try to infer it from the directory of --config supplied
    # by the integration test (tmp/config/scoring_rubric.yaml).
    argv = sys.argv[1:]
    if '--scoring_rubric' not in argv and '--config' in argv:
        try:
            cfg_idx = argv.index('--config')
            if cfg_idx + 1 < len(argv):
                cfg_path = Path(argv[cfg_idx + 1])
                candidate = cfg_path.parent / 'scoring_rubric.yaml'
                if candidate.exists():
                    sys.argv.extend(['--scoring_rubric', str(candidate)])
        except Exception:
            # Best-effort; fall through if anything is off
            pass
    # Delegate to model_vulnerability_analysis/src/main.py as module 'src.main'
    runpy.run_module('src.main', run_name='__main__')
