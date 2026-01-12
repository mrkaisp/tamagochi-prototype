from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from enum import Enum
import json
import os
from pathlib import Path
from ..data.save_manager import SaveManager
from ..utils.helpers import Observable, Timer
from ..data.config import config
from ..utils.random_manager import get_rng


def _load_growth_tables() -> Dict[str, Any]:
    """成長分岐テーブルをJSONから読み込む"""
    try:
        # プロジェクトルートからの相対パス
        json_path = Path(__file__).parent.parent / "data" / "growth_tables.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # フォールバック: デフォルト値を返す
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to load growth_tables.json: {e}. Using default values.")
        return {
            "phase2_branch": {
                "score_ranges": [
                    {"min": 70, "max": 100, "result": "まっすぐ"},
                    {"min": 40, "max": 69, "result": "しなる"},
                    {"min": 0, "max": 39, "result": "つる"}
                ],
                "default": "ふつう",
                "seed_biases": {"太陽": 5, "月": 0, "風": 2, "雨": 2},
                "mental_bonus": {"threshold": 70, "bonus": 5}
            },
            "phase3_shape": {
                "seed_base_values": {"太陽": 10, "月": 5, "風": 5, "雨": 10},
                "phase2_branch_values": {"まっすぐ": 10, "しなる": 5, "つる": 0, "ふつう": 0},
                "light_tendency_values": {"陽": 5, "陰": -5},
                "shape_candidates": [
                    {"name": "大輪", "min_base": 20},
                    {"name": "まるまる", "min_base": 15},
                    {"name": "ひらひら", "min_base": 10},
                    {"name": "ちいさめ", "min_base": 5},
                    {"name": "とがり", "min_base": -999}
                ],
                "default": "ふつう"
            }
        }


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
    water_level: float = 50.0  # 0-100 水の量（初期値を50に変更）
    light_level: float = 0.0  # 0-100 光の蓄積量（初期値は0、手動で光を与える）
    is_light_on: bool = False  # 光ON状態（ONの間は光蓄積量が増加）
    weed_count: int = 0  # 雑草の数
    pest_count: int = 0  # 害虫の数
    environment_level: float = 0.0  # 0-100 環境
    mental_level: float = 0.0  # 0-100 メンタル（言葉）
    light_tendency_yin: bool = False  # 陰/陽傾向（False=陽, True=陰）
    phase2_branch: str = "ふつう"
    phase3_shape: str = "ふつう"

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
        # 環境の自然減少
        self.environment_level = max(
            0, self.environment_level - config.game.environment_decay_rate * dt
        )
        
        # 光ON状態の時は光蓄積量が増加
        if self.is_light_on:
            self.light_level += config.game.light_amount * dt
            self.light_level = min(100, self.light_level)

        # 雑草の自然発生（低確率）
        if (
            config.game.weed_growth_chance > 0
            and self.weed_count < config.game.max_weeds
        ):
            if get_rng().random() < config.game.weed_growth_chance * dt:
                self.weed_count += 1

        # 害虫の自然発生（低確率）
        if (
            config.game.pest_growth_chance > 0
            and self.pest_count < config.game.max_pests
        ):
            if get_rng().random() < config.game.pest_growth_chance * dt:
                self.pest_count += 1

        # 成長判定
        self._check_growth()

    def _check_growth(self) -> None:
        """成長段階と分岐の判定"""
        import logging
        logger = logging.getLogger(__name__)
        
        old_stage = self.growth_stage
        # フェーズ1（種→芽）：光49/50の境界で陰/陽傾向
        if (
            self.growth_stage == GrowthStage.SEED
            and self.light_level >= self.light_required_for_sprout
        ):
            # 決定前の光蓄積で陰/陽傾向を決める（境界49/50）
            self.light_tendency_yin = self.light_level < 50
            tendency = "陰" if self.light_tendency_yin else "陽"
            logger.info(
                f"[フェーズ1分岐] 種→芽: 光レベル={self.light_level:.1f} "
                f"→ 傾向={tendency} (境界=50)"
            )
            self.growth_stage = GrowthStage.SPROUT
            self.light_level = 0  # 成長後にリセット
            self.is_light_on = False  # 成長フェーズ変更時に光をOFFにする
        elif (
            self.growth_stage == GrowthStage.SPROUT
            and self.light_level >= self.light_required_for_stem
        ):
            self.growth_stage = GrowthStage.STEM
            self.light_level = 0
            self.is_light_on = False  # 成長フェーズ変更時に光をOFFにする
            # フェーズ2（芽→茎）：総合スコア帯で分岐
            self.phase2_branch = self._compute_phase2_branch()
        elif (
            self.growth_stage == GrowthStage.STEM
            and self.light_level >= self.light_required_for_bud
        ):
            self.growth_stage = GrowthStage.BUD
            self.light_level = 0
            self.is_light_on = False  # 成長フェーズ変更時に光をOFFにする
            # フェーズ3（茎→蕾）：種×芽×茎と光傾向で形
            self.phase3_shape = self._compute_phase3_shape()
        elif self.growth_stage == GrowthStage.BUD and (
            self.light_level >= self.light_required_for_flower
            or self.age_seconds >= config.game.growth_age_threshold_flower
        ):
            self.growth_stage = GrowthStage.FLOWER
            self.light_level = 0
            self.is_light_on = False  # 成長フェーズ変更時に光をOFFにする

        # 成長段階が変更された場合、特に花が完成した場合の処理
        if old_stage != self.growth_stage:
            self._on_growth_changed(old_stage, self.growth_stage)

    def _on_growth_changed(
        self, old_stage: GrowthStage, new_stage: GrowthStage
    ) -> None:
        """成長段階が変更された時の処理"""
        if new_stage == GrowthStage.FLOWER:
            # 花が完成した場合の特別な処理
            self._on_flower_completed()

    def _on_flower_completed(self) -> None:
        """花が完成した時の処理"""
        # 花完成のログを出力
        print("🌸 おめでとうございます！花が完成しました！")
        print("Rキーを押すと新しい花を育て始めることができます。")

        # 花完成イベントを発行（外部からイベントマネージャーに通知する必要がある）
        # この処理はFlowerクラスから直接イベントを発行できないため、
        # ゲームエンジン側で成長段階の変更を監視して処理する

    def water(self) -> None:
        """水を与える"""
        self.water_level = min(100, self.water_level + config.game.water_amount)

    def fertilize(self) -> None:
        """肥料を与える（栄養加算）"""
        self.water_level = min(100, self.water_level + config.game.fertilizer_amount)

    def give_light(self, amount: float) -> None:
        """光を与える（非推奨: 時間経過で蓄積する仕様に変更）"""
        # 後方互換性のため残すが、通常は使用しない
        self.light_level += amount
        self.light_level = min(100, self.light_level)
    
    def turn_light_on(self) -> None:
        """光をONにする（光蓄積量が増加する）"""
        self.is_light_on = True
    
    def turn_light_off(self) -> None:
        """光をOFFにする（光蓄積量は維持される）"""
        self.is_light_on = False

    def remove_weeds(self) -> None:
        """雑草を除去する"""
        self.weed_count = max(0, self.weed_count - config.game.weed_removal_amount)
        self.environment_level = min(100, self.environment_level + 10)

    def remove_pests(self) -> None:
        """害虫を駆除する"""
        self.pest_count = max(0, self.pest_count - config.game.pest_removal_amount)
        self.environment_level = min(100, self.environment_level + 10)

    def adjust_mental(self, delta: float) -> None:
        """メンタル（言葉）を調整"""
        self.mental_level = max(0, min(100, self.mental_level + delta))

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
    def character_name(self) -> str:
        """キャラクター名を取得"""
        # 種タイプに基づく基本キャラクター名マッピング
        seed_name_map = {
            SeedType.SUN: "たんぽっち",
            SeedType.MOON: "さくらっち",
            SeedType.WIND: "ふじっち",
            SeedType.RAIN: "あじさいっち",
        }
        
        # 花段階の場合は、成長分岐の結果に基づいて最終進化名を返す
        if self.growth_stage == GrowthStage.FLOWER:
            # 成長分岐の結果に基づいて最終進化名を決定
            # 簡易実装: 種タイプと分岐結果の組み合わせで決定
            flower_name_map = {
                (SeedType.SUN, "まっすぐ", "大輪"): "ひまわり",
                (SeedType.SUN, "まっすぐ", "まるまる"): "たんぽぽ",
                (SeedType.MOON, "しなる", "ひらひら"): "さくら",
                (SeedType.MOON, "まっすぐ", "ほわほわ"): "ネモフィラ",
                (SeedType.WIND, "しなる", "ながれ"): "ふじのはな",
                (SeedType.RAIN, "曲がる", "まるまる"): "あじさい",
            }
            
            # 分岐結果の組み合わせで検索
            key = (self.seed_type, self.phase2_branch, self.phase3_shape)
            if key in flower_name_map:
                return flower_name_map[key]
            
            # デフォルト: 種タイプに基づく基本名
            base_name = seed_name_map.get(self.seed_type, "ふらわっち")
            # "っち"を削除して花名に変換
            if base_name.endswith("っち"):
                return base_name[:-2]
            return base_name
        
        # 種段階以降は基本名を返す
        return seed_name_map.get(self.seed_type, "ふらわっち")

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
        data["seed_type"] = self.seed_type.value
        data["growth_stage"] = self.growth_stage.value
        return data

    def _compute_phase2_branch(self) -> str:
        """フェーズ2分岐（JSONテーブルから読み込む）"""
        import logging
        logger = logging.getLogger(__name__)
        
        tables = _load_growth_tables()
        phase2_config = tables.get("phase2_branch", {})
        
        # 総合スコア: 栄養/光/メンタル + 種バイアス（環境整備機能削除によりenvironment_levelは使用停止）
        base_score = 0.0
        water_contrib = min(100, self.water_level)
        light_contrib = min(100, self.light_level)
        mental_contrib = min(100, self.mental_level)
        base_score = (water_contrib + light_contrib + mental_contrib) / 3.0
        
        logger.info(
            f"[フェーズ2分岐] 基本スコア計算: "
            f"栄養={water_contrib:.1f}, 光={light_contrib:.1f}, "
            f"メンタル={mental_contrib:.1f} → 平均={base_score:.2f}"
        )
        
        # 種バイアス（JSONから読み込む）
        seed_biases = phase2_config.get("seed_biases", {})
        seed_bias = seed_biases.get(self.seed_type.value, 0)
        score = base_score + seed_bias
        
        logger.info(
            f"[フェーズ2分岐] 種バイアス: {self.seed_type.value}=+{seed_bias} "
            f"→ スコア={score:.2f}"
        )
        
        # メンタル高値バイアス（JSONから読み込む）
        mental_bonus = phase2_config.get("mental_bonus", {})
        mental_bonus_value = 0
        if self.mental_level >= mental_bonus.get("threshold", 70):
            mental_bonus_value = mental_bonus.get("bonus", 5)
            score += mental_bonus_value
            logger.info(
                f"[フェーズ2分岐] メンタル高値バイアス: "
                f"メンタル={self.mental_level:.1f}>=70 → +{mental_bonus_value} "
                f"→ スコア={score:.2f}"
            )
        
        # スコア範囲から結果を決定（JSONから読み込む）
        score_ranges = phase2_config.get("score_ranges", [])
        result = None
        for range_config in score_ranges:
            if range_config["min"] <= score <= range_config["max"]:
                result = range_config["result"]
                logger.info(
                    f"[フェーズ2分岐] 結果決定: スコア={score:.2f} "
                    f"→ 範囲[{range_config['min']}-{range_config['max']}] "
                    f"→ {result}"
                )
                return result
        
        result = phase2_config.get("default", "ふつう")
        logger.info(
            f"[フェーズ2分岐] 結果決定: スコア={score:.2f} "
            f"→ デフォルト → {result}"
        )
        return result

    def _compute_phase3_shape(self) -> str:
        """フェーズ3形状（JSONテーブルから読み込む）"""
        import logging
        logger = logging.getLogger(__name__)
        
        tables = _load_growth_tables()
        phase3_config = tables.get("phase3_shape", {})
        
        base = 0
        
        # 種ベース値（JSONから読み込む）
        seed_base_values = phase3_config.get("seed_base_values", {})
        seed_base = seed_base_values.get(self.seed_type.value, 5)
        base += seed_base
        logger.info(
            f"[フェーズ3分岐] 種ベース値: {self.seed_type.value}=+{seed_base} "
            f"→ ベース={base}"
        )
        
        # フェーズ2分岐値（JSONから読み込む）
        phase2_branch_values = phase3_config.get("phase2_branch_values", {})
        phase2_value = phase2_branch_values.get(self.phase2_branch, 0)
        base += phase2_value
        logger.info(
            f"[フェーズ3分岐] フェーズ2分岐値: {self.phase2_branch}=+{phase2_value} "
            f"→ ベース={base}"
        )
        
        # 光傾向値（JSONから読み込む）
        light_tendency_values = phase3_config.get("light_tendency_values", {})
        light_tendency_key = "陰" if self.light_tendency_yin else "陽"
        light_tendency_value = light_tendency_values.get(light_tendency_key, 0)
        base += light_tendency_value
        logger.info(
            f"[フェーズ3分岐] 光傾向値: {light_tendency_key}=+{light_tendency_value} "
            f"→ ベース={base}"
        )
        
        # 形候補（JSONから読み込む）
        shape_candidates = phase3_config.get("shape_candidates", [])
        valid = [
            candidate["name"]
            for candidate in shape_candidates
            if base >= candidate.get("min_base", -999)
        ]
        
        logger.info(
            f"[フェーズ3分岐] 有効候補: ベース={base} → {valid}"
        )
        
        if not valid:
            result = phase3_config.get("default", "ふつう")
            logger.info(
                f"[フェーズ3分岐] 結果決定: 有効候補なし → デフォルト={result}"
            )
            return result
        
        from ..utils.random_manager import get_rng
        result = get_rng().choice(valid)
        logger.info(
            f"[フェーズ3分岐] 結果決定: ベース={base}, 候補={valid} "
            f"→ ランダム選択 → {result}"
        )
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "FlowerStats":
        """辞書から作成"""
        # デバッグ: 受信したデータを確認
        print(f"DEBUG: from_dict received data: {data}")

        # 古い形式のデータを新しい形式に変換
        if "hunger" in data:
            print("DEBUG: Converting old format to new format")
            # 古い形式から新しい形式への変換
            new_data = {
                "seed_type": SeedType.SUN,  # デフォルト値
                "growth_stage": GrowthStage.SEED,  # デフォルト値
                "age_seconds": data.get("age_seconds", 0.0),
                "water_level": 50.0,  # 古いhungerを水レベルに変換
                "light_level": 0.0,  # デフォルト値（光は手動で与える）
                "is_light_on": False,  # デフォルト値（光はOFF）
                "weed_count": 0,
                "pest_count": 0,
                "environment_level": 0.0,
                "mental_level": 0.0,
                "light_tendency_yin": False,
                "phase2_branch": "ふつう",
                "phase3_shape": "ふつう",
                "light_required_for_sprout": 20.0,
                "light_required_for_stem": 40.0,
                "light_required_for_bud": 60.0,
                "light_required_for_flower": 80.0,
            }
            data = new_data

        # 文字列をEnumに変換
        if "seed_type" in data and isinstance(data["seed_type"], str):
            data["seed_type"] = SeedType(data["seed_type"])
        if "growth_stage" in data and isinstance(data["growth_stage"], str):
            data["growth_stage"] = GrowthStage(data["growth_stage"])

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
            print(
                f"花が成長しました: {old_stats.growth_stage.value} → {new_stats.growth_stage.value}"
            )

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
        """光を与える（非推奨: 光ON/OFFで蓄積する仕様に変更）"""
        if amount is None:
            amount = config.game.light_amount
        self.stats.give_light(amount)
        self.stats_observable.value = self.stats
    
    def turn_light_on(self) -> None:
        """光をONにする（光蓄積量が増加する）"""
        self.stats.turn_light_on()
        self.stats_observable.value = self.stats
    
    def turn_light_off(self) -> None:
        """光をOFFにする（光蓄積量は維持される）"""
        self.stats.turn_light_off()
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
            save_data = self.save_manager.load()
            if save_data:
                # 新しい形式（バージョン情報付き）の場合はdataキーから取得
                if isinstance(save_data, dict) and "data" in save_data:
                    data = save_data["data"]
                else:
                    # 古い形式（直接データ）の場合はそのまま使用
                    data = save_data
                
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
        """生きているかどうか（水分が極端に低くなったら枯れる）"""
        return self.stats.water_level > 5.0

    @property
    def needs_attention(self) -> bool:
        """注意が必要かどうか"""
        return (
            self.stats.needs_water
            or self.stats.needs_light
            or self.stats.has_weeds
            or self.stats.has_pests
        )

    def get_status_summary(self) -> dict:
        """状態のサマリーを取得"""
        return {
            "age": self.stats.age_formatted,
            "seed_type": self.stats.seed_type.value,
            "growth_stage": self.stats.growth_stage_display,
            "water_level": self.stats.water_level,
            "light_level": self.stats.light_level,
            "weed_count": self.stats.weed_count,
            "pest_count": self.stats.pest_count,
            "is_fully_grown": self.stats.is_fully_grown,
            "needs_attention": self.needs_attention,
        }
