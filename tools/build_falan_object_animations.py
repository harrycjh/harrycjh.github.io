#!/usr/bin/env python3
"""
根据《魔力宝贝》客户端 bin 与 cg_export 导出的 GIF，生成法兰城网页用的
falan-object-animations.json（OID → GIF 路径）。

前置：
  1. 将客户端 bin 放在仓库根目录的 bin/（与 cg_export.py 一致）
  2. 运行  python cg_export.py --animes-only  生成 output/animes/<tag>/<aid>/d*_a*.gif
  3. 将需要的 GIF 复制到 harrycjh.github.io/assets/falan/object-map/animes/（或让本脚本 --copy）

用法示例：
  python harrycjh.github.io/tools/build_falan_object_animations.py ^
    --manifest harrycjh.github.io/assets/falan/object-map/falan-city-1000-manifest.json ^
    --out harrycjh.github.io/assets/falan/object-map/falan-object-animations.json ^
    --animes-source ..\\output\\animes ^
    --copy-to harrycjh.github.io/assets/falan/object-map/animes
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

# 仓库根（crossgate），含 cg_export.py 与 bin/
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cg_export import read_anime_actions, read_anime_info  # noqa: E402

# 与 cg_export.ANIME_SETS / GRAPHIC_SETS 对齐：资源包名 → 动画目录 tag
PACK_TO_ANIME_TAG = {
    "Graphic_20": "base",
    "GraphicEx_4": "ex",
    "GraphicV3_18": "v3",
    "Graphic_Joy_20": "joy",
}

ANIME_FILES = {
    "base": ("AnimeInfo_3.bin", "Anime_3.bin"),
    "ex": ("AnimeInfoEx_1.Bin", "AnimeEx_1.Bin"),
    "v3": ("AnimeInfoV3_7.bin", "AnimeV3_7.bin"),
    "joy": ("AnimeInfo_Joy_13.bin", "Anime_Joy_13.bin"),
}


def first_animation_match(
    bin_root: Path,
    tag: str,
    wanted: set[int],
) -> dict[int, tuple[int, int, int, int]]:
    """
    返回 image_id → (aid, direction, action, frame_count)
    规则：该图作为某动作第一帧，且总帧数≥2；取首次出现。
    """
    info_name, data_name = ANIME_FILES[tag]
    ainfo_path = bin_root / info_name
    adata_path = bin_root / data_name
    if not ainfo_path.is_file() or not adata_path.is_file():
        return {}

    anime_records = read_anime_info(str(ainfo_path))
    anime_data = adata_path.read_bytes()
    is_puk2 = tag in ("v3", "joy")

    out: dict[int, tuple[int, int, int, int]] = {}
    remaining = set(wanted)
    if not remaining:
        return out

    for aid, addr, action_count in anime_records:
        if action_count == 0 or not remaining:
            continue
        actions = read_anime_actions(anime_data, addr, action_count, puk2=is_puk2)
        for direction, action, _duration, frames, _pal_field in actions:
            if len(frames) < 2:
                continue
            first = frames[0]
            if first in remaining and first not in out:
                out[first] = (aid, direction, action, len(frames))
                remaining.discard(first)
                if not remaining:
                    return out
    return out


def rel_gif_path(tag: str, aid: int, direction: int, action: int) -> str:
    return f"object-map/animes/{tag}/{aid:06d}/d{direction}_a{action}.gif"


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 falan-object-animations.json")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "harrycjh.github.io" / "assets" / "falan" / "object-map" / "falan-city-1000-manifest.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "harrycjh.github.io" / "assets" / "falan" / "object-map" / "falan-object-animations.json",
    )
    parser.add_argument(
        "--bin",
        type=Path,
        default=ROOT / "bin",
        help="客户端 bin 目录（含 AnimeInfo / Anime 等）",
    )
    parser.add_argument(
        "--animes-source",
        type=Path,
        default=ROOT / "output" / "animes",
        help="cg_export.py --animes-only 输出根目录",
    )
    parser.add_argument(
        "--copy-to",
        type=Path,
        default=None,
        help="若设置，则从 --animes-source 复制匹配到的 GIF 到此目录（如 assets/.../object-map/animes）",
    )
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    assets = manifest.get("assets") or {}

    by_tag: dict[str, set[int]] = defaultdict(set)
    oid_by_image: dict[int, list[str]] = defaultdict(list)
    for oid, meta in assets.items():
        pack = meta.get("pack")
        tag = PACK_TO_ANIME_TAG.get(pack or "")
        if not tag:
            continue
        iid = int(meta["imageId"])
        by_tag[tag].add(iid)
        oid_by_image[iid].append(str(oid))

    image_to_spec: dict[int, dict] = {}
    for tag, image_ids in by_tag.items():
        matches = first_animation_match(args.bin, tag, image_ids)
        for iid, (aid, direction, action, nframes) in matches.items():
            rel = rel_gif_path(tag, aid, direction, action)
            src = args.animes_source / tag / f"{aid:06d}" / f"d{direction}_a{action}.gif"
            image_to_spec[iid] = {
                "tag": tag,
                "aid": aid,
                "direction": direction,
                "action": action,
                "frames": nframes,
                "gif": rel,
                "src_file": str(src),
                "exists": src.is_file(),
            }

    by_oid: dict[str, dict] = {}
    for iid, spec in image_to_spec.items():
        entry = {"gif": spec["gif"]}
        if not spec["exists"]:
            entry["_missingFile"] = spec["src_file"]
        for oid in oid_by_image.get(iid, []):
            by_oid[oid] = {"gif": spec["gif"]}

    if args.copy_to and image_to_spec:
        dest_root = args.copy_to
        dest_root.mkdir(parents=True, exist_ok=True)
        copied = 0
        for spec in image_to_spec.values():
            src = Path(spec["src_file"])
            if not src.is_file():
                continue
            parts = Path(spec["gif"].replace("\\", "/")).parts
            # object-map / animes / <tag> / <aid> / file.gif
            sub = parts[2:] if len(parts) > 2 and parts[0] == "object-map" and parts[1] == "animes" else parts
            dst = dest_root.joinpath(*sub)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
        print(f"Copied {copied} GIFs -> {dest_root}")

    payload = {"version": 1, "byOid": by_oid, "stats": {"matchedImageIds": len(image_to_spec), "oidEntries": len(by_oid)}}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps(payload["stats"], ensure_ascii=False, indent=2))
    print("Wrote falan-object-animations.json (see --out)")

    missing = [s for s in image_to_spec.values() if not s["exists"]]
    if missing:
        print(f"Warning: {len(missing)} matches have no GIF on disk; run cg_export.py --animes-only then copy files.")


if __name__ == "__main__":
    main()
