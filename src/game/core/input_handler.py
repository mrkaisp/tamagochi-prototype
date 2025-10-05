import pygame as pg
from typing import Dict, Callable, Optional
from enum import Enum, auto
from ..core.event_system import EventManager, EventType

class InputAction(Enum):
    """入力アクションの定義"""
    QUIT = auto()
    WATER = auto()
    LIGHT = auto()
    REMOVE_WEEDS = auto()
    REMOVE_PESTS = auto()
    SELECT_SEED = auto()
    RESET = auto()
    PAUSE = auto()
    DEBUG = auto()
    NAV_LEFT = auto()
    NAV_RIGHT = auto()
    NAV_CONFIRM = auto()
    NAV_CANCEL = auto()
    TIME_TOGGLE_PAUSE = auto()
    TIME_SPEED_NORMAL = auto()
    TIME_SPEED_FAST = auto()

class InputHandler:
    """入力処理クラス"""
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.key_bindings: Dict[int, InputAction] = {
            pg.K_ESCAPE: InputAction.QUIT,
            pg.K_1: InputAction.WATER,
            pg.K_2: InputAction.LIGHT,
            pg.K_3: InputAction.REMOVE_WEEDS,
            pg.K_4: InputAction.REMOVE_PESTS,
            pg.K_s: InputAction.SELECT_SEED,
            pg.K_r: InputAction.RESET,
            pg.K_p: InputAction.PAUSE,
            pg.K_F1: InputAction.DEBUG,
            pg.K_LEFT: InputAction.NAV_LEFT,
            pg.K_RIGHT: InputAction.NAV_RIGHT,
            pg.K_RETURN: InputAction.NAV_CONFIRM,
            pg.K_SPACE: InputAction.NAV_CONFIRM,
            pg.K_BACKSPACE: InputAction.NAV_CANCEL,
            pg.K_t: InputAction.TIME_TOGGLE_PAUSE,
            pg.K_0: InputAction.TIME_SPEED_NORMAL,
            pg.K_9: InputAction.TIME_SPEED_FAST,
        }
        
        # 種選択用のキーバインド
        self.seed_selection_bindings: Dict[int, str] = {
            pg.K_1: "太陽",
            pg.K_2: "月", 
            pg.K_3: "風",
            pg.K_4: "雨",
        }
        self.action_handlers: Dict[InputAction, Callable] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """デフォルトのアクションハンドラーを設定"""
        self.action_handlers = {
            InputAction.QUIT: self._handle_quit,
            InputAction.WATER: self._handle_water,
            InputAction.LIGHT: self._handle_light,
            InputAction.REMOVE_WEEDS: self._handle_remove_weeds,
            InputAction.REMOVE_PESTS: self._handle_remove_pests,
            InputAction.SELECT_SEED: self._handle_select_seed,
            InputAction.RESET: self._handle_reset,
            InputAction.PAUSE: self._handle_pause,
            InputAction.DEBUG: self._handle_debug,
            InputAction.NAV_LEFT: self._handle_nav_left,
            InputAction.NAV_RIGHT: self._handle_nav_right,
            InputAction.NAV_CONFIRM: self._handle_nav_confirm,
            InputAction.NAV_CANCEL: self._handle_nav_cancel,
            InputAction.TIME_TOGGLE_PAUSE: self._handle_time_toggle_pause,
            InputAction.TIME_SPEED_NORMAL: self._handle_time_speed_normal,
            InputAction.TIME_SPEED_FAST: self._handle_time_speed_fast,
        }
    
    def set_key_binding(self, key: int, action: InputAction) -> None:
        """キーバインドを設定"""
        self.key_bindings[key] = action
    
    def set_action_handler(self, action: InputAction, handler: Callable) -> None:
        """アクションハンドラーを設定"""
        self.action_handlers[action] = handler
    
    def handle_events(self, seed_selection_mode: bool = False) -> bool:
        """イベントを処理し、ゲームを続行するかどうかを返す"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            elif event.type == pg.KEYDOWN:
                if seed_selection_mode:
                    if not self._handle_seed_selection(event.key):
                        return False
                else:
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
    
    def _handle_seed_selection(self, key: int) -> bool:
        """種選択時のキー押下イベントを処理"""
        if key == pg.K_ESCAPE:
            return False
        elif key in self.seed_selection_bindings:
            seed_type = self.seed_selection_bindings[key]
            self.event_manager.emit_simple(EventType.SEED_SELECTED, seed_type=seed_type)
            return True
        return True
    
    def _handle_quit(self) -> bool:
        """終了処理"""
        self.event_manager.emit_simple(EventType.STATS_CHANGED, action="quit")
        return False
    
    def _handle_water(self) -> bool:
        """水を与える"""
        self.event_manager.emit_simple(EventType.FLOWER_WATERED)
        return True
    
    def _handle_light(self) -> bool:
        """光を与える"""
        self.event_manager.emit_simple(EventType.FLOWER_LIGHT_GIVEN)
        return True
    
    def _handle_remove_weeds(self) -> bool:
        """雑草を除去する"""
        self.event_manager.emit_simple(EventType.FLOWER_WEEDS_REMOVED)
        return True
    
    def _handle_remove_pests(self) -> bool:
        """害虫を駆除する"""
        self.event_manager.emit_simple(EventType.FLOWER_PESTS_REMOVED)
        return True
    
    def _handle_select_seed(self) -> bool:
        """種を選択する"""
        self.event_manager.emit_simple(EventType.SEED_SELECTED)
        return True
    
    def _handle_reset(self) -> bool:
        """ゲームをリセットする"""
        self.event_manager.emit_simple(EventType.GAME_RESET)
        return True
    
    def _handle_pause(self) -> bool:
        """一時停止"""
        # 一時停止機能は未実装
        return True
    
    def _handle_debug(self) -> bool:
        """デバッグ機能"""
        # デバッグ機能は未実装
        return True

    def _handle_nav_left(self) -> bool:
        """ナビゲーション: 左"""
        self.event_manager.emit_simple(EventType.NAV_LEFT)
        return True

    def _handle_nav_right(self) -> bool:
        """ナビゲーション: 右"""
        self.event_manager.emit_simple(EventType.NAV_RIGHT)
        return True

    def _handle_nav_confirm(self) -> bool:
        """ナビゲーション: 決定"""
        self.event_manager.emit_simple(EventType.NAV_CONFIRM)
        return True

    def _handle_nav_cancel(self) -> bool:
        """ナビゲーション: キャンセル"""
        self.event_manager.emit_simple(EventType.NAV_CANCEL)
        return True

    def _handle_time_toggle_pause(self) -> bool:
        self.event_manager.emit_simple(EventType.TIME_TOGGLE_PAUSE)
        return True

    def _handle_time_speed_normal(self) -> bool:
        self.event_manager.emit_simple(EventType.TIME_SPEED_NORMAL)
        return True

    def _handle_time_speed_fast(self) -> bool:
        self.event_manager.emit_simple(EventType.TIME_SPEED_FAST)
        return True

class InputConfig:
    """入力設定クラス"""
    
    @staticmethod
    def get_default_bindings() -> Dict[int, InputAction]:
        """デフォルトのキーバインドを取得"""
        return {
            pg.K_ESCAPE: InputAction.QUIT,
            pg.K_1: InputAction.WATER,
            pg.K_2: InputAction.LIGHT,
            pg.K_3: InputAction.REMOVE_WEEDS,
            pg.K_4: InputAction.REMOVE_PESTS,
            pg.K_s: InputAction.SELECT_SEED,
            pg.K_r: InputAction.RESET,
            pg.K_p: InputAction.PAUSE,
            pg.K_F1: InputAction.DEBUG,
            pg.K_LEFT: InputAction.NAV_LEFT,
            pg.K_RIGHT: InputAction.NAV_RIGHT,
            pg.K_RETURN: InputAction.NAV_CONFIRM,
            pg.K_SPACE: InputAction.NAV_CONFIRM,
            pg.K_BACKSPACE: InputAction.NAV_CANCEL,
            pg.K_t: InputAction.TIME_TOGGLE_PAUSE,
            pg.K_0: InputAction.TIME_SPEED_NORMAL,
            pg.K_9: InputAction.TIME_SPEED_FAST,
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
            InputAction.WATER: "水を与える",
            InputAction.LIGHT: "光を与える",
            InputAction.REMOVE_WEEDS: "雑草を除去する",
            InputAction.REMOVE_PESTS: "害虫を駆除する",
            InputAction.SELECT_SEED: "種を選択する",
            InputAction.RESET: "ゲームをリセット",
            InputAction.PAUSE: "一時停止",
            InputAction.DEBUG: "デバッグ",
            InputAction.NAV_LEFT: "左",
            InputAction.NAV_RIGHT: "右",
            InputAction.NAV_CONFIRM: "決定",
            InputAction.NAV_CANCEL: "キャンセル",
            InputAction.TIME_TOGGLE_PAUSE: "時間: 一時停止切替",
            InputAction.TIME_SPEED_NORMAL: "時間: 通常",
            InputAction.TIME_SPEED_FAST: "時間: 早送り",
        }
        return descriptions.get(action, "不明")
