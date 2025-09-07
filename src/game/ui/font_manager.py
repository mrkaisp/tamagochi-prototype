import pygame as pg
import os
from typing import Optional, Dict, Tuple
from pathlib import Path

class FontManager:
    """美咲フォントを使用したフォント管理クラス"""
    
    def __init__(self):
        self._fonts: Dict[int, pg.font.Font] = {}
        self._font_path = self._get_font_path()
        self._initialize_fonts()
    
    def _get_font_path(self) -> str:
        """美咲フォントのパスを取得"""
        # 現在のファイルの場所から相対パスでフォントを探す
        current_dir = Path(__file__).parent
        font_path = current_dir.parent / "assets" / "fonts" / "misaki_ttf_2021-05-05" / "misaki_gothic.ttf"
        
        if font_path.exists():
            return str(font_path)
        
        # フォールバック: プロジェクトルートからの相対パス
        fallback_path = current_dir.parent.parent.parent.parent / "src" / "game" / "assets" / "fonts" / "misaki_ttf_2021-05-05" / "misaki_gothic.ttf"
        if fallback_path.exists():
            return str(fallback_path)
        
        # 最後のフォールバック: 絶対パス
        absolute_path = "/workspaces/tamagotchi-prototype/src/game/assets/fonts/misaki_ttf_2021-05-05/misaki_gothic.ttf"
        if os.path.exists(absolute_path):
            return absolute_path
        
        raise FileNotFoundError(f"美咲フォントが見つかりません: {font_path}")
    
    def _initialize_fonts(self) -> None:
        """フォントを初期化"""
        try:
            # pygame.fontが初期化されているかチェック
            if not pg.font.get_init():
                print("pygame.fontが初期化されていません。遅延初期化を行います。")
                return
            
            # 128×128画面に最適化されたサイズを定義
            # 美咲フォントは8×8ドットで、最低文字サイズは8×8ピクセル
            # フォントサイズは8か16のどちらかのみ
            font_sizes = [8, 16]
            
            for size in font_sizes:
                try:
                    font = pg.font.Font(self._font_path, size)
                    self._fonts[size] = font
                    print(f"美咲フォント初期化成功: サイズ {size}")
                except Exception as e:
                    print(f"フォントサイズ {size} の初期化に失敗: {e}")
            
            if not self._fonts:
                raise Exception("どのフォントサイズも初期化できませんでした")
                
        except Exception as e:
            print(f"フォント初期化エラー: {e}")
            # フォールバック: システムフォントを使用
            self._setup_fallback_fonts()
    
    def _setup_fallback_fonts(self) -> None:
        """フォールバックフォントを設定"""
        fallback_fonts = [
            "Noto Sans Mono CJK JP",
            "DejaVu Sans Mono", 
            "Noto Sans CJK JP",
            "Noto Sans JP",
            "Yu Gothic",
            "Meiryo",
            "Hiragino Sans",
            "Hiragino Kaku Gothic ProN",
            "Takao",
            "VL PGothic",
            "IPAPGothic",
            "IPAPMincho",
            "DejaVu Sans"
        ]
        
        # フォントサイズは8か16のどちらかのみ
        font_sizes = [8, 16]
        
        for size in font_sizes:
            for font_name in fallback_fonts:
                try:
                    font = pg.font.SysFont(font_name, size)
                    # テスト用の日本語文字をレンダリング
                    test_surface = font.render("あ", False, (0, 0, 0))
                    if test_surface.get_width() > 0:
                        self._fonts[size] = font
                        print(f"フォールバックフォント使用: {font_name} サイズ {size}")
                        break
                except:
                    continue
            
            # どのフォントも見つからない場合はデフォルトフォント
            if size not in self._fonts:
                try:
                    self._fonts[size] = pg.font.Font(None, size)
                    print(f"デフォルトフォント使用: サイズ {size}")
                except:
                    print(f"サイズ {size} のフォント設定に失敗")
    
    def get_font(self, size: int) -> Optional[pg.font.Font]:
        """指定サイズのフォントを取得"""
        # フォントが初期化されていない場合は初期化を試行
        if not self._fonts and pg.font.get_init():
            self._initialize_fonts()
        
        # フォントサイズは8か16のどちらかのみ
        if size <= 8:
            size = 8
        else:
            size = 16
        
        # 指定サイズのフォントを返す
        if size in self._fonts:
            return self._fonts[size]
        
        # 利用可能なサイズから最も近いものを選択
        available_sizes = sorted(self._fonts.keys())
        if not available_sizes:
            return None
        
        closest_size = min(available_sizes, key=lambda x: abs(x - size))
        return self._fonts[closest_size]
    
    def render_text(self, text: str, size: int, color: Tuple[int, int, int] = (0, 0, 0)) -> Optional[pg.Surface]:
        """テキストをレンダリング"""
        font = self.get_font(size)
        if not font:
            return None
        
        try:
            return font.render(text, False, color)
        except Exception as e:
            print(f"テキストレンダリングエラー: {e}")
            return None
    
    def get_text_size(self, text: str, size: int) -> Tuple[int, int]:
        """テキストのサイズを取得"""
        font = self.get_font(size)
        if not font:
            return (0, 0)
        
        try:
            surface = font.render(text, False, (0, 0, 0))
            return surface.get_size()
        except:
            return (0, 0)
    
    def get_optimal_font_size(self, text: str, max_width: int, max_height: int) -> int:
        """指定された領域に収まる最適なフォントサイズを取得"""
        available_sizes = sorted(self._fonts.keys(), reverse=True)
        
        for size in available_sizes:
            width, height = self.get_text_size(text, size)
            if width <= max_width and height <= max_height:
                return size
        
        # どのサイズも収まらない場合は最小サイズを返す（最低8×8ピクセル）
        return min(available_sizes) if available_sizes else 8

# グローバルフォントマネージャーインスタンス
_font_manager: Optional[FontManager] = None

def get_font_manager() -> FontManager:
    """グローバルフォントマネージャーを取得"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager
