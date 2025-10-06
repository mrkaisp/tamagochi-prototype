from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class DisplayConfig:
    """ディスプレイ関連の設定"""
    logical_width: int = 128
    logical_height: int = 128
    base_scale: int = 4
    fps: int = 30
    pixel_perfect: bool = True
    smooth_scaling: bool = False

@dataclass
class GameConfig:
    """ゲームプレイ関連の設定"""
    # 水の自然減少（1秒あたりの変化量）
    water_decay_rate: float = 0.5
    
    # アクション効果量
    water_amount: float = 30.0
    light_amount: float = 10.0
    weed_removal_amount: int = 2
    pest_removal_amount: int = 2
    
    # 雑草・害虫の発生
    weed_growth_chance: float = 0.001  # 1秒あたりの確率
    pest_growth_chance: float = 0.0005  # 1秒あたりの確率
    max_weeds: int = 5
    max_pests: int = 3
    # メンタル/環境
    environment_decay_rate: float = 0.2
    mental_decay_rate: float = 0.0
    fertilizer_amount: float = 20.0
    # 睡眠帯（0-23 時）
    sleep_start_hour: int = 22
    sleep_end_hour: int = 6
    # 成長/分岐用
    growth_age_threshold_flower: float = 60.0

@dataclass
class DataConfig:
    """データ関連の設定"""
    save_path: str = "save/state.json"
    auto_save_interval: float = 30.0  # 30秒ごとに自動セーブ
    random_seed: Optional[int] = None

@dataclass
class Config:
    """アプリケーション全体の設定"""
    display: DisplayConfig = None
    game: GameConfig = None
    data: DataConfig = None
    
    def __post_init__(self):
        if self.display is None:
            self.display = DisplayConfig()
        if self.game is None:
            self.game = GameConfig()
        if self.data is None:
            self.data = DataConfig()

# グローバル設定インスタンス
config = Config()

# 後方互換性のための定数
LOGICAL_W = config.display.logical_width
LOGICAL_H = config.display.logical_height
SCALE = config.display.base_scale
FPS = config.display.fps
SAVE_PATH = config.data.save_path
