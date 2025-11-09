import pygame as pg
from typing import List, Dict, Any, Optional
from .components import UIComponent, Icon, Text, Colors, Rect
from ..entities.flower import FlowerStats, SeedType, GrowthStage
from .font_manager import get_font_manager
from ..utils.helpers import format_time_digital
from .menu_system import MenuCursor, MenuItem

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
        # 花のスプライト（キャラクター表示 - 表情で状態を表現）
        self.flower_sprite = Icon(Rect(44, 45, 40, 40), "flower")

        # 操作説明
        # 1/2/3 は 左/決定/右 のナビに使用
        self.controls_text = Text(Rect(6, 110, 120, 15), "1:左 2:決定 3:右", 8)

        # 種選択画面用
        self.seed_selection_title = Text(
            Rect(20, 12, 88, 14), "種を選択してください", 16
        )
        self.seed_options = [
            Text(Rect(20, 38, 88, 10), "1:太陽 2:月", 8),
            Text(Rect(20, 53, 88, 10), "3:風 4:雨", 8),
        ]
        self.seed_navigation_hint = Text(Rect(20, 68, 88, 10), "決定:中央/2", 8)

        # コンポーネントリストに追加
        self.components.extend(
            [
                self.flower_sprite,
                self.controls_text,
                self.seed_selection_title,
                self.seed_navigation_hint,
            ]
        )
        self.components.extend(self.seed_options)

    def render(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        """ゲーム状態をレンダリング"""
        # 背景をクリア
        surface.fill(Colors.WHITE)

        # 画面状態によって表示を切り替え
        screen_state = game_state.get("screen_state", "MAIN")
        if screen_state == "TITLE":
            self._render_title(surface)
        elif screen_state == "SEED_SELECTION":
            self._render_seed_selection(surface, game_state)
        elif screen_state == "TIME_SETTING":
            self._render_time_setting(surface, game_state)
        elif screen_state == "SETTINGS":
            self._render_settings(surface, game_state)
        elif screen_state == "STATUS":
            self._render_status(surface, game_state)
        elif screen_state == "MODE_WATER":
            self._render_mode(surface, game_state, "水やり")
        elif screen_state == "MODE_LIGHT":
            self._render_mode(surface, game_state, "光")
        elif screen_state == "MODE_ENV":
            self._render_mode(surface, game_state, "環境整備")
        elif screen_state == "FLOWER_LANGUAGE":
            self._render_flower_language(surface, game_state)
        elif screen_state == "DEATH":
            self._render_death(surface)
        else:
            self._render_game_play(surface, game_state)

    def _render_seed_selection(
        self, surface: pg.Surface, game_state: Dict[str, Any]
    ) -> None:
        """種選択画面をレンダリング"""
        # タイトル
        title = Text(Rect(20, 12, 88, 14), "種を選択してください", 16)
        title.render(surface)

        # メニュー項目とカーソルを表示
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        self._render_menu_items(
            surface, menu_items, cursor_index, start_y=40, item_height=14
        )

        # 説明テキスト
        hint = Text(Rect(20, 90, 88, 10), "1/3:選択 2:決定", 8)
        hint.render(surface)

    def _render_title(self, surface: pg.Surface) -> None:
        title = Text(Rect(18, 30, 88, 20), "ふらわっち", 20)
        prompt = Text(Rect(18, 60, 88, 10), "決定で開始", 10)
        title.render(surface)
        prompt.render(surface)

    def _render_time_setting(
        self, surface: pg.Surface, game_state: Dict[str, Any]
    ) -> None:
        title = Text(Rect(10, 10, 108, 12), "時間設定", 12)
        title.render(surface)

        paused = game_state.get("paused", False)
        time_scale = game_state.get("time_scale", 1.0)
        status_text = Text(
            Rect(10, 26, 108, 10),
            f"一時停止: {'ON' if paused else 'OFF'}  時間: x{time_scale:g}",
            8,
        )
        status_text.render(surface)

        # メニュー項目とカーソルを表示
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        self._render_menu_items(
            surface, menu_items, cursor_index, start_y=45, item_height=14
        )

        hint = Text(Rect(10, 100, 108, 10), "1/3:選択 2:実行", 8)
        hint.render(surface)

    def _render_settings(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        title = Text(Rect(14, 20, 100, 12), "設定", 12)
        title.render(surface)

        # メニュー項目とカーソルを表示
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        self._render_menu_items(
            surface, menu_items, cursor_index, start_y=45, item_height=14
        )

        hint = Text(Rect(10, 100, 108, 10), "1/3:選択 2:決定", 8)
        hint.render(surface)

    def _render_status(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        """ステータス画面をレンダリング（モダンデザイン）"""
        # グラデーション背景
        for i in range(128):
            color_val = 25 + int(i * 0.2)
            pg.draw.line(surface, (color_val, color_val + 15, color_val + 10), (0, i), (128, i))
        
        # タイトルバー
        pg.draw.rect(surface, (20, 35, 30), (0, 0, 128, 16))
        pg.draw.line(surface, (100, 200, 150), (0, 16), (128, 16), 2)
        title = Text(Rect(10, 4, 108, 12), "詳細ステータス", 12)
        title.color = (200, 255, 220)
        title.render(surface)
        
        flower_stats = game_state.get("flower_stats_dict", {})
        y = 20
        
        # 基本情報カード
        pg.draw.rect(surface, (45, 65, 55), (4, y, 120, 28))
        pg.draw.rect(surface, (120, 180, 150), (4, y, 120, 28), 2)
        
        seed_text = Text(Rect(8, y + 3, 60, 8), f"{flower_stats.get('seed_type', '未選択')}", 8)
        seed_text.color = (255, 255, 150)
        seed_text.render(surface)
        
        stage_text = Text(Rect(8, y + 12, 112, 8), f"成長: {flower_stats.get('growth_stage', '不明')}", 8)
        stage_text.color = (200, 255, 200)
        stage_text.render(surface)
        
        age_text = Text(Rect(8, y + 20, 112, 8), f"年齢: {flower_stats.get('age_formatted', '0秒')}", 8)
        age_text.color = (180, 220, 255)
        age_text.render(surface)
        
        y += 32
        
        # ステータスバー
        water_level = flower_stats.get('water_level', 0)
        light_level = flower_stats.get('light_level', 0)
        env_level = flower_stats.get('environment_level', 0)
        mental_level = flower_stats.get('mental_level', 0)
        
        self._render_modern_stat(surface, 4, y, "水分", water_level, (100, 180, 255))
        y += 13
        self._render_modern_stat(surface, 4, y, "光量", light_level, (255, 220, 100))
        y += 13
        self._render_modern_stat(surface, 4, y, "環境", env_level, (120, 220, 150))
        y += 13
        self._render_modern_stat(surface, 4, y, "心情", mental_level, (255, 150, 200))
        y += 16
        
        # 問題表示
        weed_count = flower_stats.get('weed_count', 0)
        pest_count = flower_stats.get('pest_count', 0)
        
        if weed_count > 0 or pest_count > 0:
            pg.draw.rect(surface, (80, 40, 40), (4, y, 120, 10))
            pg.draw.rect(surface, (200, 100, 100), (4, y, 120, 10), 1)
            problem_text = Text(Rect(8, y + 1, 112, 8), f"! 雑草:{weed_count} 害虫:{pest_count}", 8)
            problem_text.color = (255, 200, 100)
            problem_text.render(surface)
        
        # メニュー（「戻る」選択肢）
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        if menu_items:
            self._render_menu_items(surface, menu_items, cursor_index, start_y=108, item_height=10)
    
    def _render_modern_stat(self, surface: pg.Surface, x: int, y: int, label: str, value: float, color: tuple) -> None:
        """モダンなステータス表示"""
        label_text = Text(Rect(x + 4, y, 28, 8), label, 8)
        label_text.color = (180, 180, 180)
        label_text.render(surface)
        
        value_text = Text(Rect(x + 32, y, 24, 8), f"{value:.0f}%", 8)
        value_text.color = color
        value_text.render(surface)
        
        self._render_progress_bar(surface, x + 58, y + 1, 62, 7, value, 100)
    
    def _render_progress_bar(self, surface: pg.Surface, x: int, y: int, width: int, height: int, value: float, max_value: float) -> None:
        """プログレスバーを10段階で描画"""
        # 10段階に分割
        num_segments = 10
        segment_width = width // num_segments
        filled_segments = int((value / max_value) * num_segments)
        
        # 各セグメントを描画
        for i in range(num_segments):
            seg_x = x + i * segment_width
            # セグメント間に1pxの隙間を入れる
            if i < filled_segments:
                # 値に応じた色を設定
                if value > 60:
                    color = (100, 200, 100)  # 緑（良好）
                elif value > 30:
                    color = (200, 200, 100)  # 黄色（注意）
                else:
                    color = (200, 100, 100)  # 赤（危険）
                pg.draw.rect(surface, color, (seg_x, y, segment_width - 1, height))
            else:
                # 空のセグメント
                pg.draw.rect(surface, (80, 80, 80), (seg_x, y, segment_width - 1, height))
        
        # 外枠を描画
        pg.draw.rect(surface, Colors.WHITE, (x, y, width, height), 1)

    def _render_mode(
        self, surface: pg.Surface, game_state: Dict[str, Any], label: str
    ) -> None:
        title = Text(Rect(14, 20, 100, 12), label, 12)
        title.render(surface)

        # メニュー項目とカーソルを表示
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        self._render_menu_items(
            surface,
            menu_items,
            cursor_index,
            start_y=45,
            item_height=14,
            vertical=False,
        )

        # 情報メッセージを表示
        info_message = game_state.get("info_message", "")
        if info_message:
            info_text = Text(Rect(10, 70, 108, 10), info_message, 8)
            info_text.color = Colors.GREEN
            info_text.render(surface)

        hint = Text(Rect(10, 100, 110, 10), "1/3:選択 2:実行", 8)
        hint.render(surface)

    def _render_flower_language(
        self, surface: pg.Surface, game_state: Dict[str, Any]
    ) -> None:
        title = Text(Rect(8, 20, 110, 12), "花言葉を選ぶ", 12)
        title.render(surface)

        # メニュー項目とカーソルを表示
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        self._render_menu_items(
            surface, menu_items, cursor_index, start_y=45, item_height=14
        )

        hint = Text(Rect(8, 100, 110, 10), "1/3:選択 2:決定", 8)
        hint.render(surface)

    def _render_death(self, surface: pg.Surface) -> None:
        title = Text(Rect(18, 20, 100, 12), "枯れてしまった…", 12)
        tip = Text(Rect(8, 40, 110, 10), "決定でタイトル", 8)
        title.render(surface)
        tip.render(surface)

    def _render_game_play(
        self, surface: pg.Surface, game_state: Dict[str, Any]
    ) -> None:
        """ゲームプレイ画面をレンダリング"""
        flower_stats = game_state.get("flower_stats")
        if not flower_stats:
            return

        # 花のスプライトを更新（表情で状態を表現）
        self._update_flower_sprite(flower_stats)

        # 操作説明を更新
        self._update_controls_text(flower_stats)

        # 右上に時間状態を表示
        paused = game_state.get("paused", False)
        scale = game_state.get("time_scale", 1.0)
        time_text = Text(
            Rect(80, 5, 44, 10), ("PAUSE" if paused else f"x{int(scale)}"), 8
        )
        time_text.render(surface)

        # 操作メッセージ表示
        info = game_state.get("info_message", "")
        invalid = game_state.get("invalid_message", "")
        if info:
            msg = Text(Rect(10, 78, 108, 10), info, 8)
            msg.render(surface)
        elif invalid:
            msg = Text(Rect(10, 78, 108, 10), invalid, 8)
            msg.render(surface)


        # メイン画面でメニュー項目を表示
        screen_state = game_state.get("screen_state", "")
        if screen_state == "MAIN":
            menu_items = game_state.get("menu_items", [])
            cursor_index = game_state.get("cursor_index", 0)
            if menu_items:
                # メニューを縦に並べて表示
                self._render_menu_items(
                    surface, menu_items, cursor_index, start_y=50, item_height=10
                )

        # すべてのコンポーネントをレンダリング（種選択画面用は除外）
        for component in self.components:
            if (
                component
                not in [
                    self.seed_selection_title, 
                    self.seed_navigation_hint,
                ]
                + self.seed_options
            ):
                component.render(surface)

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

    def _update_controls_text(self, stats: FlowerStats) -> None:
        """操作説明を更新"""
        if stats.is_fully_grown:
            self.controls_text.set_text("2:決定で花言葉/戻る")
        else:
            self.controls_text.set_text("1:左 2:決定 3:右")

    def _render_menu_items(
        self,
        surface: pg.Surface,
        menu_items: List[MenuItem],
        cursor_index: int,
        start_y: int = 40,
        item_height: int = 12,
        vertical: bool = True,
    ) -> None:
        """メニュー項目とカーソルを表示

        Args:
            surface: レンダリング先のサーフェス
            menu_items: メニュー項目のリスト
            cursor_index: 現在のカーソル位置
            start_y: メニュー開始Y座標
            item_height: メニュー項目の高さ
            vertical: 縦並び（True）または横並び（False）
        """
        if not menu_items:
            return

        for i, item in enumerate(menu_items):
            # 縦並びの場合
            if vertical:
                x = 20
                y = start_y + i * item_height
                cursor_x = 10
                cursor_y = y + 1
            # 横並びの場合
            else:
                # 項目の幅を動的に計算（最小30、ラベル長に応じて調整）
                item_width = max(30, len(item.label) * 6 + 10)
                x = 10 + sum(max(30, len(menu_items[j].label) * 6 + 10) for j in range(i))
                y = start_y
                cursor_x = x - 8
                cursor_y = y + 1

            # メニュー項目テキスト
            color = Colors.BLACK if item.enabled else Colors.GRAY
            text_width = 120 if vertical else max(30, len(item.label) * 6 + 5)
            item_text = Text(Rect(x, y, text_width, 10), item.label, 8)
            item_text.color = color
            item_text.render(surface)

            # カーソル表示（現在選択中の項目）
            if i == cursor_index and item.enabled:
                cursor = Text(Rect(cursor_x, cursor_y, 8, 8), "→", 8)
                cursor.render(surface)

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
