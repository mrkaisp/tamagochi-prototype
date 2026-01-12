"""
栄養行為制約のテスト

仕様書参照:
- docs/checklists/code-review.md: 1時間内の連続栄養行為：同一時間で3回目以降は効果無効
- docs/specifications/01_UI定義書.md: 栄養行為の制限
"""

import unittest
from unittest.mock import Mock, patch
from src.game.core.game_engine import GameEngine
from src.game.core.screen_state import ScreenState
from src.game.data.config import config


class TestNutritionConstraints(unittest.TestCase):
    """栄養行為制約のテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        with patch('pygame.init'), \
             patch('pygame.font.init'), \
             patch('src.game.ui.display.DisplayManager.initialize'), \
             patch('src.game.ui.renderer.RenderManager'):
            self.engine = GameEngine()
            self.engine.running = True
            self.engine.render_manager = Mock()
            # テスト用に制限を有効化
            config.game.nutrition_limit_disabled = False
            self.engine._nutrition_action_limit = 3
            self.engine._nutrition_actions_in_current_hour = 0
            self.engine._last_action_hour = 0

    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 設定をリセット
        config.game.nutrition_limit_disabled = True

    def test_nutrition_limit_initial_state(self):
        """
        仕様: code-review.md - 栄養行為は1時間に3回まで
        テスト: 初期状態では3回まで可能
        """
        self.assertTrue(self.engine._can_perform_nutrition_action())
        self.assertEqual(self.engine._nutrition_remaining_cached, 3)

    def test_nutrition_action_counting(self):
        """
        仕様: code-review.md - 同一時間内で3回目以降は効果無効
        テスト: 栄養行為を実行するとカウントが増える
        """
        initial_count = self.engine._nutrition_actions_in_current_hour
        self.engine._on_nutrition_action()
        self.assertEqual(
            self.engine._nutrition_actions_in_current_hour, initial_count + 1
        )
        self.assertEqual(self.engine._nutrition_remaining_cached, 2)

    def test_nutrition_limit_enforcement(self):
        """
        仕様: code-review.md - 3回目以降は効果無効
        テスト: 3回実行後は4回目が無効になる
        """
        # 1回目と2回目は有効
        self.engine._on_nutrition_action()
        self.assertTrue(self.engine._can_perform_nutrition_action())
        self.engine._on_nutrition_action()
        self.assertTrue(self.engine._can_perform_nutrition_action())
        
        # 3回目は最後の有効な実行
        self.engine._on_nutrition_action()
        # 3回目実行後は制限に達する
        self.assertFalse(self.engine._can_perform_nutrition_action())
        self.assertEqual(self.engine._nutrition_remaining_cached, 0)

    def test_nutrition_limit_reset_on_hour_change(self):
        """
        仕様: code-review.md - 1時間ごとにリセット
        テスト: ゲーム内時間が1時間経過するとカウントがリセットされる
        """
        # 3回実行して制限に達する
        for _ in range(3):
            self.engine._on_nutrition_action()
        self.assertFalse(self.engine._can_perform_nutrition_action())

        # ゲーム内時間を1時間進める
        self.engine.flower.stats.age_seconds = 3600.0  # 1時間
        self.engine.update(0.1)  # updateで時間チェック

        # カウントがリセットされている
        self.assertEqual(self.engine._nutrition_actions_in_current_hour, 0)
        self.assertTrue(self.engine._can_perform_nutrition_action())
        self.assertEqual(self.engine._nutrition_remaining_cached, 3)

    def test_fertilizer_action_respects_limit(self):
        """
        仕様: code-review.md - 肥料も栄養行為としてカウント
        テスト: 肥料を与える際も制限が適用される
        """
        self.engine.screen_state = ScreenState.MAIN
        initial_water = self.engine.flower.stats.water_level

        # 3回まで実行可能
        for i in range(3):
            event = Mock()
            self.engine._on_fertilizer(event)
            self.assertGreater(self.engine.flower.stats.water_level, initial_water)

        # 4回目は無効
        event = Mock()
        self.engine._on_fertilizer(event)
        # 水レベルは変化しない（無効メッセージが表示される）
        self.assertIn("栄養行為は同一時間内で3回まで", self.engine._invalid_message)

    def test_water_action_respects_limit(self):
        """
        仕様: code-review.md - 水やりも栄養行為としてカウント
        テスト: 水やりも制限が適用される
        """
        self.engine.screen_state = ScreenState.MAIN
        # 水レベルを低く設定（90未満にする）
        self.engine.flower.stats.water_level = 50.0

        # 3回まで実行可能
        for i in range(3):
            initial_water = self.engine.flower.stats.water_level
            self.engine._perform_water()
            # 水レベルが90未満の場合は増加する
            if initial_water < 90:
                self.assertGreater(self.engine.flower.stats.water_level, initial_water)
            # 水レベルをリセット（90未満に保つ）
            self.engine.flower.stats.water_level = 50.0

        # 4回目は無効（制限に達している）
        self.engine.flower.stats.water_level = 50.0  # リセット
        self.engine._perform_water()
        # 無効メッセージが表示される
        self.assertIn("栄養行為は同一時間内で3回まで", self.engine._invalid_message)

    def test_nutrition_limit_disabled_option(self):
        """
        仕様: config.py - テスト用オプションで制限を無効化可能
        テスト: nutrition_limit_disabled=Trueで制限が無効になる
        """
        config.game.nutrition_limit_disabled = True

        # 3回実行後も有効
        for _ in range(3):
            self.engine._on_nutrition_action()
        self.assertTrue(self.engine._can_perform_nutrition_action())

        # さらに実行しても有効
        self.engine._on_nutrition_action()
        self.assertTrue(self.engine._can_perform_nutrition_action())

    def test_info_message_on_nutrition_action(self):
        """
        仕様: game_engine.py - 栄養行為時に残り回数を表示
        テスト: 栄養行為時に情報メッセージが表示される
        """
        self.engine._on_nutrition_action()
        self.assertIn("あと", self.engine._info_message)
        self.assertIn("回まで栄養行為が可能", self.engine._info_message)

    def test_info_message_on_limit_reached(self):
        """
        仕様: game_engine.py - 制限到達時にメッセージ表示
        テスト: 3回実行後は「今はこれ以上栄養行為ができません」と表示
        """
        for _ in range(3):
            self.engine._on_nutrition_action()
        self.assertIn("今はこれ以上栄養行為ができません", self.engine._info_message)


if __name__ == "__main__":
    unittest.main()
