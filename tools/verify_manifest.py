#!/usr/bin/env python3
"""Verify every exported evidence file against the publication manifest."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent.parent
manifest = json.loads((root / 'manifest.json').read_text())
failures = []
for entry in manifest['files']:
    path = root / entry['path']
    if not path.is_file():
        failures.append(f"missing: {entry['path']}")
    elif hashlib.sha256(path.read_bytes()).hexdigest() != entry['export_sha256']:
        failures.append(f"hash mismatch: {entry['path']}")
if failures:
    raise SystemExit('\n'.join(failures))
print(f"Verified {len(manifest['files'])} archived files")
