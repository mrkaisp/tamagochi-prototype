import pygame as pg
from typing import Optional, Dict, Any
from ..entities.tamagotchi import Tamagotchi
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
        self.tamagotchi = Tamagotchi()
        self.running = False
        self.paused = False
        
        # タイマー
        self.fps_timer = Timer(1.0 / config.display.fps, auto_reset=True)
        self.auto_save_timer = Timer(config.data.auto_save_interval, auto_reset=True)
        
        # イベントハンドラーの設定
        self._setup_event_handlers()
    
    def _setup_event_handlers(self) -> None:
        """イベントハンドラーを設定"""
        self.event_manager.subscribe(EventType.PET_FED, self._on_pet_fed)
        self.event_manager.subscribe(EventType.PET_PLAYED, self._on_pet_played)
        self.event_manager.subscribe(EventType.PET_CLEANED, self._on_pet_cleaned)
        self.event_manager.subscribe(EventType.PET_MEDICATED, self._on_pet_medicated)
        self.event_manager.subscribe(EventType.PET_SICK, self._on_pet_sick)
        self.event_manager.subscribe(EventType.PET_RECOVERED, self._on_pet_recovered)
    
    def initialize(self) -> bool:
        """ゲームエンジンを初期化"""
        try:
            pg.init()
            # フォントシステムを初期化
            pg.font.init()
            self.display_manager.initialize()
            
            # フォントマネージャーを初期化（pygame初期化後）
            from ..ui.font_manager import get_font_manager
            font_manager = get_font_manager()
            
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
            if not self.input_handler.handle_events():
                self.running = False
                break
            
            if not self.paused:
                # ゲーム状態の更新
                self.update(dt)
            
            # レンダリング
            self.render()
    
    def update(self, dt: float) -> None:
        """ゲーム状態を更新"""
        # たまごっちを更新
        self.tamagotchi.update(dt)
        
        # レンダラーを更新
        self.render_manager.update(dt)
        
        # 自動セーブ
        if self.auto_save_timer.update(dt):
            self.tamagotchi.save()
    
    def render(self) -> None:
        """ゲームをレンダリング"""
        # 論理サーフェスを取得
        logical_surface = self.display_manager.get_logical_surface()
        
        # ゲーム状態を準備
        game_state = {
            'stats': self.tamagotchi.stats,
            'needs_attention': self.tamagotchi.needs_attention,
            'is_alive': self.tamagotchi.is_alive
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
        self.tamagotchi.save()
        pg.quit()
    
    def reset_game(self) -> None:
        """ゲームをリセット"""
        self.tamagotchi.reset()
    
    def get_game_state(self) -> Dict[str, Any]:
        """ゲーム状態を取得"""
        return {
            'stats': self.tamagotchi.stats,
            'needs_attention': self.tamagotchi.needs_attention,
            'is_alive': self.tamagotchi.is_alive,
            'paused': self.paused,
            'running': self.running
        }
    
    # イベントハンドラー
    def _on_pet_fed(self, event) -> None:
        """ペットに餌を与えた時の処理"""
        self.tamagotchi.feed()
    
    def _on_pet_played(self, event) -> None:
        """ペットと遊んだ時の処理"""
        self.tamagotchi.play()
    
    def _on_pet_cleaned(self, event) -> None:
        """ペットを掃除した時の処理"""
        self.tamagotchi.clean()
    
    def _on_pet_medicated(self, event) -> None:
        """ペットに薬を与えた時の処理"""
        self.tamagotchi.medicate()
    
    def _on_pet_sick(self, event) -> None:
        """ペットが病気になった時の処理"""
        # 必要に応じて追加の処理を実装
        pass
    
    def _on_pet_recovered(self, event) -> None:
        """ペットが回復した時の処理"""
        # 必要に応じて追加の処理を実装
        pass
