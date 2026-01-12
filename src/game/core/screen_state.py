from enum import Enum, auto


class ScreenState(Enum):
    """ゲーム内の画面状態を表す状態列挙体"""
    TITLE = auto()
    SEED_SELECTION = auto()
    TIME_SETTING = auto()
    MAIN = auto()
    SETTINGS = auto()
    STATUS = auto()
    MODE_WATER = auto()
    MODE_LIGHT = auto()
    FLOWER_LANGUAGE = auto()
    DEATH = auto()


