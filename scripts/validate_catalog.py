#!/usr/bin/env python3
"""Validate regional packs, manifest integrity, and the detached manifest signature."""

import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_STATUSES = {"recommended", "conditional", "reference_only", "prohibited"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_review(review, label):
    status = review.get("status")
    require(status in ALLOWED_STATUSES, f"{label}: invalid status")
    require(review.get("plantId"), f"{label}: plantId is required")
    require(review.get("reviewedAt"), f"{label}: reviewedAt is required")
    require(review.get("sourceLabel"), f"{label}: sourceLabel is required")
    require(str(review.get("sourceUrl", "")).startswith("https://"),
            f"{label}: HTTPS sourceUrl is required")
    if status in {"recommended", "conditional"}:
        require(review.get("recommendationKeys"),
                f"{label}: eligible review needs recommendationKeys")
        require(review.get("plantingAction"),
                f"{label}: eligible review needs plantingAction")
        months = review.get("plantingMonths")
        require(isinstance(months, list) and months,
                f"{label}: eligible review needs plantingMonths")
        require(all(isinstance(month, int) and 1 <= month <= 12 for month in months),
                f"{label}: invalid planting month")
    if status in {"conditional", "reference_only", "prohibited"}:
        require(review.get("condition"), f"{label}: condition is required")


def validate_pack(path):
    root = json.loads(path.read_text(encoding="utf-8"))
    require(root.get("schemaVersion") == 1, f"{path}: schemaVersion must be 1")
    region = root.get("region")
    require(isinstance(region, dict), f"{path}: region is required")
    require(region.get("id") and region.get("name"), f"{path}: region identity is required")
    require(region.get("defaultStatus") == "unreviewed",
            f"{path}: defaultStatus must fail closed")
    reviews = root.get("reviews")
    require(isinstance(reviews, list), f"{path}: reviews must be a list")
    ids = []
    for index, review in enumerate(reviews):
        validate_review(review, f"{path}:{index + 1}")
        ids.append(review["plantId"])
    require(len(ids) == len(set(ids)), f"{path}: duplicate plant review")
    inheritance = root.get("inherits")
    if inheritance:
        inherited = inheritance.get("plantIds")
        require(inheritance.get("asset"), f"{path}: inherited asset is required")
        require(isinstance(inherited, list) and inherited,
                f"{path}: inherited plantIds are required")
        require(len(inherited) == len(set(inherited)),
                f"{path}: inherited plantIds must be unique")
    return root


def verify_signature():
    signature = base64.b64decode((ROOT / "manifest.sig").read_text().strip(), validate=True)
    with tempfile.NamedTemporaryFile() as signature_file:
        signature_file.write(signature)
        signature_file.flush()
        result = subprocess.run(
            ["openssl", "dgst", "-sha256", "-verify",
             str(ROOT / "catalog-signing-public-key.pem"),
             "-signature", signature_file.name, str(ROOT / "manifest.json")],
            check=False, capture_output=True, text=True,
        )
    require(result.returncode == 0 and "Verified OK" in result.stdout,
            "manifest.sig did not verify")


def main():
    manifest_path = ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("schemaVersion") == 1, "manifest schemaVersion must be 1")
    require(manifest.get("signatureAlgorithm") == "SHA256withRSA",
            "manifest signature algorithm is unsupported")
    packs = manifest.get("packs")
    require(isinstance(packs, list) and len(packs) == 2,
            "manifest must contain the two pilot packs")
    pack_ids = set()
    loaded = {}
    for entry in packs:
        pack_id = entry.get("id")
        require(pack_id not in pack_ids, f"duplicate manifest pack {pack_id}")
        pack_ids.add(pack_id)
        require(str(entry.get("url", "")).startswith("https://"),
                f"{pack_id}: HTTPS pack URL is required")
        require(entry.get("minAppVersionCode") == 45,
                f"{pack_id}: minAppVersionCode must be 45")
        path = ROOT / "packs" / entry["assetName"]
        content = path.read_bytes()
        require(len(content) == entry.get("sizeBytes"), f"{pack_id}: byte count mismatch")
        require(hashlib.sha256(content).hexdigest() == entry.get("sha256"),
                f"{pack_id}: SHA-256 mismatch")
        loaded[pack_id] = validate_pack(path)

    south = loaded["us-nj-south"]
    north = loaded["us-nj-north-central"]
    south_counts = {}
    for review in south["reviews"]:
        south_counts[review["status"]] = south_counts.get(review["status"], 0) + 1
    require(south_counts == {"recommended": 92, "conditional": 5, "reference_only": 19},
            f"unexpected South Jersey counts: {south_counts}")
    require(north.get("reviews") == [], "North/Central pack must not copy inherited reviews")
    inherited = north["inherits"]["plantIds"]
    require(len(inherited) == 25, "North/Central pack must inherit 25 identities")
    south_by_id = {review["plantId"]: review for review in south["reviews"]}
    keys = []
    for plant_id in inherited:
        require(plant_id in south_by_id, f"missing inherited South review: {plant_id}")
        keys.extend(south_by_id[plant_id].get("recommendationKeys", []))
    require(len(keys) == 26 and len(keys) == len(set(keys)),
            "North/Central inheritance must cover 26 unique recommendation records")
    verify_signature()
    print("Catalog validation passed: 2 signed packs; South 98 records; North/Central 26 records")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"Catalog validation failed: {error}")
