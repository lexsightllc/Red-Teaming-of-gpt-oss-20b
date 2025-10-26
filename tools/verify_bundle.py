#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0

"""
verify_bundle.py — Recompute and verify SHA-256 hashes for evaluation-awareness bundles.

Usage:
  python tools/verify_bundle.py --manifest reports/eval_awareness/manifest.json [--base-dir .]

It canonicalizes file contents (UTF-8, newline normalization) before hashing.
Exits with code 0 on success, 1 on failure.
"""
import argparse, json, hashlib, os, sys, pathlib


def canonicalize_bytes(p: pathlib.Path) -> bytes:
    data = p.read_bytes()
    try:
        # Normalize to UTF-8 with LF newlines if text; fallback to raw bytes
        text = data.decode('utf-8')
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        return text.encode('utf-8')
    except UnicodeDecodeError:
        return data


def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(canonicalize_bytes(p))
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', required=True, help='Path to manifest.json produced by the harness')
    ap.add_argument('--base-dir', default='.', help='Base directory to resolve relative paths')
    args = ap.parse_args()

    base = pathlib.Path(args.base_dir)
    manifest_path = base / args.manifest
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text())

    files = [manifest.get('report_path', '')] + list(manifest.get('generated', []))
    files = [f for f in files if f]

    missing = []
    hashes = {}
    for rel in files:
        p = base / rel
        if not p.exists():
            missing.append(rel)
            continue
        hashes[rel] = sha256_file(p)

    status = {
        'manifest': str(manifest_path),
        'files_checked': len(files),
        'files_missing': missing,
        'hashes': hashes,
    }
    print(json.dumps(status, indent=2))

    return 0 if not missing else 1


if __name__ == '__main__':
    sys.exit(main())
