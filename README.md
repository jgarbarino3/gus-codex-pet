# Gus Codex Pet

Gus is a photo-grounded Codex pet based on a fox-red Labrador retriever: floppy ears, kind eyes, compact runt-of-the-litter build, and sweet cuddly energy.

This repo ships only the finished Codex pet assets. The private reference photos used to make Gus are intentionally not included.

## Install

```bash
git clone https://github.com/jgarbarino3/gus-codex-pet.git
cd gus-codex-pet
./install.sh
```

Then open Codex and refresh/select the custom pet:

1. Open **Settings > Appearance > Pets**.
2. Refresh custom pets from your local Codex home.
3. Select **Gus**.
4. Use `/pet` or **Wake Pet** to show him.

## Files

```text
pets/gus/pet.json
pets/gus/spritesheet.webp
```

Codex loads custom pets from:

```text
~/.codex/pets/gus/
```

## Preview And QA

- `artifacts/gus_photoreal_base.png` shows the base Gus sprite.
- `qa/contact-sheet.png` shows the full 9-row Codex animation atlas.
- `qa/previews/*.gif` contains one animated preview per Codex state.
- `qa/validation.json` records atlas dimensions and transparent unused-cell validation.

The pet follows the Codex sprite contract: `1536x1872` atlas, 8 columns, 9 rows, `192x208` cells.
