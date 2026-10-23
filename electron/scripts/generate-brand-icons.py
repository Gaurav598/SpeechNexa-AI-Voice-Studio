"""Render the SpeechNexa SVG mark into native installer icon formats.

Uses Pillow (already in the backend environment). The simple paths mirror
electron/public/favicon.svg; keep their geometry and colors in sync.
"""

from pathlib import Path
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "icons"
SIZE = 1024
SCALE = SIZE / 64


def color_mix(a, b, ratio):
    return tuple(round(a[i] * (1 - ratio) + b[i] * ratio) for i in range(3))


def line_gradient(x, y, start, end, a, b):
    dx, dy = end[0] - start[0], end[1] - start[1]
    ratio = max(0, min(1, ((x - start[0]) * dx + (y - start[1]) * dy) / (dx * dx + dy * dy)))
    return color_mix(a, b, ratio)


def point(x, y):
    return round(x * SCALE), round(y * SCALE)


def bezier(p0, p1, p2, p3, count=100):
    for n in range(count + 1):
        t = n / count
        u = 1 - t
        yield (
            u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1],
        )


def gradient_stroke(canvas, points, width, opacity=255):
    points = list(points)
    mask = Image.new("L", (SIZE, SIZE))
    draw = ImageDraw.Draw(mask)
    draw.line([point(*item) for item in points], fill=opacity, width=round(width * SCALE), joint="curve")
    radius = width * SCALE / 2
    for x, y in (points[0], points[-1]):
        px, py = point(x, y)
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=opacity)
    layer = Image.new("RGBA", (SIZE, SIZE))
    pixels = layer.load()
    alpha = mask.load()
    for y in range(SIZE):
        for x in range(SIZE):
            if alpha[x, y]:
                rgb = line_gradient(x / SCALE, y / SCALE, (13, 48), (51, 17), (93, 231, 204), (139, 172, 255))
                pixels[x, y] = (*rgb, alpha[x, y])
    canvas.alpha_composite(layer)


def render():
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    field = Image.new("RGBA", (SIZE, SIZE))
    pixels = field.load()
    for y in range(SIZE):
        for x in range(SIZE):
            rgb = line_gradient(x / SCALE, y / SCALE, (5, 4), (60, 61), (20, 36, 61), (8, 18, 31))
            pixels[x, y] = (*rgb, 255)
    mask = Image.new("L", (SIZE, SIZE))
    ImageDraw.Draw(mask).rounded_rectangle((point(2, 2), point(62, 62)), radius=16 * SCALE, fill=255)
    canvas.paste(field, (0, 0), mask)
    outline = Image.new("RGBA", (SIZE, SIZE))
    ImageDraw.Draw(outline).rounded_rectangle(
        (point(2.5, 2.5), point(61.5, 61.5)), radius=15.5 * SCALE,
        outline=(255, 255, 255, 41), width=max(1, round(SCALE)),
    )
    canvas.alpha_composite(outline)
    gradient_stroke(canvas, [(16, 45), (16, 19), (32, 45), (32, 19)], 5)
    gradient_stroke(canvas, bezier((39, 24), (42.8, 27.3), (42.8, 36.7), (39, 40)), 3, 230)
    gradient_stroke(canvas, bezier((46, 19), (52.1, 25.5), (52.1, 38.5), (46, 45)), 3, 230)
    return canvas


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    image = render()
    image.resize((512, 512), Image.Resampling.LANCZOS).save(OUT / "icon.png")
    image.resize((32, 32), Image.Resampling.LANCZOS).save(OUT / "32x32.png")
    recording = image.resize((32, 32), Image.Resampling.LANCZOS)
    badge = ImageDraw.Draw(recording)
    badge.ellipse((20, 20, 31, 31), fill=(228, 72, 90, 255), outline=(255, 255, 255, 255), width=1)
    recording.save(OUT / "tray-recording.png")
    image.save(OUT / "icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    image.save(OUT / "icon.icns", format="ICNS")


if __name__ == "__main__":
    main()
