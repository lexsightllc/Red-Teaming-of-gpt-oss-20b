#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys, hashlib, time, subprocess, pathlib
from typing import Dict, Any, List


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_info() -> Dict[str, Any]:
    def run(cmd: List[str]) -> str:
        try:
            return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        except Exception:
            return ""
    return {
        "commit": run(["git", "rev-parse", "HEAD"])[:40],
        "commit_short": run(["git", "rev-parse", "--short", "HEAD"]),
        "branch": run(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "dirty": bool(run(["git", "status", "--porcelain"]))
    }


def collect_files(root: str) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for base, _, files in os.walk(root):
        for fn in files:
            p = os.path.join(base, fn)
            try:
                st = os.stat(p)
                entries.append({
                    "path": os.path.relpath(p, start=root),
                    "abs_path": os.path.abspath(p),
                    "size_bytes": st.st_size,
                    "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
                    "sha256": sha256_file(p)
                })
            except Exception as e:
                entries.append({
                    "path": os.path.relpath(p, start=root),
                    "abs_path": os.path.abspath(p),
                    "error": str(e)
                })
    # deterministic ordering
    entries.sort(key=lambda x: x.get("path", ""))
    return entries


def main():
    if len(sys.argv) < 2:
        print("usage: make_manifest.py <manifest_output_path>", file=sys.stderr)
        sys.exit(2)

    out_path = pathlib.Path(sys.argv[1])
    run_root = out_path.parent  # expected: reports/<RUN_ID>

    # Try to infer RUN_ID from directory name
    run_id = run_root.name

    logs_dir = pathlib.Path("logs") / run_id
    reports_dir = pathlib.Path("reports") / run_id

    payload: Dict[str, Any] = {
        "schema": "artifact-manifest/v1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_id": run_id,
        "git": git_info(),
        "inputs": {
            "logs_dir": str(logs_dir),
            "reports_dir": str(reports_dir),
        },
        "artifacts": {
            "logs": collect_files(str(logs_dir)) if logs_dir.exists() else [],
            "reports": collect_files(str(reports_dir)) if reports_dir.exists() else [],
        }
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)

    print(str(out_path))


if __name__ == "__main__":
    main()
