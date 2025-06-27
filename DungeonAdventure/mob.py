import random

import pyxel

from data import MOB_DATA
from constants import CHARACTER_PIXEL_SIZE, MOB_STATE_GENERATE, MOB_STATE_DEAD, MOB_STATE_MOVE, D_UP, MOB_STATE_STAY, \
    D_DOWN, D_LEFT, D_RIGHT, MOB_STATE_DAMAGE, MOB_STATE_DYING
from map import checkMapTile_pixel, checkMapTile_point


class mob:
    _MOB_NAME = 0
    _MOB_HP = 1
    _MOB_POWER = 2
    _MOB_SPEED = 3
    _MOB_U = 4
    _MOB_V = 5


    def __init__(self, id, point_x, point_y, direction):
        self.id = id
        self.name = ""
        self.hp = 0
        self.power = 0
        self.speed = 0
        if id < len(MOB_DATA):
            self.name = MOB_DATA[self.id][self._MOB_NAME]
            self.hp = MOB_DATA[self.id][self._MOB_HP]
            self.power = MOB_DATA[self.id][self._MOB_POWER]
            self.speed = MOB_DATA[self.id][self._MOB_SPEED]

        self.point_x = point_x
        self.point_y = point_y
        self.direction = direction
        self._pixel_x = self.point_x * CHARACTER_PIXEL_SIZE
        self._pixel_y = self.point_y * CHARACTER_PIXEL_SIZE
        self._state = MOB_STATE_GENERATE
        self._frame_cnt = 16

    def live(self):
        return self._state != MOB_STATE_DEAD

    def act(self):
        if self._state == MOB_STATE_MOVE and self._frame_cnt==0:
            direction_x = self._pixel_x
            direction_y = self._pixel_y
            if self.direction == D_UP:
                if checkMapTile_pixel(direction_x, direction_y - 1) or checkMapTile_pixel(direction_x + 7, direction_y - 1):
                    self._state = MOB_STATE_STAY
                    self._frame_cnt = 10 - self.speed
                else:
                    direction_y -= 1

            elif self.direction == D_DOWN:
                if checkMapTile_pixel(direction_x, direction_y + 8) or checkMapTile_pixel(direction_x + 7, direction_y + 8):
                    self._state = MOB_STATE_STAY
                    self._frame_cnt = 10 - self.speed
                else:
                    direction_y += 1

            elif self.direction == D_LEFT:
                if checkMapTile_pixel(direction_x - 1, direction_y) or checkMapTile_pixel(direction_x - 1, direction_y + 7):
                    self._state = MOB_STATE_STAY
                    self._frame_cnt = 10 - self.speed
                else:
                    direction_x -= 1

            elif self.direction == D_RIGHT:
                if checkMapTile_pixel(direction_x + 8, direction_y) or checkMapTile_pixel(direction_x + 8, direction_y + 7):
                    self._state = MOB_STATE_STAY
                    self._frame_cnt = 10 - self.speed
                else:
                    direction_x += 1

            self._pixel_x = direction_x
            self._pixel_y = direction_y

            if random.randint(0, 10+self.speed) == 0:
                self._state = MOB_STATE_STAY
                self._frame_cnt = 10 - self.speed

            self.point_x = int(self._pixel_x / 8)
            self.point_y = int(self._pixel_y / 8)

        elif self._state == MOB_STATE_STAY and self._frame_cnt == 0:
            if self.direction == D_UP or self.direction == D_DOWN:
                if random.randint(0, 1) == 0:
                    self.direction = D_RIGHT
                else:
                    self.direction = D_LEFT
                self._state = MOB_STATE_MOVE
            elif self.direction == D_LEFT or self.direction == D_RIGHT:
                if random.randint(0, 1) == 0:
                    self.direction = D_UP
                else:
                    self.direction = D_DOWN
                self._state = MOB_STATE_MOVE

        elif self._state == MOB_STATE_DAMAGE and self._frame_cnt == 0:
            if self.hp <= 0:
                self._state = MOB_STATE_DYING
                self._frame_cnt = 4
            else:
                self._state = MOB_STATE_STAY
                self._frame_cnt = 8

        elif self._state == MOB_STATE_DYING and self._frame_cnt == 0:
            self._state = MOB_STATE_DEAD

        elif self._state == MOB_STATE_GENERATE and self._frame_cnt==0:
            self._state = MOB_STATE_MOVE


    def damage(self, damage_point, battle_log, drop_item_manager):

        if self._state == MOB_STATE_MOVE or self._state == MOB_STATE_STAY:
            self._state = MOB_STATE_DAMAGE
            self._frame_cnt = 20
            self.hp -= damage_point
            pyxel.play(3, 1)
            if self.hp <= 0:
                self.hp = 0
                self._state = MOB_STATE_DYING
                pyxel.play(3, 0)
                battle_log.add_log(self.name + "を倒した！")
                drop_item_manager.get_drop(self.name, self.point_x, self.point_y)  # アイテムドロップ

    def draw(self, player_pixel_x, player_pixel_y):
        mob_pixel_x = self._pixel_x - (player_pixel_x - 32)
        mob_pixel_y = self._pixel_y - (player_pixel_y - 32)

        if (player_pixel_x - 32) <= self._pixel_x <= (player_pixel_x + 24) and (player_pixel_y - 32) <= self._pixel_y <= (
                player_pixel_y + 24):
            if self._state == MOB_STATE_MOVE or self._state == MOB_STATE_STAY:
                pyxel.blt(mob_pixel_x, mob_pixel_y, 0, MOB_DATA[self.id][self._MOB_U], MOB_DATA[self.id][self._MOB_V], 8, 8, 0)
            elif self._state == MOB_STATE_DAMAGE:
                if (self._frame_cnt % 4) == 0:
                    pyxel.blt(mob_pixel_x, mob_pixel_y, 0, MOB_DATA[self.id][self._MOB_U],
                              MOB_DATA[self.id][self._MOB_V], 8, 8, 0)
            elif self._state == MOB_STATE_DYING:
                pyxel.blt(mob_pixel_x, mob_pixel_y, 0, 16, 16, 8, 8, 0)
            elif self._state == MOB_STATE_GENERATE:
                pyxel.blt(mob_pixel_x, mob_pixel_y, 0, 16, 24, 8, 8, 0)


        if self._frame_cnt > 0:
            self._frame_cnt -= 1

    def pixel_x(self):
        return self._pixel_x

    def pixel_y(self):
        return self._pixel_y

    def nock_back(self):
        if self._frame_cnt > 0:
            return
        if self.direction == D_UP:
            self.direction = D_DOWN
        elif self.direction == D_DOWN:
            self.direction = D_UP
        elif self.direction == D_LEFT:
            self.direction = D_RIGHT
        elif self.direction == D_RIGHT:
            self.direction = D_LEFT
        self._frame_cnt = 10
        self._state = MOB_STATE_MOVE


def generate_mob(generate_x, generate_y, mobs, player):
    if not checkMapTile_point(generate_x, generate_y):
        if generate_x != player.point_x:
            if generate_y != player.point_y:
                # print(str(generate_x) + "," + str(generate_x))
                mobs.append(mob(random.randint(0, len(MOB_DATA) - 1), generate_x, generate_y, D_UP))
