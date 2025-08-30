from typing import Optional, Callable
from .pet_state import PetStats
from ..data.save_manager import SaveManager
from ..utils.helpers import Observable, Timer
from ..data.config import config

class Tamagotchi:
    """たまごっちのメインエンティティクラス"""
    
    def __init__(self, save_manager: Optional[SaveManager] = None):
        self.save_manager = save_manager or SaveManager()
        self.stats = PetStats()
        self.auto_save_timer = Timer(config.data.auto_save_interval, auto_reset=True)
        
        # 状態変更の監視
        self.stats_observable = Observable(self.stats)
        self._setup_observers()
        
        # 初期ロード
        self._load_state()
    
    def _setup_observers(self):
        """状態変更の監視を設定"""
        # 統計情報の変更を監視
        self.stats_observable.add_observer(self._on_stats_changed)
    
    def _on_stats_changed(self, old_stats: PetStats, new_stats: PetStats):
        """統計情報が変更された時の処理"""
        # 必要に応じて追加の処理を実装
        pass
    
    def update(self, dt: float) -> None:
        """たまごっちを更新"""
        # 統計情報を更新
        self.stats.update(dt)
        
        # 自動セーブタイマーを更新
        if self.auto_save_timer.update(dt):
            self.save()
    
    def feed(self) -> None:
        """餌を与える"""
        self.stats.feed()
        self.stats_observable.value = self.stats
    
    def play(self) -> None:
        """遊ぶ"""
        self.stats.play()
        self.stats_observable.value = self.stats
    
    def clean(self) -> None:
        """掃除する"""
        self.stats.clean()
        self.stats_observable.value = self.stats
    
    def medicate(self) -> None:
        """薬を与える"""
        self.stats.medicate()
        self.stats_observable.value = self.stats
    
    def save(self) -> bool:
        """状態をセーブ"""
        if self.save_manager:
            return self.save_manager.save(self.stats.to_dict())
        return False
    
    def _load_state(self) -> None:
        """状態をロード"""
        if self.save_manager:
            data = self.save_manager.load()
            if data:
                self.stats = PetStats.from_dict(data)
                self.stats_observable.value = self.stats
    
    def reset(self) -> None:
        """状態をリセット"""
        self.stats = PetStats()
        self.stats_observable.value = self.stats
        if self.save_manager:
            self.save_manager.delete_save()
    
    @property
    def is_alive(self) -> bool:
        """生きているかどうか"""
        # 現在は常にTrue（死亡機能は未実装）
        return True
    
    @property
    def needs_attention(self) -> bool:
        """注意が必要かどうか"""
        return (
            self.stats.is_sick or
            self.stats.hunger > 80 or
            self.stats.cleanliness < 20 or
            self.stats.happiness < 20 or
            self.stats.poop_count > 0
        )
    
    def get_status_summary(self) -> dict:
        """状態のサマリーを取得"""
        return {
            'age': self.stats.age_formatted,
            'health_status': self.stats.health_status,
            'is_sick': self.stats.is_sick,
            'needs_attention': self.needs_attention,
            'hunger': self.stats.hunger,
            'happiness': self.stats.happiness,
            'cleanliness': self.stats.cleanliness,
            'poop_count': self.stats.poop_count
        }
