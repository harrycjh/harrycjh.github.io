#!/usr/bin/env python3
from __future__ import annotations

import json
import mmap
import struct
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path("/Users/chujianhe/Downloads/crossgate_assets")
CLIENT = ROOT / "crossgate"
MAP_PATH = CLIENT / "map/0/1000.dat"
BIN_ROOT = CLIENT / "bin"
GRAPHICS_ROOT = ROOT / "extract_preview/graphics_export"

OUT_ROOT = Path("/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map")
ATLAS_ROOT = OUT_ROOT / "atlases"
MANIFEST_PATH = OUT_ROOT / "falan-city-1000-manifest.json"
SUMMARY_PATH = OUT_ROOT / "falan-city-1000-manifest-summary.json"

GRAPHIC_INFO_REC = struct.Struct("<iIIiiiiBBB5sI")
TILE_W = 64
TILE_H = 47
EMPTY_OBJECT_IDS = {0, 2}
ATLAS_MAX_W = 4096
ATLAS_MAX_H = 4096
ATLAS_PADDING = 2


PACK_INFO = [
    ("Graphic_20", "GraphicInfo_20.bin", "Graphic_20.bin"),
    ("GraphicEx_4", "GraphicInfoEx_4.bin", "GraphicEx_4.bin"),
    ("GraphicV3_18", "GraphicInfoV3_18.bin", "GraphicV3_18.bin"),
    ("Graphic_Joy_20", "GraphicInfo_Joy_20.bin", "Graphic_Joy_20.bin"),
    ("Puk2__Graphic_PUK2_2", "Puk2/GraphicInfo_PUK2_2.bin", "Puk2/Graphic_PUK2_2.bin"),
    ("Puk3__Graphic_PUK3_1", "Puk3/GraphicInfo_PUK3_1.bin", "Puk3/Graphic_PUK3_1.bin"),
    ("Graphic_Joy_22", "GraphicInfo_Joy_22.bin", "Graphic_Joy_22.bin"),
    ("sec__Graphic_SEC_1", "sec/GraphicInfo_SEC_1.bin", "sec/Graphic_SEC_1.bin"),
    ("sec__Graphic_SEC2_1", "sec/GraphicInfo_SEC2_1.bin", "sec/Graphic_SEC2_1.bin"),
    ("sec__Graphic_SEC3_1", "sec/GraphicInfo_SEC3_1.bin", "sec/Graphic_SEC3_1.bin"),
]


