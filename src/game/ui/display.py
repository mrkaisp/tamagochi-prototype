import pygame as pg
from typing import Tuple, Optional
from ..data.config import config

class PixelPerfectDisplay:
    """ピクセルパーフェクト表示クラス"""
    
    def __init__(self, logical_size: Optional[Tuple[int, int]] = None, base_scale: Optional[int] = None):
        self.logical_size = logical_size or (config.display.logical_width, config.display.logical_height)
        self.base_scale = base_scale or config.display.base_scale
        self.logical_surface = pg.Surface(self.logical_size)
        self.optimal_scale = self._calculate_optimal_scale()
        self.window_size = (
            self.logical_size[0] * self.optimal_scale,
            self.logical_size[1] * self.optimal_scale
        )
        self.screen: Optional[pg.Surface] = None
    
    def _calculate_optimal_scale(self) -> int:
        """ディスプレイに最適な拡大倍率を計算"""
        try:
            info = pg.display.Info()
            max_scale_w = (info.current_w - 100) // self.logical_size[0]
            max_scale_h = (info.current_h - 100) // self.logical_size[1]
            return min(max_scale_w, max_scale_h, self.base_scale, 8)
        except:
            return self.base_scale
    
    def create_window(self) -> pg.Surface:
        """ピクセルパーフェクト表示用ウィンドウを作成"""
        self.screen = pg.display.set_mode(self.window_size)
        pg.display.set_caption(
            f"Tamagotchi Prototype ({self.window_size[0]}x{self.window_size[1]})"
        )
        return self.screen
    
    def clear(self) -> None:
        """論理サーフェスをクリア"""
        self.logical_surface.fill((0, 0, 0))
    
    def render(self) -> None:
        """論理サーフェスを拡大して表示"""
        if self.screen is None:
            return
        
        if config.display.pixel_perfect:
            # ピクセルパーフェクト表示
            scaled = pg.transform.scale(self.logical_surface, self.window_size)
        else:
            # スムーズスケーリング
            scaled = pg.transform.smoothscale(self.logical_surface, self.window_size)
        
        self.screen.blit(scaled, (0, 0))
        pg.display.flip()
    
    def get_logical_surface(self) -> pg.Surface:
        """論理サーフェスを取得"""
        return self.logical_surface
    
    def resize(self, new_logical_size: Tuple[int, int]) -> None:
        """論理サイズを変更"""
        self.logical_size = new_logical_size
        self.logical_surface = pg.Surface(self.logical_size)
        self.optimal_scale = self._calculate_optimal_scale()
        self.window_size = (
            self.logical_size[0] * self.optimal_scale,
            self.logical_size[1] * self.optimal_scale
        )
        
        if self.screen is not None:
            self.create_window()

class DisplayManager:
    """ディスプレイマネージャークラス"""
    
    def __init__(self):
        self.display = PixelPerfectDisplay()
        self.screen: Optional[pg.Surface] = None
        self._is_initialized = False
    
    def initialize(self) -> None:
        """ディスプレイを初期化"""
        if not self._is_initialized:
            self.screen = self.display.create_window()
            self._is_initialized = True
    
    def get_screen(self) -> pg.Surface:
        """スクリーンを取得"""
        if not self._is_initialized:
            self.initialize()
        return self.screen
    
    def get_logical_surface(self) -> pg.Surface:
        """論理サーフェスを取得"""
        return self.display.get_logical_surface()
    
    def clear(self) -> None:
        """画面をクリア"""
        self.display.clear()
    
    def render(self) -> None:
        """画面をレンダリング"""
        self.display.render()
    
    def resize(self, new_size: Tuple[int, int]) -> None:
        """画面サイズを変更"""
        self.display.resize(new_size)
        if self._is_initialized:
            self.screen = self.display.create_window()
    
    def get_window_size(self) -> Tuple[int, int]:
        """ウィンドウサイズを取得"""
        return self.display.window_size
    
    def get_logical_size(self) -> Tuple[int, int]:
        """論理サイズを取得"""
        return self.display.logical_size
