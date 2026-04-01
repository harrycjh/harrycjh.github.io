from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
AVATAR_DIR = ROOT / "assets" / "falan" / "avatars"
PREVIEW_DIR = ROOT / "assets" / "falan" / "previews"
SPRITE_DIR = ROOT / "assets" / "falan" / "sprites"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
SPRITE_DIR.mkdir(parents=True, exist_ok=True)


TRAVELERS = [
    {
        "id": "ghost",
        "name": "大头鬼",
        "skin": "#f4dcc1",
        "hair": "#8a634a",
        "coat": "#6884d7",
        "accent": "#a8c1ff",
        "detail": "#dff6ff",
        "kind": "ghost",
    },
    {
        "id": "dog",
        "name": "小狗子",
        "skin": "#f2d5b5",
        "hair": "#7e5a3e",
        "coat": "#7d69ce",
        "accent": "#c2a6ff",
        "detail": "#ffd77f",
        "kind": "dog",
    },
    {
        "id": "fat",
        "name": "臭胖子",
        "skin": "#ebcaa1",
        "hair": "#6d4a32",
        "coat": "#bc6a56",
        "accent": "#f2a185",
        "detail": "#ffd17d",
        "kind": "fat",
    },
    {
        "id": "rabbit",
        "name": "小兔子",
        "skin": "#f0d7c3",
        "hair": "#7a5f48",
        "coat": "#58a188",
        "accent": "#9ae7d0",
        "detail": "#fff0f6",
        "kind": "rabbit",
    },
    {
        "id": "crayfish",
        "name": "小龙虾",
        "skin": "#f0ccb5",
        "hair": "#6a432e",
        "coat": "#b85a62",
        "accent": "#f39fa8",
        "detail": "#ffe1ae",
        "kind": "crayfish",
    },
]


def px(draw, scale, x, y, w, h, color):
    draw.rectangle(
        (x * scale, y * scale, (x + w) * scale - 1, (y + h) * scale - 1),
        fill=color,
    )