def bucket_name(image_id: int) -> str:
    start = (image_id // 20000) * 20000
    end = start + 19999
    return f"{start:06d}-{end:06d}"


def exported_png_path(pack: str, image_id: int) -> Path:
    return GRAPHICS_ROOT / pack / bucket_name(image_id) / f"id_{image_id:06d}.png"


def decode_rle(data: bytes) -> bytes:
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        op = data[i] & 0xF0
        if op == 0x00:
            count = data[i] & 0x0F
            i += 1
            out.extend(data[i : i + count])
            i += count
        elif op == 0x10:
            count = (data[i] & 0x0F) * 0x100 + data[i + 1]
            i += 2
            out.extend(data[i : i + count])
            i += count
        elif op == 0x20:
            count = (data[i] & 0x0F) * 0x10000 + data[i + 1] * 0x100 + data[i + 2]
            i += 3
            out.extend(data[i : i + count])
            i += count
        elif op == 0x80:
            count = data[i] & 0x0F
            out.extend([data[i + 1]] * count)
            i += 2
        elif op == 0x90:
            count = (data[i] & 0x0F) * 0x100 + data[i + 2]
            out.extend([data[i + 1]] * count)
            i += 3
        elif op == 0xA0:
            count = (data[i] & 0x0F) * 0x10000 + data[i + 2] * 0x100 + data[i + 3]
            out.extend([data[i + 1]] * count)
            i += 4
        elif op == 0xC0:
            count = data[i] & 0x0F
            out.extend([0] * count)
            i += 1
        elif op == 0xD0:
            count = (data[i] & 0x0F) * 0x100 + data[i + 1]
            out.extend([0] * count)
            i += 2
        elif op == 0xE0:
            count = (data[i] & 0x0F) * 0x10000 + data[i + 1] * 0x100 + data[i + 2]
            out.extend([0] * count)
            i += 3
        else:
            raise ValueError(f"Unknown RLE opcode {data[i]:02x} at {i}")
    return bytes(out)


def indexed_to_rgba(pixels: bytes, width: int, height: int, palette: bytes) -> Image.Image:
    buf = bytearray()
    for color_index in pixels:
        if color_index == 0:
            buf.extend((0, 0, 0, 0))
            continue
        off = color_index * 3
        if off + 2 >= len(palette):
            buf.extend((0, 0, 0, 0))
            continue
        r, g, b = palette[off], palette[off + 1], palette[off + 2]
        buf.extend((r, g, b, 255))
    rgba = Image.frombytes("RGBA", (width, height), bytes(buf))
    return rgba.transpose(Image.FLIP_TOP_BOTTOM)


def parse_map(map_path: Path) -> tuple[int, int, list[int], list[int], list[int]]:
    data = map_path.read_bytes()
    if data[:4] != b"MAP\x01":
        raise ValueError(f"Unexpected map magic in {map_path}")
    width, height = struct.unpack_from("<II", data, 12)
    count = width * height
    layers = struct.unpack_from("<" + "H" * (count * 3), data, 20)
    tiles = list(layers[:count])
    objects = list(layers[count : count * 2])
    unknown = list(layers[count * 2 : count * 3])
    return width, height, tiles, objects, unknown


def original_to_tiled(idx: int, width: int) -> tuple[int, int]:
    x = idx // width
    y = idx % width
    return x, width - y - 1


class BinaryPack:
    def __init__(self, info_path: Path, data_path: Path):
        self.info_path = info_path
        self.data_path = data_path
        self.info_buf = info_path.read_bytes()
        self._fp = data_path.open("rb")
        self.data = mmap.mmap(self._fp.fileno(), 0, access=mmap.ACCESS_READ)

    def close(self) -> None:
        self.data.close()
        self._fp.close()

    def meta(self, image_id: int) -> dict | None:
        off = image_id * GRAPHIC_INFO_REC.size
        if off + GRAPHIC_INFO_REC.size > len(self.info_buf):
            return None
        idx, addr, size, ox, oy, width, height, area_e, area_s, flag, _unk, map_id = GRAPHIC_INFO_REC.unpack_from(
            self.info_buf, off
        )
        return {
            "idx": idx,
            "addr": addr,
            "size": size,
            "ofs_x": ox,
            "ofs_y": oy,
            "width": width,
            "height": height,
            "area_e": area_e,
            "area_s": area_s,
            "flag": flag,
            "map_id": map_id,
        }

    def palette_from_image(self, image_id: int) -> bytes | None:
        meta = self.meta(image_id)
        if not meta:
            return None
        block = self.data[meta["addr"] : meta["addr"] + meta["size"]]
        if block[:2] != b"RD":
            return None
        ver = block[2]
        if ver < 2:
            return None
        _width, _height, total_len, cgp_len = struct.unpack_from("<iiii", block, 4)
        if not cgp_len:
            return None
        encoded = block[20:total_len]
        decoded = decode_rle(encoded) if ver % 2 else bytes(encoded)
        return decoded[-cgp_len:]

    def decode_image(self, image_id: int, override_palette: bytes | None = None) -> Image.Image | None:
        meta = self.meta(image_id)
        if not meta:
            return None
        block = self.data[meta["addr"] : meta["addr"] + meta["size"]]
        if block[:2] != b"RD":
            return None
        ver = block[2]
        if ver >= 2:
            width, height, total_len, cgp_len = struct.unpack_from("<iiii", block, 4)
            encoded = block[20:total_len]
        else:
            width, height, total_len = struct.unpack_from("<iii", block, 4)
            cgp_len = 0
            encoded = block[16:total_len]
        decoded = decode_rle(encoded) if ver % 2 else bytes(encoded)
        pixels = decoded[: width * height]
        if override_palette is not None:
            palette = override_palette
        elif cgp_len:
            palette = decoded[-cgp_len:]
        else:
            return None
        return indexed_to_rgba(pixels, width, height, palette)


@dataclass
class AssetMeta:
    tile_id: int
    pack: str
    image_id: int
    ofs_x: int
    ofs_y: int
    width: int
    height: int
    area_e: int
    area_s: int
    flag: int


def load_palettes() -> dict[str, bytes]:
    v3_pack = BinaryPack(BIN_ROOT / "GraphicInfoV3_18.bin", BIN_ROOT / "GraphicV3_18.bin")
    try:
        palette_3878 = v3_pack.palette_from_image(3878)
        palette_3885 = v3_pack.palette_from_image(3885)
    finally:
        v3_pack.close()
    palette_06 = (BIN_ROOT / "pal" / "palet_06.cgp").read_bytes()
    return {
        "3878": palette_3878,
        "3885": palette_3885,
        "pal06": palette_06,
    }


SPECIAL_TILE_PALETTES = {
    10309: "3878",
    10310: "3878",
    10311: "3878",
    10312: "3878",
    10001: "3885",
    10002: "3885",
    10010: "3885",
    10075: "3885",
    10313: "pal06",
    10314: "pal06",
    17644: "pal06",
}


def build_lookup(needed_ids: set[int]) -> dict[int, AssetMeta]:
    found: dict[int, AssetMeta] = {}
    for pack, rel_info, _rel_data in PACK_INFO:
        info_path = BIN_ROOT / rel_info
        if not info_path.exists():
            continue
        buf = info_path.read_bytes()
        record_count = len(buf) // GRAPHIC_INFO_REC.size
        for i in range(record_count):
            rec = GRAPHIC_INFO_REC.unpack_from(buf, i * GRAPHIC_INFO_REC.size)
            image_id, _addr, _size, ofs_x, ofs_y, width, height, area_e, area_s, flag, _unk, tile_id = rec
            if tile_id not in needed_ids or tile_id in found:
                continue
            found[tile_id] = AssetMeta(tile_id, pack, image_id, ofs_x, ofs_y, width, height, area_e, area_s, flag)
    return found


def load_asset_images(lookup: dict[int, AssetMeta]) -> tuple[dict[int, Image.Image], dict[str, int]]:
    palette_pool = load_palettes()
    binary_packs = {
        pack: BinaryPack(BIN_ROOT / rel_info, BIN_ROOT / rel_data)
        for pack, rel_info, rel_data in PACK_INFO
        if (BIN_ROOT / rel_info).exists() and (BIN_ROOT / rel_data).exists()
    }
    try:
        images: dict[int, Image.Image] = {}
        stats = {"from_export": 0, "decoded_missing": 0}
        for tile_id, asset in lookup.items():
            png_path = exported_png_path(asset.pack, asset.image_id)
            if png_path.exists():
                images[tile_id] = Image.open(png_path).convert("RGBA")
                stats["from_export"] += 1
                continue
            palette_key = SPECIAL_TILE_PALETTES.get(tile_id)
            override = palette_pool.get(palette_key) if palette_key else None
            decoded = binary_packs[asset.pack].decode_image(asset.image_id, override_palette=override)
            if decoded is None:
                raise FileNotFoundError(
                    f"Missing sprite tile_id={tile_id} pack={asset.pack} image_id={asset.image_id}"
                )
            images[tile_id] = decoded
            stats["decoded_missing"] += 1
        return images, stats
    finally:
        for pack in binary_packs.values():
            pack.close()


def pack_assets(images: dict[int, Image.Image], lookup: dict[int, AssetMeta]) -> tuple[list[str], dict[int, dict]]:
    ATLAS_ROOT.mkdir(parents=True, exist_ok=True)
    atlas_files: list[str] = []
    asset_entries: dict[int, dict] = {}
    ordered = sorted(images.items(), key=lambda item: item[1].width * item[1].height, reverse=True)

    atlas_index = -1
    atlas = None
    atlas_name = ""
    cursor_x = ATLAS_PADDING
    cursor_y = ATLAS_PADDING
    shelf_h = 0

    def flush_current() -> None:
        nonlocal atlas, atlas_name, atlas_index
        if atlas is None:
            return
        atlas.save(ATLAS_ROOT / atlas_name, optimize=True)
        atlas = None

    def new_atlas() -> None:
        nonlocal atlas_index, atlas, atlas_name, cursor_x, cursor_y, shelf_h
        flush_current()
        atlas_index += 1
        atlas_name = f"falan-atlas-{atlas_index:02d}.png"
        atlas_files.append(atlas_name)
        atlas = Image.new("RGBA", (ATLAS_MAX_W, ATLAS_MAX_H), (0, 0, 0, 0))
        cursor_x = ATLAS_PADDING
        cursor_y = ATLAS_PADDING
        shelf_h = 0

    new_atlas()
    for tile_id, img in ordered:
        iw, ih = img.size
        if iw + ATLAS_PADDING * 2 > ATLAS_MAX_W or ih + ATLAS_PADDING * 2 > ATLAS_MAX_H:
            raise ValueError(f"Asset {tile_id} too large for atlas: {img.size}")
        if cursor_x + iw + ATLAS_PADDING > ATLAS_MAX_W:
            cursor_x = ATLAS_PADDING
            cursor_y += shelf_h + ATLAS_PADDING
            shelf_h = 0
        if cursor_y + ih + ATLAS_PADDING > ATLAS_MAX_H:
            new_atlas()
        atlas.alpha_composite(img, (cursor_x, cursor_y))
        meta = lookup[tile_id]
        asset_entries[tile_id] = {
            "atlas": atlas_name,
            "atlasX": cursor_x,
            "atlasY": cursor_y,
            "atlasW": iw,
            "atlasH": ih,
            "ofsX": meta.ofs_x,
            "ofsY": meta.ofs_y,
            "width": meta.width,
            "height": meta.height,
            "pack": meta.pack,
            "imageId": meta.image_id,
            "areaE": meta.area_e,
            "areaS": meta.area_s,
            "flag": meta.flag,
        }
        cursor_x += iw + ATLAS_PADDING
        shelf_h = max(shelf_h, ih)

    flush_current()
    return atlas_files, asset_entries


def build_manifest() -> dict:
    width, height, tiles, objects, unknown = parse_map(MAP_PATH)
    needed_ids = {x for x in tiles if x > 0}
    needed_ids.update(x for x in objects if x > 0 and x not in EMPTY_OBJECT_IDS)
    lookup = build_lookup(needed_ids)
    if len(lookup) != len(needed_ids):
        missing = sorted(needed_ids - set(lookup))
        raise RuntimeError(f"Missing asset metadata for tile ids: {missing[:40]}")

    images, image_stats = load_asset_images(lookup)
    atlas_files, asset_entries = pack_assets(images, lookup)

    object_items = []
    object_count = 0
    max_object_up = 0
    max_object_left = 0
    max_object_right = 0
    for idx, tile_id in enumerate(objects):
        if tile_id in EMPTY_OBJECT_IDS or tile_id <= 0:
            continue
        tx, ty = original_to_tiled(idx, width)
        object_items.append([tx, ty, tile_id])
        object_count += 1
        meta = asset_entries[tile_id]
        max_object_up = max(max_object_up, max(0, -meta["ofsY"]))
        max_object_left = max(max_object_left, max(0, -meta["ofsX"]))
        max_object_right = max(max_object_right, max(0, meta["ofsX"] + meta["atlasW"]))

    object_items.sort(key=lambda item: (item[0] + item[1], item[1], item[0]))

    manifest = {
        "version": 1,
        "mapId": 1000,
        "cols": width,
        "rows": height,
        "worldWidth": 11128,
        "worldHeight": 8300,
        "halfW": TILE_W // 2,
        "halfH": TILE_H // 2,
        "baseX": 7004,
        "baseY": -1578,
        "atlases": atlas_files,
        "assets": {str(key): value for key, value in asset_entries.items()},
        "tileLayer": tiles,
        "objectLayer": objects,
        "objectItems": object_items,
        "emptyObjectIds": sorted(EMPTY_OBJECT_IDS),
        "viewportHint": {
            "maxObjectUpPx": max_object_up,
            "maxObjectLeftPx": max_object_left,
            "maxObjectRightPx": max_object_right,
            "objectMarginCellsX": max(4, int((max_object_left + max_object_right) / TILE_W) + 2),
            "objectMarginCellsY": max(6, int(max_object_up / TILE_H) + 2),
        },
        "stats": {
            "tileUniqueNonZero": len({x for x in tiles if x > 0}),
            "objectUniqueNonZero": len({x for x in objects if x > 0 and x not in EMPTY_OBJECT_IDS}),
            "objectCount": object_count,
            "unknownUnique": len(set(unknown)),
            "assetCount": len(asset_entries),
            "decodedMissingImages": image_stats["decoded_missing"],
            "loadedExportedImages": image_stats["from_export"],
        },
    }
    return manifest


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest()
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    SUMMARY_PATH.write_text(json.dumps(manifest["stats"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"manifest": str(MANIFEST_PATH), "stats": manifest["stats"], "atlases": manifest["atlases"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
