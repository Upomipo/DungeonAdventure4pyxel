import pyxel

from constants import D_DOWN, D_UP, D_RIGHT, D_LEFT, CHARACTER_PIXEL_SIZE
from map import checkMapTile_pixel


class attack:
    def __init__(self, type, point_x, point_y, direction, power, range):
        self.type = type
        self.point_x = point_x
        self.point_y = point_y
        self.direction = direction
        self.power = power
        self.range = range
        self._live = True
        self._frame_cnt = 8 * self.range

        if self.direction == D_DOWN:
            self.point_y += 1

        elif self.direction == D_UP:
            self.point_y -= 1

        elif self.direction == D_RIGHT:
            self.point_x += 1

        elif self.direction == D_LEFT:
            self.point_x -= 1

        self._pixel_x = self.point_x * CHARACTER_PIXEL_SIZE
        self._pixel_y = self.point_y * CHARACTER_PIXEL_SIZE

    def live(self):
        return self._live

    def act(self):
        # 弾が生存していない場合は動かない
        if not self._live:
            return

        # 移動
        if self.direction == D_UP:
            self._pixel_y = self.point_y * CHARACTER_PIXEL_SIZE - (8 - self._frame_cnt)
            if self._frame_cnt <= 0:
                self.point_y -= 1

        elif self.direction == D_DOWN:
            self._pixel_y = self.point_y * CHARACTER_PIXEL_SIZE + (8 - self._frame_cnt)
            if self._frame_cnt <= 0:
                self.point_y += 1

        elif self.direction == D_LEFT:
            self._pixel_x = self.point_x * CHARACTER_PIXEL_SIZE - (8 - self._frame_cnt)
            if self._frame_cnt <= 0:
                self.point_x -= 1

        elif self.direction == D_RIGHT:
            self._pixel_x = self.point_x * CHARACTER_PIXEL_SIZE + (8 - self._frame_cnt)
            if self._frame_cnt <= 0:
                self.point_x += 1

        # 移動後にマップが移動可能かチェック
        if checkMapTile_pixel(self._pixel_x, self._pixel_y) or checkMapTile_pixel(self._pixel_x + 7, self._pixel_y + 7):
            self._live = False

        if self._frame_cnt==0:
            self._live = False

        # if not self._live:
        #     self.point_x = int(self._pixel_x / CHARACTER_PIXEL_SIZE)
        #     self.point_y = int(self._pixel_y / CHARACTER_PIXEL_SIZE)

    def draw(self):
        if self.direction == D_LEFT:
            pyxel.blt(self._pixel_x, self._pixel_y, 0, 8, 40, 8, 8, 0)  # 弾を描画
        elif self.direction == D_RIGHT:
            pyxel.blt(self._pixel_x, self._pixel_y, 0, 0, 40, 8, 8, 0)  # 弾を描画
        elif self.direction == D_UP:
            pyxel.blt(self._pixel_x, self._pixel_y, 0, 8, 32, 8, 8, 0)  # 弾を描画
        elif self.direction == D_DOWN:
            pyxel.blt(self._pixel_x, self._pixel_y, 0, 0, 32, 8, 8, 0)  # 弾を描画

        if self._frame_cnt != 0:
            self._frame_cnt -= 1
