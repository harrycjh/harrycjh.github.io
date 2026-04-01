from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "falan" / "building-drafts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SCALE = 4

PALETTE = {
    "outline": "#2d2218",
    "shadow": "#1f2a1d",
    "stone": "#d9ceb8",
    "stone_dark": "#b4a489",
    "stone_light": "#efe6d6",
    "wood": "#6f4b31",
    "wood_dark": "#4d3424",
    "gold": "#f1d58a",
    "grass": "#6aa85b",
    "leaf": "#79b862",
    "glass": "#d8f1f2",
    "glass_dark": "#7cb6c4",
    "red": "#c45b58",
    "blue": "#5b78bf",
    "navy": "#39536e",
    "brown": "#8a5b39",
    "tan": "#c69b63",
    "beige": "#e9d5ae",
    "plaster": "#ddd8d5",
    "mint": "#6fba92",
}


def px(draw, x, y, w, h, color):
    draw.rectangle(
        (x * SCALE, y * SCALE, (x + w) * SCALE - 1, (y + h) * SCALE - 1),
        fill=color,
    )


def dot(draw, x, y, color):
    px(draw, x, y, 1, 1, color)


def new_sprite(width, height):
    image = Image.new("RGBA", (width * SCALE, height * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    return image, draw


def add_shadow(draw, x, y, w, h):
    px(draw, x, y, w, h, (20, 28, 20, 120))


def add_roof(draw, x, y, w, h, base, shade, trim, tile_step=4):
    px(draw, x, y, w, h, base)
    px(draw, x, y, w, 1, trim)
    px(draw, x, y + h - 1, w, 1, shade)
    for row in range(y + 2, y + h, 3):
        px(draw, x + 1, row, w - 2, 1, shade)
    for col in range(x + 2, x + w - 2, tile_step):
        px(draw, col, y + 1, 1, h - 2, trim)


def add_wall(draw, x, y, w, h, base, shade, foundation=None):
    px(draw, x, y, w, h, base)
    px(draw, x, y, 1, h, shade)
    px(draw, x + w - 1, y, 1, h, shade)
    px(draw, x, y + h - 1, w, 1, shade)
    if foundation:
        px(draw, x, y + h - 2, w, 2, foundation)
    for row in range(y + 3, y + h - 3, 4):
        px(draw, x + 2, row, w - 4, 1, shade)


def add_window(draw, x, y, w, h, frame, glass, shine):
    px(draw, x, y, w, h, frame)
    px(draw, x + 1, y + 1, w - 2, h - 2, glass)
    px(draw, x + 1, y + h // 2, w - 2, 1, frame)
    px(draw, x + w // 2, y + 1, 1, h - 2, frame)
    px(draw, x + 1, y + 1, 2, 1, shine)


def add_door(draw, x, y, w, h, frame, fill, knob=False, arch=False):
    px(draw, x, y, w, h, frame)
    if arch and w > 4:
        px(draw, x + 1, y, w - 2, 1, fill)
    px(draw, x + 1, y + 1, w - 2, h - 1, fill)
    px(draw, x + w // 2, y + 1, 1, h - 2, frame)
    if knob:
        dot(draw, x + w // 2 - 2, y + h // 2, PALETTE["gold"])
        dot(draw, x + w // 2 + 1, y + h // 2, PALETTE["gold"])


def add_banner(draw, x, y, w, h, pole, cloth):
    px(draw, x, y, 1, h, pole)
    px(draw, x + 1, y + 1, w, h - 2, cloth)
    px(draw, x + 1, y + h - 2, w - 1, 1, pole)


def add_bush(draw, x, y, w):
    px(draw, x, y, w, 3, PALETTE["leaf"])
    px(draw, x + 1, y - 1, w - 2, 2, PALETTE["grass"])


def draw_castle():
    image, draw = new_sprite(64, 48)
    add_shadow(draw, 14, 42, 36, 3)
    add_roof(draw, 18, 8, 28, 6, "#b9ab95", PALETTE["stone_dark"], PALETTE["stone_light"], 3)
    add_wall(draw, 18, 14, 28, 20, PALETTE["stone"], PALETTE["stone_dark"], PALETTE["stone_dark"])
    add_wall(draw, 10, 16, 10, 22, "#cfc3aa", PALETTE["stone_dark"], PALETTE["stone_dark"])
    add_wall(draw, 44, 16, 10, 22, "#cfc3aa", PALETTE["stone_dark"], PALETTE["stone_dark"])
    add_roof(draw, 8, 12, 14, 5, "#c4b7a0", PALETTE["stone_dark"], PALETTE["stone_light"], 3)
    add_roof(draw, 42, 12, 14, 5, "#c4b7a0", PALETTE["stone_dark"], PALETTE["stone_light"], 3)
    add_door(draw, 28, 24, 8, 10, PALETTE["wood_dark"], PALETTE["wood"], knob=True, arch=True)
    add_window(draw, 22, 19, 5, 7, PALETTE["stone_dark"], PALETTE["glass"], PALETTE["stone_light"])
    add_window(draw, 37, 19, 5, 7, PALETTE["stone_dark"], PALETTE["glass"], PALETTE["stone_light"])
    add_window(draw, 12, 22, 4, 6, PALETTE["stone_dark"], PALETTE["glass"], PALETTE["stone_light"])
    add_window(draw, 48, 22, 4, 6, PALETTE["stone_dark"], PALETTE["glass"], PALETTE["stone_light"])
    add_banner(draw, 14, 3, 5, 7, PALETTE["wood"], PALETTE["red"])
    add_banner(draw, 49, 3, 5, 7, PALETTE["wood"], PALETTE["blue"])
    px(draw, 23, 33, 18, 3, PALETTE["tan"])
    px(draw, 25, 36, 14, 2, PALETTE["beige"])
    return image


def draw_cathedral():
    image, draw = new_sprite(52, 40)
    add_shadow(draw, 10, 35, 30, 3)
    add_roof(draw, 12, 9, 28, 8, "#8a5f51", "#5f4039", "#c8a58e", 4)
    add_wall(draw, 12, 16, 28, 16, "#d5c099", "#aa8e67", "#aa8e67")
    add_roof(draw, 22, 4, 8, 8, "#8a5f51", "#5f4039", "#c8a58e", 2)
    px(draw, 25, 1, 2, 9, PALETTE["gold"])
    px(draw, 22, 4, 8, 1, PALETTE["gold"])
    add_door(draw, 22, 22, 8, 10, PALETTE["wood_dark"], PALETTE["wood"], arch=True)
    add_window(draw, 16, 20, 5, 8, "#7a5544", PALETTE["glass"], PALETTE["stone_light"])
    add_window(draw, 31, 20, 5, 8, "#7a5544", PALETTE["glass"], PALETTE["stone_light"])
    px(draw, 13, 30, 26, 2, "#b29569")
    return image


def draw_guild_inn():
    image, draw = new_sprite(56, 38)
    add_shadow(draw, 12, 33, 32, 3)
    add_roof(draw, 10, 10, 36, 8, "#6c4e3f", "#4b352b", "#c4a27b", 4)
    add_wall(draw, 12, 17, 32, 14, "#c3a074", "#9a7755", "#8c6a4a")
    add_door(draw, 25, 21, 8, 10, PALETTE["wood_dark"], PALETTE["wood"], knob=True)
    add_window(draw, 16, 20, 6, 6, "#6b4a33", PALETTE["glass"], PALETTE["stone_light"])
    add_window(draw, 35, 20, 6, 6, "#6b4a33", PALETTE["glass"], PALETTE["stone_light"])
    px(draw, 21, 12, 14, 4, PALETTE["navy"])
    px(draw, 23, 13, 10, 2, PALETTE["gold"])
    add_bush(draw, 12, 31, 7)
    add_bush(draw, 37, 31, 7)
    return image


def draw_workshop():
    image, draw = new_sprite(46, 34)
    add_shadow(draw, 8, 30, 26, 3)
    add_roof(draw, 8, 10, 30, 7, "#9c6a3e", "#6d472b", "#dcb182", 4)
    add_wall(draw, 10, 16, 26, 11, "#c78d52", "#9a6436", "#8b5933")
    add_window(draw, 14, 19, 5, 5, "#6d472b", "#f7e4b1", PALETTE["stone_light"])
    add_door(draw, 26, 18, 7, 9, PALETTE["wood_dark"], PALETTE["wood"])
    px(draw, 31, 6, 3, 10, "#714c33")
    px(draw, 32, 3, 1, 2, "rgba(240,240,240,180)")
    px(draw, 33, 1, 1, 2, "rgba(240,240,240,120)")
    px(draw, 18, 27, 10, 2, PALETTE["wood_dark"])
    return image


def draw_hospital():
    image, draw = new_sprite(48, 34)
    add_shadow(draw, 8, 30, 28, 3)
    add_roof(draw, 8, 11, 30, 6, "#b7c8d9", "#7f95a9", "#eef6fb", 4)
    add_wall(draw, 10, 16, 26, 11, PALETTE["plaster"], "#bfc2c7", "#b0b5bb")
    add_window(draw, 14, 19, 5, 5, "#8aa1b4", "#f1fbff", PALETTE["stone_light"])
    add_window(draw, 27, 19, 5, 5, "#8aa1b4", "#f1fbff", PALETTE["stone_light"])
    px(draw, 21, 17, 6, 6, "#f7f0da")
    px(draw, 23, 18, 2, 4, "#df7777")
    px(draw, 22, 19, 4, 2, "#df7777")
    add_door(draw, 21, 22, 6, 5, "#8aa1b4", "#d7dee7")
    return image


def draw_arena():
    image, draw = new_sprite(58, 32)
    add_shadow(draw, 8, 28, 36, 3)
    px(draw, 10, 13, 32, 4, "#8d5c38")
    px(draw, 8, 17, 36, 10, "#b8824f")
    px(draw, 14, 20, 24, 5, "#d8b16c")
    for x in range(12, 42, 8):
        px(draw, x, 24, 4, 3, "#7c5738")
    add_banner(draw, 13, 8, 4, 6, PALETTE["wood"], PALETTE["red"])
    add_banner(draw, 36, 8, 4, 6, PALETTE["wood"], PALETTE["blue"])
    px(draw, 18, 27, 16, 1, PALETTE["wood_dark"])
    return image


def draw_reversi_hall():
    image, draw = new_sprite(46, 34)
    add_shadow(draw, 8, 30, 28, 3)
    add_roof(draw, 8, 10, 30, 7, "#5c4334", "#3e2d22", "#b4936f", 4)
    add_wall(draw, 10, 16, 26, 11, "#7c5639", "#5e412d", "#533927")
    px(draw, 14, 17, 18, 4, "#355948")
    px(draw, 15, 18, 16, 2, "#4a7362")
    add_door(draw, 18, 21, 7, 6, "#332014", "#4b2d1f", knob=True)
    px(draw, 27, 20, 5, 5, "#f7efbe")
    px(draw, 29, 15, 2, 10, PALETTE["gold"])
    px(draw, 20, 13, 8, 2, PALETTE["gold"])
    dot(draw, 17, 22, PALETTE["gold"])
    dot(draw, 17, 23, PALETTE["gold"])
    return image


BUILDINGS = [
    ("castle", "richier-castle", draw_castle),
    ("cathedral", "cathedral", draw_cathedral),
    ("guild-inn", "guild-inn", draw_guild_inn),
    ("workshop", "workshop", draw_workshop),
    ("hospital", "hospital", draw_hospital),
    ("arena", "arena", draw_arena),
    ("reversi-hall", "reversi-hall", draw_reversi_hall),
]


def make_sheet(saved_paths):
    font = ImageFont.load_default()
    card_w = 260
    card_h = 190
    cols = 2
    rows = 4
    sheet = Image.new("RGBA", (card_w * cols + 32, card_h * rows + 32), "#142016")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width - 1, sheet.height - 1), outline="#5a6d49", width=4)

    for index, (_, label, path) in enumerate(saved_paths):
        col = index % cols
        row = index // cols
        left = 18 + col * card_w
        top = 18 + row * card_h
        draw.rectangle((left, top, left + card_w - 18, top + card_h - 18), fill="#1c2b1d", outline="#5d6c4a", width=3)
        image = Image.open(path)
        x = left + (card_w - 18 - image.width) // 2
        y = top + 18
        sheet.alpha_composite(image, (x, y))
        draw.text((left + 16, top + card_h - 52), label, fill="#f4efcb", font=font)
        draw.text((left + 16, top + card_h - 34), path.stem, fill="#c4d1aa", font=font)

    sheet.save(OUT_DIR / "falan-building-sheet-v1.png")


def main():
    saved = []
    for slug, label, factory in BUILDINGS:
        image = factory()
        path = OUT_DIR / f"{slug}-v1.png"
        image.save(path)
        saved.append((slug, label, path))
    make_sheet(saved)


if __name__ == "__main__":
    main()
