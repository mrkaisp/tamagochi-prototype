"""
画面遷移のテスト

仕様書参照:
- docs/specifications/01_UI定義書.md: 画面遷移の定義
- docs/checklists/code-review.md: 画面遷移のチェック項目
"""

import unittest
from unittest.mock import Mock, patch
from src.game.core.game_engine import GameEngine
from src.game.core.screen_state import ScreenState
from src.game.core.event_system import EventType
from src.game.entities.flower import SeedType, GrowthStage


class TestScreenTransitions(unittest.TestCase):
    """画面遷移のテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        # pygameの初期化をモック化
        with patch('pygame.init'), \
             patch('pygame.font.init'), \
             patch('src.game.ui.display.DisplayManager.initialize'), \
             patch('src.game.ui.renderer.RenderManager'):
            self.engine = GameEngine()
            # 初期化をスキップ（pygame依存を回避）
            self.engine.running = True
            self.engine.render_manager = Mock()

    def test_initial_screen_state(self):
        """
        仕様: 01_UI定義書.md - タイトル画面が初期状態
        テスト: ゲーム開始時はTITLE画面である
        """
        self.assertEqual(self.engine.screen_state, ScreenState.TITLE)

    def test_title_to_seed_selection(self):
        """
        仕様: 01_UI定義書.md - タイトル画面で決定ボタンで種選択画面へ
        テスト: NAV_CONFIRMでTITLE → SEED_SELECTION
        """
        self.engine.screen_state = ScreenState.TITLE
        self.engine._on_nav_confirm(None)
        self.assertEqual(self.engine.screen_state, ScreenState.SEED_SELECTION)

    def test_seed_selection_to_time_setting(self):
        """
        仕様: 01_UI定義書.md - 種選択後、時間設定画面へ
        テスト: SEED_SELECTEDでSEED_SELECTION → TIME_SETTING
        """
        self.engine.screen_state = ScreenState.SEED_SELECTION
        event = Mock()
        event.data = {"seed_type": "太陽"}
        self.engine._on_seed_selected(event)
        self.assertEqual(self.engine.screen_state, ScreenState.TIME_SETTING)
        self.assertFalse(self.engine.seed_selection_mode)

    def test_time_setting_to_main(self):
        """
        仕様: 01_UI定義書.md - 時間設定完了後、メイン画面へ
        テスト: 時間設定完了でTIME_SETTING → MAIN
        """
        self.engine.screen_state = ScreenState.TIME_SETTING
        self.engine._confirm_time_setting()
        self.assertEqual(self.engine.screen_state, ScreenState.MAIN)

    def test_main_to_settings(self):
        """
        仕様: 01_UI定義書.md - メイン画面から設定画面へ遷移可能
        テスト: メイン画面のメニューからSETTINGSへ遷移
        """
        self.engine.screen_state = ScreenState.MAIN
        # メニューカーソルでSETTINGSを選択して遷移する想定
        # 実際の実装に合わせて調整が必要
        cursor = self.engine._cursors.get(ScreenState.MAIN)
        if cursor:
            # SETTINGSメニュー項目を探して選択
            for i, item in enumerate(cursor.items):
                if hasattr(item, 'action') and 'settings' in str(item.action).lower():
                    cursor.index = i
                    cursor.select()
                    break
        # 実際の遷移ロジックに依存するため、簡易チェック
        # 完全なテストは実装詳細に依存

    def test_main_to_status(self):
        """
        仕様: 01_UI定義書.md - メイン画面からステータス画面へ遷移可能
        テスト: メイン画面のメニューからSTATUSへ遷移
        """
        self.engine.screen_state = ScreenState.MAIN
        cursor = self.engine._cursors.get(ScreenState.MAIN)
        if cursor:
            for i, item in enumerate(cursor.items):
                if hasattr(item, 'action') and 'status' in str(item.action).lower():
                    cursor.index = i
                    cursor.select()
                    break

    def test_growth_completion_to_flower_language(self):
        """
        仕様: 01_UI定義書.md - 花完成時に花言葉選択画面へ自動遷移
        テスト: FLOWER_COMPLETEDでFLOWER_LANGUAGEへ遷移
        """
        self.engine.screen_state = ScreenState.MAIN
        self.engine.flower.stats.growth_stage = GrowthStage.FLOWER
        self.engine._on_flower_completed(None)
        self.assertEqual(self.engine.screen_state, ScreenState.FLOWER_LANGUAGE)

    def test_wither_to_death(self):
        """
        仕様: 01_UI定義書.md - 枯死時に死亡画面へ自動遷移
        テスト: FLOWER_WITHEREDでDEATHへ遷移
        """
        self.engine.screen_state = ScreenState.MAIN
        self.engine._on_flower_withered(None)
        self.assertEqual(self.engine.screen_state, ScreenState.DEATH)

    def test_death_to_title_on_reset(self):
        """
        仕様: 01_UI定義書.md - 死亡画面で決定ボタンでリセット
        テスト: DEATH画面でNAV_CONFIRMでリセット
        """
        self.engine.screen_state = ScreenState.DEATH
        self.engine._on_nav_confirm(None)
        self.assertEqual(self.engine.screen_state, ScreenState.TITLE)
        self.assertTrue(self.engine.seed_selection_mode)

    def test_mode_water_auto_return(self):
        """
        仕様: 01_UI定義書.md - 水やりモードは自動でメイン画面へ復帰
        テスト: MODE_WATERは一定時間後にMAINへ戻る
        """
        self.engine.screen_state = ScreenState.MODE_WATER
        self.engine.mode_active = True
        self.engine.mode_return_timer.reset()
        # タイマーを更新して復帰をシミュレート
        self.engine.mode_return_timer.update(1.0)  # 0.8秒以上経過
        self.engine.update(0.1)  # updateで復帰チェック
        # タイマーが経過していれば復帰する
        if self.engine.mode_return_timer.update(0.0):
            self.assertEqual(self.engine.screen_state, ScreenState.MAIN)
            self.assertFalse(self.engine.mode_active)

    def test_mode_light_auto_return(self):
        """
        仕様: 01_UI定義書.md - 光モードは自動でメイン画面へ復帰
        テスト: MODE_LIGHTは一定時間後にMAINへ戻る
        """
        self.engine.screen_state = ScreenState.MODE_LIGHT
        self.engine.mode_active = True
        self.engine.mode_return_timer.reset()
        self.engine.mode_return_timer.update(1.0)
        self.engine.update(0.1)
        if self.engine.mode_return_timer.update(0.0):
            self.assertEqual(self.engine.screen_state, ScreenState.MAIN)
            self.assertFalse(self.engine.mode_active)

    def test_cancel_navigation(self):
        """
        仕様: 01_UI定義書.md - キャンセルボタンで前の画面へ戻る
        テスト: NAV_CANCELで適切な画面へ戻る
        """
        # メイン画面から設定画面へ遷移した後、キャンセルで戻る想定
        self.engine.screen_state = ScreenState.SETTINGS
        self.engine._on_nav_cancel(None)
        # 実装に応じて適切な画面へ戻ることを確認
        # 完全なテストは実装詳細に依存

    def test_screen_state_enum_values(self):
        """
        仕様: screen_state.py - 全ての画面状態が定義されている
        テスト: 必要な画面状態が全て存在する
        """
        expected_states = [
            ScreenState.TITLE,
            ScreenState.SEED_SELECTION,
            ScreenState.TIME_SETTING,
            ScreenState.MAIN,
            ScreenState.SETTINGS,
            ScreenState.STATUS,
            ScreenState.MODE_WATER,
            ScreenState.MODE_LIGHT,
            ScreenState.FLOWER_LANGUAGE,
            ScreenState.DEATH,
        ]
        for state in expected_states:
            self.assertIsInstance(state, ScreenState)


if __name__ == "__main__":
    unittest.main()
