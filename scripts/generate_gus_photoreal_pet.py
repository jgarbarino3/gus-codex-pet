from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts" / "gus_no_harness_source.png"
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
            # Keep Gus/outline pixels; drop the plain off-white generated background.
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
    crop = sheet
    dog = remove_light_background(crop)
    dog.thumbnail((158, 178), Image.Resampling.LANCZOS)
    cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    cell.alpha_composite(dog, ((CELL_W - dog.width) // 2, 18 + (160 - dog.height) // 2))
    return cell


def shift(sprite: Image.Image, dx: int = 0, dy: int = 0) -> Image.Image:
    out = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    out.alpha_composite(sprite, (dx, dy))
    return out


def subject_bbox(sprite: Image.Image) -> tuple[int, int, int, int]:
    bbox = sprite.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("sprite has no visible pixels")
    return bbox


def pose(
    sprite: Image.Image,
    dx: int = 0,
    dy: int = 0,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    angle: float = 0.0,
) -> Image.Image:
    bbox = subject_bbox(sprite)
    subject = sprite.crop(bbox)
    bottom_margin = CELL_H - bbox[3]
    new_size = (
        max(1, round(subject.width * scale_x)),
        max(1, round(subject.height * scale_y)),
    )
    subject = subject.resize(new_size, Image.Resampling.LANCZOS)
    if angle:
        subject = subject.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    out = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    x = (CELL_W - subject.width) // 2 + dx
    y = CELL_H - bottom_margin - subject.height + dy
    out.alpha_composite(subject, (x, y))
    return out


def mirror(sprite: Image.Image) -> Image.Image:
    return sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def add_shadow(sprite: Image.Image, width: int = 92, opacity: int = 52, lift: int = 0) -> Image.Image:
    out = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    bbox = subject_bbox(sprite)
    cx = (bbox[0] + bbox[2]) // 2
    y = min(CELL_H - 19, bbox[3] - 5 + lift)
    d = ImageDraw.Draw(out)
    d.ellipse((cx - width // 2, y, cx + width // 2, y + 12), fill=(0, 0, 0, opacity))
    out.alpha_composite(sprite)
    return out


def tail_spark(sprite: Image.Image, offset: int = 0) -> Image.Image:
    out = sprite.copy()
    d = ImageDraw.Draw(out, "RGBA")
    tip_y = 45 + offset
    d.line((150, 58, 162, tip_y, 173, tip_y - 5), fill=(229, 139, 63, 42), width=3, joint="curve")
    return out


def blink(sprite: Image.Image) -> Image.Image:
    out = sprite.copy()
    d = ImageDraw.Draw(out)
    # Tiny blink strokes on the eye band. Keep this subtle so Gus still reads as photo-grounded.
    d.line((43, 56, 52, 56), fill=(38, 24, 16, 235), width=2)
    d.line((67, 56, 77, 56), fill=(38, 24, 16, 235), width=2)
    return out


def sad(sprite: Image.Image, frame: int) -> Image.Image:
    out = pose(sprite, 0, 3 if frame % 2 else 4, 1.03, 0.97, -1.4)
    d = ImageDraw.Draw(out)
    if frame % 2 == 0:
        d.ellipse((66, 69, 70, 77), fill=(96, 180, 225, 220))
    d.arc((52, 83, 78, 99), 200, 340, fill=(50, 32, 24, 210), width=2)
    return add_shadow(out, 92, 44)


def wave(sprite: Image.Image, frame: int) -> Image.Image:
    lean = [-1.2, -0.6, 0.8, -0.4][frame]
    out = pose(sprite, dx=[0, 1, -1, 0][frame], dy=[0, -1, -1, 0][frame], angle=lean)
    d = ImageDraw.Draw(out)
    y = [139, 132, 123, 132][frame]
    x = [72, 74, 77, 74][frame]
    d.rounded_rectangle((x, y, x + 14, y + 25), radius=7, fill=(177, 89, 37, 238), outline=(58, 35, 24, 190), width=2)
    d.ellipse((x - 5, y - 5, x + 17, y + 13), fill=(211, 121, 56, 244), outline=(58, 35, 24, 210), width=2)
    for toe in range(3):
        d.line((x + 1 + toe * 5, y + 5, x + 2 + toe * 5, y + 9), fill=(72, 41, 24, 150), width=1)
    return add_shadow(out, 88, 48)


def focus(sprite: Image.Image, frame: int) -> Image.Image:
    out = pose(sprite, dx=[0, 0, 1, 0, -1, 0][frame], dy=[0, 1, 0, 1, 0, 0][frame], scale_x=1.0, scale_y=1.0)
    d = ImageDraw.Draw(out)
    d.line((39, 48, 53, 45), fill=(48, 30, 22, 220), width=2)
    d.line((67, 45, 82, 48), fill=(48, 30, 22, 220), width=2)
    return add_shadow(out, 88, 42)


def patient(sprite: Image.Image, frame: int) -> Image.Image:
    angles = [-2.0, -1.0, 0.0, 1.8, 0.8, 0.0]
    out = pose(sprite, dx=[0, 0, 0, 1, 0, 0][frame], dy=[1, 0, 1, 0, 1, 0][frame], angle=angles[frame])
    if frame == 2:
        out = blink(out)
    return add_shadow(out, 90, 44)


def bounce(sprite: Image.Image, frame: int, direction: int = 1) -> Image.Image:
    pattern = [
        (-3, 1, 1.06, 0.96, -1.2),
        (-1, -2, 0.98, 1.04, 0.8),
        (2, 0, 1.02, 1.00, 1.2),
        (3, 2, 1.08, 0.94, 0.0),
        (1, -2, 0.98, 1.05, -0.8),
        (-1, 0, 1.02, 1.00, -1.0),
        (-2, 1, 1.06, 0.96, 0.7),
        (0, 0, 1.00, 1.00, 0.0),
    ]
    dx, dy, sx, sy, angle = pattern[frame]
    out = pose(sprite, dx * direction, dy, sx, sy, angle * direction)
    out = tail_spark(out, [3, -3, -8, 0, 5, -4, -9, 1][frame])
    return add_shadow(out, width=[100, 84, 94, 104, 82, 94, 100, 90][frame], opacity=44)


def hop(sprite: Image.Image, frame: int) -> Image.Image:
    pattern = [
        (0, 8, 1.08, 0.91, 0.0, 104, 58),
        (0, -4, 0.98, 1.04, -1.0, 88, 42),
        (1, -24, 0.97, 1.06, 1.1, 54, 24),
        (0, -10, 1.00, 1.02, 0.0, 72, 34),
        (0, 3, 1.04, 0.97, -0.5, 98, 50),
    ]
    dx, dy, sx, sy, angle, shadow_w, shadow_o = pattern[frame]
    return add_shadow(pose(sprite, dx, dy, sx, sy, angle), shadow_w, shadow_o)


def build_frames(base: Image.Image) -> dict[str, list[Image.Image]]:
    frames: dict[str, list[Image.Image]] = {}
    frames["idle"] = [
        add_shadow(tail_spark(pose(base, 0, 0, 1.00, 1.00), 0), 88, 38),
        add_shadow(tail_spark(pose(base, 0, 1, 1.01, 0.995), -4), 90, 38),
        add_shadow(tail_spark(blink(pose(base, 0, 1, 1.01, 0.995)), -8), 90, 38),
        add_shadow(tail_spark(pose(base, 0, 0, 1.00, 1.00), -3), 88, 38),
        add_shadow(tail_spark(pose(base, 0, -1, 0.995, 1.01), 4), 86, 34),
        add_shadow(tail_spark(pose(base, 0, 0, 1.00, 1.00), 0), 88, 38),
    ]
    frames["running-right"] = [bounce(base, i, 1) for i in range(8)]
    frames["running-left"] = [mirror(frame) for frame in frames["running-right"]]
    frames["waving"] = [wave(base, i) for i in range(4)]
    frames["jumping"] = [hop(base, i) for i in range(5)]
    frames["failed"] = [sad(base, i) for i in range(8)]
    frames["waiting"] = [patient(base, i) for i in range(6)]
    frames["running"] = [bounce(base, i, 1) for i in [1, 2, 3, 4, 5, 0]]
    frames["review"] = [focus(base, i) for i in range(6)]
    return frames


def make_animation_previews(frames: dict[str, list[Image.Image]]) -> None:
    preview_dir = QA / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    durations = {
        "idle": [280, 110, 110, 140, 140, 320],
        "running-right": [120, 120, 120, 120, 120, 120, 120, 220],
        "running-left": [120, 120, 120, 120, 120, 120, 120, 220],
        "waving": [140, 140, 140, 280],
        "jumping": [140, 140, 140, 140, 280],
        "failed": [140, 140, 140, 140, 140, 140, 140, 240],
        "waiting": [150, 150, 150, 150, 150, 260],
        "running": [120, 120, 120, 120, 120, 220],
        "review": [150, 150, 150, 150, 150, 280],
    }
    for state, state_frames in frames.items():
        gif_frames = []
        for frame in state_frames:
            bg = Image.new("RGBA", (CELL_W, CELL_H), (18, 20, 22, 255))
            bg.alpha_composite(frame)
            gif_frames.append(bg.convert("P", palette=Image.Palette.ADAPTIVE))
        gif_frames[0].save(
            preview_dir / f"{state}.gif",
            save_all=True,
            append_images=gif_frames[1:],
            duration=durations[state],
            loop=0,
            disposal=2,
        )


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
    make_animation_previews(frames)

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
