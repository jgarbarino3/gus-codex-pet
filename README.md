# Gus Codex Pet Pack

Gus is a photo-grounded Codex pet based on a fox-red Labrador retriever: floppy ears, kind eyes, compact runt-of-the-litter build, no harness, and sweet cuddly energy.

This repo ships only the finished Codex pet assets. The private reference photos used to make Gus are intentionally not included.

The shipped pet is intentionally clean and static. Codex did not reliably play the idle animation loop, and fake tail motion looked wrong in the real overlay, so the GitHub version avoids those artifacts.

## Included Pets

- `Gus`: default standing Gus.
- `Gus Sitting`: Gus sitting upright on his butt.
- `Gus Laying`: Gus laying on his stomach with his front paws out and head up.
- `Gus Life Jacket`: Gus standing in a clean orange, red, and gray life jacket.
- `Gus Life Jacket Classic`: Gus standing in the alternate life jacket style.
- `Gus Real Action`: action-focused Gus with clearer running, waving, barking, waiting, flop, and review rows.

Each pose is its own selectable Codex pet. The sitting and laying pets use fresh pose sources instead of stretched or squashed copies of the standing sprite.

## Install

```bash
git clone https://github.com/jgarbarino3/gus-codex-pet.git
cd gus-codex-pet
./install.sh
```

Then open Codex and refresh/select the custom pet you want:

1. Open **Settings > Appearance > Pets**.
2. Refresh custom pets from your local Codex home.
3. Select the Gus version you want.
4. Use `/pet` or **Wake Pet** to show him. If a pet was already open, tuck it away and wake it again after refreshing.

## Files

```text
pets/gus/pet.json
pets/gus/spritesheet.webp
pets/gus-sitting/pet.json
pets/gus-sitting/spritesheet.webp
pets/gus-laying/pet.json
pets/gus-laying/spritesheet.webp
pets/gus-life-jacket/pet.json
pets/gus-life-jacket/spritesheet.webp
pets/gus-life-jacket-classic/pet.json
pets/gus-life-jacket-classic/spritesheet.webp
pets/gus-real-action/pet.json
pets/gus-real-action/spritesheet.webp
```

Codex loads custom pets from:

```text
~/.codex/pets/
```

## Preview And QA

- `artifacts/gus_photoreal_base.png` shows the base Gus sprite.
- `qa/contact-sheet.png` shows the full 9-row Codex atlas.
- `qa/contact-sheets/*.png` shows the full 9-row Codex atlas for each pet.
- `qa/previews/gus-real-action/*.gif` shows the individual action rows for the action-focused pet.
- `qa/gus-real-action-idle-running-check.png` shows the corrected idle and running row sources.
- `qa/pose-overview.png` shows all included Gus pets side by side.
- `qa/validation.json` records atlas dimensions and transparent unused-cell validation for every pet.

Each Gus pet follows the Codex sprite contract: `1536x1872` atlas, 8 columns, 9 rows, `192x208` cells.
