# North/Central Jersey verification batch 02

Reviewed: August 27, 2026

## Outcome

North/Central Jersey pack version 2 adds 22 eligible plant identities, bringing the pack to 47
identities and 48 unique recommendation records. The pack continues to inherit reviewed rows by
stable plant ID instead of duplicating the universal plant library or the South Jersey evidence
records.

## Evidence boundary

The added identities all appear in Table 1 of Rutgers NJAES Fact Sheet FS1140, *Incorporating
Native Plants in Your Residential Landscape*:

- https://njaes.rutgers.edu/fs1140/

Rutgers describes that table as a starting list of easy-to-grow, resilient species native to all or
most of New Jersey's ecosystems. This supports regional eligibility across North and Central Jersey.
It does not mean that every listed plant suits every property: the table separately specifies soil,
moisture, pH, sunlight, mature size, growth rate, and deer-resistance requirements. Garden Guide's
property matching remains responsible for those site-level constraints.

## Added identities

- Big bluestem (`big_bluestem`)
- Highbush blueberry (`blueberry`)
- Clustered mountain mint (`clustered_mountain_mint`)
- Coral honeysuckle (`coral_honeysuckle`)
- Golden Alexanders (`golden_alexanders`)
- Golden ragwort (`golden_ragwort`)
- Inkberry holly (`inkberry_holly`)
- New England aster (`new_england_aster`)
- New York ironweed (`new_york_ironweed`)
- Northern bayberry (`northern_bayberry`)
- Northern spicebush (`northern_spicebush`)
- Pennsylvania sedge (`pennsylvania_sedge`)
- Orange coneflower (`rudbeckia`)
- Serviceberry (`serviceberry`)
- Spotted joe-pye-weed (`spotted_joe_pye_weed`)
- Summersweet / sweet pepperbush (`summersweet`)
- Swamp milkweed (`swamp_milkweed`)
- Swamp white oak (`swamp_white_oak`)
- Sweet fern (`sweet_fern`)
- White wood aster (`white_wood_aster`)
- Wild bergamot (`wild_bergamot`)
- Winterberry holly (`winterberry_holly`)

## Deliberate exclusions

Celery and parsnip were considered because existing South Jersey records cite Rutgers' 2026/2027
Mid-Atlantic Commercial Vegetable Production Recommendations. Those publications explicitly say
they are not for home-gardener use, so they were not promoted into North/Central batch 02. They can
be reconsidered when a suitable home-garden source establishes the regional recommendation.

## Release gates

- Every inherited identity must resolve to one existing South Jersey review.
- Every inherited review must have `recommended` status and a Rutgers NJAES HTTPS source.
- Every batch 02 identity must cite Rutgers NJAES FS1140.
- The 47 identities must resolve to 48 unique recommendation keys.
- The generated manifest must match pack byte counts and SHA-256 checksums.
- The detached RSA/SHA-256 signature over the exact manifest bytes must verify in CI.
