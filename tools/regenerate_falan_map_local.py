#!/usr/bin/env python3
"""
从本地魔力客户端资源再生法兰城大地图资源（与 index.html 中 sceneMap 尺寸一致）。

输出：
  - assets/falan/object-map/falan-city-1000-manifest.json + atlases + summary
  - assets/falan/map/falan-city-1000-preview.png  （整图预览）
  - assets/falan/map/tiles-512/falan-city-1000-r{row}-c{col}.webp  （512 切片）

依赖：
  - 游戏根目录下 map/0/1000.dat、bin/ 下 Graphic*.bin
  - 推荐已运行 cg_export.py，得到 output/graphics/base/*.png（扁平 6 位 gid）

用法（在 tools 目录或任意目录）：
  python regenerate_falan_map_local.py
  python regenerate_falan_map_local.py --game-root "D:/path/to/魔力宝贝6.02"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# tools/ -> harrycjh.github.io -> 魔力宝贝6.02
_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_GAME_ROOT = _REPO_ROOT.parent


def _patch_build_falan_paths(game_root: Path, repo_root: Path) -> None:
    import build_falan_object_map_assets as m

    m.ROOT = game_root
    m.CLIENT = game_root
    m.MAP_PATH = game_root / "map" / "0" / "1000.dat"
    m.BIN_ROOT = game_root / "bin"
    m.GRAPHICS_ROOT = game_root / "output" / "graphics" / "base"
    m.OUT_ROOT = repo_root / "assets" / "falan" / "object-map"
    m.ATLAS_ROOT = m.OUT_ROOT / "atlases"
    m.MANIFEST_PATH = m.OUT_ROOT / "falan-city-1000-manifest.json"
    m.SUMMARY_PATH = m.OUT_ROOT / "falan-city-1000-manifest-summary.json"

    def flat_exported_png(pack: str, image_id: int) -> Path:
        return m.GRAPHICS_ROOT / f"{image_id:06d}.png"

    m.exported_png_path = flat_exported_png


def _layer_index(tx: int, ty: int, cols: int) -> int:
    return tx * cols + (cols - ty - 1)


def _map_to_preview(tx: int, ty: int, half_w: int, half_h: int, base_x: int, base_y: float) -> tuple[float, float]:
    x = (tx - ty) * half_w + base_x
    y = (tx + ty) * half_h + base_y
    return x, y


def composite_preview(
    manifest: dict,
    atlas_dir: Path,
    world_w: int,
    world_h: int,
) -> "Image.Image":
    from PIL import Image

    cols = int(manifest["cols"])
    rows = int(manifest["rows"])
    half_w = int(manifest["halfW"])
    half_h = int(manifest["halfH"])
    base_x = float(manifest["baseX"])
    base_y = float(manifest["baseY"])
    assets = manifest["assets"]
    tile_layer = manifest["tileLayer"]
    object_items = manifest["objectItems"]

    atlases: dict[str, Image.Image] = {}
    for name in manifest["atlases"]:
        p = atlas_dir / name
        if not p.exists():
            raise FileNotFoundError(f"atlas missing: {p}")
        atlases[name] = Image.open(p).convert("RGBA")

    img = Image.new("RGBA", (world_w, world_h), (0, 0, 0, 0))

    # tiles: diagonal order (same as index.html drawObjectAssembledTiles)
    for diag in range(0, (cols - 1) + (rows - 1) + 1):
        start_tx = max(0, diag - (rows - 1))
        end_tx = min(cols - 1, diag)
        for tx in range(start_tx, end_tx + 1):
            ty = diag - tx
            tid = tile_layer[_layer_index(tx, ty, cols)]
            if not tid:
                continue
            meta = assets.get(str(tid))
            if not meta:
                continue
            atlas = atlases.get(meta["atlas"])
            if not atlas:
                continue
            px, py = _map_to_preview(tx, ty, half_w, half_h, base_x, base_y)
            crop = atlas.crop(
                (
                    meta["atlasX"],
                    meta["atlasY"],
                    meta["atlasX"] + meta["atlasW"],
                    meta["atlasY"] + meta["atlasH"],
                )
            )
            dx = int(round(px + meta["ofsX"]))
            dy = int(round(py + meta["ofsY"]))
            img.alpha_composite(crop, (dx, dy))

    # objects
    for item in object_items:
        tx, ty, oid = int(item[0]), int(item[1]), int(item[2])
        meta = assets.get(str(oid))
        if not meta:
            continue
        atlas = atlases.get(meta["atlas"])
        if not atlas:
            continue
        px, py = _map_to_preview(tx, ty, half_w, half_h, base_x, base_y)
        crop = atlas.crop(
            (
                meta["atlasX"],
                meta["atlasY"],
                meta["atlasX"] + meta["atlasW"],
                meta["atlasY"] + meta["atlasH"],
            )
        )
        dx = int(round(px + meta["ofsX"]))
        dy = int(round(py + meta["ofsY"]))
        img.alpha_composite(crop, (dx, dy))

    return img


def slice_tiles(img, tile_size: int, out_dir: Path, prefix: str) -> None:
    from PIL import Image

    out_dir.mkdir(parents=True, exist_ok=True)
    w, h = img.size
    rows = (h + tile_size - 1) // tile_size
    cols = (w + tile_size - 1) // tile_size
    for row in range(rows):
        for col in range(cols):
            x0 = col * tile_size
            y0 = row * tile_size
            tile = img.crop((x0, y0, min(x0 + tile_size, w), min(y0 + tile_size, h)))
            if tile.mode != "RGBA":
                tile = tile.convert("RGBA")
            # pad to exact tile_size for consistent canvas drawing
            if tile.size != (tile_size, tile_size):
                pad = Image.new("RGBA", (tile_size, tile_size), (0, 0, 0, 0))
                pad.paste(tile, (0, 0))
                tile = pad
            out_path = out_dir / f"{prefix}-r{row}-c{col}.webp"
            tile.save(out_path, "WEBP", quality=88, method=4)
    print(f"tiles: {rows}x{cols} -> {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--game-root",
        type=Path,
        default=_DEFAULT_GAME_ROOT,
        help="魔力客户端根目录（含 map/0/1000.dat、bin/、output/graphics/base）",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_REPO_ROOT,
        help="harrycjh.github.io 仓库根",
    )
    parser.add_argument("--skip-manifest", action="store_true", help="仅根据已有 manifest 重画预览与切片")
    args = parser.parse_args()

    game_root: Path = args.game_root.resolve()
    repo_root: Path = args.repo_root.resolve()

    if not (game_root / "map" / "0" / "1000.dat").is_file():
        print(f"ERROR: 找不到地图文件: {game_root / 'map' / '0' / '1000.dat'}", file=sys.stderr)
        sys.exit(1)
    if not (game_root / "bin").is_dir():
        print(f"ERROR: 找不到 bin 目录: {game_root / 'bin'}", file=sys.stderr)
        sys.exit(1)

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    _patch_build_falan_paths(game_root, repo_root)

    import build_falan_object_map_assets as b

    manifest_path = b.MANIFEST_PATH
    atlas_dir = b.ATLAS_ROOT

    if not args.skip_manifest:
        print("Building manifest + atlases (may take a while)...")
        manifest = b.build_manifest()
        b.OUT_ROOT.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        b.SUMMARY_PATH.write_text(json.dumps(manifest["stats"], ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"manifest": str(manifest_path), "stats": manifest["stats"]}, ensure_ascii=False, indent=2))
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    world_w = int(manifest["worldWidth"])
    world_h = int(manifest["worldHeight"])

    print(f"Compositing preview {world_w}x{world_h}...")
    preview = composite_preview(manifest, atlas_dir, world_w, world_h)
    map_dir = repo_root / "assets" / "falan" / "map"
    map_dir.mkdir(parents=True, exist_ok=True)
    preview_path = map_dir / "falan-city-1000-preview.png"
    preview.save(preview_path, "PNG", optimize=True)
    print(f"saved: {preview_path}")

    tiles_dir = map_dir / "tiles-512"
    print("Slicing 512 webp tiles...")
    slice_tiles(preview, 512, tiles_dir, "falan-city-1000")

    occ = map_dir / "falan-city-1000-occupancy.png"
    if not occ.exists():
        print(
            f"NOTE: 未生成占用图 {occ}；若需要碰撞遮罩请从旧备份复制或单独管线生成。",
            file=sys.stderr,
        )

    print("Done.")


if __name__ == "__main__":
    main()
