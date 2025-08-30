from typing import Dict, List, Callable, Any
from enum import Enum, auto
from dataclasses import dataclass
from ..utils.helpers import Observable

class EventType(Enum):
    """イベントタイプの定義"""
    PET_FED = auto()
    PET_PLAYED = auto()
    PET_CLEANED = auto()
    PET_MEDICATED = auto()
    PET_SICK = auto()
    PET_RECOVERED = auto()
    STATS_CHANGED = auto()
    GAME_SAVED = auto()
    GAME_LOADED = auto()

@dataclass
class Event:
    """イベントデータクラス"""
    type: EventType
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}

class EventBus:
    """イベントバスクラス"""
    
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._global_listeners: List[Callable[[Event], None]] = []
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """特定のイベントタイプにサブスクライブ"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def subscribe_all(self, callback: Callable[[Event], None]) -> None:
        """すべてのイベントにサブスクライブ"""
        self._global_listeners.append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """サブスクリプションを解除"""
        if event_type in self._listeners:
            if callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)
    
    def unsubscribe_all(self, callback: Callable[[Event], None]) -> None:
        """すべてのイベントからサブスクリプションを解除"""
        for listeners in self._listeners.values():
            if callback in listeners:
                listeners.remove(callback)
        if callback in self._global_listeners:
            self._global_listeners.remove(callback)
    
    def emit(self, event: Event) -> None:
        """イベントを発行"""
        # 特定のイベントタイプのリスナーに通知
        if event.type in self._listeners:
            for callback in self._listeners[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Event callback error: {e}")
        
        # グローバルリスナーに通知
        for callback in self._global_listeners:
            try:
                callback(event)
            except Exception as e:
                print(f"Global event callback error: {e}")
    
    def emit_simple(self, event_type: EventType, **kwargs) -> None:
        """シンプルなイベント発行"""
        event = Event(event_type, kwargs)
        self.emit(event)

class EventManager:
    """イベントマネージャークラス"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self._observables: Dict[str, Observable] = {}
    
    def create_observable(self, name: str, initial_value: Any = None) -> Observable:
        """監視可能なオブジェクトを作成"""
        observable = Observable(initial_value)
        self._observables[name] = observable
        return observable
    
    def get_observable(self, name: str) -> Observable:
        """監視可能なオブジェクトを取得"""
        return self._observables.get(name)
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """イベントにサブスクライブ"""
        self.event_bus.subscribe(event_type, callback)
    
    def subscribe_all(self, callback: Callable[[Event], None]) -> None:
        """すべてのイベントにサブスクライブ"""
        self.event_bus.subscribe_all(callback)
    
    def emit(self, event: Event) -> None:
        """イベントを発行"""
        self.event_bus.emit(event)
    
    def emit_simple(self, event_type: EventType, **kwargs) -> None:
        """シンプルなイベント発行"""
        self.event_bus.emit_simple(event_type, **kwargs)
