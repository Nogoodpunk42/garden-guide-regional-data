#!/usr/bin/env python3
"""Build a deterministic public catalog manifest from the reviewed pack files."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = (
    "https://raw.githubusercontent.com/Nogoodpunk42/"
    "garden-guide-regional-data/main/packs"
)
CATALOG_VERSION = "2026.08.27.3"
PACKS = (
    {
        "id": "us-nj-south",
        "name": "South Jersey",
        "assetName": "regional_reviews_south_jersey_2026.json",
        "version": 2,
        "builtIn": True,
    },
    {
        "id": "us-nj-north-central",
        "name": "North/Central Jersey pilot",
        "assetName": "regional_reviews_north_central_jersey_2026.json",
        "version": 3,
        "builtIn": False,
    },
)


def main():
    published = []
    for pack in PACKS:
        path = ROOT / "packs" / pack["assetName"]
        content = path.read_bytes()
        item = dict(pack)
        item.update({
            "url": f"{BASE_URL}/{pack['assetName']}",
            "sha256": hashlib.sha256(content).hexdigest(),
            "sizeBytes": len(content),
            "minAppVersionCode": 45,
        })
        published.append(item)

    manifest = {
        "schemaVersion": 1,
        "catalogVersion": CATALOG_VERSION,
        "generatedAt": "2026-08-27T22:29:00Z",
        "signatureAlgorithm": "SHA256withRSA",
        "packs": published,
    }
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    (ROOT / "manifest.json").write_text(text, encoding="utf-8")
    print(f"Wrote manifest.json with {len(published)} regional packs")


if __name__ == "__main__":
    main()
