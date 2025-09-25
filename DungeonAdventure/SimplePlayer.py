import math
import random

import pyxel
from constants import PLAYER_JOB_FIGHTER, PLAYER_JOB_WIZARD, WEAPON_NAME_BEAM, WEAPON_NAME_BOOKOFLIGHT, \
    WEAPON_NAME_BOOKOFTHUNDER, WEAPON_NAME_BOOKOFFIRE, WEAPON_NAME_FLASHSPEAR, WEAPON_NAME_SLASHAXE, \
    WEAPON_NAME_GREATSWORD, PLAYER_JOB_THIEF, WEAPON_NAME_KNIFE, WEAPON_NAME_ARROW, WEAPON_NAME_CRAW, \
    WEAPON_NAME_THROWING_KNIFE
from game_log import battle_log
from map import checkMapTile_point
from sin_system import get_sin_modifier

job_allowed_weapons = {
    PLAYER_JOB_FIGHTER: [WEAPON_NAME_GREATSWORD, WEAPON_NAME_SLASHAXE, WEAPON_NAME_FLASHSPEAR],
    PLAYER_JOB_WIZARD: [WEAPON_NAME_BOOKOFFIRE, WEAPON_NAME_BOOKOFTHUNDER, WEAPON_NAME_BOOKOFLIGHT, WEAPON_NAME_BEAM],
    PLAYER_JOB_THIEF: [WEAPON_NAME_KNIFE, WEAPON_NAME_ARROW, WEAPON_NAME_CRAW, WEAPON_NAME_THROWING_KNIFE],
}

