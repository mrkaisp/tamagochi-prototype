"""メニューとカーソルシステム"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Callable, Any


@dataclass
class MenuItem:
    """メニュー項目"""

    id: str  # 項目の識別子
    label: str  # 表示テキスト
    action: Optional[Callable[[], Any]] = None  # 選択時に実行するアクション
    enabled: bool = True  # 選択可能かどうか


class MenuCursor:
    """メニューカーソル管理クラス"""

    def __init__(self, items: List[MenuItem]) -> None:
        """
        Args:
            items: メニュー項目のリスト
        """
        self._items = items
        self._index = 0

    @property
    def items(self) -> List[MenuItem]:
        """メニュー項目のリスト"""
        return self._items

    @property
    def index(self) -> int:
        """現在のカーソル位置（インデックス）"""
        return self._index

    @property
    def current_item(self) -> Optional[MenuItem]:
        """現在選択中の項目"""
        if 0 <= self._index < len(self._items):
            return self._items[self._index]
        return None

    def move_next(self) -> None:
        """カーソルを次の項目へ移動（循環）"""
        if not self._items:
            return
        self._index = (self._index + 1) % len(self._items)
        # 無効な項目はスキップ
        self._skip_disabled_forward()

    def move_prev(self) -> None:
        """カーソルを前の項目へ移動（循環）"""
        if not self._items:
            return
        self._index = (self._index - 1) % len(self._items)
        # 無効な項目はスキップ
        self._skip_disabled_backward()

    def _skip_disabled_forward(self) -> None:
        """無効な項目を前方向にスキップ"""
        max_iterations = len(self._items)
        for _ in range(max_iterations):
            if self.current_item and self.current_item.enabled:
                break
            self._index = (self._index + 1) % len(self._items)

    def _skip_disabled_backward(self) -> None:
        """無効な項目を後方向にスキップ"""
        max_iterations = len(self._items)
        for _ in range(max_iterations):
            if self.current_item and self.current_item.enabled:
                break
            self._index = (self._index - 1) % len(self._items)

    def reset(self) -> None:
        """カーソルを最初の項目にリセット"""
        self._index = 0
        self._skip_disabled_forward()

    def select(self) -> Optional[Any]:
        """現在の項目を選択し、アクションを実行"""
        item = self.current_item
        if item and item.enabled and item.action:
            return item.action()
        return None

    def update_items(self, items: List[MenuItem]) -> None:
        """メニュー項目を更新し、カーソル位置を調整"""
        self._items = items
        # カーソル位置が範囲外になった場合はリセット
        if self._index >= len(self._items):
            self.reset()
        else:
            # 現在の位置が無効な項目の場合はスキップ
            if self.current_item and not self.current_item.enabled:
                self._skip_disabled_forward()
