import pygame as pg
from typing import Tuple, Optional, Callable
from dataclasses import dataclass
from ..data.config import config
from .font_manager import get_font_manager
from ..utils.helpers import DigitalNumberRenderer
import os

# カラーパレット（ピクセルアート風）
class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (64, 64, 64)
    BLUE = (0, 100, 200)
    GREEN = (0, 150, 0)
    RED = (200, 0, 0)
    YELLOW = (255, 255, 0)
    BROWN = (139, 69, 19)
    DARK_TEAL = (0, 128, 128)
    ORANGE = (255, 165, 0)
    PINK = (255, 192, 203)

@dataclass
class Rect:
    """矩形クラス"""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def to_pygame(self) -> pg.Rect:
        return pg.Rect(self.x, self.y, self.width, self.height)

class UIComponent:
    """UIコンポーネントの基底クラス"""
    
    def __init__(self, rect: Rect):
        self.rect = rect
        self.visible = True
        self.enabled = True
    
    def draw(self, surface: pg.Surface) -> None:
        """描画（サブクラスで実装）"""
        pass
    
    def render(self, surface: pg.Surface) -> None:
        """レンダリング（drawのエイリアス）"""
        self.draw(surface)
    
    def update(self, dt: float) -> None:
        """更新（サブクラスで実装）"""
        pass
    
    def handle_event(self, event) -> bool:
        """イベント処理（サブクラスで実装）"""
        return False

class ProgressBar(UIComponent):
    """プログレスバーコンポーネント"""
    
    def __init__(self, rect: Rect, value: float = 0.0, max_value: float = 100.0,
                 color: Tuple[int, int, int] = Colors.DARK_TEAL,
                 bg_color: Tuple[int, int, int] = Colors.GRAY):
        super().__init__(rect)
        self.value = value
        self.max_value = max_value
        self.color = color
        self.bg_color = bg_color
    
    def set_value(self, value: float) -> None:
        """値を設定"""
        self.value = max(0.0, min(self.max_value, value))
    
    def draw(self, surface: pg.Surface) -> None:
        """描画"""
        if not self.visible:
            return
        
        # 背景
        pg.draw.rect(surface, self.bg_color, self.rect.to_pygame)
        pg.draw.rect(surface, Colors.WHITE, self.rect.to_pygame, 1)
        
        # 塗りつぶし部分
        if self.value > 0:
            fill_width = max(1, int((self.rect.width - 2) * self.value / self.max_value))
            fill_rect = Rect(self.rect.x + 1, self.rect.y + 1, fill_width, self.rect.height - 2)
            pg.draw.rect(surface, self.color, fill_rect.to_pygame)

class Icon(UIComponent):
    """アイコンコンポーネント"""
    
    def __init__(self, rect: Rect, icon_type: str):
        super().__init__(rect)
        self.icon_type = icon_type
    
    def set_icon(self, icon_type: str) -> None:
        """アイコンタイプを設定"""
        self.icon_type = icon_type
    
    def draw(self, surface: pg.Surface) -> None:
        """描画"""
        if not self.visible:
            return
        
        center = self.rect.center
        
        if self.icon_type == "water":
            # 水のアイコン（水滴）
            pg.draw.circle(surface, Colors.BLUE, center, 4)
            pg.draw.circle(surface, Colors.BLACK, center, 4, 1)
            # 水滴の形
            pg.draw.ellipse(surface, Colors.BLUE, (center[0]-2, center[1]-6, 4, 6))
            # 水滴の先端
            pg.draw.circle(surface, Colors.BLUE, (center[0], center[1]+2), 1)
        elif self.icon_type == "light":
            # 光のアイコン（太陽）
            pg.draw.circle(surface, Colors.YELLOW, center, 4)
            pg.draw.circle(surface, Colors.BLACK, center, 4, 1)
            # 光線
            for i in range(8):
                angle = i * 3.14159 / 4
                x1 = center[0] + int(6 * pg.math.Vector2(1, 0).rotate_rad(angle).x)
                y1 = center[1] + int(6 * pg.math.Vector2(1, 0).rotate_rad(angle).y)
                x2 = center[0] + int(8 * pg.math.Vector2(1, 0).rotate_rad(angle).x)
                y2 = center[1] + int(8 * pg.math.Vector2(1, 0).rotate_rad(angle).y)
                pg.draw.line(surface, Colors.YELLOW, (x1, y1), (x2, y2), 1)
        elif self.icon_type == "seed":
            # 種のアイコン
            pg.draw.ellipse(surface, Colors.BROWN, (center[0]-3, center[1]-2, 6, 4))
            pg.draw.ellipse(surface, Colors.BLACK, (center[0]-3, center[1]-2, 6, 4), 1)
        elif self.icon_type == "sprout":
            # 芽のアイコン
            pg.draw.line(surface, Colors.GREEN, (center[0], center[1]+3), (center[0], center[1]-3), 2)
            pg.draw.ellipse(surface, Colors.GREEN, (center[0]-2, center[1]-4, 4, 3))
        elif self.icon_type == "stem":
            # 茎のアイコン
            pg.draw.line(surface, Colors.GREEN, (center[0], center[1]+5), (center[0], center[1]-5), 3)
            pg.draw.ellipse(surface, Colors.GREEN, (center[0]-3, center[1]-6, 6, 4))
        elif self.icon_type == "bud":
            # 蕾のアイコン
            pg.draw.line(surface, Colors.GREEN, (center[0], center[1]+5), (center[0], center[1]-2), 3)
            pg.draw.ellipse(surface, Colors.PINK, (center[0]-3, center[1]-4, 6, 5))
        elif self.icon_type == "flower":
            # 花のアイコン
            pg.draw.line(surface, Colors.GREEN, (center[0], center[1]+5), (center[0], center[1]-3), 3)
            # 花びら
            for i in range(5):
                angle = i * 2 * 3.14159 / 5
                x = center[0] + int(4 * pg.math.Vector2(1, 0).rotate_rad(angle).x)
                y = center[1] + int(4 * pg.math.Vector2(1, 0).rotate_rad(angle).y)
                pg.draw.circle(surface, Colors.PINK, (x, y), 2)
            # 中心
            pg.draw.circle(surface, Colors.YELLOW, center, 2)

