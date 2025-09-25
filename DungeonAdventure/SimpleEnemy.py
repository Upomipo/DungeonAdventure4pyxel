import math
import random

import attack
import pyxel
from map import checkMapTile_pixel

ENEMY_STATS = {
    "bat": {
        "hp": 30,
        "sprite_u": 0,
        "sprite_v": 48,
        "behavior": "bounce"
    },
    "skeleton": {
        "hp": 50,
        "sprite_u": 0,
        "sprite_v": 56,
        "behavior": "chase",
        "speed": 0.2
    },
    "ghost": {
        "hp": 50,
        "sprite_u": 8,
        "sprite_v": 48,
        "behavior": "bounce",
        "speed": 1.2
    },
    "orc": {
        "hp": 150,
        "sprite_u": 0,
        "sprite_v": 64,
        "behavior": "chase",
        "speed": 0.5
    },
    "spider": {
        "hp": 100,
        "sprite_u": 8,
        "sprite_v": 56,
        "behavior": "bounce",
        "speed": 1.0
    },
    "spector": {
        "hp": 250,
        "sprite_u": 8,
        "sprite_v": 64,
        "behavior": "chase",
        "speed": 0.7
    },
    "rich": {
        "hp": 500,
        "sprite_u": 8,
        "sprite_v": 72,
        "behavior": "chase",
        "speed": 0.5
    },
    "dragon": {
        "hp": 600,
        "sprite_u": 0,
        "sprite_v": 72,
        "behavior": "bounce"
    },
    "default": {
        "hp": 3,
        "sprite_u": 88,
        "sprite_v": 0,
        "behavior": ""
    }
}


class SimpleEnemy:
    def __init__(self, x, y, enemy_type="bat", target=None, drop_item=None):
        self.sprite_v = None
        self.sprite_u = None
        self.hp = 1
        self.x = x
        self.y = y
        self.size = 8
        self.type = enemy_type
        self.behavior = "bounce"  # 追尾 or "bounce"（反射型）

        self.angle = random.uniform(0, math.pi * 2)
        self.speed = 0.8  # 敵ごとの速度調整も可能

        self.hit_timer = 0
        self.is_hit = False

        self.death_timer = 0      # 撃破エフェクト表示用タイマー
        self.is_dying = False     # 撃破中フラグ

        self.spawn_timer = 15  # 出現演出表示時間（15フレームなど）
        self.has_spawned = False

        self.target = target
        self.set_stats_by_type(enemy_type)

        self.drop_item = drop_item
        self.has_dropped = False
        self.disp_damage=0

    def set_stats_by_type(self, enemy_type):
        stats = ENEMY_STATS.get(enemy_type, ENEMY_STATS["default"])
        self.hp = stats["hp"]
        self.sprite_u = stats["sprite_u"]
        self.sprite_v = stats["sprite_v"]
        self.behavior = stats.get("behavior", "")
        self.speed = stats.get("speed", 0.1)  # 速度未定義なら標準値
        # if enemy_type == "bat":
        #     self.hp = 3
        #     self.sprite_u = 0
        #     self.sprite_v = 48
        #     self.behavior = "bounce"
        # elif enemy_type == "skeleton":
        #     self.hp = 5
        #     self.sprite_u = 0
        #     self.sprite_v = 56
        #     self.behavior = "chase"
        #     self.speed = 0.2
        # elif enemy_type == "dragon":
        #     self.hp = 10
        #     self.sprite_u = 104
        #     self.sprite_v = 0
        #     self.behavior = ""
        # else:
        #     self.hp = 3
        #     self.sprite_u = 88
        #     self.sprite_v = 0

    def on_hit(self, damage=1):
        # print(damage)
        # print(self.hit_timer)
        # print(self.hp > 0 and self.is_invincible())
        if self.is_dying or (self.hp > 0 and self.is_invincible()):
            return

        self.hp -= damage
        self.disp_damage = damage
        pyxel.play(3, 1)

        if self.hp <= 0:
            self.death_timer = 6        # 撃破エフェクト表示時間（例：6フレーム）
            self.is_dying = True
            attack.player_attack.add_exp()

            pyxel.play(3, 0)
            if not self.has_dropped:
                if self.drop_item:
                    self.drop_item.get_drop(self.type, self.x, self.y)
                self.has_dropped = True

        else:
            self.hit_timer = 15
            self.is_hit = True

    def update(self):
        if self.spawn_timer > 0:
            self.spawn_timer -= 1
            return  # 出現中は動かさない

        self.has_spawned = True

        # 移動処理
        if not self.is_invincible():
            if self.behavior == "chase":
                dx = self.target.x - self.x
                dy = self.target.y - self.y
                angle = math.atan2(dy, dx)
                move_x = math.cos(angle) * self.speed
                move_y = math.sin(angle) * self.speed
                nx = self.x + move_x
                ny = self.y + move_y

                if not checkMapTile_pixel(nx, ny):
                    self.x, self.y = nx, ny
                elif not checkMapTile_pixel(self.x + move_x, self.y):
                    # X方向にだけ滑る
                    self.x = nx
                elif not checkMapTile_pixel(self.x, self.y + move_y):
                    # Y方向にだけ滑る
                    self.y = ny

            elif self.behavior == "bounce":
                nx = self.x + math.cos(self.angle) * self.speed
                ny = self.y + math.sin(self.angle) * self.speed

                if checkMapTile_pixel(nx, ny):
                    self.angle = random.uniform(0, math.pi * 2)
                else:
                    self.x, self.y = nx, ny

        # ダメージ判定
        if self.hit_timer > 0:
            self.hit_timer -= 1
        else:
            self.is_hit = False
            self.disp_damage = 0

        if self.is_dying and self.death_timer > 0:
            self.death_timer -= 1

        # プレイヤーとの接触チェック
        if self.target and self.is_alive() and self.has_spawned:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy)
            if dist < (self.size + self.target.size) // 2:
                self.target.take_damage(1)  # プレイヤーに1ダメージ

    def draw(self):
        if not self.has_spawned:
            # 出現エフェクト表示
            scale = 0.2 + (15 - self.spawn_timer) * 0.05  # 徐々に拡大など演出可能
            pyxel.blt(self.x - 4, self.y - 4, 0, 16, 24, 8, 8, 0, None, scale)
            return

        if self.is_dying and self.death_timer > 0:
            # 撃破エフェクト（徐々に拡大して消える）
            scale = 1.0 + (6 - self.death_timer) * 0.2
            pyxel.blt(self.x - 4, self.y - 4, 0, 16, 16, 8, 8, 0, None, scale)
            return

        if not self.hp > 0:
            return

        if self.disp_damage > 0:
            pyxel.text(self.x,
                      self.y,
                       str(self.disp_damage),
                       pyxel.COLOR_WHITE
                       )
            # pyxel.text(self.x - self.size // 2,
            #           self.y - self.size // 2,
            #            str(self.disp_damage),
            #            pyxel.COLOR_WHITE
            #            )

        # 点滅演出（無敵中）
        if self.is_invincible() and pyxel.frame_count % 6 < 3:
            return

        pyxel.blt(self.x - self.size // 2,
                  self.y - self.size // 2,
                  0,
                  self.sprite_u,
                  self.sprite_v,
                  self.size,
                  self.size,
                  0)

    def is_alive(self):
        # 撃破演出が終わるまでは生存扱いにしてリストから除外しない
        return self.hp > 0 or self.death_timer > 0

    def is_invincible(self):
        # print(self.hit_timer > 0)
        return self.hit_timer > 0