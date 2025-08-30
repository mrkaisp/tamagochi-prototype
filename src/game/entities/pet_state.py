from dataclasses import dataclass, asdict
from typing import Tuple
from ..data.config import config
from ..utils.helpers import clamp, format_time_compact, format_time_digital

@dataclass
class PetStats:
    """ペットの基本統計情報"""
    hunger: float = 20.0       # 0(満腹) - 100(腹ペコ)
    happiness: float = 80.0    # 0 - 100
    cleanliness: float = 80.0  # 0 - 100
    age_seconds: float = 0.0
    poop_count: int = 0
    is_sick: bool = False
    
    def update(self, dt: float) -> None:
        """統計情報を更新"""
        self.age_seconds += dt
        
        # 自然変化
        self.hunger = clamp(
            self.hunger + config.game.hunger_rate * dt, 0, 100
        )
        self.happiness = clamp(
            self.happiness - config.game.happiness_decay * dt, 0, 100
        )
        self.cleanliness = clamp(
            self.cleanliness - config.game.cleanliness_decay * dt, 0, 100
        )
        
        # 病気判定
        self.is_sick = (
            self.hunger >= config.game.sick_hunger_threshold or
            self.cleanliness <= config.game.sick_cleanliness_threshold or
            self.poop_count > config.game.max_poop
        )
    
    def feed(self) -> None:
        """餌を与える"""
        self.hunger = clamp(
            self.hunger - config.game.feed_amount, 0, 100
        )
        # 食べると一定確率でうんち
        self.poop_count = min(
            self.poop_count + 1, config.game.max_poop + 2
        )
    
    def play(self) -> None:
        """遊ぶ"""
        self.happiness = clamp(
            self.happiness + config.game.play_amount, 0, 100
        )
    
    def clean(self) -> None:
        """掃除する"""
        self.poop_count = 0
        self.cleanliness = clamp(
            self.cleanliness + config.game.clean_amount, 0, 100
        )
    
    def medicate(self) -> None:
        """薬を与える"""
        if self.is_sick:
            self.is_sick = False
    
    @property
    def age(self) -> Tuple[int, int, int]:
        """年齢を時:分:秒で取得"""
        total_seconds = int(self.age_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return hours, minutes, seconds
    
    @property
    def age_formatted(self) -> str:
        """年齢をフォーマットされた文字列で取得"""
        return format_time_compact(self.age_seconds)
    
    @property
    def age_digital(self) -> str:
        """年齢をデジタル時計形式で取得"""
        return format_time_digital(self.age_seconds)
    
    @property
    def health_status(self) -> str:
        """健康状態を文字列で取得"""
        if self.is_sick:
            return "病気"
        elif self.hunger > 80:
            return "空腹"
        elif self.cleanliness < 30:
            return "汚い"
        elif self.happiness < 30:
            return "悲しい"
        else:
            return "健康"
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PetStats':
        """辞書から作成"""
        # 古いセーブデータとの互換性
        if 'poop' in data:
            data['poop_count'] = data.pop('poop')
        if 'sick' in data:
            data['is_sick'] = data.pop('sick')
        
        return cls(**data)
