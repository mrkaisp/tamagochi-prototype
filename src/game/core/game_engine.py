import pygame as pg
from typing import Dict, Any, Optional
from ..entities.flower import Flower
from ..core.event_system import EventManager, EventType
from ..core.input_handler import InputHandler
from ..ui.display import DisplayManager
from ..ui.renderer import RenderManager
from ..data.config import config
from ..utils.helpers import Timer
from .screen_state import ScreenState
from ..utils.random_manager import get_rng
from ..ui.menu_system import MenuCursor, MenuItem


class GameEngine:
    """ゲームエンジンクラス"""

    def __init__(self):
        # システムの初期化
        self.event_manager = EventManager()
        self.input_handler = InputHandler(self.event_manager)
        self.display_manager = DisplayManager()
        self.render_manager = None  # 初期化時に作成

        # ゲーム状態
        self.flower = Flower()
        self.running = False
        self.paused = False
        self.seed_selection_mode = True  # 互換用フラグ（今後廃止予定）
        self.screen_state = ScreenState.TITLE

        # タイマー
        self.fps_timer = Timer(1.0 / config.display.fps, auto_reset=True)
        self.auto_save_timer = Timer(config.data.auto_save_interval, auto_reset=True)
        self.time_scale = 1.0
        self.mode_return_timer = Timer(0.8, auto_reset=False)
        self.mode_active = False

        # 行為制約
        self._nutrition_action_limit = 3
        self._nutrition_actions_in_current_hour = 0
        self._last_action_hour = 0
        self._nutrition_remaining_cached = self._nutrition_action_limit
        # 無効操作フィードバック
        self._invalid_message = ""
        self._invalid_message_timer = 0.0
        # 情報メッセージ
        self._info_message = ""
        self._info_message_timer = 0.0

        # 各画面のメニューカーソル
        self._cursors: Dict[ScreenState, Optional[MenuCursor]] = {}
        self._initialize_menu_cursors()

        # イベントハンドラーの設定
        self._setup_event_handlers()

    def _initialize_menu_cursors(self) -> None:
        """各画面のメニューカーソルを初期化"""
        from ..entities.flower import SeedType

        # 種選択画面
        self._cursors[ScreenState.SEED_SELECTION] = MenuCursor(
            [
                MenuItem(
                    "sun",
                    "太陽",
                    lambda: self._select_seed(SeedType.SUN),
                ),
                MenuItem("moon", "月", lambda: self._select_seed(SeedType.MOON)),
                MenuItem("wind", "風", lambda: self._select_seed(SeedType.WIND)),
                MenuItem(
                    "rain", "雨", lambda: self._select_seed(SeedType.RAIN)
                ),
            ]
        )

        # 時間設定画面
        self._cursors[ScreenState.TIME_SETTING] = MenuCursor(
            [
                MenuItem("pause", "一時停止", lambda: self._toggle_pause_setting()),
                MenuItem("speed", "時間スケール", lambda: self._cycle_time_scale()),
                MenuItem("confirm", "決定", lambda: self._confirm_time_setting()),
            ]
        )

        # メイン画面
        self._cursors[ScreenState.MAIN] = MenuCursor(
            [
                MenuItem(
                    "status",
                    "詳細情報",
                    lambda: self._goto_screen(ScreenState.STATUS),
                ),
                MenuItem(
                    "water", "水やり", lambda: self._goto_screen(ScreenState.MODE_WATER)
                ),
                MenuItem(
                    "light", "光", lambda: self._goto_screen(ScreenState.MODE_LIGHT)
                ),
                MenuItem(
                    "env", "環境整備", lambda: self._goto_screen(ScreenState.MODE_ENV)
                ),
                MenuItem(
                    "settings", "設定", lambda: self._goto_screen(ScreenState.SETTINGS)
                ),
            ]
        )

        # 設定画面
        self._cursors[ScreenState.SETTINGS] = MenuCursor(
            [
                MenuItem(
                    "time",
                    "時間設定変更",
                    lambda: self._goto_screen(ScreenState.TIME_SETTING),
                ),
                MenuItem("reset", "やりなおし", lambda: self._reset_game_confirm()),
                MenuItem("back", "戻る", lambda: self._goto_screen(ScreenState.MAIN)),
            ]
        )

        # ステータス画面
        self._cursors[ScreenState.STATUS] = MenuCursor(
            [
                MenuItem("back", "戻る", lambda: self._goto_screen(ScreenState.MAIN)),
            ]
        )

        # 水やりモード画面
        self._cursors[ScreenState.MODE_WATER] = MenuCursor(
            [
                MenuItem("water", "水やり", lambda: self._perform_water()),
                MenuItem("fertilizer", "肥料", lambda: self._perform_fertilizer()),
                MenuItem("back", "戻る", lambda: self._goto_screen(ScreenState.MAIN)),
            ]
        )

        # 光モード画面
        self._cursors[ScreenState.MODE_LIGHT] = MenuCursor(
            [
                MenuItem("light_on", "光 ON", lambda: self._perform_light_on()),
                MenuItem("light_off", "光 OFF", lambda: self._perform_light_off()),
                MenuItem("back", "戻る", lambda: self._goto_screen(ScreenState.MAIN)),
            ]
        )

        # 環境整備モード画面
        self._cursors[ScreenState.MODE_ENV] = MenuCursor(
            [
                MenuItem("weeds", "雑草除去", lambda: self._perform_remove_weeds()),
                MenuItem("pests", "害虫駆除", lambda: self._perform_remove_pests()),
                MenuItem("back", "戻る", lambda: self._goto_screen(ScreenState.MAIN)),
            ]
        )

        # 花言葉選択画面
        self._cursors[ScreenState.FLOWER_LANGUAGE] = MenuCursor(
            [
                MenuItem(
                    "like",
                    "「好き」を伝える",
                    lambda: self._select_flower_language_like(),
                ),
                MenuItem(
                    "dislike",
                    "「嫌い」を伝える",
                    lambda: self._select_flower_language_dislike(),
                ),
            ]
        )

        # タイトル画面・死亡画面はカーソル不要（ボタン2で次へ）
        self._cursors[ScreenState.TITLE] = None
        self._cursors[ScreenState.DEATH] = None

    def _setup_event_handlers(self) -> None:
        """イベントハンドラーを設定"""
        self.event_manager.subscribe(EventType.FLOWER_WATERED, self._on_flower_watered)
        self.event_manager.subscribe(
            EventType.FLOWER_LIGHT_GIVEN, self._on_flower_light_given
        )
        self.event_manager.subscribe(
            EventType.FLOWER_WEEDS_REMOVED, self._on_flower_weeds_removed
        )
        self.event_manager.subscribe(
            EventType.FLOWER_PESTS_REMOVED, self._on_flower_pests_removed
        )
        self.event_manager.subscribe(EventType.SEED_SELECTED, self._on_seed_selected)
        self.event_manager.subscribe(
            EventType.FLOWER_GROWTH_CHANGED, self._on_flower_growth_changed
        )
        self.event_manager.subscribe(
            EventType.FLOWER_WITHERED, self._on_flower_withered
        )
        self.event_manager.subscribe(
            EventType.FLOWER_COMPLETED, self._on_flower_completed
        )
        self.event_manager.subscribe(EventType.GAME_RESET, self._on_game_reset)
        # 新規アクション
        self.event_manager.subscribe(EventType.FERTILIZER_GIVEN, self._on_fertilizer)
        self.event_manager.subscribe(EventType.MENTAL_LIKE, self._on_mental_like)
        self.event_manager.subscribe(EventType.MENTAL_DISLIKE, self._on_mental_dislike)
        self.event_manager.subscribe(EventType.INVALID_ACTION, self._on_invalid_action)

    def initialize(self) -> bool:
        """ゲームエンジンを初期化"""
        try:
            pg.init()
            # フォントシステムを初期化
            pg.font.init()
            self.display_manager.initialize()
            # RNG seed initialize (reproducibility)
            get_rng().set_seed(config.data.random_seed)

            # RenderManagerを初期化（フォント初期化後）
            self.render_manager = RenderManager()
            self.running = True
            return True
        except Exception as e:
            print(f"Game engine initialization failed: {e}")
            return False

    def run(self) -> None:
        """ゲームループを実行"""
        clock = pg.time.Clock()

        while self.running:
            dt = clock.tick(config.display.fps) / 1000.0
            dt *= self.time_scale

            # イベント処理（カーソルシステムでは種選択も通常ナビゲーション）
            if not self.input_handler.handle_events(False):
                self.running = False
                break

            if not self.paused:
                # ゲーム状態の更新
                self.update(dt)

            # レンダリング
            self.render()

    def update(self, dt: float) -> None:
        """ゲーム状態を更新"""
        # ゲームプレイ中は花を更新（メイン画面とモード画面の両方）
        should_update_flower = (
            self.screen_state in (
                ScreenState.MAIN,
                ScreenState.MODE_WATER,
                ScreenState.MODE_LIGHT,
                ScreenState.MODE_ENV,
                ScreenState.STATUS
            ) 
            and not self.paused
        )
        
        if should_update_flower:
            # 成長段階の変化を検知するため、更新前の段階を保持
            previous_stage = self.flower.stats.growth_stage
            # 早送り/一時停止に応じた更新
            self.flower.update(dt)
            # 成長段階の変更イベントを発行
            if previous_stage != self.flower.stats.growth_stage:
                self.event_manager.emit_simple(
                    EventType.FLOWER_GROWTH_CHANGED,
                    old_stage=previous_stage.value,
                    new_stage=self.flower.stats.growth_stage.value,
                )
            # 枯死判定→自動遷移
            if not self.flower.is_alive:
                self.event_manager.emit_simple(EventType.FLOWER_WITHERED)

        # レンダラーを更新
        if self.render_manager:
            self.render_manager.update(dt)

        # 自動セーブ
        if self.auto_save_timer.update(dt) and not self.seed_selection_mode:
            self.flower.save()

        # モード画面からの自動復帰
        if self.mode_active and self.mode_return_timer.update(dt):
            self.screen_state = ScreenState.MAIN
            self.mode_active = False

        # 行為制約: ゲーム内時間（時）を更新し、同一時内のカウンタ初期化
        current_hour = int(self.flower.stats.age_seconds // 3600)
        if current_hour != self._last_action_hour:
            self._last_action_hour = current_hour
            self._nutrition_actions_in_current_hour = 0
            self._nutrition_remaining_cached = self._nutrition_action_limit
        # 無効操作メッセージの寿命
        if self._invalid_message_timer > 0.0:
            self._invalid_message_timer = max(0.0, self._invalid_message_timer - dt)
            if self._invalid_message_timer == 0.0:
                self._invalid_message = ""
        if self._info_message_timer > 0.0:
            self._info_message_timer = max(0.0, self._info_message_timer - dt)
            if self._info_message_timer == 0.0:
                self._info_message = ""

    def render(self) -> None:
        """ゲームをレンダリング"""
        # 論理サーフェスを取得
        if self.render_manager:
            logical_surface = self.display_manager.get_logical_surface()

            # ゲーム状態を準備
            cursor = self.get_current_cursor()
            # get_game_state()を使用（ステータス画面用の辞書データ含む）
            game_state_dict = self.get_game_state()
            # レンダリング用のゲーム状態（FlowerStatsオブジェクトも含む）
            game_state = {
                "flower_stats": self.flower.stats,  # FlowerStatsオブジェクト（game_play用）
                "flower_stats_dict": game_state_dict["flower_stats"],  # 辞書（status画面用）
                "needs_attention": game_state_dict["needs_attention"],
                "is_alive": game_state_dict["is_alive"],
                "seed_selection_mode": game_state_dict["seed_selection_mode"],
                "paused": game_state_dict["paused"],
                "running": game_state_dict["running"],
                "info_message": game_state_dict["info_message"],
                "invalid_message": game_state_dict["invalid_message"],
                "screen_state": self.screen_state.name,
                "time_scale": self.time_scale,
                "nutrition_remaining": self._nutrition_remaining_cached,
                "nutrition_limit": self._nutrition_action_limit,
                "cursor": cursor,
                "cursor_index": cursor.index if cursor else 0,
                "menu_items": cursor.items if cursor else [],
            }

            # レンダリング
            self.render_manager.render(logical_surface, game_state)

            # ディスプレイに表示
            self.display_manager.render()

    def pause(self) -> None:
        """ゲームを一時停止"""
        self.paused = True

    def resume(self) -> None:
        """ゲームを再開"""
        self.paused = False

    def quit(self) -> None:
        """ゲームを終了"""
        self.running = False
        if not self.seed_selection_mode:
            self.flower.save()
        pg.quit()

    def reset_game(self) -> None:
        """ゲームをリセット"""
        self.flower.reset()
        self.screen_state = ScreenState.TITLE
        self.seed_selection_mode = True

    def get_game_state(self) -> Dict[str, Any]:
        """ゲーム状態を取得"""
        # ステータス画面用の詳細情報を含む花の情報
        flower_stats_dict = {
            "seed_type": self.flower.stats.seed_type.value,
            "growth_stage": self.flower.stats.growth_stage_display,
            "age_formatted": self.flower.stats.age_formatted,
            "water_level": self.flower.stats.water_level,
            "light_level": self.flower.stats.light_level,
            "environment_level": self.flower.stats.environment_level,
            "mental_level": self.flower.stats.mental_level,
            "weed_count": self.flower.stats.weed_count,
            "pest_count": self.flower.stats.pest_count,
        }
        
        return {
            "flower_stats": flower_stats_dict,
            "needs_attention": self.flower.needs_attention,
            "is_alive": self.flower.is_alive,
            "seed_selection_mode": self.seed_selection_mode,
            "paused": self.paused,
            "running": self.running,
            "info_message": self._info_message if self._info_message_timer > 0 else "",
            "invalid_message": self._invalid_message if self._invalid_message_timer > 0 else "",
        }

    # イベントハンドラー
    def _on_flower_watered(self, event) -> None:
        """花に水を与えた時の処理（レガシー・使用されていない）"""
        # 現在はメニューから_perform_water()を直接呼び出すため、このハンドラーは使用されない
        pass

    def _on_flower_light_given(self, event) -> None:
        """花に光を与えた時の処理"""
        if self._is_sleep_time():
            self._emit_invalid("睡眠中は操作できません")
            return
        if self.screen_state in (ScreenState.MAIN, ScreenState.MODE_LIGHT):
            self.flower.give_light()
            self.screen_state = ScreenState.MODE_LIGHT
            self.mode_return_timer.reset()
            self.mode_active = True

    def _on_flower_weeds_removed(self, event) -> None:
        """花の雑草を除去した時の処理"""
        if self._is_sleep_time():
            self._emit_invalid("睡眠中は操作できません")
            return
        if self.screen_state in (ScreenState.MAIN, ScreenState.MODE_ENV):
            self.flower.remove_weeds()
            self.screen_state = ScreenState.MODE_ENV
            self.mode_return_timer.reset()
            self.mode_active = True

    def _on_flower_pests_removed(self, event) -> None:
        """花の害虫を駆除した時の処理"""
        if self._is_sleep_time():
            self._emit_invalid("睡眠中は操作できません")
            return
        if self.screen_state in (ScreenState.MAIN, ScreenState.MODE_ENV):
            self.flower.remove_pests()
            self.screen_state = ScreenState.MODE_ENV
            self.mode_return_timer.reset()
            self.mode_active = True

    def _on_fertilizer(self, event) -> None:
        if not self._can_perform_nutrition_action():
            self._emit_invalid("栄養行為は同一時間内で3回まで")
            return
        if self._is_sleep_time():
            self._emit_invalid("睡眠中は操作できません")
            return
        if self.screen_state in (ScreenState.MAIN, ScreenState.MODE_WATER):
            self.flower.stats.fertilize()
            self.screen_state = ScreenState.MODE_WATER
            self.mode_return_timer.reset()
            self.mode_active = True
            self._on_nutrition_action()

    def _on_mental_like(self, event) -> None:
        if self._is_sleep_time():
            self._emit_invalid("睡眠中は操作できません")
            return
        self.flower.stats.adjust_mental(+5)

    def _on_mental_dislike(self, event) -> None:
        if self._is_sleep_time():
            self._emit_invalid("睡眠中は操作できません")
            return
        self.flower.stats.adjust_mental(-5)

    def _on_invalid_action(self, event) -> None:
        msg = event.data.get("message", "") if event and event.data else ""
        self._invalid_message = msg
        self._invalid_message_timer = 2.0

    def _on_seed_selected(self, event) -> None:
        """種を選択した時の処理"""
        if self.screen_state in (ScreenState.SEED_SELECTION, ScreenState.TITLE):
            from ..entities.flower import SeedType

            seed_type_name = event.data.get("seed_type", "太陽")
            seed_type = SeedType(seed_type_name)
            self.flower.select_seed(seed_type)
            # 次は時間設定へ
            self.screen_state = ScreenState.TIME_SETTING
            self.seed_selection_mode = False
            print(f"{seed_type_name}の種を選択しました。時間設定へ進みます。")

    def _on_flower_growth_changed(self, event) -> None:
        """花の成長段階が変化した時の処理"""
        print(f"花が成長しました: {self.flower.stats.growth_stage_display}")

        # 花が完成した場合の特別な処理
        if self.flower.stats.is_fully_grown:
            self.event_manager.emit_simple(EventType.FLOWER_COMPLETED)

    def _on_flower_withered(self, event) -> None:
        """花が枯れた時の処理"""
        print("花が枯れてしまいました。")
        self.screen_state = ScreenState.DEATH

    def _on_flower_completed(self, event) -> None:
        """花が完成した時の処理"""
        print("🌸 花が完成しました！花言葉選択へ。")
        self.screen_state = ScreenState.FLOWER_LANGUAGE

    def _on_game_reset(self, event) -> None:
        """ゲームリセットの処理"""
        print("ゲームをリセットします...")
        self.reset_game()
        # ログファイルをリセット
        self._reset_log_file()
        print("新しい花の育成を開始します！")

    def _reset_log_file(self) -> None:
        """ログファイルをリセット"""
        import logging
        import os

        # 現在のログファイルを削除
        log_file = "flower_game.log"
        if os.path.exists(log_file):
            os.remove(log_file)

        # ログハンドラーをリセット
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logger.removeHandler(handler)

        # 新しいファイルハンドラーを追加
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        print("ログファイルをリセットしました。")

    # --- 画面ナビゲーション ---
    def _setup_event_handlers(self) -> None:
        """イベントハンドラーを設定"""
        self.event_manager.subscribe(EventType.FLOWER_WATERED, self._on_flower_watered)
        self.event_manager.subscribe(
            EventType.FLOWER_LIGHT_GIVEN, self._on_flower_light_given
        )
        self.event_manager.subscribe(
            EventType.FLOWER_WEEDS_REMOVED, self._on_flower_weeds_removed
        )
        self.event_manager.subscribe(
            EventType.FLOWER_PESTS_REMOVED, self._on_flower_pests_removed
        )
        self.event_manager.subscribe(EventType.SEED_SELECTED, self._on_seed_selected)
        self.event_manager.subscribe(
            EventType.FLOWER_GROWTH_CHANGED, self._on_flower_growth_changed
        )
        self.event_manager.subscribe(
            EventType.FLOWER_WITHERED, self._on_flower_withered
        )
        self.event_manager.subscribe(
            EventType.FLOWER_COMPLETED, self._on_flower_completed
        )
        self.event_manager.subscribe(EventType.GAME_RESET, self._on_game_reset)
        # ナビゲーション
        self.event_manager.subscribe(EventType.NAV_LEFT, self._on_nav_left)
        self.event_manager.subscribe(EventType.NAV_RIGHT, self._on_nav_right)
        self.event_manager.subscribe(EventType.NAV_CONFIRM, self._on_nav_confirm)
        self.event_manager.subscribe(EventType.NAV_CANCEL, self._on_nav_cancel)
        # 時間制御
        self.event_manager.subscribe(
            EventType.TIME_TOGGLE_PAUSE, self._on_time_toggle_pause
        )
        self.event_manager.subscribe(
            EventType.TIME_SPEED_NORMAL, self._on_time_speed_normal
        )
        self.event_manager.subscribe(
            EventType.TIME_SPEED_FAST, self._on_time_speed_fast
        )

    def _on_nav_left(self, event) -> None:
        """ナビゲーション左ボタン（カーソルを前へ移動）"""
        cursor = self._cursors.get(self.screen_state)
        if cursor:
            cursor.move_prev()

    def _on_nav_right(self, event) -> None:
        """ナビゲーション右ボタン（カーソルを次へ移動）"""
        cursor = self._cursors.get(self.screen_state)
        if cursor:
            cursor.move_next()

    def _on_nav_confirm(self, event) -> None:
        """ナビゲーション決定ボタン（カーソルで選択中の項目を実行）"""
        # タイトル画面と死亡画面は特別処理（カーソルなし）
        if self.screen_state == ScreenState.TITLE:
            self.screen_state = ScreenState.SEED_SELECTION
            return
        elif self.screen_state == ScreenState.DEATH:
            self.reset_game()
            return

        # カーソルがある画面では、選択中の項目のアクションを実行
        cursor = self._cursors.get(self.screen_state)
        if cursor:
            cursor.select()

    def _is_sleep_time(self) -> bool:
        # 仮のゲーム内時間（分解能: 時）
        hour = int((self.flower.stats.age_seconds // 3600) % 24)
        start = config.game.sleep_start_hour
        end = config.game.sleep_end_hour
        if start <= end:
            return start <= hour < end
        else:
            return hour >= start or hour < end

    def _can_perform_nutrition_action(self) -> bool:
        # テスト用オプション: 制限を無効化
        if config.game.nutrition_limit_disabled:
            return True
        # 1時間内：3回まで
        return self._nutrition_actions_in_current_hour < self._nutrition_action_limit

    def _on_nutrition_action(self) -> None:
        self._nutrition_actions_in_current_hour += 1
        remaining = max(
            0, self._nutrition_action_limit - self._nutrition_actions_in_current_hour
        )
        self._nutrition_remaining_cached = remaining
        if remaining > 0:
            self._emit_info(f"あと{remaining}回まで栄養行為が可能")
        else:
            self._emit_info("今はこれ以上栄養行為ができません")

    def _emit_invalid(self, message: str) -> None:
        self._invalid_message = message
        self._invalid_message_timer = 2.0

    def _emit_info(self, message: str, duration: float = 2.0) -> None:
        self._info_message = message
        self._info_message_timer = duration

    def _confirm_time_setting(self) -> None:
        """時間設定画面で決定した際の処理"""
        # ここでは time_scale や paused 状態を既存入力イベントから決定済みとみなし、
        # 単純にメイン画面へ戻す。今後 UI から値を受け取る際はこの関数を拡張する。
        self.screen_state = ScreenState.MAIN

    def _on_nav_cancel(self, event) -> None:
        if self.screen_state in (
            ScreenState.SEED_SELECTION,
            ScreenState.TIME_SETTING,
            ScreenState.SETTINGS,
            ScreenState.STATUS,
        ):
            self.screen_state = (
                ScreenState.MAIN if self.flower.stats.seed_type else ScreenState.TITLE
            )

    # --- 時間制御 ---
    def _on_time_toggle_pause(self, event) -> None:
        self.paused = not self.paused

    def _on_time_speed_normal(self, event) -> None:
        self.time_scale = 1.0

    def _on_time_speed_fast(self, event) -> None:
        self.time_scale = 4.0

    # --- メニューアクションヘルパー ---
    def _select_seed(self, seed_type) -> None:
        """種を選択"""
        self.flower.select_seed(seed_type)
        self.screen_state = ScreenState.TIME_SETTING
        self.seed_selection_mode = False
        print(f"{seed_type.value}の種を選択しました。時間設定へ進みます。")

    def _toggle_pause_setting(self) -> None:
        """時間設定画面で一時停止を切り替え"""
        self.paused = not self.paused
        state = "ON" if self.paused else "OFF"
        self._emit_info(f"一時停止: {state}")

    def _cycle_time_scale(self) -> None:
        """時間スケールを循環変更"""
        if self.time_scale == 1.0:
            self.time_scale = 4.0
        elif self.time_scale == 4.0:
            self.time_scale = 0.25
        else:
            self.time_scale = 1.0
        self._emit_info(f"時間スケール: x{self.time_scale:g}")

    def _goto_screen(self, target_screen: ScreenState) -> None:
        """指定画面へ遷移"""
        self.screen_state = target_screen
        # 画面遷移時にカーソルをリセット
        cursor = self._cursors.get(target_screen)
        if cursor:
            cursor.reset()

    def _reset_game_confirm(self) -> None:
        """ゲームリセットを実行"""
        self.event_manager.emit_simple(EventType.GAME_RESET)
        self.screen_state = ScreenState.TITLE

    def _perform_water(self) -> None:
        """水やり実行（睡眠時間に関係なく常時可能）"""
        # 栄養行為の制限チェック
        if not self._can_perform_nutrition_action():
            self._emit_invalid("栄養行為は同一時間内で3回まで")
            return
        
        # 水分チェック
        if self.flower.stats.water_level >= 90:
            self._emit_info("もう十分水分があります")
        else:
            self.flower.water()
            self._on_nutrition_action()
            self._emit_info("水をあげました！")

    def _perform_fertilizer(self) -> None:
        """肥料実行（睡眠時間に関係なく常時可能）"""
        # 栄養行為の制限チェック
        if not self._can_perform_nutrition_action():
            self._emit_invalid("栄養行為は同一時間内で3回まで")
            return
        
        if self.flower.stats.water_level >= 90:
            self._emit_info("もう十分栄養があります")
        else:
            self.flower.stats.fertilize()
            self._on_nutrition_action()
            self._emit_info("肥料をあげました！")

    def _perform_light_on(self) -> None:
        """光ON実行"""
        # 睡眠時間チェック
        if self._is_sleep_time():
            self._emit_invalid("睡眠中は操作できません")
            return
        
        if self.flower.stats.light_level >= 90:
            self._emit_info("もう十分光があります")
        else:
            self.flower.give_light()
            self._emit_info("光を当てました！")

    def _perform_light_off(self) -> None:
        """光OFF実行（実装予定）"""
        # TODO: 光OFFのイベントを追加
        self._emit_info("光をOFFにしました")

    def _perform_remove_weeds(self) -> None:
        """雑草除去実行"""
        # 睡眠時間チェック
        if self._is_sleep_time():
            self._emit_invalid("睡眠中は操作できません")
            return
        
        if self.flower.stats.weed_count == 0:
            self._emit_info("雑草はありません")
        else:
            self.flower.remove_weeds()
            self._emit_info("雑草を除去しました！")

    def _perform_remove_pests(self) -> None:
        """害虫駆除実行"""
        # 睡眠時間チェック
        if self._is_sleep_time():
            self._emit_invalid("睡眠中は操作できません")
            return
        
        if self.flower.stats.pest_count == 0:
            self._emit_info("害虫はいません")
        else:
            self.flower.remove_pests()
            self._emit_info("害虫を駆除しました！")

    def _select_flower_language_like(self) -> None:
        """花言葉選択：好き"""
        self.event_manager.emit_simple(EventType.MENTAL_LIKE)
        self.screen_state = ScreenState.MAIN

    def _select_flower_language_dislike(self) -> None:
        """花言葉選択：嫌い"""
        self.event_manager.emit_simple(EventType.MENTAL_DISLIKE)
        self.screen_state = ScreenState.MAIN

    def get_current_cursor(self) -> Optional[MenuCursor]:
        """現在の画面のカーソルを取得"""
        return self._cursors.get(self.screen_state)
