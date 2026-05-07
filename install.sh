#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${CODEX_HOME:-$HOME/.codex}/pets/gus"

mkdir -p "$DEST"
cp "$ROOT/pets/gus/pet.json" "$DEST/pet.json"
cp "$ROOT/pets/gus/spritesheet.webp" "$DEST/spritesheet.webp"

echo "Installed Gus to $DEST"
echo "In Codex, open Settings > Appearance > Pets, refresh custom pets, then select Gus."
