"""ボタンレイアウト定義モジュール"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pygame as pg


@dataclass(frozen=True)
class ButtonLayout:
    """左/決定/右ボタンのキー割当を保持する"""

    left: int
    confirm: int
    right: int


# 主要ボタン（ハードウェア準拠: 1/2/3キー）
PRIMARY_BUTTONS = ButtonLayout(left=pg.K_1, confirm=pg.K_2, right=pg.K_3)

# 代替入力（PC向け互換操作）
ALT_LEFT_KEYS: Tuple[int, ...] = (pg.K_LEFT,)
ALT_CONFIRM_KEYS: Tuple[int, ...] = (pg.K_RETURN, pg.K_SPACE)
ALT_RIGHT_KEYS: Tuple[int, ...] = (pg.K_RIGHT,)
