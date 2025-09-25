# text_renderer.py
import time

import pyxel

from story_texts import FLOOR_FLAVORS
from util import draw_text_with_border

# 表示制御用の変数
_floor_text_start_time = None
_floor_text_floor = None
_floor_text_duration = 5.0  # 秒数（ここを変えれば表示時間を調整可能）

def start_floor_flavor_display(floor):
    """階層テキスト表示を開始"""
    global _floor_text_start_time, _floor_text_floor
    _floor_text_start_time = time.time()
    _floor_text_floor = floor

def draw_floor_flavor(x, y, col=pyxel.COLOR_WHITE, bcol=pyxel.COLOR_BLACK):
    """表示時間内なら階層テキストを描画"""
    if _floor_text_start_time is None or _floor_text_floor not in FLOOR_FLAVORS:
        return

    elapsed = time.time() - _floor_text_start_time
    if elapsed <= _floor_text_duration:

        for by in range(20):
            for bx in range(pyxel.width):
                if (bx + by) % 2 == 0:  # 1ドットおきに塗る
                    pyxel.pset(0 + bx, y + by, pyxel.COLOR_DARK_BLUE)

        lines = FLOOR_FLAVORS[_floor_text_floor]
        draw_text_with_border(x, y, lines[0], col, bcol)
        draw_text_with_border(x, y + 10, lines[1], col, bcol)