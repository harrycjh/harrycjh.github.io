import unittest

from tools.build_falan_object_map_assets import original_to_tiled
from tools.build_falan_collision_from_rules import (
    build_base_walkable,
    build_final_collision_payload,
    collision_grid_index,
    partition_mid_and_sky_items,
    apply_mid_object_rules,
)


class BuildFalanCollisionFromRulesTest(unittest.TestCase):
    def test_build_base_walkable_uses_manifest_tile_layer_non_zero_cells(self):
        tile_layer = [0, 7, 9, 0]

        actual = build_base_walkable(tile_layer)

        self.assertEqual(actual, [0, 1, 1, 0])

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

    def test_apply_mid_object_rules_defaults_to_block_and_force_pass_clears(self):
        cols = 4
        rows = 4
        base = [0] * (cols * rows)

        assets = {
            "100": {"flag": 0, "areaE": 1, "areaS": 1},
            "101": {"flag": 0, "areaE": 3, "areaS": 3},
        }
        items = [
            [1, 1, 100],
            [0, 0, 101],
        ]
        rules = {
            "default": "force_block",
            "rules": {
                "100": "force_pass",
            },
        }

        actual, summary = apply_mid_object_rules(base, items, assets, rules, cols, rows)

        self.assertEqual(actual[collision_grid_index(1, 1, cols)], 0)
        self.assertEqual(actual[collision_grid_index(0, 0, cols)], 1)
        self.assertEqual(actual[collision_grid_index(2, 2, cols)], 0)
        self.assertEqual(
            summary,
            {"forcePassObjects": 1, "forceBlockObjects": 0, "defaultBlockedObjects": 1},
        )

    def test_end_to_end_generation_uses_manifest_tile_layer_and_skips_sky(self):
        cols = 3
        rows = 3
        manifest = {
            "rows": rows,
            "cols": cols,
            "tileLayer": [
                1, 1, 1,
                1, 0, 1,
                1, 1, 1,
            ],
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
            "default": "force_block",
            "rules": {"100": "force_pass", "200": "force_block"},
        }

        payload, summary = build_final_collision_payload(manifest, rules)

        self.assertEqual(payload["width"], 3)
        self.assertEqual(payload["height"], 3)
        self.assertEqual(payload["flags"][collision_grid_index(1, 1, cols)], 0)
        self.assertEqual(payload["flags"][collision_grid_index(2, 2, cols)], 0)
        self.assertEqual(summary["skySkipped"], 1)
        self.assertEqual(summary["midProcessed"], 1)

    def test_end_to_end_generation_emits_blocked_flags_from_tile_layer(self):
        manifest = {
            "rows": 2,
            "cols": 2,
            "tileLayer": [1, 1, 0, 1],
            "assets": {},
            "objectItems": [],
        }
        rules = {
            "default": "force_block",
            "rules": {},
        }

        payload, summary = build_final_collision_payload(manifest, rules)

        self.assertEqual(payload["flags"], [0, 0, 1, 0])
        self.assertEqual(summary["baseBlocked"], 1)
        self.assertEqual(summary["finalBlocked"], 1)
        self.assertEqual(summary["defaultBlockedObjects"], 0)

    def test_end_to_end_generation_blocks_mid_by_default_without_area_expansion(self):
        manifest = {
            "rows": 2,
            "cols": 2,
            "tileLayer": [1, 1, 1, 1],
            "assets": {
                "100": {"flag": 0, "areaE": 3, "areaS": 3},
            },
            "objectItems": [
                [1, 0, 100],
            ],
        }
        rules = {
            "default": "force_block",
            "rules": {},
        }

        payload, summary = build_final_collision_payload(manifest, rules)

        self.assertEqual(payload["flags"][collision_grid_index(1, 0, 2)], 1)
        self.assertEqual(payload["flags"][collision_grid_index(0, 0, 2)], 0)
        self.assertEqual(payload["flags"][collision_grid_index(1, 1, 2)], 0)
        self.assertEqual(summary["defaultBlockedObjects"], 1)

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

    def test_collision_grid_index_inverts_original_to_tiled(self):
        width = 300
        for idx in [0, 1, 17, 299, 300, 301, 45149, 89999]:
            tx, ty = original_to_tiled(idx, width)
            self.assertEqual(collision_grid_index(tx, ty, width), idx)


if __name__ == "__main__":
    unittest.main()
