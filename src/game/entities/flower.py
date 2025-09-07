from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum
from ..data.save_manager import SaveManager
from ..utils.helpers import Observable, Timer
from ..data.config import config

class SeedType(Enum):
    """種の種類"""
    SUN = "太陽"
    MOON = "月"
    WIND = "風"
    RAIN = "雨"

class GrowthStage(Enum):
    """成長段階"""
    SEED = "種"
    SPROUT = "芽"
    STEM = "茎"
    BUD = "蕾"
    FLOWER = "花"

@dataclass
class FlowerStats:
    """花の基本統計情報"""
    # 基本情報
    seed_type: SeedType = SeedType.SUN
    growth_stage: GrowthStage = GrowthStage.SEED
    age_seconds: float = 0.0
    
    # 育成要素
    water_level: float = 50.0      # 0-100 水の量
    light_level: float = 0.0       # 0-100 光の蓄積量
    weed_count: int = 0            # 雑草の数
    pest_count: int = 0            # 害虫の数
    
    # 成長に必要な光の蓄積量
    light_required_for_sprout: float = 20.0
    light_required_for_stem: float = 40.0
    light_required_for_bud: float = 60.0
    light_required_for_flower: float = 80.0
    
    def update(self, dt: float) -> None:
        """統計情報を更新"""
        self.age_seconds += dt
        
        # 水の自然減少
        self.water_level = max(0, self.water_level - config.game.water_decay_rate * dt)
        
        # 雑草の自然発生（低確率）
        if config.game.weed_growth_chance > 0 and self.weed_count < config.game.max_weeds:
            import random
            if random.random() < config.game.weed_growth_chance * dt:
                self.weed_count += 1
        
        # 害虫の自然発生（低確率）
        if config.game.pest_growth_chance > 0 and self.pest_count < config.game.max_pests:
            import random
            if random.random() < config.game.pest_growth_chance * dt:
                self.pest_count += 1
        
        # 成長判定
        self._check_growth()
    
    def _check_growth(self) -> None:
        """成長段階の判定"""
        if self.growth_stage == GrowthStage.SEED and self.light_level >= self.light_required_for_sprout:
            self.growth_stage = GrowthStage.SPROUT
            self.light_level = 0  # 成長後にリセット
        elif self.growth_stage == GrowthStage.SPROUT and self.light_level >= self.light_required_for_stem:
            self.growth_stage = GrowthStage.STEM
            self.light_level = 0
        elif self.growth_stage == GrowthStage.STEM and self.light_level >= self.light_required_for_bud:
            self.growth_stage = GrowthStage.BUD
            self.light_level = 0
        elif self.growth_stage == GrowthStage.BUD and self.light_level >= self.light_required_for_flower:
            self.growth_stage = GrowthStage.FLOWER
            self.light_level = 0
    
    def water(self) -> None:
        """水を与える"""
        self.water_level = min(100, self.water_level + config.game.water_amount)
    
    def give_light(self, amount: float) -> None:
        """光を与える"""
        self.light_level += amount
        self.light_level = min(100, self.light_level)
    
    def remove_weeds(self) -> None:
        """雑草を除去する"""
        self.weed_count = max(0, self.weed_count - config.game.weed_removal_amount)
    
    def remove_pests(self) -> None:
        """害虫を駆除する"""
        self.pest_count = max(0, self.pest_count - config.game.pest_removal_amount)
    
    @property
    def age_formatted(self) -> str:
        """年齢をフォーマットされた文字列で取得"""
        from ..utils.helpers import format_time_compact
        return format_time_compact(self.age_seconds)
    
    @property
    def age_digital(self) -> str:
        """年齢をデジタル時計形式で取得"""
        from ..utils.helpers import format_time_digital
        return format_time_digital(self.age_seconds)
    
    @property
    def growth_stage_display(self) -> str:
        """成長段階を文字列で取得"""
        return self.growth_stage.value
    
    @property
    def needs_water(self) -> bool:
        """水が必要かどうか"""
        return self.water_level < 30
    
    @property
    def needs_light(self) -> bool:
        """光が必要かどうか"""
        return self.light_level < 10
    
    @property
    def has_weeds(self) -> bool:
        """雑草があるかどうか"""
        return self.weed_count > 0
    
    @property
    def has_pests(self) -> bool:
        """害虫がいるかどうか"""
        return self.pest_count > 0
    
    @property
    def is_fully_grown(self) -> bool:
        """完全に成長したかどうか"""
        return self.growth_stage == GrowthStage.FLOWER
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        data = asdict(self)
        # Enumを文字列に変換
        data['seed_type'] = self.seed_type.value
        data['growth_stage'] = self.growth_stage.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FlowerStats':
        """辞書から作成"""
        # 文字列をEnumに変換
        if 'seed_type' in data and isinstance(data['seed_type'], str):
            data['seed_type'] = SeedType(data['seed_type'])
        if 'growth_stage' in data and isinstance(data['growth_stage'], str):
            data['growth_stage'] = GrowthStage(data['growth_stage'])
        
        return cls(**data)

