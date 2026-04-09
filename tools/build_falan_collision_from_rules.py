#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path("/Users/chujianhe/.openclaw/workspace-taizi")
MANIFEST_PATH = ROOT / "assets" / "falan" / "object-map" / "falan-city-1000-manifest.json"
RULES_PATH = ROOT / "assets" / "falan" / "map" / "collision-rules-by-object-id.json"
OUTPUT_PATH = ROOT / "assets" / "falan" / "map" / "map-1000-collision-final.json"
SUMMARY_PATH = ROOT / "assets" / "falan" / "map" / "map-1000-collision-final-summary.json"
PREVIEW_PATH = ROOT / "output" / "falan-collision-final-preview.svg"
SKY_FLAG_VALUES = {45}


def collision_grid_index(tx: int, ty: int, cols: int) -> int:
    return tx * cols + (cols - 1 - ty)


def build_base_walkable(tile_layer: list[int]) -> list[int]:
    return [1 if cell else 0 for cell in tile_layer]


def walkable_to_blocked_flags(walkable: list[int]) -> list[int]:
    return [0 if cell else 1 for cell in walkable]


def render_collision_preview_svg(width: int, height: int, flags: list[int], cell_size: int = 6) -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width * cell_size}" height="{height * cell_size}" viewBox="0 0 {width * cell_size} {height * cell_size}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    for tx in range(width):
        for ty in range(height):
            idx = collision_grid_index(tx, ty, width)
            if not flags[idx]:
                continue
            x = tx * cell_size
            y = ty * cell_size
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="#d63a34" fill-opacity="0.78" stroke="#8b1d18" stroke-width="0.4"/>'
            )
    parts.append("</svg>")
    return "".join(parts)


def partition_mid_and_sky_items(items: list[list[int]], assets: dict[str, dict]) -> tuple[list[list[int]], list[list[int]]]:
    mid: list[list[int]] = []
    sky: list[list[int]] = []
    for row in items:
        oid = str(row[2])
        meta = assets.get(oid, {})
        (sky if meta.get("flag") in SKY_FLAG_VALUES else mid).append(row)
    return mid, sky


def iter_object_cells(tx: int, ty: int, _meta: dict, cols: int, rows: int):
    """
    objectItems 已经是 object layer 的逐格条目，不是“大物件锚点”列表。
    所以这里不能再按 areaE/areaS 扩 footprint，否则会把同一批 object cell
    多次外扩到周围空地上，造成大面积误挡。
    """
    if 0 <= tx < cols and 0 <= ty < rows:
        yield tx, ty


def apply_mid_object_rules(base: list[int], items: list[list[int]], assets: dict[str, dict], rules: dict, cols: int, rows: int) -> tuple[list[int], dict]:
    out = list(base)
    summary = {"forcePassObjects": 0, "forceBlockObjects": 0, "defaultBlockedObjects": 0}
    by_id = rules.get("rules", {})
    default_mode = rules.get("default", "force_block")
    if default_mode == "inherit":
        default_mode = "force_block"
    for tx, ty, oid in items:
        oid_str = str(oid)
        explicit_rule = oid_str in by_id
        # Mid-layer objects block by default; the rules file only needs pass-through exceptions.
        mode = by_id.get(oid_str, default_mode)
        if mode == "inherit":
            mode = default_mode
        meta = assets.get(oid_str, {})
        touched = False
        for cx, cy in iter_object_cells(tx, ty, meta, cols, rows):
            idx = collision_grid_index(cx, cy, cols)
            if mode == "force_pass":
                out[idx] = 0
                touched = True
            elif mode == "force_block":
                out[idx] = 1
                touched = True
        if touched and mode == "force_pass":
            summary["forcePassObjects"] += 1
        if touched and mode == "force_block" and explicit_rule:
            summary["forceBlockObjects"] += 1
        if touched and mode == "force_block" and not explicit_rule:
            summary["defaultBlockedObjects"] += 1
    return out, summary


def build_final_collision_payload(manifest: dict, rules: dict) -> tuple[dict, dict]:
    cols = int(manifest["cols"])
    rows = int(manifest["rows"])
    base_walkable = build_base_walkable(manifest["tileLayer"])
    base = walkable_to_blocked_flags(base_walkable)
    mid, sky = partition_mid_and_sky_items(manifest["objectItems"], manifest["assets"])
    final_flags, rule_summary = apply_mid_object_rules(base, mid, manifest["assets"], rules, cols, rows)
    payload = {"width": cols, "height": rows, "flags": final_flags}
    summary = {
        "width": cols,
        "height": rows,
        "baseBlocked": sum(1 for x in base if x),
        "finalBlocked": sum(1 for x in final_flags if x),
        "changedCells": sum(1 for a, b in zip(base, final_flags) if a != b),
        "midProcessed": len(mid),
        "skySkipped": len(sky),
        **rule_summary,
    }
    return payload, summary


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--rules", type=Path, default=RULES_PATH)
    parser.add_argument("--out", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_PATH)
    args = parser.parse_args()

    payload, summary = build_final_collision_payload(
        load_json(args.manifest),
        load_json(args.rules),
    )
    save_json(args.out, payload)
    save_json(args.summary_out, summary)
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW_PATH.write_text(
        render_collision_preview_svg(payload["width"], payload["height"], payload["flags"]),
        encoding="utf-8",
    )
    print(f"saved: {args.out}")
    print(f"saved: {args.summary_out}")
    print(f"saved: {PREVIEW_PATH}")
    print(f"finalBlocked={summary['finalBlocked']} changedCells={summary['changedCells']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
