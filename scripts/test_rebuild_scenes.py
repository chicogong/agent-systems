"""Keep the checked-in figure generators covered by the shared rebuild command."""

import unittest

from rebuild_scenes import BUILDERS, ROOT


class RebuildSceneCoverageTests(unittest.TestCase):
    def test_kimi_nonstandard_generator_is_included(self):
        self.assertIn(ROOT / "figures/kimi-code/build_scene.py", BUILDERS)

    def test_all_declared_local_generators_are_covered_once(self):
        local_builders = {
            builder
            for pattern in ("*/build.py", "*/build_scene.py")
            for builder in (ROOT / "figures").glob(pattern)
        }
        selected = [builder for builder in BUILDERS if builder.parent.parent == ROOT / "figures"]
        self.assertEqual(set(selected), local_builders)
        self.assertEqual(len(selected), len(set(selected)))

    def test_every_scene_has_a_known_generator(self):
        special = {
            "pi-architecture": ROOT / "scripts/build_pi_figures.py",
            "pi-extensions": ROOT / "scripts/build_pi_figures.py",
        }
        for scene in (ROOT / "figures").glob("*/scene.excalidraw"):
            with self.subTest(figure=scene.parent.name):
                if scene.parent.name in special:
                    self.assertIn(special[scene.parent.name], BUILDERS)
                else:
                    self.assertTrue(any(builder.parent == scene.parent for builder in BUILDERS))


if __name__ == "__main__":
    unittest.main()
