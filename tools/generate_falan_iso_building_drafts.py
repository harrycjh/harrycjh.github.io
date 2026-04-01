from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "falan" / "building-drafts-iso"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SCALE = 4
TW = 16
TH = 8
ZH = 8

PALETTE = {
    "outline": "#2d241b",
    "shadow": "#151d15",
    "stone_top": "#e8ddc7",
    "stone_left": "#cbb89a",
    "stone_right": "#dbc9ac",
    "stone_dark": "#b39d81",
    "wood_top": "#866043",
    "wood_left": "#654830",
    "wood_right": "#78553a",
    "roof_top": "#7a5a4a",
    "roof_left": "#5e4338",
    "roof_right": "#6e4f42",
    "roof_gold_top": "#d9b36a",
    "roof_gold_left": "#b18747",
    "roof_gold_right": "#c79d5f",
    "leaf_top": "#81b55e",
    "leaf_left": "#5d8d42",
    "leaf_right": "#73a852",
    "water_top": "#6db8c6",
    "water_left": "#4f8b99",
    "water_right": "#5ca3af",
    "red": "#c7635a",
    "blue": "#5c7ac9",
    "gold": "#f0d483",
    "glass": "#eef7fb",
    "glass_line": "#9db7c9",
    "cross": "#ef7f7f",
    "mint": "#3a6556",
    "mint_light": "#4f7f6e",
    "plaster": "#dfe4ea",
    "plaster_left": "#b7c0cb",
    "plaster_right": "#cbd4dd",
}


def scale_points(points):
    return [(x * SCALE, y * SCALE) for x, y in points]


