import math

import pyxel
import os
font_path = os.path.join(os.path.dirname(__file__), "assets", "misaki_gothic.bdf")
systemfont = pyxel.Font(font_path)
# systemfont = pyxel.Font("assets/misaki_gothic.bdf")
# systemfont = pyxel.Font("DungeonAdventures/assets/misaki_gothic.bdf")

def check_collision(x1, y1, x2, y2):
    return (
        x1 < x2 + 8 and
        x1 + 8 > x2 and
        y1 < y2 + 8 and
        y1 + 8 > y2
    )


def draw_text_with_border(x, y, s, col, bcol):
    font = systemfont
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx != 0 or dy != 0:
                pyxel.text(
                    x + dx,
                    y + dy,
                    s,
                    bcol,
                    font,
                )

    pyxel.text(x, y, s, col, font)

def angle_diff(a, b):
    return abs((a - b + math.pi) % (2 * math.pi) - math.pi)
