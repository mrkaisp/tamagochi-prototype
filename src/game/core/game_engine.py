import pygame as pg
from typing import Dict, Any  # Removed Optional
from ..entities.flower import Flower
from ..core.event_system import EventManager, EventType
from ..core.input_handler import InputHandler
from ..ui.display import DisplayManager
from ..ui.renderer import RenderManager
from ..data.config import config
from ..utils.helpers import Timer

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
        self.seed_selection_mode = True  # 種選択モード
        
        # タイマー
        self.fps_timer = Timer(1.0 / config.display.fps, auto_reset=True)
        self.auto_save_timer = Timer(config.data.auto_save_interval, auto_reset=True)
        
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
            
            # イベント処理
            if not self.input_handler.handle_events(self.seed_selection_mode):
                self.running = False
                break
            
            if not self.paused:
                # ゲーム状態の更新
                self.update(dt)
            
            # レンダリング
            self.render()
    
    def update(self, dt: float) -> None:
        """ゲーム状態を更新"""
        # 種選択モードでない場合のみ花を更新
        if not self.seed_selection_mode:
            self.flower.update(dt)
        
        # レンダラーを更新
        if self.render_manager:
            self.render_manager.update(dt)
        
        # 自動セーブ
        if self.auto_save_timer.update(dt) and not self.seed_selection_mode:
            self.flower.save()
    
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
                'seed_selection_mode': self.seed_selection_mode
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
        if not self.seed_selection_mode:
            self.flower.water()
    
    def _on_flower_light_given(self, event) -> None:
        """花に光を与えた時の処理"""
        if not self.seed_selection_mode:
            self.flower.give_light()
    
    def _on_flower_weeds_removed(self, event) -> None:
        """花の雑草を除去した時の処理"""
        if not self.seed_selection_mode:
            self.flower.remove_weeds()
    
    def _on_flower_pests_removed(self, event) -> None:
        """花の害虫を駆除した時の処理"""
        if not self.seed_selection_mode:
            self.flower.remove_pests()
    
    def _on_seed_selected(self, event) -> None:
        """種を選択した時の処理"""
        if self.seed_selection_mode:
            from ..entities.flower import SeedType
            seed_type_name = event.data.get("seed_type", "太陽")
            seed_type = SeedType(seed_type_name)
            self.flower.select_seed(seed_type)
            # 種選択モードを終了
            self.seed_selection_mode = False
            print(f"{seed_type_name}の種を選択しました。花の育成を開始します。")
    
    def _on_flower_growth_changed(self, event) -> None:
        """花の成長段階が変化した時の処理"""
        print(f"花が成長しました: {self.flower.stats.growth_stage_display}")
        
        # 花が完成した場合の特別な処理
        if self.flower.stats.is_fully_grown:
            self.event_manager.emit_simple(EventType.FLOWER_COMPLETED)
    
    def _on_flower_withered(self, event) -> None:
        """花が枯れた時の処理"""
        print("花が枯れてしまいました。")
        # 必要に応じてゲーム終了やリセット処理を実装
    
    def _on_flower_completed(self, event) -> None:
        """花が完成した時の処理"""
        print("🌸 花が完成しました！Rキーでリセットできます。")
    
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
