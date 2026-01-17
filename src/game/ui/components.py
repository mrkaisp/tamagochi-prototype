import pygame as pg
from typing import Tuple, Optional, Callable
from dataclasses import dataclass
from ..data.config import config
from .font_manager import get_font_manager
from ..utils.helpers import DigitalNumberRenderer
from .character_sprite_manager import CharacterSpriteManager
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
        # 擬人化キャラクター用の状態情報
        self.character_state = None  # FlowerStatsオブジェクトを保持
        self._sprite_manager = CharacterSpriteManager()
    
    def set_icon(self, icon_type: str) -> None:
        """アイコンタイプを設定"""
        self.icon_type = icon_type
    
    def set_character_state(self, stats) -> None:
        """擬人化キャラクターの状態を設定"""
        self.character_state = stats
    
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
        elif self.icon_type in ["seed", "sprout", "stem", "bud", "flower"]:
            # 擬人化キャラクターを描画
            if self.character_state:
                sprite = self._sprite_manager.get_character_surface(
                    self.character_state, (self.rect.width, self.rect.height)
                )
                if sprite:
                    sprite_rect = sprite.get_rect(center=center)
                    surface.blit(sprite, sprite_rect)
                else:
                    self._draw_character(surface, center)
            else:
                # フォールバック: 従来の描画
                self._draw_fallback_icon(surface, center)
    
    def _draw_fallback_icon(self, surface: pg.Surface, center: Tuple[int, int]) -> None:
        """フォールバック: 従来のアイコン描画"""
        if self.icon_type == "seed":
            pg.draw.ellipse(surface, Colors.BROWN, (center[0]-3, center[1]-2, 6, 4))
            pg.draw.ellipse(surface, Colors.BLACK, (center[0]-3, center[1]-2, 6, 4), 1)
        elif self.icon_type == "sprout":
            pg.draw.line(surface, Colors.GREEN, (center[0], center[1]+3), (center[0], center[1]-3), 2)
            pg.draw.ellipse(surface, Colors.GREEN, (center[0]-2, center[1]-4, 4, 3))
        elif self.icon_type == "stem":
            pg.draw.line(surface, Colors.GREEN, (center[0], center[1]+5), (center[0], center[1]-5), 3)
            pg.draw.ellipse(surface, Colors.GREEN, (center[0]-3, center[1]-6, 6, 4))
        elif self.icon_type == "bud":
            pg.draw.line(surface, Colors.GREEN, (center[0], center[1]+5), (center[0], center[1]-2), 3)
            pg.draw.ellipse(surface, Colors.PINK, (center[0]-3, center[1]-4, 6, 5))
        elif self.icon_type == "flower":
            pg.draw.line(surface, Colors.GREEN, (center[0], center[1]+5), (center[0], center[1]-3), 3)
            for i in range(5):
                angle = i * 2 * 3.14159 / 5
                x = center[0] + int(4 * pg.math.Vector2(1, 0).rotate_rad(angle).x)
                y = center[1] + int(4 * pg.math.Vector2(1, 0).rotate_rad(angle).y)
                pg.draw.circle(surface, Colors.PINK, (x, y), 2)
            pg.draw.circle(surface, Colors.YELLOW, center, 2)
    
    def _draw_character(self, surface: pg.Surface, center: Tuple[int, int]) -> None:
        """擬人化キャラクターを描画（仕様書に基づく）"""
        from ..entities.flower import GrowthStage
        
        stats = self.character_state
        growth_stage = stats.growth_stage
        
        # 状態判定（優先順位: 栄養 > メンタル）（環境整備機能削除により環境は使用停止）
        water_level = stats.water_level
        mental_level = stats.mental_level
        
        # 栄養状態判定（栄養<20でしょんぼり表情）
        if water_level >= 60:
            nutrition_state = "good"
        elif water_level >= 20:
            nutrition_state = "normal"
        else:
            nutrition_state = "weak"  # 栄養<20でしょんぼり表情
        
        # 環境状態判定（環境整備機能削除により使用停止、常に"normal"として扱う）
        env_state = "normal"
        
        # メンタル状態判定
        if mental_level >= 60:
            mental_state = "good"
        elif mental_level >= 30:
            mental_state = "normal"
        else:
            mental_state = "low"
        
        # 成長段階に応じて描画
        if growth_stage == GrowthStage.SEED:
            self._draw_seed(surface, center, nutrition_state)
        elif growth_stage == GrowthStage.SPROUT:
            self._draw_sprout(surface, center, nutrition_state, env_state)
        elif growth_stage == GrowthStage.STEM:
            self._draw_stem(surface, center, nutrition_state, env_state)
        elif growth_stage == GrowthStage.BUD:
            self._draw_bud(surface, center, nutrition_state, env_state, mental_state)
        elif growth_stage == GrowthStage.FLOWER:
            self._draw_flower(surface, center, nutrition_state, env_state, mental_state)
    
    def _draw_seed(self, surface: pg.Surface, center: Tuple[int, int], nutrition: str) -> None:
        """種の擬人化キャラクターを描画"""
        cx, cy = center
        
        # 体（丸い種）- 240×240画面に合わせてサイズ拡大（表情がよく分かるようにさらに拡大）
        body_size = 25 if nutrition == "good" else (22 if nutrition == "normal" else 18)
        body_y_offset = 4 if nutrition == "good" else (2 if nutrition == "normal" else 0)
        
        pg.draw.ellipse(surface, Colors.BROWN, 
                       (cx - body_size//2, cy - body_size//2 + body_y_offset, body_size, body_size))
        pg.draw.ellipse(surface, Colors.BLACK, 
                       (cx - body_size//2, cy - body_size//2 + body_y_offset, body_size, body_size), 1)
        
        # 顔
        if nutrition == "good":
            # 目を開けて、やや上向き
            pg.draw.circle(surface, Colors.BLACK, (cx - 4, cy - 2 + body_y_offset), 2)
            pg.draw.circle(surface, Colors.BLACK, (cx + 4, cy - 2 + body_y_offset), 2)
            # 笑顔
            pg.draw.arc(surface, Colors.BLACK, (cx - 6, cy + body_y_offset, 12, 8), 0, 3.14, 2)
        elif nutrition == "normal":
            # 目は半開き
            pg.draw.line(surface, Colors.BLACK, (cx - 4, cy + body_y_offset), (cx - 2, cy + body_y_offset), 2)
            pg.draw.line(surface, Colors.BLACK, (cx + 2, cy + body_y_offset), (cx + 4, cy + body_y_offset), 2)
            # 落ち着いた表情
            pg.draw.line(surface, Colors.BLACK, (cx - 4, cy + 4 + body_y_offset), (cx + 4, cy + 4 + body_y_offset), 2)
        else:
            # 目を閉じている、しょんぼり
            pg.draw.arc(surface, Colors.BLACK, (cx - 4, cy - 2 + body_y_offset, 8, 4), 0, 3.14, 2)
            pg.draw.arc(surface, Colors.BLACK, (cx + 4, cy - 2 + body_y_offset, 8, 4), 0, 3.14, 2)
            # 下向きの口
            pg.draw.arc(surface, Colors.BLACK, (cx - 4, cy + 2 + body_y_offset, 8, 4), 3.14, 6.28, 2)
    
    def _draw_sprout(self, surface: pg.Surface, center: Tuple[int, int], 
                     nutrition: str, env: str) -> None:
        """芽の擬人化キャラクターを描画"""
        cx, cy = center
        
        # 体（細長い）- 240×240画面に合わせてサイズ拡大（表情がよく分かるようにさらに拡大）
        body_height = 35 if nutrition == "good" else (30 if nutrition == "normal" else 25)
        body_y = cy - body_height // 2
        
        # 姿勢調整
        if nutrition == "weak":
            body_y += 2  # うつむき加減
        
        pg.draw.line(surface, Colors.GREEN, (cx, cy + 10), (cx, body_y), 5)
        
        # 葉（頭部）
        if nutrition == "good":
            # 葉を広げて、明るい笑顔
            pg.draw.ellipse(surface, Colors.GREEN, (cx - 8, body_y - 6, 16, 10))
            pg.draw.ellipse(surface, Colors.GREEN, (cx - 8, body_y - 6, 16, 10), 2)
            # 顔
            pg.draw.circle(surface, Colors.BLACK, (cx - 4, body_y - 2), 2)
            pg.draw.circle(surface, Colors.BLACK, (cx + 4, body_y - 2), 2)
            pg.draw.arc(surface, Colors.BLACK, (cx - 6, body_y, 12, 8), 0, 3.14, 2)
        elif nutrition == "normal":
            # 葉を少し垂らし、穏やかな表情
            pg.draw.ellipse(surface, Colors.GREEN, (cx - 6, body_y - 4, 12, 8))
            pg.draw.line(surface, Colors.BLACK, (cx - 2, body_y), (cx + 2, body_y), 2)
        else:
            # 葉が萎れ気味、困った表情
            pg.draw.ellipse(surface, Colors.DARK_GRAY, (cx - 6, body_y - 4, 12, 6))
            pg.draw.arc(surface, Colors.BLACK, (cx - 4, body_y - 2, 8, 4), 3.14, 6.28, 2)
    
    def _draw_stem(self, surface: pg.Surface, center: Tuple[int, int],
                   nutrition: str, env: str) -> None:
        """茎の擬人化キャラクターを描画"""
        cx, cy = center
        
        # 体（細長い茎）- 240×240画面に合わせてサイズ拡大（表情がよく分かるようにさらに拡大）
        body_height = 45 if nutrition == "good" else (40 if nutrition == "normal" else 35)
        body_y = cy - body_height // 2
        
        # 姿勢調整
        if nutrition == "good":
            # 背筋をピンと伸ばし
            pg.draw.line(surface, Colors.GREEN, (cx, cy + 12), (cx, body_y), 7)
        elif nutrition == "weak":
            # 茎が曲がる、疲れた表情
            pg.draw.line(surface, Colors.GREEN, (cx, cy + 12), (cx - 2, body_y), 5)
            body_y += 2
        else:
            # やや前傾姿勢
            pg.draw.line(surface, Colors.GREEN, (cx, cy + 12), (cx, body_y), 5)
        
        # 葉
        if nutrition == "good":
            # 葉を広げる
            pg.draw.ellipse(surface, Colors.GREEN, (cx - 10, body_y - 4, 20, 12))
            pg.draw.ellipse(surface, Colors.GREEN, (cx - 6, body_y + 4, 12, 8))
        elif nutrition == "weak":
            # 葉が垂れる
            pg.draw.ellipse(surface, Colors.DARK_GRAY, (cx - 6, body_y, 12, 6))
        
        # 顔
        face_y = body_y - 4
        if nutrition == "good":
            # 自信に満ちた表情
            pg.draw.circle(surface, Colors.BLACK, (cx - 4, face_y), 2)
            pg.draw.circle(surface, Colors.BLACK, (cx + 4, face_y), 2)
            pg.draw.arc(surface, Colors.BLACK, (cx - 6, face_y + 2, 12, 8), 0, 3.14, 2)
        elif nutrition == "normal":
            # 落ち着いた表情
            pg.draw.line(surface, Colors.BLACK, (cx - 4, face_y), (cx + 4, face_y), 2)
        else:
            # 疲れた表情
            pg.draw.arc(surface, Colors.BLACK, (cx - 4, face_y - 2, 8, 4), 3.14, 6.28, 2)
    
    def _draw_bud(self, surface: pg.Surface, center: Tuple[int, int],
                  nutrition: str, env: str, mental: str) -> None:
        """蕾の擬人化キャラクターを描画"""
        cx, cy = center
        
        # 体（丸みを帯びた蕾）- 240×240画面に合わせてサイズ拡大（表情がよく分かるようにさらに拡大）
        bud_size = 30 if nutrition == "good" and mental == "good" else (25 if nutrition == "normal" else 20)
        bud_y = cy - bud_size // 2
        
        # 姿勢調整
        if nutrition == "good" and mental == "good":
            bud_y -= 2  # やや上向き
        elif nutrition == "weak" or mental == "low":
            bud_y += 2  # うつむき加減
        
        # 蕾の形
        pg.draw.ellipse(surface, Colors.PINK, (cx - bud_size//2, bud_y, bud_size, bud_size + 4))
        pg.draw.ellipse(surface, Colors.BLACK, (cx - bud_size//2, bud_y, bud_size, bud_size + 4), 2)
        
        # 茎
        pg.draw.line(surface, Colors.GREEN, (cx, cy + 12), (cx, bud_y + bud_size + 4), 5)
        
        # 顔
        face_y = bud_y + bud_size // 2
        if nutrition == "good" and mental == "good":
            # 期待に満ちた表情
            pg.draw.circle(surface, Colors.BLACK, (cx - 4, face_y - 2), 2)
            pg.draw.circle(surface, Colors.BLACK, (cx + 4, face_y - 2), 2)
            pg.draw.arc(surface, Colors.BLACK, (cx - 6, face_y, 12, 8), 0, 3.14, 2)
        elif nutrition == "normal":
            # 穏やかな表情
            pg.draw.line(surface, Colors.BLACK, (cx - 2, face_y), (cx + 2, face_y), 2)
        else:
            # 不安そうな表情
            pg.draw.arc(surface, Colors.BLACK, (cx - 4, face_y - 2, 8, 4), 3.14, 6.28, 2)
    
    def _draw_flower(self, surface: pg.Surface, center: Tuple[int, int],
                    nutrition: str, env: str, mental: str) -> None:
        """花の擬人化キャラクターを描画"""
        cx, cy = center
        
        # 茎 - 240×240画面に合わせてサイズ拡大（表情がよく分かるようにさらに拡大）
        stem_height = 20
        stem_y = cy + 15
        
        # 姿勢調整
        if nutrition == "good" and mental == "good":
            # 自信に満ちた姿勢
            pg.draw.line(surface, Colors.GREEN, (cx, stem_y), (cx, cy - 8), 5)
            flower_y = cy - 8
        elif nutrition == "weak" or mental == "low":
            # やや前傾姿勢
            pg.draw.line(surface, Colors.GREEN, (cx, stem_y), (cx - 2, cy - 4), 5)
            flower_y = cy - 4
        else:
            # 標準的な姿勢
            pg.draw.line(surface, Colors.GREEN, (cx, stem_y), (cx, cy - 6), 5)
            flower_y = cy - 6
        
        # 花びら - 240×240画面に合わせてサイズ拡大（表情がよく分かるようにさらに拡大）
        petal_size = 15 if nutrition == "good" and mental == "good" else (12 if nutrition == "normal" else 9)
        petal_count = 5
        
        if nutrition == "good" and mental == "good":
            # 花びらを広げ
            for i in range(petal_count):
                angle = i * 2 * 3.14159 / petal_count
                x = cx + int(petal_size * pg.math.Vector2(1, 0).rotate_rad(angle).x)
                y = flower_y + int(petal_size * pg.math.Vector2(1, 0).rotate_rad(angle).y)
                pg.draw.circle(surface, Colors.PINK, (x, y), 4)
        elif nutrition == "normal":
            # 花びらを適度に広げ
            for i in range(petal_count):
                angle = i * 2 * 3.14159 / petal_count
                x = cx + int((petal_size - 2) * pg.math.Vector2(1, 0).rotate_rad(angle).x)
                y = flower_y + int((petal_size - 2) * pg.math.Vector2(1, 0).rotate_rad(angle).y)
                pg.draw.circle(surface, Colors.PINK, (x, y), 2)
        else:
            # 花びらが閉じ気味
            for i in range(petal_count):
                angle = i * 2 * 3.14159 / petal_count
                x = cx + int((petal_size - 4) * pg.math.Vector2(1, 0).rotate_rad(angle).x)
                y = flower_y + int((petal_size - 4) * pg.math.Vector2(1, 0).rotate_rad(angle).y)
                pg.draw.circle(surface, Colors.DARK_GRAY, (x, y), 2)
        
        # 中心
        pg.draw.circle(surface, Colors.YELLOW, (cx, flower_y), 4)
        
        # 顔
        if nutrition == "good" and mental == "good":
            # 明るい笑顔
            pg.draw.circle(surface, Colors.BLACK, (cx - 4, flower_y - 2), 2)
            pg.draw.circle(surface, Colors.BLACK, (cx + 4, flower_y - 2), 2)
            pg.draw.arc(surface, Colors.BLACK, (cx - 6, flower_y, 12, 8), 0, 3.14, 2)
        elif nutrition == "normal":
            # 穏やかな表情
            pg.draw.line(surface, Colors.BLACK, (cx - 2, flower_y), (cx + 2, flower_y), 2)
        else:
            # 疲れた表情
            pg.draw.arc(surface, Colors.BLACK, (cx - 4, flower_y - 2, 8, 4), 3.14, 6.28, 2)

class Text(UIComponent):
    """テキストコンポーネント（美咲フォント対応）"""
    
    def __init__(self, rect: Rect, text: str = "", font_size: int = 8,
                 color: Tuple[int, int, int] = Colors.BLACK, center: bool = False):
        super().__init__(rect)
        self.text = text
        # フォントサイズ: 8, 16, 24, 32から選択
        if font_size <= 8:
            self.font_size = 8
        elif font_size <= 16:
            self.font_size = 16
        elif font_size <= 24:
            self.font_size = 24
        else:
            self.font_size = 32
        self.color = color
        self.center = center  # 中央揃えフラグ
        self._font_manager = get_font_manager()
        # 240×240画面に最適化されたデフォルトサイズ
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
                if self.center:
                    # 中央揃え: テキストの幅と高さを取得して中央に配置
                    text_width, text_height = text_surface.get_size()
                    x = int(self.rect.x + (self.rect.width - text_width) // 2)
                    y = int(self.rect.y + (self.rect.height - text_height) // 2)
                else:
                    x = int(self.rect.x)
                    y = int(self.rect.y)
                surface.blit(text_surface, (x, y))
            else:
                # フォールバック: 最小サイズ（8×8ピクセル）で再試行
                fallback_surface = self._font_manager.render_text(
                    self.text, 8, self.color
                )
                if fallback_surface:
                    if self.center:
                        text_width, text_height = fallback_surface.get_size()
                        x = int(self.rect.x + (self.rect.width - text_width) // 2)
                        y = int(self.rect.y + (self.rect.height - text_height) // 2)
                    else:
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
