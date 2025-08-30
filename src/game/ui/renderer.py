import pygame as pg
from typing import List, Dict, Any
from .components import (
    UIComponent, ProgressBar, Icon, Text, PetSprite, PoopIndicator,
    Colors, Rect, DigitalClock
)
from ..entities.pet_state import PetStats
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
        self.hunger_icon = Icon(Rect(6, 6, 10, 10), "hunger")
        self.hunger_bar = ProgressBar(Rect(18, 8, 45, 6), color=Colors.GREEN)
        self.hunger_label = Text(Rect(65, 8, 25, 10), "おなか", 8)
        
        self.happiness_icon = Icon(Rect(6, 16, 10, 10), "happy")
        self.happiness_bar = ProgressBar(Rect(18, 18, 45, 6), color=Colors.YELLOW)
        self.happiness_label = Text(Rect(65, 18, 25, 10), "きげん", 8)
        
        self.cleanliness_icon = Icon(Rect(6, 26, 10, 10), "clean")
        self.cleanliness_bar = ProgressBar(Rect(18, 28, 45, 6), color=Colors.BLUE)
        self.cleanliness_label = Text(Rect(65, 28, 25, 10), "きれい", 8)
        
        # ペットスプライト
        self.pet_sprite = PetSprite(Rect(44, 45, 40, 40))
        
        # うんちインジケーター
        self.poop_indicator = PoopIndicator(Rect(90, 100, 30, 20))
        
        # 操作説明
        self.controls_text = Text(Rect(6, 110, 120, 15), "1:ごはん 2:あそび 3:そうじ", 8)
        
        # 年齢表示（デジタル時計風）
        self.age_clock = DigitalClock(Rect(103, 5, DIGITAL_CLOCK_WIDTH, DIGITAL_CLOCK_HEIGHT), Colors.BLACK)
        
        # コンポーネントリストに追加
        self.components = [
            self.hunger_icon, self.hunger_bar, self.hunger_label,
            self.happiness_icon, self.happiness_bar, self.happiness_label,
            self.cleanliness_icon, self.cleanliness_bar, self.cleanliness_label,
            self.pet_sprite, self.poop_indicator,
            self.controls_text, self.age_clock
        ]
    
    def update_stats(self, stats: PetStats) -> None:
        """統計情報を更新"""
        self._update_bars(stats)
        self._update_colors(stats)
        self._update_pet_state(stats)
        self._update_age(stats)
    
    def _update_bars(self, stats: PetStats) -> None:
        """バーの値を更新"""
        self.hunger_bar.set_value(stats.hunger)
        self.happiness_bar.set_value(stats.happiness)
        self.cleanliness_bar.set_value(stats.cleanliness)
    
    def _update_colors(self, stats: PetStats) -> None:
        """バーの色を状態に応じて変更"""
        self.hunger_bar.color = Colors.GREEN if stats.hunger > 50 else Colors.RED
        self.happiness_bar.color = Colors.YELLOW if stats.happiness > 50 else Colors.RED
        self.cleanliness_bar.color = Colors.BLUE if stats.cleanliness > 50 else Colors.RED
    
    def _update_pet_state(self, stats: PetStats) -> None:
        """ペットの状態を更新"""
        self.pet_sprite.set_state(stats.is_sick, stats.happiness)
        self.poop_indicator.set_poop_count(stats.poop_count)
    
    def _update_age(self, stats: PetStats) -> None:
        """年齢をデジタル時計形式で更新"""
        digital_time = format_time_digital(stats.age_seconds)
        self.age_clock.set_time(digital_time)
    
    def draw(self, surface: pg.Surface) -> None:
        """すべてのコンポーネントを描画"""
        self._draw_background(surface)
        self._draw_components(surface)
    
    def _draw_background(self, surface: pg.Surface) -> None:
        """背景を描画"""
        surface.fill(Colors.WHITE)
        display_rect = Rect(DISPLAY_MARGIN, DISPLAY_MARGIN, DISPLAY_WIDTH, DISPLAY_HEIGHT)
        pg.draw.rect(surface, Colors.LIGHT_GRAY, display_rect.to_pygame)
        pg.draw.rect(surface, Colors.BLACK, display_rect.to_pygame, 2)
    
    def _draw_components(self, surface: pg.Surface) -> None:
        """各コンポーネントを描画"""
        for component in self.components:
            component.draw(surface)
    
    def update(self, dt: float) -> None:
        """コンポーネントを更新"""
        for component in self.components:
            component.update(dt)
    
    def handle_event(self, event) -> bool:
        """イベントを処理"""
        for component in self.components:
            if component.handle_event(event):
                return True
        return False


class RenderManager:
    """レンダリングマネージャークラス"""
    
    def __init__(self):
        self.ui_renderer = UIRenderer()
        self.debug_mode = False
    
    def render(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        """ゲーム状態をレンダリング"""
        if 'stats' in game_state:
            self.ui_renderer.update_stats(game_state['stats'])
        
        self.ui_renderer.draw(surface)
        
        if self.debug_mode:
            self._draw_debug_info(surface, game_state)
    
    def _draw_debug_info(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        """デバッグ情報を描画"""
        if 'stats' not in game_state:
            return
            
        stats = game_state['stats']
        debug_text = [
            f"おなか: {stats.hunger:.1f}",
            f"きげん: {stats.happiness:.1f}",
            f"きれい: {stats.cleanliness:.1f}",
            f"うんち: {stats.poop_count}",
            f"びょうき: {stats.is_sick}",
            f"とし: {stats.age_formatted}"
        ]
        
        font_manager = get_font_manager()
        
        for i, text in enumerate(debug_text):
            debug_surface = font_manager.render_text(text, 8, Colors.RED)
            if debug_surface:
                surface.blit(debug_surface, (10, 10 + i * 12))
    
    def toggle_debug_mode(self) -> None:
        """デバッグモードを切り替え"""
        self.debug_mode = not self.debug_mode
    
    def update(self, dt: float) -> None:
        """レンダラーを更新"""
        self.ui_renderer.update(dt)
    
    def handle_event(self, event) -> bool:
        """イベントを処理"""
        return self.ui_renderer.handle_event(event)
