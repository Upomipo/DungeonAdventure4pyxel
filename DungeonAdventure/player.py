import pyxel

from util import check_collision
from game_log import battle_log
from constants import CHARACTER_PIXEL_SIZE, PLAYER_STATE_DEAD, PLAYER_STATE_NORMAL, PLAYER_STATE_DAMAGE, D_LEFT, \
    PLAYER_STATE_MOVE, D_RIGHT, D_UP, D_DOWN, PLAYER_STATE_ATTACK, PLAYER_WEAPON_SWORD, PLAYER_WEAPON_MAGIC_FIRE, \
    PLAYER_WEAPON_MAGIC_THUNDER, PLAYER_STATE_LEVEL_UP_EFFECT, PLAYER_JOB_FIGHTER, PLAYER_JOB_WIZARD
from map import checkMapTile_point


class player:
    def __init__(self, hp, mp, state, point_x, point_y, direction, job, weapon):
        self.hp = hp
        self.max_hp = hp
        self.mp = mp
        self.max_mp = mp
        self.state = state
        self._frame_cnt = 0
        self.point_x = point_x
        self.point_y = point_y
        self.direction = direction
        self._pixel_x = self.point_x * CHARACTER_PIXEL_SIZE
        self._pixel_y = self.point_y * CHARACTER_PIXEL_SIZE
        self.job = job
        self.weapon = weapon
        # self.init(hp, state, point_x, point_y, direction, weapon)
        self.inventory = {} #Item仮実装

    def init(self, hp, mp, state, point_x, point_y, direction, job, weapon):
        self.hp = hp
        self.max_hp = hp
        self.mp = mp
        self.max_mp = mp
        self.state = state
        self._frame_cnt = 0
        self.point_x = point_x
        self.point_y = point_y
        self.direction = direction
        self._pixel_x = self.point_x * CHARACTER_PIXEL_SIZE
        self._pixel_y = self.point_y * CHARACTER_PIXEL_SIZE
        self.job = job
        self.weapon = weapon

    def has_move(self):
        return self._frame_cnt == 0 and self.state != PLAYER_STATE_DEAD

    def set_move_left(self):
        if not self.has_move():
            return
        if self.state == PLAYER_STATE_NORMAL or self.state == PLAYER_STATE_DAMAGE:
            if not checkMapTile_point(self.point_x - 1, self.point_y):
                    self._frame_cnt =  8
                    self.direction = D_LEFT
                    self.state = PLAYER_STATE_MOVE

    def set_move_right(self):
        if not self.has_move():
            return
        if self.state == PLAYER_STATE_NORMAL or self.state == PLAYER_STATE_DAMAGE:
            if not checkMapTile_point(self.point_x + 1, self.point_y):
                self._frame_cnt =  8
                self.direction = D_RIGHT
                self.state = PLAYER_STATE_MOVE

    def set_move_up(self):
        if not self.has_move():
            return
        if self.state == PLAYER_STATE_NORMAL or self.state == PLAYER_STATE_DAMAGE:
            if not checkMapTile_point(self.point_x, self.point_y - 1):
                self._frame_cnt =  8
                self.direction = D_UP
                self.state = PLAYER_STATE_MOVE

    def set_move_down(self):
        if not self.has_move():
            return
        if self.state == PLAYER_STATE_NORMAL or self.state == PLAYER_STATE_DAMAGE:
            if not checkMapTile_point(self.point_x, self.point_y + 1):
                self._frame_cnt =  8
                self.direction = D_DOWN
                self.state = PLAYER_STATE_MOVE

    def move_act(self):
        if self.state != PLAYER_STATE_MOVE:
            return

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

    def collision(self, target_pixel_x, target_pixel_y):
        return check_collision(self.pixel_x(), self.pixel_y(), target_pixel_x, target_pixel_y)

    def collision_attack(self, target_pixel_x, target_pixel_y):
        rtn = False
        if self.state != PLAYER_STATE_ATTACK:
            return rtn

        myself_pixel_x = self.pixel_x()
        myself_pixel_y = self.pixel_y()

        if self.weapon == PLAYER_WEAPON_SWORD:
            if self.direction == D_UP:
                if self._frame_cnt > 6:
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                elif self._frame_cnt > 4:
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                else:
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)

            elif self.direction == D_DOWN:
                if self._frame_cnt > 6:
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                elif self._frame_cnt > 4:
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                else:
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)

            elif self.direction == D_LEFT:
                if self._frame_cnt > 6:
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                elif self._frame_cnt > 4:
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                else:
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)

            elif self.direction == D_RIGHT:
                if self._frame_cnt > 6:
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                elif self._frame_cnt > 4:
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                else:
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)

            # rtn = check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)

        elif self.weapon == PLAYER_WEAPON_MAGIC_FIRE:
            if self.direction == D_UP:
                # myself_pixel_y -= CHARACTER_PIXEL_SIZE
                if self._frame_cnt > 8:
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                elif self._frame_cnt > 4:
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                else:
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_y -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)

            elif self.direction == D_DOWN:
                # myself_pixel_y += CHARACTER_PIXEL_SIZE
                if self._frame_cnt > 8:
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                elif self._frame_cnt > 4:
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                else:
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_y += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)

            elif self.direction == D_LEFT:
                # myself_pixel_x -= CHARACTER_PIXEL_SIZE
                if self._frame_cnt > 8:
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                elif self._frame_cnt > 4:
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                else:
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x -= CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)

            elif self.direction == D_RIGHT:
                # myself_pixel_x += CHARACTER_PIXEL_SIZE
                if self._frame_cnt > 8:
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                elif self._frame_cnt > 4:
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                else:
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
                    myself_pixel_x += CHARACTER_PIXEL_SIZE
                    rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)

            # rtn = check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
        elif self.weapon == PLAYER_WEAPON_MAGIC_THUNDER:
            if self._frame_cnt > 6:
                rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y, target_pixel_x, target_pixel_y)
            elif self._frame_cnt > 2:
                rtn = rtn or check_collision(myself_pixel_x+CHARACTER_PIXEL_SIZE, myself_pixel_y, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x+CHARACTER_PIXEL_SIZE, myself_pixel_y-CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y-CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x-CHARACTER_PIXEL_SIZE, myself_pixel_y-CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x-CHARACTER_PIXEL_SIZE, myself_pixel_y, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x-CHARACTER_PIXEL_SIZE, myself_pixel_y-CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y+CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x+CHARACTER_PIXEL_SIZE, myself_pixel_y+CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)
            else:
                rtn = rtn or check_collision(myself_pixel_x+CHARACTER_PIXEL_SIZE, myself_pixel_y, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x+CHARACTER_PIXEL_SIZE, myself_pixel_y-CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y-CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x-CHARACTER_PIXEL_SIZE, myself_pixel_y-CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x-CHARACTER_PIXEL_SIZE, myself_pixel_y, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x-CHARACTER_PIXEL_SIZE, myself_pixel_y-CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y+CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x+CHARACTER_PIXEL_SIZE, myself_pixel_y+CHARACTER_PIXEL_SIZE, target_pixel_x, target_pixel_y)

                rtn = rtn or check_collision(myself_pixel_x+(CHARACTER_PIXEL_SIZE*2), myself_pixel_y, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x+(CHARACTER_PIXEL_SIZE*2), myself_pixel_y-(CHARACTER_PIXEL_SIZE*2), target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y-(CHARACTER_PIXEL_SIZE*2), target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x-(CHARACTER_PIXEL_SIZE*2), myself_pixel_y-(CHARACTER_PIXEL_SIZE*2), target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x-(CHARACTER_PIXEL_SIZE*2), myself_pixel_y, target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x-(CHARACTER_PIXEL_SIZE*2), myself_pixel_y-(CHARACTER_PIXEL_SIZE*2), target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x, myself_pixel_y+(CHARACTER_PIXEL_SIZE*2), target_pixel_x, target_pixel_y)
                rtn = rtn or check_collision(myself_pixel_x+(CHARACTER_PIXEL_SIZE*2), myself_pixel_y+(CHARACTER_PIXEL_SIZE*2), target_pixel_x, target_pixel_y)

        return rtn

    def damage(self, damage_point):
        if self._frame_cnt == 0 and self.state!= PLAYER_STATE_DEAD:
            self.state = PLAYER_STATE_DAMAGE
            self._frame_cnt = 20
            self.hp -= damage_point
            pyxel.play(3, 1)
            if self.hp <= 0:
                self.state = PLAYER_STATE_DEAD
                self._frame_cnt = 50
                battle_log.add_log("倒された")


    def attack(self):
        if self.state == PLAYER_STATE_NORMAL or self.state == PLAYER_STATE_DAMAGE:
            if self.weapon == PLAYER_WEAPON_SWORD:
                self._frame_cnt = 8
                self.state = PLAYER_STATE_ATTACK
                pyxel.play(3, 4)
            elif self.weapon == PLAYER_WEAPON_MAGIC_FIRE:
                if self.mp > 0:
                    self.mp -= 1
                else:
                    return
                self._frame_cnt = 12
                self.state = PLAYER_STATE_ATTACK
                pyxel.play(3, 3)
            elif self.weapon == PLAYER_WEAPON_MAGIC_THUNDER:
                if self.mp > 2:
                    self.mp -= 2
                else:
                    return
                self._frame_cnt = 12
                self.state = PLAYER_STATE_ATTACK
                pyxel.play(3, 0)


    def draw_player(self):
        if self.state == PLAYER_STATE_MOVE or self.state == PLAYER_STATE_NORMAL:
            self._draw_player_myself()

        elif self.state == PLAYER_STATE_DAMAGE:
            if (self._frame_cnt % 4) == 0:
                self._draw_player_myself()

        elif self.state == PLAYER_STATE_ATTACK:
            self._draw_player_myself()

            attack_x = 4 * CHARACTER_PIXEL_SIZE
            attack_y = 4 * CHARACTER_PIXEL_SIZE

            if self.weapon == PLAYER_WEAPON_SWORD:
                if self.direction == D_LEFT:
                    # attack_x -= CHARACTER_PIXEL_SIZE
                    # # pyxel.blt(attack_x, attack_y, 0, 8, 40, 8, 8, 0)  # 弾を描画
                    # if self._frame_cnt > 6:
                    #     pyxel.blt(attack_x, attack_y, 0, 16, 40, 8, 8, 0)
                    # else:
                    #     pyxel.blt(attack_x, attack_y, 0, 24, 40, 8, 8, 0)
                    if self._frame_cnt > 6:
                        attack_y += CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0, 90.0)
                        attack_y += CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0, 90.0)
                    elif self._frame_cnt > 4:
                        attack_y += CHARACTER_PIXEL_SIZE
                        attack_x -= CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0, 135.0)
                        attack_y += 5
                        attack_x -= 5
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0, 135.0)
                    else:
                        attack_x -= CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0, 180.0)
                        attack_x -= CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0, 180.0)
                elif self.direction == D_RIGHT:
                    # if self._frame_cnt > 3:
                    #     pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0)
                    # else:
                    #     pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0)
                    #     attack_x += CHARACTER_PIXEL_SIZE
                    #     pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0)
                    if self._frame_cnt > 6:
                        attack_y -= CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0, -90.0)
                        attack_y -= CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0, -90.0)
                    elif self._frame_cnt > 4:
                        attack_y -= CHARACTER_PIXEL_SIZE
                        attack_x += CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0, -45.0)
                        attack_y -= 5
                        attack_x += 5
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0, -45.0)
                    else:
                        attack_x += CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0)
                        attack_x += CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0)
                elif self.direction == D_UP:
                    # attack_y -= CHARACTER_PIXEL_SIZE
                    # if self._frame_cnt > 6:
                    #     pyxel.blt(attack_x, attack_y, 0, 32, 32, 8, 8, 0)
                    # else:
                    #     pyxel.blt(attack_x, attack_y, 0, 40, 32, 8, 8, 0)
                    if self._frame_cnt > 6:
                        attack_x -= CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0, 180)
                        attack_x -= CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0, 180)
                    elif self._frame_cnt > 4:
                        attack_y -= CHARACTER_PIXEL_SIZE
                        attack_x -= CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0, 225.0)
                        attack_y -= 5
                        attack_x -= 5
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0, 225.0)
                    else:
                        attack_y -= CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0, -90.0)
                        attack_y -= CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0, -90.0)
                elif self.direction == D_DOWN:
                    # attack_y += CHARACTER_PIXEL_SIZE
                    # if self._frame_cnt > 6:
                    #     pyxel.blt(attack_x, attack_y, 0, 32, 40, 8, 8, 0)
                    # else:
                    #     pyxel.blt(attack_x, attack_y, 0, 40, 40, 8, 8, 0)
                    if self._frame_cnt > 6:
                        attack_x += CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0)
                        attack_x += CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0)
                    elif self._frame_cnt > 4:
                        attack_y += CHARACTER_PIXEL_SIZE
                        attack_x += CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0, 45.0)
                        attack_y += 5
                        attack_x += 5
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0, 45.0)
                    else:
                        attack_y += CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 24, 32, 8, 8, 0, 90.0)
                        attack_y += CHARACTER_PIXEL_SIZE
                        pyxel.blt(attack_x, attack_y, 0, 16, 32, 8, 8, 0, 90.0)
            elif self.weapon == PLAYER_WEAPON_MAGIC_FIRE:
                if self.direction == D_LEFT:
                    attack_x -= CHARACTER_PIXEL_SIZE
                    # pyxel.blt(attack_x, attack_y, 0, 8, 40, 8, 8, 0)  # 弾を描画
                    if self._frame_cnt > 8:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                    elif self._frame_cnt > 4:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x - CHARACTER_PIXEL_SIZE, attack_y, 0, 0, 32, 8, 8, 0)
                    else:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x - CHARACTER_PIXEL_SIZE, attack_y, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x - (CHARACTER_PIXEL_SIZE * 2), attack_y, 0, 0, 32, 8, 8, 0)
                elif self.direction == D_RIGHT:
                    attack_x += CHARACTER_PIXEL_SIZE
                    if self._frame_cnt > 8:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                    elif self._frame_cnt > 4:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x + CHARACTER_PIXEL_SIZE, attack_y, 0, 0, 32, 8, 8, 0)
                    else:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x + CHARACTER_PIXEL_SIZE, attack_y, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x + (CHARACTER_PIXEL_SIZE * 2), attack_y, 0, 0, 32, 8, 8, 0)
                elif self.direction == D_UP:
                    attack_y -= CHARACTER_PIXEL_SIZE
                    if self._frame_cnt > 8:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                    elif self._frame_cnt > 4:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x, attack_y - CHARACTER_PIXEL_SIZE, 0, 0, 32, 8, 8, 0)
                    else:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x, attack_y - CHARACTER_PIXEL_SIZE, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x, attack_y - (CHARACTER_PIXEL_SIZE * 2), 0, 0, 32, 8, 8, 0)
                elif self.direction == D_DOWN:
                    attack_y += CHARACTER_PIXEL_SIZE
                    if self._frame_cnt > 8:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                    elif self._frame_cnt > 4:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x, attack_y + CHARACTER_PIXEL_SIZE, 0, 0, 32, 8, 8, 0)
                    else:
                        pyxel.blt(attack_x, attack_y, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x, attack_y + CHARACTER_PIXEL_SIZE, 0, 0, 32, 8, 8, 0)
                        pyxel.blt(attack_x, attack_y + (CHARACTER_PIXEL_SIZE * 2), 0, 0, 32, 8, 8, 0)
            elif self.weapon == PLAYER_WEAPON_MAGIC_THUNDER:
                # attack_y += CHARACTER_PIXEL_SIZE
                # attack_x += CHARACTER_PIXEL_SIZE
                if self._frame_cnt > 6:
                    pyxel.blt(attack_x, attack_y, 0, 8, 32, 8, 8, 0, 0.0, 2.0)
                elif self._frame_cnt > 2:
                    pyxel.blt(attack_x+CHARACTER_PIXEL_SIZE, attack_y, 0, 8, 32, 8, 8, 0, 0.0, 1.5)
                    pyxel.blt(attack_x, attack_y-CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.5)
                    pyxel.blt(attack_x-CHARACTER_PIXEL_SIZE, attack_y, 0, 8, 32, 8, 8, 0, 0.0, 1.5)
                    pyxel.blt(attack_x, attack_y+CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.5)
                    pyxel.blt(attack_x+CHARACTER_PIXEL_SIZE, attack_y-CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.5)
                    pyxel.blt(attack_x-CHARACTER_PIXEL_SIZE, attack_y-CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.5)
                    pyxel.blt(attack_x+CHARACTER_PIXEL_SIZE, attack_y+CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.5)
                    pyxel.blt(attack_x-CHARACTER_PIXEL_SIZE, attack_y+CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.5)
                else:
                    pyxel.blt(attack_x+CHARACTER_PIXEL_SIZE, attack_y, 0, 8, 32, 8, 8, 0, 0.0, 1.0)
                    pyxel.blt(attack_x, attack_y-CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.0)
                    pyxel.blt(attack_x-CHARACTER_PIXEL_SIZE, attack_y, 0, 8, 32, 8, 8, 0, 0.0, 1.0)
                    pyxel.blt(attack_x, attack_y+CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.0)
                    pyxel.blt(attack_x+CHARACTER_PIXEL_SIZE, attack_y-CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.0)
                    pyxel.blt(attack_x-CHARACTER_PIXEL_SIZE, attack_y-CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.0)
                    pyxel.blt(attack_x+CHARACTER_PIXEL_SIZE, attack_y+CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.0)
                    pyxel.blt(attack_x-CHARACTER_PIXEL_SIZE, attack_y+CHARACTER_PIXEL_SIZE, 0, 8, 32, 8, 8, 0, 0.0, 1.0)
                    pyxel.blt(attack_x+(CHARACTER_PIXEL_SIZE*2), attack_y, 0, 8, 32, 8, 8, 0, 0.0, 0.5)
                    pyxel.blt(attack_x, attack_y-(CHARACTER_PIXEL_SIZE*2), 0, 8, 32, 8, 8, 0, 0.0, 0.5)
                    pyxel.blt(attack_x-(CHARACTER_PIXEL_SIZE*2), attack_y, 0, 8, 32, 8, 8, 0, 0.0, 0.5)
                    pyxel.blt(attack_x, attack_y+(CHARACTER_PIXEL_SIZE*2), 0, 8, 32, 8, 8, 0, 0.0, 0.5)
                    pyxel.blt(attack_x+(CHARACTER_PIXEL_SIZE*2), attack_y-(CHARACTER_PIXEL_SIZE*2), 0, 8, 32, 8, 8, 0, 0.0, 0.5)
                    pyxel.blt(attack_x-(CHARACTER_PIXEL_SIZE*2), attack_y-(CHARACTER_PIXEL_SIZE*2), 0, 8, 32, 8, 8, 0, 0.0, 0.5)
                    pyxel.blt(attack_x+(CHARACTER_PIXEL_SIZE*2), attack_y+(CHARACTER_PIXEL_SIZE*2), 0, 8, 32, 8, 8, 0, 0.0, 0.5)
                    pyxel.blt(attack_x-(CHARACTER_PIXEL_SIZE*2), attack_y+(CHARACTER_PIXEL_SIZE*2), 0, 8, 32, 8, 8, 0, 0.0, 0.5)
        elif self.state == PLAYER_STATE_DEAD:
            pyxel.text(15, 30, "  YOU DEAD   ", 10)

        elif self.state == PLAYER_STATE_LEVEL_UP_EFFECT:
            self._draw_player_myself()
            pyxel.text(20, 32+self._frame_cnt, "LEVEL UP!!!", pyxel.frame_count % 16)
            if self._frame_cnt == 0:
                self.state = PLAYER_STATE_NORMAL

        # ターゲットに到達したらステータスをノーマルへ
        if self.has_move():
            self.state = PLAYER_STATE_NORMAL

        if self._frame_cnt != 0:
            self._frame_cnt -= 1

        if self.max_mp > self.mp and pyxel.frame_count % 50 == 0:
            self.mp += 1

        # else:
        #     self.state = PLAYER_STATE_NORMAL
        # print(str(self.frame_cnt))

    def _draw_player_myself(self):
        job_align = 0
        if self.job == PLAYER_JOB_FIGHTER:
            job_align = 0
        elif self.job == PLAYER_JOB_WIZARD:
            job_align = 16
        if self.direction == D_LEFT:
            if self._frame_cnt % 4 == 0:
                pyxel.blt(32, 32, 0, 72, 8 + job_align, 8, 8, 0)  # プレイヤーキャラクターを描画
            else:
                pyxel.blt(32, 32, 0, 80, 8 + job_align, 8, 8, 0)  # プレイヤーキャラクターを描画

        elif self.direction == D_RIGHT:
            if self._frame_cnt % 4 == 0:
                pyxel.blt(32, 32, 0, 72, 0 + job_align, 8, 8, 0)  # プレイヤーキャラクターを描画
            else:
                pyxel.blt(32, 32, 0, 80, 0 + job_align, 8, 8, 0)  # プレイヤーキャラクターを描画
            # pyxel.blt(32, 32, 0, 0, 24, 8, 8, 0)  # プレイヤーキャラクターを描画
        elif self.direction == D_UP:
            if self._frame_cnt % 4 == 0:
                pyxel.blt(32, 32, 0, 56, 8 + job_align, 8, 8, 0)  # プレイヤーキャラクターを描画
            else:
                pyxel.blt(32, 32, 0, 64, 8 + job_align, 8, 8, 0)  # プレイヤーキャラクターを描画
            # pyxel.blt(32, 32, 0, 8, 16, 8, 8, 0)  # プレイヤーキャラクターを描画
        elif self.direction == D_DOWN:
            if self._frame_cnt % 4 == 0:
                pyxel.blt(32, 32, 0, 56, 0 + job_align, 8, 8, 0)  # プレイヤーキャラクターを描画
            else:
                pyxel.blt(32, 32, 0, 64, 0 + job_align, 8, 8, 0)  # プレイヤーキャラクターを描画
            # pyxel.blt(32, 32, 0, 0, 16, 8, 8, 0)  # プレイヤーキャラクターを描画

    def draw_inventory(self):
        x = 70
        for item, count in self.inventory.items():
            if item ==  "ポーション":
                pyxel.blt(x, 27, 0, 0, 16, 8, 8, 0)
            elif item == "エリクサー":
                pyxel.blt(x, 27, 0, 0, 24, 8, 8, 0)
            elif item == "スクロール":
                pyxel.blt(x, 27, 0, 8, 16, 8, 8, 0)

            pyxel.text(x+3, 29, f"{count}個", 7)
            # writer.draw(5, y, f"{item}: {count}個", 8, 7)
            x += 10

    def pixel_x(self):
        return self._pixel_x

    def pixel_y(self):
        return self._pixel_y

    def live(self):
        return not(self.state == PLAYER_STATE_DEAD and self._frame_cnt == 0)

    def cure_hp(self, point):
        self.hp += point
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def cure_mp(self, point):
        self.mp += point
        if self.mp > self.max_mp:
            self.mp = self.max_mp

    def level_up(self):
        if self.job == PLAYER_JOB_FIGHTER:
            self.max_hp += 3
        elif self.job == PLAYER_JOB_WIZARD:
            self.max_hp += 1
            self.max_mp += 2
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.state = PLAYER_STATE_LEVEL_UP_EFFECT
        self._frame_cnt = 8
        battle_log.add_log("レベルが上がった")

    def jump(self, jump_point_x, jump_point_y):
        self.point_x = jump_point_x
        self.point_y = jump_point_y
        self.direction = D_DOWN
        self._pixel_x = self.point_x * CHARACTER_PIXEL_SIZE
        self._pixel_y = self.point_y * CHARACTER_PIXEL_SIZE

    def add_item(self, item):
        if item in self.inventory:
            self.inventory[item] += 1
        else:
            self.inventory[item] = 1
        # print(f"{item} を手に入れた！ ({self.inventory[item]}個)")
        battle_log.add_log(f"{item} を手に入れた！ ({self.inventory[item]}個)")

    def use_item(self, item):
        if not self.has_move():
            return
        if item in self.inventory and self.inventory[item] > 0:
            self.inventory[item] -= 1
            # print(f"{item} を使用した！ 残り: {self.inventory[item]}個")
            battle_log.add_log(f"{item} を使用した！ 残り: {self.inventory[item]}個")
            if self.inventory[item] == 0:
                del self.inventory[item]
            if item == "ポーション":
                self.cure_hp(5)
                pyxel.play(3, 6)
                self._frame_cnt += 10
            elif item == "エリクサー":
                self.cure_hp(15)
                self.cure_mp(15)
                pyxel.play(3, 6)
                self._frame_cnt += 10
            elif item == "スクロール":
                self._frame_cnt += 10
                # todo 未実装
        else:
            # print(f"{item} は持っていない。")
            battle_log.add_log(f"{item} は持っていない。")

    def use_item_index(self, index):
        if not self.has_move():
            return
        if 0 <= index < len(self.inventory.items()):
            target_item = list(self.inventory.items())[index]
            target_item_key = target_item[0]
            self.use_item(target_item_key)
