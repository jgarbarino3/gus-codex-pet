# Gus Codex Pet

Gus is a photo-grounded Codex pet based on a fox-red Labrador retriever: floppy ears, kind eyes, compact runt-of-the-litter build, no harness, and sweet cuddly energy.

This repo ships only the finished Codex pet assets. The private reference photos used to make Gus are intentionally not included. The final sprite has no harness or collar.

The shipped pet is intentionally clean and static. Codex did not reliably play the idle animation loop, and fake tail motion looked wrong in the real overlay, so the GitHub version avoids those artifacts.

## Included Pet

- `Gus`: default standing Gus.

Additional real poses, like Gus sitting upright on his butt, should be added from a fresh generated or redrawn source image instead of stretching this standing sprite.

## Install

```bash
git clone https://github.com/jgarbarino3/gus-codex-pet.git
cd gus-codex-pet
./install.sh
```

Then open Codex and refresh/select the custom pet:

1. Open **Settings > Appearance > Pets**.
2. Refresh custom pets from your local Codex home.
3. Select Gus.
4. Use `/pet` or **Wake Pet** to show him. If a pet was already open, tuck it away and wake it again after refreshing.

## Files

```text
pets/gus/pet.json
pets/gus/spritesheet.webp
```

Codex loads custom pets from:

```text
~/.codex/pets/
```

## Preview And QA

- `artifacts/gus_photoreal_base.png` shows the base Gus sprite.
- `qa/contact-sheet.png` shows the full 9-row Codex atlas.
- `qa/validation.json` records atlas dimensions and transparent unused-cell validation.

Gus follows the Codex sprite contract: `1536x1872` atlas, 8 columns, 9 rows, `192x208` cells.
