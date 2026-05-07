from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts" / "gus_photoreal_candidates.png"
ARTIFACTS = ROOT / "artifacts"
QA = ROOT / "qa"
PET_DIR = ROOT / "pets" / "gus"

CELL_W = 192
CELL_H = 208
COLS = 8
ROWS = 9

ROW_COUNTS = {
    "idle": 6,
    "running-right": 8,
    "running-left": 8,
    "waving": 4,
    "jumping": 5,
    "failed": 8,
    "waiting": 6,
    "running": 6,
    "review": 6,
}
ROW_ORDER = list(ROW_COUNTS)


def find_subject_bbox(mask: Image.Image) -> tuple[int, int, int, int]:
    w, h = mask.size
    pix = mask.load()
    seen = set()
    best: list[tuple[int, int]] = []

    for y in range(h):
        for x in range(w):
            if pix[x, y] == 0 or (x, y) in seen:
                continue
            q = deque([(x, y)])
            seen.add((x, y))
            pts = []
            while q:
                px, py = q.popleft()
                pts.append((px, py))
                for nx, ny in ((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)):
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and pix[nx, ny] > 0:
                        seen.add((nx, ny))
                        q.append((nx, ny))
            if len(pts) > len(best):
                best = pts

    xs = [p[0] for p in best]
    ys = [p[1] for p in best]
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def remove_light_background(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    w, h = rgba.size
    pixels = rgba.load()
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            # Keep dog/outline/harness pixels; drop the plain off-white candidate card.
            off_white = r > 218 and g > 214 and b > 205 and max(r, g, b) - min(r, g, b) < 32
            beige_border = r > 185 and g > 175 and b > 160 and abs(r - g) < 35 and abs(g - b) < 45
            if a and not (off_white or beige_border):
                mp[x, y] = 255

    # Keep the largest connected subject so card borders and tiny artifacts disappear.
    bbox = find_subject_bbox(mask)
    clean = Image.new("L", (w, h), 0)
    cropped = mask.crop(bbox)
    clean.paste(cropped, bbox)
    clean = clean.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    clean = clean.filter(ImageFilter.GaussianBlur(0.35))
    rgba.putalpha(clean)
    return rgba.crop(bbox)


def extract_gus_sprite() -> Image.Image:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    sheet = Image.open(SOURCE).convert("RGBA")
    w, h = sheet.size
    # Bottom-right candidate from the generated 2x2 sheet.
    crop = sheet.crop((w // 2, h // 2, w, h))
    dog = remove_light_background(crop)
    dog.thumbnail((150, 174), Image.Resampling.LANCZOS)
    cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    cell.alpha_composite(dog, ((CELL_W - dog.width) // 2, 22 + (154 - dog.height) // 2))
    return cell


def shift(sprite: Image.Image, dx: int = 0, dy: int = 0) -> Image.Image:
    out = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    out.alpha_composite(sprite, (dx, dy))
    return out


def mirror(sprite: Image.Image) -> Image.Image:
    return sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def blink(sprite: Image.Image) -> Image.Image:
    out = sprite.copy()
    d = ImageDraw.Draw(out)
    # Small dark blink strokes in the approximate eye band. The real sprite remains photo-grounded.
    d.line((77, 72, 88, 73), fill=(42, 26, 18, 230), width=2)
    d.line((103, 72, 114, 73), fill=(42, 26, 18, 230), width=2)
    return out


def sad(sprite: Image.Image, frame: int) -> Image.Image:
    out = shift(sprite, 0, 2)
    d = ImageDraw.Draw(out)
    if frame % 2 == 0:
        d.ellipse((79, 83, 83, 91), fill=(96, 180, 225, 230))
    d.arc((86, 102, 111, 120), 200, 340, fill=(50, 32, 24, 210), width=2)
    return out


def wave(sprite: Image.Image, frame: int) -> Image.Image:
    out = sprite.copy()
    d = ImageDraw.Draw(out)
    # Attached paw lift: subtle, because this version is photo-like.
    y = 128 - frame * 6
    d.ellipse((115, y, 136, y + 21), fill=(190, 94, 42, 245), outline=(58, 35, 24, 230), width=2)
    return out


def focus(sprite: Image.Image, frame: int) -> Image.Image:
    out = shift(sprite, 0, 0 if frame % 2 else 1)
    d = ImageDraw.Draw(out)
    d.line((73, 68, 86, 64), fill=(48, 30, 22, 220), width=2)
    d.line((102, 64, 116, 68), fill=(48, 30, 22, 220), width=2)
    return out


def build_frames(base: Image.Image) -> dict[str, list[Image.Image]]:
    frames: dict[str, list[Image.Image]] = {}
    frames["idle"] = [shift(base, 0, y) for y in [0, 1, 1, 0, -1, 0]]
    frames["idle"][2] = blink(frames["idle"][2])
    frames["running-right"] = [shift(base, dx, dy) for dx, dy in [(-2, 1), (0, -1), (2, 0), (1, 1), (-1, -1), (0, 0), (2, 1), (0, 0)]]
    frames["running-left"] = [mirror(frame) for frame in frames["running-right"]]
    frames["waving"] = [wave(base, i) for i in [0, 1, 2, 1]]
    frames["jumping"] = [shift(base, 0, y) for y in [8, -2, -18, -8, 2]]
    frames["failed"] = [sad(base, i) for i in range(8)]
    frames["waiting"] = [shift(base, 0, y) for y in [1, 0, 1, 0, 2, 0]]
    frames["waiting"][2] = blink(frames["waiting"][2])
    frames["running"] = [shift(base, dx, dy) for dx, dy in [(0, -1), (1, 1), (0, 0), (-1, -1), (0, 1), (1, 0)]]
    frames["review"] = [focus(base, i) for i in range(6)]
    return frames


def make_atlas(frames: dict[str, list[Image.Image]]) -> Image.Image:
    atlas = Image.new("RGBA", (CELL_W * COLS, CELL_H * ROWS), (0, 0, 0, 0))
    for row, state in enumerate(ROW_ORDER):
        for col, frame in enumerate(frames[state]):
            atlas.alpha_composite(frame, (col * CELL_W, row * CELL_H))
    return atlas


def make_contact_sheet(frames: dict[str, list[Image.Image]]) -> Image.Image:
    scale = 2
    label_w = 132
    sheet = Image.new("RGB", (label_w + CELL_W * scale * COLS, CELL_H * scale * ROWS), (20, 22, 24))
    d = ImageDraw.Draw(sheet)
    for row, state in enumerate(ROW_ORDER):
        y = row * CELL_H * scale
        d.text((12, y + 16), state, fill=(235, 229, 220))
        for col in range(COLS):
            x = label_w + col * CELL_W * scale
            d.rectangle((x, y, x + CELL_W * scale - 1, y + CELL_H * scale - 1), outline=(64, 66, 68))
            if col < len(frames[state]):
                frame = Image.new("RGB", (CELL_W * scale, CELL_H * scale), (20, 22, 24))
                enlarged = frames[state][col].resize((CELL_W * scale, CELL_H * scale), Image.Resampling.NEAREST)
                frame.paste(enlarged.convert("RGB"), mask=enlarged.getchannel("A"))
                sheet.paste(frame, (x, y))
    return sheet


def validate(atlas: Image.Image) -> dict[str, object]:
    errors: list[str] = []
    if atlas.size != (1536, 1872):
        errors.append(f"atlas size was {atlas.size}, expected (1536, 1872)")
    for row, state in enumerate(ROW_ORDER):
        used = ROW_COUNTS[state]
        for col in range(COLS):
            cell = atlas.crop((col * CELL_W, row * CELL_H, (col + 1) * CELL_W, (row + 1) * CELL_H))
            bbox = cell.getchannel("A").getbbox()
            if col < used and bbox is None:
                errors.append(f"{state} frame {col} is empty")
            if col >= used and bbox is not None:
                errors.append(f"{state} unused frame {col} is not transparent")
    return {"errors": errors, "rows": ROW_COUNTS, "atlas_size": list(atlas.size), "source": str(SOURCE)}


def main() -> None:
    for path in [ARTIFACTS, QA, PET_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    base = extract_gus_sprite()
    base.save(ARTIFACTS / "gus_photoreal_base.png")
    frames = build_frames(base)
    atlas = make_atlas(frames)
    atlas.save(ARTIFACTS / "gus_spritesheet.png")
    atlas.save(PET_DIR / "spritesheet.webp", "WEBP", lossless=True, quality=100, method=6)
    make_contact_sheet(frames).save(QA / "contact-sheet.png", quality=95)

    manifest = {
        "id": "gus",
        "displayName": "Gus",
        "description": "A photo-grounded fox-red Labrador Codex pet with floppy ears, kind eyes, and cuddly Gus energy.",
        "spritesheetPath": "spritesheet.webp",
    }
    (PET_DIR / "pet.json").write_text(json.dumps(manifest, indent=2) + "\n")
    validation = validate(atlas)
    (QA / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
    if validation["errors"]:
        raise SystemExit("validation failed: " + "; ".join(validation["errors"]))
    print(ARTIFACTS / "gus_photoreal_base.png")
    print(PET_DIR / "spritesheet.webp")
    print(QA / "contact-sheet.png")


if __name__ == "__main__":
    main()
