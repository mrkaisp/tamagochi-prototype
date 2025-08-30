#!/usr/bin/env python3
"""
美咲フォントテストスクリプト
128×128ピクセル画面での可読性を確認（最低8×8ピクセル）
"""

import pygame as pg
import sys
import os

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_font():
    """フォントテスト"""
    # pygame初期化
    pg.init()
    pg.font.init()
    
    # 128×128の画面を作成
    screen = pg.display.set_mode((128, 128))
    pg.display.set_caption("美咲フォントテスト（最低8×8ピクセル）")
    
    # フォントマネージャーをインポート
    from game.ui.font_manager import get_font_manager
    font_manager = get_font_manager()
    
    # テスト用テキスト
    test_texts = [
        "1:食 2:遊 3:掃",
        "お腹: 満腹",
        "機嫌: 良好",
        "清潔: 清潔",
        "年齢: 1日",
        "うんち: 0個"
    ]
    
    # 色定義
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    
    clock = pg.time.Clock()
    running = True
    
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
        
        # 背景を白で塗りつぶし
        screen.fill(WHITE)
        
        # 枠を描画
        pg.draw.rect(screen, BLACK, (0, 0, 128, 128), 2)
        
        # テストテキストを描画
        y_offset = 10
        for i, text in enumerate(test_texts):
            # フォントサイズを8から順番に試行（最低8×8ピクセル）
            font_size = 8 + (i % 3)  # 8, 9, 10のサイズを順番に使用
            
            text_surface = font_manager.render_text(text, font_size, BLACK)
            if text_surface:
                x = 5
                y = y_offset + i * 15
                screen.blit(text_surface, (x, y))
                
                # フォントサイズを表示
                size_text = f"サイズ: {font_size}"
                size_surface = font_manager.render_text(size_text, 8, GRAY)
                if size_surface:
                    screen.blit(size_surface, (x + 80, y))
        
        # 美咲フォント情報を表示
        info_text = "美咲フォント 最低8×8"
        info_surface = font_manager.render_text(info_text, 8, GRAY)
        if info_surface:
            screen.blit(info_surface, (5, 110))
        
        pg.display.flip()
        clock.tick(30)
    
    pg.quit()
    print("フォントテスト完了（最低8×8ピクセル）")

if __name__ == "__main__":
    test_font()
