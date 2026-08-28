# Catalog-driven region routing

Published: August 28, 2026

## Purpose

Regional pack discovery and automatic property matching must scale without adding region constants
or buttons to the Android app. Catalog version `2026.08.28.1` introduced signed `coverage`
metadata. Version `2026.08.28.2` uses that contract to publish the first data-only region outside
New Jersey without an APK release.

## Coverage fields

- `country` and `state` identify the administrative scope.
- `priority` resolves intentionally overlapping future coverage rules.
- `zipPrefixRanges` provides the preferred automatic match when a usable ZIP is available.
- `bounds` is a conservative coordinate fallback only when the property has no usable ZIP.

The coverage object is protected by the existing detached RSA/SHA-256 manifest signature. The app
must reject unsigned or modified routing metadata exactly as it rejects modified pack checksums.

## Current routing

| Pack | ZIP prefixes | Coordinate fallback |
|---|---|---|
| South Jersey | 080–084 | 38.90–40.149999° N, 75.15–74.00° W |
| North/Central Jersey | 070–079 and 085–089 | 40.15–41.40° N, 75.15–74.00° W |
| Philadelphia/Delaware Valley | 190–199 | 39.40–40.65° N, 76.20–75.150001° W |

The Delaware Valley coordinate fallback deliberately stops west of the South Jersey boundary.
Properties with a complete `19xxx` ZIP still match the new pack across Philadelphia, southeastern
Pennsylvania, and Delaware. The conservative fallback avoids guessing across the Delaware River
when a property has coordinates but no usable ZIP.

When a complete ZIP is present but does not match a signed ZIP range, coordinate fallback must not
silently override it. The property remains unsupported until the catalog contains an applicable
region. This preserves the existing fail-closed behavior near borders and outside reviewed areas.

## Compatibility

Older Garden Guide builds ignore unknown manifest fields and continue to use their existing New
Jersey resolver. Catalog-driven builds parse the signed coverage fields, cache the verified
manifest privately for offline use, and generate region controls from the pack list.
