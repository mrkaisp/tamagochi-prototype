import pygame as pg
from typing import List, Dict, Any, Optional
from .components import UIComponent, Icon, Text, Colors, Rect
from ..entities.flower import FlowerStats, SeedType, GrowthStage
from .font_manager import get_font_manager
from ..utils.helpers import format_time_digital
from .menu_system import MenuCursor, MenuItem

# 定数定義
DISPLAY_MARGIN = 2
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240
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
        # 240×240画面に収まるサイズで中央に配置
        self.flower_sprite = Icon(Rect(68, 60, 104, 104), "flower")

        # 種選択画面用
        self.seed_selection_title = Text(
            Rect(40, 24, 160, 26), "種を選択してください", 16
        )

        # コンポーネントリストに追加
        self.components.extend(
            [
                self.flower_sprite,
                self.seed_selection_title,
            ]
        )

    def render(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        """ゲーム状態をレンダリング"""
        # 画面状態によって表示を切り替え
        screen_state = game_state.get("screen_state", "MAIN")
        
        # メイン画面以外は白背景でクリア
        # メイン画面は _render_game_play 内で光の状態に応じた背景色を設定
        if screen_state != "MAIN":
            surface.fill(Colors.WHITE)
        
        if screen_state == "TITLE":
            self._render_title(surface, game_state)
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
        title = Text(Rect(40, 24, 160, 26), "種を選択してください", 16)
        title.render(surface)

        # メニュー項目とカーソルを表示
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        self._render_menu_items(
            surface, menu_items, cursor_index, start_y=75, item_height=26
        )

    def _render_title(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        # ふんわりした背景グラデーション
        for y in range(240):
            color = (255, 245 - y // 6, 250 - y // 5)
            surface.fill(color, pg.Rect(0, y, 240, 1))

        # 装飾フレーム
        pg.draw.rect(surface, (230, 210, 235), (6, 6, 228, 228))
        pg.draw.rect(surface, (180, 140, 190), (10, 10, 220, 220), 2)

        # コーナーの花飾り
        for x, y in ((26, 26), (214, 26), (26, 214), (214, 214)):
            pg.draw.circle(surface, (255, 210, 230), (x, y), 10)
            pg.draw.circle(surface, (255, 170, 210), (x, y), 6)
            pg.draw.circle(surface, (255, 240, 120), (x, y), 3)

        # タイトル文字（影付き）
        title_shadow = Text(Rect(0, 74, 240, 44), "ふらわっち", 32, center=True)
        title_shadow.color = (140, 100, 140)
        title_shadow.render(surface)
        title = Text(Rect(0, 70, 240, 44), "ふらわっち", 32, center=True)
        title.color = (90, 170, 120)
        title.render(surface)

        subtitle = Text(Rect(0, 108, 240, 18), "おはなをそだてよう", 12, center=True)
        subtitle.color = (120, 120, 120)
        subtitle.render(surface)
        
        # メニュー項目とカーソルを表示
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        self._render_menu_items(
            surface, menu_items, cursor_index, start_y=150, item_height=24
        )

    def _render_time_setting(
        self, surface: pg.Surface, game_state: Dict[str, Any]
    ) -> None:
        title = Text(Rect(70, 20, 100, 22), "時間設定", 12)
        title.render(surface)

        paused = game_state.get("paused", False)
        time_scale = game_state.get("time_scale", 1.0)
        status_text = Text(
            Rect(20, 50, 200, 18),
            f"一時停止: {'ON' if paused else 'OFF'}  時間: x{time_scale:g}",
            8,
        )
        status_text.render(surface)

        # メニュー項目とカーソルを表示
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        self._render_menu_items(
            surface, menu_items, cursor_index, start_y=85, item_height=26
        )

    def _render_settings(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        title = Text(Rect(90, 40, 60, 22), "設定", 12)
        title.render(surface)

        # メニュー項目とカーソルを表示
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        self._render_menu_items(
            surface, menu_items, cursor_index, start_y=85, item_height=26
        )

    def _render_status(self, surface: pg.Surface, game_state: Dict[str, Any]) -> None:
        """ステータス画面をレンダリング（モダンデザイン）"""
        # グラデーション背景
        for i in range(240):
            color_val = 25 + int(i * 0.2)
            pg.draw.line(surface, (color_val, color_val + 15, color_val + 10), (0, i), (240, i))
        
        # タイトルバー
        pg.draw.rect(surface, (20, 35, 30), (0, 0, 240, 40))
        pg.draw.line(surface, (100, 200, 150), (0, 40), (240, 40), 2)
        title = Text(Rect(0, 8, 240, 32), "詳細ステータス", 24, center=True)
        title.color = (200, 255, 220)
        title.render(surface)
        
        flower_stats = game_state.get("flower_stats_dict", {})
        y = 38
        
        # 基本情報カード
        pg.draw.rect(surface, (45, 65, 55), (8, y, 224, 52))
        pg.draw.rect(surface, (120, 180, 150), (8, y, 224, 52), 2)
        
        seed_text = Text(Rect(16, y + 6, 208, 20), f"{flower_stats.get('seed_type', '未選択')}", 16)
        seed_text.color = (255, 255, 150)
        seed_text.render(surface)
        
        stage_text = Text(Rect(16, y + 28, 208, 20), f"成長: {flower_stats.get('growth_stage', '不明')}", 16)
        stage_text.color = (200, 255, 200)
        stage_text.render(surface)
        
        age_text = Text(Rect(16, y + 50, 208, 20), f"年齢: {flower_stats.get('age_formatted', '0秒')}", 16)
        age_text.color = (180, 220, 255)
        age_text.render(surface)
        
        y += 70
        
        # ステータスバー
        water_level = flower_stats.get('water_level', 0)
        light_level = flower_stats.get('light_level', 0)
        mental_level = flower_stats.get('mental_level', 0)
        
        self._render_modern_stat(surface, 8, y, "水分", water_level, (100, 180, 255))
        y += 28
        self._render_modern_stat(surface, 8, y, "光量", light_level, (255, 220, 100))
        y += 28
        self._render_modern_stat(surface, 8, y, "心情", mental_level, (255, 150, 200))
        y += 35
        
        # メニュー（「戻る」選択肢）
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        if menu_items:
            self._render_menu_items(surface, menu_items, cursor_index, start_y=200, item_height=18)
    
    def _render_modern_stat(self, surface: pg.Surface, x: int, y: int, label: str, value: float, color: tuple) -> None:
        """モダンなステータス表示"""
        label_text = Text(Rect(x + 8, y, 60, 20), label, 16)
        label_text.color = (180, 180, 180)
        label_text.render(surface)
        
        value_text = Text(Rect(x + 70, y, 50, 20), f"{value:.0f}%", 16)
        value_text.color = color
        value_text.render(surface)
        
        self._render_progress_bar(surface, x + 120, y + 2, 110, 16, value, 100)
    
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
        title = Text(Rect(70, 40, 100, 22), label, 12)
        title.render(surface)

        # メニュー項目とカーソルを表示
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        self._render_menu_items(
            surface,
            menu_items,
            cursor_index,
            start_y=85,
            item_height=26,
            vertical=False,
        )

        # 情報メッセージと無効メッセージを表示
        info_message = game_state.get("info_message", "")
        invalid_message = game_state.get("invalid_message", "")
        if info_message:
            info_text = Text(Rect(20, 130, 200, 18), info_message, 8)
            info_text.color = Colors.GREEN
            info_text.render(surface)
        elif invalid_message:
            invalid_text = Text(Rect(20, 130, 200, 18), invalid_message, 8)
            invalid_text.color = Colors.RED
            invalid_text.render(surface)

    def _render_flower_language(
        self, surface: pg.Surface, game_state: Dict[str, Any]
    ) -> None:
        title = Text(Rect(50, 40, 140, 22), "花言葉を選ぶ", 12)
        title.render(surface)

        # メニュー項目とカーソルを表示
        menu_items = game_state.get("menu_items", [])
        cursor_index = game_state.get("cursor_index", 0)
        self._render_menu_items(
            surface, menu_items, cursor_index, start_y=85, item_height=26
        )

    def _render_death(self, surface: pg.Surface) -> None:
        title = Text(Rect(50, 100, 140, 22), "枯れてしまった…", 12)
        title.render(surface)

    def _render_game_play(
        self, surface: pg.Surface, game_state: Dict[str, Any]
    ) -> None:
        """ゲームプレイ画面をレンダリング"""
        flower_stats = game_state.get("flower_stats")
        if not flower_stats:
            return
        
        # 光の状態に応じて背景色を変更
        if flower_stats.is_light_on:
            # 光ON時: 明るい黄色がかった背景（光が当たっている感じ）
            surface.fill((255, 255, 240))  # 薄い黄色
        else:
            # 光OFF時: 薄暗い背景（光がない感じ）
            surface.fill((200, 200, 200))  # 薄暗いグレー

        # 花のスプライトを更新（表情で状態を表現）
        self._update_flower_sprite(flower_stats)

        # 上部に時間・キャラ名・時間倍率を1行で表示
        paused = game_state.get("paused", False)
        scale = game_state.get("time_scale", 1.0)
        flower_stats = game_state.get("flower_stats")
        if flower_stats:
            clock_text = flower_stats.age_digital
            character_label = flower_stats.character_label
            scale_text = "PAUSE" if paused else f"x{int(scale)}"

            clock_display = Text(Rect(6, 8, 60, 16), clock_text, 8)
            clock_display.render(surface)

            name_text = Text(Rect(66, 8, 108, 16), character_label, 8, center=True)
            name_text.color = Colors.BLACK
            name_text.render(surface)

            time_text = Text(Rect(176, 8, 58, 16), scale_text, 8, center=True)
            time_text.render(surface)

        # 操作メッセージ表示
        info = game_state.get("info_message", "")
        invalid = game_state.get("invalid_message", "")
        if info:
            msg = Text(Rect(20, 145, 200, 18), info, 8)
            msg.render(surface)
        elif invalid:
            msg = Text(Rect(20, 145, 200, 18), invalid, 8)
            msg.render(surface)


        # メイン画面でメニュー項目を表示（画面下部に配置）
        screen_state = game_state.get("screen_state", "")
        if screen_state == "MAIN":
            menu_items = game_state.get("menu_items", [])
            cursor_index = game_state.get("cursor_index", 0)
            if menu_items:
                # メニューを縦に並べて表示（キャラクターと重ならないように画面下部に配置）
                # キャラクターは Y=80-160 を使用、メニューは Y=170 以降に配置
                self._render_menu_items(
                    surface, menu_items, cursor_index, start_y=170, item_height=18
                )

        # すべてのコンポーネントをレンダリング（種選択画面用は除外）
        for component in self.components:
            if component != self.seed_selection_title:
                component.render(surface)

    def _update_flower_sprite(self, stats: FlowerStats) -> None:
        """花のスプライトを更新（擬人化キャラクター）"""
        # 成長段階に応じてスプライト名を設定
        sprite_name = self._get_sprite_name(stats)
        self.flower_sprite.set_icon(sprite_name)
        # 成長段階に応じてサイズを調整（240×240画面に収まるサイズ）
        if stats.growth_stage == GrowthStage.SEED:
            self.flower_sprite.rect = Rect(64, 52, 112, 112)
        else:
            self.flower_sprite.rect = Rect(72, 60, 96, 96)
        # 状態情報を渡して擬人化キャラクターを描画
        self.flower_sprite.set_character_state(stats)

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
                x = 40
                y = start_y + i * item_height
                cursor_x = 20
                cursor_y = y + 2
            # 横並びの場合
            else:
                # 項目の幅を動的に計算（最小56、ラベル長に応じて調整）
                item_width = max(56, len(item.label) * 11 + 18)
                x = 20 + sum(max(56, len(menu_items[j].label) * 11 + 18) for j in range(i))
                y = start_y
                cursor_x = x - 15
                cursor_y = y + 2

            # メニュー項目テキスト
            color = Colors.BLACK if item.enabled else Colors.GRAY
            text_width = 200 if vertical else max(56, len(item.label) * 11 + 10)
            item_text = Text(Rect(x, y, text_width, 18), item.label, 8)
            item_text.color = color
            item_text.render(surface)

            # カーソル表示（現在選択中の項目）
            if i == cursor_index and item.enabled:
                cursor = Text(Rect(cursor_x, cursor_y, 15, 15), "→", 8)
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
