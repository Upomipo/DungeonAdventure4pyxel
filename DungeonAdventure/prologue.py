import pyxel
from util import draw_text_with_border
from story_texts import PROLOGUE

scroll_y = 228  # 最初は画面下端からスタート
scroll_speed = 0.25       # 1フレームあたりのスクロール速度（調整可）

def update():
    global scroll_y
    scroll_y -= scroll_speed
    # 全部流れ切ったらループさせたい場合
    if scroll_y < -len(PROLOGUE) * 10:
        scroll_y = pyxel.height

def draw():
    # pyxel.cls(0)
    # 背景色（例: 濃紺）
    # pyxel.rect(0, 0, pyxel.width, pyxel.height, 1)

    # PROLOGUE全行をスクロール位置に応じて描画
    for i, line in enumerate(PROLOGUE):
        y = scroll_y + i * 10
        draw_text_with_border(4, y, line, 7, 0)