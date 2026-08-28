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
BATCH_02_IDS = {
    "big_bluestem",
    "blueberry",
    "clustered_mountain_mint",
    "coral_honeysuckle",
    "golden_alexanders",
    "golden_ragwort",
    "inkberry_holly",
    "new_england_aster",
    "new_york_ironweed",
    "northern_bayberry",
    "northern_spicebush",
    "pennsylvania_sedge",
    "rudbeckia",
    "serviceberry",
    "spotted_joe_pye_weed",
    "summersweet",
    "swamp_milkweed",
    "swamp_white_oak",
    "sweet_fern",
    "white_wood_aster",
    "wild_bergamot",
    "winterberry_holly",
}
BATCH_03_IDS = {"celery", "parsnip"}


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
    require(manifest.get("catalogVersion") == "2026.08.28.1",
            "catalogVersion must identify catalog-driven regional routing")
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
        expected_coverage = {
            "us-nj-south": {
                "country": "US",
                "state": "NJ",
                "priority": 100,
                "zipPrefixRanges": [{"start": 80, "end": 84}],
                "bounds": {
                    "minLatitude": 38.90,
                    "maxLatitude": 40.149999,
                    "minLongitude": -75.15,
                    "maxLongitude": -74.00,
                },
            },
            "us-nj-north-central": {
                "country": "US",
                "state": "NJ",
                "priority": 100,
                "zipPrefixRanges": [
                    {"start": 70, "end": 79},
                    {"start": 85, "end": 89},
                ],
                "bounds": {
                    "minLatitude": 40.15,
                    "maxLatitude": 41.40,
                    "minLongitude": -75.15,
                    "maxLongitude": -74.00,
                },
            },
        }
        require(entry.get("coverage") == expected_coverage.get(pack_id),
                f"{pack_id}: signed coverage routing metadata is incorrect")
        expected_version = 3 if pack_id == "us-nj-north-central" else 2
        require(entry.get("version") == expected_version,
                f"{pack_id}: expected pack version {expected_version}")
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
    south_by_id = {review["plantId"]: review for review in south["reviews"]}
    south_celery = south_by_id["celery"]
    south_parsnip = south_by_id["parsnip"]
    require(south_celery["sourceUrl"] == "https://njaes.rutgers.edu/fs129/" and
            south_celery["plantingMonths"] == [5, 6],
            "South Jersey celery must use Rutgers FS129 home-garden evidence")
    require(south_parsnip["sourceUrl"] == "https://njaes.rutgers.edu/fs129/" and
            south_parsnip["plantingMonths"] == [4],
            "South Jersey parsnip must use Rutgers FS129 home-garden evidence")
    north_reviews = north.get("reviews")
    require({review["plantId"] for review in north_reviews} == BATCH_03_IDS,
            "North/Central direct reviews must be the batch 03 overrides")
    inherited = north["inherits"]["plantIds"]
    require(len(inherited) == 47, "North/Central pack must inherit 47 identities")
    require(inherited == sorted(inherited),
            "North/Central inherited identities must be sorted")
    require(BATCH_02_IDS.issubset(inherited),
            "North/Central pack is missing a batch 02 identity")
    keys = []
    for plant_id in inherited:
        require(plant_id in south_by_id, f"missing inherited South review: {plant_id}")
        review = south_by_id[plant_id]
        require(review["status"] == "recommended",
                f"North/Central inherited review is not recommended: {plant_id}")
        require("njaes.rutgers.edu" in review["sourceUrl"],
                f"North/Central inherited review is not Rutgers-backed: {plant_id}")
        if plant_id in BATCH_02_IDS:
            require(review["sourceUrl"] == "https://njaes.rutgers.edu/fs1140/",
                    f"batch 02 identity is not backed by Rutgers FS1140: {plant_id}")
        keys.extend(review.get("recommendationKeys", []))
    for review in north_reviews:
        require(review["status"] == "recommended",
                f"batch 03 review is not recommended: {review['plantId']}")
        require(review["sourceUrl"] == "https://njaes.rutgers.edu/fs129/",
                f"batch 03 review is not backed by Rutgers FS129: {review['plantId']}")
        keys.extend(review.get("recommendationKeys", []))
    require(len(inherited) + len(north_reviews) == 49,
            "North/Central pack must cover 49 identities")
    require(len(keys) == 50 and len(keys) == len(set(keys)),
            "North/Central pack must cover 50 unique recommendation records")
    celery = next(review for review in north_reviews if review["plantId"] == "celery")
    parsnip = next(review for review in north_reviews if review["plantId"] == "parsnip")
    require(celery["plantingAction"] == "Use transplants" and
            celery["plantingMonths"] == [5, 6],
            "celery must use the Rutgers FS129 home-garden window")
    require(parsnip["plantingAction"] == "Direct sow fresh seed" and
            parsnip["plantingMonths"] == [4],
            "parsnip must use the Rutgers FS129 home-garden window")
    verify_signature()
    print("Catalog validation passed: 2 signed packs with coverage routing; "
          "South 98 records; North/Central 50 records")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"Catalog validation failed: {error}")
