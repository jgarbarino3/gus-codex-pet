#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_ROOT="${CODEX_HOME:-$HOME/.codex}/pets"

mkdir -p "$DEST_ROOT"

for pet_dir in "$ROOT"/pets/*; do
  [ -d "$pet_dir" ] || continue
  pet_name="$(basename "$pet_dir")"
  dest="$DEST_ROOT/$pet_name"
  mkdir -p "$dest"
  cp "$pet_dir/pet.json" "$dest/pet.json"
  cp "$pet_dir/spritesheet.webp" "$dest/spritesheet.webp"
  echo "Installed $pet_name to $dest"
done

echo "In Codex, open Settings > Appearance > Pets, refresh custom pets, then select the Gus version you want."
