"""
UI画面スクリーンショット生成機能

各画面の実装画面を描画して画像ファイルとしてレビューできるようにする。
"""
import pygame as pg
import os
from pathlib import Path
from ..core.game_engine import GameEngine
from ..core.screen_state import ScreenState
from ..entities.flower import FlowerStats, GrowthStage, SeedType


def generate_screenshots():
    """全画面のスクリーンショットを生成"""
    # ディレクトリ作成
    screenshot_dir = Path("docs/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    # ゲームエンジンを初期化
    engine = GameEngine()
    if not engine.initialize():
        print("Failed to initialize game engine")
        return
    
    # 画面サイズ
    width = 240
    height = 240
    
    # 各画面のスクリーンショットを生成
    screenshots = [
        ("title", ScreenState.TITLE, None),
        ("seed_selection", ScreenState.SEED_SELECTION, None),
        ("time_setting", ScreenState.TIME_SETTING, None),
        ("main_seed", ScreenState.MAIN, GrowthStage.SEED),
        ("main_sprout", ScreenState.MAIN, GrowthStage.SPROUT),
        ("main_stem", ScreenState.MAIN, GrowthStage.STEM),
        ("main_bud", ScreenState.MAIN, GrowthStage.BUD),
        ("main_flower", ScreenState.MAIN, GrowthStage.FLOWER),
        ("settings", ScreenState.SETTINGS, None),
        ("status", ScreenState.STATUS, None),
        ("mode_water", ScreenState.MODE_WATER, None),
        ("mode_light", ScreenState.MODE_LIGHT, None),
        ("flower_language", ScreenState.FLOWER_LANGUAGE, None),
        ("death", ScreenState.DEATH, None),
    ]
    
    for name, screen_state, growth_stage in screenshots:
        print(f"Generating screenshot: {name}.png")
        
        # 画面状態を設定
        engine.screen_state = screen_state
        
        # 成長段階を設定（メイン画面の場合）
        if growth_stage is not None:
            engine.flower.stats.growth_stage = growth_stage
            # 各成長段階に応じた状態を設定
            if growth_stage == GrowthStage.SEED:
                engine.flower.stats.water_level = 50.0
                engine.flower.stats.light_level = 0.0
            elif growth_stage == GrowthStage.SPROUT:
                engine.flower.stats.water_level = 60.0
                engine.flower.stats.light_level = 0.0
            elif growth_stage == GrowthStage.STEM:
                engine.flower.stats.water_level = 70.0
                engine.flower.stats.light_level = 0.0
            elif growth_stage == GrowthStage.BUD:
                engine.flower.stats.water_level = 80.0
                engine.flower.stats.light_level = 0.0
            elif growth_stage == GrowthStage.FLOWER:
                engine.flower.stats.water_level = 90.0
                engine.flower.stats.light_level = 0.0
        
        # ゲーム状態を準備（renderメソッドと同じ形式）
        cursor = engine.get_current_cursor()
        game_state_dict = engine.get_game_state()
        game_state = {
            "flower_stats": engine.flower.stats,
            "flower_stats_dict": game_state_dict["flower_stats"],
            "needs_attention": game_state_dict["needs_attention"],
            "is_alive": game_state_dict["is_alive"],
            "seed_selection_mode": game_state_dict["seed_selection_mode"],
            "paused": game_state_dict["paused"],
            "running": game_state_dict["running"],
            "info_message": game_state_dict["info_message"],
            "invalid_message": game_state_dict["invalid_message"],
            "screen_state": engine.screen_state.name,
            "time_scale": engine.time_scale,
            "nutrition_remaining": engine._nutrition_remaining_cached,
            "nutrition_limit": engine._nutrition_action_limit,
            "cursor": cursor,
            "cursor_index": cursor.index if cursor else 0,
            "menu_items": cursor.items if cursor else [],
        }
        
        # レンダリング用のサーフェスを作成
        surface = pg.Surface((width, height))
        
        # レンダリング実行
        if engine.render_manager:
            engine.render_manager.render(surface, game_state)
        
        # 画像ファイルとして保存
        output_path = screenshot_dir / f"{name}.png"
        pg.image.save(surface, str(output_path))
        print(f"  Saved: {output_path}")
    
    print(f"\nAll screenshots generated in {screenshot_dir}")


if __name__ == "__main__":
    generate_screenshots()
