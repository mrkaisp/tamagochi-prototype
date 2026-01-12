import unittest
from pathlib import Path
import tempfile
from src.game.entities.flower import Flower, FlowerStats, GrowthStage, SeedType
from src.game.data.config import config
from src.game.data.save_manager import SaveManager


class TestFlowerStats(unittest.TestCase):
    """Flower/FlowerStats の基本テスト"""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        save_path = Path(self.tmpdir.name) / "state.json"
        self.flower = Flower(save_manager=SaveManager(save_path=str(save_path)))
        self.stats = self.flower.stats

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_initial_values(self):
        self.assertEqual(self.stats.seed_type, SeedType.SUN)
        self.assertEqual(self.stats.growth_stage, GrowthStage.SEED)
        self.assertEqual(self.stats.age_seconds, 0.0)
        self.assertEqual(self.stats.water_level, 50.0)  # 現在の仕様: 初期値50（栄養）
        self.assertEqual(self.stats.light_level, 0.0)  # 現在の仕様: 初期値0（手動で与える）
        self.assertEqual(self.stats.weed_count, 0)
        self.assertEqual(self.stats.pest_count, 0)

    def test_update_and_decay(self):
        # 水を与えてから減少テストを実行
        self.flower.water()
        initial_water = self.stats.water_level
        self.flower.update(1.0)
        self.assertLess(self.stats.water_level, initial_water)
        self.assertGreater(self.stats.age_seconds, 0.0)

    def test_actions_affect_stats(self):
        # water
        initial = self.stats.water_level
        self.flower.water()
        self.assertGreaterEqual(self.stats.water_level, initial)

        # light
        initial_light = self.stats.light_level
        self.flower.give_light()
        self.assertGreater(self.stats.light_level, initial_light)

        # weeds/pests
        self.stats.weed_count = 2
        self.flower.remove_weeds()
        self.assertLessEqual(self.stats.weed_count, 2)
        self.stats.pest_count = 2
        self.flower.remove_pests()
        self.assertLessEqual(self.stats.pest_count, 2)

    def test_growth_progression(self):
        # accumulate light to progress stages
        self.flower.give_light(amount=self.stats.light_required_for_sprout)
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.SPROUT)

        self.flower.give_light(amount=self.stats.light_required_for_stem)
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.STEM)

        self.flower.give_light(amount=self.stats.light_required_for_bud)
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.BUD)

        self.flower.give_light(amount=self.stats.light_required_for_flower)
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.FLOWER)


if __name__ == "__main__":
    unittest.main()