class IsoCanvas:
    def __init__(self, width=128, height=128, origin=(64, 48)):
        self.width = width
        self.height = height
        self.origin = origin
        self.image = Image.new("RGBA", (width * SCALE, height * SCALE), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def iso(self, x, y, z):
        ox, oy = self.origin
        return (
            ox + (x - y) * TW // 2,
            oy + (x + y) * TH // 2 - z * ZH,
        )

    def polygon(self, points, fill, outline=PALETTE["outline"]):
        scaled = scale_points(points)
        self.draw.polygon(scaled, fill=fill)
        self.draw.line(scaled + [scaled[0]], fill=outline, width=max(1, SCALE // 2))

    def line(self, points, fill, width=1):
        self.draw.line(scale_points(points), fill=fill, width=width * SCALE)

    def rect(self, xy, fill):
        x0, y0, x1, y1 = xy
        self.draw.rectangle((x0 * SCALE, y0 * SCALE, x1 * SCALE, y1 * SCALE), fill=fill)


def prism(canvas, x, y, w, d, h, top, left, right, outline=PALETTE["outline"]):
    nw = canvas.iso(x, y, h)
    ne = canvas.iso(x + w, y, h)
    se = canvas.iso(x + w, y + d, h)
    sw = canvas.iso(x, y + d, h)
    nw0 = canvas.iso(x, y, 0)
    ne0 = canvas.iso(x + w, y, 0)
    se0 = canvas.iso(x + w, y + d, 0)
    sw0 = canvas.iso(x, y + d, 0)

    canvas.polygon([nw, ne, se, sw], top, outline)
    canvas.polygon([nw, sw, sw0, nw0], left, outline)
    canvas.polygon([ne, se, se0, ne0], right, outline)
    return {"nw": nw, "ne": ne, "se": se, "sw": sw, "nw0": nw0, "ne0": ne0, "se0": se0, "sw0": sw0}


def roof(canvas, x, y, w, d, h, palette, lip=0):
    top = prism(canvas, x - lip, y - lip, w + lip * 2, d + lip * 2, h, palette[0], palette[1], palette[2])
    return top


def shadow(canvas, x, y, w, d, alpha=56):
    nw = canvas.iso(x, y, 0)
    ne = canvas.iso(x + w, y, 0)
    se = canvas.iso(x + w, y + d, 0)
    sw = canvas.iso(x, y + d, 0)
    overlay = Image.new("RGBA", canvas.image.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.polygon(scale_points([(nw[0], nw[1] + 6), (ne[0], ne[1] + 6), (se[0], se[1] + 10), (sw[0], sw[1] + 10)]), fill=(13, 20, 14, alpha))
    canvas.image.alpha_composite(overlay)


def left_window(canvas, x, y, z, fill=PALETTE["glass"]):
    p0 = canvas.iso(x, y, z)
    p1 = canvas.iso(x, y + 0.42, z)
    p2 = canvas.iso(x, y + 0.42, z - 0.42)
    p3 = canvas.iso(x, y, z - 0.42)
    canvas.polygon([p0, p1, p2, p3], fill, PALETTE["glass_line"])


def right_window(canvas, x, y, z, fill=PALETTE["glass"]):
    p0 = canvas.iso(x, y, z)
    p1 = canvas.iso(x + 0.42, y, z)
    p2 = canvas.iso(x + 0.42, y, z - 0.42)
    p3 = canvas.iso(x, y, z - 0.42)
    canvas.polygon([p0, p1, p2, p3], fill, PALETTE["glass_line"])


def left_door(canvas, x, y, z, fill=PALETTE["wood_right"]):
    p0 = canvas.iso(x, y, z)
    p1 = canvas.iso(x, y + 0.58, z)
    p2 = canvas.iso(x, y + 0.58, 0)
    p3 = canvas.iso(x, y, 0)
    canvas.polygon([p0, p1, p2, p3], fill, PALETTE["outline"])


def right_door(canvas, x, y, z, fill=PALETTE["wood_right"]):
    p0 = canvas.iso(x, y, z)
    p1 = canvas.iso(x + 0.58, y, z)
    p2 = canvas.iso(x + 0.58, y, 0)
    p3 = canvas.iso(x, y, 0)
    canvas.polygon([p0, p1, p2, p3], fill, PALETTE["outline"])


def flag(canvas, x, y, z, cloth):
    start = canvas.iso(x, y, z)
    top = canvas.iso(x, y, z + 1.3)
    canvas.line([start, top], "#725238", width=1)
    cloth_pts = [
        top,
        (top[0] + 8, top[1] + 2),
        (top[0] + 3, top[1] + 7),
        (top[0], top[1] + 5),
    ]
    canvas.polygon(cloth_pts, cloth, PALETTE["outline"])


def tree(canvas, x, y, size=1.0):
    prism(canvas, x + 0.18, y + 0.18, 0.22, 0.22, 1.0 * size, "#6c4a31", "#533725", "#62422d")
    prism(canvas, x - 0.25, y - 0.1, 0.7, 0.7, 1.6 * size, PALETTE["leaf_top"], PALETTE["leaf_left"], PALETTE["leaf_right"])
    prism(canvas, x - 0.12, y + 0.02, 0.45, 0.45, 2.2 * size, "#91c970", "#69974d", "#7eb960")


def draw_castle():
    c = IsoCanvas(origin=(64, 44))
    shadow(c, 2.3, 2.5, 4.8, 3.6)
    prism(c, 2.8, 2.5, 3.8, 3.0, 2.5, PALETTE["stone_top"], PALETTE["stone_left"], PALETTE["stone_right"])
    roof(c, 2.55, 2.25, 4.3, 3.4, 2.95, (PALETTE["roof_top"], PALETTE["roof_left"], PALETTE["roof_right"]))
    prism(c, 2.0, 2.0, 1.0, 1.0, 3.2, "#d7cab2", "#bdab8f", "#ccbba0")
    prism(c, 6.3, 2.0, 1.0, 1.0, 3.2, "#d7cab2", "#bdab8f", "#ccbba0")
    roof(c, 1.8, 1.8, 1.3, 1.3, 3.55, (PALETTE["roof_top"], PALETTE["roof_left"], PALETTE["roof_right"]))
    roof(c, 6.1, 1.8, 1.3, 1.3, 3.55, (PALETTE["roof_top"], PALETTE["roof_left"], PALETTE["roof_right"]))
    right_door(c, 4.55, 5.1, 1.5, PALETTE["wood_left"])
    left_window(c, 3.15, 4.4, 1.8)
    right_window(c, 5.45, 4.15, 1.8)
    left_window(c, 2.45, 2.95, 2.3)
    right_window(c, 6.3, 3.0, 2.3)
    flag(c, 2.35, 2.1, 4.1, PALETTE["red"])
    flag(c, 7.1, 2.1, 4.1, PALETTE["blue"])
    return c.image


def draw_cathedral():
    c = IsoCanvas(origin=(64, 46))
    shadow(c, 2.8, 2.8, 3.6, 2.8)
    prism(c, 3.0, 3.0, 3.0, 2.2, 2.2, "#d8c3a1", "#bb9f7a", "#ccb08b")
    roof(c, 2.85, 2.85, 3.3, 2.55, 2.7, ("#8a6253", "#68483d", "#7b5949"))
    prism(c, 4.05, 3.85, 0.9, 0.9, 3.6, "#d8c3a1", "#bb9f7a", "#ccb08b")
    roof(c, 3.95, 3.75, 1.1, 1.1, 4.0, ("#8a6253", "#68483d", "#7b5949"))
    start = c.iso(4.48, 4.25, 5.0)
    c.line([start, (start[0], start[1] - 12)], PALETTE["gold"], width=1)
    c.line([(start[0] - 5, start[1] - 8), (start[0] + 5, start[1] - 8)], PALETTE["gold"], width=1)
    left_window(c, 3.55, 4.65, 1.6)
    right_window(c, 5.2, 4.25, 1.6)
    right_door(c, 4.25, 5.0, 1.45, PALETTE["wood_left"])
    return c.image


def draw_guild_inn():
    c = IsoCanvas(origin=(64, 48))
    shadow(c, 2.5, 3.0, 4.0, 2.8)
    prism(c, 2.8, 3.0, 3.5, 2.5, 1.9, "#cba476", "#a37d56", "#bb9163")
    roof(c, 2.55, 2.8, 3.9, 2.9, 2.5, ("#6f4e40", "#52392f", "#62463a"))
    right_door(c, 4.55, 5.0, 1.25, PALETTE["wood_left"])
    left_window(c, 3.35, 4.65, 1.45)
    right_window(c, 5.35, 4.15, 1.45)
    sign = prism(c, 3.7, 3.2, 1.6, 0.36, 2.15, "#3f6178", "#2c4758", "#355466")
    return c.image


def draw_workshop():
    c = IsoCanvas(origin=(62, 50))
    shadow(c, 3.0, 3.4, 3.2, 2.0)
    prism(c, 3.25, 3.6, 2.5, 1.6, 1.65, "#c98c54", "#9f693a", "#b57b47")
    roof(c, 3.05, 3.35, 2.85, 1.95, 2.15, ("#9a6a41", "#754b2d", "#88573a"))
    right_door(c, 4.7, 4.9, 1.1, PALETTE["wood_left"])
    left_window(c, 3.7, 4.55, 1.25, "#f6e2a9")
    prism(c, 5.2, 3.7, 0.35, 0.35, 3.2, "#704b32", "#563725", "#65422d")
    smoke = Image.new("RGBA", c.image.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke)
    for cx, cy, r, a in [(82, 86, 8, 110), (90, 76, 6, 90), (96, 66, 5, 70)]:
      sd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(235, 235, 235, a))
    c.image.alpha_composite(smoke)
    return c.image


def draw_hospital():
    c = IsoCanvas(origin=(64, 50))
    shadow(c, 2.8, 3.1, 3.5, 2.4)
    prism(c, 3.1, 3.3, 3.0, 1.9, 1.5, PALETTE["plaster"], PALETTE["plaster_left"], PALETTE["plaster_right"])
    roof(c, 2.9, 3.05, 3.3, 2.2, 1.95, ("#c4d3e1", "#a4b6c6", "#b6c8d7"))
    left_window(c, 3.65, 4.75, 1.1, "#f3fbff")
    right_window(c, 5.15, 4.35, 1.1, "#f3fbff")
    p0 = c.iso(4.45, 4.15, 1.8)
    c.rect((p0[0] - 8, p0[1] - 7, p0[0] + 8, p0[1] + 7), "#f5efe0")
    c.rect((p0[0] - 2, p0[1] - 7, p0[0] + 2, p0[1] + 7), PALETTE["cross"])
    c.rect((p0[0] - 8, p0[1] - 2, p0[0] + 8, p0[1] + 2), PALETTE["cross"])
    return c.image


def draw_arena():
    c = IsoCanvas(origin=(64, 54))
    shadow(c, 2.4, 3.3, 4.5, 2.8)
    prism(c, 2.8, 3.6, 3.8, 2.1, 0.9, "#d2a15f", "#aa7945", "#be8b52")
    prism(c, 2.7, 3.5, 4.0, 0.6, 1.5, "#956339", "#734928", "#855630")
    prism(c, 2.7, 5.0, 4.0, 0.6, 1.5, "#956339", "#734928", "#855630")
    flag(c, 3.0, 3.5, 1.8, PALETTE["red"])
    flag(c, 6.4, 3.5, 1.8, PALETTE["blue"])
    return c.image


def draw_reversi_hall():
    c = IsoCanvas(origin=(64, 50))
    shadow(c, 3.0, 3.2, 3.2, 2.1)
    prism(c, 3.25, 3.45, 2.6, 1.7, 1.55, "#7b583d", "#5f4330", "#6f4e37")
    roof(c, 3.05, 3.25, 2.95, 2.0, 2.1, ("#5f4536", "#483328", "#543d31"))
    sign = prism(c, 3.6, 3.85, 1.6, 0.32, 1.95, PALETTE["mint_light"], PALETTE["mint"], "#446f60")
    right_door(c, 4.55, 4.85, 1.0, "#41271a")
    p = c.iso(5.25, 4.25, 2.0)
    c.rect((p[0] - 3, p[1] - 12, p[0] + 1, p[1] + 8), PALETTE["gold"])
    c.rect((p[0] - 11, p[1] - 3, p[0] + 7, p[1] + 1), PALETTE["gold"])
    return c.image


BUILDINGS = [
    ("castle", draw_castle),
    ("cathedral", draw_cathedral),
    ("guild-inn", draw_guild_inn),
    ("workshop", draw_workshop),
    ("hospital", draw_hospital),
    ("arena", draw_arena),
    ("reversi-hall", draw_reversi_hall),
]


def trim_image(image, margin=2):
    bbox = image.getbbox()
    if not bbox:
        return image
    left, top, right, bottom = bbox
    left = max(0, left - margin * SCALE)
    top = max(0, top - margin * SCALE)
    right = min(image.width, right + margin * SCALE)
    bottom = min(image.height, bottom + margin * SCALE)
    return image.crop((left, top, right, bottom))


def make_sheet(paths):
    card_w = 280
    card_h = 200
    cols = 2
    rows = 4
    sheet = Image.new("RGBA", (card_w * cols + 32, card_h * rows + 32), "#142016")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width - 1, sheet.height - 1), outline="#5a6d49", width=4)

    for idx, (slug, path) in enumerate(paths):
        col = idx % cols
        row = idx // cols
        left = 18 + col * card_w
        top = 18 + row * card_h
        draw.rectangle((left, top, left + card_w - 18, top + card_h - 18), fill="#1c2b1d", outline="#5d6c4a", width=3)
        image = Image.open(path)
        x = left + (card_w - 18 - image.width) // 2
        y = top + 18
        sheet.alpha_composite(image, (x, y))
        draw.text((left + 18, top + card_h - 48), slug, fill="#f4efcb")
        draw.text((left + 18, top + card_h - 28), path.stem, fill="#c4d1aa")

    sheet.save(OUT_DIR / "falan-iso-building-sheet-v1.png")


def main():
    saved = []
    for slug, factory in BUILDINGS:
        image = trim_image(factory())
        path = OUT_DIR / f"{slug}-iso-v1.png"
        image.save(path)
        saved.append((slug, path))
    make_sheet(saved)


if __name__ == "__main__":
    main()
