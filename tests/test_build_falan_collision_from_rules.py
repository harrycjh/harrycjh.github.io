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
