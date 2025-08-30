import pygame as pg
from typing import Dict, Callable, Optional
from enum import Enum, auto
from ..core.event_system import EventManager, EventType

class InputAction(Enum):
    """入力アクションの定義"""
    QUIT = auto()
    FEED = auto()
    PLAY = auto()
    CLEAN = auto()
    MEDICATE = auto()
    PAUSE = auto()
    DEBUG = auto()

class InputHandler:
    """入力処理クラス"""
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.key_bindings: Dict[int, InputAction] = {
            pg.K_ESCAPE: InputAction.QUIT,
            pg.K_1: InputAction.FEED,
            pg.K_2: InputAction.PLAY,
            pg.K_3: InputAction.CLEAN,
            pg.K_4: InputAction.MEDICATE,
            pg.K_p: InputAction.PAUSE,
            pg.K_F1: InputAction.DEBUG,
        }
        self.action_handlers: Dict[InputAction, Callable] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """デフォルトのアクションハンドラーを設定"""
        self.action_handlers = {
            InputAction.QUIT: self._handle_quit,
            InputAction.FEED: self._handle_feed,
            InputAction.PLAY: self._handle_play,
            InputAction.CLEAN: self._handle_clean,
            InputAction.MEDICATE: self._handle_medicate,
            InputAction.PAUSE: self._handle_pause,
            InputAction.DEBUG: self._handle_debug,
        }
    
    def set_key_binding(self, key: int, action: InputAction) -> None:
        """キーバインドを設定"""
        self.key_bindings[key] = action
    
    def set_action_handler(self, action: InputAction, handler: Callable) -> None:
        """アクションハンドラーを設定"""
        self.action_handlers[action] = handler
    
    def handle_events(self) -> bool:
        """イベントを処理し、ゲームを続行するかどうかを返す"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            elif event.type == pg.KEYDOWN:
                if not self._handle_keydown(event.key):
                    return False
        
        return True
    
    def _handle_keydown(self, key: int) -> bool:
        """キー押下イベントを処理"""
        if key in self.key_bindings:
            action = self.key_bindings[key]
            if action in self.action_handlers:
                handler = self.action_handlers[action]
                return handler()
        return True
    
    def _handle_quit(self) -> bool:
        """終了処理"""
        self.event_manager.emit_simple(EventType.STATS_CHANGED, action="quit")
        return False
    
    def _handle_feed(self) -> bool:
        """餌を与える"""
        self.event_manager.emit_simple(EventType.PET_FED)
        return True
    
    def _handle_play(self) -> bool:
        """遊ぶ"""
        self.event_manager.emit_simple(EventType.PET_PLAYED)
        return True
    
    def _handle_clean(self) -> bool:
        """掃除する"""
        self.event_manager.emit_simple(EventType.PET_CLEANED)
        return True
    
    def _handle_medicate(self) -> bool:
        """薬を与える"""
        self.event_manager.emit_simple(EventType.PET_MEDICATED)
        return True
    
    def _handle_pause(self) -> bool:
        """一時停止"""
        # 一時停止機能は未実装
        return True
    
    def _handle_debug(self) -> bool:
        """デバッグ機能"""
        # デバッグ機能は未実装
        return True

class InputConfig:
    """入力設定クラス"""
    
    @staticmethod
    def get_default_bindings() -> Dict[int, InputAction]:
        """デフォルトのキーバインドを取得"""
        return {
            pg.K_ESCAPE: InputAction.QUIT,
            pg.K_1: InputAction.FEED,
            pg.K_2: InputAction.PLAY,
            pg.K_3: InputAction.CLEAN,
            pg.K_4: InputAction.MEDICATE,
            pg.K_p: InputAction.PAUSE,
            pg.K_F1: InputAction.DEBUG,
        }
    
    @staticmethod
    def get_key_name(key: int) -> str:
        """キー名を取得"""
        return pg.key.name(key).upper()
    
    @staticmethod
    def get_action_description(action: InputAction) -> str:
        """アクションの説明を取得"""
        descriptions = {
            InputAction.QUIT: "終了",
            InputAction.FEED: "餌を与える",
            InputAction.PLAY: "遊ぶ",
            InputAction.CLEAN: "掃除する",
            InputAction.MEDICATE: "薬を与える",
            InputAction.PAUSE: "一時停止",
            InputAction.DEBUG: "デバッグ",
        }
        return descriptions.get(action, "不明")
