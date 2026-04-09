#!/usr/bin/env python3
from __future__ import annotations


SKY_FLAG_VALUES = {45}


def collision_grid_index(tx: int, ty: int, cols: int) -> int:
    return tx * cols + (cols - 1 - ty)


def build_base_walkable(ground: list[int], flags: list[int]) -> list[int]:
    return [1 if (ground[i] and flags[i]) else 0 for i in range(len(flags))]


def partition_mid_and_sky_items(items: list[list[int]], assets: dict[str, dict]) -> tuple[list[list[int]], list[list[int]]]:
    mid: list[list[int]] = []
    sky: list[list[int]] = []
    for row in items:
        oid = str(row[2])
        meta = assets.get(oid, {})
        (sky if meta.get("flag") in SKY_FLAG_VALUES else mid).append(row)
    return mid, sky


def iter_object_cells(tx: int, ty: int, meta: dict, cols: int, rows: int):
    area_e = max(1, int(meta.get("areaE", 1)))
    area_s = max(1, int(meta.get("areaS", 1)))
    for dx in range(area_e):
        for dy in range(area_s):
            cx = tx + dx
            cy = ty + dy
            if 0 <= cx < cols and 0 <= cy < rows:
                yield cx, cy


def apply_mid_object_rules(
    base: list[int],
    items: list[list[int]],
    assets: dict[str, dict],
    rules: dict,
    cols: int,
    rows: int,
) -> list[int]:
    out = list(base)
    by_id = rules.get("rules", {})
    for tx, ty, oid in items:
        mode = by_id.get(str(oid), rules.get("default", "inherit"))
        if mode == "inherit":
            continue
        meta = assets.get(str(oid), {})
        for cx, cy in iter_object_cells(tx, ty, meta, cols, rows):
            idx = collision_grid_index(cx, cy, cols)
            if mode == "force_pass":
                out[idx] = 0
            elif mode == "force_block":
                out[idx] = 1
    return out