class SimplePlayer:
    def __init__(self, x, y, job=PLAYER_JOB_FIGHTER, speed=2, base_u=88, base_v=0):
        self.x = x
        self.y = y
        self.angle = 0  # 攻撃向き（ラジアン）

        # 表示サイズや色など（必要に応じて調整可能）
        self.size = 8
        self.color = 11

        self.speed = speed

        self.target_x = None
        self.target_y = None
        self.base_u = base_u  # キャラクターごとのスプライト開始位置
        self.base_v = base_v  # キャラクターごとのスプライト開始位置

        self.max_hp = 10
        self.hp = self.max_hp

        self.invincible_timer = 0  # 無敵時間（フレーム単位）
        self.job = job
        self.attacks = {}  # 所持武器一覧

        self.near_enemy_angle = 0

        self.money = 0  #よどんだ精神の欠片

    def can_equip(self, weapon_name):
        return weapon_name in job_allowed_weapons.get(self.job, [])

    def reset_attacks(self):
        self.attacks = {}

    def gain_weapon(self, weapon_name, weapon_obj):
        if weapon_name in self.attacks:
            # すでに持っている武器 → 強化処理 todo
            # self.attacks[weapon_name].traits["強化"] = self.attacks[weapon_name].traits.get("強化", 0) + 1
            self.attacks[weapon_name].apply_traits()
        else:
            # 未所持 → 新しく追加
            self.attacks[weapon_name] = weapon_obj
            # self.attacks[weapon_name].apply_traits()

    def is_alive(self):
        return self.hp > 0

    def update_angle_toward(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        self.angle = math.atan2(dy, dx)

    def move_to(self, tx, ty):
        self.target_x = tx
        self.target_y = ty
        self.update_angle_toward(tx, ty)


    def move_forward(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def can_move_to(self, x, y):
        tile_x = x // 8
        tile_y = y // 8

        tile = pyxel.tilemap(0).pget(tile_x, tile_y)

        # タイル番号で通行判定（例：0〜15は通れる、16以上は障害物など）
        return not checkMapTile_point(tile_x, tile_y)

    def take_damage(self, amount):
        if self.invincible_timer > 0:
            return  # 無敵中なら無効

        nullify_chance = get_sin_modifier("傲慢", "damage_nullify_chance")  # 例：0.3 → 30%
        if random.random() < nullify_chance:
            # ダメージ無効化
            # print("傲慢補正によりダメージ無効化！")
            pyxel.play(3,7)
            battle_log.add_log("傲慢が敵の攻撃を拒絶した")
            return

        self.hp -= amount
        self.invincible_timer = 10  # 約*秒間の無敵（sフレーム）
        pyxel.play(3, 1)

        if self.hp <= 0:
            self.hp = 0
            self.on_defeated()  # 倒れた時の処理を分けて書けると良し

    def on_defeated(self):
        print("Game Over!")  # 演出や再スタート処理など



    def draw_hp_bar(self):
        bar_width = 8  # キャラの横幅と合わせる
        bar_height = 1
        filled = int(bar_width * self.hp / self.max_hp)

        # プレイヤー座標に合わせて上に表示
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.size // 2 - 4  # キャラ上部から少し離して

        pyxel.rect(bar_x, bar_y, bar_width, bar_height, pyxel.COLOR_RED)  # 背景（暗色）
        pyxel.rect(bar_x, bar_y, filled, bar_height, pyxel.COLOR_LIME)  # HPバー（赤系）

    def draw(self):
        # # プレイヤー本体（四角形）
        # pyxel.blt(self.x - self.size // 2, self.y - self.size // 2, 0, 56, 0, 8, 8, 0)
        # pyxel.camera(self.x - 64, self.y - 64)
        #
        # # 向き表示（先端に小さな円）
        # dir_x = self.x + math.cos(self.angle) * (self.size + 4)
        # dir_y = self.y + math.sin(self.angle) * (self.size + 4)
        # pyxel.circ(dir_x, dir_y, 2, 7)  # 白い向きマーカー
        # pyxel.camera(self.x - pyxel.width // 2, self.y - pyxel.height // 2)

        if not self.is_alive():
            # pyxel.text(self.x - self.size//2, self.y - self.size//2, "  YOU DEAD   ", pyxel.COLOR_RED)
            pyxel.blt(self.x - self.size // 2, self.y - self.size // 2, 0, 24, 24, 8, 8, 0)
            return

        if self.invincible_timer > 0 and pyxel.frame_count % 6 < 3:
            return  # 一瞬だけ非表示で点滅演出に

        angle_deg = math.degrees(self.angle)
        if -135 < angle_deg <= -45:
            direction_index = 0  # 上
        elif -45 < angle_deg <= 45:
            direction_index = 1  # 右
        elif 45 < angle_deg <= 135:
            direction_index = 2  # 下
        else:
            direction_index = 3  # 左

        is_walking = self.target_x is not None and self.target_y is not None
        frame = (pyxel.frame_count // 6) % 2 if is_walking else 0

        u = self.base_u + direction_index * 16 + frame * 8
        v = self.base_v

        pyxel.blt(self.x - self.size // 2, self.y - self.size // 2, 0, u, v, 8, 8, 0)

        dir_x = self.x + math.cos(self.angle) * (self.size + 4)
        dir_y = self.y + math.sin(self.angle) * (self.size + 4)
        pyxel.circ(dir_x, dir_y, 2, 7)

        # HPバー表示（例：画面左上）
        self.draw_hp_bar()


    def update(self):
        if self.target_x is None or self.target_y is None:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist <= self.speed:
            if self.can_move_to(self.target_x, self.target_y):
                self.x = self.target_x
                self.y = self.target_y
            self.target_x = None
            self.target_y = None
        else:
            move_x = dx / dist * self.speed
            move_y = dy / dist * self.speed

            next_x = self.x + move_x
            next_y = self.y + move_y

            if self.can_move_to(next_x, next_y):
                self.x = next_x
                self.y = next_y
            elif self.can_move_to(self.x + move_x, self.y):
                # X方向にだけ滑る
                self.x += move_x
            elif self.can_move_to(self.x, self.y + move_y):
                # Y方向にだけ滑る
                self.y += move_y
            # else: 壁に挟まれているので動かない

        if self.invincible_timer > 0:
            self.invincible_timer -= 1
