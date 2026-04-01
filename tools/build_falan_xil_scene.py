from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "output" / "free-iso-assets" / "components"
OUT = ROOT / "assets" / "falan" / "kitbash"


def load_component(group: str, index: int) -> Image.Image:
    return Image.open(COMPONENTS / group / f"{index:02d}.png").convert("RGBA")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def scale(img: Image.Image, factor: float) -> Image.Image:
    width = max(1, round(img.width * factor))
    height = max(1, round(img.height * factor))
    return img.resize((width, height), Image.Resampling.NEAREST)


def crop_alpha(img: Image.Image) -> Image.Image:
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def paste_bottom_center(canvas: Image.Image, sprite: Image.Image, center_x: int, bottom_y: int) -> None:
    canvas.alpha_composite(sprite, (round(center_x - sprite.width / 2), round(bottom_y - sprite.height)))


def place(canvas: Image.Image, sprite: Image.Image, x: int, y: int) -> None:
    canvas.alpha_composite(sprite, (round(x), round(y)))


def draw_badge(text: str, width: int, fill: str, ink: str = "#ffffff") -> Image.Image:
    font = ImageFont.load_default()
    badge = Image.new("RGBA", (width, 22), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    draw.rounded_rectangle((0, 0, width - 1, 21), radius=6, fill=fill)
    draw.text((6, 6), text, fill=ink, font=font)
    return badge


def draw_reversi_sign() -> Image.Image:
    sign = Image.new("RGBA", (58, 34), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sign)
    draw.rounded_rectangle((0, 0, 57, 23), radius=6, fill="#2a231c", outline="#f4d78f")
    draw.ellipse((9, 5, 23, 19), fill="#fcfcf6", outline="#d2d2ca")
    draw.ellipse((31, 5, 45, 19), fill="#181818", outline="#555555")
    draw.rectangle((26, 23, 30, 33), fill="#6d5434")
    return sign


def draw_cross_sign() -> Image.Image:
    sign = Image.new("RGBA", (36, 34), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sign)
    draw.rounded_rectangle((3, 0, 32, 23), radius=6, fill="#f4efe2", outline="#c8c1b3")
    draw.rectangle((15, 5, 20, 18), fill="#d44a4a")
    draw.rectangle((11, 9, 24, 14), fill="#d44a4a")
    draw.rectangle((16, 23, 19, 33), fill="#7a5f3d")
    return sign


def draw_cross() -> Image.Image:
    cross = Image.new("RGBA", (18, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cross)
    draw.rectangle((8, 0, 10, 16), fill="#f3dea0")
    draw.rectangle((3, 6, 15, 9), fill="#f3dea0")
    return cross


def draw_flag(color: str) -> Image.Image:
    flag = Image.new("RGBA", (18, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(flag)
    draw.rectangle((2, 0, 3, 19), fill="#7e6545")
    draw.polygon([(4, 3), (15, 6), (4, 10)], fill=color)
    return flag


def with_shadow(sprite: Image.Image, width: int, height: int, opacity: int = 70) -> Image.Image:
    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.ellipse((0, 0, width - 1, height - 1), fill=(16, 20, 24, opacity))
    return shadow


def build_castle() -> Image.Image:
    canvas = Image.new("RGBA", (340, 220), (0, 0, 0, 0))
    back_wall = scale(load_component("oga_build", 14), 0.38)
    front_wall = scale(load_component("oga_build", 13), 0.36)
    tower_left = scale(load_component("oga_build", 6), 1.6)
    tower_right = scale(load_component("oga_build", 8), 1.9)
    roof = scale(load_component("oga_build", 4), 0.72)
    spire = scale(load_component("x_struct1", 2), 1.3)
    flag_l = draw_flag("#b65555")
    flag_r = draw_flag("#547db4")

    place(canvas, with_shadow(front_wall, 194, 24, 72), 72, 182)
    place(canvas, back_wall, 58, 98)
    place(canvas, roof, 118, 42)
    place(canvas, front_wall, 72, 114)
    paste_bottom_center(canvas, tower_left, 94, 152)
    paste_bottom_center(canvas, tower_right, 252, 152)
    paste_bottom_center(canvas, spire, 170, 122)
    place(canvas, flag_l, 88, 54)
    place(canvas, flag_r, 233, 45)

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((154, 126, 187, 151), radius=6, fill="#614633")
    draw.rectangle((167, 112, 174, 151), fill="#d9b06d")
    return crop_alpha(canvas)


def build_cathedral() -> Image.Image:
    canvas = Image.new("RGBA", (250, 190), (0, 0, 0, 0))
    hall = scale(load_component("x_struct1", 0), 1.34)
    spire = scale(load_component("x_struct1", 2), 1.52)
    roof = scale(load_component("oga_build", 2), 1.05)
    cross = draw_cross()
    place(canvas, with_shadow(hall, 116, 22), 70, 164)
    paste_bottom_center(canvas, hall, 126, 156)
    paste_bottom_center(canvas, spire, 164, 122)
    place(canvas, roof, 88, 58)
    place(canvas, cross, 162, 36)
    return crop_alpha(canvas)


def build_guild_inn() -> Image.Image:
    canvas = Image.new("RGBA", (260, 200), (0, 0, 0, 0))
    inn = scale(load_component("x_struct2", 0), 1.22)
    rug = scale(load_component("x_struct2", 1), 1.15)
    rug2 = scale(load_component("x_struct2", 2), 0.98)
    table = scale(load_component("x_struct2", 4), 0.86)
    badge = draw_badge("INN", 36, "#7f5836")
    place(canvas, with_shadow(inn, 126, 24), 72, 165)
    paste_bottom_center(canvas, rug, 68, 172)
    paste_bottom_center(canvas, rug2, 193, 172)
    paste_bottom_center(canvas, inn, 140, 158)
    paste_bottom_center(canvas, table, 188, 164)
    place(canvas, badge, 154, 94)
    return crop_alpha(canvas)


def build_workshop() -> Image.Image:
    canvas = Image.new("RGBA", (220, 180), (0, 0, 0, 0))
    house = scale(load_component("x_struct1", 1), 1.2)
    table = scale(load_component("x_struct2", 3), 0.92)
    plank = scale(load_component("oga_build", 10), 1.0)
    badge = draw_badge("WORK", 46, "#70583f")
    place(canvas, with_shadow(house, 92, 18), 66, 152)
    paste_bottom_center(canvas, plank, 68, 161)
    paste_bottom_center(canvas, house, 120, 148)
    paste_bottom_center(canvas, table, 174, 155)
    place(canvas, badge, 126, 97)
    return crop_alpha(canvas)


def build_hospital() -> Image.Image:
    canvas = Image.new("RGBA", (230, 180), (0, 0, 0, 0))
    house = scale(load_component("x_struct1", 0), 1.22)
    sign = draw_cross_sign()
    place(canvas, with_shadow(house, 102, 18), 63, 151)
    paste_bottom_center(canvas, house, 116, 147)
    place(canvas, sign, 142, 101)
    return crop_alpha(canvas)


def build_arena() -> Image.Image:
    canvas = Image.new("RGBA", (250, 170), (0, 0, 0, 0))
    stage = scale(load_component("oga_build", 10), 1.4)
    stage_big = scale(load_component("oga_build", 7), 1.18)
    rug = scale(load_component("x_struct2", 1), 1.15)
    rug2 = scale(load_component("x_struct2", 2), 1.15)
    place(canvas, with_shadow(stage, 126, 20), 64, 143)
    paste_bottom_center(canvas, rug, 74, 153)
    paste_bottom_center(canvas, rug2, 176, 153)
    paste_bottom_center(canvas, stage, 125, 150)
    paste_bottom_center(canvas, stage_big, 124, 137)
    return crop_alpha(canvas)


def build_reversi_hall() -> Image.Image:
    canvas = Image.new("RGBA", (240, 180), (0, 0, 0, 0))
    hall = scale(load_component("x_struct1", 1), 1.26)
    sign = draw_reversi_sign()
    place(canvas, with_shadow(hall, 98, 18), 70, 152)
    paste_bottom_center(canvas, hall, 122, 147)
    place(canvas, sign, 132, 98)
    return crop_alpha(canvas)


def save_sprite(img: Image.Image, folder: Path, name: str) -> Path:
    ensure_dir(folder)
    path = folder / name
    crop_alpha(img).save(path)
    return path


def build_contact_sheet(images: list[tuple[str, Path]], out_path: Path) -> None:
    ensure_dir(out_path.parent)
    font = ImageFont.load_default()
    card_w = 170
    card_h = 150
    cols = 3
    pad = 18
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * (card_w + pad) + pad, rows * (card_h + 42 + pad) + pad + 24), (13, 17, 23, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 8), "Falan Xilurus + OGA kitbash preview", fill="#f0f6fc", font=font)
    for idx, (label, path) in enumerate(images):
        card_x = pad + (idx % cols) * (card_w + pad)
        card_y = pad + 24 + (idx // cols) * (card_h + 42 + pad)
        draw.rounded_rectangle((card_x, card_y, card_x + card_w, card_y + card_h), radius=12, fill="#1b2230", outline="#30363d")
        img = Image.open(path).convert("RGBA")
        preview = ImageOps.contain(img, (card_w - 20, card_h - 20), method=Image.Resampling.NEAREST)
        sheet.alpha_composite(preview, (card_x + (card_w - preview.width) // 2, card_y + (card_h - preview.height) // 2))
        draw.text((card_x + 4, card_y + card_h + 8), label, fill="#dce3f1", font=font)
    sheet.convert("RGB").save(out_path)


def main() -> None:
    buildings_out = OUT / "buildings"
    flora_out = OUT / "flora"
    props_out = OUT / "props"

    generated = [
        ("castle", save_sprite(build_castle(), buildings_out, "castle-xil-oga.png")),
        ("cathedral", save_sprite(build_cathedral(), buildings_out, "cathedral-xil-oga.png")),
        ("guildInn", save_sprite(build_guild_inn(), buildings_out, "guild-inn-xil-oga.png")),
        ("workshop", save_sprite(build_workshop(), buildings_out, "workshop-xil-oga.png")),
        ("hospital", save_sprite(build_hospital(), buildings_out, "hospital-xil-oga.png")),
        ("arena", save_sprite(build_arena(), buildings_out, "arena-xil-oga.png")),
        ("reversiHall", save_sprite(build_reversi_hall(), buildings_out, "reversi-hall-xil-oga.png")),
    ]

    tree_oak = scale(load_component("oga_outside", 52), 0.65)
    tree_round = scale(load_component("oga_outside", 57), 0.72)
    tree_pine = scale(load_component("oga_outside", 53), 0.72)
    bush = scale(load_component("oga_outside", 44), 1.2)
    market_rug = scale(load_component("x_struct2", 1), 1.0)
    market_rug_alt = scale(load_component("x_struct2", 2), 1.0)
    market_table = scale(load_component("x_struct2", 4), 0.86)
    plank = scale(load_component("oga_build", 10), 1.0)

    generated.extend(
        [
            ("tree-oak", save_sprite(tree_oak, flora_out, "tree-oak.png")),
            ("tree-round", save_sprite(tree_round, flora_out, "tree-round.png")),
            ("tree-pine", save_sprite(tree_pine, flora_out, "tree-pine.png")),
            ("bush", save_sprite(bush, flora_out, "bush-wide.png")),
            ("market-red", save_sprite(market_rug, props_out, "market-red.png")),
            ("market-red-alt", save_sprite(market_rug_alt, props_out, "market-red-alt.png")),
            ("market-table", save_sprite(market_table, props_out, "market-table.png")),
            ("plank", save_sprite(plank, props_out, "plank-floor.png")),
        ]
    )

    build_contact_sheet(generated, OUT / "falan-xil-oga-sheet.png")


if __name__ == "__main__":
    main()
