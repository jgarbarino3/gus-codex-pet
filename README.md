# Gus Codex Pet

Gus is a photo-grounded Codex pet based on a fox-red Labrador retriever: floppy ears, kind eyes, compact runt-of-the-litter build, no harness, and sweet cuddly energy.

This repo ships only the finished Codex pet assets. The private reference photos used to make Gus are intentionally not included. The final sprite has no harness or collar.

## Animations

Gus uses the full Codex pet atlas with the always-on personality concentrated in `idle`, because Codex loops that row during normal pet display:

- `idle`: visible cute-alive loop with breathing/body bob, blink, shadow shift, and tail wag.
- `running-right` / `running-left`: bouncy trot with grounded shadows.
- `waving`: small front-paw lift.
- `jumping`: squash, hop, air frame, and landing.
- `failed`: droopy sad expression with a small tear.
- `waiting`: patient head tilt and blink.
- `running`: compact in-place trot.
- `review`: focused attentive look.

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
4. Use `/pet` or **Wake Pet** to show him. If he was already open, tuck him away and wake him again after refreshing.

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
