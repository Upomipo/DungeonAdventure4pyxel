import pyxel
from util import draw_text_with_border


class SimpleDialog:
    def __init__(self, text, choices, choices_color=None, face_info=None):
        self.text = text
        self.choices = choices
        if choices_color is None:
            choices_color = [pyxel.COLOR_WHITE] * len(choices)
        self.choices_color = choices_color
        self.face_info = face_info  # 顔グラ情報 {"img": 1, "u": 0, "v": 0, "w": 32, "h": 32}
        self.active = True
        self.result = None
        self.boxes = []

    def update(self):
        if not self.active:
            return

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            for i, (x, y, w, h) in enumerate(self.boxes):
                if x <= mx <= x + w and y <= my <= y + h:
                    self.result = self.choices[i]
                    self.active = False
                    break

    def draw(self):
        if not self.active:
            return

        window_height = 20 + self.text.count("\n") * 10
        x, y, w, h = 8, pyxel.height // 2, pyxel.width - 10, window_height
        pyxel.rect(x, y, w, h, 0)
        pyxel.rectb(x, y, w, h, 7)

        if self.face_info:
            info = self.face_info
            # 顔グラ位置（ウィンドウの上に乗るイメージ）
            face_x = x + 8
            face_y = y - info["h"] - 4

            # 白枠（外側）
            pyxel.rect(
                face_x - 3, face_y - 3,  # ← 外側に1px余裕
                info["w"] + 6, info["h"] + 6,
                pyxel.COLOR_WHITE
            )

            # 黒枠（内側）
            pyxel.rect(
                face_x - 2, face_y - 2,
                info["w"] + 4, info["h"] + 4,
                pyxel.COLOR_BLACK
            )

            # 顔グラ本体
            pyxel.blt(
                face_x, face_y,
                info["img"],
                info["u"], info["v"],
                info["w"], info["h"],
                0
            )
            text_x = x + 6  # ← もう枠内に顔グラないので余白少なくてOK
        else:
            text_x = x + 6

        # 💬 メッセージ
        # pyxel.text(text_x, y + 6, self.text, 9)
        # draw_text_with_border(0, pyxel.height - 20, "剣をそうびした", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK, systemfont)
        lines = self.text.split("\n")
        for i, line in enumerate(lines):
            # pyxel.text(text_x, y + 6 + i * 8, line, 9)
            draw_text_with_border(text_x,  y + 6 + i * 8,line, pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)


        # 🎮 選択肢表示
        self.boxes.clear()
        for i, choice in enumerate(self.choices):
            # bx = x + 5 + i * 48
            # by = y + h - 12
            # bw, bh = 44, 12
            # self.boxes.append((bx, by, bw, bh))
            #縦置き
            bx = x + 5
            by = y + h + i * 12
            bw, bh = pyxel.width -20, 12
            self.boxes.append((bx, by, bw, bh))

            pyxel.rect(bx, by, bw, bh, 1)
            pyxel.rectb(bx, by, bw, bh, 7)
            draw_text_with_border(bx + 6, by + 2, choice, self.choices_color[i] ,pyxel.COLOR_BLACK)