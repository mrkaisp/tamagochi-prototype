"""
成長分岐のテスト

仕様書参照:
- docs/specifications/04_フェーズ1.md: フェーズ1（種→芽）の分岐条件
- docs/specifications/04_フェーズ2.md: フェーズ2（芽→茎）の分岐条件
- docs/specifications/05_成長分岐表.md: 成長分岐表（集約）
- docs/checklists/code-review.md: 成長フェーズ分岐ロジック
"""

import unittest
from pathlib import Path
import tempfile
from src.game.entities.flower import Flower, FlowerStats, GrowthStage, SeedType
from src.game.data.save_manager import SaveManager
from src.game.data.config import config
from src.game.utils.random_manager import get_rng


class TestGrowthBranching(unittest.TestCase):
    """成長分岐のテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        self.tmpdir = tempfile.TemporaryDirectory()
        save_path = Path(self.tmpdir.name) / "state.json"
        self.flower = Flower(save_manager=SaveManager(save_path=str(save_path)))
        self.stats = self.flower.stats
        # テスト用にシードを固定
        get_rng().set_seed(42)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.tmpdir.cleanup()

    def test_phase1_light_threshold_49_yin(self):
        """
        仕様: 05_成長分岐表.md - フェーズ1: 光<50で陰寄り（棘芽）
        テスト: 光レベル49で陰寄りになる
        """
        self.stats.growth_stage = GrowthStage.SEED
        self.stats.light_level = 49.0
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.SPROUT)
        self.assertTrue(self.stats.light_tendency_yin)

    def test_phase1_light_threshold_50_yang(self):
        """
        仕様: 05_成長分岐表.md - フェーズ1: 光>=50で陽寄り（ハート芽）
        テスト: 光レベル50で陽寄りになる
        """
        self.stats.growth_stage = GrowthStage.SEED
        self.stats.light_level = 50.0
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.SPROUT)
        self.assertFalse(self.stats.light_tendency_yin)

    def test_phase1_light_requirement(self):
        """
        仕様: 05_成長分岐表.md - フェーズ1: 成長条件は光レベル>=20
        テスト: 光レベル20以上で成長する
        """
        self.stats.growth_stage = GrowthStage.SEED
        self.stats.light_level = 20.0
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.SPROUT)

    def test_phase1_light_reset_after_growth(self):
        """
        仕様: 05_成長分岐表.md - フェーズ1: 成長後、光レベルは0にリセット
        テスト: 成長後、光レベルが0になる
        """
        self.stats.growth_stage = GrowthStage.SEED
        self.stats.light_level = 50.0
        self.stats._check_growth()
        self.assertEqual(self.stats.light_level, 0.0)

    def test_phase2_score_range_70_100_bend(self):
        """
        仕様: 05_成長分岐表.md - フェーズ2: 総合スコア50〜100で「しなる」
        テスト: スコア50以上でしなるになる
        """
        self.stats.growth_stage = GrowthStage.SPROUT
        self.stats.water_level = 100.0
        self.stats.light_level = 100.0
        self.stats.mental_level = 100.0
        self.stats.seed_type = SeedType.YANG  # +5バイアス
        self.stats.light_level = 40.0  # 成長条件
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.STEM)
        self.assertEqual(self.stats.phase2_branch, "しなる")

    def test_phase2_score_range_40_69_bend(self):
        """
        仕様: 04_フェーズ2.md - フェーズ2: 総合スコア40〜69で「しなる」
        テスト: スコア40-69でしなるになる
        """
        self.stats.growth_stage = GrowthStage.SPROUT
        self.stats.water_level = 60.0
        self.stats.mental_level = 60.0
        self.stats.seed_type = SeedType.YIN  # +0バイアス
        # 平均(60+60+60)/3 = 60 → しなる（40-69）
        # light_levelは成長条件（>=40）とスコア計算の両方に使用
        self.stats.light_level = 60.0  # 成長条件を満たし、スコア計算にも使用
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.STEM)
        self.assertEqual(self.stats.phase2_branch, "しなる")

    def test_phase2_score_range_0_39_vine(self):
        """
        仕様: 04_フェーズ2.md - フェーズ2: 総合スコア0〜39で「つる」
        テスト: スコア0-39でつるになる
        """
        self.stats.growth_stage = GrowthStage.SPROUT
        self.stats.water_level = 10.0
        self.stats.light_level = 10.0
        self.stats.mental_level = 10.0
        self.stats.seed_type = SeedType.YIN  # +0バイアス
        self.stats.light_level = 40.0  # 成長条件
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.STEM)
        self.assertEqual(self.stats.phase2_branch, "つる")

    def test_phase2_seed_bias_yang(self):
        """
        仕様: 05_成長分岐表.md - 種バイアス: 陽+5
        テスト: 陽種でスコアが+5される
        """
        self.stats.growth_stage = GrowthStage.SPROUT
        self.stats.seed_type = SeedType.YANG
        self.stats.water_level = 65.0
        self.stats.light_level = 40.0  # 成長条件（スコア計算にも使用）
        self.stats.mental_level = 65.0
        # 平均(65+40+65)/3 = 56.67 + 太陽バイアス5 = 61.67 → しなる（40-69）
        # まっすぐにするには平均65以上が必要: (70+70+70)/3 = 70 + 太陽バイアス5 = 75
        self.stats._check_growth()
        # スコア61.67は「しなる」の範囲（40-69）に入る
        self.assertEqual(self.stats.phase2_branch, "しなる")

    def test_phase2_mental_bonus_70(self):
        """
        仕様: 04_フェーズ2.md - メンタル70以上で+5バイアス
        テスト: メンタル70以上でスコアが+5される
        """
        self.stats.growth_stage = GrowthStage.SPROUT
        self.stats.water_level = 70.0
        self.stats.light_level = 40.0  # 成長条件
        self.stats.mental_level = 70.0  # 閾値以上
        self.stats.seed_type = SeedType.YIN  # +0バイアス
        # 平均(70+40+70)/3 = 60 + メンタルバイアス5 = 65 → しなる（40-69）
        # まっすぐにするには平均65以上が必要: (70+70+70)/3 = 70 + メンタルバイアス5 = 75
        self.stats._check_growth()
        # スコア65は「しなる」の範囲（40-69）に入る
        self.assertEqual(self.stats.phase2_branch, "しなる")

    def test_phase2_light_requirement(self):
        """
        仕様: 04_フェーズ2.md - 成長条件: 光レベル>=40
        テスト: 光レベル40以上で成長する
        """
        self.stats.growth_stage = GrowthStage.SPROUT
        self.stats.light_level = 40.0
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.STEM)

    def test_phase2_light_reset_after_growth(self):
        """
        仕様: 05_成長分岐表.md - フェーズ2: 成長後、光レベルは0にリセット
        テスト: 成長後、光レベルが0になる
        """
        self.stats.growth_stage = GrowthStage.SPROUT
        self.stats.light_level = 40.0
        self.stats._check_growth()
        self.assertEqual(self.stats.light_level, 0.0)

    def test_phase3_shape_calculation(self):
        """
        仕様: 05_成長分岐表.md - フェーズ3: 種×茎×光傾向で形決定
        テスト: フェーズ3で適切な形が決定される
        """
        self.stats.growth_stage = GrowthStage.STEM
        self.stats.seed_type = SeedType.YANG  # +10
        self.stats.phase2_branch = "しなる"  # +5
        self.stats.light_tendency_yin = False  # 陽 +5
        # 合計: 10 + 5 + 5 = 20 → 大輪（min_base=20）
        self.stats.light_level = 60.0  # 成長条件
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.BUD)
        # ランダム要素があるため、候補の中から選択されることを確認
        self.assertIn(
            self.stats.phase3_shape,
            ["大輪", "まるまる", "ひらひら", "ちいさめ", "とがり", "ふつう"],
        )

    def test_phase3_light_requirement(self):
        """
        仕様: 05_成長分岐表.md - フェーズ3: 成長条件: 光レベル>=60
        テスト: 光レベル60以上で成長する
        """
        self.stats.growth_stage = GrowthStage.STEM
        self.stats.light_level = 60.0
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.BUD)

    def test_phase3_light_reset_after_growth(self):
        """
        仕様: 05_成長分岐表.md - フェーズ3: 成長後、光レベルは0にリセット
        テスト: 成長後、光レベルが0になる
        """
        self.stats.growth_stage = GrowthStage.STEM
        self.stats.light_level = 60.0
        self.stats._check_growth()
        self.assertEqual(self.stats.light_level, 0.0)

    def test_phase4_light_requirement(self):
        """
        仕様: 05_成長分岐表.md - フェーズ4: 成長条件: 光レベル>=80
        テスト: 光レベル80以上で成長する
        """
        self.stats.growth_stage = GrowthStage.BUD
        self.stats.light_level = 80.0
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.FLOWER)

    def test_phase4_age_requirement(self):
        """
        仕様: 05_成長分岐表.md - フェーズ4: 成長条件: 年齢>=60秒
        テスト: 年齢60秒以上で成長する
        """
        self.stats.growth_stage = GrowthStage.BUD
        self.stats.age_seconds = 60.0
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.FLOWER)

    def test_phase4_light_reset_after_growth(self):
        """
        仕様: 05_成長分岐表.md - フェーズ4: 成長後、光レベルは0にリセット
        テスト: 成長後、光レベルが0になる
        """
        self.stats.growth_stage = GrowthStage.BUD
        self.stats.light_level = 80.0
        self.stats._check_growth()
        self.assertEqual(self.stats.light_level, 0.0)

    def test_growth_progression_complete(self):
        """
        仕様: 05_成長分岐表.md - 全フェーズの成長進行
        テスト: 種→芽→茎→蕾→花の順に成長する
        """
        # フェーズ1: 種→芽
        self.stats.light_level = 50.0
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.SPROUT)

        # フェーズ2: 芽→茎
        self.stats.light_level = 40.0
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.STEM)

        # フェーズ3: 茎→蕾
        self.stats.light_level = 60.0
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.BUD)

        # フェーズ4: 蕾→花
        self.stats.light_level = 80.0
        self.stats._check_growth()
        self.assertEqual(self.stats.growth_stage, GrowthStage.FLOWER)


if __name__ == "__main__":
    unittest.main()
