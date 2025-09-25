from collections import deque

import pyxel
from util import draw_text_with_border


class BattleLog:
    def __init__(self, max_logs=5):
        self.logs = deque(maxlen=max_logs)  # 最大ログ数を設定
        self.timer_max = 60
        self.timer = self.timer_max
        self.disp_text = None

    def add_log(self, message):
        self.logs.append(message)

    def clear_logs(self):
        self.logs.clear()

    def draw(self):
        # 表示中なら描画して、タイマーを減らす
        if self.timer > 0 and self.disp_text:
            for y in range(20):
                for x in range(pyxel.width):
                    if (x + y) % 2 == 0:  # 1ドットおきに塗る
                        pyxel.pset(0 + x, (pyxel.height/3) - 20 + y, pyxel.COLOR_BLACK)
            # pyxel.rect(0, pyxel.height - 20, pyxel.width, 20, pyxel.COLOR_BLACK)
            draw_text_with_border(5, (pyxel.height/3) - 15, self.disp_text, pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
            self.timer -= 1

        # 表示していない状態で、ログが残っていれば次を取得
        elif self.logs:
            self.disp_text = self.logs.pop()
            self.timer = self.timer_max


battle_log = BattleLog(max_logs=5)
