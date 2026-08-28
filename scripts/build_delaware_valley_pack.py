#!/usr/bin/env python3
"""Build the reviewed Philadelphia/Delaware Valley pilot datapack."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOUTH_PACK = ROOT / "packs" / "regional_reviews_south_jersey_2026.json"
OUTPUT = ROOT / "packs" / "regional_reviews_delaware_valley_2026.json"

UD_PLANNING_URL = (
    "https://www.udel.edu/academics/colleges/canr/cooperative-extension/"
    "fact-sheets/planning-a-vegetable-garden/"
)
UD_GROW_URL = (
    "https://www.udel.edu/academics/colleges/canr/cooperative-extension/"
    "environmental-stewardship/lawn-and-garden/grow-your-own/"
)
PHILADELPHIA_PLANTS_URL = (
    "https://water.phila.gov/wp-content/uploads/files/"
    "table-i-1-non-invasive-plants-1.pdf"
)

VEGETABLE_MONTHS = {
    "arugula": [4, 5],
    "beet": [4, 6, 7, 8],
    "broccoli": [3, 4, 7, 8],
    "brussels_sprouts": [7, 8],
    "bush_bean": [5, 7, 8],
    "cabbage": [3, 4, 7, 8],
    "carrot": [4, 5, 7, 8],
    "cauliflower": [4, 7, 8],
    "chili": [5],
    "collard_greens": [4, 5],
    "corn": [5, 6, 7],
    "cucumber": [5],
    "eggplant": [5],
    "kale": [3, 4, 7, 8, 9],
    "kohlrabi": [3, 4, 8],
    "lettuce": [4, 7, 8, 9],
    "melon": [5],
    "onion": [3, 4],
    "pea": [3, 4, 7, 8],
    "radish": [3, 4, 8, 9],
    "spinach": [3, 4, 8, 9],
    "swiss_chard": [4, 5],
    "tomato": [5],
    "watermelon": [5],
    "winter_squash": [5],
    "zucchini": [5],
}

COMMUNITY_GARDEN_IDS = {"arugula", "collard_greens"}

NATIVE_IDS = {
    "big_bluestem",
    "butterfly_weed",
    "buttonbush",
    "coral_honeysuckle",
    "golden_alexanders",
    "new_york_ironweed",
    "northern_bayberry",
    "northern_spicebush",
    "pawpaw",
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


def main():
    south = json.loads(SOUTH_PACK.read_text(encoding="utf-8"))
    source = {review["plantId"]: review for review in south["reviews"]}
    requested = set(VEGETABLE_MONTHS) | NATIVE_IDS
    missing = requested - set(source)
    if missing:
        raise ValueError(f"South Jersey source pack is missing: {sorted(missing)}")

    reviews = []
    for plant_id in sorted(requested):
        review = {
            key: value
            for key, value in source[plant_id].items()
            if key in {"plantId", "status", "recommendationKeys", "plantingAction"}
        }
        if review.get("status") != "recommended":
            raise ValueError(f"Expected a recommended source record for {plant_id}")
        review["reviewedAt"] = "August 2026"

        if plant_id in NATIVE_IDS:
            review.update({
                "sourceLabel": (
                    "Philadelphia Water Department · Native and Recommended "
                    "Non-Invasive Plants"
                ),
                "sourceUrl": PHILADELPHIA_PLANTS_URL,
                "plantingMonths": [3, 4, 5, 9, 10, 11],
            })
        else:
            community = plant_id in COMMUNITY_GARDEN_IDS
            review.update({
                "sourceLabel": (
                    "University of Delaware Cooperative Extension · Grow Your Own Food"
                    if community else
                    "University of Delaware Cooperative Extension · Planning a Vegetable Garden"
                ),
                "sourceUrl": UD_GROW_URL if community else UD_PLANNING_URL,
                "plantingMonths": VEGETABLE_MONTHS[plant_id],
            })
        reviews.append(review)

    pack = {
        "schemaVersion": 1,
        "region": {
            "id": "us-delaware-valley",
            "name": "Philadelphia/Delaware Valley pilot",
            "country": "US",
            "state": "PA/DE",
            "reviewedAt": "August 2026",
            "defaultStatus": "unreviewed",
            "scopeNote": (
                "Initial data-only pilot limited to 26 University of Delaware-reviewed "
                "vegetables and 19 Philadelphia-listed native landscape plants."
            ),
        },
        "reviews": reviews,
    }
    OUTPUT.write_text(
        json.dumps(pack, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    keys = [key for review in reviews for key in review["recommendationKeys"]]
    print(
        f"Wrote {OUTPUT.name}: {len(reviews)} identities, "
        f"{len(keys)} recommendation records"
    )


if __name__ == "__main__":
    main()
