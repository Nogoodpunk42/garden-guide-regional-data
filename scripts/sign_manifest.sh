#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

: "${CATALOG_SIGNING_PRIVATE_KEY:?Set CATALOG_SIGNING_PRIVATE_KEY}"
: "${CATALOG_SIGNING_PASSWORD_FILE:?Set CATALOG_SIGNING_PASSWORD_FILE}"

openssl dgst -sha256 \
  -sign "$CATALOG_SIGNING_PRIVATE_KEY" \
  -passin "file:$CATALOG_SIGNING_PASSWORD_FILE" \
  "$ROOT/manifest.json" \
  | openssl base64 -A > "$ROOT/manifest.sig"
printf '\n' >> "$ROOT/manifest.sig"

echo "Signed manifest.json as manifest.sig"