class Flower:
    """花のメインエンティティクラス"""
    
    def __init__(self, save_manager: Optional[SaveManager] = None):
        self.save_manager = save_manager or SaveManager()
        self.stats = FlowerStats()
        self.auto_save_timer = Timer(config.data.auto_save_interval, auto_reset=True)
        
        # 状態変更の監視
        self.stats_observable = Observable(self.stats)
        self._setup_observers()
        
        # 初期ロード
        self._load_state()
    
    def _setup_observers(self):
        """状態変更の監視を設定"""
        self.stats_observable.add_observer(self._on_stats_changed)
    
    def _on_stats_changed(self, old_stats: FlowerStats, new_stats: FlowerStats):
        """統計情報が変更された時の処理"""
        # 成長段階の変更を通知
        if old_stats.growth_stage != new_stats.growth_stage:
            print(f"花が成長しました: {old_stats.growth_stage.value} → {new_stats.growth_stage.value}")
    
    def select_seed(self, seed_type: SeedType) -> None:
        """種を選択する"""
        self.stats.seed_type = seed_type
        self.stats_observable.value = self.stats
    
    def update(self, dt: float) -> None:
        """花を更新"""
        # 統計情報を更新
        self.stats.update(dt)
        
        # 自動セーブタイマーを更新
        if self.auto_save_timer.update(dt):
            self.save()
    
    def water(self) -> None:
        """水を与える"""
        self.stats.water()
        self.stats_observable.value = self.stats
    
    def give_light(self, amount: float = None) -> None:
        """光を与える"""
        if amount is None:
            amount = config.game.light_amount
        self.stats.give_light(amount)
        self.stats_observable.value = self.stats
    
    def remove_weeds(self) -> None:
        """雑草を除去する"""
        self.stats.remove_weeds()
        self.stats_observable.value = self.stats
    
    def remove_pests(self) -> None:
        """害虫を駆除する"""
        self.stats.remove_pests()
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
                self.stats = FlowerStats.from_dict(data)
                self.stats_observable.value = self.stats
    
    def reset(self) -> None:
        """状態をリセット"""
        self.stats = FlowerStats()
        self.stats_observable.value = self.stats
        if self.save_manager:
            self.save_manager.delete_save()
    
    @property
    def is_alive(self) -> bool:
        """生きているかどうか（水が完全になくなったら枯れる）"""
        return self.stats.water_level > 0
    
    @property
    def needs_attention(self) -> bool:
        """注意が必要かどうか"""
        return (
            self.stats.needs_water or
            self.stats.needs_light or
            self.stats.has_weeds or
            self.stats.has_pests
        )
    
    def get_status_summary(self) -> dict:
        """状態のサマリーを取得"""
        return {
            'age': self.stats.age_formatted,
            'seed_type': self.stats.seed_type.value,
            'growth_stage': self.stats.growth_stage_display,
            'water_level': self.stats.water_level,
            'light_level': self.stats.light_level,
            'weed_count': self.stats.weed_count,
            'pest_count': self.stats.pest_count,
            'is_fully_grown': self.stats.is_fully_grown,
            'needs_attention': self.needs_attention
        }
