import pygame as pg
from typing import Dict, Any  # Removed Optional
from ..entities.flower import Flower
from ..core.event_system import EventManager, EventType
from ..core.input_handler import InputHandler
from ..ui.display import DisplayManager
from ..ui.renderer import RenderManager
from ..data.config import config
from ..utils.helpers import Timer
from .screen_state import ScreenState

class GameEngine:
    """ゲームエンジンクラス"""
    
    def __init__(self):
        # システムの初期化
        self.event_manager = EventManager()
        self.input_handler = InputHandler(self.event_manager)
        self.display_manager = DisplayManager()
        self.render_manager = None  # 初期化時に作成
        
        # ゲーム状態
        self.flower = Flower()
        self.running = False
        self.paused = False
        self.seed_selection_mode = True  # 互換用フラグ（今後廃止予定）
        self.screen_state = ScreenState.TITLE
        
        # タイマー
        self.fps_timer = Timer(1.0 / config.display.fps, auto_reset=True)
        self.auto_save_timer = Timer(config.data.auto_save_interval, auto_reset=True)
        self.time_scale = 1.0
        self.mode_return_timer = Timer(0.8, auto_reset=False)
        self.mode_active = False
        self.settings_reset_selected = False
        
        # イベントハンドラーの設定
        self._setup_event_handlers()
    
    def _setup_event_handlers(self) -> None:
        """イベントハンドラーを設定"""
        self.event_manager.subscribe(EventType.FLOWER_WATERED, self._on_flower_watered)
        self.event_manager.subscribe(EventType.FLOWER_LIGHT_GIVEN, self._on_flower_light_given)
        self.event_manager.subscribe(EventType.FLOWER_WEEDS_REMOVED, self._on_flower_weeds_removed)
        self.event_manager.subscribe(EventType.FLOWER_PESTS_REMOVED, self._on_flower_pests_removed)
        self.event_manager.subscribe(EventType.SEED_SELECTED, self._on_seed_selected)
        self.event_manager.subscribe(EventType.FLOWER_GROWTH_CHANGED, self._on_flower_growth_changed)
        self.event_manager.subscribe(EventType.FLOWER_WITHERED, self._on_flower_withered)
        self.event_manager.subscribe(EventType.FLOWER_COMPLETED, self._on_flower_completed)
        self.event_manager.subscribe(EventType.GAME_RESET, self._on_game_reset)
    
    def initialize(self) -> bool:
        """ゲームエンジンを初期化"""
        try:
            pg.init()
            # フォントシステムを初期化
            pg.font.init()
            self.display_manager.initialize()
            
            # RenderManagerを初期化（フォント初期化後）
            self.render_manager = RenderManager()
            self.running = True
            return True
        except Exception as e:
            print(f"Game engine initialization failed: {e}")
            return False
    
    def run(self) -> None:
        """ゲームループを実行"""
        clock = pg.time.Clock()
        
        while self.running:
            dt = clock.tick(config.display.fps) / 1000.0
            dt *= self.time_scale
            
            # イベント処理
            if not self.input_handler.handle_events(self.screen_state in (ScreenState.SEED_SELECTION,)):
                self.running = False
                break
            
            if not self.paused:
                # ゲーム状態の更新
                self.update(dt)
            
            # レンダリング
            self.render()
    
    def update(self, dt: float) -> None:
        """ゲーム状態を更新"""
        # メインプレイ中のみ花を更新
        if self.screen_state == ScreenState.MAIN and not self.paused:
            self.flower.update(dt)
        
        # レンダラーを更新
        if self.render_manager:
            self.render_manager.update(dt)
        
        # 自動セーブ
        if self.auto_save_timer.update(dt) and not self.seed_selection_mode:
            self.flower.save()

        # モード画面からの自動復帰
        if self.mode_active and self.mode_return_timer.update(dt):
            self.screen_state = ScreenState.MAIN
            self.mode_active = False
    
    def render(self) -> None:
        """ゲームをレンダリング"""
        # 論理サーフェスを取得
        if self.render_manager:
            logical_surface = self.display_manager.get_logical_surface()
            
            # ゲーム状態を準備
            game_state = {
                'flower_stats': self.flower.stats,
                'needs_attention': self.flower.needs_attention,
                'is_alive': self.flower.is_alive,
                'seed_selection_mode': (self.screen_state == ScreenState.SEED_SELECTION),
                'screen_state': self.screen_state.name,
                'paused': self.paused,
                'time_scale': self.time_scale,
                'settings_reset_selected': self.settings_reset_selected,
            }
            
            # レンダリング
            self.render_manager.render(logical_surface, game_state)
            
            # ディスプレイに表示
            self.display_manager.render()
    
    def pause(self) -> None:
        """ゲームを一時停止"""
        self.paused = True
    
    def resume(self) -> None:
        """ゲームを再開"""
        self.paused = False
    
    def quit(self) -> None:
        """ゲームを終了"""
        self.running = False
        if not self.seed_selection_mode:
            self.flower.save()
        pg.quit()
    
    def reset_game(self) -> None:
        """ゲームをリセット"""
        self.flower.reset()
        self.screen_state = ScreenState.TITLE
        self.seed_selection_mode = True
    
    def get_game_state(self) -> Dict[str, Any]:
        """ゲーム状態を取得"""
        return {
            'flower_stats': self.flower.stats,
            'needs_attention': self.flower.needs_attention,
            'is_alive': self.flower.is_alive,
            'seed_selection_mode': self.seed_selection_mode,
            'paused': self.paused,
            'running': self.running
        }
    
    # イベントハンドラー
    def _on_flower_watered(self, event) -> None:
        """花に水を与えた時の処理"""
        if self.screen_state in (ScreenState.MAIN, ScreenState.MODE_WATER):
            self.flower.water()
            self.screen_state = ScreenState.MODE_WATER
            self.mode_return_timer.reset()
            self.mode_active = True
    
    def _on_flower_light_given(self, event) -> None:
        """花に光を与えた時の処理"""
        if self.screen_state in (ScreenState.MAIN, ScreenState.MODE_LIGHT):
            self.flower.give_light()
            self.screen_state = ScreenState.MODE_LIGHT
            self.mode_return_timer.reset()
            self.mode_active = True
    
    def _on_flower_weeds_removed(self, event) -> None:
        """花の雑草を除去した時の処理"""
        if self.screen_state in (ScreenState.MAIN, ScreenState.MODE_ENV):
            self.flower.remove_weeds()
            self.screen_state = ScreenState.MODE_ENV
            self.mode_return_timer.reset()
            self.mode_active = True
    
    def _on_flower_pests_removed(self, event) -> None:
        """花の害虫を駆除した時の処理"""
        if self.screen_state in (ScreenState.MAIN, ScreenState.MODE_ENV):
            self.flower.remove_pests()
            self.screen_state = ScreenState.MODE_ENV
            self.mode_return_timer.reset()
            self.mode_active = True
    
    def _on_seed_selected(self, event) -> None:
        """種を選択した時の処理"""
        if self.screen_state in (ScreenState.SEED_SELECTION, ScreenState.TITLE):
            from ..entities.flower import SeedType
            seed_type_name = event.data.get("seed_type", "太陽")
            seed_type = SeedType(seed_type_name)
            self.flower.select_seed(seed_type)
            # 次は時間設定へ
            self.screen_state = ScreenState.TIME_SETTING
            self.seed_selection_mode = False
            print(f"{seed_type_name}の種を選択しました。時間設定へ進みます。")
    
    def _on_flower_growth_changed(self, event) -> None:
        """花の成長段階が変化した時の処理"""
        print(f"花が成長しました: {self.flower.stats.growth_stage_display}")
        
        # 花が完成した場合の特別な処理
        if self.flower.stats.is_fully_grown:
            self.event_manager.emit_simple(EventType.FLOWER_COMPLETED)
    
    def _on_flower_withered(self, event) -> None:
        """花が枯れた時の処理"""
        print("花が枯れてしまいました。")
        self.screen_state = ScreenState.DEATH
    
    def _on_flower_completed(self, event) -> None:
        """花が完成した時の処理"""
        print("🌸 花が完成しました！花言葉選択へ。")
        self.screen_state = ScreenState.FLOWER_LANGUAGE
    
    def _on_game_reset(self, event) -> None:
        """ゲームリセットの処理"""
        print("ゲームをリセットします...")
        self.reset_game()
        # ログファイルをリセット
        self._reset_log_file()
        print("新しい花の育成を開始します！")
    
    def _reset_log_file(self) -> None:
        """ログファイルをリセット"""
        import logging
        import os
        
        # 現在のログファイルを削除
        log_file = "flower_game.log"
        if os.path.exists(log_file):
            os.remove(log_file)
        
        # ログハンドラーをリセット
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logger.removeHandler(handler)
        
        # 新しいファイルハンドラーを追加
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        print("ログファイルをリセットしました。")

    # --- 画面ナビゲーション ---
    def _setup_event_handlers(self) -> None:
        """イベントハンドラーを設定"""
        self.event_manager.subscribe(EventType.FLOWER_WATERED, self._on_flower_watered)
        self.event_manager.subscribe(EventType.FLOWER_LIGHT_GIVEN, self._on_flower_light_given)
        self.event_manager.subscribe(EventType.FLOWER_WEEDS_REMOVED, self._on_flower_weeds_removed)
        self.event_manager.subscribe(EventType.FLOWER_PESTS_REMOVED, self._on_flower_pests_removed)
        self.event_manager.subscribe(EventType.SEED_SELECTED, self._on_seed_selected)
        self.event_manager.subscribe(EventType.FLOWER_GROWTH_CHANGED, self._on_flower_growth_changed)
        self.event_manager.subscribe(EventType.FLOWER_WITHERED, self._on_flower_withered)
        self.event_manager.subscribe(EventType.FLOWER_COMPLETED, self._on_flower_completed)
        self.event_manager.subscribe(EventType.GAME_RESET, self._on_game_reset)
        # ナビゲーション
        self.event_manager.subscribe(EventType.NAV_LEFT, self._on_nav_left)
        self.event_manager.subscribe(EventType.NAV_RIGHT, self._on_nav_right)
        self.event_manager.subscribe(EventType.NAV_CONFIRM, self._on_nav_confirm)
        self.event_manager.subscribe(EventType.NAV_CANCEL, self._on_nav_cancel)
        # 時間制御
        self.event_manager.subscribe(EventType.TIME_TOGGLE_PAUSE, self._on_time_toggle_pause)
        self.event_manager.subscribe(EventType.TIME_SPEED_NORMAL, self._on_time_speed_normal)
        self.event_manager.subscribe(EventType.TIME_SPEED_FAST, self._on_time_speed_fast)

    def _on_nav_left(self, event) -> None:
        if self.screen_state == ScreenState.MAIN:
            self.screen_state = ScreenState.SETTINGS
        elif self.screen_state in (ScreenState.SETTINGS, ScreenState.STATUS, ScreenState.MODE_WATER, ScreenState.MODE_LIGHT, ScreenState.MODE_ENV, ScreenState.FLOWER_LANGUAGE, ScreenState.DEATH):
            self.screen_state = ScreenState.MAIN

    def _on_nav_right(self, event) -> None:
        if self.screen_state == ScreenState.MAIN:
            self.screen_state = ScreenState.STATUS
        elif self.screen_state == ScreenState.SETTINGS:
            self.settings_reset_selected = not self.settings_reset_selected

    def _on_nav_confirm(self, event) -> None:
        if self.screen_state == ScreenState.TITLE:
            self.screen_state = ScreenState.SEED_SELECTION
        elif self.screen_state == ScreenState.TIME_SETTING:
            self.screen_state = ScreenState.MAIN
        elif self.screen_state == ScreenState.SETTINGS:
            # 設定画面: 選択に応じて分岐
            if self.settings_reset_selected:
                self.event_manager.emit_simple(EventType.GAME_RESET)
                self.screen_state = ScreenState.TITLE
                self.settings_reset_selected = False
            else:
                self.screen_state = ScreenState.TIME_SETTING
        elif self.screen_state in (ScreenState.FLOWER_LANGUAGE, ScreenState.DEATH):
            # 決定でタイトルへ
            self.reset_game()
        elif self.screen_state == ScreenState.STATUS:
            # ステータスから決定でメインへ
            self.screen_state = ScreenState.MAIN

    def _on_nav_cancel(self, event) -> None:
        if self.screen_state in (ScreenState.SEED_SELECTION, ScreenState.TIME_SETTING, ScreenState.SETTINGS, ScreenState.STATUS):
            self.screen_state = ScreenState.MAIN if self.flower.stats.seed_type else ScreenState.TITLE

    # --- 時間制御 ---
    def _on_time_toggle_pause(self, event) -> None:
        self.paused = not self.paused

    def _on_time_speed_normal(self, event) -> None:
        self.time_scale = 1.0

    def _on_time_speed_fast(self, event) -> None:
        self.time_scale = 4.0
