from typing import TypeVar, Generic, Any, Tuple
import math
import pygame as pg

T = TypeVar('T')

def clamp(value: float, min_val: float, max_val: float) -> float:
    """値を指定範囲内に制限する"""
    return max(min_val, min(max_val, value))

def lerp(start: float, end: float, t: float) -> float:
    """線形補間"""
    return start + (end - start) * t

def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """スムーズステップ関数"""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def format_time(seconds: float) -> str:
    """秒数を時:分:秒形式にフォーマット"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_time_compact(seconds: float) -> str:
    """秒数をコンパクトな形式にフォーマット（全角対応）"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}時間{minutes}分"
    else:
        return f"{minutes}分"

def format_time_digital(seconds: float) -> str:
    """秒数をデジタル時計形式（mm:dd）にフォーマット"""
    total_minutes = int(seconds // 60)
    days = total_minutes // 1440  # 1日 = 1440分
    minutes = total_minutes % 1440
    return f"{minutes:02d}:{days:02d}"

class Observable(Generic[T]):
    """値の変更を監視できるクラス"""
    
    def __init__(self, initial_value: T):
        self._value = initial_value
        self._observers = []
    
    @property
    def value(self) -> T:
        return self._value
    
    @value.setter
    def value(self, new_value: T):
        if self._value != new_value:
            old_value = self._value
            self._value = new_value
            self._notify_observers(old_value, new_value)
    
    def add_observer(self, observer):
        """オブザーバーを追加"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer):
        """オブザーバーを削除"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self, old_value: T, new_value: T):
        """オブザーバーに変更を通知"""
        for observer in self._observers:
            try:
                observer(old_value, new_value)
            except Exception as e:
                print(f"Observer notification error: {e}")

class Timer:
    """タイマークラス"""
    
    def __init__(self, duration: float, auto_reset: bool = False):
        self.duration = duration
        self.auto_reset = auto_reset
        self.elapsed = 0.0
        self.is_finished = False
    
    def update(self, dt: float) -> bool:
        """タイマーを更新し、終了したかどうかを返す"""
        if self.is_finished:
            return True
        
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.is_finished = True
            if self.auto_reset:
                self.reset()
            return True
        return False
    
    def reset(self):
        """タイマーをリセット"""
        self.elapsed = 0.0
        self.is_finished = False
    
    @property
    def progress(self) -> float:
        """進捗率（0.0-1.0）"""
        return clamp(self.elapsed / self.duration, 0.0, 1.0)

class DigitalNumberRenderer:
    """デジタル時計風の数字描画クラス（3×5ピクセル）"""
    
    def __init__(self):
        # 数字の描画定義（3×5ピクセル）- 高さ5×幅3
        self.digit_patterns = {
            '0': [(1,1,1), (1,0,1), (1,0,1), (1,0,1), (1,1,1)],  # 111
            '1': [(0,1,0), (1,1,0), (0,1,0), (0,1,0), (1,1,1)],  # 010
            '2': [(1,1,1), (0,0,1), (1,1,1), (1,0,0), (1,1,1)],  # 111
            '3': [(1,1,1), (0,0,1), (1,1,1), (0,0,1), (1,1,1)],  # 111
            '4': [(1,0,1), (1,0,1), (1,1,1), (0,0,1), (0,0,1)],  # 101
            '5': [(1,1,1), (1,0,0), (1,1,1), (0,0,1), (1,1,1)],  # 111
            '6': [(1,1,1), (1,0,0), (1,1,1), (1,0,1), (1,1,1)],  # 111
            '7': [(1,1,1), (0,0,1), (0,1,0), (0,1,0), (0,1,0)],  # 111
            '8': [(1,1,1), (1,0,1), (1,1,1), (1,0,1), (1,1,1)],  # 111
            '9': [(1,1,1), (1,0,1), (1,1,1), (0,0,1), (1,1,1)],  # 111
            ':': [(0,1,0), (0,0,0), (0,0,0), (0,0,0), (0,1,0)]   # 010
        }
    
    def draw_digit(self, surface, digit: str, x: int, y: int, size: int = 1, color: Tuple[int, int, int] = (0, 0, 0)):
        """数字を描画"""
        if digit not in self.digit_patterns:
            return
        
        pattern = self.digit_patterns[digit]
        for row_idx, row in enumerate(pattern):
            for col_idx, pixel in enumerate(row):
                if pixel:
                    px = x + col_idx * size
                    py = y + row_idx * size
                    if size == 1:
                        surface.set_at((px, py), color)
                    else:
                        pg.draw.rect(surface, color, (px, py, size, size))
    
    def draw_time(self, surface, time_str: str, x: int, y: int, size: int = 1, color: Tuple[int, int, int] = (0, 0, 0), spacing: int = 1):
        """時間文字列を描画（文字間隔付き）"""
        char_width = 3 * size  # 3×5ピクセルなので幅は3
        for i, char in enumerate(time_str):
            char_x = x + i * (char_width + spacing * size)
            self.draw_digit(surface, char, char_x, y, size, color)
