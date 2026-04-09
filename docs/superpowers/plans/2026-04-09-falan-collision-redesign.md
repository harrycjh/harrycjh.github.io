# Falan Collision Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Falan's current collision source with a new offline-generated final collision file built from `map-1000.json` plus `object id` rules, where ground defines the candidate walkable area, mid-layer objects may override it, and sky-layer objects never block.

**Architecture:** Keep the browser runtime simple. A Python generator will read `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000.json`, `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/falan-city-1000-manifest.json`, and a new `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/collision-rules-by-object-id.json`, then emit `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final.json`. The browser will switch to the new file and keep using the existing `collisionState.grid`, `collides()`, and overlay renderer unchanged.

**Tech Stack:** Python 3.14 stdlib (`json`, `pathlib`, `unittest`, `argparse`), existing HTML/CSS/JS in `/Users/chujianhe/.openclaw/workspace-taizi/index.html`

---

## File Structure

- Create: `/Users/chujianhe/.openclaw/workspace-taizi/tools/build_falan_collision_from_rules.py`
- Create: `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/collision-rules-by-object-id.json`
- Create: `/Users/chujianhe/.openclaw/workspace-taizi/tests/test_build_falan_collision_from_rules.py`
- Modify: `/Users/chujianhe/.openclaw/workspace-taizi/index.html`
- Modify: `/Users/chujianhe/.openclaw/workspace-taizi/docs/falan-collision-and-coords.md`
- Modify: `/Users/chujianhe/.openclaw/workspace-taizi/docs/falan-runtime-architecture.md`

Notes:
- Keep `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000.json` untouched as the baseline input.
- Keep the output file separate as `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final.json`.
- Do not add runtime semantic collision logic back into the browser.

### Task 1: Add Characterization Tests For The Offline Collision Builder

**Files:**
- Create: `/Users/chujianhe/.openclaw/workspace-taizi/tests/test_build_falan_collision_from_rules.py`
- Test: `/Users/chujianhe/.openclaw/workspace-taizi/tests/test_build_falan_collision_from_rules.py`

- [ ] **Step 1: Write the failing test file**

Create `/Users/chujianhe/.openclaw/workspace-taizi/tests/test_build_falan_collision_from_rules.py`:

```python
import unittest

from tools.build_falan_collision_from_rules import (
    build_base_walkable,
    collision_grid_index,
    partition_mid_and_sky_items,
    apply_mid_object_rules,
)


class BuildFalanCollisionFromRulesTest(unittest.TestCase):
    def test_build_base_walkable_intersects_ground_and_flags(self):
        ground = [0, 7, 9, 4]
        flags = [1, 1, 0, 1]

        actual = build_base_walkable(ground, flags)

        self.assertEqual(actual, [0, 1, 0, 1])

    def test_partition_mid_and_sky_items_uses_flag_45_as_sky(self):
        assets = {
            "100": {"flag": 0, "areaE": 1, "areaS": 1},
            "200": {"flag": 45, "areaE": 1, "areaS": 1},
        }
        items = [
            [10, 20, 100],
            [11, 21, 200],
        ]

        mid, sky = partition_mid_and_sky_items(items, assets)

        self.assertEqual(mid, [[10, 20, 100]])
        self.assertEqual(sky, [[11, 21, 200]])

    def test_apply_mid_object_rules_force_pass_and_force_block(self):
        cols = 4
        rows = 4
        base = [0] * (cols * rows)
        base[collision_grid_index(1, 1, cols)] = 1
        base[collision_grid_index(2, 2, cols)] = 1

        assets = {
            "100": {"flag": 0, "areaE": 1, "areaS": 1},
            "101": {"flag": 0, "areaE": 1, "areaS": 1},
        }
        items = [
            [1, 1, 100],
            [0, 0, 101],
        ]
        rules = {
            "default": "inherit",
            "rules": {
                "100": "force_pass",
                "101": "force_block",
            },
        }

        actual = apply_mid_object_rules(base, items, assets, rules, cols, rows)

        self.assertEqual(actual[collision_grid_index(1, 1, cols)], 0)
        self.assertEqual(actual[collision_grid_index(0, 0, cols)], 1)
        self.assertEqual(actual[collision_grid_index(2, 2, cols)], 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
python3 -m unittest tests.test_build_falan_collision_from_rules -v
```

Expected:

```text
ERROR: Failed to import test module: test_build_falan_collision_from_rules
ModuleNotFoundError: No module named 'tools.build_falan_collision_from_rules'
```

