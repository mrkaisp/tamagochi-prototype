import pygame as pg
from typing import List, Dict, Any
from .components import (
    UIComponent, ProgressBar, Icon, Text, Colors, Rect, DigitalClock
)
from ..entities.flower import FlowerStats, SeedType, GrowthStage
from .font_manager import get_font_manager
from ..utils.helpers import format_time_digital

# 定数定義
DISPLAY_MARGIN = 2
DISPLAY_WIDTH = 124
DISPLAY_HEIGHT = 124
DIGITAL_CLOCK_WIDTH = 20
DIGITAL_CLOCK_HEIGHT = 6

class UIRenderer:
    """UIレンダラークラス"""
    
    def __init__(self):
        self.components: List[UIComponent] = []
        self._setup_components()
    
    def _setup_components(self) -> None:
        """UIコンポーネントを設定"""
        # ステータスバー
        self.water_icon = Icon(Rect(6, 6, 10, 10), "water")
        self.water_bar = ProgressBar(Rect(18, 8, 45, 6), color=Colors.BLUE)
        self.water_label = Text(Rect(65, 8, 25, 10), "水", 8)
        
        self.light_icon = Icon(Rect(6, 16, 10, 10), "light")
        self.light_bar = ProgressBar(Rect(18, 18, 45, 6), color=Colors.YELLOW)
        self.light_label = Text(Rect(65, 18, 25, 10), "光", 8)
        
        # 花のスプライト
        self.flower_sprite = Icon(Rect(44, 45, 40, 40), "flower")
        
        # 雑草・害虫インジケーター
        self.weed_indicator = Text(Rect(90, 100, 30, 10), "雑草:0", 8)
        self.pest_indicator = Text(Rect(90, 110, 30, 10), "害虫:0", 8)
        self.env_indicator = Text(Rect(6, 28, 60, 10), "環境:0", 8)
        self.mental_indicator = Text(Rect(70, 28, 50, 10), "言葉:0", 8)
        
        # 操作説明
        # 1/2/3 は 左/決定/右 のナビに使用
        self.controls_text = Text(Rect(6, 110, 120, 15), "1:左 2:決定 3:右", 8)
        
        # 年齢表示（デジタル時計風）
        self.age_clock = DigitalClock(Rect(103, 5, DIGITAL_CLOCK_WIDTH, DIGITAL_CLOCK_HEIGHT), Colors.BLACK)
        
        # 成長段階表示
        self.growth_stage_text = Text(Rect(6, 95, 80, 10), "種", 8)
        
        # 種選択画面用
        self.seed_selection_title = Text(Rect(20, 20, 88, 15), "種を選択してください", 16)
        self.seed_options = [
            Text(Rect(20, 40, 88, 10), "1:太陽 2:月", 8),
            Text(Rect(20, 55, 88, 10), "3:風 4:雨", 8),
        ]
        
        # コンポーネントリストに追加
        self.components.extend([
            self.water_icon, self.water_bar, self.water_label,
            self.light_icon, self.light_bar, self.light_label,
            self.flower_sprite, self.weed_indicator, self.pest_indicator,
            self.env_indicator, self.mental_indicator,
            self.controls_text, self.age_clock, self.growth_stage_text,
            self.seed_selection_title
        ])
        self.components.extend(self.seed_options)
    
    def render(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        """ゲーム状態をレンダリング"""
        # 背景をクリア
        surface.fill(Colors.WHITE)
        
        # 画面状態によって表示を切り替え
        screen_state = game_state.get('screen_state', 'MAIN')
        if screen_state == 'TITLE':
            self._render_title(surface)
        elif screen_state == 'SEED_SELECTION':
            self._render_seed_selection(surface)
        elif screen_state == 'TIME_SETTING':
            self._render_time_setting(surface)
        elif screen_state == 'SETTINGS':
            self._render_settings(surface)
        elif screen_state == 'STATUS':
            self._render_status(surface, game_state)
        elif screen_state == 'MODE_WATER':
            self._render_mode(surface, '水やり')
        elif screen_state == 'MODE_LIGHT':
            self._render_mode(surface, '光')
        elif screen_state == 'MODE_ENV':
            self._render_mode(surface, '環境整備')
        elif screen_state == 'FLOWER_LANGUAGE':
            self._render_flower_language(surface)
        elif screen_state == 'DEATH':
            self._render_death(surface)
        else:
            self._render_game_play(surface, game_state)
    
    def _render_seed_selection(self, surface: pg.Surface) -> None:
        """種選択画面をレンダリング"""
        # タイトル
        self.seed_selection_title.render(surface)
        
        # 種の選択肢
        for option in self.seed_options:
            option.render(surface)
        
        # 説明テキスト
        instruction_text = Text(Rect(20, 80, 88, 20), "キーを押して種を選択", 8)
        instruction_text.render(surface)

    def _render_title(self, surface: pg.Surface) -> None:
        title = Text(Rect(18, 30, 88, 20), "ふらわっち", 20)
        prompt = Text(Rect(18, 60, 88, 10), "決定で開始", 10)
        title.render(surface)
        prompt.render(surface)

    def _render_time_setting(self, surface: pg.Surface) -> None:
        title = Text(Rect(14, 20, 100, 12), "時間設定", 12)
        tip = Text(Rect(10, 40, 110, 10), "T:一時停止 9:早送り 0:通常", 8)
        tip2 = Text(Rect(10, 55, 110, 10), "決定でメインへ", 8)
        title.render(surface)
        tip.render(surface)
        tip2.render(surface)

    def _render_settings(self, surface: pg.Surface) -> None:
        title = Text(Rect(14, 20, 100, 12), "設定", 12)
        opt1 = Text(Rect(10, 40, 110, 10), "決定: 時間設定", 8)
        opt2 = Text(Rect(10, 55, 110, 10), "右でトグル: やりなおし", 8)
        back = Text(Rect(10, 70, 110, 10), "左/キャンセル: 戻る", 8)
        title.render(surface)
        opt1.render(surface)
        opt2.render(surface)
        back.render(surface)

    def _render_status(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        self._render_game_play(surface, game_state)
        overlay = Text(Rect(40, 5, 80, 10), "ステータス", 10)
        overlay.render(surface)

    def _render_mode(self, surface: pg.Surface, label: str) -> None:
        title = Text(Rect(14, 20, 100, 12), label, 12)
        tip = Text(Rect(10, 40, 110, 10), "行動後に戻る", 8)
        title.render(surface)
        tip.render(surface)

    def _render_flower_language(self, surface: pg.Surface) -> None:
        title = Text(Rect(8, 20, 110, 12), "花言葉を選ぶ", 12)
        tip = Text(Rect(8, 40, 110, 10), "決定で戻る", 8)
        title.render(surface)
        tip.render(surface)

    def _render_death(self, surface: pg.Surface) -> None:
        title = Text(Rect(18, 20, 100, 12), "枯れてしまった…", 12)
        tip = Text(Rect(8, 40, 110, 10), "決定でタイトル", 8)
        title.render(surface)
        tip.render(surface)
    
    def _render_game_play(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        """ゲームプレイ画面をレンダリング"""
        flower_stats = game_state.get('flower_stats')
        if not flower_stats:
            return
        
        # ステータスバーを更新
        self._update_status_bars(flower_stats)
        
        # 花のスプライトを更新
        self._update_flower_sprite(flower_stats)
        
        # 雑草・害虫表示を更新
        self._update_indicators(flower_stats)

        # 環境/言葉表示
        self._update_env_mental(flower_stats)
        
        # 成長段階表示を更新
        self._update_growth_stage(flower_stats)
        
        # 年齢表示を更新
        self._update_age_display(flower_stats)
        
        # 操作説明を更新
        self._update_controls_text(flower_stats)

        # 右上に時間状態を表示
        paused = game_state.get('paused', False)
        scale = game_state.get('time_scale', 1.0)
        time_text = Text(Rect(80, 5, 44, 10), ("PAUSE" if paused else f"x{int(scale)}"), 8)
        time_text.render(surface)

        # 無効操作メッセージ（短時間表示）
        invalid = game_state.get('invalid_message', "")
        if invalid:
            msg = Text(Rect(10, 85, 108, 10), invalid, 8)
            msg.render(surface)
        
        # すべてのコンポーネントをレンダリング
        for component in self.components:
            if component not in [self.seed_selection_title] + self.seed_options:
                component.render(surface)
    
    def _update_status_bars(self, stats: FlowerStats) -> None:
        """ステータスバーを更新"""
        # 水の量
        water_percentage = stats.water_level / 100.0
        self.water_bar.set_value(water_percentage)
        
        # 光の蓄積量
        light_percentage = stats.light_level / 100.0
        self.light_bar.set_value(light_percentage)
    
    def _update_flower_sprite(self, stats: FlowerStats) -> None:
        """花のスプライトを更新"""
        # 成長段階に応じてスプライトを変更
        sprite_name = self._get_sprite_name(stats)
        self.flower_sprite.set_icon(sprite_name)
    
    def _get_sprite_name(self, stats: FlowerStats) -> str:
        """成長段階に応じたスプライト名を取得"""
        if stats.growth_stage == GrowthStage.SEED:
            return "seed"
        elif stats.growth_stage == GrowthStage.SPROUT:
            return "sprout"
        elif stats.growth_stage == GrowthStage.STEM:
            return "stem"
        elif stats.growth_stage == GrowthStage.BUD:
            return "bud"
        elif stats.growth_stage == GrowthStage.FLOWER:
            return "flower"
        else:
            return "seed"
    
    def _update_indicators(self, stats: FlowerStats) -> None:
        """雑草・害虫インジケーターを更新"""
        self.weed_indicator.set_text(f"雑草:{stats.weed_count}")
        self.pest_indicator.set_text(f"害虫:{stats.pest_count}")

    def _update_env_mental(self, stats: FlowerStats) -> None:
        self.env_indicator.set_text(f"環境:{int(stats.environment_level)}")
        self.mental_indicator.set_text(f"言葉:{int(stats.mental_level)}")
    
    def _update_growth_stage(self, stats: FlowerStats) -> None:
        """成長段階表示を更新"""
        stage_text = f"{stats.growth_stage_display} ({stats.seed_type.value})"
        self.growth_stage_text.set_text(stage_text)
    
    def _update_age_display(self, stats: FlowerStats) -> None:
        """年齢表示を更新"""
        age_text = stats.age_digital
        self.age_clock.set_time(age_text)
    
    def _update_controls_text(self, stats: FlowerStats) -> None:
        """操作説明を更新"""
        if stats.is_fully_grown:
            self.controls_text.set_text("2:決定で花言葉/戻る")
        else:
            self.controls_text.set_text("1:左 2:決定 3:右")
    
    def update(self, dt: float) -> None:
        """レンダラーの更新"""
        # 必要に応じてアニメーションなどを更新
        pass

class RenderManager:
    """レンダリング管理クラス"""
    
    def __init__(self):
        self.ui_renderer = UIRenderer()
    
    def render(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        """ゲーム状態をレンダリング"""
        self.ui_renderer.render(surface, game_state)
    
    def update(self, dt: float) -> None:
        """レンダラーの更新"""
        self.ui_renderer.update(dt)