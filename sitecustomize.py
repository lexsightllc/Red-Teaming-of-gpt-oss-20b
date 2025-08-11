# Auto-adjust PATH for test subprocesses that invoke 'python'
# This file is auto-imported by Python if present on sys.path.
import os
from pathlib import Path

try:
    repo_root = Path(__file__).resolve().parent
    shim = repo_root / "python"
    if shim.exists() and os.access(shim, os.X_OK):
        current = os.environ.get("PATH", "")
        parts = current.split(":") if current else []
        if str(repo_root) not in parts:
            os.environ["PATH"] = f"{repo_root}:{current}" if current else str(repo_root)
except Exception:
    # Never break interpreter startup
    pass