- [ ] **Step 3: Create the minimal implementation skeleton**

Create `/Users/chujianhe/.openclaw/workspace-taizi/tools/build_falan_collision_from_rules.py`:

```python
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
```

- [ ] **Step 4: Re-run the tests and verify they pass**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
python3 -m unittest tests.test_build_falan_collision_from_rules -v
```

Expected:

```text
Ran 3 tests in ...
OK
```

- [ ] **Step 5: Commit the test-backed skeleton**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
git add tests/test_build_falan_collision_from_rules.py tools/build_falan_collision_from_rules.py
git commit -m "test: add coverage for Falan collision generator"
```

### Task 2: Implement Rule Loading And Final Collision JSON Generation

**Files:**
- Modify: `/Users/chujianhe/.openclaw/workspace-taizi/tools/build_falan_collision_from_rules.py`
- Create: `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/collision-rules-by-object-id.json`
- Create: `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final.json`
- Create: `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final-summary.json`
- Test: `/Users/chujianhe/.openclaw/workspace-taizi/tests/test_build_falan_collision_from_rules.py`

- [ ] **Step 1: Extend the test file with an end-to-end fixture test**

Append to `/Users/chujianhe/.openclaw/workspace-taizi/tests/test_build_falan_collision_from_rules.py`:

```python
    def test_end_to_end_generation_uses_ground_flags_and_mid_rules(self):
        cols = 3
        rows = 3
        map_json = {
            "width": cols,
            "height": rows,
            "ground": [
                1, 1, 1,
                1, 0, 1,
                1, 1, 1,
            ],
            "objects": [0] * 9,
            "flags": [
                1, 1, 1,
                1, 1, 1,
                1, 0, 1,
            ],
        }
        manifest = {
            "rows": rows,
            "cols": cols,
            "assets": {
                "100": {"flag": 0, "areaE": 1, "areaS": 1},
                "200": {"flag": 45, "areaE": 1, "areaS": 1},
            },
            "objectItems": [
                [1, 1, 100],
                [2, 2, 200],
            ],
        }
        rules = {
            "default": "inherit",
            "rules": {"100": "force_block", "200": "force_block"},
        }

        from tools.build_falan_collision_from_rules import build_final_collision_payload
        payload, summary = build_final_collision_payload(map_json, manifest, rules)

        self.assertEqual(payload["width"], 3)
        self.assertEqual(payload["height"], 3)
        self.assertEqual(payload["flags"][collision_grid_index(1, 1, cols)], 1)
        self.assertEqual(payload["flags"][collision_grid_index(2, 2, cols)], 1)
        self.assertEqual(summary["skySkipped"], 1)
```

- [ ] **Step 2: Run the tests to verify the new test fails**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
python3 -m unittest tests.test_build_falan_collision_from_rules -v
```

Expected:

```text
ImportError / AttributeError for build_final_collision_payload
```

- [ ] **Step 3: Implement the real generator and JSON outputs**

Replace `/Users/chujianhe/.openclaw/workspace-taizi/tools/build_falan_collision_from_rules.py` with:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path("/Users/chujianhe/.openclaw/workspace-taizi")
BASE_MAP_PATH = ROOT / "assets" / "falan" / "map" / "map-1000.json"
MANIFEST_PATH = ROOT / "assets" / "falan" / "object-map" / "falan-city-1000-manifest.json"
RULES_PATH = ROOT / "assets" / "falan" / "map" / "collision-rules-by-object-id.json"
OUTPUT_PATH = ROOT / "assets" / "falan" / "map" / "map-1000-collision-final.json"
SUMMARY_PATH = ROOT / "assets" / "falan" / "map" / "map-1000-collision-final-summary.json"
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


def apply_mid_object_rules(base: list[int], items: list[list[int]], assets: dict[str, dict], rules: dict, cols: int, rows: int) -> tuple[list[int], dict]:
    out = list(base)
    summary = {"forcePassObjects": 0, "forceBlockObjects": 0}
    by_id = rules.get("rules", {})
    default_mode = rules.get("default", "inherit")
    for tx, ty, oid in items:
        mode = by_id.get(str(oid), default_mode)
        if mode == "inherit":
            continue
        meta = assets.get(str(oid), {})
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
        if touched and mode == "force_block":
            summary["forceBlockObjects"] += 1
    return out, summary


def build_final_collision_payload(map_json: dict, manifest: dict, rules: dict) -> tuple[dict, dict]:
    cols = int(map_json["width"])
    rows = int(map_json["height"])
    base = build_base_walkable(map_json["ground"], map_json["flags"])
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
    parser.add_argument("--map", type=Path, default=BASE_MAP_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--rules", type=Path, default=RULES_PATH)
    parser.add_argument("--out", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_PATH)
    args = parser.parse_args()

    payload, summary = build_final_collision_payload(
        load_json(args.map),
        load_json(args.manifest),
        load_json(args.rules),
    )
    save_json(args.out, payload)
    save_json(args.summary_out, summary)
    print(f"saved: {args.out}")
    print(f"saved: {args.summary_out}")
    print(f"finalBlocked={summary['finalBlocked']} changedCells={summary['changedCells']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Create `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/collision-rules-by-object-id.json`:

```json
{
  "default": "inherit",
  "rules": {
    "10000": "force_pass",
    "10085": "force_pass",
    "10086": "force_pass",
    "10087": "force_pass",
    "10088": "force_pass",
    "10089": "force_pass",
    "10090": "force_pass",
    "10426": "force_pass",
    "10427": "force_pass",
    "10452": "force_pass",
    "10453": "force_pass",
    "10465": "force_pass",
    "10466": "force_pass",
    "10467": "force_pass",
    "10468": "force_pass",
    "10469": "force_pass",
    "10470": "force_pass",
    "10471": "force_pass",
    "10472": "force_pass"
  }
}
```

- [ ] **Step 4: Run the unit tests and then build the real final collision file**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
python3 -m unittest tests.test_build_falan_collision_from_rules -v
python3 tools/build_falan_collision_from_rules.py
```

