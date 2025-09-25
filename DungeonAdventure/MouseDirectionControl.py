import math

import pyxel


class MouseDirectionControl:
    def __init__(self, distance=20):
        # self.start_pos = None
        # self.is_dragging = False
        # self.dir_vector = (0, 0)
        self.distance = distance  # 一定距離（移動量）
        self.is_dragging = False
        self.start_pos = None
        self.angle = 0

    def get_target_position(self, origin_x, origin_y):
        if not self.is_dragging:
            return origin_x, origin_y

        offset_x = math.cos(self.angle) * self.distance
        offset_y = math.sin(self.angle) * self.distance

        return origin_x + offset_x, origin_y + offset_y

    def update(self, key):
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        if self.is_dragging == False and key==pyxel.MOUSE_BUTTON_LEFT:
            self.start_pos = (mx, my)
            self.is_dragging = True
            # print("dragging on:"+str(self.start_pos))

        elif self.is_dragging and key==pyxel.MOUSE_BUTTON_LEFT:
            dx = mx - self.start_pos[0]
            dy = my - self.start_pos[1]
            self.angle = math.atan2(dy, dx)
            # print("dragging now:"+str(self.angle))

        elif self.is_dragging:
            self.is_dragging = False
            # print("dragging off")

    def draw(self):
        if self.is_dragging and self.start_pos:
            # 起点（マウス押し始めた位置）
            origin_x, origin_y = self.start_pos

            # ターゲット（一定距離先）
            target_x, target_y = self.get_target_position(origin_x, origin_y)

            # 線を引く
            pyxel.line(origin_x, origin_y, target_x, target_y, 7)

            # 起点に円を描く
            pyxel.circ(origin_x, origin_y, 3, 10)