def make_avatar(traveler):
    scale = 4
    image = Image.new("RGBA", (16 * scale, 16 * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    px(draw, scale, 2, 11, 12, 3, "#233321")
    px(draw, scale, 3, 3, 10, 10, traveler["coat"])
    px(draw, scale, 4, 4, 8, 6, traveler["skin"])
    px(draw, scale, 4, 10, 8, 2, traveler["accent"])
    px(draw, scale, 5, 6, 1, 1, "#221714")
    px(draw, scale, 10, 6, 1, 1, "#221714")
    px(draw, scale, 7, 8, 2, 1, "#d48476")

    kind = traveler["kind"]
    if kind == "ghost":
        px(draw, scale, 3, 1, 10, 3, traveler["accent"])
        px(draw, scale, 5, 0, 6, 2, traveler["detail"])
        px(draw, scale, 2, 4, 1, 4, traveler["accent"])
        px(draw, scale, 13, 4, 1, 4, traveler["accent"])
    elif kind == "dog":
        px(draw, scale, 2, 2, 2, 5, traveler["hair"])
        px(draw, scale, 12, 2, 2, 5, traveler["hair"])
        px(draw, scale, 5, 3, 6, 2, traveler["detail"])
        px(draw, scale, 6, 10, 4, 1, traveler["detail"])
    elif kind == "fat":
        px(draw, scale, 3, 2, 10, 2, traveler["hair"])
        px(draw, scale, 4, 1, 8, 2, traveler["detail"])
        px(draw, scale, 3, 10, 10, 3, traveler["accent"])
    elif kind == "rabbit":
        px(draw, scale, 4, 0, 2, 5, traveler["detail"])
        px(draw, scale, 10, 0, 2, 5, traveler["detail"])
        px(draw, scale, 4, 1, 1, 3, traveler["accent"])
        px(draw, scale, 10, 1, 1, 3, traveler["accent"])
        px(draw, scale, 6, 10, 4, 1, traveler["detail"])
    elif kind == "crayfish":
        px(draw, scale, 3, 2, 10, 3, traveler["coat"])
        px(draw, scale, 2, 4, 2, 2, traveler["accent"])
        px(draw, scale, 12, 4, 2, 2, traveler["accent"])
        px(draw, scale, 0, 7, 3, 2, traveler["coat"])
        px(draw, scale, 1, 6, 2, 1, traveler["accent"])
        px(draw, scale, 13, 7, 3, 2, traveler["coat"])
        px(draw, scale, 13, 6, 2, 1, traveler["accent"])
        px(draw, scale, 5, 10, 6, 1, traveler["detail"])

    image.save(AVATAR_DIR / f"{traveler['id']}.png")


def draw_body(draw, traveler, direction, step):
    skin = traveler["skin"]
    hair = traveler["hair"]
    coat = traveler["coat"]
    accent = traveler["accent"]
    detail = traveler["detail"]

    if direction == "down":
        px(draw, 1, 5, 2, 6, 2, hair)
        px(draw, 1, 4, 4, 8, 4, skin)
        px(draw, 1, 5, 6, 1, 1, "#241916")
        px(draw, 1, 10, 6, 1, 1, "#241916")
        px(draw, 1, 6, 8, 4, 1, "#cc7f73")
        px(draw, 1, 4, 8, 8, 5, coat)
        px(draw, 1, 5, 10, 6, 1, accent)
        px(draw, 1, 3, 9, 1, 3, skin)
        px(draw, 1, 12, 9, 1, 3, skin)
    elif direction == "up":
        px(draw, 1, 4, 3, 8, 5, hair)
        px(draw, 1, 4, 8, 8, 5, coat)
        px(draw, 1, 5, 10, 6, 1, accent)
        px(draw, 1, 3, 9, 1, 3, accent)
        px(draw, 1, 12, 9, 1, 3, accent)
    else:
        px(draw, 1, 5, 2, 5, 2, hair)
        px(draw, 1, 4, 4, 6, 4, skin)
        eye_x = 8 if direction == "right" else 5
        px(draw, 1, eye_x, 6, 1, 1, "#241916")
        px(draw, 1, 4, 8, 7, 5, coat)
        px(draw, 1, 5, 10, 5, 1, accent)
        hand_x = 11 if direction == "right" else 3
        px(draw, 1, hand_x, 9, 1, 3, skin)

    leg_shift = 1 if step else 0
    px(draw, 1, 5, 13, 2, 3 + leg_shift, "#47382d")
    px(draw, 1, 9, 13, 2, 3 + (1 - leg_shift), "#47382d")
    px(draw, 1, 5, 16, 2, 1, "#201814")
    px(draw, 1, 9, 16, 2, 1, "#201814")

    kind = traveler["kind"]
    if kind == "ghost":
        px(draw, 1, 3, 3, 1, 4, accent)
        px(draw, 1, 12, 3, 1, 4, accent)
        px(draw, 1, 6, 1, 4, 1, detail)
    elif kind == "dog":
        px(draw, 1, 3, 2, 2, 4, hair)
        px(draw, 1, 11, 2, 2, 4, hair)
        px(draw, 1, 6, 9, 4, 1, detail)
    elif kind == "fat":
        px(draw, 1, 3, 3, 10, 2, hair)
        px(draw, 1, 4, 2, 8, 1, detail)
        px(draw, 1, 4, 11, 8, 2, accent)
    elif kind == "rabbit":
        if direction in ("down", "up"):
            px(draw, 1, 5, 0, 2, 4, detail)
            px(draw, 1, 9, 0, 2, 4, detail)
            px(draw, 1, 5, 1, 1, 2, accent)
            px(draw, 1, 9, 1, 1, 2, accent)
        else:
            rear_x = 5 if direction == "right" else 8
            front_x = 8 if direction == "right" else 5
            px(draw, 1, rear_x, 0, 2, 4, detail)
            px(draw, 1, front_x, 1, 1, 3, accent)
    elif kind == "crayfish":
        px(draw, 1, 4, 2, 8, 3, coat)
        px(draw, 1, 2, 5, 2, 2, accent)
        px(draw, 1, 12, 5, 2, 2, accent)
        if direction in ("down", "up"):
            px(draw, 1, 1, 8, 3, 2, coat)
            px(draw, 1, 2, 7, 2, 1, accent)
            px(draw, 1, 12, 8, 3, 2, coat)
            px(draw, 1, 12, 7, 2, 1, accent)
        else:
            px(draw, 1, 1, 7, 2, 2, accent)
            px(draw, 1, 2, 9, 2, 1, coat)
            px(draw, 1, 11, 7, 4, 2, coat)
            px(draw, 1, 13, 6, 2, 1, accent)
        px(draw, 1, 6, 10, 4, 1, detail)


def make_preview(traveler):
    base = Image.new("RGBA", (24, 28), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)
    px(draw, 1, 7, 23, 10, 2, (18, 28, 22, 180))

    body = Image.new("RGBA", (16, 20), (0, 0, 0, 0))
    body_draw = ImageDraw.Draw(body)
    draw_body(body_draw, traveler, "down", 0)
    base.alpha_composite(body, (4, 3))

    scaled = base.resize((96, 112), Image.Resampling.NEAREST)
    scaled.save(PREVIEW_DIR / f"{traveler['id']}.png")


def make_sprite_sheet(traveler):
    frame_w = 16
    frame_h = 20
    order = [
        ("down", 0),
        ("down", 1),
        ("right", 0),
        ("right", 1),
        ("up", 0),
        ("up", 1),
    ]
    sheet = Image.new("RGBA", (frame_w * len(order), frame_h), (0, 0, 0, 0))

    for index, (direction, step) in enumerate(order):
        frame = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame)
        draw_body(draw, traveler, direction, step)
        sheet.paste(frame, (index * frame_w, 0), frame)

    sheet.save(SPRITE_DIR / f"{traveler['id']}.png")


def main():
    for traveler in TRAVELERS:
        make_avatar(traveler)
        make_preview(traveler)
        make_sprite_sheet(traveler)


if __name__ == "__main__":
    main()