Expected:

```text
Ran 4 tests in ...
OK
saved: /Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final.json
saved: /Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final-summary.json
```

- [ ] **Step 5: Commit the generator and initial rules**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
git add \
  tools/build_falan_collision_from_rules.py \
  assets/falan/map/collision-rules-by-object-id.json \
  assets/falan/map/map-1000-collision-final.json \
  assets/falan/map/map-1000-collision-final-summary.json \
  tests/test_build_falan_collision_from_rules.py
git commit -m "feat: generate final Falan collision from object id rules"
```

### Task 3: Add A Visual Preview And Switch The Browser To The New Final Collision File

**Files:**
- Modify: `/Users/chujianhe/.openclaw/workspace-taizi/tools/build_falan_collision_from_rules.py`
- Modify: `/Users/chujianhe/.openclaw/workspace-taizi/index.html`
- Create: `/Users/chujianhe/.openclaw/workspace-taizi/output/falan-collision-final-preview.svg`
- Test: `/Users/chujianhe/.openclaw/workspace-taizi/tests/test_build_falan_collision_from_rules.py`

- [ ] **Step 1: Add a failing test for preview export**

Append to `/Users/chujianhe/.openclaw/workspace-taizi/tests/test_build_falan_collision_from_rules.py`:

```python
    def test_svg_preview_contains_blocked_cells(self):
        from tools.build_falan_collision_from_rules import render_collision_preview_svg

        svg = render_collision_preview_svg(
            width=2,
            height=2,
            flags=[0, 1, 1, 0],
            cell_size=8,
        )

        self.assertIn("<svg", svg)
        self.assertIn("fill=\"#d63a34\"", svg)
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
python3 -m unittest tests.test_build_falan_collision_from_rules -v
```

Expected:

```text
AttributeError: module 'tools.build_falan_collision_from_rules' has no attribute 'render_collision_preview_svg'
```

- [ ] **Step 3: Implement SVG preview export and point the browser to the final file**

Append to `/Users/chujianhe/.openclaw/workspace-taizi/tools/build_falan_collision_from_rules.py`:

```python
PREVIEW_PATH = ROOT / "output" / "falan-collision-final-preview.svg"


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
```

Update `main()` in `/Users/chujianhe/.openclaw/workspace-taizi/tools/build_falan_collision_from_rules.py`:

```python
    svg = render_collision_preview_svg(payload["width"], payload["height"], payload["flags"])
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW_PATH.write_text(svg, encoding="utf-8")
    print(f"saved: {PREVIEW_PATH}")
```

Update `/Users/chujianhe/.openclaw/workspace-taizi/index.html`:

```javascript
const MAP_COLLISION_JSON = './assets/falan/map/map-1000-collision-final.json';
```

- [ ] **Step 4: Re-run tests, rebuild collision, and verify the browser wiring**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
python3 -m unittest tests.test_build_falan_collision_from_rules -v
python3 tools/build_falan_collision_from_rules.py
rg -n "map-1000-collision-final.json" index.html
```