class Text(UIComponent):
    """テキストコンポーネント（美咲フォント対応）"""
    
    def __init__(self, rect: Rect, text: str = "", font_size: int = 8,
                 color: Tuple[int, int, int] = Colors.BLACK):
        super().__init__(rect)
        self.text = text
        # フォントサイズは8か16のどちらかのみ
        self.font_size = 8 if font_size <= 8 else 16
        self.color = color
        self._font_manager = get_font_manager()
        # 128×128画面に最適化されたデフォルトサイズ
        self._optimal_size = self._font_manager.get_optimal_font_size(
            text, rect.width, rect.height
        ) if text else self.font_size
    
    def set_text(self, text: str) -> None:
        """テキストを設定"""
        self.text = text
        # テキストが変更されたら最適なフォントサイズを再計算
        if text:
            self._optimal_size = self._font_manager.get_optimal_font_size(
                text, self.rect.width, self.rect.height
            )
    
    def draw(self, surface: pg.Surface) -> None:
        """描画"""
        if not self.visible or not self.text:
            return
        
        try:
            # フォントマネージャーを使用してテキストをレンダリング
            text_surface = self._font_manager.render_text(
                self.text, self._optimal_size, self.color
            )
            
            if text_surface:
                x = int(self.rect.x)
                y = int(self.rect.y)
                surface.blit(text_surface, (x, y))
            else:
                # フォールバック: 最小サイズ（8×8ピクセル）で再試行
                fallback_surface = self._font_manager.render_text(
                    self.text, 8, self.color
                )
                if fallback_surface:
                    x = int(self.rect.x)
                    y = int(self.rect.y)
                    surface.blit(fallback_surface, (x, y))
                    
        except Exception as e:
            print(f"Text rendering failed: {e}")
    
    def get_text_size(self) -> Tuple[int, int]:
        """テキストのサイズを取得"""
        return self._font_manager.get_text_size(self.text, self._optimal_size)


class DigitalClock(UIComponent):
    """デジタル時計コンポーネント（3×5ピクセル）"""
    
    def __init__(self, rect: Rect, color: Tuple[int, int, int] = Colors.BLACK):
        super().__init__(rect)
        self.color = color
        self.time_str = "00:00"
        self._number_renderer = DigitalNumberRenderer()
    
    def set_time(self, time_str: str) -> None:
        """時間を設定"""
        self.time_str = time_str
    
    def draw(self, surface: pg.Surface) -> None:
        """描画"""
        if not self.visible:
            return
        
        # 数字のサイズを計算（3×5ピクセルベース）
        char_width = 3  # 1文字の幅（3×5ピクセル）
        char_spacing = 1  # 文字間隔1ピクセル
        total_width = len(self.time_str) * char_width + (len(self.time_str) - 1) * char_spacing
        available_width = self.rect.width
        
        # サイズを調整（最小1ピクセル）
        size = max(1, available_width // total_width)
        
        # 中央揃えのためのオフセット計算
        total_width_pixels = len(self.time_str) * char_width * size + (len(self.time_str) - 1) * char_spacing * size
        x_offset = (available_width - total_width_pixels) // 2
        
        x = int(self.rect.x + x_offset)
        y = int(self.rect.y + (self.rect.height - 5 * size) // 2)  # 縦方向中央揃え（5ピクセル高さ）
        
        # 各文字を描画（文字間隔を考慮）
        for i, char in enumerate(self.time_str):
            char_x = x + i * (char_width * size + char_spacing * size)
            self._number_renderer.draw_digit(surface, char, char_x, y, size, self.color)
