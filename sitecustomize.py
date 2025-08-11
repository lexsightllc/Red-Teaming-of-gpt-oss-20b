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

# Compatibility: some tests expect requests_mock.exceptions.ConnectionError,
# but requests-mock exposes exceptions via requests.exceptions.
try:
    import requests as _req
    import requests_mock as _req_mock
    if not hasattr(_req_mock, "exceptions"):
        setattr(_req_mock, "exceptions", _req.exceptions)
    # Ensure the fixture object (Mocker instance) also exposes `.exceptions`
    try:
        from requests_mock.mocker import Mocker as _RM_Mocker
        if not hasattr(_RM_Mocker, "exceptions"):
            setattr(_RM_Mocker, "exceptions", _req.exceptions)
    except Exception:
        pass
except Exception:
    # Best-effort only
    pass