Expected:

```text
OK
saved: /Users/chujianhe/.openclaw/workspace-taizi/output/falan-collision-final-preview.svg
const MAP_COLLISION_JSON = './assets/falan/map/map-1000-collision-final.json';
```

- [ ] **Step 5: Commit the output switch**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
git add \
  tools/build_falan_collision_from_rules.py \
  output/falan-collision-final-preview.svg \
  index.html \
  tests/test_build_falan_collision_from_rules.py
git commit -m "feat: switch Falan to final offline collision file"
```

### Task 4: Update Documentation And Do End-To-End Verification

**Files:**
- Modify: `/Users/chujianhe/.openclaw/workspace-taizi/docs/falan-collision-and-coords.md`
- Modify: `/Users/chujianhe/.openclaw/workspace-taizi/docs/falan-runtime-architecture.md`
- Modify: `/Users/chujianhe/.openclaw/workspace-taizi/VERSION`
- Modify: `/Users/chujianhe/.openclaw/workspace-taizi/manifest.webmanifest`
- Modify: `/Users/chujianhe/.openclaw/workspace-taizi/sw.js`
- Test: `/Users/chujianhe/.openclaw/workspace-taizi/tools/check_falan_obstacle_overlay.py`

- [ ] **Step 1: Update the docs to describe the new collision source**

Update `/Users/chujianhe/.openclaw/workspace-taizi/docs/falan-collision-and-coords.md` so section 5 says:

```markdown
## 5. 当前碰撞来源

当前碰撞直接来自：

- `/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final.json`

它由离线脚本读取：

- `map-1000.json`
- `falan-city-1000-manifest.json`
- `collision-rules-by-object-id.json`

生成，不再把 `map-1000.json.flags` 直接当最终真相。
```

Update `/Users/chujianhe/.openclaw/workspace-taizi/docs/falan-runtime-architecture.md` so the collision section says:

```markdown
- 碰撞：读取 `map-1000-collision-final.json`
- 生成链：ground ∩ 原始 flags，再由中间层 object id 规则修正
- 天空层 object 永远不参与碰撞
```

- [ ] **Step 2: Bump the build version and cache version**

Update:

- `/Users/chujianhe/.openclaw/workspace-taizi/VERSION`
- `/Users/chujianhe/.openclaw/workspace-taizi/manifest.webmanifest`
- `/Users/chujianhe/.openclaw/workspace-taizi/index.html`
- `/Users/chujianhe/.openclaw/workspace-taizi/sw.js`

Use the same pattern as current releases; if current version is `4.43`, change to:

```text
4.44
```

and update:

```javascript
const FALAN_BUILD_VERSION = '4.44';
await navigator.serviceWorker.register('./sw.js?v=427', { scope: './' });
const SHELL_CACHE = 'falan-shell-v427';
const RUNTIME_CACHE = 'falan-runtime-v427';
```

- [ ] **Step 3: Run full verification**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
python3 -m unittest tests.test_build_falan_collision_from_rules -v
python3 tools/build_falan_collision_from_rules.py
python3 tools/check_falan_obstacle_overlay.py
git diff --check
```

Expected:

```text
OK
saved: /Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final.json
PASS: obstacle overlay layer is enabled
```

- [ ] **Step 4: Verify in the browser**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
curl -s 'http://127.0.0.1:8766/?falan_nocache=1' | rg -n "map-1000-collision-final.json|FALAN_BUILD_VERSION = '4.44'"
```

Expected:

```text
const MAP_COLLISION_JSON = './assets/falan/map/map-1000-collision-final.json';
const FALAN_BUILD_VERSION = '4.44';
```

- [ ] **Step 5: Commit the final documentation and version bump**

Run:

```bash
cd /Users/chujianhe/.openclaw/workspace-taizi
git add \
  docs/falan-collision-and-coords.md \
  docs/falan-runtime-architecture.md \
  VERSION \
  manifest.webmanifest \
  sw.js \
  index.html
git commit -m "docs: document final Falan collision pipeline"
```

## Self-Review

- Spec coverage: covered baseline intersection, mid-only object rules, sky exclusion, offline generation, front-end switch, and verification.
- Placeholder scan: no pending placeholders; all steps include file paths, commands, and code.
- Type consistency: the plan consistently uses `build_base_walkable`, `partition_mid_and_sky_items`, `apply_mid_object_rules`, and `build_final_collision_payload`.
