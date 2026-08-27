# Garden Guide regional data

Public, versioned regional evidence packs for the Garden Guide Android app.

This repository contains plant-region decisions, planting windows, evidence links, and review dates.
It does **not** contain Garden Guide application source, signing secrets, user locations, saved yards,
or other user data.

## Published files

- `manifest.json` lists every available pack, version, size, checksum, and minimum app version.
- `manifest.sig` is an RSA/SHA-256 signature over the exact `manifest.json` bytes.
- `catalog-signing-public-key.pem` lets the app and CI verify that signature.
- `packs/` contains human-readable regional JSON packages.

Garden Guide downloads the manifest and requested pack over HTTPS, verifies the manifest signature,
checks the pack SHA-256 and byte count, and installs the pack atomically. Recommendations continue to
work from the validated local copy when the phone is offline.

## Current catalog

| Region | Pack type | Eligible identities | Recommendation records |
|---|---|---:|---:|
| South Jersey | Full starter pack | 97 | 98 |
| North/Central Jersey pilot | Inheritance plus regional overrides | 49 | 50 |

The North/Central pack reuses statewide Rutgers-reviewed decisions by stable plant ID. Version 2
adds 22 plants from Rutgers NJAES FS1140 that are identified as native to all or most New Jersey
ecosystems. Version 3 adds Rutgers FS129 home-garden records for celery and parsnip as direct
regional overrides. It does not copy the universal plant library or duplicate inherited review rows.

## Editing a pack

1. Edit the regional JSON in `packs/`.
2. Keep every evidence decision attached to a stable universal `plantId`.
3. Update its review date, source, status, planting window, and condition as appropriate.
4. Run `python3 scripts/build_manifest.py`.
5. Sign the generated manifest with the separate private catalog key.
6. Run `python3 scripts/validate_catalog.py`.
7. Submit the pack, manifest, and signature together in one pull request.

The private catalog key is intentionally not stored in this repository and is unrelated to the APK
signing key.

## Runtime endpoint

The pilot reads the public bootstrap manifest from:

`https://raw.githubusercontent.com/Nogoodpunk42/garden-guide-regional-data/main/manifest.json`

Pack URLs live inside the signed manifest, so the files can move to a dedicated CDN later without
changing the package format.
